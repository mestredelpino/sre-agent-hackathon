import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import urllib.parse
import uuid

from config import identity, target
from runtime import Runtime, SETTINGS, require


FOLDERS = {'07': '07-network-policy', '08': '08-ingress-backend', '09': '09-service-selector'}


def label_selector(labels):
    require(labels, 'An empty selector would target the entire namespace')
    return ','.join(f'{key}={value}' for key, value in sorted(labels.items()))


def policy_manifest(deployment, name, namespace, token):
    selector = deployment['spec']['selector']
    require(selector.get('matchLabels') and not selector.get('matchExpressions'),
            'NetworkPolicy scenario requires a nonempty matchLabels-only deployment selector')
    return {'apiVersion': 'networking.k8s.io/v1', 'kind': 'NetworkPolicy',
            'metadata': {'name': name, 'namespace': namespace, 'labels': {'injects.sre/owner': token}},
            'spec': {'podSelector': copy.deepcopy(selector), 'policyTypes': ['Ingress'], 'ingress': []}}


def selected(selector, labels):
    if not all(labels.get(key) == value for key, value in selector.get('matchLabels', {}).items()):
        return False
    for expression in selector.get('matchExpressions', []):
        actual = labels.get(expression['key'])
        operator = expression['operator']
        values = expression.get('values', [])
        require(operator in ('In', 'NotIn', 'Exists', 'DoesNotExist'), 'Unsupported label selector operator')
        matches = {'In': actual is not None and actual in values,
                   'NotIn': actual is None or actual not in values,
                   'Exists': actual is not None, 'DoesNotExist': actual is None}
        if not matches[operator]:
            return False
    return True


def ingress_backend(resource, options):
    routes = [(rule_index, path_index, path)
              for rule_index, rule in enumerate(resource['spec'].get('rules', []))
              if rule.get('host', '') == options['host']
              for path_index, path in enumerate(rule.get('http', {}).get('paths', []))
              if path['path'] == options['path'] and path['pathType'] == options['path_type']]
    require(len(routes) == 1, 'Expected exactly one Ingress host/path/pathType match')
    rule_index, path_index, path = routes[0]
    require('service' in path['backend'] and 'resource' not in path['backend'],
            'Only Service-backed Ingress routes are supported')
    return f'/spec/rules/{rule_index}/http/paths/{path_index}/backend', copy.deepcopy(path['backend'])


def service_selector(resource):
    require(resource['spec'].get('type', 'ClusterIP') != 'ExternalName' and
            resource['spec'].get('clusterIP') != 'None', 'ExternalName/headless Services are unsupported')
    selector = resource['spec'].get('selector')
    require(isinstance(selector, dict) and selector, 'Selectorless Services are unsupported')
    return copy.deepcopy(selector)


def ready_endpoints(slices):
    return [endpoint for item in slices['items'] for endpoint in item.get('endpoints', [])
            if endpoint.get('conditions', {}).get('ready') is not False and endpoint.get('addresses')]


def validate_options(settings, number):
    target(settings)
    options = settings['scenarios'][number]
    name_key = {'07': 'deployment', '08': 'ingress', '09': 'service'}[number]
    require(options[name_key], f'Configure scenarios.{number}.{name_key}')
    probe = options['probe']
    require(all(probe[key] for key in ('pod', 'container', 'executable', 'url')), 'Configure an existing client pod/container and probe URL')
    url = urllib.parse.urlsplit(probe['url'])
    require(url.scheme in ('http', 'https') and url.hostname and not url.username and not url.password,
            'Probe requires an HTTP(S) URL without credentials')
    require(probe['timeout_seconds'] > 0 and probe['healthy_statuses'] and
            all(200 <= status < 300 for status in probe['healthy_statuses']), 'Configure positive timeout and healthy HTTP 2xx statuses')
    require(probe['broken_statuses'] and all(status == 0 or 400 <= status <= 599
            for status in probe['broken_statuses']), 'Broken statuses must be HTTP errors or transport failure (0)')
    require(set(probe['broken_errors']) <= {'ETIMEDOUT', 'ECONNREFUSED', 'ECONNRESET'},
            'DNS/TLS failures are not accepted as evidence of these faults')
    if number == '07':
        require(options['enforcement_confirmed'] is True, 'Confirm NetworkPolicy enforcement before setting enforcement_confirmed=true')
        require(options['policy_name'], 'Configure a reserved policy name')
    if number == '08':
        require(options['wrong_service'] and 1 <= options['wrong_port'] <= 65535, 'Configure a missing backend Service and numeric port')
    return options


def probe_request(client, options):
    settings = options['probe']
    pod = client.get('pod', settings['pod'])
    require(not pod['metadata'].get('deletionTimestamp') and
            any(container['name'] == settings['container'] for container in pod['spec']['containers']),
            'Probe client pod/container is unavailable')
    script = (Path(__file__).parent / 'network-probe.cjs').read_text()
    result = json.loads(client.k('exec', '-i', settings['pod'], '-c', settings['container'], '--',
                                 settings['executable'], '-', json.dumps(settings), raw=script))
    return result


