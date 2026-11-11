# Portable Target Configuration

Every scenario reads one JSON file selected by **INJECT_CONFIG**. There is no
default cluster, namespace, kubeconfig path or API server. Missing target values
stop execution before kubectl runs. Authentication comes from that kubeconfig;
these scripts do not select an Azure tenant, sign in, or create Azure resources.

Start with [target.example.json](target.example.json), create a private target
file and replace every `YOUR_...` placeholder after inspecting the destination.
Keep it outside version control; `target.local.json` is ignored here.

```bash
export INJECT_CONFIG=/absolute/path/to/target.local.json
python3 injects/config.py
bash injects/01-crashloop-secret/inject.sh --plan
```

`python3 injects/config.py` prints the resolved noncredential settings as quoted
environment assignments; it does not contact the cluster. Configured broker URLs
must not contain credentials. The app supplies broker credentials from its own
environment; never put passwords/tokens in the JSON file.

For Kubernetes NetworkPolicy, Ingress and Service-selector faults (07-09), use
[network-target.example.json](network-target.example.json) and the
[network-fault guide](NETWORK-FAULTS.md). No NodeClass is needed. Finish older
active rehearsals before upgrading: newly added defaults change the full-config
state hash, so old baselines must not be manually moved to the new hash.

## Target and Inspection

Required `target` fields: `context`, `namespace`, `server` (exact inspected HTTPS
Kubernetes API URL), and `kubeconfig` (path on this machine). The scripts pass them
explicitly to every kubectl operation and compare the selected context's server
with the configured URL. They do not inherit the active kubectl context or an old
local KUBECONFIG. For a different tenant, acquire and test an appropriately scoped
kubeconfig using your normal approved sign-in workflow first.

Inspect the destination before configuring or injecting:

```bash
kubectl --kubeconfig /path/to/config --context YOUR_CONTEXT config view --minify
kubectl --kubeconfig /path/to/config --context YOUR_CONTEXT -n YOUR_NAMESPACE get deployments,statefulsets,services,secrets,configmaps,pdb,pvc
kubectl --kubeconfig /path/to/config --context YOUR_CONTEXT get nodepools,aksnodeclasses
kubectl --kubeconfig /path/to/config --context YOUR_CONTEXT explain nodepool.spec --recursive
```

Do not print Secret contents. Describe targeted workloads and inspect CRD fields,
image versions, selectors, env/envFrom, probes, queue/HTTP contracts, actual zones,
SKU availability and NodeClass readiness. Validate generated pools using server
dry-run against the destination CRD before approval. Current scripts use managed
NAP NodePool v1 semantics: a configurable API version does not translate schemas.
Never install standalone Karpenter or change existing pools to fit these scripts.

## Input Groups

All accepted inputs and lab defaults are defined in [config.py](config.py);
the supplied JSON overrides only the values you need. Unknown keys fail rather
than silently falling back to defaults. Lists replace entire lists.

- `target`: explicit Kubernetes target identity and kubeconfig path.
- `workloads`: roles `order`, `customer`, `product`, `makeline`, `front`, `database`,
  `broker`. Set `name` and `selector`; deployments additionally have `container`
  and optional `image` pins. Configure selectors independently of resource names.
  Empty image pins permit the inspected image but do not imply API compatibility.
- `broker`: Secret/ConfigMap names, credential/config key names, hostname, port,
  queue, virtual host, management/order/health URLs, app publisher/route paths and
  synthetic `test_order` body. URLs and key values must match the real app. Current
  Scenario 01 intentionally requires Secret + ConfigMap envFrom and a single main
  container; unsupported layouts fail, not auto-mutate unrelated resources.
- `nodepool`: NodePool API version, existing read-only `nodeclass_ref`, labels,
  instance requirements, startup taints, CPU sizes, memory ceiling and consolidation
  delay. Configure these from the destination cluster/network dataplane; Cilium
  defaults are not appropriate for every cluster. NodeClass name is mandatory for
  scenarios that create pools. Existing NodeClass/pools are never modified.
