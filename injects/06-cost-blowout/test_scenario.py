from decimal import Decimal
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess

spec = importlib.util.spec_from_file_location('cost_scenario', Path(__file__).with_name('scenario.py'))
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)


class CostTests(unittest.TestCase):
    def test_quantity_units(self):
        self.assertEqual(scenario.quantity('10m'), Decimal('0.01'))
        self.assertEqual(scenario.quantity('64Mi'), Decimal(64 * 1024 ** 2))
        self.assertEqual(scenario.quantity('1e3'), Decimal(1000))

    def test_unknown_units_fail_closed(self):
        with self.assertRaises(RuntimeError):
            scenario.quantity('invalid')

    def check(self, resources, cpu='1m', memory='7Mi'):
        pods = [{'metadata': {'name': 'pod'}, 'spec': {'containers': [{'resources': resources}]}}]
        scenario.check_rightsizing(pods, {'pod': {'cpu': scenario.quantity(cpu), 'memory': scenario.quantity(memory)}})

    def test_rightsized_requests(self):
        self.check(scenario.SMALL)

    def test_inflated_requests_rejected(self):
        with self.assertRaises(RuntimeError):
            self.check(scenario.LARGE)

    def test_underprovisioned_usage_rejected(self):
        with self.assertRaises(RuntimeError):
            self.check(scenario.SMALL, cpu='50m')

    def test_transient_metrics_are_retried(self):
        samples = {'pod': {'cpu': Decimal('0.001'), 'memory': scenario.quantity('7Mi')}}
        with patch.object(scenario, 'usage', side_effect=[
            subprocess.CalledProcessError(1, 'kubectl', stderr='error: metrics not available yet'), samples
        ]), patch.object(scenario, 'bounded') as bounded:
            def retry(check, seconds, description):
                self.assertFalse(check())
                self.assertTrue(check())
            bounded.side_effect = retry
            self.assertEqual(scenario.measured_usage(object()), samples)

    def test_authorization_errors_not_retried(self):
        with patch.object(scenario, 'usage', side_effect=subprocess.CalledProcessError(
            1, 'kubectl', stderr='Forbidden'
        )):
            with self.assertRaises(subprocess.CalledProcessError):
                scenario.measured_usage(object())


if __name__ == '__main__':
    unittest.main()