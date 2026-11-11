import hashlib
import json
import os
from pathlib import Path
import shlex


DEFAULTS = {
    'target': {'context': '', 'namespace': '', 'server': '', 'kubeconfig': ''},
    'workloads': {
        'order': {'name': 'order-service', 'container': 'order-service', 'selector': 'app=order-service', 'image': ''},
        'customer': {'name': 'virtual-customer', 'container': 'virtual-customer', 'selector': 'app=virtual-customer', 'image': ''},
        'product': {'name': 'product-service', 'container': 'product-service', 'selector': 'app=product-service', 'image': ''},
        'makeline': {'name': 'makeline-service', 'container': 'makeline-service', 'selector': 'app=makeline-service', 'image': ''},
        'front': {'name': 'store-front', 'container': 'store-front', 'selector': 'app=store-front', 'image': ''},
        'database': {'name': 'documentdb', 'selector': 'app=documentdb'},
        'broker': {'name': 'rabbitmq', 'selector': 'app=rabbitmq'},
    },
    'broker': {
        'secret': 'order-service-secrets', 'configmap': 'order-service-configs',
        'password_key': 'ORDER_QUEUE_PASSWORD', 'username_env': 'ORDER_QUEUE_USERNAME',
        'password_env': 'ORDER_QUEUE_PASSWORD', 'hostname_key': 'ORDER_QUEUE_HOSTNAME',
        'port_key': 'ORDER_QUEUE_PORT', 'queue_key': 'ORDER_QUEUE_NAME',
        'host': 'rabbitmq', 'port': '5672', 'queue': 'orders', 'vhost': '/',
        'management_url': 'http://rabbitmq:15672/api', 'order_url': 'http://order-service:3000/',
        'health_url': 'http://order-service:3000/health', 'publisher_path': '/app/plugins/messagequeue.js',
        'route_path': '/app/routes/root.js',
        'test_order': {'items': [{'productId': 1, 'quantity': 1, 'price': 10}]},
    },
    'nodepool': {
        'api_version': 'karpenter.sh/v1',
        'nodeclass_ref': {'group': 'karpenter.azure.com', 'kind': 'AKSNodeClass', 'name': ''},
        'labels': {'kubernetes.azure.com/mode': 'user', 'kubernetes.azure.com/ebpf-dataplane': 'cilium'},
        'requirements': [
            {'key': 'kubernetes.io/os', 'operator': 'In', 'values': ['linux']},
            {'key': 'kubernetes.io/arch', 'operator': 'In', 'values': ['amd64']},
            {'key': 'karpenter.azure.com/sku-family', 'operator': 'In', 'values': ['D']},
        ],
        'startup_taints': [{'key': 'node.cilium.io/agent-not-ready', 'value': 'true', 'effect': 'NoExecute'}],
        'memory_limit': '64Gi', 'cpu_sizes': ['2', '4'], 'consolidate_after': '10s',
    },
    'timing': {'request': '30s', 'rollout': 600, 'delete': 600, 'consolidation': 900,
               'metrics': 180, 'stability': 60, 'protection': 180, 'recent_restarts': 300},
    'scenarios': {
        '01': {'wrong_password': 'scenario01-deliberately-invalid-password'},
        '02': {'pool': 'inject02-limits', 'cpu_limit': '1', 'memory_limit': '16Gi', 'cpu_sizes': ['2'], 'replicas': 3},
        '03': {'zone': 'unavailable-zone', 'tolerations': []},
        '04': {'pool': 'inject04-consolidation', 'filler': 'inject04-filler', 'filler_image': 'busybox:1.37.0',
               'filler_cpu': '2', 'filler_low_cpu': '1m', 'filler_memory': '64Mi', 'cpu_limit': '8',
               'witness_queue': 'inject04-durability-witness'},
        '05': {'pool': 'inject05-spot', 'cpu_limit': '4', 'blocked_cpu_limit': '0', 'replicas': 1},
        '06': {'pool': 'inject06-cost', 'cpu_limit': '8', 'memory_limit': '32Gi', 'cpu_sizes': ['2', '4'],
               'replicas': 3, 'reduction_percent': 50, 'minimum_baseline_vcpu': '4',
               'large': {'requests': {'cpu': '1', 'memory': '2Gi'}, 'limits': {'cpu': '1', 'memory': '2Gi'}},
               'small': {'requests': {'cpu': '10m', 'memory': '64Mi'}, 'limits': {'cpu': '1', 'memory': '512Mi'}},
               'cpu_floor': '5m', 'memory_floor': '32Mi', 'cpu_allowance': '100m',
               'memory_allowance': '128Mi', 'usage_multiplier': 4, 'samples': 3, 'sample_interval': 15},
         '07': {'deployment': '', 'policy_name': 'inject07-deny-ingress', 'enforcement_confirmed': False,
             'probe': {'pod': '', 'container': '', 'executable': 'node', 'url': '',
                    'timeout_seconds': 8, 'healthy_statuses': [200], 'broken_statuses': [0],
                    'broken_errors': ['ETIMEDOUT']}},
         '08': {'ingress': '', 'host': '', 'path': '/', 'path_type': 'Prefix',
             'wrong_service': 'inject08-missing-service', 'wrong_port': 80,
             'probe': {'pod': '', 'container': '', 'executable': 'node', 'url': '',
                         'timeout_seconds': 8, 'healthy_statuses': [200], 'broken_statuses': [404, 502, 503],
                         'broken_errors': []}},
         '09': {'service': '',
             'probe': {'pod': '', 'container': '', 'executable': 'node', 'url': '',
                         'timeout_seconds': 8, 'healthy_statuses': [200], 'broken_statuses': [0],
                         'broken_errors': ['ETIMEDOUT', 'ECONNREFUSED', 'ECONNRESET']}},
    },
}


