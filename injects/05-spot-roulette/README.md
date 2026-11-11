# Scenario 05: Spot Roulette (Facilitator Only)

Use [portable configuration](../CONFIGURATION.md) via `INJECT_CONFIG` for target,
workload, pool, replicas and limits. Names and commands below describe the original
rehearsal; substitute your configured values. No original target is a runtime default.

## Plan, symptoms and cause

Inspected live 2026-11-10: makeline-service `2.2.0`, one replica, queue `orders`,
RabbitMQ dependency and MongoDB-compatible DocumentDB order store. Scripts guard
context `aks-srehackk8s-y2p5u5` / namespace `aks-store-demo` and actual image.
Only this deployment and owned `inject05-spot` NodePool are changed. Existing
NodePools/NodeClass are read-only. Requests are tiny; a 4-vCPU pool limit bounds
the exercise, though Karpenter limit enforcement is eventually consistent.

```bash
bash injects/05-spot-roulette/inject.sh --plan
# Explicit approval required:
bash injects/05-spot-roulette/inject.sh --apply
```

Injection waits for real Spot placement with dedicated label/taint and
`karpenter.sh/capacity-type: spot`. Then it sets this pool CPU limit to 0 to
deterministically block replacement and deletes only its Spot NodeClaim using
UID preconditions. This is a **manual interruption simulation**, not an Azure
Spot eviction notice or proof that regional Spot inventory is exhausted.
No arbitrary nonexistent SKU is passed off as a real capacity shortage.
With makeline Pending, orders cannot progress through its processing path.
Spot capacity/quota may be unavailable even before injection; fail closed, do not
switch silently to on-demand and claim that Spot was tested.

## Repair and behavioral verification

Allow both Spot and on-demand in the pool, remove the workload's Spot-only selector,
and restore a sufficient CPU ceiling. This repair helper makes exactly that change:

```bash
python3 injects/05-spot-roulette/scenario.py repair
bash injects/05-spot-roulette/verify.sh
bash injects/05-spot-roulette/reset.sh
```

**verify.sh is an active disruption test**, not read-only. It first checks a healthy
makeline and a both-capacity policy, establishes fresh Spot placement, then temporarily
excludes Spot from the scenario pool, unpins the workload's capacity type, deletes
the Spot claim again, and requires a Ready on-demand replacement on that pool.
Finally it restores the both-types policy. Controlled Spot exclusion is necessary
to prove fallback rather than a lucky Spot retry; it is not a real provider outage.
NodeClaim deletion is guarded against unrelated pods across all namespaces.
The zero voluntary disruption budget prevents template drift from doing the
interruption before explicit deletion. PDBs/budgets cannot guarantee Spot availability.

Reset restores saved workload scheduling and removes owned capacity after unrelated
pod checks. Repeated completed injection does not delete another claim; reset before
a new rehearsal. A failed fallback can leave the workload capacity-constrained;
run repair/reset to recover and report the failure honestly. No existing pool is modified.
Do not delete private `.state` while active or edit scheduling concurrently.

## Hints

1. Follow stuck order processing to makeline readiness and Pending pod events.
2. Inspect node/claim capacity-type labels, workload Spot selector and eligible
   NodePool requirements/limits; distinguish broker failure from lost compute.
3. Remove hard Spot-only placement, allow both types and restore scenario capacity;
   prove on-demand replacement after another controlled Spot interruption.

## Azure Monitor alert and SRE Agent

Create a workspace log search alert with the exact cluster ID:

```kusto
KubePodInventory
| where TimeGenerated > ago(5m)
| where ClusterId =~ "<AKS_RESOURCE_ID>" and Namespace == "aks-store-demo"
| where Name startswith "makeline-service-"
| summarize arg_max(TimeGenerated, *) by PodUid
| where PodStatus =~ "Pending"
| summarize PendingPods=count()
```

Maximum of `PendingPods` > 0, evaluate every minute over 5 minutes, severity 2,
automatic resolution. A long-running pending/processing order alert is preferable
where application telemetry exists; Pending is the tested infrastructure proxy.
Test against the actual fault, attach a real enabled Action Group receiver, route
to SRE Agent Azure Monitor incident intake and record firing/delivery/investigation.
No alert/intake resources are deployed by scripts; notification delivery untested.

## References, rehearsal and cost

- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-disruption

Live approved rehearsal passed 2026-11-10: real Spot placement, owned claim deletion,
Pending replacement under zero CPU ceiling, both-types repair, controlled Spot
exclusion/second claim deletion, actual Ready on-demand replacement and full reset.
This proves the simulated fallback path, not Azure eviction-notice delivery or a
real regional Spot shortage. Alert delivery/agent intake remains untested.
Spot and on-demand tests incur
Azure charges and consume shared quota/IPs. External store users can lose order
processing while makeline is unavailable. No changes outside the namespace or owned
pool, but node-wide DaemonSets share the provisioned nodes. Never delete a claim
with unrelated non-DaemonSet pods present.