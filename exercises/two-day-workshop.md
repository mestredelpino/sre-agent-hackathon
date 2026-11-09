# Two-Day Participant Labs

Follow the [agenda](../AGENDA.md); it owns all event times. Run commands from
the repository root in Bash unless stated otherwise. The main route is AKS and
the pre-provisioned Store app. Labs 1-2 use the
[environment handover](pre-provisioned-workshop.md), not attendee deployment.
The VM material is an optional alternative, not a second workload to deploy
during these slots. No fault injection is allowed until Lab 7.

| Lab | Scheduled time | Deliverable |
| --- | --- | --- |
| [1. Platform](labs/01-platform.md) | Day 1 12:00-12:45 combined architecture; 12:45-13:00 access with Lab 2 | Inspected pre-provisioned platform, scope and approved access |
| [2. Application](labs/02-application.md) | Day 1 12:00-12:45 combined architecture; 12:45-13:00 access with Lab 1 | Application path, workload readiness, public HTTPS and approved synthetic-order evidence |
| [3. Observability](labs/03-observability.md) | Day 1 13:15-14:00 | Fresh dashboard data, operational rules and test notification |
| [4. Agent configuration](labs/04-agent-configuration.md) | Day 1 14:00-15:00 | Full five-agent/twelve-skill bundle, bootstrap, scoped tools/connections, both Review plans and first read |
| [5. Agent validation](labs/05-agent-validation.md) | Day 1 15:00-16:00; checkpoint 15:50-16:00 | Runtime, denial, delegation and real alert-intake evidence; overnight handover |
| [6. Autoscaling](labs/06-autoscaling.md) | Day 2 12:45-13:45 | Observed KEDA and NAP scale-out/scale-in |
| [7. Challenge](labs/07-challenge.md) | Day 2 14:00-14:20 and 14:20-15:00 | Same facilitator-injected scenario per team; original agent outputs and verified reset |
| [8. Closeout](labs/08-closeout.md) | Day 2 15:00-16:00 | Evidence review, presentations and cleanup ownership |

## Before You Start

Check the [persistent readiness checklist](READINESS.md) for completed build/docs,
required live verification and features outside the baseline. Its status is not
a substitute for each team's lab evidence.

Your facilitator supplies the approved subscription/tenant/region, assigned team
resources, participant read access, separate read-only agent identity,
provisioning/broker/recovery owner, budget and STOP contact. Tooling, quota,
provider/policy approval and service availability must be checked before the
event. A failed gate means STOP or a labeled fallback, not wider permissions.

Use the supplied dedicated user kubeconfig and exact approved context/API per
team. Fixed namespace helpers require separate team clusters unless namespaces
and controls have been deliberately adapted and rehearsed. Terraform root/state
and deployment credentials stay with the provisioning owner; attendees do not
apply infrastructure or redeploy the app in Labs 1-2.

For every lab, keep concise private notes: actor, approved scope, source revision,
UTC time, expected versus observed result, PASS/FAIL/BLOCKED and next owner.
No mandatory forms or scoring. Keep credentials, raw state/plans, secrets,
personal data and fault ledgers out of Git, knowledge uploads and screenshots.
An operator terminal result does not prove the agent has the same capability.

The combined architecture walkthrough covers platform, application and
observability from 12:00-12:45; confirm access from 12:45-13:00, then break
13:00-13:15 before Lab 3. Read the diagrams within each lab and the handover;
these remain separate lab guides, not a mandatory continuous workflow.

## Day 1 Checkpoint: 15:50-16:00

Confirm the app, metrics/logs, test receiver, agent configuration and Lab 5
runtime validation checkpoints. Complete first validation on Day 1.
Record unfinished gates without claiming completion. Disable temporary test
rules and pause response plans; retain intended Review settings. Record current
`virtual-customer` replicas before an approved operator scales it to zero for
the night; preserve that baseline privately for restoration on Day 2. Stop any
other explicitly identified synthetic load, without stopping database consumers
while orders remain queued. Close port-forwards, preserve protected state and
record overnight owner, costs and disposal deadline. Stopping traffic does not
stop infrastructure costs. Do not stop AKS unless restart is rehearsed.

## Day 2 Reconnect: 09:00-09:15

Reconfirm subscription/context/exact API, Ready workloads and nodes, public HTTP,
fresh telemetry and agent state. Restore recorded synthetic-customer replicas
only with operator approval, then check order processing. Check for overnight
configuration changes. Repeat failed gates before dependent work; labeled saved
evidence or a facilitator-prebuilt fallback is not a live participant result.

## Day 2 Optional Refinement: 12:00-12:45

Revisit Day 1 agent evidence, resolve recorded blockers and optionally refine
prompts, skills or scoped configuration. Repeat affected validation after a
change. This is not the first Lab 5 validation window; unresolved required gates
remain BLOCKED before dependent work.

## Day 2 Experiment Planning: 10:45-11:00

After the AKS roadmap and NAP/Karpenter presentations, predict which resource
KEDA changes and what makes NAP create a node. Read Lab 6 limits, target guards,
observations and stop conditions. Record customer baseline, approved maximum
load and node budget. This is planning, not an early load or fault window.

Use [Workshop Setup And Operations](../WORKSHOP-SETUP.md) for technical context.
Older one-day exercise clocks and briefing exports are reference material only;
this route and the agenda supersede their timings and fault allowances.

## Offline Document Check

```bash
node exercises/verify-two-day.mjs
```

Run with the available Node.js executable. This checks schedule continuity,
lunch placement, lab coverage and local links/anchors, not live deployment,
permissions, alert delivery or agent execution. Offline helper tests are listed
in the linked bootstrap and scaling guides.