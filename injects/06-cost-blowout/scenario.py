import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import Runtime, bounded, require, SETTINGS

HERE = Path(__file__).resolve().parent
OPTIONS = SETTINGS['scenarios']['06']
POOL = OPTIONS['pool']
WORKLOAD = SETTINGS['workloads']['front']['name']
TARGET = OPTIONS['replicas']
REDUCTION = Decimal(str(OPTIONS['reduction_percent'])) / 100
LARGE = OPTIONS['large']
SMALL = OPTIONS['small']


def quantity(value):
    match = re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([a-zA-Z]*)', str(value))
    require(match is not None, f'Unsupported resource quantity {value}')
    scale = {'': 1, 'n': Decimal('0.000000001'), 'u': Decimal('0.000001'), 'm': Decimal('0.001'),
             'k': 1000, 'K': 1000, 'M': 1000 ** 2, 'G': 1000 ** 3, 'T': 1000 ** 4,
             'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4}
    require(match[2] in scale, f'Unsupported resource suffix {value}')
    return Decimal(match[1]) * scale[match[2]]


def inventory(runtime):
    nodes = runtime.get('nodes', None, '-l', f'karpenter.sh/nodepool={POOL}')['items']
    return [{'name': node['metadata']['name'],
             'sku': node['metadata']['labels'].get('node.kubernetes.io/instance-type'),
             'vcpu': str(quantity(node['status']['capacity']['cpu'])),
             'deleting': bool(node['metadata'].get('deletionTimestamp'))} for node in nodes]


def usage(runtime):
    output = runtime.k('top', 'pods', '-l', runtime.selector(WORKLOAD), '--containers', '--no-headers')
    samples = {}
    for line in output.splitlines():
        fields = line.split()
        require(len(fields) == 4 and fields[1] == SETTINGS['workloads']['front']['container'], 'Unexpected kubectl top output contract')
        samples[fields[0]] = {'cpu': quantity(fields[2]), 'memory': quantity(fields[3])}
    require(len(samples) == TARGET, 'Metrics missing for one or more target replicas')
    return samples


def check_rightsizing(pods, samples):
    for pod in pods:
        name = pod['metadata']['name']
        require(name in samples, f'Missing live usage for {name}')
        resources = pod['spec']['containers'][0]['resources']['requests']
        cpu, memory = quantity(resources['cpu']), quantity(resources['memory'])
        require(cpu >= quantity(OPTIONS['cpu_floor']) and memory >= quantity(OPTIONS['memory_floor']), 'Requests unreasonably small')
        require(cpu <= max(quantity(OPTIONS['cpu_allowance']), samples[name]['cpu'] * OPTIONS['usage_multiplier']), 'CPU request is oversized versus live usage')
        require(memory <= max(quantity(OPTIONS['memory_allowance']), samples[name]['memory'] * OPTIONS['usage_multiplier']), 'Memory request is oversized versus live usage')
        require(cpu >= samples[name]['cpu'] and memory >= samples[name]['memory'],
                'Requests below measured usage; review representative load before accepting')


def measured_usage(runtime):
    result = {}

    def available():
        try:
            result.update(usage(runtime))
            return True
        except subprocess.CalledProcessError as error:
            if 'metrics not available yet' not in (error.stderr or '').lower():
                raise
            return False
        except RuntimeError as error:
            if str(error) != 'Metrics missing for one or more target replicas':
                raise
            return False

    bounded(available, SETTINGS['timing']['metrics'], 'fresh metrics for all storefront replicas')
    return result


def repair(runtime):
    runtime.pin('deployment', WORKLOAD, resources=SMALL, replicas=TARGET)
    runtime.workload_ready(WORKLOAD, TARGET)


def verify(runtime):
    require(runtime.state and runtime.state.get('baseline_vcpu'), 'No measured inflated capacity baseline')
    require(runtime.owned('nodepool', POOL) is not None, 'Scenario pool missing')
    pods = runtime.workload_ready(WORKLOAD, TARGET)
    for sample in range(OPTIONS['samples']):
        check_rightsizing(pods, measured_usage(runtime))
        if sample < OPTIONS['samples'] - 1:
            time.sleep(OPTIONS['sample_interval'])
    before = Decimal(runtime.state['baseline_vcpu'])
    require(before > 0, 'Invalid capacity baseline')
    threshold = before * (1 - REDUCTION)

    def reduced():
        nodes = inventory(runtime)
        total = sum((Decimal(node['vcpu']) for node in nodes), Decimal(0))
        print(f'Pool nodes={len(nodes)} total_vCPU={total}; required <= {threshold}', flush=True)
        return bool(nodes) and total <= threshold and not any(node['deleting'] for node in nodes)

    bounded(reduced, SETTINGS['timing']['consolidation'], f'at least {OPTIONS["reduction_percent"]}% actual pool vCPU reduction after natural consolidation')
    pods = runtime.workload_ready(WORKLOAD, TARGET)
    check_rightsizing(pods, measured_usage(runtime))
    after_nodes = inventory(runtime)
    after = sum(Decimal(node['vcpu']) for node in after_nodes)
    runtime.state['verified_vcpu'] = str(after)
    runtime.state['verified_nodes'] = after_nodes
    runtime.save()
    print(json.dumps({'before_vcpu': str(before), 'after_vcpu': str(after),
                      'reduction_percent': str((1 - after / before) * 100), 'nodes': after_nodes}, indent=2))
    print(f'PASS: {TARGET} Ready scenario-pool replicas, requests within measured usage bounds, and >={OPTIONS["reduction_percent"]}% actual vCPU reduction')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inject', 'verify', 'reset', 'repair'])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    runtime = Runtime(HERE, POOL)
    deployment = runtime.get('deployment', WORKLOAD)
    containers = deployment['spec']['template']['spec']['containers']
    reference = SETTINGS['workloads']['front']
    require(len(containers) == 1 and containers[0]['name'] == reference['container'], 'Container contract changed')
    require(not reference['image'] or containers[0]['image'] == reference['image'], 'Image contract changed')
    require(0 < REDUCTION < 1 and TARGET > 0 and OPTIONS['samples'] > 0, 'Invalid reduction, replicas or samples')
    if args.action == 'inject' and (not args.apply or args.plan):
        details = {'pool': POOL, 'cpu_limit': OPTIONS['cpu_limit'], 'memory_limit': OPTIONS['memory_limit'],
                   'workload': WORKLOAD, 'replicas': TARGET, 'resources': LARGE,
                   'reduction_percent': OPTIONS['reduction_percent']}
        print('PLAN: ' + json.dumps(details) + '; billable capacity. No injection performed.')
        return
    require(args.action == 'inject' or runtime.state is not None, 'No saved baseline')
    if args.action == 'inject':
        runtime.baseline([('deployment', WORKLOAD)])
        if runtime.state.get('baseline_vcpu'):
            print('Inflated baseline already recorded; reset before another injection')
            print(json.dumps(runtime.state['inflated_nodes'], indent=2))
            return
        manifest = runtime.pool_manifest(cpu=OPTIONS['cpu_limit'], cpu_sizes=OPTIONS['cpu_sizes'])
        manifest['spec']['limits']['memory'] = OPTIONS['memory_limit']
        runtime.create(manifest)
        runtime.pin('deployment', WORKLOAD, resources=LARGE, replicas=TARGET)
        runtime.workload_ready(WORKLOAD, TARGET)
        nodes = inventory(runtime)
        total = sum(Decimal(node['vcpu']) for node in nodes)
        require(total >= Decimal(OPTIONS['minimum_baseline_vcpu']) and not any(node['deleting'] for node in nodes), 'Inflated baseline not stable')
        runtime.state['baseline_vcpu'] = str(total)
        runtime.state['inflated_nodes'] = nodes
        runtime.save()
        print(json.dumps({'node_count': len(nodes), 'total_vcpu': str(total), 'nodes': nodes}, indent=2))
    elif args.action == 'repair':
        repair(runtime)
    elif args.action == 'verify':
        verify(runtime)
    else:
        saved = runtime.state['workloads'][WORKLOAD]
        runtime.patch('deployment', WORKLOAD, [{
            'op': 'add', 'path': '/spec/template/spec/containers/0/resources',
            'value': saved['spec']['containers'][0]['resources']}])
        runtime.restore(['nodeSelector', 'tolerations'])
        runtime.cleanup_pool()
        print('Original storefront resources/replicas/scheduling restored; scenario capacity removed')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError, InvalidOperation) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)