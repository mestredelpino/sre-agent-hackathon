import copy
import unittest

from network_faults import ingress_backend, label_selector, policy_manifest, ready_endpoints, selected, service_selector


class NetworkFaultTests(unittest.TestCase):
    def test_policy_targets_only_deployment_and_only_ingress(self):
        deployment = {'spec': {'selector': {'matchLabels': {'component': 'catalog'}}}}
        original = copy.deepcopy(deployment)
        policy = policy_manifest(deployment, 'deny', 'alternate-space', 'owner')
        self.assertEqual(policy['metadata']['namespace'], 'alternate-space')
        self.assertEqual(policy['spec'], {'podSelector': deployment['spec']['selector'],
                                        'policyTypes': ['Ingress'], 'ingress': []})
        self.assertEqual(deployment, original)
        with self.assertRaises(RuntimeError):
            policy_manifest({'spec': {'selector': {}}}, 'deny', 'space', 'owner')

    def test_ingress_selects_exact_route_without_editing_neighbors(self):
        path = {'path': '/shop', 'pathType': 'Prefix', 'backend': {'service': {'name': 'shop', 'port': {'number': 80}}}}
        ingress = {'spec': {'rules': [{'host': 'other.example', 'http': {'paths': [copy.deepcopy(path)]}},
                                     {'host': 'lab.example', 'http': {'paths': [copy.deepcopy(path)]}}]}}
        original = copy.deepcopy(ingress)
        options = {'host': 'lab.example', 'path': '/shop', 'path_type': 'Prefix'}
        pointer, before = ingress_backend(ingress, options)
        self.assertEqual(pointer, '/spec/rules/1/http/paths/0/backend')
        self.assertEqual(before, path['backend'])
        self.assertEqual(ingress, original)
        options['host'] = 'missing.example'
        with self.assertRaises(RuntimeError):
            ingress_backend(ingress, options)

    def test_service_rejects_selectorless_and_headless(self):
        self.assertEqual(service_selector({'spec': {'selector': {'app': 'shop'}}}), {'app': 'shop'})
        for spec in ({}, {'selector': {}}, {'clusterIP': 'None', 'selector': {'app': 'shop'}},
                     {'type': 'ExternalName', 'selector': {'app': 'shop'}}):
            with self.assertRaises(RuntimeError):
                service_selector({'spec': spec})

    def test_policy_matching_accounts_for_additive_allow_rules(self):
        self.assertTrue(selected({}, {'app': 'shop'}))
        self.assertFalse(selected({'matchLabels': {'app': 'other'}}, {'app': 'shop'}))
        self.assertTrue(selected({'matchExpressions': [{'key': 'team', 'operator': 'NotIn',
                                                       'values': ['other']}]}, {'app': 'shop'}))

    def test_endpoint_readiness_does_not_count_unready_addresses(self):
        slices = {'items': [{'endpoints': [{'addresses': ['10.0.0.1'], 'conditions': {'ready': False}},
                                          {'addresses': ['10.0.0.2']}, {'addresses': []}]}]}
        self.assertEqual(len(ready_endpoints(slices)), 1)

    def test_empty_label_selector_refused(self):
        with self.assertRaises(RuntimeError):
            label_selector({})


if __name__ == '__main__':
    unittest.main()