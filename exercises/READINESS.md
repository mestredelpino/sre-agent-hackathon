# Workshop Readiness And Remaining Work

Status reviewed 2026-11-06. This is the persistent delivery checklist; the chat
todo list is only a work-session tracker. A checked documentation item does not
mean every team has deployed or passed its live acceptance gate.

## Completed Implementation And Documentation

- [x] Two-day agenda, eight progressive labs, fixed lunches and welcome export.
- [x] [Build-to-lab inventory](../WORKSHOP-SETUP.md#built-components-and-workshop-coverage)
  maps the implemented platform, app, monitoring, agent and scaling components.
- [x] [Lab 1](labs/01-platform.md): Overlay/Cilium, ACNS, fixed system nodes,
  managed KEDA/NAP, identity, quota, CIDRs, controllers and Karpenter API checks.
- [x] [Lab 2](labs/02-application.md): pinned store overlay, database startup fix,
  two ingress paths, product/order checks and disposable-storage limitations.
- [x] [Reusable storefront NSG rule](../scenarios/kubernetes/store-demo/README.md#optional-subnet-nsg-storefront-access):
  explicit existing NSG, disabled by default, IPv4 /32 TCP/80, reviewed setup and
  removal. Terraform validation and static rule checks pass; the generic option
  has not been applied to a fresh team environment.
- [x] [Lab 3](labs/03-observability.md): telemetry collection and identity paths,
  six panels, optional Graphviz, Azure Monitor rules, receiver configuration and
  test-alert instructions. All five monitoring tests now pass.
- [x] [Lab 4](labs/04-agent-configuration.md): five agents, twelve skills,
  supporting files, pinned bootstrap, tools, native delegation, permissions,
  knowledge, both paused Review plans, read-back and recovery instructions.
- [x] [Lab 5](labs/05-agent-validation.md): executable acceptance procedure for
  actual agent reads, skill use, denial, delegation and real alert intake.
- [x] [Lab 6](labs/06-autoscaling.md): RabbitMQ scaler/authentication, bounded
  customers/workers, tainted NodePool/AKSNodeClass, separate deterministic node
  probe, consolidation and reset. All fifteen scaling tests pass.
- [x] [Labs 7](labs/07-challenge.md) and [8](labs/08-closeout.md): common
  facilitator-only faults, original agent outputs, separate human assistance,
  recovery, retained-object cleanup and cost/disposal ownership.
- [x] Twenty bootstrap tests pass; workshop checks cover schedules, component
  coverage, duplicate sections and local links. These are offline checks.

## Required Live Verification Before Delivery

- [ ] Facilitator/subscription owner: rehearse a fresh team deployment from its
  original root, including quota, consent, policies and the actual timeboxes.
- [ ] Network owner: verify the opt-in rule against the team's effective NSGs,
  rule ownership and priorities if needed. Prove current external HTTP, products,
  images and a processed order; the facilitator's repaired path is not team proof.
- [ ] Monitoring owner: configure the approved `alert_email` receiver or approved
  equivalent, apply a reviewed plan, then capture rule evaluation and delivered
  notification. The recorded facilitator action group had no receiver; no later
  delivery proof is recorded here.
- [ ] Agent owner: prove runtime skill retrieval/use, scoped query execution,
  permitted-read and denied-action checks, actual native Task call/return, and
  alert-to-intended-thread routing. Published definitions and paused plans do
  not satisfy these checks. Preserve evidence using Lab 5.
- [ ] Facilitator: rehearse the same fault and reset on equivalent isolated team
  targets, with timing, sealed records, STOP and equal observation windows.
  Existing nginx helpers do not establish store-compatible fault automation.
- [ ] Resource owners: rehearse overnight restart/rebinding and final cleanup,
  including manual alerts/plans, NSG rule, NAP nodes and remaining Azure costs.

Mark each gate PASS, FAIL or BLOCKED with UTC evidence and its actual owner.
Unperformed tests stay unchecked; use labeled saved evidence/prebuilt fallback
when agreed rather than claiming a live success.

## Not Built Or Outside The Baseline

- [ ] Continuous external storefront availability probe and alert: manual curl,
  pod readiness and Application Gateway health do not cover the separate store
  LoadBalancer/NSG path. Implement and rehearse it or explicitly accept the gap.
- [ ] Dedicated queue/HPA/NAP dashboard panels: current scaling evidence comes
  from helper status, metrics and Kubernetes objects, not dedicated panels.
- [ ] Store-specific automated common-fault helpers, if the store is selected
  instead of the existing nginx scenario: design/rehearse before enabling them.

Durable database/queue storage, backup/restore, production TLS/hardening and
distributed tracing are not part of this disposable baseline. Do not describe
them as completed or silently make them requirements within existing lab slots.

## Operator-Only Recovery Records

The sibling infrastructure repository owns the live deployment's state, private
overrides, MSI reconcile/import record, identity recovery and deployed NSG rule.
The workshop explains their consequences (changed endpoints, identities, IPs and
ephemeral data), not a universal replay procedure. Never copy those plans/state
into a team environment. See the [authoritative-root boundary](../WORKSHOP-SETUP.md#choose-the-authoritative-terraform-root).