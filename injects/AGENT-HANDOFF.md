# Fault Injection Agent Handoff

## Copyable Agent Request

> Read injects/AGENT-HANDOFF.md, injects/README.md and the selected scenario guide.
> Inspect the explicitly configured target and current symptoms before any write.
> Run the read-only plan and obtain approval for its exact scope before applying.
> Introduce one fault at a time unless I explicitly approve overlapping faults.
> Verify an actual broken request or scheduler symptom, then check the matching
> Azure alert instance separately. Do not equate rule deployment with firing or
> delivery. Leave approved faults active until I request recovery. Preserve all
> local configuration and baselines and give me exact recovery commands.
> Never broaden a deny rule, disable a guard, or fabricate a healthy baseline to
> make a failing test pass. Do not change credentials, management access, existing
> unrelated rules, infrastructure state, or notification receivers.

## Targets and Local Prerequisites

The last approved lab is subscription `361b408e-3d2e-4831-bef9-aad31d8d6caa`
(`demos`), tenant `3a691654-794d-44b3-a922-3df7286ec681`, resource group
`rg-sre-agent-hackathon-k8s`, cluster `aks-srehackk8s-y2p5u5`.
These are historical identifiers, not permission to mutate another session.
Confirm the current Azure account and selected API server independently.

Install Bash, Python 3, kubectl, jq, flock, Azure CLI and an appropriate Node.js
runtime. Authenticate locally; never send credentials to an agent or commit them.
The authoritative infrastructure checkout is the sibling `sre-agent-hackathon-infra`;
its local `kubeconfig` and Terraform state are not shipped in this repository.

Create private JSON configuration from [target.example.json](target.example.json)
and [network-target.example.json](network-target.example.json). Read
[CONFIGURATION.md](CONFIGURATION.md) and [NETWORK-FAULTS.md](NETWORK-FAULTS.md).
Set an absolute kubeconfig path, context, namespace and inspected HTTPS API URL.
For network tests, identify an existing Node.js client container in that namespace;
the storefront image in this lab has no Node.js runtime. Never guess pod names.

## Kubernetes Commands

Run from the workshop checkout. Choose a stable absolute configuration filename
outside version control; do not modify any input until recovery is complete.

```bash
export INJECT_CONFIG=/absolute/private/target.local.json
bash injects/03-impossible-affinity/inject.sh --plan
# After exact-target approval:
bash injects/03-impossible-affinity/inject.sh --apply
kubectl --kubeconfig /absolute/private/kubeconfig --context YOUR_CONTEXT \
  -n YOUR_NAMESPACE get pods -l app=product-service -o wide
```

Scenario 03 requires an inspected impossible zone in `scenarios.03.zone`; the
last test used `francecentral-99`. Check FailedScheduling events and the actual
new pod. The old healthy replica can remain; do not claim a complete app outage.

For the network fault, configure `scenarios.07.deployment`, a reserved policy
name, confirmed CNI enforcement, and a real Service probe from a different pod.

```bash
bash injects/07-network-policy/inject.sh --plan
# After exact-target approval:
bash injects/07-network-policy/inject.sh --apply
bash injects/07-network-policy/verify.sh --expect broken
```

This denies ingress only to the configured deployment. Existing additive allow
policies can prevent isolation; never delete someone else's policy to force it.
The script requires a healthy real request before writing and saves recovery state.

## NSG Commands

Read [azure-network/README.md](azure-network/README.md) and privately copy its
[example configuration](azure-network/target.example.json). Confirm all NSG
associations and exact source/destination CIDRs, port and unoccupied priority.
Only set `dedicated_lab` and `exclusive_control` after confirming those conditions;
coordinate other Terraform/operators. Do not pause AGIC for a standalone NSG
rule unless the inspected resource has an actual conflicting writer.

```bash
export AZURE_FAULT_CONFIG=/absolute/private/azure-network.local.json
python3 injects/azure-network/scenario.py nsg plan
# After exact-target approval:
python3 injects/azure-network/scenario.py nsg inject --apply
python3 injects/azure-network/scenario.py nsg verify --expect broken
```

Do not use wildcard or whole-Internet prefixes. Preserve GatewayManager,
AzureLoadBalancer, control-plane and operator recovery paths. The selected endpoint
must be healthy before injection. Fresh connections must show the expected failure;
an NSG rule existing is not proof that this client's traffic traverses it.

## Last Observed State: 2026-11-11

- Scenario 03: applied to `aks-store-demo/product-service`; a new pod was Pending
  with FailedScheduling after requiring `francecentral-99`. Left active by request.
- Scenario 07: applied to `aks-store-demo/store-front`. An `order-service` Node.js
  client observed HTTP 200 become ETIMEDOUT. Subsequently reset with approval;
  the internal healthy HTTP 200 probe passed. Do not assume it is still active.
- NSG rule `sreLabDenyStoreHTTP` was created at priority 900 on
  `vnet-srehackk8s-subnet-aks-nsg-francecentral`, denying inbound TCP from
  `165.225.194.201/32` to `20.199.58.224/32:80`. Left installed, but public HTTP
  remained 200: configuration verified, effective outage NOT verified. Do not
  reuse the source IP without checking the actual traffic path/source.
- Gateway was started; HTTP 502 was observed before the injected network fault.
  No gateway fault or WAF/backend mutation was applied in this session.
- Seven workload alerts were enabled through the infrastructure script. Alert
  firing, email delivery and SRE Agent intake were not verified.

Local configurations on the original machine are
`/tmp/sre-store-faults-20261111.json` and `/tmp/sre-nsg-fault-20261111.json`.
Securely preserve them outside temporary storage, byte-for-byte, before reboot.
Baselines live under the scenario's ignored `.state/<configuration-hash>/` folder.
They are not encrypted and are not pushed. A fresh clone cannot safely reset an
existing fault without the original configuration and saved baseline. Do not
re-inject to reconstruct a baseline or overwrite unexpected drift.

## Recovery Only When Requested

Use the original configuration for the fault being restored:

```bash
export INJECT_CONFIG=/absolute/private/original-target.local.json
bash injects/03-impossible-affinity/reset.sh
bash injects/03-impossible-affinity/verify.sh
# Only if scenario 07 is currently active:
bash injects/07-network-policy/reset.sh --apply
bash injects/07-network-policy/verify.sh
export AZURE_FAULT_CONFIG=/absolute/private/original-azure-network.local.json
python3 injects/azure-network/scenario.py nsg reset --apply
python3 injects/azure-network/scenario.py nsg verify --expect healthy
```

Verify configuration and real traffic independently after convergence. Never
force cleanup past UID/resourceVersion/drift guards or restore whole resources.

## Alerts and Evidence

The infrastructure repository contains `scripts/create-alert-rules.py`,
`scripts/alerts.env`, `scripts/alert-rules.json` and `scripts/ALERTS.md`.
Source the environment file and run the Python script with `--apply` only when
alert creation is approved. It replaces that named group's complete rule catalog;
Terraform also tracks the group and can overwrite it. Coordinate its writer.

`PodPending` requires five minutes plus metric collection/evaluation delay.
Availability alerts do not necessarily fire when the old replica remains Ready.
NSG/NetworkPolicy drops can leave all pods Ready; the seven workload rules do not
provide end-to-end network availability coverage. The gateway unhealthy-host rule
only sees its own backend path, not the direct storefront LoadBalancer endpoint.
Report separately: injected setting, real symptom, matching telemetry, fired alert,
notification delivery, and agent investigation. Mark anything unobserved unverified.