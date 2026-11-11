import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('manifest', HERE / 'manifest.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copy(HERE.parent / 'config.py', self.root / 'config.py')
        for folder in ('01-crashloop-secret', '02-nodepool-limits'):
            shutil.copytree(HERE.parent / folder, self.root / folder,
                            ignore=shutil.ignore_patterns('.state', '__pycache__'))
        self.settings = copy.deepcopy(generator.config.DEFAULTS)
        self.settings['target'] = {'context': 'offline-context', 'namespace': 'tenant-blue',
                                   'server': 'https://offline.invalid', 'kubeconfig': '/offline/config'}
        self.settings['workloads']['order'].update(name='checkout', container='checkout-container',
                                                    selector='component=checkout', image='')
        self.settings['workloads']['customer'].update(name='buyer', container='buyer-container',
                                                       selector='component=buyer', image='')
        self.settings['broker'].update(secret='checkout-secret', configmap='checkout-config',
                                       password_key='credential.key', password_env='CHECKOUT_PASSWORD',
                                       hostname_key='HOST', port_key='PORT', queue_key='QUEUE',
                                       host='queue.internal', port='5673', queue='checkout')
        self.settings['scenarios']['02'].update(pool='portable-pool', cpu_limit='3',
                                                memory_limit='12Gi', cpu_sizes=['4', '8'], replicas=5)
        self.settings['nodepool'].update(
            api_version='karpenter.sh/v1beta1',
            nodeclass_ref={'group': 'example.invalid', 'kind': 'PortableClass', 'name': 'portable-class'},
            labels={'kubernetes.azure.com/mode': 'portable', 'kubernetes.azure.com/ebpf-dataplane': 'other'},
            startup_taints=[], consolidate_after='45s',
            requirements=[{'key': 'kubernetes.io/arch', 'operator': 'In', 'values': ['arm64']}])
        self.fixtures = {}
        self.log = self.root / 'calls.jsonl'
        binary = self.root / 'bin'
        binary.mkdir()
        fake = binary / 'kubectl'
        fake.write_text(f'#!{sys.executable}\n' + '''import json, os, sys
from pathlib import Path
args = sys.argv[5:]
payload = sys.stdin.read() if any(item in args for item in ("--patch-file=/dev/stdin", "create", "--raw", "exec")) else ""
with open(os.environ["CALL_LOG"], "a") as stream:
    stream.write(json.dumps({"global": sys.argv[1:5], "args": args, "payload": payload}) + "\\n")
fixtures = json.loads(Path(os.environ["FIXTURES"]).read_text())
key = " ".join(args[:3])
if args[:2] == ["config", "view"]:
    print("https://offline.invalid")
elif args[0] in ("patch", "create", "rollout", "wait", "delete", "exec"):
    pass
elif key in fixtures:
    value = fixtures[key]
    print(value if isinstance(value, str) else json.dumps(value))
else:
    raise SystemExit("Unexpected fake kubectl call: " + key)
''')
        fake.chmod(0o700)
        self.environment = {**os.environ, 'PATH': f'{binary}:{os.environ["PATH"]}',
                            'INJECT_CONFIG': str(self.root / 'target.json'),
                            'FIXTURES': str(self.root / 'fixtures.json'), 'CALL_LOG': str(self.log),
                            'PYTHONDONTWRITEBYTECODE': '1'}
        for role in ('order', 'customer'):
            workload = self.settings['workloads'][role]
            self.fixtures[f'get deployment {workload["name"]}'] = {
                'metadata': {'uid': f'{role}-uid', 'resourceVersion': '1'},
                'spec': {'replicas': 1, 'template': {'spec': {'containers': [{
                    'name': workload['container'], 'image': 'custom:image',
                    'envFrom': [{'secretRef': {'name': 'checkout-secret'}}]}]}}},
                'status': {'readyReplicas': 1}}
        self.fixtures.update({
            'get secret checkout-secret': {'metadata': {'uid': 'secret-uid'}, 'data': {'credential.key': 'b2s='}},
            'get configmap checkout-config': {'data': {'HOST': 'queue.internal', 'PORT': '5673', 'QUEUE': 'checkout'}},
            'get pods -l': {'items': [{'metadata': {'uid': 'pod-uid'}, 'spec': {'nodeName': 'node'},
                                       'status': {'phase': 'Running', 'conditions': [{'type': 'Ready', 'status': 'True'}],
                                                  'containerStatuses': [{'name': 'checkout-container', 'ready': True, 'restartCount': 0}]}}]},
            'get PortableClass.example.invalid portable-class': {'status': {'conditions': [{'type': 'Ready', 'status': 'True'}]}},
            'get nodepool portable-pool': '',
            'get pods --all-namespaces': {'items': []}, 'get nodes -l': {'items': []},
            'get nodeclaims -l': '',
        })

    def run_script(self, number, script='inject.sh', *arguments):
        Path(self.environment['INJECT_CONFIG']).write_text(json.dumps(self.settings))
        Path(self.environment['FIXTURES']).write_text(json.dumps(self.fixtures))
        folder = '01-crashloop-secret' if number == '01' else '02-nodepool-limits'
        return subprocess.run(['bash', str(self.root / folder / script), *arguments],
                              env=self.environment, text=True, capture_output=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def state(self, number):
        folder = '01-crashloop-secret' if number == '01' else '02-nodepool-limits'
        return self.root / folder / '.state' / generator.config.identity(self.settings) / 'baseline.json'

    def test_incomplete_target_fails_before_any_cluster_command(self):
        self.settings['target']['context'] = ''
        for number in ('01', '02'):
            self.assertNotEqual(self.run_script(number).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_missing_nodeclass_fails_before_any_cluster_command(self):
        self.settings['nodepool']['nodeclass_ref']['name'] = ''
        self.assertNotEqual(self.run_script('02').returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_configured_targets_and_isolated_state(self):
        for number in ('01', '02'):
            result = self.run_script(number, 'inject.sh', '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            state = self.state(number)
            self.assertTrue(state.exists())
            self.assertTrue(state.with_name('lock').exists())
            self.assertEqual(state.stat().st_mode & 0o777, 0o600)
            old_state = state
            self.settings['target']['namespace'] = 'tenant-green'
            self.assertNotEqual(old_state, self.state(number))
            self.assertFalse(self.state(number).exists())
            self.settings['target']['namespace'] = 'tenant-blue'
        for call in self.calls():
            self.assertEqual(call['global'], ['--kubeconfig=/offline/config', '--context=offline-context',
                                              '--namespace=tenant-blue', '--request-timeout=30s'])
        created = next(call for call in self.calls() if call['args'][0] == 'create')
        manifest = json.loads(created['payload'])
        self.assertEqual(manifest['metadata']['name'], 'portable-pool')
        self.assertEqual(manifest['spec']['limits']['cpu'], '3')
        patched = [json.loads(call['payload']) for call in self.calls()
                   if call['args'][:3] == ['patch', 'deployment', 'buyer']]
        self.assertEqual(patched[0][2]['value'], 5)
        secret_patch = next(json.loads(call['payload']) for call in self.calls()
                            if call['args'][:3] == ['patch', 'secret', 'checkout-secret'])
        self.assertEqual(secret_patch[1]['path'], '/data/credential.key')

    def test_optional_images_and_one_container_contract(self):
        for number, role in (('01', 'order'), ('02', 'customer')):
            self.settings['workloads'][role]['image'] = 'required:image'
            self.assertNotEqual(self.run_script(number).returncode, 0)
            self.settings['workloads'][role]['image'] = ''
            name = self.settings['workloads'][role]['name']
            containers = self.fixtures[f'get deployment {name}']['spec']['template']['spec']['containers']
            containers.append(copy.deepcopy(containers[0]))
            self.assertNotEqual(self.run_script(number).returncode, 0)
            containers.pop()

    def test_recreated_deployments_keep_uid_guards(self):
        for number, name in (('01', 'checkout'), ('02', 'buyer')):
            result = self.run_script(number, 'inject.sh', '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.fixtures[f'get deployment {name}']['metadata']['uid'] = 'replacement'
            result = self.run_script(number, 'reset.sh')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('recreated', result.stderr)

    def test_verifier_passes_config_not_credentials(self):
        result = self.run_script('01', 'verify.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        call = next(call for call in self.calls() if call['args'][0] == 'exec')
        self.assertEqual(call['args'][1:8], ['-i', 'deployment/checkout', '-c', 'checkout-container', '--', 'node', '-'])
        self.assertEqual(json.loads(call['args'][8]), self.settings['broker'])
        self.assertEqual(json.loads(call['args'][9]), self.settings['timing'])

    def test_namespace_and_configuration_changes_do_not_reuse_baselines(self):
        for number in ('01', '02'):
            result = self.run_script(number, 'inject.sh', '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            original = self.state(number)
            baseline = original.read_text()
            self.settings['target']['namespace'] = 'another-namespace'
            result = self.run_script(number, 'reset.sh')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No saved', result.stderr)
            self.settings['target']['namespace'] = 'tenant-blue'
            self.settings['timing']['stability'] += 1
            result = self.run_script(number, 'reset.sh')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No saved', result.stderr)
            self.settings['timing']['stability'] -= 1
            self.assertEqual(original.read_text(), baseline)

    def test_secret_identity_and_external_rotation_guards(self):
        result = self.run_script('01', 'inject.sh', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        secret = self.fixtures['get secret checkout-secret']
        secret['metadata']['uid'] = 'replacement'
        result = self.run_script('01', 'reset.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('recreated', result.stderr)
        secret['metadata']['uid'] = 'secret-uid'
        secret['data']['credential.key'] = 'cm90YXRlZA=='
        result = self.run_script('01', 'reset.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Credential changed', result.stderr)

    def test_reset_uses_configured_api_and_preserves_ownership_guard(self):
        self.settings['timing'].update(rollout=47, delete=49)
        result = self.run_script('02', 'inject.sh', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.state('02').read_text())
        self.fixtures['get nodepool portable-pool'] = {
            'metadata': {'uid': 'pool-uid', 'labels': {'injects.sre/owner': 'someone-else'}}}
        result = self.run_script('02', 'reset.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not owned', result.stderr)
        self.fixtures['get nodepool portable-pool']['metadata']['labels']['injects.sre/owner'] = state['token']
        result = self.run_script('02', 'reset.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        deletion = next(call for call in self.calls() if call['args'][0] == 'delete')
        self.assertIn('/apis/karpenter.sh/v1beta1/nodepools/portable-pool', deletion['args'])
        self.assertEqual(json.loads(deletion['payload'])['preconditions'], {'uid': 'pool-uid'})
        rollout = next(call for call in self.calls() if call['args'][0] == 'rollout')
        self.assertEqual(rollout['args'], ['rollout', 'status', 'deployment/buyer', '--timeout=47s'])
        self.assertTrue(any('--timeout=49s' in call['args'] for call in self.calls()))

    def test_manifest_overrides_all_portable_fields(self):
        result = generator.manifest(self.settings, 'owner-token')
        self.assertEqual(result['apiVersion'], 'karpenter.sh/v1beta1')
        self.assertEqual(result['metadata']['labels'], {'injects.sre/owner': 'owner-token'})
        self.assertEqual(result['spec']['limits'], {'cpu': '3', 'memory': '12Gi'})
        template = result['spec']['template']
        self.assertEqual(template['metadata']['labels'],
                 {**self.settings['nodepool']['labels'], 'injects.sre/scenario02': 'limits'})
        self.assertEqual(template['spec']['nodeClassRef'], self.settings['nodepool']['nodeclass_ref'])
        self.assertEqual(template['spec']['startupTaints'], [])
        self.assertEqual(template['spec']['taints'],
                 [{'key': 'injects.sre/scenario02', 'value': 'limits', 'effect': 'NoSchedule'}])
        self.assertEqual(result['spec']['disruption']['budgets'], [{'nodes': '0'}])
        self.assertEqual(result['spec']['disruption']['consolidateAfter'], '45s')
        requirements = {entry['key']: entry['values'] for entry in template['spec']['requirements']}
        self.assertEqual(requirements['kubernetes.io/arch'], ['arm64'])
        self.assertEqual(requirements['karpenter.azure.com/sku-cpu'], ['4', '8'])
        self.assertNotIn('lab-scaling', json.dumps(result))

    def test_verifier_uses_configured_replicas_selector_and_pool(self):
        result = self.run_script('02', 'inject.sh', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.state('02').read_text())
        self.fixtures['get nodepool portable-pool'] = {
            'metadata': {'uid': 'pool-uid', 'labels': {'injects.sre/owner': state['token']}}}
        deployment = self.fixtures['get deployment buyer']
        deployment['metadata']['generation'] = 2
        deployment['spec']['replicas'] = 5
        deployment['spec']['template']['spec']['nodeSelector'] = {'injects.sre/scenario02': 'limits'}
        deployment['status'] = {'observedGeneration': 2, 'readyReplicas': 5,
                                'updatedReplicas': 5, 'availableReplicas': 5}
        self.fixtures['get pods -l'] = {'items': [
            {'metadata': {'uid': f'buyer-{index}'}, 'spec': {'nodeName': 'portable-node'},
             'status': {'phase': 'Running', 'conditions': [{'type': 'Ready', 'status': 'True'}]}}
            for index in range(5)]}
        self.fixtures['get node portable-node'] = {
            'metadata': {'labels': {'karpenter.sh/nodepool': 'portable-pool', 'injects.sre/scenario02': 'limits'}},
            'status': {'conditions': [{'type': 'Ready', 'status': 'True'}]}}
        result = self.run_script('02', 'verify.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('all 5 replicas Ready', result.stdout)
        self.assertTrue(any('component=buyer' in call['args'] for call in self.calls()))
        self.fixtures['get pods -l']['items'].pop()
        result = self.run_script('02', 'verify.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Pending, missing or unready', result.stderr)


if __name__ == '__main__':
    unittest.main()