- `timing`: Kubernetes request, rollout/deletion, consolidation/metrics wait and
  pod stability/protection windows. Values except `request` are seconds.
- `scenarios.01`: deliberately wrong password value (not a real credential).
- `scenarios.02`: owned pool name, low CPU/memory limits, allowed CPU sizes and
  target replicas. Choose limits that genuinely prevent allowed instance allocation.
- `scenarios.03`: confirmed impossible `zone` and required pool `tolerations` list.
  Include existing taints only after inspection so NAP can evaluate the bad zone;
  otherwise the visible failure may simply be an untolerated taint.
- `scenarios.04`: owned pool/filler names, filler image/resource demand and reduction,
  CPU ceiling, witness queue name. Database/broker remain single-replica ephemeral
  StatefulSets starting at ordinal zero; durable/replicated variants are rejected.
- `scenarios.05`: owned pool, healthy/blocked CPU ceilings and baseline replicas.
  Verification actively simulates Spot exclusion and deletes owned Spot claims.
- `scenarios.06`: pool CPU/memory ceilings, CPU sizes, replicas, large/small resource
  objects, minimum inflated baseline, reduction percentage, usage thresholds and
  metric sampling. Budget for capacity and confirm a feasible reduction first.
- `scenarios.07`: deployment, owned NetworkPolicy name, explicit enforcement
  confirmation and existing client pod/container HTTP probe settings.
- `scenarios.08`: Ingress name, exact host/path/path type, missing backend Service/
  port and client probe through the actual ingress URL.
- `scenarios.09`: Service name and client probe through its DNS/port. Selector
  mismatch is unique to the rehearsal; the original selector is captured, not guessed.

Standard Kubernetes label names and deliberate fault behavior remain fixed protocol
constants, not tenant inputs. The apps must retain the verified RabbitMQ HTTP/order
acknowledgement contract; configuration does not make arbitrary application APIs
compatible. Review a new image implementation before relying on verification.

## Renamed Resources Example

Merge these fields into your target file when the app is renamed:

```json
{
  "workloads": {
    "order": {"name": "orders-api", "container": "api", "selector": "component=orders"},
    "front": {"name": "shop", "container": "web", "selector": "component=web"}
  },
  "broker": {
    "secret": "orders-auth",
    "configmap": "orders-settings",
    "host": "message-broker",
    "queue": "shop-orders",
    "management_url": "http://message-broker:15672/api",
    "order_url": "http://orders-api:3000/",
    "health_url": "http://orders-api:3000/health"
  },
  "scenarios": {"06": {"reduction_percent": 50}}
}
```

## State and Approval

Saved state/locks now live under each scenario's `.state/<configuration-hash>/`.
Target and all resolved inputs determine the hash; state also carries the
configuration identity. Changing the namespace, API, names or sizing cannot reuse
another configuration's credentials/baselines. Keep the **same configuration file
contents until reset completes**; do not lower limits by editing JSON mid-run.
Use the repair commands to change actual workload state instead.

Old pre-portability `.state/baseline.json` files are deliberately NOT migrated or
reused. The original rehearsals were fully reset; retain/archive those files
privately as needed. New target rehearsals have not been performed. Offline mock
tests prove command/config propagation, not live permissions/capacity in your tenant.

Obtain separate approval for every injection and any active verification/data loss
or capacity charge. Parallel agent sessions must still use separate app namespaces
and distinct owned pool names; configuration alone does not isolate shared resources.

## Alerts Across Tenants

Scenario README commands/queries and named resources in historical rehearsal records
are examples, **not deployment defaults**. Substitute the configured namespace,
workload selectors/names and cluster ARM ID in every alert query and manual command.
Choose the destination tenant/subscription, workspace and action group explicitly
in Azure Monitor; no alert provisioning script inherits the old tenant. Validate
fresh tables/metrics, a fired alert, actual receiver delivery and SRE Agent intake.
None of the alert resources or cross-tenant agent permissions has been deployed or
tested by this portability change.