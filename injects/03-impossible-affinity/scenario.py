import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from config import load, target, state_directory, identity

SETTINGS = load()
STATE = state_directory(SETTINGS, HERE) / 'baseline.json'
CONTEXT = SETTINGS['target']['context']
NAMESPACE = SETTINGS['target']['namespace']
SERVER = SETTINGS['target']['server']
WORKLOAD = SETTINGS['workloads']['product']
SCENARIO = SETTINGS['scenarios']['03']
AFFINITY = {'nodeAffinity': {'requiredDuringSchedulingIgnoredDuringExecution': {
    'nodeSelectorTerms': [{'matchExpressions': [{
        'key': 'topology.kubernetes.io/zone', 'operator': 'In',
        'values': [SCENARIO['zone']],
    }]}],
}}}


def kubectl(*args, payload=None):
    selected = target(SETTINGS)
    command = ['kubectl', '--kubeconfig', selected['kubeconfig'],
               '--context', selected['context'], '--namespace', selected['namespace'],
               f'--request-timeout={SETTINGS["timing"]["request"]}', *args]
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, check=True)
    return result.stdout


def get(*args):
    return json.loads(kubectl('get', *args, '-o', 'json'))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def matches(expression, labels):
    key, operator = expression['key'], expression['operator']
    values = expression.get('values', [])
    actual = labels.get(key)
    if operator == 'In':
        return actual is not None and actual in values
    if operator == 'NotIn':
        return actual is None or actual not in values
    if operator == 'Exists':
        return key in labels
    if operator == 'DoesNotExist':
        return key not in labels
    if operator in ('Gt', 'Lt'):
        try:
            return int(actual) > int(values[0]) if operator == 'Gt' else int(actual) < int(values[0])
        except (ValueError, TypeError, IndexError):
            return False
    raise RuntimeError(f'Unsupported affinity operator: {operator}')


def satisfies(spec, node):
    labels = node['metadata'].get('labels', {})
    if not all(labels.get(key) == value for key, value in spec.get('nodeSelector', {}).items()):
        return False
    required = spec.get('affinity', {}).get('nodeAffinity', {}).get(
        'requiredDuringSchedulingIgnoredDuringExecution')
    if required is None:
        return True
    for term in required.get('nodeSelectorTerms', []):
        if not term:
            continue
        if all(matches(expression, labels) for expression in term.get('matchExpressions', [])) and all(
            matches(expression, {'metadata.name': node['metadata']['name']})
            for expression in term.get('matchFields', [])
        ):
            return True
    return False


def patch(deployment, affinity, tolerations):
    operations = [
        {'op': 'test', 'path': '/metadata/uid', 'value': deployment['metadata']['uid']},
        {'op': 'test', 'path': '/metadata/resourceVersion', 'value': deployment['metadata']['resourceVersion']},
        {'op': 'add', 'path': '/spec/template/spec/affinity', 'value': affinity},
        {'op': 'add', 'path': '/spec/template/spec/tolerations', 'value': tolerations},
    ]
    kubectl('patch', 'deployment', WORKLOAD['name'], '--type=json', '--patch-file=/dev/stdin', payload=operations)


def verify():
    kubectl('rollout', 'status', f'deployment/{WORKLOAD["name"]}',
            f'--timeout={SETTINGS["timing"]["rollout"]}s')
    deployment = get('deployment', WORKLOAD['name'])
    target = deployment['spec']['replicas']
    require(target > 0 and deployment['status'].get('updatedReplicas') == target and
            deployment['status'].get('readyReplicas') == target and
            deployment['status'].get('availableReplicas') == target,
            'Target replicas not fully updated, Ready and available')
    pods = [pod for pod in get('pods', '-l', WORKLOAD['selector'])['items']
            if not pod['metadata'].get('deletionTimestamp')]
    require(len(pods) == target, 'Unexpected pod count')
    for pod in pods:
        require(pod['status']['phase'] == 'Running' and any(
            condition['type'] == 'Ready' and condition['status'] == 'True'
            for condition in pod['status'].get('conditions', [])), 'Pod not Ready')
        node = get('node', pod['spec']['nodeName'])
        require(satisfies(pod['spec'], node), 'Actual node does not satisfy pod scheduling requirements')
        require(satisfies(deployment['spec']['template']['spec'], node),
                'Actual node does not satisfy current deployment requirements')
        require(any(condition['type'] == 'Ready' and condition['status'] == 'True'
                    for condition in node['status']['conditions']), 'Node not Ready')
    print(f'PASS: {WORKLOAD["name"]} fully Ready on nodes satisfying its actual requirements')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inject', 'verify', 'reset'])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    os.umask(0o077)
    target(SETTINGS)
    server = json.loads(kubectl('config', 'view', '--minify', '-o', 'json'))['clusters'][0]['cluster']['server']
    require(server == SERVER, 'Wrong cluster API')
    deployment = get('deployment', WORKLOAD['name'])
    containers = deployment['spec']['template']['spec']['containers']
    require(len(containers) == 1 and containers[0]['name'] == WORKLOAD['container'],
            'Expected a single configured container')
    if WORKLOAD['image']:
        require(containers[0]['image'] == WORKLOAD['image'], 'Image contract changed')
    STATE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (STATE.parent / 'lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.action == 'verify':
            verify()
            return
        if args.action == 'inject' and (not args.apply or args.plan):
            print(f'PLAN: {CONTEXT}/{NAMESPACE}; API {SERVER}; '
                f'kubeconfig {SETTINGS["target"]["kubeconfig"]}; '
                f'require zone {SCENARIO["zone"]} on deployment/{WORKLOAD["name"]}; '
                f'container {WORKLOAD["container"]}; selector {WORKLOAD["selector"]}; '
                f'image guard {WORKLOAD["image"] or "disabled"}; '
                f'append configured tolerations {json.dumps(SCENARIO["tolerations"])}. '
                  'No NodePool writes. Existing replica remains during stalled rollout. No injection performed.')
            return
        if STATE.exists():
            baseline = json.loads(STATE.read_text())
            require(baseline.get('config_id') == identity(SETTINGS),
                    'Saved configuration does not match target')
            require(baseline['uid'] == deployment['metadata']['uid'], 'Deployment recreated; review baseline')
        else:
            require(args.action == 'inject', 'No saved baseline')
            verify()
            spec = deployment['spec']['template']['spec']
            require(not spec.get('affinity'), 'Existing affinity requires a new reviewed scenario plan')
            baseline = {'config_id': identity(SETTINGS),
                        'uid': deployment['metadata']['uid'], 'affinity': {},
                        'tolerations': spec.get('tolerations', [])}
            temporary = STATE.with_suffix('.tmp')
            temporary.write_text(json.dumps(baseline))
            temporary.replace(STATE)
        tolerations = baseline['tolerations'] + SCENARIO['tolerations']
        current = deployment['spec']['template']['spec']
        require(current.get('affinity', {}) in (baseline['affinity'], AFFINITY),
                'Unexpected affinity edits; refusing to overwrite')
        require(current.get('tolerations', []) in (baseline['tolerations'], tolerations),
                'Unexpected toleration edits; refusing to overwrite')
        if args.action == 'inject':
            patch(deployment, AFFINITY, tolerations)
            print('Injected impossible required zone affinity; inspect Pending pod and provisioning events')
        else:
            patch(deployment, baseline['affinity'], baseline['tolerations'])
            verify()
            print('Baseline affinity/tolerations restored')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)