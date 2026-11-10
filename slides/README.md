# Workshop Presentations

## Lab Presentation Index

The `lab-` prefix matches the numbered [lab worksheets](../exercises/labs/),
not the foundational library numbering. Labs 1 and 2 share one architecture
deck. Foundation decks `01` (welcome), `02` (fundamentals), `03` (L100),
and historical `04` (red/blue) retain their existing names.

| Lab | Presentation | HTML |
| --- | --- | --- |
| 1-2 | [Workshop architecture](present/lab-01-02-workshop-architecture.md) | [HTML](html/lab-01-02-workshop-architecture.html) |
| 3 | [Observability](present/lab-03-observability.md) | [HTML](html/lab-03-observability.html) |
| 4 | [Agent configuration](present/lab-04-agent-configuration.md) | [HTML](html/lab-04-agent-configuration.html) |
| 5 | [Agent validation](present/lab-05-agent-validation.md) | [HTML](html/lab-05-agent-validation.html) |
| 6 | [Autoscaling](present/lab-06-autoscaling.md) | [HTML](html/lab-06-autoscaling.html) |
| 7 | [Challenge briefing](present/lab-07-challenge-briefing.md) | [HTML](html/lab-07-challenge-briefing.html) |
| 8 | [Closeout](present/lab-08-closeout.md) | [HTML](html/lab-08-closeout.html) |

The delivery notes below retain historical schedules; use the [agenda](../AGENDA.md)
and lab worksheets for the current route.

## Current Two-Day Slots

The [two-day agenda](../AGENDA.md) schedules Fundamentals and Azure SRE Agent
L100 on Day 1, then AKS overview/roadmap 09:15-10:00 and NAP/Karpenter
10:00-10:45 on Day 2. The two additional decks have not been created or supplied
here. Existing briefing/reference decks retain historical clocks until migrated;
use the agenda and [participant labs](../exercises/two-day-workshop.md), not those
exports, for event timings. No presentations were generated for this update.

## Existing Library And Historical Delivery Notes

Five presentation assets, **113 slides in the library**: introduction reference 7, fundamentals 30, supplied L100 PowerPoint 27, red/blue briefing 11 including potential team roles, and SRE facilitator reference 38. Only fundamentals and L100 are full scheduled theory presentations; welcome fits within fundamentals and selected briefing slides fit within the instructor demo. Follow [the owning agenda](../AGENDA.md): **09:00-16:00**, walk-ins **09:00-09:30**, taught window **09:30-16:00**. Day 2 is outside scope. Every Marp slide has notes; L100 is unchanged, with no claim of complete notes or factual verification. See [build instructions](BUILD.md) for validation limits.

## Folder Guide

For live Marp delivery, open `present/`: three Marp sources plus the supplied L100 PowerPoint, with no Marp equivalent. The introduction and full red/blue briefing are reference, not extra sessions. `reference/` holds the optional SRE facilitator source.

```text
slides/
	present/        01 introduction, 02 fundamentals, 03 L100 .pptx, 04 red/blue
	html/           all four current Marp HTML exports
	reference/      05 SRE facilitator reference (Marp .md)
	microsoft.css   shared theme
```

Build instructions and validation scripts remain here. Source edits require fresh HTML rendering; no PDF or PowerPoint regeneration is part of the schedule revision.

## Delivery Order

Prefixes identify library assets, not additional teaching slots. `01` is arrival/reference; `02` and `03` are morning theory; selected `04` slides support the demo; `05` is facilitator reference.

