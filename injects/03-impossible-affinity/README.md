# Scenario 03: Impossible Affinity (Facilitator Only)

Portability: see [shared configuration](../CONFIGURATION.md).

## Portable Configuration

Select a JSON configuration with `INJECT_CONFIG`. All four `target` fields
(`context`, `namespace`, inspected HTTPS `server`, and `kubeconfig`) must be
explicitly configured; ambient `KUBECONFIG` is not used as a fallback. The scripts
validate these fields before invoking kubectl and compare the selected API URL
before proceeding. Plans perform read-only cluster inspection, not offline simulation.

Configure `workloads.product.name`, `container`, and `selector` for the deployment.
It must have exactly one container with the configured name. Set
`workloads.product.image` to enforce an exact image guard, or leave it empty to
disable that optional guard. Set `scenarios.03.zone` to a deliberately unavailable
zone and `scenarios.03.tolerations` to the tolerations to append to the baseline.
The default tolerations list is empty; no lab-specific toleration is implicit.
Request and rollout timeouts use `timing.request` and `timing.rollout`.

The plan reports the actual configured target, workload, zone, image guard and
tolerations. Injection still requires `--apply`. Baselines and locks live under
`.state/<configuration identity>/` via the shared `state_directory` helper.
Saved baselines must match the complete configuration identity and deployment
UID before reuse. Historical unscoped baselines are not migrated automatically;
preserve them for their original rehearsal rather than copying them into a new
configuration directory. An absent or empty `{}` baseline affinity is accepted,
including after reset; nonempty existing affinity requires a separately reviewed plan.

## Historical Rehearsal

The deployment names, images, zones, tolerations, commands, query and live results
below describe the 2026-11-10 rehearsal only. They are not portable defaults or
evidence that a different configured target has been tested. Adapt inspection,
recovery and alert examples to the selected configuration. This portability
change was validated offline only; it made no live calls.

## Plan and symptom

Inspected 2026-11-10: product-service `2.2.0`, one healthy replica, Linux selector,
no affinity; current nodes have zone `0`. Scope is `aks-store-demo` on context
`aks-srehackk8s-y2p5u5` with exact API guard. No NodePool/NodeClass is modified.
Injection requires nonexistent zone `francecentral-99` and tolerates the existing
`lab-scaling` pool so NAP can evaluate and reject the invalid zone. The label is
not fabricated on a node: that would conceal rather than solve the scheduling fault.

```bash
bash injects/03-impossible-affinity/inject.sh --plan
# Obtain explicit facilitator approval:
bash injects/03-impossible-affinity/inject.sh --apply
kubectl -n aks-store-demo describe pod <pending-product-pod>
kubectl -n aks-store-demo get events --sort-by=.lastTimestamp
```

A new product-service pod remains Pending; the old Ready replica can remain
during the stalled rolling update, so complete storefront failure is not promised.
Karpenter should report no compatible instance/zone; inspect the actual events.
No eligible NodeClaim may be created. Other workloads/namespaces must not be changed.

## Root cause and expected fix

Required node affinity is a hard constraint. A nonexistent Azure zone cannot be
satisfied by an instance, even when existing nodes have spare CPU. Remove/correct
the required affinity using real eligible zone labels and allowed pool requirements.
Do not install standalone Karpenter on this managed-NAP cluster.

```bash
kubectl -n aks-store-demo patch deployment product-service --type=merge -p '{"spec":{"template":{"spec":{"affinity":null}}}}'
bash injects/03-impossible-affinity/verify.sh
bash injects/03-impossible-affinity/reset.sh
```

Verification requires fully updated Ready/available replicas and checks each
actual Ready node against both the pod and deployment nodeSelector/required
affinity, including OR terms, AND expressions and supported operators. It does
not accept readiness of an old rollout as recovery. Reset restores saved
affinity/tolerations, checks recreated-resource UIDs and refuses unexpected edits.
Baseline stays in private gitignored `.state`; repeated inject/reset is supported.
One scenario at a time: separate checkouts do not share the local lock.

## Three hint levels

1. Compare old/new ReplicaSets; inspect the Pending pod rather than application logs.
2. Read required node affinity and compare it with actual node zone labels and the
   eligible NodePool's requirements; capacity alone cannot solve incompatible constraints.
3. `francecentral-99` is not an available zone. Remove/correct that constraint,
   complete the rollout and verify actual placement. Reset removes the added toleration.

## Azure Monitor alert

Create a workspace-scoped log search alert; replace `<AKS_RESOURCE_ID>`:

```kusto
KubePodInventory
| where TimeGenerated > ago(5m)
| where ClusterId =~ "<AKS_RESOURCE_ID>" and Namespace == "aks-store-demo"
| where Name startswith "product-service-"
| summarize arg_max(TimeGenerated, *) by PodUid
| where PodStatus =~ "Pending"
| summarize PendingPods=count()
```

Use numeric `PendingPods`, Maximum > 0, evaluation 1 minute, lookback 5 minutes,
severity 2, automatic resolution. Test the query on the injected Pending pod.
Attach an enabled Action Group with a real receiver, connect Azure Monitor intake
to the SRE Agent response plan, and record firing, delivery and agent incident.
None of these Azure resources is created by the scripts; intake is not yet tested.

## Validation and boundaries

Run `python3 -m unittest discover -s injects/03-impossible-affinity -p 'test_*.py'`.
Live rehearsal passed 2026-11-10 with explicit approval: new pod Pending, Karpenter
event "no instance type met the scheduling requirements" with zone
`francecentral-99`, independent affinity removal, actual-node verification, reset
and repeated reset. A label-wide wait included the old Ready replica and timed
out; the retained Pending pod/events provided the failure proof instead.
Alert delivery/intake is untested. Optional 03b is NOT implemented: it requires
separate image-manifest proof and ARM capacity approval; do not assume tag `2.2.0`
is single-architecture. No writes occur outside the namespace. During injection,
external storefront users may see degraded catalog capacity. A toleration alone
does not force healthy replacement pods onto the existing NAP pool.

Current references reviewed 2026-11-10:

- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-aksnodeclass
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-log-alert-rule