def check_probe(client, options, broken):
    result = probe_request(client, options)
    settings = options['probe']
    if result['status'] == 0:
        require(broken and 0 in settings['broken_statuses'] and result.get('error') in settings['broken_errors'],
                f'Unexpected transport error: {result}; not evidence of the intended fault')
    else:
        require(result['status'] in settings['broken_statuses' if broken else 'healthy_statuses'],
                f'Unexpected HTTP outcome: {result}; inspect the path and allow controller/CNI propagation')
    print('Request check passed: ' + json.dumps(result))


class NetworkScenario:
    def __init__(self, client, settings, number):
        self.client, self.settings, self.number = client, settings, number
        self.options = validate_options(settings, number)
        self.kind = {'07': 'deployment', '08': 'ingress', '09': 'service'}[number]
        self.name = self.options[self.kind]

    def resource(self):
        resource = self.client.get(self.kind, self.name)
        if self.client.state:
            require(resource['metadata']['uid'] == self.client.state['subject_uid'], 'Target resource was recreated; review baseline')
        return resource

    def policy(self):
        policy = self.client.optional('networkpolicy', self.options['policy_name'])
        if policy:
            state = self.client.state
            require(state and policy['metadata'].get('labels', {}).get('injects.sre/owner') == state['token'],
                    'Reserved NetworkPolicy exists and is not owned')
            require(not state.get('policy_uid') or policy['metadata']['uid'] == state['policy_uid'],
                    'NetworkPolicy recreated; review saved identity')
        return policy

    def value(self, resource):
        if self.number == '07':
            policy = self.policy()
            if not policy:
                return None
            spec = copy.deepcopy(policy['spec'])
            spec.setdefault('ingress', [])
            return spec
        if self.number == '08':
            return ingress_backend(resource, self.options)[1]
        return service_selector(resource)

    def check_policy_scope(self, deployment):
        manifest = policy_manifest(deployment, self.options['policy_name'], self.settings['target']['namespace'], 'preview')
        selector = manifest['spec']['podSelector']['matchLabels']
        pods = self.client.get('pods', None, '-l', label_selector(selector))['items']
        require(pods, 'Target deployment has no pods')
        client = self.client.get('pod', self.options['probe']['pod'])
        require(not client['spec'].get('hostNetwork') and
                not selected(manifest['spec']['podSelector'], client['metadata'].get('labels', {})),
                'Probe must use ordinary networking and must not belong to the isolated deployment')
        policies = self.client.get('networkpolicies')['items']
        for pod in pods:
            require(not pod['spec'].get('hostNetwork'), 'hostNetwork target pods are unsupported')
            owners = [owner for owner in pod['metadata'].get('ownerReferences', [])
                      if owner['kind'] == 'ReplicaSet' and owner.get('controller')]
            require(len(owners) == 1, 'Selected pod is not owned by a deployment ReplicaSet')
            replica = self.client.get('replicaset', owners[0]['name'])
            require(replica['metadata']['uid'] == owners[0]['uid'] and any(
                owner['kind'] == 'Deployment' and owner['uid'] == deployment['metadata']['uid']
                and owner.get('controller') for owner in replica['metadata'].get('ownerReferences', [])),
                'Selector includes a pod from another workload')
            for policy in policies:
                spec = policy['spec']
                ingress_types = spec.get('policyTypes', ['Ingress'])
                require(not ('Ingress' in ingress_types and spec.get('ingress') and
                             selected(spec['podSelector'], pod['metadata'].get('labels', {}))),
                        'An existing additive allow NetworkPolicy could defeat this deny; inspect instead of deleting it')

    def new_state(self, resource):
        token = str(uuid.uuid4())
        before = self.value(resource)
        if self.number == '07':
            self.check_policy_scope(resource)
            after = policy_manifest(resource, self.options['policy_name'], self.settings['target']['namespace'], token)['spec']
        elif self.number == '08':
            require(self.client.optional('service', self.options['wrong_service']) is None, 'Wrong backend Service must not exist')
            require(self.client.optional('service', before['service']['name']) is not None, 'Original backend Service is missing')
            after = {'service': {'name': self.options['wrong_service'], 'port': {'number': self.options['wrong_port']}}}
        else:
            after = {'injects.sre/missing': token}
            require(not self.client.get('pods', None, '-l', label_selector(after))['items'], 'Fault selector unexpectedly matches pods')
            require(ready_endpoints(self.client.get('endpointslices', None, '-l', f'kubernetes.io/service-name={self.name}')),
                    'Original Service has no ready EndpointSlice addresses')
        check_probe(self.client, self.options, False)
        return {'config_id': identity(self.settings), 'token': token, 'subject_uid': resource['metadata']['uid'],
                'before': before, 'after': after}

    def write(self, resource, replacement):
        if self.number == '07':
            if replacement is not None:
                manifest = policy_manifest(resource, self.options['policy_name'], self.settings['target']['namespace'], self.client.state['token'])
                self.client.k('create', '-f', '-', payload=manifest)
                policy = self.policy()
                require(policy is not None, 'NetworkPolicy create not confirmed')
                self.client.state['policy_uid'] = policy['metadata']['uid']
                self.client.save()
            else:
                policy = self.policy()
                self.client.k('delete', '--raw', '/apis/networking.k8s.io/v1/namespaces/' +
                              self.settings['target']['namespace'] + '/networkpolicies/' + self.options['policy_name'],
                              '-f', '-', payload={'apiVersion': 'v1', 'kind': 'DeleteOptions',
                                  'preconditions': {'uid': policy['metadata']['uid'],
                                                    'resourceVersion': policy['metadata']['resourceVersion']}})
                self.client.k('wait', '--for=delete', f'networkpolicy/{self.options["policy_name"]}',
                              f'--timeout={self.settings["timing"]["delete"]}s')
        else:
            pointer = ingress_backend(resource, self.options)[0] if self.number == '08' else '/spec/selector'
            self.client.k('patch', self.kind, self.name, '--type=json', '--patch-file=/dev/stdin', payload=[
                {'op': 'test', 'path': '/metadata/uid', 'value': resource['metadata']['uid']},
                {'op': 'test', 'path': '/metadata/resourceVersion', 'value': resource['metadata']['resourceVersion']},
                {'op': 'replace', 'path': pointer, 'value': replacement}])

    def run(self, action, apply=False, plan=False, expect='healthy'):
        require(not plan or action == 'inject', '--plan is supported only with inject')
        resource = self.resource()
        current = self.value(resource)
        state = self.client.state
        if action == 'inject' and (not apply or plan):
            if self.number == '07':
                self.check_policy_scope(resource)
            preview = policy_manifest(resource, self.options['policy_name'], self.settings['target']['namespace'], 'preview') if self.number == '07' else self.options
            print('PLAN: ' + json.dumps({'scenario': self.number, 'target': self.settings['target'],
                                        'resource': f'{self.kind}/{self.name}', 'current': current, 'fault': preview,
                                        'mutation': False}))
            return
        if action == 'verify':
            require(state is not None, 'No saved baseline; cannot verify original settings')
            broken = expect == 'broken'
            require(current == state['after' if broken else 'before'], 'Affected settings do not match requested verification state')
            if self.number == '07' and broken:
                self.check_policy_scope(resource)
            if self.number == '08' and broken:
                require(self.client.optional('service', self.options['wrong_service']) is None, 'Fault backend Service now exists')
            if self.number == '09':
                endpoints = ready_endpoints(self.client.get('endpointslices', None, '-l', f'kubernetes.io/service-name={self.name}'))
                require(not endpoints if broken else bool(endpoints), 'Service EndpointSlices do not match expected state; retry after convergence')
            check_probe(self.client, self.options, broken)
            print(f'PASS: scenario {self.number} configuration and real request match {expect}')
            return
        require(apply, 'Reset/mutation requires explicit --apply')
        if action == 'inject':
            require(not state or not state.get('reset_complete'), 'Archive completed baseline privately before a fresh rehearsal')
            if not state:
                self.client.state = self.new_state(resource)
                self.client.save()
                state = self.client.state
            if self.number == '07':
                self.check_policy_scope(resource)
            if self.number == '08':
                require(self.client.optional('service', self.options['wrong_service']) is None, 'Fault backend Service now exists')
            replacement = state['after']
        else:
            require(state is not None, 'No saved baseline; refusing reset')
            replacement = state['before']
        require(current in (state['before'], state['after']), 'Affected settings drifted; refusing overwrite')
        if current != replacement:
            self.write(resource, replacement)
        require(self.value(self.resource()) == replacement, 'Mutation not confirmed; preserve baseline and inspect')
        if action == 'reset':
            state['reset_complete'] = True
            self.client.save()
        print(f'{action} configuration confirmed. Run verify --expect {"healthy" if action == "reset" else "broken"} after propagation.')


def main():
    parser = argparse.ArgumentParser(description='Namespace-scoped Kubernetes network fault rehearsals')
    parser.add_argument('scenario', choices=FOLDERS)
    parser.add_argument('action', choices=['inject', 'verify', 'reset'])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--expect', choices=['healthy', 'broken'], default='healthy')
    arguments = parser.parse_args()
    validate_options(SETTINGS, arguments.scenario)
    client = Runtime(Path(__file__).parent / FOLDERS[arguments.scenario], '')
    try:
        NetworkScenario(client, SETTINGS, arguments.scenario).run(arguments.action, arguments.apply,
                                                                arguments.plan, arguments.expect)
    finally:
        client.lock.close()


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)