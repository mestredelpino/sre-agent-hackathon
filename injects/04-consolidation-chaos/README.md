# Scenario 04: Consolidation Chaos (Facilitator Only)

## Portable configuration

Select a reviewed JSON file with `INJECT_CONFIG`; see the shared
[configuration guide](../CONFIGURATION.md). The entry points use `../config.py`
through `runtime.py`'s `SETTINGS`. Configure `target` (context, namespace, server,
kubeconfig), `workloads.database.name`, `workloads.broker.name`, and
`workloads.order.name` / `container` for broker witness execution. Workload selector
settings should reflect the deployment's real labels. PDB creation reads each
StatefulSet's actual `spec.selector.matchLabels`, not `app=<name>`; empty selectors
and `matchExpressions` are rejected. Verification matches PDB selectors against
actual pod labels.

Configure `scenarios.04` pool/filler names, filler image, CPU/memory requests and
limits, low CPU request, pool CPU limit and witness queue. Filler labels and
affinity are derived from the configured filler name. `nodepool` supplies the API
version, NodeClass reference, requirements, labels, sizes and disruption settings.
Reset paths use the configured namespace and NodePool API version. The witness
receives broker/settings JSON arguments: `broker.management_url`, `vhost`,
`username_env`, `password_env` and `scenarios.04.witness_queue` determine requests;
credentials are read from the configured environment keys inside the exec
container, not passed as JSON values. `timing.request` controls HTTP timeout;
`rollout`, `delete`, `consolidation` and `protection` control wait windows.

