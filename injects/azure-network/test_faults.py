import copy
import unittest

from faults import affected, canonical, desired, fault_settings, resource_parts


class FaultTests(unittest.TestCase):
    def test_resource_scope_is_explicit(self):
        resource = '/subscriptions/sub/resourceGroups/lab/providers/Microsoft.Network/applicationGateways/gateway'
        self.assertEqual(resource_parts(resource, 'sub', 'applicationGateways'), ('lab', 'gateway'))
        with self.assertRaises(RuntimeError):
            resource_parts(resource, 'different', 'applicationGateways')
        with self.assertRaises(RuntimeError):
            resource_parts(resource + '/backendAddressPools/shared', 'sub', 'applicationGateways')

    def test_nsg_fault_is_narrow_and_refuses_collision(self):
        options = {'rule_name': 'lab-deny', 'priority': 120, 'source_prefix': '10.1.0.4/32',
                   'destination_prefix': '10.2.0.4/32', 'destination_port': 443}
        rule = desired({'securityRules': []}, 'nsg', options)
        self.assertEqual(rule['access'], 'Deny')
        self.assertEqual(rule['destinationPortRange'], '443')
        with self.assertRaises(RuntimeError):
            desired({'securityRules': [rule]}, 'nsg', options)
        other = dict(rule, name='someone-elses-rule')
        with self.assertRaises(RuntimeError):
            desired({'securityRules': [other]}, 'nsg', options)

    def test_waf_preserves_existing_rules_and_mode(self):
        original = {'policySettings': {'mode': 'Prevention', 'state': 'Enabled'}, 'customRules': []}
        options = {'rule_name': 'labBlock', 'priority': 20, 'header_name': 'X-SRE-Lab', 'header_value': 'test'}
        saved = copy.deepcopy(original)
        rules = desired(original, 'waf', options)
        self.assertEqual(original, saved)
        self.assertEqual(rules[0]['matchConditions'][0]['matchVariables'][0]['variableName'], 'RequestHeaders')
        with self.assertRaises(RuntimeError):
            desired(dict(original, customRules=rules), 'waf', options)
        with self.assertRaises(RuntimeError):
            desired(dict(original, policySettings={'mode': 'Detection', 'state': 'Enabled'}), 'waf', options)

    def test_backend_only_changes_selected_pool(self):
        resource = {'backendAddressPools': [{'name': 'store', 'backendAddresses': [{'fqdn': 'store.example'}]},
                                            {'name': 'other', 'backendAddresses': [{'ipAddress': '10.0.0.5'}]}]}
        original = copy.deepcopy(resource)
        options = {'pool_name': 'store', 'wrong_address': '10.0.0.254'}
        self.assertEqual(desired(resource, 'backend', options), [{'ipAddress': '10.0.0.254'}])
        self.assertEqual(affected(resource, 'backend', options), [{'fqdn': 'store.example'}])
        self.assertEqual(resource, original)

    def test_wildcard_nsg_is_rejected(self):
        config = {'target': {'tenant_id': 'tenant', 'subscription_id': 'sub'}, 'dedicated_lab': True,
                  'nsg': {'resource_id': '/subscriptions/sub/resourceGroups/lab/providers/Microsoft.Network/networkSecurityGroups/nsg',
                          'priority': 120, 'source_prefix': '0.0.0.0/0',
                          'destination_prefix': '10.0.0.1/32', 'destination_port': 443}}
        with self.assertRaisesRegex(RuntimeError, 'whole-Internet'):
            fault_settings(config, 'nsg')

    def test_canonical_ignores_only_server_metadata(self):
        self.assertEqual(canonical({'id': 'server', 'etag': 'etag', 'resourceGroup': 'lab',
                                    'name': 'rule', 'priority': 120}),
                         {'name': 'rule', 'priority': 120})


if __name__ == '__main__':
    unittest.main()