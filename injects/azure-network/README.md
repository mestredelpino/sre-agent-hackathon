# Azure Network Fault Rehearsals

One Python runner provides three configurable, reversible faults: an inbound NSG
deny, a header-matching WAF block, and an incorrect Application Gateway backend.
These are separate from the Kubernetes scenarios and require separate approval.
On 2026-11-11, a scoped NSG deny was created in the approved lab, but HTTP remained
200: an effective outage was not proven. WAF/backend faults remain offline-tested
only. See the [handoff record](../AGENT-HANDOFF.md) for scope and retained state.

## Prerequisites

- Use only dedicated disposable lab resources, not shared/production infrastructure.
  NSG/backend failures can affect every client using the selected path or pool.
  Check all NSG associations, backend routing references and WAF policy associations.
- Install Python 3 and a current Azure CLI on Linux/WSL. Sign in to the destination
  tenant using your approved workflow. The runner never logs in or changes your
  default account; every CLI call explicitly supplies the configured subscription,
  and account read-back must match both tenant and subscription.
- The operator needs read access and the relevant NSG security-rule, WAF-policy or
  Application Gateway write permissions. Scope permissions to approved lab resources.
- Pause Terraform, AGIC and all other writers through the approved lab process.
  A wrong AGIC-managed backend may otherwise be immediately reconciled. The runner
  does not pause controllers, stop pipelines or grant permissions for you.
- Configure an HTTP(S) GET endpoint that returns a known 2xx response before faults.
  Run probes from a machine that traverses the actual NSG/gateway/WAF path. TLS is
  validated, redirects are not followed, and environment HTTP proxies are bypassed.
  Do not put credentials in URLs, header values or the configuration file.

## Configure and Run

Use [target.example.json](target.example.json) as the shape of your private
`target.local.json`. Replace placeholders for the selected scenario and the tenant/
subscription. Unused scenario blocks may remain placeholders; selected inputs are
validated. There are no default Azure targets. After inspecting scope and pausing
writers, explicitly set `dedicated_lab` and `exclusive_control` to `true`.

```bash
export AZURE_FAULT_CONFIG=/absolute/path/to/target.local.json
python3 injects/azure-network/scenario.py nsg plan
# Obtain approval for the printed target, prefixes, port, and outage.
python3 injects/azure-network/scenario.py nsg inject --apply
python3 injects/azure-network/scenario.py nsg verify --expect broken
# After repair approval:
python3 injects/azure-network/scenario.py nsg reset --apply
python3 injects/azure-network/scenario.py nsg verify --expect healthy
```

Replace `nsg` with `waf` or `backend`. `--config /path/to/file.json` is an alternative
to the environment variable. `plan` performs Azure reads but no mutations; injection
checks the healthy HTTP baseline before saving state and writing. Every injection
and reset requires `--apply`; do not treat that flag as approval without review.
Verification is read-only except normal HTTP GET traffic/access logs.

Run only one fault at a time and verify healthy recovery before the next. Azure
updates and data-plane propagation take time. Retry verification after inspecting
provisioning/backend health; do not broaden a fault just because the first probe
has not changed. There is no background job or automatic delayed reset.

## NSG Deny

Adds one new inbound TCP deny rule with configured source CIDR, destination CIDR,
port and priority. Both CIDRs must be explicit, not `*` or `/0`. Existing rules are
never replaced; name or priority collisions are rejected. Lower numeric priority
wins: choose an unoccupied priority evaluated before the applicable allow rule.
Do not target management, GatewayManager, AzureLoadBalancer, cluster control-plane
or operator recovery traffic. Maintain a separate management path.

NSGs are stateful, so existing connections may survive. Probe a new connection.
For a direct blocked client path, expect timeout (`broken_statuses: [0]`). If the
NSG instead blocks gateway-to-backend traffic, the gateway may return 502; configure
that explicit outcome and use the gateway subnet as the source, not your client IP.
An unrelated DNS/TLS/connection-refused error is rejected, not counted as success.

Hints: (1) compare direct and gateway paths; (2) inspect effective NSG rules and
the source seen at the backend; (3) find the configured deny rule and remove it
through `reset --apply`, or restore independently and verify healthy state.

## WAF Block

