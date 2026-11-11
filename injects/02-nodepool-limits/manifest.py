import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config


def manifest(settings, token):
    config.target(settings)
    nodepool = settings['nodepool']
    reference = nodepool['nodeclass_ref']
    if not all(reference.get(key) for key in ('group', 'kind', 'name')):
        raise RuntimeError('Configure nodepool.nodeclass_ref group, kind and name before injection')
    scenario = settings['scenarios']['02']
    result = json.loads(Path(__file__).with_name('nodepool.json').read_text())
    result['apiVersion'] = nodepool['api_version']
    result['metadata'] = {'name': scenario['pool'], 'labels': {'injects.sre/owner': token}}
    result['spec']['limits'] = {'cpu': scenario['cpu_limit'], 'memory': scenario['memory_limit']}
    result['spec']['disruption']['consolidateAfter'] = nodepool['consolidate_after']
    template = result['spec']['template']
    template['metadata']['labels'] = {**nodepool['labels'], 'injects.sre/scenario02': 'limits'}
    template['spec']['nodeClassRef'] = dict(reference)
    template['spec']['startupTaints'] = nodepool['startup_taints']
    requirements = [entry for entry in nodepool['requirements']
                    if entry['key'] != 'karpenter.azure.com/sku-cpu']
    if not any(entry['key'] == 'karpenter.sh/capacity-type' for entry in requirements):
        requirements.append({'key': 'karpenter.sh/capacity-type', 'operator': 'In', 'values': ['on-demand']})
    requirements.append({'key': 'karpenter.azure.com/sku-cpu', 'operator': 'In', 'values': scenario['cpu_sizes']})
    template['spec']['requirements'] = requirements
    return result


if __name__ == '__main__':
    try:
        settings = config.load()
        result = manifest(settings, sys.argv[1])
        if sys.argv[1] == '--nodeclass-resource':
            reference = result['spec']['template']['spec']['nodeClassRef']
            print(f"{reference['kind']}.{reference['group']}")
        else:
            print(json.dumps(result))
    except (RuntimeError, ValueError, OSError, IndexError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)