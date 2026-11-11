# Kubernetes Network Faults

Scenarios [07](07-network-policy/README.md), [08](08-ingress-backend/README.md) and
[09](09-service-selector/README.md) share [network_faults.py](network_faults.py).
They use the same explicit `INJECT_CONFIG` target and namespace guards as 01-06,
but do not create NodePools or require a NodeClass. Only offline tests have run;
no NetworkPolicy, Ingress, Service or pod has been changed in a live cluster.

## Configure

Start with [network-target.example.json](network-target.example.json) in a private
target file. Fill the target fields and the selected scenario's inputs. Unused
scenario blocks can remain placeholders. All accepted fields and defaults are in
[config.py](config.py). Resource names, client pod/container, URLs, timeouts, accepted
HTTP statuses, transport-error codes, route host/path/type and backend port are
configurable. There is no implicit cluster, namespace or kubeconfig.

Use only a dedicated lab namespace with no unrelated clients. Inventory the selected
deployment/pod ownership, Services/EndpointSlices, NetworkPolicies and Ingress routes.
Read the relevant scenario before obtaining approval. Pause GitOps/Helm or other
writers through your approved workflow; local configuration locks do not prevent
external reconciliation, concurrent checkouts or other configuration files.
Do not disable the ingress controller: it must reconcile the Ingress fault.

The probe runs a short standard-library Node.js script inside an **existing** pod
and named container, using `kubectl exec -i`, without a shell or filesystem writes.
The image must have Node.js; `probe.executable` can be its absolute path. No probe pod
or credentials are created. The client must be in the configured namespace and have
an allowed path to the configured URL. Scenario 07 requires a different, non-hostNetwork
client outside the isolated deployment. Prefer a dedicated stable client rather
than a pod that will be rescheduled or become unavailable during the rehearsal.

Probes issue GETs, do not follow redirects, validate TLS and do not accept credentials
in URLs. Requests can still produce application/access logs. Configure a read-only
endpoint that returns a known 2xx response. For 07/09, use the actual target Service
DNS/port, not localhost or a direct pod IP. For 08, use the ingress URL/hostname/path,
not the backend Service URL. Confirm DNS resolves to the intended ingress controller.

## Lifecycle

```bash
export INJECT_CONFIG=/absolute/path/to/target.local.json
bash injects/07-network-policy/inject.sh --plan
# Obtain explicit approval for this target and outage.
bash injects/07-network-policy/inject.sh --apply
bash injects/07-network-policy/verify.sh --expect broken
# After diagnosis/repair approval:
bash injects/07-network-policy/reset.sh --apply
bash injects/07-network-policy/verify.sh
```

Substitute the 08 or 09 folder as needed. Injection without `--apply` is a read-only
plan; reset requires `--apply`. `verify.sh` defaults to **healthy**, so an independently
repaired scenario can be verified without resetting first. Use `--expect broken`
only to prove the fault. There is no automatic timer that restores connectivity.
Run one fault at a time; reset and verify healthy before continuing.

Injection checks a real healthy request before saving baseline/intent and mutating.
Mutation read-back is not functional verification: allow CNI/controller/EndpointSlice
convergence and rerun verification. Verification requires both the expected affected
configuration and an actual request outcome, plus Service endpoints for 09.
HTTP error codes alone do not establish controller identity/root cause; retain
controller logs, effective policy and EndpointSlice evidence independently.

Status `0` represents a transport failure **with an explicit error code**, not an
HTTP status. Scenario 07 accepts only `ETIMEDOUT` by default; 09 additionally accepts
`ECONNREFUSED`/`ECONNRESET` because dataplanes reject empty Services differently.
DNS/TLS failures are always rejected, not counted as successful fault injection.
08 defaults to 404/502/503 and no transport failures. Configure observed error
statuses rather than accepting arbitrary failures to make a test pass.

## Safety and Recovery

Only the selected namespace is accessed. 07 creates/deletes one owned policy;
08 patches one route's backend; 09 patches one Service selector. No Azure resource,
existing policy, pod, Deployment spec, other ingress route or cluster-scoped object
is mutated. Ingress controllers can reconcile their own infrastructure as a result
of a changed Ingress; review that downstream blast radius separately.

Baselines/locks use each scenario's `.state/<full-config-hash>/` directory. Preserve
them privately and keep **all configuration unchanged** until recovery completes.
Injection/reset are idempotent while affected settings remain the saved baseline or
fault. Unexpected changes or recreated resource UIDs cause refusal. UID and resourceVersion
preconditions guard patches/deletes. State is saved before mutation so interrupted
runs can inspect/retry/reset; no blind overwrite or force-delete fallback exists.

07 refuses an unowned same-name policy and checks recorded ownership/UID when deleting.
08 locates the saved route by host/path/pathType each time rather than trusting a
stale array index. 09 preserves ports, ClusterIP and all fields except the selector.
After completed reset, archive the private baseline before starting a fresh run.
If another operator edited/recreated the target, inspect the saved baseline and
current state together; restore only the intended field through approved tooling.
Never overwrite the whole resource or remove someone else's NetworkPolicies.

Adding 07-09 introduced new default configuration fields and therefore new full-config
hashes. Do not upgrade scripts in the middle of an older active rehearsal: finish
reset using that rehearsal's original script/configuration first. Do not rename or
manually migrate old baseline directories to bypass identity checks.

## Offline Tests

```bash
python3 -W error -m unittest discover -s injects -p 'test_*.py'
node --test injects/test-network-probe.cjs
python3 -m compileall -q injects
find injects -name '*.sh' -exec bash -n {} \;
```

These tests use a fake Kubernetes API and local HTTP server. They do not prove CNI
enforcement, ingress-controller reconciliation, live rollback or Azure Monitor intake.