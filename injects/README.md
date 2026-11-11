# Facilitator Fault Scenarios

For delegation, use the [agent handoff guide](AGENT-HANDOFF.md), including exact
commands, last observed faults, alert limitations and recovery-state requirements.

Current scripts use [portable JSON configuration](CONFIGURATION.md) selected by
`INJECT_CONFIG`; start with [target.example.json](target.example.json). Cluster,
namespace, API server and kubeconfig must be explicit, with no original-cluster
fallback. The rehearsal details below are historical, not runtime defaults.

Rehearsed sequentially with explicit approval on `aks-srehackk8s-y2p5u5`, namespace
**aks-store-demo**, 2026-11-10, before the portability update. Those results do not
validate a new cluster/tenant. Configure `target.kubeconfig` in your JSON file;
the scripts no longer inherit the old path or `KUBECONFIG` environment variable.
No credentials or local baselines belong in source control.

## Catalog

1. [Crashloop secret](01-crashloop-secret/README.md): invalid RabbitMQ password;
   probes can stay healthy while real orders fail.
2. [NodePool limits](02-nodepool-limits/README.md): dedicated pool limit prevents
   its smallest allowed node; verify actual three-replica placement after repair.
3. [Impossible affinity](03-impossible-affinity/README.md): nonexistent zone;
   verify Ready replicas on nodes satisfying their real scheduling requirements.
4. [Consolidation chaos](04-consolidation-chaos/README.md): natural consolidation
   erases ephemeral state; PDB/budget repair with active stability retrigger.
5. [Spot roulette](05-spot-roulette/README.md): manual Spot claim deletion and
   replacement block; actively prove an on-demand replacement under Spot exclusion.
6. [Cost blowout](06-cost-blowout/README.md): reduced-cost oversized requests,
   measured usage and at least 50% actual pool vCPU reduction.
7. [NetworkPolicy](07-network-policy/README.md): owned deny-ingress policy selecting
  one deployment; real client timeout check with CNI/additive-policy prerequisites.
8. [Ingress backend](08-ingress-backend/README.md): one route points to a missing
  Service; real ingress response verification and controller-dependent outcomes.
9. [Service selector](09-service-selector/README.md): selector mismatch removes
  ready EndpointSlice addresses while pods and Service DNS can remain healthy.

Scenarios 07-09 are **offline-tested only**, not part of the original live rehearsals.
Use their [shared network-fault guide](NETWORK-FAULTS.md) and
[configuration example](network-target.example.json). They do not create NodePools.

Separate Azure infrastructure faults are available in
[Azure network rehearsals](azure-network/README.md): scoped NSG deny, header-matching
WAF block and wrong Application Gateway backend addresses. These require explicit
Azure tenant/subscription/resource configuration and separate approval; they are
not covered by the Kubernetes namespace-only authorization or historical rehearsals.

Each numbered Kubernetes folder contains injection, verification and reset shell entry points plus
facilitator symptoms/root cause/fix, three hint levels and Azure Monitor alert
creation instructions. Copy accompanying helpers too: Scenarios 04-06 require
[runtime.py](runtime.py), not just their shell wrappers. 07-09 additionally use
[network_faults.py](network_faults.py) and [network-probe.cjs](network-probe.cjs).

## Run Rules

- Run one failure at a time in this shared namespace, in order. Separate agent
  sessions/checkouts do not isolate workloads or share the local script locks.
- Read the scenario and run `bash injects/<scenario>/inject.sh --plan` first.
  Get explicit approval before **every** `--apply`, including data-loss/cost scope.
- Verification is a functional repair check, not an undo check. Scenarios 04/05
  verification actively retriggers demand/disruption; obtain approval for that too.
- Keep private gitignored `.state` while active. It can contain credentials and is
  not encrypted. After verified cleanup, securely archive/remove that rehearsal's
  baseline before a fresh run, especially after credential/replica changes.
- Reset restores captured workload settings and removes owned capacity. It never
  restores historical data from ephemeral queues/databases. Read Scenario 04's
  separately approved client-reconnection recovery step before using it again.
- Existing NodePools, AKSNodeClasses, Azure NSGs and other namespaces are not
  patched. Read-only all-namespace inspection prevents deleting nodes used by
  unrelated pods. Scenario 05 explicitly deletes only owned-pool NodeClaims.
- Do not force-delete claims/nodes, strip finalizers, or change quota/network
  configuration without separate approval. Taints are not security boundaries.

