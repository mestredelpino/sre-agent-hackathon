# Scenario 06: Cost Blowout (Facilitator Only)

Use [portable configuration](../CONFIGURATION.md) via `INJECT_CONFIG` for target,
workload, pool, replicas, sizing and reduction target. Names and commands below
describe the original rehearsal, not runtime defaults for your cluster.

## Plan and symptoms

Inspected live 2026-11-10: store-front `2.2.0`, one replica, requests 1m/200Mi,
limits 1 CPU/512Mi, observed `kubectl top` usage 1m CPU/7Mi. Guarded scope:
`aks-srehackk8s-y2p5u5` / `aks-store-demo`. Existing NodePools and referenced
AKSNodeClass remain unchanged.

```bash
bash injects/06-cost-blowout/inject.sh --plan
# Explicit capacity/cost approval required:
bash injects/06-cost-blowout/inject.sh --apply
```

Reduced at facilitator request: creates owned `inject06-cost`, on-demand amd64
D-family 2/4 CPU candidates, CPU ceiling 8 and memory ceiling 32Gi. Pins three
storefront replicas by unique label/taint, each with **1 CPU / 2Gi requests and
limits**. Including DaemonSet overhead, around 4-6 vCPU may be
provisioned. Limits are eventually consistent, not a financial hard cap. Injection
prints and saves actual node count, SKUs and total capacity vCPU after all replicas
are Ready. Re-run preserves the measured baseline rather than overwriting it.

Symptom: healthy but oversized nodes with low real usage. Requests affect packing
and instance choice even when the process barely uses CPU/memory. An Azure billing
increase is delayed; this exercise measures capacity, not an actual cost invoice.

## Investigation trail

```bash
kubectl -n aks-store-demo top pods -l app=store-front --containers
kubectl -n aks-store-demo describe deployment store-front
kubectl get nodeclaims -l karpenter.sh/nodepool=inject06-cost -o wide
kubectl describe nodeclaim <scenario-claim>
kubectl get nodes -l karpenter.sh/nodepool=inject06-cost -L node.kubernetes.io/instance-type
kubectl describe nodepool inject06-cost
```

Read NodeClaim `status.capacity`, `status.allocatable`, `status.providerID` and
`status.nodeName`, selected instance labels and provisioning events to identify
what NAP actually chose; do not infer the final SKU from allowed requirements.
Relate requests plus system/DaemonSet overhead to allocatable capacity. Look at
consolidation events after rightsizing, not just lower requested CPU in the spec.

## Expected fix and verification

Measure representative load and reduce requests while retaining sensible headroom.
The rehearsal helper proposes 10m CPU / 64Mi requests, limits 1 CPU / 512Mi, based
on the inspected sample. These are lab choices, not production recommendations.

```bash
python3 injects/06-cost-blowout/scenario.py repair
bash injects/06-cost-blowout/verify.sh
bash injects/06-cost-blowout/reset.sh
```

Verification keeps three Ready updated replicas on actual scenario-pool nodes,
samples `kubectl top` three times, and requires requests >= observed usage and
within a four-times usage allowance (floors 100m CPU/128Mi memory). Requests must
also be at least 5m/32Mi; setting zero cannot pass. It then waits up to 15 minutes
for **actual total node capacity vCPU to drop at least 50%** versus the saved
inflated baseline, including deleting nodes until fully gone. Replicas cannot be
scaled down or moved off-pool to fake savings. NAP must perform natural consolidation;
the verifier never deletes claims. Transient/idle samples are not a production
load test or evidence of equivalent performance under peak traffic.

Reset restores original replicas/resources/scheduling, removes only owned pool
capacity and refuses deletion with unrelated non-DaemonSet pods present anywhere.
Preserve private `.state` while active; no concurrent edits to targeted fields.

## Hints

1. Compare actual CPU/memory with requested resources; the app can be healthy
   while its scheduling footprint is unnecessarily expensive.
2. Follow pod requests -> allocatable node capacity -> NodeClaim SKU/events.
   Include DaemonSet overhead when explaining why requests affect the chosen VM.
3. Right-size requests, keep target replicas, and wait for consolidation. Prove
   at least 50% capacity reduction from the saved nodes, not just a changed manifest.

## Azure Monitor alert and agent intake

Create a managed Prometheus **PromQL alert** in Azure Monitor scoped to the
cluster's Azure Monitor workspace. Confirm these exact metrics/labels are present
in that workspace and substitute the cluster selector if it contains other clusters:

```promql
sum(kube_pod_container_resource_requests{namespace="aks-store-demo",pod=~"store-front-.*",resource="cpu",unit="core"}) > 2
```

Use a one-minute evaluation interval, `for: 2m`, severity 2 and automatic resolution.
This detects the inflated 3-core storefront footprint without needing delayed
billing data. Add a low-CPU-utilization condition only after validating the actual
container metrics and matching labels; otherwise a missing series can hide the fault.
Test a firing sample while injected, attach an enabled Action Group with a real
receiver, configure SRE Agent Azure Monitor incident intake/response-plan filtering
and record firing/delivery/investigation. Metrics not collected? Configure the
collection and test it before claiming the alert is deployable. Scripts create no
Azure alert/action group and do not claim delivery proof.

## References and rehearsal

- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-disruption
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/prometheus-alerts

Live approved rehearsal passed 2026-11-10: three Standard_D2as_v5 nodes, 6 vCPU,
reduced naturally to one Standard_D2als_v6 node, 2 vCPU (66.7% reduction), with
three rightsized Ready replicas and actual-usage checks. Reset and repeated reset
restored original settings and removed scenario capacity. Transient missing metrics
required bounded readiness retries; terminating old pods required a bounded cleanup
wait. No claim deletion was used for savings. Alert delivery/intake untested.
This scenario consumes
billable on-demand capacity and shared regional quota, subnet IPs and cluster-wide
DaemonSet overhead; those indirect effects can affect workloads outside the target
namespace despite no writes there. Stop and seek approval for any quota/network
change or unrelated workload removal. Reset must clean the scenario nodes afterward.