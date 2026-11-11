import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import Runtime, bounded, require, SETTINGS, NAMESPACE

HERE = Path(__file__).resolve().parent
OPTIONS = SETTINGS['scenarios']['05']
POOL = OPTIONS['pool']
WORKLOAD = SETTINGS['workloads']['makeline']['name']
TARGET = OPTIONS['replicas']


def capacity(runtime, values, cpu=None):
    cpu = cpu or OPTIONS['cpu_limit']
    pool = runtime.owned('nodepool', POOL)
    require(pool is not None, 'Scenario pool missing')
    requirements = pool['spec']['template']['spec']['requirements']
    for requirement in requirements:
        if requirement['key'] == 'karpenter.sh/capacity-type':
            requirement['values'] = values
    runtime.patch('nodepool', POOL, [
        {'op': 'add', 'path': '/spec/limits/cpu', 'value': cpu},
        {'op': 'add', 'path': '/spec/template/spec/requirements', 'value': requirements}])


def pin(runtime, spot=False):
    runtime.pin('deployment', WORKLOAD)
    if spot:
        runtime.patch('deployment', WORKLOAD, [{
            'op': 'add', 'path': '/spec/template/spec/nodeSelector/karpenter.sh~1capacity-type', 'value': 'spot'}])


def delete_spot_claim(runtime):
    nodes = runtime.get('nodes', None, '-l', f'karpenter.sh/nodepool={POOL},karpenter.sh/capacity-type=spot')['items']
    node_names = {node['metadata']['name'] for node in nodes}
    require(node_names, 'No scenario Spot node exists; cannot claim an eviction test')
    allowed_pods = {pod['metadata']['uid'] for pod in runtime.get(
        'pods', None, '-l', runtime.selector(WORKLOAD))['items']}
    for pod in runtime.get('pods', None, '--all-namespaces')['items']:
        if pod['spec'].get('nodeName') not in node_names:
            continue
        owners = pod['metadata'].get('ownerReferences', [])
        require(any(owner['kind'] == 'DaemonSet' for owner in owners) or
                (pod['metadata']['namespace'] == NAMESPACE and
                 pod['metadata']['uid'] in allowed_pods),
                'Unrelated workload on Spot node; refusing eviction')
    claims = runtime.get('nodeclaims', None, '-l', f'karpenter.sh/nodepool={POOL}')['items']
    claims = [claim for claim in claims if claim.get('status', {}).get('nodeName') in node_names]
    require(claims, 'No matching Spot NodeClaim')
    for claim in claims:
        runtime.k('delete', '--raw', f'/apis/{SETTINGS["nodepool"]["api_version"]}/nodeclaims/{claim["metadata"]["name"]}', '-f', '-', payload={
            'apiVersion': 'v1', 'kind': 'DeleteOptions', 'preconditions': {'uid': claim['metadata']['uid']}})
        runtime.k('wait', '--for=delete', f'nodeclaim/{claim["metadata"]["name"]}', f'--timeout={SETTINGS["timing"]["delete"]}s')


def repair(runtime):
    capacity(runtime, ['spot', 'on-demand'])
    pin(runtime)
    runtime.workload_ready(WORKLOAD, TARGET)


def verify(runtime):
    pool = runtime.owned('nodepool', POOL)
    require(pool is not None, 'Scenario pool missing')
    requirements = pool['spec']['template']['spec']['requirements']
    require(any(item['key'] == 'karpenter.sh/capacity-type' and item['operator'] == 'In' and
                {'spot', 'on-demand'} <= set(item['values']) for item in requirements), 'Both capacity types not allowed')
    deployment = runtime.get('deployment', WORKLOAD)
    require('karpenter.sh/capacity-type' not in deployment['spec']['template']['spec'].get('nodeSelector', {}),
            'Workload still pinned to Spot')
    runtime.workload_ready(WORKLOAD, TARGET)
    print('Establishing a fresh Spot placement before controlled fallback test', flush=True)
    capacity(runtime, ['spot'])
    pin(runtime, spot=True)
    runtime.workload_ready(WORKLOAD, TARGET, 'spot')
    try:
        capacity(runtime, ['on-demand'])
        pin(runtime)
        delete_spot_claim(runtime)
        runtime.workload_ready(WORKLOAD, TARGET, 'on-demand')
    finally:
        capacity(runtime, ['spot', 'on-demand'])
        pin(runtime)
    runtime.workload_ready(WORKLOAD, TARGET, 'on-demand')
    print('PASS: controlled Spot exclusion and NodeClaim deletion recovered makeline on-demand; both capacity types restored')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inject', 'verify', 'reset', 'repair'])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    runtime = Runtime(HERE, POOL)
    workload = runtime.get('deployment', WORKLOAD)
    containers = workload['spec']['template']['spec']['containers']
    reference = SETTINGS['workloads']['makeline']
    require(len(containers) == 1 and containers[0]['name'] == reference['container'], 'Workload container contract changed')
    require(not reference['image'] or containers[0]['image'] == reference['image'], 'Workload image contract changed')
    require(workload['spec']['replicas'] == TARGET, 'Configure scenario 05 replicas to match the inspected baseline')
    if args.action == 'inject' and (not args.apply or args.plan):
        print(f'PLAN: create isolated Spot-only {POOL} (CPU limit {OPTIONS["cpu_limit"]}), pin {WORKLOAD}, wait Ready; '
              f'set scenario CPU ceiling to {OPTIONS["blocked_cpu_limit"]} and delete its Spot NodeClaim, blocking replacement. '
              'Only namespace workload and new pool change. No injection performed.')
        return
    require(args.action == 'inject' or runtime.state is not None, 'No saved baseline')
    if args.action == 'inject':
        runtime.baseline([('deployment', WORKLOAD)])
        if runtime.state.get('injection_complete'):
            print('Injection already complete; reset before another destructive rehearsal')
            return
        runtime.create(runtime.pool_manifest(cpu=OPTIONS['cpu_limit'], capacities=['spot'], budget=[{'nodes': '0'}]))
        pin(runtime, spot=True)
        runtime.workload_ready(WORKLOAD, TARGET, 'spot')
        capacity(runtime, ['spot'], OPTIONS['blocked_cpu_limit'])
        delete_spot_claim(runtime)
        bounded(lambda: any(pod['status']['phase'] == 'Pending' for pod in
                            runtime.get('pods', None, '-l', runtime.selector(WORKLOAD))['items']), SETTINGS['timing']['rollout'], 'Pending replacement')
        runtime.state['injection_complete'] = True
        runtime.save()
        print('Spot claim evicted; makeline replacement Pending under blocked pool limit')
    elif args.action == 'repair':
        repair(runtime)
    elif args.action == 'verify':
        verify(runtime)
    else:
        runtime.restore(['nodeSelector', 'tolerations'])
        runtime.cleanup_pool()
        print('Baseline makeline scheduling restored; owned Spot/fallback capacity removed')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)