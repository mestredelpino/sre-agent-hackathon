# Lab 1: Inspect The Pre-Provisioned Platform

Day 1 12:00-12:45 is the combined platform, application and observability
architecture walkthrough with Lab 2; 12:45-13:00 confirms access across both labs.
These are shared slots, not separate deployment windows. Use the facilitator's
[environment handover](../pre-provisioned-workshop.md) and
[lab route](../two-day-workshop.md). The platform and SRE Agent resource already
exist. Do not run Terraform, create resources or change role assignments.

## Architecture

![Azure platform: browser HTTPS terminates at Application Gateway; AGIC routes to the Store on AKS. Cilium, managed KEDA and NAP support the cluster.](../../diagrams/platform.svg)

[Editable platform diagram](../../diagrams/platform.drawio).
Trace the public request path separately from cluster management and scaling.
KEDA changes workload replicas; NAP provides bounded node capacity in Lab 6.
Neither is an instruction to start a scaling experiment during this walkthrough.

![Observability: managed Prometheus and Container Insights feed Azure Monitor workspaces and Grafana; alerts and agent reads have separate access boundaries.](../../diagrams/observability.svg)

[Editable observability diagram](../../diagrams/observability.drawio).
Identify metrics, logs, dashboard and alert receiver separately. A resource's
existence does not prove fresh collection, notification delivery or agent intake;
Lab 3 owns those checks.

## Steps

1. Match the private handover to the approved tenant, subscription, resource
   groups, region and team. Record the provisioning/recovery owner, budget and
   STOP contact. In Azure portal, open **Directories + subscriptions**, select
   the approved scope, then **Resource groups** and the supplied group. Compare
   full resource IDs, not just display names; do not create replacement resources.
2. Open the supplied **Kubernetes service**. Read **Overview** for resource ID,
   region and API FQDN; inspect **Node pools** for system capacity and provisioner
   settings, and **Networking** for Overlay/Cilium and the gateway relationship.
   Compare the actual values with the readiness record below. If a blade or
   setting is unavailable to your identity, request dated facilitator evidence
   and label it as supplied rather than claiming your own successful read.
3. Open the supplied **Azure Monitor workspace**, **Log Analytics workspace**
   and **Azure Managed Grafana** resources. Record their IDs and the Grafana
   endpoint. Open the supplied dashboard, select the approved data sources and
   inspect the time range and latest sample timestamps without saving changes.
   Use the observability diagram to explain which source answers metrics versus
   logs questions. Missing access or stale samples are blockers for Lab 3.
4. Open the supplied agent URL at `https://sre.azure.com`; inspect its resource
   and actual execution identity using the
   [product and ownership checks](../../SRE-AGENT-SETUP.md#1-confirm-product-and-ownership).
   Record URL, resource ID, state and approved scope. Do not create another agent
   or broaden roles. A Running resource is not a configured or validated
   investigator: Labs 4-5 establish that evidence. Leave untested automation paused.
5. During the shared 12:45-13:00 access check, confirm portal, Grafana and agent
   reads, then use the supplied dedicated user kubeconfig for the guarded reads
   below if authorized. Keep `KUBECONFIG`, `EXPECTED_CONTEXT`, `AKS_FQDN` and exact
   `API_SERVER` privately for later labs. Never copy Terraform state, deployment
   credentials or administrator kubeconfig into attendee storage.

## AKS Configuration And Readiness Record

Before proceeding, retain a sanitized record of actual settings and their source,
not an assumption that provisioning or a diagram proves readiness:

- Azure CNI Overlay, Cilium and the approved non-overlapping pod/service CIDRs.
   The scaling-enabled root selects pod CIDR `10.244.0.0/16`; review connected
   networks before accepting that value.
- Managed KEDA enabled, NAP provisioning mode `Auto`, default NAP pools `None`,
   and two Ready fixed system nodes. `None` is intentional: Lab 6 creates its own
   bounded pool, rather than relying on an unrestricted default pool.
- Inspect managed controller readiness and the CRDs
   `scaledobjects.keda.sh`, `triggerauthentications.keda.sh`,
   `nodepools.karpenter.sh`, `aksnodeclasses.karpenter.azure.com` and
   `nodeclaims.karpenter.sh`. Managed AKS NAP uses Karpenter APIs; do not install a
   second standalone Karpenter controller to satisfy this check. Missing APIs are
   a readiness/support blocker, not permission to install unrelated controllers.
- Approved region/SKU quota, cluster identity permissions, outbound registry
   access and network policy. A saved NodePool specification cannot guarantee
   available capacity or permission to create a VM.
- AGIC/Application Gateway identity and supplied backend-health evidence for
   the Store HTTPS Ingress. The Store frontend Services are ClusterIP; the old
   direct-HTTP LoadBalancer route is not this workshop baseline.
- Managed Prometheus collection/association, Log Analytics collection and Grafana
   identity/data-source access. Resource creation alone proves none of their data
   paths. Lab 3 verifies fresh samples and receivers.

Use the approved read-only shell with the dedicated user kubeconfig for API
checks. A denial is BLOCKED; obtain labeled owner evidence instead of wider roles:

```bash
: "${KUBECONFIG:?Use the dedicated approved user kubeconfig}"
: "${EXPECTED_CONTEXT:?Use the facilitator-approved context}"
: "${API_SERVER:?Use the facilitator-approved exact API URL}"
test "$(kubectl config current-context)" = "$EXPECTED_CONTEXT" || exit 1
test "$(kubectl --context "$EXPECTED_CONTEXT" config view --minify -o jsonpath='{.clusters[0].cluster.server}')" = "$API_SERVER" || exit 1
kubectl --context "$EXPECTED_CONTEXT" get nodes
kubectl --context "$EXPECTED_CONTEXT" get crd scaledobjects.keda.sh triggerauthentications.keda.sh nodepools.karpenter.sh aksnodeclasses.karpenter.azure.com nodeclaims.karpenter.sh
```

Keep the resulting source revision, target binding and settings with the Lab 1
evidence. Your participant reads do not prove the investigator agent has access.

## Suggested Prompts

Use these as optional discussion or later agent prompts, not as evidence of
runtime validation before Labs 4-5:

> Using only the supplied diagram and handover, explain the public request path,
> metrics/log destinations and separate participant, agent and recovery identities.
> Mark anything not verified as unknown; do not execute tools or change resources.

> Which supplied settings distinguish KEDA replica scaling from NAP node
> provisioning, and which live checks remain necessary before Lab 6?

Optional background: [technical setup](../../WORKSHOP-SETUP.md),
[operator preparation](../../facilitator/README.md) and
[SRE Agent architecture](../sre-agent-architecture.md). Deployment procedures
are owner references outside this attendee slot, not steps to execute here.

## Checkpoint

PASS requires correct target binding, evidence of Ready nodes and expected
platform settings, monitoring access and an accessible Running SRE Agent resource
with identified execution identity. Distinguish your observations from dated
facilitator evidence. Record UTC, actor, revision, resource IDs, PASS/FAIL/BLOCKED
and next owner without including secrets. Configuration/runtime proof comes later.

## Troubleshooting And Safe Stop

For missing resources, access denials or unexpected settings, STOP the dependent
check and contact the provisioning owner. Do not deploy, rebuild, fetch admin
credentials or bypass policy. Label fallback evidence and unfinished work; never
replay a saved plan or claim an old rehearsal is today's observation.

Continue the shared walkthrough with [Lab 2](02-application.md); both labs finish
access checks by 13:00, before the 13:00-13:15 break.