# 09: Service Selector Mismatch

Replaces one Service's selector with a unique lab label that currently matches no
pods. The Service remains present but loses its ready EndpointSlice addresses.
Read the shared [configuration and recovery guide](../NETWORK-FAULTS.md) first.

## Prerequisites and Symptom

Configure `scenarios.09.service` and a Node.js client pod/container with a read-only
URL using that Service's DNS and port. The Service must have a nonempty selector,
ready EndpointSlice addresses and a successful baseline request. Selectorless,
headless and ExternalName Services are rejected. No Service ports, IPs, traffic
policies, pod labels or Deployment fields are changed.

Expected symptom: Service DNS can still resolve and pods can remain healthy, but
new requests time out or receive a connection refusal/reset depending on dataplane.
Every client of the Service is affected. A URL that bypasses the Service invalidates
the exercise; do not replace the target with a direct pod IP or localhost.
The verifier requires both zero ready endpoints and the configured transport error,
not simply any failed request. DNS/TLS errors do not count as success.

## Run and Repair

```bash
bash injects/09-service-selector/inject.sh --plan
# Obtain injection approval.
bash injects/09-service-selector/inject.sh --apply
bash injects/09-service-selector/verify.sh --expect broken
# Obtain repair approval.
bash injects/09-service-selector/reset.sh --apply
bash injects/09-service-selector/verify.sh
```

Reset restores the captured selector using Service UID/resourceVersion guards.
Healthy verification requires the original selector, ready EndpointSlice addresses
and an actual successful request. Wait for EndpointSlice convergence; do not
hand-edit EndpointSlices or relabel application pods to satisfy the bad selector.

## Three Hints

1. Separate DNS resolution, ready application pods and Service reachability.
2. Compare the Service selector with actual pod labels and inspect EndpointSlices.
3. Find the saved original selector and restore that field only through reset.

## Azure Monitor Alert

If kube-state-metrics Service endpoint availability is collected, confirm the
actual exposed metric/schema before creating an alert; do not assume a particular
endpoint-count metric exists. Otherwise use the existing in-cluster synthetic
request-failure signal. Filter to the configured cluster/namespace/Service, set a
window/threshold, wire an enabled Action Group and SRE Agent intake, then validate
a fresh failed request and receiver delivery. No monitoring resources are created.

Offline-tested only; live dataplane convergence and recovery have not been rehearsed.