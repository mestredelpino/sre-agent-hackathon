import unittest
import copy
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from runtime import Runtime, require, SETTINGS
import runtime


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = Runtime.__new__(Runtime)
        self.runtime.pool = 'owned-pool'
        self.runtime.settings = copy.deepcopy(SETTINGS)
        self.runtime.settings['nodepool']['nodeclass_ref']['name'] = 'test-class'
        self.runtime.state = {'token': 'private-token', 'workloads': {}}

    def test_explicit_no_budgets_and_never_expire(self):
        manifest = self.runtime.pool_manifest()
        self.assertEqual(manifest['spec']['disruption']['budgets'], [])
        self.assertEqual(manifest['spec']['template']['spec']['expireAfter'], 'Never')
        self.assertEqual(manifest['spec']['disruption']['consolidationPolicy'], 'WhenEmptyOrUnderutilized')

    def test_pool_is_tainted_and_labelled_exclusively(self):
        spec = self.runtime.pool_manifest()['spec']['template']
        self.assertEqual(spec['metadata']['labels']['injects.sre/pool'], 'owned-pool')
        self.assertEqual(spec['spec']['taints'][0]['value'], 'owned-pool')

    def test_rejects_resource_with_different_owner(self):
        self.runtime.optional = lambda *args: {'metadata': {'labels': {'injects.sre/owner': 'someone-else'}}}
        with self.assertRaises(RuntimeError):
            self.runtime.owned('nodepool', 'owned-pool')

    def test_missing_resource_is_not_an_ownership_error(self):
        self.runtime.optional = lambda *args: None
        self.assertIsNone(self.runtime.owned('nodepool', 'owned-pool'))

    def test_precondition_guard_rejects_false(self):
        with self.assertRaises(RuntimeError):
            require(False, 'unsafe')

    def test_cleanup_refuses_unrelated_namespace_pod(self):
        calls = []

        def get(kind, name=None, *options):
            if kind == 'nodes':
                return {'items': [{'metadata': {'name': 'scenario-node'}}]}
            if kind == 'pods':
                return {'items': [{'metadata': {'namespace': 'other', 'name': 'unrelated'},
                                   'spec': {'nodeName': 'scenario-node'}}]}
            raise AssertionError(kind)

        self.runtime.get = get
        self.runtime.delete_owned = lambda *args: calls.append(args)
        with self.assertRaisesRegex(RuntimeError, 'other/unrelated'):
            self.runtime.cleanup_pool()
        self.assertEqual(calls, [])

    def test_delete_uses_resource_uid_precondition(self):
        self.runtime.owned = lambda *args: {'metadata': {'uid': 'exact-uid'}}
        calls = []
        self.runtime.k = lambda *args, **kwargs: calls.append((args, kwargs))
        self.runtime.delete_owned('nodepool', 'owned-pool', '/apis/karpenter.sh/v1/nodepools/owned-pool')
        self.assertEqual(calls[0][1]['payload']['preconditions'], {'uid': 'exact-uid'})
        self.assertEqual(calls[1][0][0:2], ('wait', '--for=delete'))

    def test_alternate_target_is_used_in_every_command(self):
        settings = copy.deepcopy(SETTINGS)
        settings['target'] = {'context': 'tenant-b-context', 'namespace': 'tenant-b-store',
                              'server': 'https://tenant-b.example:443', 'kubeconfig': '/tmp/tenant b/config'}
        response = SimpleNamespace(stdout=json.dumps({'clusters': [{'cluster': {
            'server': settings['target']['server']}}]}))
        with tempfile.TemporaryDirectory() as directory, patch.object(runtime, 'SETTINGS', settings), \
             patch.object(runtime, 'CONTEXT', settings['target']['context']), \
             patch.object(runtime, 'NAMESPACE', settings['target']['namespace']), \
             patch.object(runtime, 'SERVER', settings['target']['server']), \
             patch.object(runtime.subprocess, 'run', return_value=response) as command:
            instance = Runtime(directory, 'owned-b-pool')
            instance.k('get', 'pods')
            for call in command.call_args_list:
                arguments = call.args[0]
                self.assertEqual(arguments[arguments.index('--context') + 1], 'tenant-b-context')
                self.assertEqual(arguments[arguments.index('--namespace') + 1], 'tenant-b-store')
                self.assertEqual(arguments[arguments.index('--kubeconfig') + 1], '/tmp/tenant b/config')
            self.assertTrue(instance.state_path.parent.is_dir())
            self.assertNotEqual(instance.state_path, Path(directory) / '.state' / 'baseline.json')
            instance.lock.close()

    def test_api_mismatch_stops_before_workload_access(self):
        settings = copy.deepcopy(SETTINGS)
        settings['target'] = {'context': 'b', 'namespace': 'b-store',
                              'server': 'https://expected.example', 'kubeconfig': '/tmp/b'}
        response = SimpleNamespace(stdout=json.dumps({'clusters': [{'cluster': {'server': 'https://wrong.example'}}]}))
        with tempfile.TemporaryDirectory() as directory, patch.object(runtime, 'SETTINGS', settings), \
             patch.object(runtime, 'SERVER', settings['target']['server']), \
             patch.object(runtime.subprocess, 'run', return_value=response) as command:
            with self.assertRaisesRegex(RuntimeError, 'Wrong cluster API'):
                Runtime(directory, 'owned')
            self.assertEqual(command.call_count, 1)


if __name__ == '__main__':
    unittest.main()