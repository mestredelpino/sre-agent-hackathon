# Two-Day Workshop Agenda

Audience: operations engineers with basic Azure knowledge and introductory
Kubernetes experience. Teams inspect a pre-provisioned platform and application,
then verify observability, configure and validate SRE Agent, and continue with
autoscaling, controlled failure and recovery.

Both days run 09:00-16:00. Lunch is 11:00-12:00 on both days, with no break
immediately before lunch. Day 1 has 315 session minutes, 30 arrival minutes,
15 break minutes and 60 lunch minutes. Day 2 has 345 session minutes,
15 break minutes and 60 lunch minutes. These are delivery budgets, not measured
provisioning guarantees.

## Day 1: Inspect, Observe, Configure And Validate

| Time | Session | Outcome |
| --- | --- | --- |
| 09:00-09:30 | Arrival and access checks | Optional tooling/access checks; required scope briefing follows at 12:00 |
| 09:30-10:15 | AI and Agents Fundamentals | Existing presentation; welcome, context, tools, grounding, orchestration and safety |
| 10:15-11:00 | Azure SRE Agent L100 | Existing supplied presentation; introduction to the product and its boundaries |
| 11:00-12:00 | Lunch | Protected lunch; no required participant work |
| 12:00-12:45 | Labs 1-2: combined platform, application and observability architecture | Inspect pre-provisioned resources, diagrams, scope, costs, identities, approval gates and STOP |
| 12:45-13:00 | Labs 1-2: access and permissions confirmation | Confirm approved portal, cluster, Store, Grafana and SRE Agent access; record blockers |
| 13:00-13:15 | Break | No required participant work |
| 13:15-14:00 | Lab 3: dashboards and alert rules | Fresh metrics/logs, published Grafana dashboard and tested Azure Monitor notification path |
| 14:00-15:00 | Lab 4: configure SRE Agent | Full repo setup: five agents, twelve skills, bootstrap, scoped connections/tools, both Review plans and first read |
| 15:00-16:00 | Lab 5: validate SRE Agent and Day 1 checkpoint | Runtime, denial, delegation and alert-intake evidence; checkpoint and overnight handover 15:50-16:00 |

## Day 2: Validate, Scale And Recover

| Time | Session | Outcome |
| --- | --- | --- |
| 09:00-09:15 | Reconnect and verify the baseline | Application health, fresh telemetry and overnight change review |
| 09:15-10:00 | AKS overview and roadmap | Additional presentation slot; distinguish available features from roadmap items |
| 10:00-10:45 | NAP and Karpenter | Additional presentation slot; provisioning, NodePools, constraints, disruption and costs |
| 10:45-11:00 | Guided scaling walkthrough and experiment planning | Predict pod versus node scaling and define bounded tests and stop conditions |
| 11:00-12:00 | Lunch | Protected lunch; no required participant work |
| 12:00-12:45 | Optional SRE Agent refinement | Revisit Day 1 evidence and failed gates; refine prompts/configuration, not the first validation session |
| 12:45-13:45 | Lab 6: KEDA and NAP autoscaling | Configure scaling resources, observe pod/node scale-out separately, then verify scale-in |
| 13:45-14:00 | Break | No required participant work |
| 14:00-14:20 | Lab 7: improve and prepare the challenge | Equivalent healthy targets, common intake, agent-output capture and approved recovery |
| 14:20-15:00 | Lab 7: facilitator fault and agent challenge | Apply the same scenario per team 14:20-14:25; agents investigate 14:25-14:50; reset 14:50-15:00 |
| 15:00-15:20 | Lab 8: evidence review and approved cleanup | Freeze original agent outputs and participant notes, reconcile observations and start authorized disposal |
| 15:20-15:50 | Team presentations | Share build results, investigation evidence, scaling observations and lessons |
| 15:50-16:00 | Final closeout | Confirm disposal or approved remaining-resource owner, budget and deadline |

## Labs And Materials

Follow the [participant lab sequence](exercises/two-day-workshop.md) and
[technical setup runbook](WORKSHOP-SETUP.md). The main route uses AKS and the AKS
Store app. Check the [readiness checklist](exercises/READINESS.md) for completed
setup coverage, outstanding live verification and features outside the baseline.
The VM lane remains an optional alternative,
not an additional requirement. Existing presentation assets are indexed in
[slides](slides/README.md). The two additional presentation slots above are
planned material, not decks created by this agenda.

SRE Agent has 120 minutes of dedicated configuration/validation on Day 1,
including the final ten-minute checkpoint, plus 45 minutes of optional refinement
on Day 2 and its use in scaling analysis and the challenge. The facilitator
pre-provisions the platform, application and agent resource; a prepared shell is
not a participant-created or runtime-validated investigator.

## Delivery Gates

- The provisioning owner prepares quota, policy/provider approval, tooling,
  regional availability and separate deployment/investigation/broker identities
  before the event. Rehearse and hand over the pre-provisioned environment using
  the [pre-provisioned route](exercises/pre-provisioned-workshop.md). Attendees
  inspect rather than deploy in Labs 1-2; do not consume lunch or extend 16:00.
- Enable NAP-compatible Cilium Overlay networking and managed KEDA in the initial
  reviewed cluster plan. Configure NodePool/scaler resources and test them on
  Day 2; no surprise networking rebuild belongs in the scaling lab.
- Require a working app before interpreting telemetry, fresh telemetry before
  agent analysis, and scale-test reset before challenge admission. Record each
  checkpoint PASS/FAIL/BLOCKED with UTC, source and owner; never invent success.
- Keep investigation agents read-only. Review applies to supported plans/tasks,
  not every tool. Independently enforce identity/tool boundaries and use a
  separately approved operator for deployment and recovery.
- The challenge is only on Day 2. The facilitator applies the same approved
  fault scenario to each team's isolated target; teams do not attack each other.
  Use equal observation windows and record intake mode and participant assistance.
  Keep one active fault per target and reveal fault details only after original
  agent outputs freeze at 15:00. Exclude unready targets rather than improvising.
- Stop synthetic load overnight, preserve protected state/configuration and
  record ownership and cost approval. Verify fresh health on Day 2. Cleanup must
  cover each resource's original deployment state and any separately created
  agent, alert or access configuration.

This agenda supersedes the earlier single-day/five-round timetable. Until older
reference documents and slide exports are migrated, their clocks are not event
instructions; use this agenda and the two-day labs. Safety, scope, STOP and
read-only controls in the detailed procedures still apply. The challenge lab
defines the new timing and one-fault limit, not the historical round allowances.
