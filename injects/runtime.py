import copy
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from config import load, target, identity, state_directory

SETTINGS = load()
CONTEXT = SETTINGS['target']['context']
NAMESPACE = SETTINGS['target']['namespace']
SERVER = SETTINGS['target']['server']


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Runtime:
    def __init__(self, directory, pool):
        os.umask(0o077)
        self.directory = Path(directory)
        self.pool = pool
        self.settings = SETTINGS
        target(self.settings)
        self.state_path = state_directory(self.settings, self.directory) / 'baseline.json'
        self.state_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        config = json.loads(self.k('config', 'view', '--minify', '-o', 'json'))
        require(config['clusters'][0]['cluster']['server'] == SERVER, 'Wrong cluster API')
        self.lock = (self.state_path.parent / 'lock').open('w')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else None
        if self.state:
            require(self.state.get('config_id') == identity(self.settings), 'Saved configuration does not match target')

    def k(self, *args, payload=None, raw=None):
        result = subprocess.run([
            'kubectl', '--kubeconfig', self.settings['target']['kubeconfig'],
            '--context', CONTEXT, '--namespace', NAMESPACE,
            f'--request-timeout={self.settings["timing"]["request"]}', *args,
        ], input=raw if raw is not None else json.dumps(payload) if payload is not None else None,
            text=True, capture_output=True, check=True)
        return result.stdout

    def get(self, kind, name=None, *options):
        return json.loads(self.k('get', kind, *([name] if name else []), *options, '-o', 'json'))

    def optional(self, kind, name):
        result = self.k('get', kind, name, '--ignore-not-found', '-o', 'json')
        return json.loads(result) if result.strip() else None

    def save(self):
        temporary = self.state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.state, indent=2))
        temporary.replace(self.state_path)

    def baseline(self, workloads):
        if self.state:
            for name, saved in self.state['workloads'].items():
                require(self.get(saved['kind'], name)['metadata']['uid'] == saved['uid'],
                        f'{name} recreated; review saved baseline')
            return
        require(self.optional('nodepool', self.pool) is None, 'Reserved pool already exists')
        saved = {}
        for kind, name in workloads:
            resource = self.get(kind, name)
            require(resource['spec']['replicas'] > 0 and resource['status'].get('readyReplicas') ==
                    resource['spec']['replicas'], f'{name} not healthy')
            saved[name] = {'kind': kind, 'uid': resource['metadata']['uid'],
                           'replicas': resource['spec']['replicas'],
                           'spec': copy.deepcopy(resource['spec']['template']['spec']),
                           'annotations': resource['spec']['template']['metadata'].get('annotations', {})}
        self.state = {'token': str(uuid.uuid4()), 'workloads': saved, 'config_id': identity(self.settings)}
        self.save()

    def owned(self, kind, name):
        resource = self.optional(kind, name)
        if resource:
            require(self.state and resource['metadata'].get('labels', {}).get('injects.sre/owner') ==
                    self.state['token'], f'{kind}/{name} not owned by this scenario')
        return resource

    def create(self, resource):
        resource = copy.deepcopy(resource)
        resource.setdefault('metadata', {}).setdefault('labels', {})['injects.sre/owner'] = self.state['token']
        name, kind = resource['metadata']['name'], resource['kind']
        if not self.owned(kind, name):
            self.k('create', '-f', '-', payload=resource)

    def patch(self, kind, name, operations):
        resource = self.get(kind, name)
        if kind not in ('deployment', 'statefulset') or name not in self.state['workloads']:
            require(self.owned(kind, name) is not None, 'Resource not owned')
        else:
            require(resource['metadata']['uid'] == self.state['workloads'][name]['uid'], 'Workload UID changed')
        guard = [{'op': 'test', 'path': '/metadata/uid', 'value': resource['metadata']['uid']},
                 {'op': 'test', 'path': '/metadata/resourceVersion', 'value': resource['metadata']['resourceVersion']}]
        self.k('patch', kind, name, '--type=json', '--patch-file=/dev/stdin', payload=guard + operations)

    def pin(self, kind, name, affinity=None, resources=None, replicas=None):
        saved = self.state['workloads'][name]
        spec = saved['spec']
        selector = dict(spec.get('nodeSelector', {}), **{'injects.sre/pool': self.pool})
        tolerations = spec.get('tolerations', []) + [
            {'key': 'injects.sre/pool', 'operator': 'Equal', 'value': self.pool, 'effect': 'NoSchedule'}]
        operations = [
            {'op': 'add', 'path': '/spec/template/spec/nodeSelector', 'value': selector},
            {'op': 'add', 'path': '/spec/template/spec/tolerations', 'value': tolerations}]
        if affinity is not None:
            operations.append({'op': 'add', 'path': '/spec/template/spec/affinity', 'value': affinity})
        if resources is not None:
            operations.append({'op': 'add', 'path': '/spec/template/spec/containers/0/resources', 'value': resources})
        if replicas is not None:
            operations.append({'op': 'add', 'path': '/spec/replicas', 'value': replicas})
        self.patch(kind, name, operations)

    def rollout(self, kind, name, timeout=None):
        print(f'Waiting for {kind}/{name} rollout', flush=True)
        timeout = timeout or self.settings['timing']['rollout']
        self.k('rollout', 'status', f'{kind}/{name}', f'--timeout={timeout}s')

    def snapshots(self, names):
        result = {}
        for name in names:
            resource = self.get('statefulset', name)
            require(resource['status'].get('readyReplicas') == resource['spec']['replicas'], f'{name} not Ready')
            pod = self.get('pod', f'{name}-0')
            require(any(condition['type'] == 'Ready' and condition['status'] == 'True'
                        for condition in pod['status'].get('conditions', [])), f'{name} pod not Ready')
            result[name] = {'uid': pod['metadata']['uid'], 'node': pod['spec']['nodeName'],
                            'restarts': [status['restartCount'] for status in pod['status']['containerStatuses']]}
        return result

    def workload_ready(self, name, replicas, capacity=None):
        self.rollout('deployment', name)
        resource = self.get('deployment', name)
        require(resource['spec']['replicas'] == replicas and resource['status'].get('readyReplicas') == replicas
                and resource['status'].get('updatedReplicas') == replicas, 'Target replicas not Ready/updated')
        selector = self.selector(name)
        pods = [pod for pod in self.get('pods', None, '-l', selector)['items']
                if not pod['metadata'].get('deletionTimestamp')]
        require(len(pods) == replicas, 'Unexpected pod count')
        for pod in pods:
            require(pod['status']['phase'] == 'Running' and any(condition['type'] == 'Ready' and
                    condition['status'] == 'True' for condition in pod['status'].get('conditions', [])), 'Pod not Ready')
            node = self.get('node', pod['spec']['nodeName'])
            require(node['metadata']['labels'].get('karpenter.sh/nodepool') in self.pool_names(), 'Wrong pool placement')
            if capacity:
                require(node['metadata']['labels'].get('karpenter.sh/capacity-type') == capacity, 'Wrong capacity type')
        return pods

    def pool_names(self):
        return [self.pool]

    def selector(self, name):
        return next((workload['selector'] for workload in self.settings['workloads'].values()
                     if workload['name'] == name), f'app={name}')

    def pool_manifest(self, cpu='8', capacities=None, budget=None, cpu_sizes=None):
        settings = getattr(self, 'settings', SETTINGS)['nodepool']
        require(settings['nodeclass_ref']['name'], 'Configure nodepool.nodeclass_ref.name from live inspection')
        return {
            'apiVersion': settings['api_version'], 'kind': 'NodePool', 'metadata': {'name': self.pool},
            'spec': {'limits': {'cpu': cpu, 'memory': settings['memory_limit']},
                     'disruption': {'consolidationPolicy': 'WhenEmptyOrUnderutilized',
                                    'consolidateAfter': settings['consolidate_after'], 'budgets': [] if budget is None else budget},
                     'template': {'metadata': {'labels': dict(settings['labels'], **{'injects.sre/pool': self.pool})},
                                  'spec': {'expireAfter': 'Never', 'nodeClassRef': settings['nodeclass_ref'],
                                      'taints': [{'key': 'injects.sre/pool', 'value': self.pool, 'effect': 'NoSchedule'}],
                                      'startupTaints': settings['startup_taints'],
                                      'requirements': copy.deepcopy(settings['requirements']) + [
                                          {'key': 'karpenter.sh/capacity-type', 'operator': 'In', 'values': capacities or ['on-demand']},
                                          {'key': 'karpenter.azure.com/sku-cpu', 'operator': 'In', 'values': cpu_sizes or settings['cpu_sizes']},
                                      ]}}}}

    def delete_owned(self, kind, name, api_path):
        resource = self.owned(kind, name)
        if resource:
            self.k('delete', '--raw', api_path, '-f', '-', payload={
                'apiVersion': 'v1', 'kind': 'DeleteOptions',
                'preconditions': {'uid': resource['metadata']['uid']}, 'propagationPolicy': 'Background'})
            self.k('wait', '--for=delete', f'{kind}/{name}', f'--timeout={self.settings["timing"]["delete"]}s')

    def restore(self, fields):
        for name, saved in self.state['workloads'].items():
            operations = [{'op': 'add', 'path': '/spec/replicas', 'value': saved['replicas']}]
            for field in fields:
                value = saved['spec'].get(field, [] if field == 'tolerations' else {})
                operations.append({'op': 'add', 'path': f'/spec/template/spec/{field}', 'value': value})
            self.patch(saved['kind'], name, operations)
            self.rollout(saved['kind'], name)

    def cleanup_pool(self):
        nodes = self.get('nodes', None, '-l', f'karpenter.sh/nodepool={self.pool}')['items']
        node_names = {node['metadata']['name'] for node in nodes}
        scenario_pods = set()
        for name in self.state['workloads']:
            scenario_pods.update(pod['metadata']['uid'] for pod in self.get(
                'pods', None, '-l', self.selector(name))['items'])

        def drained():
            waiting = False
            for pod in self.get('pods', None, '--all-namespaces')['items']:
                if pod['spec'].get('nodeName') not in node_names:
                    continue
                if any(owner['kind'] == 'DaemonSet' for owner in pod['metadata'].get('ownerReferences', [])):
                    continue
                if (pod['metadata']['namespace'] == NAMESPACE and
                    pod['metadata']['uid'] in scenario_pods and
                    pod['metadata'].get('deletionTimestamp')):
                    waiting = True
                    continue
                require(False, f'Refusing node deletion while pod {pod["metadata"]["namespace"]}/{pod["metadata"]["name"]} remains')
            return not waiting

        bounded(drained, self.settings['timing']['delete'], 'scenario workload pods finishing termination')
        self.delete_owned('nodepool', self.pool, f'/apis/{self.settings["nodepool"]["api_version"]}/nodepools/{self.pool}')
        for kind in ['nodeclaims', 'nodes']:
            if self.get(kind, None, '-l', f'karpenter.sh/nodepool={self.pool}')['items']:
                self.k('wait', '--for=delete', kind, '-l', f'karpenter.sh/nodepool={self.pool}', f'--timeout={self.settings["timing"]["delete"]}s')


def bounded(check, seconds, description):
    deadline = time.monotonic() + seconds
    while True:
        if check():
            return
        if time.monotonic() >= deadline:
            raise RuntimeError(f'Timed out: {description}')
        time.sleep(5)