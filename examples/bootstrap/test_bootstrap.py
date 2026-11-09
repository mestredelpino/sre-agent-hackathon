import unittest
import tempfile
import json
import hashlib
from pathlib import Path
from unittest.mock import patch

import bootstrap


class FakeClient:
    def __init__(self):
        self.values = {}
        self.writes = []
        self.fail_name = None

    def request(self, method, resource):
        name = resource['body']['name']
        if method == 'GET':
            return self.values.get(name)
        if name == self.fail_name:
            raise ValueError('injected API failure')
        self.writes.append(name)
        self.values[name] = resource['body']
        return resource['body']


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.target = '/subscriptions/test/resourceGroups/lab/providers/Microsoft.App/agents/demo'
        self.resources = [{'name': 'lab-triage'}]
        self.plan = {'target': self.target, 'desiredHash': bootstrap.digest(self.resources)}

    def test_exact_confirmation_required(self):
        with self.assertRaises(ValueError):
            bootstrap.require_review(self.plan, self.resources, self.target, 'yes')

    def test_changed_bundle_rejected(self):
        with self.assertRaises(ValueError):
            bootstrap.require_review(self.plan, [], self.target, self.target)

    def test_changed_target_rejected(self):
        with self.assertRaises(ValueError):
            bootstrap.require_review(self.plan, self.resources, 'other', 'other')

    def test_reviewed_bundle_accepted(self):
        bootstrap.require_review(self.plan, self.resources, self.target, self.target)

    def test_workspace_task_mode_omits_static_edges(self):
        resources = bootstrap.build({'scope': {'fixture': True}, 'delegationMode': 'task'})
        triage = next(item['body']['properties'] for item in resources if item['body']['name'] == 'lab-triage')
        self.assertEqual(triage['handoffs'], [])
        self.assertIn('native Task tool', triage['instructions'])

class DiagnosticBundleTests(unittest.TestCase):
    def test_skill_readback_name_uses_envelope(self):
        desired = bootstrap.skill_resource('example', 'Description', 'Content')['body']
        actual = json.loads(json.dumps(desired))
        del actual['properties']['name']
        self.assertTrue(bootstrap.same_properties(actual, desired))
        actual['name'] = 'wrong'
        self.assertFalse(bootstrap.same_properties(actual, desired))

    def test_mermaid_is_original_local_procedure(self):
        self.assertIn('mermaid-diagram', bootstrap.LOCAL_SKILLS)
        self.assertFalse(any('mermaid-diagram' in source['skills'] for source in bootstrap.SOURCES))
        self.assertIn('mermaid-diagram', bootstrap.ROLES['lab-incident-analyst'][0])

    def test_diagnostics_source_is_pinned(self):
        source = next(source for source in bootstrap.SOURCES if 'azure-diagnostics' in source['skills'])
        self.assertEqual(source['repo'], 'microsoft/azure-skills')
        self.assertRegex(source['commit'], r'^[0-9a-f]{40}$')
        self.assertEqual(source['skills']['azure-diagnostics'], 'skills/azure-diagnostics')

    def test_specialists_select_diagnostics_within_skill_limit(self):
        for name in ('lab-network-specialist', 'lab-vm-specialist', 'lab-k8s-specialist'):
            skills, _ = bootstrap.ROLES[name]
            self.assertIn('azure-diagnostics', skills)
            self.assertLessEqual(len(skills), 5)
        self.assertNotIn('azure-diagnostics', bootstrap.ROLES['lab-incident-analyst'][0])

    def test_import_never_attaches_upstream_tools(self):
        resource = bootstrap.skill_resource('azure-diagnostics', 'Diagnostics', 'Upstream tool guidance')
        self.assertEqual(resource['body']['properties']['tools'], [])


class WorksheetTests(unittest.TestCase):
    def test_exact_bootstrap_instructions_and_selections(self):
        for name, (skills, instructions) in bootstrap.ROLES.items():
            text = bootstrap.worksheet(name)
            self.assertIn(instructions, text)
            self.assertIn(bootstrap.CONTRACT.strip(), text)
            self.assertIn('**Choose Skills:** ' + ', '.join(f'`{skill}`' for skill in skills), text)
            self.assertNotIn('lab-incident-recorder', text)
            if name != 'lab-triage':
                self.assertIn('**Handoff Agents:** none;', text)


class BundleAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        state_patch = patch.object(bootstrap, 'STATE', Path(self.directory.name))
        state_patch.start()
        self.addCleanup(state_patch.stop)
        records = []
        for source in bootstrap.SOURCES:
            for name, directory in source['skills'].items():
                contents = {'SKILL.md': '# Fixture skill\n'}
                if name == 'azure-diagnostics':
                    contents['troubleshooting/aks/aks-troubleshooting.md'] = '# AKS fixture\n'
                    contents['troubleshooting/compute/vm-troubleshooting.md'] = '# VM fixture\n'
                    contents['scripts/aks-baseline.sh'] = 'exit 99\n'
                hashes = {}
                for relative, content in contents.items():
                    path = bootstrap.STATE / 'vendor' / name / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding='utf-8')
                    hashes[relative] = hashlib.sha256(content.encode()).hexdigest()
                records.append({'name': name, 'repo': source['repo'], 'commit': source['commit'],
                                'license': source['license'], 'path': directory, 'files': hashes})
        bootstrap.save(bootstrap.STATE / 'sources.lock.json', records)

    def test_supporting_files_are_imported_without_execution(self):
        with patch.object(bootstrap.subprocess, 'run', side_effect=AssertionError('No execution allowed')):
            resources = bootstrap.build({'scope': {'fixture': True}})
        self.assertEqual(len(resources), 17)
        diagnostic = next(item['body']['properties'] for item in resources if item['body']['name'] == 'azure-diagnostics')
        self.assertEqual(len(diagnostic['additionalFiles']), 3)
        self.assertTrue(all('filePath' in item and 'name' not in item for item in diagnostic['additionalFiles']))
        self.assertIn('Operational Azure incident diagnosis', diagnostic['description'])
        self.assertEqual(diagnostic['tools'], [])
        skills = {item['body']['name'] for item in resources if item['kind'] == 'skills'}
        for resource in resources:
            if resource['kind'] == 'agents':
                self.assertLessEqual(len(resource['body']['properties']['handoffDescription']), 500)
                self.assertLessEqual(len(resource['body']['properties']['allowedSkills']), 5)
                self.assertTrue(set(resource['body']['properties']['allowedSkills']) <= skills)

    def test_changed_diagnostic_script_is_rejected(self):
        script = bootstrap.STATE / 'vendor/azure-diagnostics/scripts/aks-baseline.sh'
        script.write_text('changed\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Cached file changed'):
            bootstrap.build({'scope': {'fixture': True}})


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        state_patch = patch.object(bootstrap, 'STATE', Path(self.directory.name))
        state_patch.start()
        self.addCleanup(state_patch.stop)
        subscription = '11111111-1111-1111-1111-111111111111'
        group = f'/subscriptions/{subscription}/resourceGroups/workload'
        self.config = {
            'agentResourceId': f'/subscriptions/{subscription}/resourceGroups/agent/providers/Microsoft.App/agents/demo',
            'scope': {'resourceGroups': [group], 'clusterResourceId': group + '/providers/Microsoft.ContainerService/managedClusters/aks', 'namespace': 'lab'},
            'readOnlyBoundariesVerified': True,
            'approvedUnlicensedSources': [],
        }
        self.resources = [bootstrap.skill_resource('one', 'description', 'procedure'),
                          bootstrap.skill_resource('two', 'description', 'procedure')]
        build_patch = patch.object(bootstrap, 'build', return_value=self.resources)
        build_patch.start()
        self.addCleanup(build_patch.stop)
        self.client = FakeClient()

    def run_command(self, command):
        bootstrap.execute(command, self.config, self.config['agentResourceId'], self.client)

    def test_plan_is_read_only(self):
        self.run_command('plan')
        self.assertEqual(self.client.writes, [])
        self.assertTrue((bootstrap.STATE / 'export.json').exists())

    def test_apply_and_repeat_plan_are_idempotent(self):
        self.run_command('plan')
        self.run_command('apply')
        self.assertEqual(self.client.writes, ['one', 'two'])
        self.run_command('verify')
        self.run_command('plan')
        self.run_command('apply')
        self.assertEqual(self.client.writes, ['one', 'two'])

    def test_drift_blocks_all_writes(self):
        self.run_command('plan')
        self.client.values['one'] = {'properties': {'skillContent': 'external change'}}
        with self.assertRaisesRegex(ValueError, 'drifted'):
            self.run_command('apply')
        self.assertEqual(self.client.writes, [])

    def test_attestation_required(self):
        self.run_command('plan')
        self.config['readOnlyBoundariesVerified'] = False
        with self.assertRaisesRegex(ValueError, 'readOnlyBoundariesVerified'):
            self.run_command('apply')
        self.assertEqual(self.client.writes, [])

    def test_unlicensed_publication_requires_permission(self):
        self.run_command('plan')
        self.config['approvedUnlicensedSources'] = []
        with patch.object(bootstrap, 'SOURCES', [{'repo': 'fixture/unlicensed', 'requiresPermission': True}]):
            with self.assertRaisesRegex(ValueError, 'obtain permission'):
                self.run_command('apply')
        self.assertEqual(self.client.writes, [])

    def test_partial_failure_retains_backup_and_journal(self):
        self.run_command('plan')
        self.client.fail_name = 'two'
        with self.assertRaisesRegex(ValueError, 'injected'):
            self.run_command('apply')
        self.assertEqual(self.client.writes, ['one'])
        self.assertEqual(len(list(bootstrap.STATE.glob('backup-*.json'))), 1)
        self.assertEqual(bootstrap.load(bootstrap.STATE / 'applied.json')['completed'], [{'kind': 'skills', 'name': 'one'}])

    def test_verify_rejects_missing_definition(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.run_command('verify')


if __name__ == '__main__':
    unittest.main()