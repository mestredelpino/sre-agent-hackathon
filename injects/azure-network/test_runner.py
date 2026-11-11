import copy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import socket
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import scenario


def configuration():
    prefix = '/subscriptions/sub/resourceGroups/lab/providers/Microsoft.Network/'
    probe = {'url': 'https://store.example/', 'timeout_seconds': 5,
             'healthy_statuses': [200], 'broken_statuses': [502]}
    return {'target': {'tenant_id': 'tenant', 'subscription_id': 'sub'},
            'dedicated_lab': True, 'exclusive_control': True,
            'nsg': {'resource_id': prefix + 'networkSecurityGroups/nsg', 'rule_name': 'lab-deny',
                    'priority': 120, 'source_prefix': '10.1.0.4/32', 'destination_prefix': '10.2.0.4/32',
                    'destination_port': 443, 'probe': dict(probe, broken_statuses=[0])},
            'waf': {'resource_id': prefix + 'ApplicationGatewayWebApplicationFirewallPolicies/policy',
                    'rule_name': 'labBlock', 'priority': 20, 'header_name': 'X-SRE-Lab',
                    'header_value': 'test', 'probe': dict(probe, broken_statuses=[403])},
            'backend': {'resource_id': prefix + 'applicationGateways/gateway', 'pool_name': 'store',
                        'wrong_address': '10.2.0.254', 'probe': probe}}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.config = configuration()
        self.resources = {}
        for name in ('nsg', 'waf', 'backend'):
            self.resources[name] = {'id': self.config[name]['resource_id'], 'etag': 'etag',
                                    'provisioningState': 'Succeeded'}
        self.resources['nsg']['securityRules'] = []
        self.resources['waf'].update(customRules=[], policySettings={'mode': 'Prevention', 'state': 'Enabled'})
        self.resources['backend']['backendAddressPools'] = [
            {'name': 'store', 'backendAddresses': [{'fqdn': 'original.example'}]},
            {'name': 'unrelated', 'backendAddresses': [{'ipAddress': '10.2.0.7'}]}]
        self.azure = Mock(subscription='sub')
        self.azure.show.side_effect = lambda name, options: copy.deepcopy(self.resources[name])
        self.azure.write.side_effect = self.write

    def write(self, name, options, value):
        resource = self.resources[name]
        if name == 'nsg':
            resource['securityRules'] = [value] if value else []
        elif name == 'waf':
            resource['customRules'] = value
        else:
            resource['backendAddressPools'][0]['backendAddresses'] = value

    def test_all_lifecycles_are_idempotent_and_preserve_unrelated_state(self):
        for name in ('nsg', 'waf', 'backend'):
            original = copy.deepcopy(self.resources[name])
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory, \
                 patch.object(scenario, 'Azure', return_value=self.azure), \
                 patch.object(scenario, 'check_http'), contextlib.redirect_stdout(io.StringIO()):
                scenario.run(self.config, name, 'plan', False, directory)
                self.assertEqual(self.resources[name], original)
                scenario.run(self.config, name, 'inject', True, directory)
                writes = self.azure.write.call_count
                scenario.run(self.config, name, 'inject', True, directory)
                self.assertEqual(self.azure.write.call_count, writes)
                scenario.run(self.config, name, 'verify', False, directory, 'broken')
                scenario.run(self.config, name, 'reset', True, directory)
                scenario.run(self.config, name, 'reset', True, directory)
                scenario.run(self.config, name, 'verify', False, directory, 'healthy')
                self.assertEqual(self.resources[name], original)
                with self.assertRaisesRegex(RuntimeError, 'Archive completed state'):
                    scenario.run(self.config, name, 'inject', True, directory)

    def test_plan_and_unapproved_injection_never_write(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(scenario, 'Azure', return_value=self.azure), contextlib.redirect_stdout(io.StringIO()):
            scenario.run(self.config, 'backend', 'plan', False, directory)
            with self.assertRaisesRegex(RuntimeError, '--apply'):
                scenario.run(self.config, 'backend', 'inject', False, directory)
        self.azure.write.assert_not_called()

    def test_reset_refuses_drift_and_missing_baseline(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(scenario, 'Azure', return_value=self.azure), \
             patch.object(scenario, 'check_http'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'No saved baseline'):
                scenario.run(self.config, 'backend', 'reset', True, directory)
            scenario.run(self.config, 'backend', 'inject', True, directory)
            self.resources['backend']['backendAddressPools'][0]['backendAddresses'] = [{'ipAddress': '10.4.0.1'}]
            self.azure.write.reset_mock()
            with self.assertRaisesRegex(RuntimeError, 'drifted'):
                scenario.run(self.config, 'backend', 'reset', True, directory)
            self.azure.write.assert_not_called()

    def test_baseline_is_saved_even_when_write_fails(self):
        self.azure.write.side_effect = RuntimeError('transient failure')
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(scenario, 'Azure', return_value=self.azure), \
             patch.object(scenario, 'check_http'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'transient failure'):
                scenario.run(self.config, 'backend', 'inject', True, directory)
            saved = json.loads(next(Path(directory).glob('*/*.json')).read_text())
            self.assertEqual(saved['before'], [{'fqdn': 'original.example'}])

    def test_resource_etag_change_prevents_write(self):
        self.azure.show.side_effect = [copy.deepcopy(self.resources['backend']),
                                      dict(self.resources['backend'], etag='changed')]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(scenario, 'Azure', return_value=self.azure), \
             patch.object(scenario, 'check_http'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'changed during checks'):
                scenario.run(self.config, 'backend', 'inject', True, directory)
            self.azure.write.assert_not_called()

    def test_wrong_tenant_aborts_after_account_read(self):
        result = SimpleNamespace(stdout=json.dumps({'id': 'sub', 'tenantId': 'other'}))
        with patch.object(scenario.subprocess, 'run', return_value=result) as command:
            with self.assertRaisesRegex(RuntimeError, 'tenant mismatch'):
                scenario.Azure(self.config)
            self.assertEqual(command.call_count, 1)
            self.assertIn('--subscription', command.call_args.args[0])

    def test_cli_writes_use_explicit_scope_and_single_waf_update(self):
        client = object.__new__(scenario.Azure)
        client.subscription = 'sub'
        client.run = Mock()
        for name in ('nsg', 'waf', 'backend'):
            value = scenario.desired(self.resources[name], name, self.config[name])
            client.write(name, self.config[name], value)
        arguments = client.run.call_args_list[1].args
        self.assertIn('--custom-rules', arguments)
        self.assertEqual(arguments[arguments.index('--ids') + 1], self.config['waf']['resource_id'])
        arguments = client.run.call_args_list[2].args
        self.assertEqual(arguments[arguments.index('--gateway-name') + 1], 'gateway')
        self.assertEqual(arguments[arguments.index('--servers') + 1], '10.2.0.254')

    def test_waf_verifies_unmarked_and_marked_requests(self):
        with patch.object(scenario, 'http_status', side_effect=[200, 403]) as probe, \
             contextlib.redirect_stdout(io.StringIO()):
            scenario.check_http(self.config, 'waf', True)
            self.assertEqual(probe.call_args.args[1], {'X-SRE-Lab': 'test'})
        with patch.object(scenario, 'http_status', side_effect=[200, 200]):
            with self.assertRaisesRegex(RuntimeError, 'Unexpected HTTP outcome'):
                scenario.check_http(self.config, 'waf', True)

    def test_no_exclusive_control_refuses_before_azure(self):
        self.config['exclusive_control'] = False
        with patch.object(scenario, 'Azure') as client, tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, 'Pause Terraform/AGIC'):
                scenario.run(self.config, 'backend', 'plan', False, directory)
            client.assert_not_called()

    def test_only_connection_timeout_counts_as_timeout_symptom(self):
        probe = self.config['nsg']['probe']
        opener = Mock()
        with patch.object(scenario.urllib.request, 'build_opener', return_value=opener):
            opener.open.side_effect = scenario.urllib.error.URLError(socket.timeout())
            self.assertEqual(scenario.http_status(probe), 0)
            opener.open.side_effect = scenario.urllib.error.URLError('certificate verification failed')
            with self.assertRaisesRegex(RuntimeError, 'not proof of the fault'):
                scenario.http_status(probe)

    def test_credentials_in_probe_urls_are_rejected(self):
        probe = dict(self.config['backend']['probe'], url='https://user:password@store.example/')
        with patch.object(scenario.urllib.request, 'build_opener') as opener:
            with self.assertRaisesRegex(RuntimeError, 'without credentials'):
                scenario.http_status(probe)
            opener.assert_not_called()


if __name__ == '__main__':
    unittest.main()