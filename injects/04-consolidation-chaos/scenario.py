import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import Runtime, SETTINGS, bounded, require

HERE = Path(__file__).resolve().parent
CONFIG = SETTINGS['scenarios']['04']
POOL = CONFIG['pool']
FILLER = CONFIG['filler']
FILLER_LABELS = {'app': FILLER}
WORKLOADS = [SETTINGS['workloads'][role]['name'] for role in ('database', 'broker')]
TIMING = SETTINGS['timing']
NAMESPACE = SETTINGS['target']['namespace']


def filler(runtime):
    return {'apiVersion': 'apps/v1', 'kind': 'Deployment', 'metadata': {'name': FILLER},
            'spec': {'replicas': 1, 'selector': {'matchLabels': FILLER_LABELS},
                     'template': {'metadata': {'labels': FILLER_LABELS}, 'spec': {
                         'nodeSelector': {'injects.sre/pool': POOL},
                         'tolerations': [{'key': 'injects.sre/pool', 'value': POOL, 'operator': 'Equal', 'effect': 'NoSchedule'}],
                         'containers': [{'name': 'filler', 'image': CONFIG['filler_image'], 'command': ['tail', '-f', '/dev/null'],
                                         'resources': {'requests': {'cpu': CONFIG['filler_cpu'], 'memory': CONFIG['filler_memory']},
                                                       'limits': {'cpu': CONFIG['filler_cpu'], 'memory': CONFIG['filler_memory']}}}]}}}}


def resize(runtime, cpu):
    require(runtime.owned('deployment', FILLER) is not None, 'Filler missing')
    runtime.patch('deployment', FILLER, [{
        'op': 'add', 'path': '/spec/template/spec/containers/0/resources/requests/cpu', 'value': cpu}])
    runtime.rollout('deployment', FILLER)


def witness(runtime, action):
    order = SETTINGS['workloads']['order']
    print(runtime.k('exec', '-i', f'deployment/{order["name"]}', '-c', order['container'], '--', 'node', '-', action,
                    json.dumps(SETTINGS['broker']), json.dumps({'scenario': CONFIG, 'timing': TIMING}),
                    raw=(HERE / 'witness.cjs').read_text()).strip(), flush=True)


def workload_selector(runtime, name):
    selector = runtime.get('statefulset', name)['spec']['selector']
    require(not selector.get('matchExpressions'), f'{name}: selector matchExpressions are unsupported')
    require(selector.get('matchLabels'), f'{name}: selector matchLabels must not be empty')
    return selector['matchLabels']


def pdb_manifest(runtime, name):
    return {'apiVersion': 'policy/v1', 'kind': 'PodDisruptionBudget',
            'metadata': {'name': f'inject04-{name}'},
            'spec': {'minAvailable': 1, 'selector': {'matchLabels': workload_selector(runtime, name)}}}


def protect(runtime):
    for name in WORKLOADS:
        runtime.create(pdb_manifest(runtime, name))
    runtime.patch('nodepool', POOL, [{
        'op': 'add', 'path': '/spec/disruption/budgets', 'value': [{'nodes': '0'}]}])
    print('Applied scenario PDBs and zero voluntary disruption budget')


