# Two-Day Workshop Agenda

Audience: operations engineers with basic Azure knowledge and introductory
Kubernetes experience. Teams inspect a pre-provisioned platform and application,
then verify observability, configure and validate SRE Agent, and continue with
autoscaling, controlled failure and recovery.

Day 1 runs 09:00-16:00; Day 2 runs 09:00-15:00. Lunch is 11:00-12:00 on both days, with no break
immediately before lunch. Day 1 has 315 session minutes, 30 arrival minutes,
15 break minutes and 60 lunch minutes. Day 2 has 300 session minutes,
no scheduled break and 60 lunch minutes. These are delivery budgets, not measured
provisioning guarantees.

## Day 1: Inspect, Observe, Configure And Validate

| Time | Session | Outcome |
| --- | --- | --- |
| 09:00-09:30 | Arrival and access checks | Optional tooling/access checks; required scope briefing follows at 12:00 |
| 09:30-10:15 | AI and Agents Fundamentals | Existing presentation; welcome, context, tools, grounding, orchestration and safety |
| 10:15-11:00 | Azure SRE Agent L100 | Existing supplied presentation; introduction to the product and its boundaries |
| 11:00-12:00 | Lunch | Protected lunch; no required participant work |
| 12:00-12:15 | Architecture, scope, costs and access briefing | Confirm supplied resources, identities, approval gates, recovery ownership and STOP |
| 12:15-13:00 | Labs 1-2: platform and application validation | Validate the already-deployed platform and Store, approved access, workload readiness and public HTTPS; record evidence and blockers, not new deployments |
| 13:00-13:15 | Break | No required participant work |
| 13:15-14:00 | Lab 3: observability validation | Inspect fresh metrics/logs, supplied Grafana panels and notification evidence before agent creation |
| 14:00-15:00 | Lab 4: create and configure SRE Agent | Participants create the resource, configure scoped connections, three starter skills and three custom agents, and record proposed Review plan settings |
| 15:00-16:00 | Lab 5: validate SRE Agent and Day 1 checkpoint | Executed reads, retrieval, denial and delegation evidence; native intake BLOCKED under read-only boundary; checkpoint and overnight handover 15:50-16:00 |

## Day 2: Validate, Scale And Recover

| Time | Session | Outcome |
| --- | --- | --- |
| 09:00-09:15 | Reconnect and verify the baseline | Application health, fresh telemetry and overnight change review |
| 09:15-10:00 | AKS overview and roadmap | Additional presentation slot; distinguish available features from roadmap items |
| 10:00-10:45 | NAP and Karpenter | Additional presentation slot; provisioning, NodePools, constraints, disruption and costs |
| 10:45-11:00 | Guided scaling walkthrough and experiment planning | Predict pod versus node scaling and define bounded tests and stop conditions |
| 11:00-12:00 | Lunch | Protected lunch; no required participant work |
| 12:00-12:45 | Lab 6: KEDA and NAP autoscaling | Configure scaling resources, observe pod/node scale-out separately, then verify scale-in |
| 12:45-14:20 | Lab 7: prepare, investigate and recover | Prepare equivalent healthy targets and capture 12:45-13:05; facilitator applies the same scenario per team 13:05-13:10; agents investigate 13:10-14:10; freeze outputs at 14:10; approved reset 14:10-14:20 |
| 14:20-14:50 | Team presentations | Share original investigation evidence, scaling observations and lessons without rewriting agent outputs |
| 14:50-15:00 | Final closeout | Confirm recovery, disposal or approved remaining-resource owner, budget and deadline; finish at 15:00 |

## Labs And Materials

Follow the [pre-provisioned participant route](exercises/pre-provisioned-workshop.md)
and [lab sequence](README.md#participant-labs). The main route uses AKS and the AKS
Store app. Check the [readiness checklist](exercises/READINESS.md) for completed
setup coverage, outstanding live verification and features outside the baseline.
The VM lane remains an optional alternative,
not an additional requirement. Existing presentation assets are indexed in
[slides](slides/README.md). The two additional presentation slots above are
planned material, not decks created by this agenda.

SRE Agent has 120 minutes of dedicated configuration/validation on Day 1,
including the final ten-minute checkpoint, followed by its use in scaling analysis
and the challenge on Day 2. There is no optional refinement session or scheduled
Lab 8; final closeout retains recovery, resource ownership and cost responsibilities. The facilitator
pre-provisions the platform, application and observability, but not the SRE Agent.
Participants create it in Lab 4 and must perform Lab 5 on Day 1; a prepared shell
is not a participant-created or runtime-validated investigator.

## Delivery Gates

- The provisioning owner prepares quota, policy/provider approval, tooling,
  regional availability and separate deployment/investigation/broker identities
  before the event. Rehearse and hand over the pre-provisioned environment using
  the [pre-provisioned route](exercises/pre-provisioned-workshop.md). Attendees
  inspect rather than deploy in Labs 1-2; do not consume lunch or extend the
  Day 1 16:00 or Day 2 15:00 finish.
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
  agent outputs freeze at 14:10. Exclude unready targets rather than improvising.
- Stop synthetic load overnight, preserve protected state/configuration and
  record ownership and cost approval. Verify fresh health on Day 2. Cleanup must
  cover each resource's original deployment state and any separately created
  agent, alert or access configuration.

This agenda supersedes the earlier single-day/five-round timetable. Until older
reference documents and slide exports are migrated, their clocks are not event
instructions; use this agenda and the two-day labs. Safety, scope, STOP and
read-only controls in the detailed procedures still apply. The challenge lab
defines the new timing and one-fault limit, not the historical round allowances.