Requires an already Enabled/Prevention WAF policy associated with the tested
gateway/listener/path. Adds a custom MatchRule that blocks only requests whose
configured header equals the configured value. Unmarked requests must still be
healthy. The runner never switches Detection to Prevention or weakens managed rules.
Choose a free priority before any earlier terminating Allow rule; otherwise this
fault may never execute. Account for per-listener/per-path policy overrides.

Default symptom: the marked request returns 403 while the unmarked request returns
200. If the policy has an existing custom block status, set `broken_statuses` to that
HTTP error. Earlier rules and routing can affect outcomes; verify WAF logs rather
than assuming a 403 came from this rule. The complete custom-rule list is captured
and updated in one CLI call, preserving existing rules and leaving mode unchanged.

Hints: (1) compare identical requests with/without the configured header; (2) check
the effective WAF policy, rule priority and firewall logs; (3) identify the named
lab rule and use reset to restore the saved rule list.

## Wrong Gateway Backend

Replaces addresses in exactly one existing nonempty pool with one configured,
inspected unused private IP. It does not change listeners, routing rules, backend
HTTP settings, health probes or other pools. Confirm the tested route uses this
pool, the IP is unused/unreachable from the gateway, and no unrelated route shares
the pool. The script cannot prove an IP is unused merely from its address.

Expected symptom after health-probe convergence: unhealthy backend and HTTP 502.
Reset restores the original IP/FQDN address list. Restart paused controllers only
after reset/verification and reconcile IaC to confirm the intended original state.

Hints: (1) distinguish frontend/WAF responses from backend errors; (2) inspect
Application Gateway backend health and the route's actual pool; (3) compare the
pool addresses with the saved baseline and restore using reset.

## State and Recovery

Private baselines live in `.state/<full-config-hash>/<scenario>.json`. Preserve this
directory and keep configuration contents identical until reset completes; changing
even an unused input selects different state. State is not encrypted. A per-resource
local lock coordinates this runner's processes in this checkout only, not remote
operators, other checkouts or controllers. Full resource IDs isolate subscriptions.

The baseline and intended fault are saved atomically before mutation, including
when a CLI call later fails. Repeated inject/reset calls are idempotent while
affected settings match either the saved baseline or intended fault. Unexpected
changes cause refusal, not blind overwrite. WAF checks the entire custom-rule list;
NSG/backend checks the reserved rule/selected address list. Reset preserves current
unrelated settings. After completed reset, archive state privately before a fresh
rehearsal; the runner will not silently recapture a new baseline.

Each write rechecks the resource ETag, but CLI read-check-write is **not atomic**
and the local lock cannot prevent Azure-side races. Exclusive control is mandatory.
Recreation is detected where Azure exposes a changed resourceGuid; an identical-ID
resource without that field cannot be reliably distinguished. Inspect activity logs
and refuse reuse of baselines after any delete/recreate.

If provisioning fails, keep the baseline, inspect Azure operation/activity logs,
and restore only the intended settings using the portal/approved tooling if the
runner refuses the failed provisioning state. Never delete the gateway/policy to
clear an error. Verify healthy HTTP behavior independently after recovery, then
resume writers. Configuration restoration alone is not functional recovery.

## Monitoring

No alert rules or receivers are deployed. In the destination tenant, configure an
Application Gateway unhealthy-backend/failed-request alert and a WAF blocked-request
log alert filtered to the actual gateway, policy and lab rule. For NSGs, use the
approved end-to-end availability probe and effective-rule/Network Watcher evidence;
do not assume newly creating legacy NSG flow logs is supported. Confirm table/metric
schemas and diagnostic collection, exercise a fresh sample, then test Action Group
delivery and SRE Agent incident intake separately.

## Offline Tests

```bash
python3 -W error -m unittest discover -s injects/azure-network -p 'test_*.py'
python3 -m compileall -q injects/azure-network
```

The tests mock Azure and HTTP; no destination permissions, routing, propagation,
notification delivery or live rollback have been proven.

Microsoft references: [NSG rule CLI](https://learn.microsoft.com/cli/azure/network/nsg/rule),
[WAF policy CLI](https://learn.microsoft.com/cli/azure/network/application-gateway/waf-policy),
[backend pool CLI](https://learn.microsoft.com/cli/azure/network/application-gateway/address-pool),
and [WAF custom-rule evaluation](https://learn.microsoft.com/azure/web-application-firewall/ag/custom-waf-rules-overview).