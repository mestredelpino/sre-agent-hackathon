# Scenario 02: NodePool Limits (Facilitator Only)

> Portability: select your target, customer workload, NodeClass, pool and timing
> settings with `INJECT_CONFIG`; see [shared configuration](../CONFIGURATION.md).
> Names, commands and recorded results below describe the historical rehearsal,
> not current defaults. Injection generates its manifest from configuration;
> the template's historical NodeClass reference is never used. Private baselines
> and locks live together in `.state/$CONFIG_ID/` per complete configuration.

## Plan and boundaries

Context `aks-srehackk8s-y2p5u5`, namespace `aks-store-demo`. Inspected Kubernetes
`1.36.5`, `karpenter.sh/v1` NodePool, and `karpenter.azure.com/v1beta1`
AKSNodeClass on 2026-11-10. Existing `lab-scaling` NodePool and AKSNodeClass
are NOT modified. The new `inject02-limits` NodePool references that Ready
NodeClass read-only, which Microsoft Learn explicitly supports.

```bash
bash injects/02-nodepool-limits/inject.sh --plan
# Obtain explicit injection approval before this command:
bash injects/02-nodepool-limits/inject.sh --apply
```

The dedicated pool has a unique scheduling label and NoSchedule taint, on-demand
amd64 D-family instances with 2 CPU, CPU limit 1, memory ceiling 16Gi and no
expiry. Three virtual-customer replicas get its selector and exact toleration.
The CPU limit is below the smallest allowed node: pods remain Pending regardless
of their tiny requests. A zero disruption budget suppresses voluntary churn
during this limits exercise. It does NOT block explicit NodePool deletion.

Injection preserves original replicas/selector/tolerations privately in `.state`.
It refuses an existing pool of the same name without its saved ownership token.
Rerunning reuses the saved baseline and intentionally re-applies the low limit.
Do not delete `.state` during the scenario or run concurrent failures against the
same deployment/namespace. Scripts on different checkouts do not share the lock.

## Symptoms and investigation trail

virtual-customer has Pending pods and no new customer orders; existing order,
catalog and makeline services need not fail. During rolling update an original
customer pod can remain available. This is a degraded scaling symptom, not
necessarily a complete storefront outage.

```bash
kubectl -n aks-store-demo get pods -l app=virtual-customer -o wide
kubectl -n aks-store-demo describe pod <pending-pod>
kubectl -n aks-store-demo get events --sort-by=.lastTimestamp
kubectl get nodeclaims -l karpenter.sh/nodepool=inject02-limits -o wide
kubectl describe nodepool inject02-limits
```

Follow **pod -> scheduling events -> NodeClaim -> NodePool limits**. The selector
and taint make this pool the only eligible destination. A NodeClaim may never be
created: provisioning can reject candidates before NodeClaim creation. If a
claim exists, inspect its conditions/events and provider allocation errors rather
than assuming every Pending pod means a CPU-limit failure. Controller logs in
`kube-system` can be read but must never be patched for this exercise.

## Expected fix and verification

Raise only the dedicated pool CPU limit to 4, preserving placement isolation:

```bash
kubectl patch nodepool inject02-limits --type=merge -p '{"spec":{"limits":{"cpu":"4"}}}'
bash injects/02-nodepool-limits/verify.sh
```

The verifier requires exactly three current Ready/updated/available replicas,
no Pending pods, a running completed rollout, and actual placement on Ready
nodes belonging to the dedicated pool. Removing the selector or reducing replica
count cannot pass. Provisioning can take several minutes; quota, image availability
or regional capacity may independently block the repair. Fixing those problems
outside the allowed scope requires separate approval.

```bash
bash injects/02-nodepool-limits/reset.sh
```

Reset restores original replicas and scheduling fields with UID/resourceVersion
guards, waits for recovery, then deletes only the owned scenario pool and checks
its nodes/claims are gone. Unexpected scheduling edits require manual review
rather than overwriting them. The controller performs node/claim deletion; do not
remove finalizers or delete underlying Azure VMs manually. `verify.sh` is a repair
check before reset, not a check that a removed exercise still exists afterward.

## Hints

1. Compare desired replicas, ready replicas and pod scheduling events. This is not
   an application crash or a RabbitMQ credential problem.
2. Follow the workload selector/toleration to its eligible NodePool; look for a
   limit rejection even if no NodeClaim exists.
3. Compare `spec.limits.cpu: 1` with allowed `karpenter.azure.com/sku-cpu: ["2"]`.
   Raise the scenario limit; do not modify pre-existing pools or unpin the workload.

## Azure Monitor alert instructions

Create a log search alert on the cluster Log Analytics workspace using this query.
Replace `<AKS_RESOURCE_ID>` with the exact cluster ARM resource ID. Test collection
with the live injected Pending pods, not only the query editor's syntax check.

```kusto
KubePodInventory
| where TimeGenerated > ago(5m)
| where ClusterId =~ "<AKS_RESOURCE_ID>" and Namespace == "aks-store-demo"
| where Name startswith "virtual-customer-"
| summarize arg_max(TimeGenerated, *) by PodUid
| where PodStatus =~ "Pending"
| summarize PendingPods=count()
```

Measurement `PendingPods`, aggregation Maximum, greater than 0, every minute,
5-minute lookback, severity 2, automatic resolution. Attach an enabled Action
Group with a real receiver and connect the alert to the Azure SRE Agent incident
intake/response plan. Record fired alert ID, delivery and agent investigation;
creating a rule alone does not prove intake. Telemetry ingestion latency can
delay firing/clearance. No alert or action group is deployed by these scripts.

## References and rehearsal

Current Microsoft Learn, reviewed 2026-11-10:

- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-aksnodeclass
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-disruption
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-log-alert-rule

Live rehearsal passed on 2026-11-10 with explicit approval: injection produced a
Pending new replica and no NodeClaims; retained Karpenter events reported
"all available instance types exceed limits for nodepool (NodePool=inject02-limits)".
Raising only CPU limit to 4 provisioned a node and all three replicas passed the
placement/readiness verifier. Reset restored the original one replica and scheduling,
then deleted the owned pool and controller-managed claims/nodes. Initial reset
detected asynchronous claim cleanup; after adding bounded deletion waits, reset
and a repeated reset passed. Schema server dry-run and Bash syntax checks passed.
Alert delivery/SRE Agent intake and independent agent-led remediation are untested.

## Shared-cluster risk

No existing pool or other namespace is patched. New nodes still run cluster-wide
DaemonSets, consume shared subscription quota/IPs and incur Azure charges. Reset
deletes scenario nodes; if any unrelated non-DaemonSet workloads use them, stop and
obtain approval before deletion. A NoSchedule taint is not an absolute security
boundary: workloads elsewhere with broad tolerations can still land on the pool.