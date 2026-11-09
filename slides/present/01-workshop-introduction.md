---
marp: true
theme: default
style: |
  :root {
    --c-ink: #201f1e;
    --c-muted: #605e5c;
    --c-blue: #0078d4;
    --c-line: #d9e2e8;
    --c-good: #107c10;
    --c-warning: #9a6700;
    --c-danger: #a4262c;
    --c-background: #faf9f8;
  }
  section {
    width: 1280px;
    height: 720px;
    padding: 90px 64px 66px;
    justify-content: flex-start;
    background: radial-gradient(circle at 100% 100%, #eaf3fb 0, #eaf3fb 150px, transparent 151px), var(--c-background);
    color: var(--c-ink);
    font-family: 'Segoe UI', 'Segoe UI Variable', sans-serif;
    font-size: 25px;
    line-height: 1.34;
    letter-spacing: 0;
  }
  section::before {
    content: '';
    position: absolute;
    top: 28px;
    left: 64px;
    width: 13px;
    height: 13px;
    background: #f25022;
    box-shadow: 16px 0 #7fba00, 0 16px #00a4ef, 16px 16px #ffb900;
  }
  header { position: absolute; top: 30px; left: 110px; right: 64px; font-size: 17px; color: var(--c-muted); }
  footer { left: 64px; bottom: 23px; font-size: 14px; color: var(--c-muted); }
  section::after { right: 42px; bottom: 22px; font-size: 15px; color: var(--c-muted); }
  h1 { margin: 0 0 23px; border: 0; color: var(--c-blue); font-size: 41px; font-weight: 600; line-height: 1.15; }
  h2 { margin: 12px 0 18px; font-size: 29px; font-weight: 400; color: var(--c-muted); }
  p { margin: 0 0 17px; }
  strong, a { color: var(--c-blue); }
  strong { font-weight: 600; }
  a { text-decoration: none; }
  ul, ol { padding-left: 28px; margin: 0 0 20px; }
  li { margin-bottom: 12px; }
  li::marker { color: var(--c-blue); }
  code { font-family: 'Cascadia Code', Consolas, monospace; font-size: 0.86em; background: #eef4f8; color: #005a9e; }
  section.title { justify-content: center; }
  section.title h1 { font-size: 62px; max-width: 1000px; margin-bottom: 20px; }
  .eyebrow { color: var(--c-good); font-size: 19px; font-weight: 600; margin-bottom: 16px; }
  .subtitle { font-size: 32px; color: var(--c-muted); max-width: 980px; }
  .meta { font-size: 21px; color: var(--c-muted); margin-top: 28px; }
  .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 27px; margin: 10px 0 22px; }
  .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .capability { border-top: 4px solid var(--c-blue); padding-top: 16px; font-size: 24px; }
  .capability b { display: block; font-size: 26px; margin-bottom: 12px; }
  .capability p { margin-bottom: 12px; }
  .focus, .caution, .risk { padding: 16px 22px; border-left: 4px solid var(--c-blue); background: #edf6fc; font-size: 23px; margin: 18px 0 0; }
  .caution { border-color: var(--c-warning); background: #fff8e5; }
  .risk { border-color: var(--c-danger); background: #fde7e9; }
  .flow { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 17px; margin: 22px 0; }
  .step { border: 1px solid var(--c-line); border-top: 4px solid var(--c-blue); border-radius: 4px; background: #fff; padding: 18px; font-size: 24px; min-height: 122px; }
  .step b { display: block; font-size: 19px; color: var(--c-blue); margin-bottom: 12px; }
  .step small { display: block; font-size: 20px; color: var(--c-muted); margin-top: 10px; }
  .prompt { border-left: 4px solid var(--c-blue); background: #f0f6fa; padding: 22px 26px; font-size: 25px; line-height: 1.48; margin: 8px 0 22px; }
  .small { font-size: 20px; color: var(--c-muted); }
  .label { font-size: 18px; color: var(--c-good); font-weight: 600; margin-bottom: 10px; }
  .agenda { display: grid; grid-template-columns: 165px 1fr 165px 1fr; gap: 13px 22px; margin-top: 12px; font-size: 23px; }
  .agenda b, .checklist b { color: var(--c-good); }
  .checklist { display: grid; grid-template-columns: 145px 1fr; gap: 17px 24px; margin: 15px 0 22px; font-size: 24px; }
  .path { display: flex; gap: 13px; align-items: center; margin: 22px 0; }
  .path .step { flex: 1; min-width: 0; min-height: 100px; }
  .arrow { color: var(--c-blue); font-size: 26px; }
  table { width: 100%; border-collapse: collapse; background: transparent; font-size: 23px; margin: 8px 0 18px; }
  th { color: #005a9e; background: #eaf3fb; font-weight: 600; }
  th, td { padding: 11px 15px; border: 0; border-bottom: 1px solid var(--c-line); text-align: left; }
  tr:nth-child(2n) { background: #f3f5f6; }
  section.compact table { font-size: 21px; }
  section.compact th, section.compact td { padding: 9px 13px; }
  .sources { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 28px; font-size: 18px; margin-top: 22px; }
  @media print { section { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
size: 16:9
paginate: true
title: Azure SRE Agent Two-Day Workshop | Welcome
description: Two-day workshop agenda and a brief introduction to SRE, AI agents and AKS scaling.
header: 'Azure SRE Agent Workshop | Two-Day Welcome'
footer: 'Evidence first | Scoped access | Anyone may STOP'
---

<!-- _class: title -->

TWO-DAY WORKSHOP | 09:00-16:00 EACH DAY

# Azure SRE Agent Workshop

- **Day 1:** build the platform and app, observe, configure your agent.
- **Day 2:** validate the agent, test scaling, investigate and recover.
- **Our challenge:** the same fault for every team; compare the agents' work.

<!--
TIME: 30 seconds when introducing fundamentals.
Use this deck as arrival/reference material and integrate welcome into Day 1 fundamentals, 09:30-10:15. It is not an extra scheduled lecture. Arrival checks are optional, not required teaching. Both days finish at 16:00. Ask teams to distinguish a verified result from a plausible explanation; success is evidence and safe recovery, not ranking or scoring.
-->

---

# A few ideas for the next two days

- **SRE:** apply engineering to reliability, using service signals to guide
  investigation, recovery and improvement.
- **AI agents:** use context and tools to investigate; check their evidence,
  uncertainty and recommendations.
- **AKS:** run our application on Kubernetes, with metrics and logs to observe it.
- **KEDA and NAP:** scale workload replicas and provision nodes when demand needs
  more capacity. They solve different problems.

<!--
TIME: 60 seconds; introductory vocabulary, not a technical lesson.
SRE is broader than incident response: mention service-level objectives and learning from incidents without teaching them here. Azure SRE Agent supports investigation; it does not replace ownership or prove a diagnosis by sounding confident. KEDA responds to workload signals; managed AKS NAP uses Karpenter APIs to provision suitable nodes. The scheduled fundamentals, L100, AKS and NAP sessions provide the detail. Move promptly into the agenda.
-->

---

<!-- _class: compact -->

# Day 1 | Morning foundations

| Time | Session |
| --- | --- |
| 09:00-09:30 | Arrival and access checks |
| 09:30-10:15 | AI and Agents Fundamentals |
| 10:15-11:00 | Azure SRE Agent L100 |
| 11:00-12:00 | Lunch |

**Lunch is 11:00-12:00 on both days.** Welcome is included in fundamentals.

<!--
TIME: 30 seconds; schedule reference.
Arrival is 09:00-09:30 for optional access checks. Fundamentals includes welcome, context, tools, grounding, orchestration and safety; the existing supplied L100 follows. Neither session creates a new deployment obligation before the required 12:00 briefing. Protect lunch from 11:00 to noon and do not insert a break before it. Ask participants to raise access blockers early rather than silently bypassing controls.
-->

---

<!-- _class: compact -->

# Day 1 | Build, observe and configure

| Time | Session |
| --- | --- |
| 12:00-12:15 | Architecture, scope, costs and deployment briefing |
| 12:15-13:15 | Lab 1: deploy the platform |
| 13:15-13:45 | Lab 2: deploy and test the application |
| 13:45-14:00 | Break |
| 14:00-14:45 | Lab 3: dashboards and alert rules |
| 14:45-15:45 | Lab 4: configure SRE Agent |
| 15:45-16:00 | Day 1 checkpoint and overnight handover |

<!--
TIME: 45 seconds; refer back during the day.
At noon confirm exact targets, identities, cost approval, recovery ownership and STOP. Lab 1 creates the platform and agent in parallel. Lab 2 proves public access, workload readiness and synthetic orders before telemetry interpretation. Lab 3 checks fresh metrics/logs, the Grafana dashboard and an actual alert notification path. Lab 4 configures scoped connections, tools, skills/custom agents and explicit Review plans, then performs a first real read. Before leaving, stop synthetic load, preserve protected state/configuration and record overnight owner, budget and blockers.
-->

---

<!-- _class: compact -->

# Day 2 | Reconnect and plan scaling

| Time | Session |
| --- | --- |
| 09:00-09:15 | Reconnect and verify the baseline |
| 09:15-10:00 | AKS overview and roadmap |
| 10:00-10:45 | NAP and Karpenter |
| 10:45-11:00 | Guided scaling walkthrough and experiment planning |
| 11:00-12:00 | Lunch |

**From concepts to experiments:** workload scaling and node provisioning.

<!--
TIME: 30 seconds; schedule reference.
Reconnect by checking application health, fresh telemetry and overnight changes. The two additional presentation slots cover AKS roadmap and NAP/Karpenter; do not imply this welcome update supplies those decks. Distinguish available features from roadmap items. In the walkthrough ask teams to predict pod versus node scaling and define cost limits and stop conditions before experiments. Lunch is protected from 11:00 to noon, with no preceding break.
-->

---

<!-- _class: compact -->

# Day 2 | Validate, scale and prepare

| Time | Session |
| --- | --- |
| 12:00-12:45 | Lab 5: validate and refine SRE Agent |
| 12:45-13:45 | Lab 6: KEDA and NAP autoscaling |
| 13:45-14:00 | Break |
| 14:00-14:20 | Lab 7: improve and prepare the challenge |

**Facilitator-injected faults only.** Teams prepare their agents, not attacks.

<!--
TIME: 45 seconds; refer back before labs.
Lab 5 verifies actual skill use, scoped reads, denial proof, specialist return and alert-to-investigation flow for the five-agent, twelve-skill bundle configured through bootstrap on Day 1. Preserve actual traces. Lab 6 observes workload and node scaling separately and resets the experiment. Prepare equivalent healthy targets, common intake, original-output capture and authorized recovery. Teams receive no fault-injection access.
-->

---

<!-- _class: compact -->

# Day 2 | Challenge and closeout

| Time | Session |
| --- | --- |
| 14:20-15:00 | Lab 7: facilitator fault and agent challenge |
| 15:00-15:20 | Lab 8: evidence review and approved cleanup |
| 15:20-15:50 | Team presentations |
| 15:50-16:00 | Final closeout |

**Same fault scenario for every team.** Compare what each agent actually produces.

<!--
TIME: 45 seconds; reference at challenge admission.
During 14:20-14:25 the facilitator applies the same approved scenario to each team's isolated healthy target. Record injection times and allow equal observation windows if staggered. Agents investigate until 14:50; retain original queries, evidence, diagnosis, recommendations and reports or diagrams, with human prompts and hints recorded separately. Use 14:50-15:00 for approved recovery and verified reset. Freeze outputs at 15:00 and reveal the fault record without rewriting answers. No team attacks another. Additional scenarios require the same rehearsed sequence and reset for all teams, one active fault per target. Close with disposal or approved owner, budget and deadline.
-->

---

# Keep the agenda and labs close

- Open the [two-day participant labs](../../exercises/two-day-workshop.md).
- Use the [authoritative agenda](../../AGENDA.md) for all clocks and delivery gates.
- Raise access blockers with the facilitator before the labs.

**Next: AI and Agents Fundamentals.**

<!--
TIME: 30 seconds; transition into fundamentals, not another session.
Point participants to the agenda and progressive lab sequence, then continue with fundamentals. The noon briefing and lab instructions own the detailed permissions, safety, deployment and cleanup procedures. This short welcome adds no extra scheduled session and grants no cloud permissions.
-->