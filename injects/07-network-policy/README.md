# 07: Blocking NetworkPolicy

Creates an owned deny-ingress NetworkPolicy selecting exactly the configured
deployment's nonempty matchLabels selector. Egress is unchanged. Read the shared
[configuration, execution and recovery guide](../NETWORK-FAULTS.md) first.

## Prerequisites and Symptom

Configure `scenarios.07.deployment`, reserved `policy_name`, and the existing Node.js
client pod/container plus target Service URL under `probe`. Confirm the CNI actually
enforces networking.k8s.io/v1 policies, then set `enforcement_confirmed: true`.
The runner does not infer enforcement merely because the API accepts a policy.

Client requests should time out while the Deployment can remain Ready. Existing
connections, kubelet/node-originated traffic and host-network paths can behave
differently; the verifier opens a fresh request from another ordinary pod.
HostNetwork targets/clients, broad/complex deployment selectors, overlapping
workload ownership and matching additive allow-ingress policies are rejected.
Existing allow policies are never removed to force a fault. Other application
clients of these target pods will also be interrupted: use a dedicated lab.

## Run and Repair

```bash
bash injects/07-network-policy/inject.sh --plan
# Obtain injection approval.
bash injects/07-network-policy/inject.sh --apply
bash injects/07-network-policy/verify.sh --expect broken
# Obtain repair approval.
bash injects/07-network-policy/reset.sh --apply
bash injects/07-network-policy/verify.sh
```

Reset removes only the owned policy with UID/resourceVersion preconditions. An
independent repair can remove that policy and run default healthy verification.
Do not add a broad allow policy: that changes unrelated policy posture and prevents
the saved-state verifier from recognizing restoration until the lab policy is gone.

## Three Hints

1. Compare pod readiness with a fresh request from the configured client.
2. Inspect policies selecting the destination pod, not only Service endpoints;
   NetworkPolicy allow rules are additive, not ordered deny/allow firewall rules.
3. Identify the owned `inject07-deny-ingress` policy (or configured name), confirm
   its empty ingress rules, and remove only that lab policy through reset.

## Azure Monitor Alert

Use an existing in-cluster synthetic availability signal for this Service; a
pod-readiness alert alone may never fire. In the destination workspace, configure
a scheduled-query/metric alert on failed fresh requests filtered to the actual
cluster, namespace, client and target. Network-policy drop signals depend on the
installed CNI/collection; do not assume a universal drop metric. Choose the window/
threshold, Action Group and SRE Agent intake explicitly, inject an approved sample,
and prove alert delivery separately. No alert or receiver is deployed by this script.

Offline-tested only; live CNI behavior and recovery have not been rehearsed.