def verify(runtime):
    require(runtime.state is not None, 'No saved scenario baseline')
    pool = runtime.owned('nodepool', POOL)
    require(pool is not None, 'Scenario pool missing')
    zero_budget = any(budget['nodes'] == '0' and not budget.get('schedule') and not budget.get('reasons')
                      for budget in pool['spec']['disruption'].get('budgets', []))
    for name in WORKLOADS:
        pod = runtime.get('pod', f'{name}-0')
        labels = pod['metadata'].get('labels', {})
        selector = workload_selector(runtime, name)
        require(all(labels.get(key) == value for key, value in selector.items()),
            f'{name}: pod labels do not match StatefulSet selector')
        pdbs = runtime.get('pdb')['items']
        valid = [pdb for pdb in pdbs if pdb['spec'].get('selector', {}).get('matchLabels')
             and all(labels.get(key) == value for key, value in pdb['spec']['selector']['matchLabels'].items())
                 and not pdb['spec']['selector'].get('matchExpressions')
                 and pdb['spec'].get('minAvailable') == 1 and
                 pdb['status'].get('observedGeneration') == pdb['metadata']['generation'] and
                 pdb['status'].get('currentHealthy', 0) >= 1 and pdb['status'].get('disruptionsAllowed') == 0]
        require(valid, f'{name} lacks an effective PDB')
        require(zero_budget or pod['metadata'].get('annotations', {}).get('karpenter.sh/do-not-disrupt') == 'true',
                f'{name} lacks extra voluntary-disruption protection')
        node = runtime.get('node', pod['spec']['nodeName'])
        require(node['metadata']['labels'].get('karpenter.sh/nodepool') == POOL, 'Wrong stateful placement')
    before = runtime.snapshots(WORKLOADS)
    resize(runtime, CONFIG['filler_cpu'])
    resize(runtime, CONFIG['filler_low_cpu'])
    deadline = time.monotonic() + TIMING['protection']
    while time.monotonic() < deadline:
        require(runtime.snapshots(WORKLOADS) == before, 'Stateful pod moved/restarted during consolidation retrigger')
        time.sleep(5)
    print(f'PASS: effective PDBs and disruption protection; repeated filler reduction caused no stateful replacement/restarts over {TIMING["protection"]} seconds')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inject', 'verify', 'reset', 'protect'])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    runtime = Runtime(HERE, POOL)
    for name in WORKLOADS:
        resource = runtime.get('statefulset', name)
        require(resource['spec']['replicas'] == 1 and not resource['spec'].get('volumeClaimTemplates') and
                not any(volume.get('persistentVolumeClaim') for volume in resource['spec']['template']['spec'].get('volumes', [])),
                'Storage/replica contract changed; inspect before proceeding')
        workload_selector(runtime, name)
    if args.action == 'inject' and (not args.apply or args.plan):
        print(f'PLAN: move {", ".join(WORKLOADS)} to owned {POOL} pool in {NAMESPACE}; no PVCs. '
              f'Use filler CPU {CONFIG["filler_cpu"]} -> {CONFIG["filler_low_cpu"]}, seed durable broker witness, and await natural '
              'consolidation plus witness loss. DESTRUCTIVE: existing in-memory data can be lost on placement AND reset. '
              f'Pool CPU ceiling {CONFIG["cpu_limit"]}; existing pools/NodeClass unchanged. No injection performed.')
        return
    require(args.action == 'inject' or runtime.state is not None, 'No saved baseline')
    if args.action == 'inject':
        require(not runtime.get('pdb')['items'], 'PDBs exist: do not remove protections; use a clean approved baseline')
        runtime.baseline([('statefulset', name) for name in WORKLOADS])
        if runtime.state.get('injection_complete'):
            print('Injection already demonstrated; not repeating destructive data loss. Reset before another rehearsal.')
            return
        for saved in runtime.state['workloads'].values():
            require(not saved['spec'].get('affinity') and not saved['annotations'].get('karpenter.sh/do-not-disrupt'),
                    'Existing protection/affinity requires a new plan')
        runtime.create(runtime.pool_manifest(cpu=CONFIG['cpu_limit']))
        runtime.create(filler(runtime))
        runtime.rollout('deployment', FILLER)
        affinity = {'podAffinity': {'requiredDuringSchedulingIgnoredDuringExecution': [{
            'labelSelector': {'matchLabels': FILLER_LABELS}, 'topologyKey': 'kubernetes.io/hostname'}]}}
        for name in WORKLOADS:
            runtime.pin('statefulset', name, affinity=affinity)
            runtime.rollout('statefulset', name)
        before = runtime.snapshots(WORKLOADS)
        witness(runtime, 'seed')
        runtime.state['before_consolidation'] = before
        runtime.save()
        resize(runtime, CONFIG['filler_low_cpu'])
        def replaced():
            pods = [runtime.optional('pod', f'{name}-0') for name in WORKLOADS]
            return all(pod and pod['metadata']['uid'] != before[name]['uid']
                       for name, pod in zip(WORKLOADS, pods))
        bounded(replaced, TIMING['consolidation'], 'natural consolidation replacing both stateful pods')
        for name in WORKLOADS:
            runtime.rollout('statefulset', name)
        witness(runtime, 'lost')
        runtime.state['injection_complete'] = True
        runtime.save()
        print('DEMONSTRATED: stateful pod replacements and durable broker witness loss; inspect NodeClaim/events for consolidation trail')
    elif args.action == 'protect':
        protect(runtime)
    elif args.action == 'verify':
        verify(runtime)
    else:
        for name in WORKLOADS:
            runtime.delete_owned('pdb', f'inject04-{name}',
                                 f'/apis/policy/v1/namespaces/{NAMESPACE}/poddisruptionbudgets/inject04-{name}')
        runtime.restore(['nodeSelector', 'tolerations', 'affinity'])
        runtime.delete_owned('deployment', FILLER,
                             f'/apis/apps/v1/namespaces/{NAMESPACE}/deployments/{FILLER}')
        filler_selector = ','.join(f'{key}={value}' for key, value in FILLER_LABELS.items())
        bounded(lambda: not runtime.get('pods', None, '-l', filler_selector)['items'], TIMING['delete'], 'filler pod deletion')
        runtime.cleanup_pool()
        witness(runtime, 'delete')
        print('Healthy scheduling baseline restored; historical ephemeral data cannot be restored by reset')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)