Runtime state is bound to the complete configuration identity beneath
`.state/<config-id>/`; changing settings does not reuse an old baseline. Preserve
existing state until its original target is safely reset. `--plan` performs target
reads and is not an offline check. For offline validation only:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s injects/04-consolidation-chaos -p 'test_*.py'
node --check injects/04-consolidation-chaos/witness.cjs
node --test injects/04-consolidation-chaos/test_witness.cjs
bash -n injects/04-consolidation-chaos/{inject,verify,reset}.sh
```

## Destructive rehearsal plan

Historical inspection on 2026-11-10 found `documentdb` (MongoDB-compatible DocumentDB, not
MongoDB image) and `rabbitmq`, one replica each, no volumes/PVC templates/PDBs.
Use the actual app implementations, do not replace the database for this exercise.
Historical context/namespace were `aks-srehackk8s-y2p5u5` / `aks-store-demo`;
these are not current target defaults. All concrete names, quantities and timings
below describe that historical rehearsal; current execution uses the configuration.

```bash
bash injects/04-consolidation-chaos/inject.sh --plan
# Explicit approval must include irreversible loss of existing ephemeral data:
bash injects/04-consolidation-chaos/inject.sh --apply
```

This creates only `inject04-consolidation`, pins the two stateful workloads there
with a label/taint and affinity to a scenario filler. Existing NodePools and the
referenced AKSNodeClass are read-only. Filler requests 2 CPU, forcing a larger node;
then drops to 1m so a cheaper 2-CPU node can replace it. The pool uses
`WhenEmptyOrUnderutilized`, `consolidateAfter: 10s`, `expireAfter: Never`, and
`budgets: []`. Omitting budgets would default to 10%, not mean no budget.
No pre-existing PDB is removed: injection refuses any namespace PDBs/protection.

Moving these pods initially already loses their process-local data; after placement
the script creates a separate durable witness queue/message in RabbitMQ, lowers
filler requests, and waits up to 15 minutes for **natural** replacement of both
stateful pods. The witness queue must then be absent. No forced node deletion is
used to masquerade as consolidation. If NAP finds no cheaper consolidation option,
injection fails rather than claiming success. Inspect events/claims for cause.
Rerunning completed injection does not repeat destructive loss; interrupted runs
reuse the baseline but can lose more data. Obtain approval before recovery retries.

## Symptoms, cause and expected fix

Stateful pod UIDs change, broker queues/messages disappear, and stored orders can
disappear. Catalog products may be reseeded by the application, so a populated
catalog does not prove durability. Lack of persistent storage is the data-loss
cause; consolidation is the disruption trigger. PDBs/budgets reduce voluntary
disruption but do not make ephemeral storage durable or protect against VM failure.

Create effective `minAvailable: 1` PDBs for both single-replica workloads and set
an always-active pool disruption budget `nodes: "0"`, or use pod-level
`karpenter.sh/do-not-disrupt: "true"` in addition to the PDBs. A helper applies
the first repair without modifying other pools:

```bash
python3 injects/04-consolidation-chaos/scenario.py protect
bash injects/04-consolidation-chaos/verify.sh
bash injects/04-consolidation-chaos/reset.sh
```

Verification checks effective healthy PDB coverage with zero disruptions allowed,
actual placement and additional protection, raises/lowers filler demand again,
and checks unchanged stateful UID/node/restart counts over 180 seconds. This is a
bounded voluntary-disruption test, not a guarantee against expiration, explicit
deletion, terminationGracePeriod overrides or Spot interruption. Future production
work requires persistent volumes, backups, replicas and tested restoration.

Reset removes only scenario-owned PDBs/filler/pool after restoring scheduling.
It refuses deletion if unrelated non-DaemonSet pods remain on scenario nodes,
including pods in other namespaces. Saved workload replicas/scheduling are restored,
not historical database/queue contents. Restore required data from a separately
validated backup; the script never claims an ephemeral-data backup exists.
RabbitMQ replacement may require reconnecting application clients; verify a real
order afterward using Scenario 01's functional check and approve client restarts
if the application cannot reconnect automatically.

## Hints

1. Compare pod UIDs/start times with missing order history; a Ready stateful pod
   says nothing about whether it still has the previous pod's data.
2. Follow pod -> node -> NodeClaim -> NodePool disruption settings/events. Check
   PVCs and PDBs; distinguish voluntary consolidation from manual deletion.
3. Add PDBs plus a zero pool disruption budget or do-not-disrupt annotation, rerun
   pressure reduction, then address durable storage separately.

## Azure Monitor alert and agent intake

Create a Log Analytics log search alert for stateful replacement, substituting the
cluster resource ID, configured namespace and StatefulSet pod names. The old
namespace/workload values below are historical examples. Historical pod rows allow UID replacement detection even
when Kubernetes restartCount resets to zero:

```kusto
KubePodInventory
| where TimeGenerated > ago(10m)
| where ClusterId =~ "<AKS_RESOURCE_ID>" and Namespace == "aks-store-demo"
| where Name in ("documentdb-0", "rabbitmq-0")
| summarize PodIdentities=dcount(PodUid), Restarts=max(PodRestartCount) by Name
| where PodIdentities > 1 or Restarts > 0
| summarize AffectedWorkloads=count()
```

Measure `AffectedWorkloads`, Maximum > 0, every minute, 10-minute lookback,
severity 2, automatic resolution. Test actual column availability and fresh data;
restart-count history may produce alerts unrelated to this injection. Add business
order-loss checks where history telemetry exists; UID churn is a proxy, not a data
loss proof. Configure a real Action Group receiver and SRE Agent Azure Monitor
intake/response plan, then record firing/delivery/agent incident. Not deployed by
scripts and not yet tested.

## References and risks

- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-disruption
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-aksnodeclass

Reviewed against current docs and live v1 CRD on 2026-11-10. Some Learn disruption
examples use older spelling/expiry placement; the installed schema and successful
server dry-run are authoritative for this cluster (`WhenEmptyOrUnderutilized`,
`spec.template.spec.expireAfter`). Live approved rehearsal passed 2026-11-10:
natural consolidation replaced both pods, the durable broker witness disappeared,
and PDBs plus a zero budget prevented stateful UID/restart changes on a 180-second
retrigger. Reset removed scenario resources and restored scheduling. Historical
data was not recoverable. The producer retained a stale connection: a real order
timed out until separately approved rollouts of order-service, makeline-service
and virtual-worker. After those restarts Scenario 01's real-order verification
passed. Client reconnection is a required manual recovery step if this recurs;
reset does not silently restart these additional deployments. Alert intake untested.
Billable capacity up to an 8-vCPU pool limit and shared quota/IP consumption can
affect the cluster; external store users will be affected by the stateful restarts.
All script writes stay in the target namespace or the created NodePool. Private
`.state` holds baseline and witnesses; do not delete while active. Run one failure
at a time and do not concurrently edit targeted scheduling/resource fields.