| Time | Presentation or activity | Budget | Material |
| --- | --- | --- | --- |
| 09:00-09:30 | Walk-ins; no required teaching | 30 min | [Introduction reference](present/01-workshop-introduction.md), [HTML](html/01-workshop-introduction.html) |
| 09:30-10:15 | AI and Agents Fundamentals, welcome inline | 45 min, 30 slides | [Source](present/02-ai-agents-fundamentals.md), [HTML](html/02-ai-agents-fundamentals.html) |
| 10:15-11:00 | Azure SRE Agent L100 | 45 min, 27 slides | [Supplied unchanged PowerPoint](present/03-SRE-Agent-L100.pptx) |
| 11:00-12:00 | Lunch | 60 min | |
| 12:00-12:30 | Instructor end-to-end workflow demo | 30 min including brief rules/roles | [Demo runbook](../RED-BLUE-COMPETITION.md#instructor-demo-and-team-duties), [briefing source](present/04-red-blue-hackathon.md), [HTML](html/04-red-blue-hackathon.html) |
| 12:30-13:00 | Round 1: parallel setup | 30 min, both teams active | [Build worksheet](../exercises/single-day-workshop.md#blue-build-60-minutes) |
| 13:00-13:30 | Round 2: setup and validation | 30 min, both teams active | [Build worksheet](../exercises/single-day-workshop.md#blue-build-60-minutes) |
| 13:30-14:00 | Break/readiness/reset buffer | 30 min, no attacks | [Facilitator](../FACILITATOR-GUIDE.md) |
| 14:00-14:30 | Round 3: A attacks, B defends | 20 active + 10 reset/verify/revoke | [Runbook](../RED-BLUE-COMPETITION.md) |
| 14:30-15:00 | Round 4: B attacks, A defends | 20 active + 10 reset/verify/revoke | [Runbook](../RED-BLUE-COMPETITION.md) |
| 15:00-15:30 | Conclusions and evidence writing | 30 min; operator cleanup first 5 alongside writing | [Core worksheet](../exercises/single-day-workshop.md#conclusions-and-evidence-writing-30-minutes) |
| 15:30-16:00 | Team presentations | 30 min; finish and hand over by 16:00 | [Core worksheet](../exercises/single-day-workshop.md#team-presentations-30-minutes) |

**420 elapsed = 30 walk-ins + 90 lunch/break + 300 sessions.** Sessions: 90 theory + 30 demo + 120 rounds + 30 writing + 30 presentations. The afternoon is 240 minutes including the 30-minute break. Rounds contain 60 parallel setup + 40 active attack/defense + 20 reset, so practice is 100 wall-clock minutes. Choose assigned rehearsed VM or Kubernetes target(s); both lanes remain available, not mandatory cold deployment of both in an hour. Slow provisioning requires explicit participant pre-work, not a late finish. Budgets require rehearsal; L100's 45 minutes is planned, not measured.

## Supplied L100 PowerPoint

[03-SRE-Agent-L100.pptx](present/03-SRE-Agent-L100.pptx) is the user-supplied 27-slide deck, unchanged; it is not the older Marp export. ZIP/XML inspection identified Agentic DevOps, product overview, investigations/context, mitigation, extensibility, integrations and resources. That is not factual verification, rendered review or evidence of live connections/controls. Workshop gates remain authoritative.

Sharing review required: the unchanged file contains a presenter-guide contact, personal author metadata, and an Ecolab customer story with a named speaker. No source-folder path is needed for delivery. These items were flagged, not silently edited; obtain appropriate sharing approval before redistribution. No L100 HTML conversion or new notes were generated.

Expected SHA-256: `a6a4f2c1ab14b34958faa9bb5df5e316c9ee6c36066d0766c1d9624ee400d48b`.

## 05 - SRE Facilitator Reference

Use selected [red/blue briefing slides](present/04-red-blue-hackathon.md) within 12:00-12:05 of the instructor demo. The full 11-slide reference has 600 seconds of notes including four potential team duties; do not deliver it as an additional ten-minute session.

**FACILITATOR REFERENCE, not another lecture:** [Source](reference/05-azure-sre-agent-hackathon.md) and [HTML](html/05-azure-sre-agent-hackathon.html), 38 slides. Slides **5, 7, 9, 10, 13** support foundation safety and gates; **20-23 and 27-30** support configuration using rehearsed permissions. The full tutorial is optional. Actual deployment, query, retrieval, skill use, routing and response evidence are required; blocked ingestion/zero receivers remain unverified.

Slides **16-19 and 24-26** retain optional guided detail, not two extra 60-minute sessions. Slides **31-36** cover whole-team sequence, 240-minute afternoon, cards and rubric; **37-38** support writing/presentations and operator cleanup. Additional pairs remain isolated with no simultaneous reciprocal attacks. Follow [the runbook](../RED-BLUE-COMPETITION.md) for enforcement, recovery and revocation gates.

The [25-minute prompt exercise](../exercises/single-day-workshop.md#evidence-prompt-exercise-25-minutes), [35/40/45-minute exercises](../exercises/ai-agents-fundamentals.md), legacy guided labs and [full configuration tutorial](../AGENT-CONFIGURATION.md) are optional unscheduled references. The old simultaneous 60-minute competition is retired from the core model. Day 2 is unspecified. Keep [facilitator answers](../exercises/FACILITATOR-NOTES.md) out of participant assistant context.

## Preview And Exports

### Current HTML Preview

Open the [red/blue HTML](html/04-red-blue-hackathon.html) for briefing reference after regeneration. Its source includes whole-team role flow, four potential duties and 600 seconds of reference notes; selected slides fit inside the noon demo, not an extra lecture.

Fundamentals keeps tools/grounding and orchestration/safety within 2,700 seconds, welcome included. Former standalone decks remain retired. Regenerate all four affected Marp HTML files and check layout before delivery; see [the build record](BUILD.md) for actual results and limits. Historical geometry checks do not validate this revision. The Microsoft stylesheet and supplied L100 remain unchanged. Standard Marp PPTX uses slide images, not fully editable objects.

In PowerShell from this folder:

```powershell
$env:HOST="0.0.0.0"
marp --server . --port 8080
```

Preview [fundamentals](http://localhost:8080/present/02-ai-agents-fundamentals.md), [red/blue](http://localhost:8080/present/04-red-blue-hackathon.md), [introduction](http://localhost:8080/present/01-workshop-introduction.md), or [facilitator reference](http://localhost:8080/reference/05-azure-sre-agent-hackathon.md). If 8080 is occupied, do not stop an unrelated process or change ports without agreement; use regenerated standalone HTML instead. A running server does not prove it has the latest sources; verify the new schedule before delivery.
