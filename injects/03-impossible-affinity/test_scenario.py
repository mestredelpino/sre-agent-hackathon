import importlib.util
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('scenario', Path(__file__).with_name('scenario.py'))
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)


class AffinityTests(unittest.TestCase):
    def setUp(self):
        self.node = {'metadata': {'name': 'node', 'labels': {
            'topology.kubernetes.io/zone': '0', 'kubernetes.io/os': 'linux', 'cpu': '4'}}}

    def test_injected_affinity_rejects_actual_zone(self):
        self.assertFalse(scenario.satisfies({'affinity': scenario.AFFINITY}, self.node))

    def test_baseline_accepts_actual_node(self):
        self.assertTrue(scenario.satisfies({'nodeSelector': {'kubernetes.io/os': 'linux'}}, self.node))

    def test_selector_mismatch_rejected(self):
        self.assertFalse(scenario.satisfies({'nodeSelector': {'kubernetes.io/os': 'windows'}}, self.node))

    def test_empty_terms_rejected(self):
        self.assertFalse(scenario.satisfies({'affinity': {'nodeAffinity': {
            'requiredDuringSchedulingIgnoredDuringExecution': {'nodeSelectorTerms': [{}]}}}}, self.node))

    def test_numeric_and_set_operators(self):
        self.assertTrue(scenario.matches({'key': 'cpu', 'operator': 'Gt', 'values': ['2']}, self.node['metadata']['labels']))
        self.assertFalse(scenario.matches({'key': 'cpu', 'operator': 'Lt', 'values': ['2']}, self.node['metadata']['labels']))
        self.assertTrue(scenario.matches({'key': 'missing', 'operator': 'NotIn', 'values': ['x']}, {}))


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        settings = {
            'target': {'context': 'other-context', 'namespace': 'other-namespace',
                       'server': 'https://other.example:443', 'kubeconfig': '/other/kubeconfig'},
            'workloads': {'product': {'name': 'catalog', 'container': 'catalog-api',
                                     'selector': 'component=catalog', 'image': ''}},
            'scenarios': {'03': {'zone': 'other-region-99', 'tolerations': [
                {'key': 'other-pool', 'operator': 'Exists', 'effect': 'NoSchedule'}]}},
            'timing': {'request': '7s', 'rollout': 42},
        }
        filename = self.directory / 'config.json'
        filename.write_text(json.dumps(settings))
        module_spec = importlib.util.spec_from_file_location('alternate_scenario', scenario.__file__)
        self.module = importlib.util.module_from_spec(module_spec)
        with mock.patch.dict(os.environ, {'INJECT_CONFIG': str(filename)}):
            module_spec.loader.exec_module(self.module)
        self.assertEqual(self.module.STATE, self.module.state_directory(
            self.module.SETTINGS, self.module.HERE) / 'baseline.json')
        self.module.STATE = self.module.state_directory(self.module.SETTINGS, self.directory) / 'baseline.json'
        self.deployment = {
            'metadata': {'uid': 'catalog-uid', 'resourceVersion': '3'},
            'spec': {'replicas': 1, 'template': {'spec': {'containers': [
                {'name': 'catalog-api', 'image': 'registry.example/catalog:custom'}]}}},
            'status': {'updatedReplicas': 1, 'readyReplicas': 1, 'availableReplicas': 1},
        }
        self.process = mock.patch.object(subprocess, 'run', side_effect=AssertionError('No live calls')).start()
        self.addCleanup(mock.patch.stopall)

    @contextmanager
    def execution(self, *arguments):
        output = io.StringIO()
        with mock.patch.object(sys, 'argv', ['scenario.py', *arguments]), \
                mock.patch.object(self.module, 'kubectl', return_value=json.dumps({
                    'clusters': [{'cluster': {'server': self.module.SERVER}}]})) as kubectl, \
                mock.patch.object(self.module, 'get', return_value=self.deployment), \
                mock.patch.object(self.module, 'verify') as verify, \
                mock.patch.object(self.module, 'patch') as patch, redirect_stdout(output):
            yield kubectl, verify, patch, output

    def save_baseline(self, **overrides):
        baseline = {'config_id': self.module.identity(self.module.SETTINGS),
                    'uid': 'catalog-uid', 'affinity': {}, 'tolerations': []}
        baseline.update(overrides)
        self.module.STATE.parent.mkdir(parents=True, exist_ok=True)
        self.module.STATE.write_text(json.dumps(baseline))

    def test_alternative_zone_comes_from_configuration(self):
        node = {'metadata': {'name': 'other-node', 'labels': {
            'topology.kubernetes.io/zone': 'other-region-99'}}}
        self.assertTrue(self.module.satisfies({'affinity': self.module.AFFINITY}, node))
        node['metadata']['labels']['topology.kubernetes.io/zone'] = 'other-region-1'
        self.assertFalse(self.module.satisfies({'affinity': self.module.AFFINITY}, node))

    def test_kubectl_uses_configured_target_and_request_timeout(self):
        self.process.side_effect = None
        self.process.return_value.stdout = '{}'
        with mock.patch.dict(os.environ, {'KUBECONFIG': '/ignored/kubeconfig'}):
            self.module.kubectl('get', 'pods')
        self.assertEqual(self.process.call_args.args[0], [
            'kubectl', '--kubeconfig', '/other/kubeconfig', '--context', 'other-context',
            '--namespace', 'other-namespace', '--request-timeout=7s', 'get', 'pods'])

    def test_incomplete_or_insecure_target_fails_before_subprocess(self):
        for field in ('context', 'namespace', 'server', 'kubeconfig'):
            with self.subTest(field=field), mock.patch.dict(self.module.SETTINGS['target'], {field: ''}):
                with self.assertRaises(RuntimeError):
                    self.module.kubectl('get', 'pods')
        with mock.patch.dict(self.module.SETTINGS['target'], {'server': 'http://other.example'}):
            with self.assertRaisesRegex(RuntimeError, 'HTTPS'):
                self.module.kubectl('get', 'pods')
        self.process.assert_not_called()

    def test_main_validates_target_before_kubectl(self):
        with mock.patch.dict(self.module.SETTINGS['target'], {'context': ''}), \
                self.execution('inject', '--plan') as (kubectl, verify, patch, output):
            with self.assertRaisesRegex(RuntimeError, 'target.context'):
                self.module.main()
            kubectl.assert_not_called()

    def test_plan_reflects_configuration_without_injection(self):
        with self.execution('inject', '--plan') as (kubectl, verify, patch, output):
            self.module.main()
            for value in ('other-context/other-namespace', 'https://other.example:443',
                          '/other/kubeconfig', 'other-region-99', 'deployment/catalog',
                          'catalog-api', 'component=catalog', 'other-pool', 'image guard disabled'):
                self.assertIn(value, output.getvalue())
            patch.assert_not_called()
            verify.assert_not_called()
            self.assertFalse(self.module.STATE.exists())

    def test_wrong_server_rejected_before_patch(self):
        with self.execution('inject', '--apply') as (kubectl, verify, patch, output):
            kubectl.return_value = json.dumps({'clusters': [{'cluster': {'server': 'https://wrong'}}]})
            with self.assertRaisesRegex(RuntimeError, 'Wrong cluster API'):
                self.module.main()
            patch.assert_not_called()

    def test_optional_image_guard(self):
        with self.execution('inject', '--plan'):
            self.module.main()
        with mock.patch.dict(self.module.WORKLOAD, {'image': 'registry.example/catalog:custom'}), \
                self.execution('inject', '--plan') as (kubectl, verify, patch, output):
            self.module.main()
            self.assertIn('image guard registry.example/catalog:custom', output.getvalue())
        with mock.patch.dict(self.module.WORKLOAD, {'image': 'unexpected:image'}), \
                self.execution('inject', '--apply') as (kubectl, verify, patch, output):
            with self.assertRaisesRegex(RuntimeError, 'Image contract changed'):
                self.module.main()
            patch.assert_not_called()

    def test_requires_single_configured_container(self):
        for containers in ([], [{'name': 'wrong', 'image': 'any'}],
                           [{'name': 'catalog-api', 'image': 'any'}, {'name': 'sidecar', 'image': 'any'}]):
            with self.subTest(containers=containers), self.execution('inject', '--apply') as execution:
                self.deployment['spec']['template']['spec']['containers'] = containers
                with self.assertRaisesRegex(RuntimeError, 'single configured container'):
                    self.module.main()
                execution[2].assert_not_called()

    def test_inject_reset_repeat_with_absent_or_empty_affinity(self):
        for affinity in (None, {}):
            with self.subTest(affinity=affinity):
                self.module.STATE.unlink(missing_ok=True)
                pod_spec = self.deployment['spec']['template']['spec']
                pod_spec.pop('affinity', None)
                pod_spec['tolerations'] = [{'key': 'baseline', 'operator': 'Exists'}]
                if affinity is not None:
                    pod_spec['affinity'] = affinity
                for action in ('inject', 'reset', 'inject', 'reset'):
                    with self.execution(action, '--apply') as (kubectl, verify, patch, output):
                        self.module.main()
                        _, updated_affinity, tolerations = patch.call_args.args
                        expected = self.module.AFFINITY if action == 'inject' else {}
                        self.assertEqual(updated_affinity, expected)
                        self.assertEqual(tolerations, [{'key': 'baseline', 'operator': 'Exists'}] + (
                            self.module.SCENARIO['tolerations'] if action == 'inject' else []))
                        pod_spec['affinity'] = deepcopy(updated_affinity)
                        pod_spec['tolerations'] = deepcopy(tolerations)
                saved = json.loads(self.module.STATE.read_text())
                self.assertEqual(saved['config_id'], self.module.identity(self.module.SETTINGS))

    def test_saved_config_and_uid_guards(self):
        for overrides, message in (({'config_id': 'other-config'}, 'configuration'),
                                   ({'uid': 'other-uid'}, 'recreated')):
            self.save_baseline(**overrides)
            for action in ('inject', 'reset'):
                with self.subTest(overrides=overrides, action=action), \
                        self.execution(action, '--apply') as execution:
                    with self.assertRaisesRegex(RuntimeError, message):
                        self.module.main()
                    execution[2].assert_not_called()
        self.save_baseline()
        baseline = json.loads(self.module.STATE.read_text())
        baseline.pop('config_id')
        self.module.STATE.write_text(json.dumps(baseline))
        with self.execution('reset') as execution:
            with self.assertRaisesRegex(RuntimeError, 'configuration'):
                self.module.main()
            execution[2].assert_not_called()

    def test_existing_affinity_and_unexpected_edits_rejected(self):
        pod_spec = self.deployment['spec']['template']['spec']
        pod_spec['affinity'] = {'nodeAffinity': {'preferredDuringSchedulingIgnoredDuringExecution': []}}
        with self.execution('inject', '--apply') as execution:
            with self.assertRaisesRegex(RuntimeError, 'Existing affinity'):
                self.module.main()
            execution[2].assert_not_called()
        self.save_baseline()
        with self.execution('reset') as execution:
            with self.assertRaisesRegex(RuntimeError, 'Unexpected affinity'):
                self.module.main()
            execution[2].assert_not_called()
        pod_spec['affinity'] = {}
        pod_spec['tolerations'] = [{'key': 'unexpected'}]
        with self.execution('reset') as execution:
            with self.assertRaisesRegex(RuntimeError, 'Unexpected toleration'):
                self.module.main()
            execution[2].assert_not_called()

    def test_verify_uses_configured_workload_selector_and_rollout(self):
        node = {'metadata': {'name': 'node', 'labels': {}}, 'status': {'conditions': [
            {'type': 'Ready', 'status': 'True'}]}}
        pod = {'metadata': {}, 'spec': {'nodeName': 'node'}, 'status': {
            'phase': 'Running', 'conditions': [{'type': 'Ready', 'status': 'True'}]}}
        with mock.patch.object(self.module, 'kubectl') as kubectl, \
                mock.patch.object(self.module, 'get', side_effect=[
                    self.deployment, {'items': [pod]}, node]) as get, redirect_stdout(io.StringIO()):
            self.module.verify()
            kubectl.assert_called_once_with('rollout', 'status', 'deployment/catalog', '--timeout=42s')
            self.assertEqual(get.call_args_list, [mock.call('deployment', 'catalog'),
                             mock.call('pods', '-l', 'component=catalog'), mock.call('node', 'node')])


if __name__ == '__main__':
    unittest.main()