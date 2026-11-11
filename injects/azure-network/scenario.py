import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

from faults import affected, canonical, desired, fault_settings, require, resource_parts


COMMANDS = {'nsg': ['network', 'nsg'], 'waf': ['network', 'application-gateway', 'waf-policy'],
            'backend': ['network', 'application-gateway']}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Azure:
    def __init__(self, config):
        self.subscription = config['target']['subscription_id']
        account = self.run('account', 'show')
        require(account['tenantId'].lower() == config['target']['tenant_id'].lower(),
                'Azure CLI account tenant mismatch; sign in/select the approved account yourself')
        require(account['id'].lower() == self.subscription.lower(), 'Azure subscription mismatch')

    def run(self, *arguments):
        result = subprocess.run(['az', *arguments, '--subscription', self.subscription,
                                 '--only-show-errors', '--output', 'json'],
                                check=True, text=True, capture_output=True)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def show(self, scenario, options):
        resource = self.run(*COMMANDS[scenario], 'show', '--ids', options['resource_id'])
        require(resource['id'].lower() == options['resource_id'].lower(), 'Unexpected resource returned')
        require(resource.get('provisioningState') == 'Succeeded', 'Resource operation not complete/successful')
        return resource

    def write(self, scenario, options, value):
        group, name = resource_parts(options['resource_id'], self.subscription,
            {'nsg': 'networkSecurityGroups', 'waf': 'ApplicationGatewayWebApplicationFirewallPolicies',
             'backend': 'applicationGateways'}[scenario])
        if scenario == 'nsg':
            arguments = ['network', 'nsg', 'rule']
            scope = ['--resource-group', group, '--nsg-name', name, '--name', options['rule_name']]
            if value is None:
                self.run(*arguments, 'delete', *scope)
            else:
                self.run(*arguments, 'create', *scope, '--priority', str(value['priority']),
                    '--access', 'Deny', '--direction', 'Inbound', '--protocol', 'Tcp',
                    '--source-address-prefixes', value['sourceAddressPrefix'], '--source-port-ranges', '*',
                    '--destination-address-prefixes', value['destinationAddressPrefix'],
                    '--destination-port-ranges', value['destinationPortRange'],
                    '--description', value['description'])
        elif scenario == 'waf':
            self.run(*COMMANDS[scenario], 'update', '--ids', options['resource_id'],
                     '--custom-rules', json.dumps(value))
        else:
            servers = [entry.get('ipAddress') or entry.get('fqdn') for entry in value]
            require(servers and all(servers), 'Cannot restore unsupported backend address entries')
            self.run('network', 'application-gateway', 'address-pool', 'update',
                     '--resource-group', group, '--gateway-name', name, '--name', options['pool_name'],
                     '--servers', *servers)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def http_status(probe, headers=None):
    url = urllib.parse.urlsplit(probe['url'])
    require(url.scheme in ('http', 'https') and url.hostname and not url.username and not url.password,
            'Probe must be an HTTP(S) URL without credentials')
    request = urllib.request.Request(probe['url'], headers=headers or {}, method='GET')
    opener = urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=probe['timeout_seconds']) as response:
            return response.status
    except urllib.error.HTTPError as error:
        error.close()
        return error.code
    except (TimeoutError, socket.timeout):
        return 0
    except urllib.error.URLError as error:
        if isinstance(error.reason, (TimeoutError, socket.timeout)):
            return 0
        raise RuntimeError(f'Probe transport/DNS/TLS error is not proof of the fault: {error.reason}') from error


def check_http(config, scenario, broken):
    probe = config[scenario]['probe']
    require(probe['timeout_seconds'] > 0, 'Probe timeout must be positive')
    if scenario == 'waf':
        status = http_status(probe)
        require(status in probe['healthy_statuses'], f'Unmarked WAF request is not healthy: HTTP {status}')
        options = config[scenario]
        status = http_status(probe, {options['header_name']: options['header_value']})
    else:
        status = http_status(probe)
    expected = probe['broken_statuses'] if broken else probe['healthy_statuses']
    require(status in expected, f'Unexpected HTTP outcome {status}; expected {expected}; retry after propagation')
    print(f'HTTP check passed: {status} (0 means connection timeout)')


