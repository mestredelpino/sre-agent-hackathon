import copy
import ipaddress
import re


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def resource_parts(resource_id, subscription, kind):
    match = re.fullmatch(
        r'/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.Network/([^/]+)/([^/]+)',
        resource_id, re.IGNORECASE)
    require(match is not None, 'Expected a top-level Microsoft.Network resource ID')
    require(match[1].lower() == subscription.lower(), 'Resource belongs to another subscription')
    require(match[3].lower() == kind.lower(), f'Expected resource type {kind}')
    return match[2], match[4]


def fault_settings(config, scenario):
    target = config['target']
    require(all(target.get(key) for key in ('tenant_id', 'subscription_id')), 'Explicit tenant/subscription required')
    options = config[scenario]
    kind = {'nsg': 'networkSecurityGroups', 'waf': 'ApplicationGatewayWebApplicationFirewallPolicies',
            'backend': 'applicationGateways'}[scenario]
    resource_parts(options['resource_id'], target['subscription_id'], kind)
    require(config.get('dedicated_lab') is True, 'Set dedicated_lab=true only for an approved isolated lab')
    if scenario == 'nsg':
        require(100 <= options['priority'] <= 4096, 'NSG priority must be 100..4096')
        for key in ('source_prefix', 'destination_prefix'):
            network = ipaddress.ip_network(options[key], strict=False)
            require(network.prefixlen > 0, 'Wildcard/whole-Internet NSG prefixes are not allowed')
        require(1 <= int(options['destination_port']) <= 65535, 'Specify one destination TCP port')
    elif scenario == 'waf':
        require(1 <= options['priority'] <= 100, 'WAF priority must be 1..100')
        require(re.fullmatch(r'[A-Za-z0-9-]+', options['header_name']) is not None, 'Invalid header name')
        require(bool(options['header_value']), 'A nonempty test header value is required')
    else:
        address = ipaddress.ip_address(options['wrong_address'])
        require(address.is_private and not address.is_unspecified and not address.is_loopback,
                'Choose an inspected unused private backend IP')
        probe = options['probe']
        require(probe['healthy_statuses'] and all(200 <= status < 300 for status in probe['healthy_statuses']),
            'Healthy probe statuses must be successful HTTP 2xx responses')
        require(probe['broken_statuses'] and all(status == 0 or 400 <= status <= 599
            for status in probe['broken_statuses']), 'Broken statuses must be HTTP errors or timeout (0)')
        require(scenario != 'waf' or 0 not in probe['broken_statuses'], 'WAF verification requires an HTTP block response')
        require(probe['timeout_seconds'] > 0, 'Probe timeout must be positive')
    return options


def affected(resource, scenario, options):
    if scenario == 'nsg':
        return next((rule for rule in resource.get('securityRules', [])
                     if rule['name'] == options['rule_name']), None)
    if scenario == 'waf':
        return copy.deepcopy(resource.get('customRules', []))
    pool = next((pool for pool in resource['backendAddressPools']
                 if pool['name'] == options['pool_name']), None)
    require(pool is not None, 'Configured backend pool not found')
    return copy.deepcopy(pool.get('backendAddresses', []))


def desired(resource, scenario, options):
    before = affected(resource, scenario, options)
    if scenario == 'nsg':
        require(before is None, 'Reserved NSG rule already exists')
        require(not any(rule['priority'] == options['priority'] for rule in resource.get('securityRules', [])),
                'NSG priority already occupied')
        return {'name': options['rule_name'], 'priority': options['priority'], 'access': 'Deny',
                'direction': 'Inbound', 'protocol': 'Tcp', 'sourceAddressPrefix': options['source_prefix'],
                'sourcePortRange': '*', 'destinationAddressPrefix': options['destination_prefix'],
                'destinationPortRange': str(options['destination_port']),
                'description': 'Approved SRE lab fault; restore using saved local state'}
    if scenario == 'waf':
        settings = resource.get('policySettings', {})
        require(settings.get('mode') == 'Prevention' and settings.get('state') == 'Enabled',
                'WAF must already be Enabled/Prevention; script never changes policy mode')
        require(not any(rule['name'] == options['rule_name'] or rule['priority'] == options['priority']
                        for rule in before), 'WAF rule name or priority occupied')
        return before + [{'name': options['rule_name'], 'priority': options['priority'],
                          'ruleType': 'MatchRule', 'action': 'Block', 'state': 'Enabled',
                          'matchConditions': [{'matchVariables': [{'variableName': 'RequestHeaders',
                              'selector': options['header_name']}], 'operator': 'Equal',
                              'negationConditon': False, 'matchValues': [options['header_value']],
                              'transforms': []}]}]
    require(bool(before), 'Refusing to overwrite an empty backend pool')
    result = [{'ipAddress': options['wrong_address']}]
    require(before != result, 'Backend already has the configured wrong address')
    return result


def canonical(value):
    if isinstance(value, dict):
        return {key: canonical(item) for key, item in value.items()
                if key not in ('etag', 'provisioningState', 'id', 'type', 'resourceGroup') and item is not None and item != []}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value