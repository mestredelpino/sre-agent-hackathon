# Scenario 01: Crashloop Secret (Facilitator Only)

> Portability: select your target and workload/broker/timing settings with
> `INJECT_CONFIG`; see [shared configuration](../CONFIGURATION.md).
> Names, commands and recorded results below describe the historical rehearsal,
> not current defaults. Scripts use the shared loader and keep private baselines
> and locks in `.state/$CONFIG_ID/` for each complete configuration.

## Scope and approval

Inspected on 2026-11-10: context `aks-srehackk8s-y2p5u5`, namespace
`aks-store-demo`, order-service image `2.2.0`, RabbitMQ `4.3.2-management-alpine`.
Only `order-service-secrets.data.ORDER_QUEUE_PASSWORD` and an order-service pod
template annotation are changed. No NodePool or other namespace is modified.
Do not run another failure against this namespace during this scenario.

```bash
bash injects/01-crashloop-secret/inject.sh --plan
bash injects/01-crashloop-secret/verify.sh
# Stop here and get explicit approval before applying the fault.
bash injects/01-crashloop-secret/inject.sh --apply
```

The saved baseline in `.state/$CONFIG_ID/baseline.json` contains a base64-encoded password,
not an encrypted password. It is gitignored, owner-readable and must stay private.
The scripts refuse a different cluster API, changed image/config contract, recreated
resources or an unexpectedly changed credential. A per-directory lock prevents
overlapping invocations on this checkout, not on other machines/checkouts.
Never delete the baseline while the scenario is active. Re-runs reuse it rather
than backing up the broken password. If someone rotates the healthy credential,
reset first and archive/remove the old baseline before rehearsing again.

## Symptoms and root cause

Orders fail at `POST /` with HTTP 5xx or timeouts; virtual-customer logs report
failures and order-service logs show RabbitMQ authentication failures.
The inspected application catches initial broker connection errors, so `/health`
can return 200 and pods can remain Ready. CrashLoopBackOff is possible but is NOT
the required symptom and must NOT be the sole alert signal.

`order-service-configs` selects `rabbitmq:5672`, queue `orders`;
`order-service-secrets` supplies `ORDER_QUEUE_USERNAME` and `ORDER_QUEUE_PASSWORD`
through `envFrom`. The injection replaces only the password with a deliberately
invalid value and changes the pod template to load it.

## Expected fix and verification

Restore the known-good password from the private baseline/credential authority,
then roll order-service so its environment is refreshed. Do not weaken RabbitMQ
authentication, change its password, or disable probes to conceal the symptom.
The baseline can be restored using:

```bash
bash injects/01-crashloop-secret/reset.sh
bash injects/01-crashloop-secret/verify.sh
```

The verifier is independent of the saved baseline and does not require the fault
marker to be removed. It checks target replicas, Running/Ready conditions, no
termination within five minutes, and unchanged pod UIDs/restart counts over a
60-second observation. It submits a uniquely tagged order through the Service
and requires HTTP 201 from the broker-confirmed publication path.
The inspected application returns 201 only after RabbitMQ ACCEPTED. RabbitMQ's
management endpoint has no publish counter in this installation, so the verifier
instead checks the running publisher/route acknowledgement contract and confirms
the real `orders` queue is running before and after the POST. This proves broker
acceptance, not durable storage or downstream processing. It fails closed when
broker management or the inspected code contract is unavailable. The synthetic
order is real and may be processed/persisted by the app. No queue is purged and
consumers/KEDA are not paused. Verification is safely repeatable but adds one
order per successful run. It is not a historical order-durability test.

Reset preserves unrelated Secret fields and deployment settings. Repeating reset
does not deliberately start another rollout. An interrupted injection can be
recovered with reset once the baseline exists. Check rollout completion and run
verification again; successful restoration alone is not a functional pass.

## Hints

1. Compare a storefront order attempt with order-service health and recent logs.
   A healthy HTTP probe does not prove a healthy broker connection.
2. Follow the deployment's `envFrom` references. Compare broker hostname/queue
   settings with authentication failure messages, without printing credentials.
3. Inspect the password source in `order-service-secrets`. Restore its known-good
   `ORDER_QUEUE_PASSWORD` and roll the deployment; prove a new order is accepted.

## Azure Monitor alert and SRE Agent intake

Create an Azure Monitor **log search alert** scoped to the cluster's Log Analytics
workspace. The following query uses the legacy `ContainerLog` table observed in
this workshop. Substitute the exact cluster ARM resource ID for `<AKS_RESOURCE_ID>`
and test against a controlled failed order before enabling the rule. If collection
uses only `ContainerLogV2`, adapt the source and verify fresh matching records.

```kusto
let pods = KubePodInventory
| where TimeGenerated > ago(15m)
| where ClusterId =~ "<AKS_RESOURCE_ID>" and Namespace == "aks-store-demo"
| where Name startswith "order-service-"
| summarize arg_max(TimeGenerated, *) by ContainerID
| project ContainerID;
ContainerLog
| where TimeGenerated > ago(5m)
| join kind=inner pods on ContainerID
| where LogEntry has_any ("failed to initialize RabbitMQ connection",
                          "ACCESS_REFUSED", "AuthenticationFailure", "SASL")
| summarize Failures=count()
```

Set measurement to numeric column `Failures`, aggregation Maximum, threshold
greater than 0, evaluation every 1 minute, lookback 5 minutes, severity 2, and
automatic resolution. Confirm the real auth failure text matches the query;
absence of a matching sample is a failed alert rehearsal, not proof of health.
Where HTTP telemetry exists, add an order-route 5xx/failed synthetic order alert;
do not alert solely on pod readiness or an empty queue.

Attach an enabled Action Group with a configured receiver and test its delivery.
In SRE Agent, configure Azure Monitor incident intake/response-plan filtering for
this alert/cluster and keep remediation approval-gated. A firing rule does not
prove agent intake: record alert ID, fired time, delivered notification and the
matching agent investigation. Do not assume the workshop's existing action group
has receivers. No alert, receiver or response plan is created by these scripts.

Official references, reviewed 2026-11-10:

- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-log-alert-rule
- https://learn.microsoft.com/en-us/azure/sre-agent/incident-response
- https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools

## Rehearsal record

Rehearsed live on 2026-11-10 with explicit facilitator approval:

- Healthy-baseline verification passed with a real order and 60-second stability.
- Injection rolled order-service; probes stayed green, but a real order returned
   HTTP 500 and the verifier rejected RabbitMQ management HTTP 401.
- Reset restored the original password and removed only the scenario marker.
- Recovery verification passed: real order HTTP 201 via RabbitMQ ACCEPTED, queue
   running, no recent restarts and 60 seconds of unchanged pod identity/counters.
- Repeating reset and verification passed again without another rollout.
- All seven offline verifier tests and Bash syntax checks passed.

The first telemetry-counter check failed closed and was replaced after confirming
that the broker does not expose that counter here. Alert deployment/delivery and
SRE Agent intake remain untested. The remediation rehearsal used reset rather
than an independent agent/human repair; no agent-led remediation is claimed.

Offline verifier checks:

```bash
node --test injects/01-crashloop-secret/test-verifier.cjs
```

Outside-scope risk: no writes outside this namespace, but the failed order path
affects all users of this shared store, including any external storefront clients.