def merge(base, overrides, path=''):
    for key, value in overrides.items():
        location = f'{path}.{key}' if path else key
        if location in ('nodepool.labels', 'broker.test_order'):
            base[key] = value
            continue
        if key not in base:
            raise RuntimeError(f'Unknown configuration key: {key}')
        if isinstance(base[key], dict) and isinstance(value, dict):
            merge(base[key], value, location)
        else:
            base[key] = value
    return base


def load():
    result = json.loads(json.dumps(DEFAULTS))
    filename = os.environ.get('INJECT_CONFIG')
    if filename:
        merge(result, json.loads(Path(filename).read_text()))
    return result


def target(settings):
    for name in ('context', 'namespace', 'server', 'kubeconfig'):
        if not settings['target'].get(name):
            raise RuntimeError(f'Set target.{name} in the JSON file selected by INJECT_CONFIG')
    if not settings['target']['server'].startswith('https://'):
        raise RuntimeError('target.server must be the inspected HTTPS Kubernetes API URL')
    return settings['target']


def identity(settings):
    return hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()


def state_directory(settings, directory):
    return Path(directory) / '.state' / identity(settings)


def shell(settings):
    selected = target(settings)
    values = {'CONTEXT': selected['context'], 'NAMESPACE': selected['namespace'],
              'EXPECTED_SERVER': selected['server'], 'KUBECONFIG': selected['kubeconfig'],
              'CONFIG_ID': identity(settings), 'REQUEST_TIMEOUT': settings['timing']['request'],
              'ROLLOUT_TIMEOUT': str(settings['timing']['rollout']),
              'RECENT_RESTARTS': str(settings['timing']['recent_restarts']),
              'NODECLASS': settings['nodepool']['nodeclass_ref']['name'],
              'BROKER_JSON': json.dumps(settings['broker']), 'TIMING_JSON': json.dumps(settings['timing']),
              'POOL_API': settings['nodepool']['api_version']}
    for role, workload in settings['workloads'].items():
        for key, value in workload.items():
            values[f'{role.upper()}_{key.upper()}'] = value
    for key, value in settings['broker'].items():
        if isinstance(value, str):
            values[f'BROKER_{key.upper()}'] = value
    for number in ('01', '02'):
        for key, value in settings['scenarios'][number].items():
            values[f'S{number}_{key.upper()}'] = str(value) if not isinstance(value, list) else json.dumps(value)
    return '\n'.join(f'export {key}={shlex.quote(value)}' for key, value in values.items())


if __name__ == '__main__':
    import sys
    try:
        print(shell(load()))
    except (RuntimeError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)