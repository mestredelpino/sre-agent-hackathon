import copy
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import config
import runtime


class ConfigTests(unittest.TestCase):
    def test_target_has_no_original_cluster_default(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = config.load()
        with self.assertRaisesRegex(RuntimeError, 'target.context'):
            config.target(settings)

    def test_alternate_target_and_state_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'target.json'
            filename.write_text('{"target":{"context":"other-context","namespace":"other-store",'
                                '"server":"https://other.example:443","kubeconfig":"/tmp/other-config"}}')
            with patch.dict(os.environ, {'INJECT_CONFIG': str(filename)}):
                settings = config.load()
            self.assertEqual(config.target(settings)['namespace'], 'other-store')
            before = config.state_directory(settings, directory)
            settings['target']['server'] = 'https://third.example:443'
            self.assertNotEqual(before, config.state_directory(settings, directory))

    def test_unknown_key_fails(self):
        with self.assertRaises(RuntimeError):
            config.merge({}, {'typo': 1})

    def test_shell_quotes_values(self):
        settings = config.load()
        settings['target'] = {'context': 'other', 'namespace': 'store', 'server': 'https://other',
                              'kubeconfig': '/tmp/path with spaces'}
        self.assertIn("KUBECONFIG='/tmp/path with spaces'", config.shell(settings))

    def test_spot_and_cost_use_renamed_workloads_and_sizing(self):
        settings = copy.deepcopy(config.DEFAULTS)
        settings['workloads']['makeline']['name'] = 'alternate-kitchen'
        settings['workloads']['front']['name'] = 'alternate-shop'
        settings['scenarios']['05'].update(pool='alternate-spot', replicas=2)
        settings['scenarios']['06'].update(pool='alternate-cost', replicas=4, reduction_percent=25)
        for folder, number, name in [('05-spot-roulette', '05', 'alternate-kitchen'),
                                     ('06-cost-blowout', '06', 'alternate-shop')]:
            spec = importlib.util.spec_from_file_location('portable_' + number,
                Path(__file__).parent / folder / 'scenario.py')
            module = importlib.util.module_from_spec(spec)
            with patch.object(runtime, 'SETTINGS', settings), patch.object(runtime.subprocess, 'run') as command:
                spec.loader.exec_module(module)
            command.assert_not_called()
            self.assertEqual(module.WORKLOAD, name)
            self.assertEqual(module.POOL, settings['scenarios'][number]['pool'])
            self.assertEqual(module.TARGET, settings['scenarios'][number]['replicas'])
        self.assertEqual(str(module.REDUCTION), '0.25')

    def test_custom_labels_and_order_body_replace_defaults(self):
        settings = copy.deepcopy(config.DEFAULTS)
        config.merge(settings, {'nodepool': {'labels': {'team': 'alternate'}},
                                'broker': {'test_order': {'customItems': []}}})
        self.assertEqual(settings['nodepool']['labels'], {'team': 'alternate'})
        self.assertEqual(settings['broker']['test_order'], {'customItems': []})


if __name__ == '__main__':
    unittest.main()