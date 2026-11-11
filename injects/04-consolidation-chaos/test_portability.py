import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import config
import runtime


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(config.DEFAULTS)
        self.settings['target'] = {'context': 'offline-context', 'namespace': 'alternate-space',
                                   'server': 'https://offline.invalid', 'kubeconfig': '/offline/config'}
        self.settings['workloads']['database']['name'] = 'inventory-db'
        self.settings['workloads']['broker']['name'] = 'message-bus'
        self.settings['workloads']['order'].update(name='checkout', container='publisher')
        self.settings['nodepool']['api_version'] = 'karpenter.sh/v9'
        self.settings['nodepool']['nodeclass_ref']['name'] = 'alternate-class'
        self.settings['scenarios']['04'].update(pool='alternate-pool', filler='pressure',
            filler_image='example.invalid/filler:test', filler_cpu='3', filler_low_cpu='7m',
            filler_memory='96Mi', cpu_limit='12', witness_queue='proof / queue')
        self.settings['timing'].update(protection=7, consolidation=23, delete=19)
        self.block_calls = patch('subprocess.run', side_effect=AssertionError('No live calls allowed'))
        self.block_calls.start()
        self.addCleanup(self.block_calls.stop)
        module_spec = importlib.util.spec_from_file_location('scenario04_offline', HERE / 'scenario.py')
        self.scenario = importlib.util.module_from_spec(module_spec)
        with patch.object(runtime, 'SETTINGS', self.settings):
            module_spec.loader.exec_module(self.scenario)
        self.client = Mock()
        self.client.state = {'workloads': {}, 'token': 'offline'}

    def resource(self, expressions=None):
        selector = {'matchLabels': {'role': 'data', 'team': 'alternate'}}
        if expressions:
            selector['matchExpressions'] = expressions
        return {'spec': {'replicas': 1, 'selector': selector, 'template': {'spec': {}}}}

    def test_manifests_and_exec_use_settings(self):
        manifest = self.scenario.filler(self.client)
        self.assertEqual(manifest['metadata']['name'], 'pressure')
        template = manifest['spec']['template']
        self.assertEqual(template['metadata']['labels'], manifest['spec']['selector']['matchLabels'])
        self.assertEqual(template['spec']['nodeSelector']['injects.sre/pool'], 'alternate-pool')
        container = template['spec']['containers'][0]
        self.assertEqual(container['image'], 'example.invalid/filler:test')
        self.assertEqual(container['resources'], {
            'requests': {'cpu': '3', 'memory': '96Mi'}, 'limits': {'cpu': '3', 'memory': '96Mi'}})
        with contextlib.redirect_stdout(io.StringIO()):
            self.scenario.witness(self.client, 'seed')
        args = self.client.k.call_args.args
        self.assertEqual(args[:10], ('exec', '-i', 'deployment/checkout', '-c', 'publisher', '--', 'node', '-', 'seed', json.dumps(self.settings['broker'])))
        self.assertEqual(json.loads(args[10])['scenario']['witness_queue'], 'proof / queue')

    def test_pdb_uses_actual_selector_and_rejects_expressions(self):
        self.client.get.return_value = self.resource()
        pdb = self.scenario.pdb_manifest(self.client, 'inventory-db')
        self.assertEqual(pdb['spec']['selector']['matchLabels'], {'role': 'data', 'team': 'alternate'})
        self.client.get.return_value = self.resource(expressions=[{'key': 'role', 'operator': 'Exists'}])
        with self.assertRaisesRegex(RuntimeError, 'matchExpressions'):
            self.scenario.pdb_manifest(self.client, 'inventory-db')
        self.client.get.return_value = {'spec': {'selector': {'matchLabels': {}}}}
        with self.assertRaisesRegex(RuntimeError, 'must not be empty'):
            self.scenario.pdb_manifest(self.client, 'inventory-db')

    def verifier_client(self, pdb_labels):
        self.client.owned.return_value = {'spec': {'disruption': {'budgets': [{'nodes': '0'}]}}}
        def get(kind, name=None):
            if kind == 'statefulset':
                return self.resource()
            if kind == 'pod':
                return {'metadata': {'labels': {'role': 'data', 'team': 'alternate', 'extra': 'label'}},
                        'spec': {'nodeName': 'offline-node'}}
            if kind == 'pdb':
                return {'items': [{'metadata': {'generation': 2},
                    'spec': {'selector': {'matchLabels': pdb_labels}, 'minAvailable': 1},
                    'status': {'observedGeneration': 2, 'currentHealthy': 1, 'disruptionsAllowed': 0}}]}
            if kind == 'node':
                return {'metadata': {'labels': {'karpenter.sh/nodepool': 'alternate-pool'}}}
            raise AssertionError(kind)
        self.client.get.side_effect = get

    def test_verifier_matches_real_labels_and_configured_window(self):
        self.verifier_client({'team': 'alternate'})
        with patch.object(self.scenario, 'resize') as resize, \
             patch.object(self.scenario.time, 'monotonic', side_effect=[100, 101, 108]), \
             patch.object(self.scenario.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()) as output:
            self.scenario.verify(self.client)
        self.assertEqual([call.args[1] for call in resize.call_args_list], ['3', '7m'])
        self.assertIn('7 seconds', output.getvalue())
        self.assertEqual(self.client.snapshots.call_args.args[0], ['inventory-db', 'message-bus'])

    def test_verifier_rejects_nonmatching_pdb(self):
        self.verifier_client({'app': 'inventory-db'})
        with self.assertRaisesRegex(RuntimeError, 'effective PDB'):
            self.scenario.verify(self.client)

    def test_plan_and_reset_use_target_names_and_paths(self):
        self.client.get.side_effect = lambda kind, *args: {'items': []} if kind == 'pods' else self.resource()
        with patch.object(self.scenario, 'Runtime', return_value=self.client), \
             patch.object(sys, 'argv', ['scenario.py', 'inject', '--plan']), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.scenario.main()
        self.assertIn('inventory-db, message-bus', output.getvalue())
        self.assertIn('alternate-pool pool in alternate-space', output.getvalue())
        self.assertIn('ceiling 12', output.getvalue())
        self.client.create.assert_not_called()
        with patch.object(self.scenario, 'Runtime', return_value=self.client), \
             patch.object(sys, 'argv', ['scenario.py', 'reset']), \
             patch.object(self.scenario, 'witness'), \
             patch.object(self.scenario, 'bounded') as bounded, contextlib.redirect_stdout(io.StringIO()):
            self.scenario.main()
        paths = [call.args[2] for call in self.client.delete_owned.call_args_list]
        self.assertEqual(paths, [
            '/apis/policy/v1/namespaces/alternate-space/poddisruptionbudgets/inject04-inventory-db',
            '/apis/policy/v1/namespaces/alternate-space/poddisruptionbudgets/inject04-message-bus',
            '/apis/apps/v1/namespaces/alternate-space/deployments/pressure'])
        self.assertEqual(bounded.call_args.args[1], 19)
        self.assertTrue(bounded.call_args.args[0]())
        self.client.get.assert_called_with('pods', None, '-l', 'app=pressure')

    def test_pool_and_state_use_shared_configuration(self):
        client = object.__new__(runtime.Runtime)
        client.settings = self.settings
        client.pool = self.scenario.POOL
        client.state = {'workloads': {name: {} for name in self.scenario.WORKLOADS}}
        manifest = client.pool_manifest(cpu=self.scenario.CONFIG['cpu_limit'])
        self.assertEqual(manifest['apiVersion'], 'karpenter.sh/v9')
        self.assertEqual(manifest['spec']['limits']['cpu'], '12')
        self.assertEqual(manifest['spec']['template']['spec']['nodeClassRef']['name'], 'alternate-class')
        client.get = Mock(return_value={'items': []})
        client.delete_owned = Mock()
        with patch.object(runtime, 'bounded', side_effect=lambda check, *args: self.assertTrue(check())):
            client.cleanup_pool()
        client.delete_owned.assert_called_once_with('nodepool', 'alternate-pool', '/apis/karpenter.sh/v9/nodepools/alternate-pool')
        first = config.state_directory(self.settings, HERE)
        changed = copy.deepcopy(self.settings)
        changed['broker']['vhost'] = 'other-vhost'
        self.assertNotEqual(first, config.state_directory(changed, HERE))
        self.assertEqual(first.name, config.identity(self.settings))

    def test_injection_uses_configured_pool_and_consolidation_window(self):
        self.client.state['injection_complete'] = False
        self.client.get.side_effect = lambda kind, *args: {'items': []} if kind == 'pdb' else self.resource()
        self.client.snapshots.return_value = {
            name: {'uid': f'old-{name}'} for name in self.scenario.WORKLOADS}
        self.client.optional.side_effect = lambda kind, name: {'metadata': {'uid': f'new-{name}'}}
        with patch.object(self.scenario, 'Runtime', return_value=self.client), \
             patch.object(sys, 'argv', ['scenario.py', 'inject', '--apply']), \
             patch.object(self.scenario, 'witness') as witness, \
             patch.object(self.scenario, 'bounded') as bounded, contextlib.redirect_stdout(io.StringIO()):
            self.scenario.main()
        self.client.pool_manifest.assert_called_once_with(cpu='12')
        self.client.baseline.assert_called_once_with([('statefulset', 'inventory-db'), ('statefulset', 'message-bus')])
        self.assertEqual(bounded.call_args.args[1], 23)
        self.assertTrue(bounded.call_args.args[0]())
        self.assertEqual([call.args[1] for call in witness.call_args_list], ['seed', 'lost'])
        self.assertTrue(self.client.state['injection_complete'])
        for call in self.client.pin.call_args_list:
            selector = call.kwargs['affinity']['podAffinity']['requiredDuringSchedulingIgnoredDuringExecution'][0]['labelSelector']
            self.assertEqual(selector['matchLabels'], {'app': 'pressure'})

    def test_runtime_state_is_config_bound_and_mismatches_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory, \
             patch.object(runtime, 'SETTINGS', self.settings), \
             patch.object(runtime, 'SERVER', self.settings['target']['server']), \
             patch.object(runtime.Runtime, 'k', return_value=json.dumps({
                 'clusters': [{'cluster': {'server': self.settings['target']['server']}}]})):
            (Path(directory) / '.state').mkdir()
            client = runtime.Runtime(directory, self.scenario.POOL)
            try:
                client.state = {'config_id': config.identity(self.settings)}
                client.save()
                self.assertEqual(client.state_path, config.state_directory(self.settings, directory) / 'baseline.json')
                self.assertEqual(json.loads(client.state_path.read_text())['config_id'], config.identity(self.settings))
                client.state = {'config_id': 'wrong-configuration'}
                client.save()
            finally:
                client.lock.close()
            rejected = object.__new__(runtime.Runtime)
            try:
                with self.assertRaisesRegex(RuntimeError, 'Saved configuration does not match target'):
                    rejected.__init__(directory, self.scenario.POOL)
            finally:
                rejected.lock.close()


if __name__ == '__main__':
    unittest.main()