Dependencies: Bash, kubectl, jq, flock, Python 3, and the app's installed Node
runtime. Use `bash` to invoke entry points. External store clients can be affected;
new capacity consumes shared quota/IPs, runs cluster DaemonSets and incurs charges.

## Live Rehearsal Results

- **01 passed:** bad credential -> actual order HTTP 500 and verifier rejection ->
  password restored -> real order accepted by RabbitMQ -> repeated reset/verify.
  No CrashLoopBackOff is claimed: the app catches broker errors and probes stay green.
- **02 passed:** Pending replica/no claim, Karpenter event "all available instance
  types exceed limits" -> raised owned pool limit -> three Ready replicas placed on
  real scenario nodes -> reset/repeated reset, owned pool/claims/nodes gone.
- **03 passed:** Pending/incompatible-instance event for `francecentral-99` ->
  independent affinity removal -> real-node verification -> reset/repeated reset.
  Optional ARM/single-arch variant 03b is not implemented.
- **04 passed with recovery caveat:** natural consolidation replaced both stateful
  pods and erased a seeded durable RabbitMQ witness -> PDBs/zero-budget fix ->
  180-second retrigger with unchanged stateful UID/restarts -> scheduling reset.
  Existing ephemeral data was irreversibly lost by approval. Broker clients retained
  stale connections; separately approved restarts of order-service, makeline-service
  and virtual-worker restored functional order publication. No database restoration
  or persisted order/product-history comparison is claimed.
- **05 passed:** real Spot placement -> claim deletion/blocked replacement -> repair
  -> controlled Spot exclusion/second claim deletion -> Ready on-demand replacement
  -> reset. This is not a provider eviction-notice or real regional shortage test.
- **06 passed:** reduced at facilitator request to three 1-CPU/2Gi replicas under
  an 8-vCPU ceiling. Baseline: three Standard_D2as_v5 nodes / **6 vCPU**. Repair:
  three 10m/64Mi replicas on one Standard_D2als_v6 / **2 vCPU**, a **66.7% reduction**.
  Actual usage bounds passed. Reset/repeated reset removed owned capacity and
  restored original resources/replicas/scheduling. Transient missing metrics and
  terminating old pods required bounded retries; neither check was bypassed.

These are facilitator repairs, not proof of autonomous agent diagnosis/remediation.
Documented tests intentionally place synthetic real orders; those can persist in
the app. No production peak-load/performance, historical-data recovery, real Spot
outage or Azure notification integration is claimed.

Final live audit passed: all seven deployments and both StatefulSets restored to
one Ready replica; real order HTTP 201 through RabbitMQ acceptance; product actual
node placement valid; no scenario PDBs, NodePools, NodeClaims or nodes remain.
Only original `lab-scaling` NodePool (zero nodes) and two system nodes remain.
All 26 focused offline tests, Bash syntax and Python compilation passed. All six
folders have their four required deliverables and executable shell entry points.

## Remaining Manual Gates

Alert instructions are supplied, **not deployed**. Validate each workspace's table/
metric schema, exact cluster selector and fresh symptom sample. Create the Azure
Monitor rule, configure an enabled Action Group with a real receiver, connect SRE
Agent incident intake/response-plan filtering, and capture the fired alert plus
matching agent investigation. Rule creation alone does not prove delivery/intake.

Scenario 04 remains deliberately non-durable; backups, persistent storage and
automatic reconnect behavior require separate work. Its reset restores the original
unprotected baseline, not a production-hardened database architecture. Final cluster
health/cleanup must be checked after each future session, even when a test fails.

## Offline Checks

```bash
node --test injects/01-crashloop-secret/test-verifier.cjs injects/04-consolidation-chaos/test_witness.cjs
node --test injects/test-network-probe.cjs
python3 -m unittest discover -s injects -p 'test_*.py'
python3 -m unittest discover -s injects/02-nodepool-limits -p 'test_*.py'
python3 -m unittest discover -s injects/03-impossible-affinity -p 'test_*.py'
python3 -m unittest discover -s injects/04-consolidation-chaos -p 'test_*.py'
python3 -m unittest discover -s injects/06-cost-blowout -p 'test_*.py'
python3 -m unittest discover -s injects/azure-network -p 'test_*.py'
python3 -m compileall -q injects
find injects -name '*.sh' -exec bash -n {} \;
```

On this WSL host, use the Windows Node binary if Linux Node is unavailable.
Live API server dry-run validation passed before each scenario NodePool injection.