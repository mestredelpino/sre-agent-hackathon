import contextlib
import copy
import io
import unittest
from unittest.mock import Mock, patch

from config import DEFAULTS
import network_faults as faults


class NetworkLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(DEFAULTS)
        self.settings['target'] = {'context': 'other-context', 'namespace': 'other-space',
                                   'server': 'https://other.example', 'kubeconfig': '/tmp/other-config'}
        for number in ('07', '08', '09'):
            self.settings['scenarios'][number]['probe'].update(pod='client', container='client', url='http://shop/')
        self.settings['scenarios']['07'].update(deployment='shop', enforcement_confirmed=True)
        self.settings['scenarios']['08'].update(ingress='shop-ingress', host='lab.example')
        self.settings['scenarios']['09']['service'] = 'shop'
        metadata = {'uid': 'subject-uid', 'resourceVersion': '7'}
        self.resources = {
            ('deployment', 'shop'): {'metadata': copy.deepcopy(metadata), 'spec': {'selector': {'matchLabels': {'app': 'shop'}}}},
            ('service', 'shop'): {'metadata': copy.deepcopy(metadata), 'spec': {'selector': {'app': 'shop'}}},
            ('ingress', 'shop-ingress'): {'metadata': copy.deepcopy(metadata), 'spec': {'rules': [
                {'host': 'lab.example', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix',
                    'backend': {'service': {'name': 'shop', 'port': {'number': 80}}}}]}}]}},
            ('pod', 'client'): {'metadata': {'name': 'client', 'labels': {'app': 'client'}},
                                'spec': {'containers': [{'name': 'client'}]}},
            ('replicaset', 'shop-rs'): {'metadata': {'uid': 'replica-uid', 'ownerReferences': [
                {'kind': 'Deployment', 'uid': 'subject-uid', 'controller': True}]}},
        }
        self.pods = [{'metadata': {'name': 'shop-pod', 'labels': {'app': 'shop'}, 'ownerReferences': [
            {'kind': 'ReplicaSet', 'name': 'shop-rs', 'uid': 'replica-uid', 'controller': True}]}, 'spec': {}}]
        self.policies = []
        self.client = Mock(state=None)
        self.client.get.side_effect = self.get
        self.client.optional.side_effect = lambda kind, name: copy.deepcopy(self.resources.get((kind, name)))
        self.client.k.side_effect = self.command

    def get(self, kind, name=None, *options):
        if kind == 'pods':
            selector = options[options.index('-l') + 1]
            labels = dict(item.split('=', 1) for item in selector.split(','))
            return {'items': [copy.deepcopy(pod) for pod in self.pods if faults.selected({'matchLabels': labels}, pod['metadata']['labels'])]}
        if kind == 'networkpolicies':
            return {'items': copy.deepcopy(self.policies)}
        if kind == 'endpointslices':
            selector = self.resources[('service', 'shop')]['spec']['selector']
            endpoints = [{'addresses': ['10.0.0.1'], 'conditions': {'ready': True}}] if selector == {'app': 'shop'} else []
            return {'items': [{'endpoints': endpoints}]}
        return copy.deepcopy(self.resources[(kind, name)])

    def command(self, *arguments, payload=None, raw=None):
        if arguments[0] == 'create':
            resource = copy.deepcopy(payload)
            resource['metadata'].update(uid='policy-uid', resourceVersion='9')
            resource['spec'].pop('ingress')
            self.resources[('networkpolicy', resource['metadata']['name'])] = resource
        elif arguments[0] == 'patch':
            resource = self.resources[(arguments[1], arguments[2])]
            self.assertEqual(payload[0]['value'], resource['metadata']['uid'])
            self.assertEqual(payload[1]['value'], resource['metadata']['resourceVersion'])
            pointer = payload[2]['path'].split('/')[1:]
            parent = resource
            for component in pointer[:-1]:
                parent = parent[int(component)] if isinstance(parent, list) else parent[component]
            parent[pointer[-1]] = copy.deepcopy(payload[2]['value'])
        elif arguments[0] == 'delete':
            self.assertEqual(payload['preconditions'], {'uid': 'policy-uid', 'resourceVersion': '9'})
            del self.resources[('networkpolicy', self.settings['scenarios']['07']['policy_name'])]
        return ''

    def test_inject_verify_reset_are_idempotent_for_all_three(self):
        for number in ('07', '08', '09'):
            with self.subTest(number=number), patch.object(faults, 'check_probe') as probe, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.client.state = None
                original = copy.deepcopy(self.resources)
                runner = faults.NetworkScenario(self.client, self.settings, number)
                runner.run('inject', plan=True)
                self.assertEqual(self.resources, original)
                runner.run('inject', apply=True)
                calls = self.client.k.call_count
                runner.run('inject', apply=True)
                self.assertEqual(self.client.k.call_count, calls)
                runner.run('verify', expect='broken')
                self.assertTrue(probe.call_args.args[2])
                runner.run('reset', apply=True)
                runner.run('reset', apply=True)
                runner.run('verify')
                self.assertFalse(probe.call_args.args[2])
                self.assertEqual(self.resources, original)

    def test_foreign_policy_collision_prevents_mutation(self):
        name = self.settings['scenarios']['07']['policy_name']
        self.resources[('networkpolicy', name)] = {'metadata': {'uid': 'foreign'}, 'spec': {}}
        with self.assertRaisesRegex(RuntimeError, 'not owned'):
            faults.NetworkScenario(self.client, self.settings, '07').run('inject', apply=True)
        self.client.k.assert_not_called()

    def test_additive_allow_policy_refused_without_deleting_it(self):
        self.policies = [{'spec': {'podSelector': {}, 'policyTypes': ['Ingress'], 'ingress': [{}]}}]
        with self.assertRaisesRegex(RuntimeError, 'additive allow'):
            faults.NetworkScenario(self.client, self.settings, '07').run('inject', apply=True)
        self.client.k.assert_not_called()

    def test_reset_rejects_drift_and_recreated_subject(self):
        runner = faults.NetworkScenario(self.client, self.settings, '09')
        with patch.object(faults, 'check_probe'), contextlib.redirect_stdout(io.StringIO()):
            runner.run('inject', apply=True)
        self.resources[('service', 'shop')]['spec']['selector'] = {'app': 'someone-else'}
        self.client.k.reset_mock()
        with self.assertRaisesRegex(RuntimeError, 'drifted'):
            runner.run('reset', apply=True)
        self.resources[('service', 'shop')]['metadata']['uid'] = 'new-uid'
        with self.assertRaisesRegex(RuntimeError, 'recreated'):
            runner.run('reset', apply=True)
        self.client.k.assert_not_called()

    def test_missing_baseline_and_unapproved_reset_refused(self):
        runner = faults.NetworkScenario(self.client, self.settings, '09')
        with self.assertRaisesRegex(RuntimeError, '--apply'):
            runner.run('reset')
        with self.assertRaisesRegex(RuntimeError, 'No saved baseline'):
            runner.run('reset', apply=True)
        self.client.k.assert_not_called()

    def test_ingress_refuses_a_real_wrong_service(self):
        self.resources[('service', 'inject08-missing-service')] = {'metadata': {'uid': 'real'}}
        with self.assertRaisesRegex(RuntimeError, 'must not exist'):
            faults.NetworkScenario(self.client, self.settings, '08').run('inject', apply=True)
        self.client.k.assert_not_called()

    def test_probe_passes_script_stdin_and_configured_pod_container(self):
        self.client.k.side_effect = None
        self.client.k.return_value = '{"status":200}'
        result = faults.probe_request(self.client, self.settings['scenarios']['09'])
        self.assertEqual(result['status'], 200)
        self.assertEqual(self.client.k.call_args.args[:7], ('exec', '-i', 'client', '-c', 'client', '--', 'node'))
        self.assertIn('require.main', self.client.k.call_args.kwargs['raw'])

    def test_networkpolicy_does_not_accept_connection_refused_as_drop(self):
        with patch.object(faults, 'probe_request', return_value={'status': 0, 'error': 'ECONNREFUSED'}):
            with self.assertRaisesRegex(RuntimeError, 'Unexpected transport error'):
                faults.check_probe(self.client, self.settings['scenarios']['07'], True)

    def test_unhealthy_baseline_never_mutates_or_saves(self):
        runner = faults.NetworkScenario(self.client, self.settings, '09')
        with patch.object(faults, 'check_probe', side_effect=RuntimeError('baseline unhealthy')):
            with self.assertRaisesRegex(RuntimeError, 'baseline unhealthy'):
                runner.run('inject', apply=True)
        self.client.k.assert_not_called()
        self.client.save.assert_not_called()
        self.assertIsNone(self.client.state)

    def test_failed_write_preserves_original_selector_and_intent(self):
        runner = faults.NetworkScenario(self.client, self.settings, '09')
        self.client.k.side_effect = RuntimeError('write interrupted')
        saved = []
        self.client.save.side_effect = lambda: saved.append(copy.deepcopy(self.client.state))
        with patch.object(faults, 'check_probe'):
            with self.assertRaisesRegex(RuntimeError, 'write interrupted'):
                runner.run('inject', apply=True)
        self.assertEqual(saved[0]['before'], {'app': 'shop'})
        self.assertIn('injects.sre/missing', saved[0]['after'])
        self.assertEqual(self.resources[('service', 'shop')]['spec']['selector'], {'app': 'shop'})

    def test_plan_cannot_be_combined_with_mutating_reset(self):
        runner = faults.NetworkScenario(self.client, self.settings, '09')
        with self.assertRaisesRegex(RuntimeError, 'only with inject'):
            runner.run('reset', apply=True, plan=True)
        self.client.k.assert_not_called()

    def test_policy_rejects_selector_overlap_with_other_workload(self):
        self.resources[('replicaset', 'shop-rs')]['metadata']['ownerReferences'][0]['uid'] = 'another-deployment'
        with self.assertRaisesRegex(RuntimeError, 'another workload'):
            faults.NetworkScenario(self.client, self.settings, '07').run('inject', apply=True)
        self.client.k.assert_not_called()


if __name__ == '__main__':
    unittest.main()