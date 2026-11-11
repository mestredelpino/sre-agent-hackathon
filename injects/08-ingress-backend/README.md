# 08: Wrong Ingress Backend

Changes the backend of exactly one existing networking.k8s.io/v1 Ingress route to a
configured missing Service/port. Hosts, paths, TLS, annotations, ingress class and
other routes remain unchanged. Read the shared [guide](../NETWORK-FAULTS.md) first.

## Prerequisites and Symptom

Configure `scenarios.08.ingress`, exact `host`, `path`, `path_type`, missing
`wrong_service`, numeric `wrong_port`, and a Node.js client pod/container with a
probe URL that traverses that ingress route. The original backend Service must
exist; the wrong Service must not exist. Resource-backed/default-backend-only
routes and ambiguous host/path matches are unsupported.

Expected symptom depends on controller: commonly 404, 502 or 503 while direct
Service access still works. AGIC and other controllers may reject the bad route
and retain a last-known-good downstream configuration; in that case broken
verification must fail, not claim an outage. Inspect controller logs and actual
traffic before selecting an appropriate disposable controller/route for the lab.
The script does not patch Application Gateway directly. Pause external GitOps/IaC
writers but leave the ingress controller running. Every client of the selected
route can be affected, including routes translated into a shared gateway.

## Run and Repair

```bash
bash injects/08-ingress-backend/inject.sh --plan
# Obtain injection approval.
bash injects/08-ingress-backend/inject.sh --apply
bash injects/08-ingress-backend/verify.sh --expect broken
# Obtain repair approval.
bash injects/08-ingress-backend/reset.sh --apply
bash injects/08-ingress-backend/verify.sh
```

Reset restores the original backend only, guarded by Ingress UID/resourceVersion.
It resolves the configured route afresh, so unrelated route reordering cannot make
it patch the wrong array entry. Drift in the selected backend/route causes refusal.
Allow controller/backend-health convergence before healthy verification.

## Three Hints

1. Compare direct Service connectivity with the ingress hostname/path.
2. Follow the actual route through ingress class/controller, host, path and backend;
   inspect controller events rather than assuming a pod failure.
3. Compare the selected backend Service/port with the saved baseline and use reset
   to restore only that backend.

## Azure Monitor Alert

Collect the actual ingress-controller access/error logs or exposed response metrics.
Create a destination-workspace scheduled-query/metric alert for configured error
statuses on this hostname/path, filtered to the cluster/namespace/controller. For
AGIC, gateway failed-request/backend-health signals and controller reconciliation
errors may be different evidence; choose the one observed in the approved test.
Set evaluation window/threshold, an enabled Action Group and SRE Agent intake,
then prove fired alert and delivery. The script deploys no diagnostics or alerts.

Offline-tested only; controller reconciliation and downstream outage are unproven.