def save(path, state):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2))
    temporary.replace(path)


def run(config, scenario, action, apply, directory, expect='broken'):
    options = fault_settings(config, scenario)
    require(config.get('exclusive_control') is True,
            'Pause Terraform/AGIC/other writers and set exclusive_control=true; CLI updates are not atomic')
    os.umask(0o077)
    directory = Path(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = directory / (digest(options['resource_id'].lower()) + '.lock')
    with lock_path.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        azure = Azure(config)
        resource = azure.show(scenario, options)
        current = affected(resource, scenario, options)
        path = directory / digest(config) / (scenario + '.json')
        state = json.loads(path.read_text()) if path.exists() else None
        if state:
            require(state['config_id'] == digest(config), 'Saved target/configuration differs')
            require(state['resource_id'].lower() == resource['id'].lower(), 'Saved resource ID differs')
            require(state.get('resource_guid') == resource.get('resourceGuid'), 'Resource was recreated')
        if action == 'plan':
            after = state['after'] if state else desired(resource, scenario, options)
            print(json.dumps({'scenario': scenario, 'tenant': config['target']['tenant_id'],
                              'subscription': azure.subscription, 'resource': resource['id'],
                              'current': current, 'fault': after, 'state_file': str(path),
                              'mutation': False}, indent=2))
            return
        require(action == 'verify' or apply, 'Mutation requires explicit --apply after reviewing plan')
        if action == 'verify':
            require(state is not None, 'No saved baseline; verification cannot guess original settings')
            broken = expect == 'broken'
            require(canonical(current) == canonical(state['after'] if broken else state['before']),
                    'Affected settings do not match the requested verification state')
            check_http(config, scenario, broken)
            print(f'PASS: {scenario} configuration and HTTP outcome match {expect}')
            return
        if action == 'inject':
            if state:
                require(not state.get('reset_complete'), 'Archive completed state privately before a fresh rehearsal')
            else:
                after = desired(resource, scenario, options)
                check_http(config, scenario, False)
                state = {'config_id': digest(config), 'resource_id': resource['id'],
                         'resource_guid': resource.get('resourceGuid'), 'before': current, 'after': after}
                path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                save(path, state)
            expected, replacement = state['before'], state['after']
        else:
            require(state is not None, 'No saved baseline; refusing reset')
            expected, replacement = state['after'], state['before']
        require(canonical(current) in (canonical(expected), canonical(replacement)),
                'Affected settings drifted; refusing to overwrite another change')
        if canonical(current) != canonical(replacement):
            latest = azure.show(scenario, options)
            require(latest.get('etag') and latest['etag'] == resource.get('etag'),
                    'Resource changed during checks; replan before retrying')
            azure.write(scenario, options, replacement)
        observed = affected(azure.show(scenario, options), scenario, options)
        require(canonical(observed) == canonical(replacement),
                'Write not confirmed; preserve baseline and inspect before retrying/resetting')
        if action == 'reset':
            state['reset_complete'] = True
            save(path, state)
        print(f'{action} configuration confirmed. Run verify --expect {"healthy" if action == "reset" else "broken"} '
              'after Azure propagation; configuration success is not functional verification.')


def main():
    parser = argparse.ArgumentParser(description='Approved isolated Azure network fault rehearsals')
    parser.add_argument('scenario', choices=COMMANDS)
    parser.add_argument('action', choices=['plan', 'inject', 'verify', 'reset'])
    parser.add_argument('--config', default=os.environ.get('AZURE_FAULT_CONFIG'))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--expect', choices=['broken', 'healthy'], default='broken')
    arguments = parser.parse_args()
    require(arguments.config, 'Set AZURE_FAULT_CONFIG or pass --config')
    config = json.loads(Path(arguments.config).read_text())
    run(config, arguments.scenario, arguments.action, arguments.apply,
        Path(__file__).parent / '.state', arguments.expect)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(getattr(error, 'stderr', None) or str(error), file=sys.stderr)
        sys.exit(1)