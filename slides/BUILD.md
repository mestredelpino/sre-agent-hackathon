# Build and Rehearse

## Canonical Workshop Decks

There is one Day 1 architecture deck and one Day 2 challenge briefing:

- [Labs 1-2 Workshop Architecture source](present/lab-01-02-workshop-architecture.md) · [HTML](html/lab-01-02-workshop-architecture.html): **13 slides and 13 substantive note blocks, 1200 seconds (20 minutes)**. Use it within Day 1's combined 12:00-12:45 handover and architecture block; allow 25 minutes for handover and guided walkthrough, then confirm access at 12:45-13:00.
- [Lab 7 Challenge Briefing source](present/lab-07-challenge-briefing.md) · [HTML](html/lab-07-challenge-briefing.html): **2 slides and 2 substantive note blocks, 210 seconds (3 minutes 30 seconds)**. Use it for Day 2 challenge preparation, not as another architecture lecture.

Architecture includes platform topology, resource-group inventory, execution
identities, seven baseline alert rules, ingress, certificate/AGIC control,
application dependencies, telemetry and scaling boundaries. It follows the supplied
baseline and pinned revisions; local scenario Terraform is not assumed to be the
deployed infrastructure. Resource declarations do not prove live health or intake.

The incident introduction explains how symptoms, evidence and competing
hypotheses guide investigation, and why recovery is separate from diagnosis.
Safety and timing context remain in speaker notes; operational instructions
and human responsibilities belong in the lab and facilitator guides.

The architecture uses **five external SVG diagram images**, not inline SVG:
`05-platform.svg`, `05-ingress.svg`, `06-control.svg`, `05-application.svg` and
`05-observability.svg` under `../diagrams/`. Four images are 1152x338; the control
diagram is 1152x300 with `class="diagram compact"`. Export with `--html` and retain
the files at the referenced relative paths; the diagrams are not embedded copies.
Linked reference documents must also remain accessible.

From this folder in Windows PowerShell, using the existing Marp/Node installation:

```powershell
node .\verify-workshop-architecture.mjs --source-only
node .\verify-architecture-and-challenge.mjs --source-only
marp --html .\present\lab-01-02-workshop-architecture.md --output .\html\lab-01-02-workshop-architecture.html
marp --html .\present\lab-07-challenge-briefing.md --output .\html\lab-07-challenge-briefing.html
node .\verify-architecture-and-challenge.mjs
node .\verify-architecture-and-challenge.mjs --browser
node .\verify-workshop-architecture.mjs
node .\verify-workshop-architecture.mjs --browser
node .\verify-architecture-and-challenge.mjs --all --source-only
marp --html .\present\01-workshop-introduction.md --output .\html\01-workshop-introduction.html
marp --html .\present\02-ai-agents-fundamentals.md --output .\html\02-ai-agents-fundamentals.html
node .\verify-architecture-and-challenge.mjs --all --browser
node .\verify-fundamentals.mjs
```

Both verifier commands run the same shared checks for **both canonical decks**;
the workshop-architecture entry point is a thin compatibility wrapper. Checks
cover source/export counts, per-slide substantive notes, exact timings, one
heading per slide, platform/alert and challenge role/rule contracts, baseline
revision anchors, accessible external images and export parity, index entries,
and local links with query strings/fragments. HTTP(S) links are parsed as remote
URLs, not treated as filesystem paths; anchor-only links are skipped. These
checks do not fetch remote documents or prove fragment targets exist.
`--source-only` needs no HTML exports. `--all` additionally checks introduction
**8 slides/315 seconds**, fundamentals **21/2700** and red/blue **11/600**;
regenerate their exports before using `--all --browser`.

Browser mode uses Puppeteer from the installed Marp CLI
and headless Microsoft Edge; set `MARP_CLI_ROOT` and `BROWSER_PATH` to override
those locations. It opens both local HTML exports, checks every slide at 1280x720
and 390x844 (**30 slide/viewport checks** for the canonical pair), tests text/footer
clearance, table/code clipping and external image loading, saves screenshots and
reports runtime errors, failed asset requests and HTTP error responses.
Mobile is a letterboxed 16:9 presentation, not a reflowed document. Inspect the
screenshots as well as running the geometry checks.

On 2026-11-09 welcome, fundamentals and architecture exports were regenerated
with installed Windows Marp `--html`; `export_marp` was unavailable. Windows
Node `--all --source-only` and `--all --browser` checks passed across all five
decks, including the unchanged red/blue and challenge briefing exports. Headless
Edge passed **110 slide/viewport bounds checks across 55 slides**, with no runtime
errors or failed asset requests. The focused fundamentals checker passed, including
CSS parity, updated closing clock and the unchanged supplied L100 hash. See the
[schedule audit](BOUNDS-VALIDATION.md#schedule-synchronization--2026-11-09).
No server, PDF/PPTX generation, cloud validation, live queries or writes were used.

The approved afternoon clock is handover/architecture **12:00-12:45**, access
**12:45-13:00**, break **13:00-13:15**, Lab 3 **13:15-14:00**, Lab 4
**14:00-15:00**, and first Lab 5 validation **15:00-16:00**. Its final
**15:50-16:00** includes the checkpoint and overnight handover. Day 2
**12:00-12:45** is optional refinement and validation follow-up, not first
validation; no faults. Lab 6 scaling remains **12:45-13:45**. The shared validator
checks literal agenda session labels/times as well as the welcome schedule rows.
Source checks cannot establish runtime health, permissions, telemetry freshness,
order processing or incident intake. Historical inventory validators below do
not define this deck's content or count.

## Observability Intro

[Lab 3 Observability source](present/lab-03-observability.md) and
[HTML](html/lab-03-observability.html) contain **exactly 2 slides, 2 substantive
speaker-note blocks and 210 seconds (3 minutes 30 seconds)**. Deliver the intro
inside Day 1 Lab 3's **13:15-14:00** slot, not as an extra session. The
[agenda](../AGENDA.md) owns the clock and the
[current Lab 3](../exercises/labs/03-observability.md) owns the agent-led activity.
Participants use the supplied main agent and one existing Grafana panel; they
do not write LAW queries, deploy resources or configure the custom workflow here.
Lab 4 configures it; Lab 5 supplies runtime proof.

Slide 2 uses the dedicated **1152x408**
[presentation architecture SVG](../diagrams/07-sre-agent-architecture.svg),
generated from its [editable source](../diagrams/07-sre-agent-architecture.drawio)
through the existing draw.io pipeline. The unchanged
[full architecture](../diagrams/sre-agent-architecture.svg) is **1800x1580**;
its 18-22px labels would shrink to about 5-6px in this slide's diagram area.
The focused view keeps labels at 20-22px at presentation size and links to the
full diagram and guide. It preserves the main/custom split, triage return routes,
skills versus knowledge, tool connections and independent permission bounds.
Optional triggers and individual identity details remain in the full reference
and speaker notes. The SVG has an accessible title/description, image alt text
and a visible caption. Keep `diagrams/` and linked references beside `slides/`
when sharing the HTML; the deck is not a single-file embedded bundle.

From this folder in Windows PowerShell:

```powershell
node .\verify-observability.mjs --source-only
marp --html .\present\lab-03-observability.md --output .\html\lab-03-observability.html
node .\verify-observability.mjs
node .\verify-observability.mjs --browser
```

Only if the diagram baseline changes, run from the repository root:

```powershell
node diagrams/verify.mjs --source-only
node diagrams/generate.mjs --view=07-sre-agent-architecture
node diagrams/verify.mjs --browser
```

The focused verifier follows the existing document-contract patterns without
calling the historical presentation-inventory assertion. It checks exact source
and export counts, substantive notes, 90+120-second timings, exact exported note
and image parity, headings, accessible caption/alt text, local asset/link
existence, the current agenda label/time and index entries. It also checks the
full editable architecture and the derived view's route parity and label size.
Browser mode uses the same Marp Puppeteer/Edge defaults and overrides described
above; it checks both slides at 1280x720 and 390x844, image loading, text/footer
bounds and SVG label clipping/overlap, and saves screenshots for visual review.

On 2026-11-09 the export tool succeeded, then installed Windows Marp was run
explicitly with `--html`. Source/export checks and **all 4 desktop/mobile
slide checks passed**; SVG labels were at least 20px with no label clipping or
overlap, and Edge reported no page errors or failed image requests. Desktop
and letterboxed mobile screenshots were inspected. The integrated browser
opened the HTML but reported its existing VS Code preload error and a denied
wake-lock request; clean rendering validation used headless Edge. The final
screenshots are in Windows Temp `sre-observability-GM01jg`. Shared diagram
validation also passed all **13 editable source/SVG pairs**, icon hashes,
embedded-source parity and rendered text/icon checks. No server, PDF/PPTX
export, live telemetry queries, faults or Azure writes were performed.

Existing checks have separate limitations: `verify-architecture-and-challenge.mjs`
without flags fails its old literal Lab 3 label (`explore metrics, logs and alerts`
versus the current `explore with SRE Agent`). Its `--source-only` invocation
exits early in the imported diagram verifier, so that success does not establish
the old deck contracts passed. Neither behavior was changed for this intro.
A whole-index link scan also finds pre-existing historical links to the missing
single-day worksheet. The new/current index entries and new deck links resolve;
historical link cleanup and existing deck migrations are outside this change.

## Remaining Lab Intros

Each new intro contains **exactly 2 slides, 2 substantive speaker-note blocks
and 180 seconds (90+90)**. Deliver the three minutes inside the existing lab
slot, not as another session. The [agenda](../AGENDA.md) owns the clock and the
linked lab owns the activity:

- Lab 4, Day 1 **14:00-15:00**: [Source](present/lab-04-agent-configuration.md) and [HTML](html/lab-04-agent-configuration.html). Introduces skills, agents, connections and the independent permission boundaries around them.
- Lab 5, Day 1 **15:00-16:00**: [Source](present/lab-05-agent-validation.md) and [HTML](html/lab-05-agent-validation.html). Explains configured intent versus demonstrated behavior, and the evidence behind trust. The lab retains the **15:50-16:00** checkpoint and overnight handover.
- Lab 6, Day 2 **12:45-13:45**: [Source](present/lab-06-autoscaling.md) and [HTML](html/lab-06-autoscaling.html). Explains KEDA workload replicas, NAP node capacity and how the two scaling loops interact.
- Lab 8, Day 2: [Source](present/lab-08-closeout.md) and [HTML](html/lab-08-closeout.html). Introduces incident learning, evidence and ownership at **15:00**, within the **15:00-15:20** review block; presentations and final closeout follow as scheduled in the agenda.

These are text-only introductions using the Lab 3 visual language. Existing
architecture references remain linked; no new diagram or remote image is needed.
Keep the repository layout when sharing exports so their lab/source links resolve.

From this folder in Windows PowerShell:

```powershell
node .\verify-lab-intros.mjs --source-only
marp --html .\present\lab-04-agent-configuration.md --output .\html\lab-04-agent-configuration.html
marp --html .\present\lab-05-agent-validation.md --output .\html\lab-05-agent-validation.html
marp --html .\present\lab-06-autoscaling.md --output .\html\lab-06-autoscaling.html
marp --html .\present\lab-08-closeout.md --output .\html\lab-08-closeout.html
node .\verify-lab-intros.mjs
node .\verify-lab-intros.mjs --browser
node .\verify-architecture-and-challenge.mjs --source-only
node .\verify-architecture-and-challenge.mjs --browser
node .\verify-observability.mjs --browser
node ..\exercises\verify-two-day.mjs
```

[The focused verifier](verify-lab-intros.mjs) checks all four decks together:
source/export counts, one heading and substantive note per slide, exact note and
90+90-second timing parity, current agenda/lab slots, required content, local
links and Markdown heading anchors, and image alternatives/export parity if
images are added. It does not assert the historical presentation inventory or
require new index entries. Source mode needs only Node and no HTML exports;
do not combine `--source-only` and `--browser`.

Browser mode reuses the [existing renderer helper](../diagrams/render.mjs),
installed Marp Puppeteer and headless Edge. The existing `MARP_CLI_ROOT`,
`BROWSER_PATH` and `DRAWIO_WEBAPP` overrides apply; the helper also needs the
installed draw.io mxGraph bundle. It opens local HTML without a server and checks
every slide at **1280x720** and **390x844**, rendered headings, text/footer
clearance, overlap, element clipping and image loading, plus runtime/request
errors. Negative controls reject a third slide, timing drift, missing links and
deliberate browser overflow. Screenshots hide only Marp's transient navigation
overlay; exported controls are unchanged. Mobile remains letterboxed 16:9.

On 2026-11-09 the four exports were generated with the Marp tool; updated copies
used installed Windows Marp with `--html`. Source/export checks and **all 16
desktop/mobile bounds checks passed**, including the negative controls, with no
runtime or asset errors. All eight desktop and eight mobile screenshots were
visually inspected. Final clean captures are in Windows Temp
`sre-lab-intros-zMTB96`. Canonical architecture/challenge regression passed
**30** browser checks; observability passed **4** plus diagram label checks;
the two-day route passed its schedules, eight labs and **164 links/anchors**.
No server, PDF/PPTX generation, cloud operations or live agent tests were used.

The shared verifier's stale agenda Lab 3 literal and imported source-only
`process.exit(0)` problem described above are now fixed: it calls diagram
contract functions directly and source-only reaches the deck assertions. Run
the diagram browser verifier separately for rendered diagram checks. The broader
`--all --source-only` regression currently fails because the welcome source still
uses the old Lab 3 label, rather than `explore with SRE Agent`. That source/export
and index/historical cleanup are left to their owning agent; no full-library
regression success is claimed here. Neither this change nor its checks edit
the index, labs, agenda or historical decks.

## Historical Deck

This folder contains a 38-slide Marp deck, its local Fluent-inspired theme, and a dependency-free source checker. Visible slide content uses native Markdown; HTML comments retain Marp directives and all 38 substantive speaker-note blocks. Both 75-minute guided labs are required. Two 30-minute configuration blocks precede the 60-minute reciprocal red/blue battle. The parent agenda, configuration guide, and competition runbook control content and rules.

## Validation Status

- The revised source checker passed for 38 slides, substantive notes, native Markdown without body HTML tags or entities, exact parent agenda labels/times, ordering, battle timing, rubric, scoped reciprocal safety, and embedded/reference CSS parity.
- Segoe UI, Microsoft light styling, and `theme: default` with embedded CSS are preserved.
- The existing HTML export is stale and was not regenerated for this Markdown conversion. Any previously generated PDF/PPTX exports also require regeneration; no refreshed exports are claimed.
- Rendered layout, footer clearance, browser screenshots, PDF/PPTX counts, and presentation-app rendering have not been verified for this conversion. Earlier rendering checks do not validate the new Markdown layout.
- No live preview was started or verified for this revision. Use the command below to start one when needed.
- No cloud access, telemetry queries, test alerts, role assignments, skill loads, delegation, cards, or repairs were executed. Rehearsal remains required.

## Local Checks and Exports

Run in this folder using Windows PowerShell. Prerequisites: Node.js, an installed Marp CLI (`marp` on PATH), and a Marp-supported browser for PDF/PPTX. Keep the parent agenda one directory above this folder. No package installation is performed by this deck. Use `export_marp` through the parent workflow when available, or the CLI commands below.

```powershell
node .\verify.mjs
marp --version
marp .\azure-sre-agent-hackathon.md --output .\azure-sre-agent-hackathon.html
marp .\azure-sre-agent-hackathon.md --pdf --output .\azure-sre-agent-hackathon.pdf
marp .\azure-sre-agent-hackathon.md --pptx --output .\azure-sre-agent-hackathon.pptx
```

The checker validates 38 slides, substantive notes, exact 09:00-17:00 parent agenda labels/times parsed from the native Markdown table, activity order, and the 5+20+10+20+5 battle. It asserts configuration 20 (monitoring/repository/skill/chain, 5 each), defense 60 (diagnosis/recovery/bounds, 20 each), and offense 20 (two judged cards, 10 each), totaling 100 across both waves. It also rejects body HTML tags and entities after stripping comments and frontmatter, and checks reciprocal safety wording, default theme/full embedded CSS parity, and text hygiene. It does not validate rendering, export freshness, or cloud behavior. Segoe UI uses the Windows installation.

The deck deliberately uses `theme: default` plus a YAML `style: |` block containing the full stylesheet, excluding the `@theme` comment and `@import`. The separate `microsoft.css` remains the source/reference stylesheet, including its custom-theme registration and default-theme import. Keep both copies synchronized; the checker enforces parity. This duplication makes standalone `export_marp` exports reliable because that tool does not register the separate CSS. Supply the Markdown input and desired HTML or PDF output path to that tool; no custom-theme registration is needed.

After regenerating, check all 38 slides at 16:9, especially agenda, role names, routing steps, card tables, and scoring; inspect footer clearance, wrapping, and clipping. Verify 38 PDF pages and 38 PPTX slides. Standard Marp PPTX output uses slide images, not editable PowerPoint objects. Check speaker notes in the intended workflow; Markdown remains the source of truth.

Marp live preview from this folder in Windows PowerShell:

```powershell
$env:HOST="0.0.0.0"
marp --server . --port 8080 --theme-set .\microsoft.css
```

Preview address after a successful start: `http://localhost:8080/azure-sre-agent-hackathon.md`. No custom application or application dev server is required. Do not change firewall rules as part of the build.

## Delivery Gate

Preprovision the Running agent, scoped identities, collectors, sanitized repository/clean history, and repeatable harmless alert signal before the clock. Rehearse both guided reads and fallback packets. Confirm effective UAMI and connector permissions, inheritance, namespace authorization, and denied operations; do not use temporary elevation to bypass a failed read.

Distinguish collection, authorized telemetry reads, and native incident routing. Require real fresh query/metric results, a fresh Fired Azure Monitor alert linked to an automatic thread, and a matching enabled Review plan. No guessed webhooks, fabricated rows, or invented repository cause. Verify file/branch/commit, skill loading plus tool use, and downstream traces after role edits.

Native Agent Canvas handoffs, verified workspace Task children, and manual handovers must be labeled accurately. Competition permits full chain credit for an inspected manual chain. The configuration guide additionally requires native or Task automation to pass its automatic-delegation readiness gate; disclose both results. A portal response plan does not prove invocation of local Task roles. Specialists can share credentials; names do not isolate teams.

Explicitly select Review on each response plan/task; both default to Autonomous. Only SRE Agent Administrators approve supported Azure infrastructure writes. Review is not a universal gate for Kubernetes or external tools. Keep the four-role investigation graph read-only; repairs remain facilitator-executed unless a separately isolated own-team executor was approved and rehearsed.

Guided mutations remain facilitator-only. The battle exception is a separately registered red path against exact rival disposable targets, using a separate identity; blue and its agent retain only own-team scope. Default to a constrained broker or facilitator-held manual session and record red initiator versus actual executor. No broad Contributor. Azure writes are not field-level authorization. Kubernetes patch/resourceNames is not property-only: direct red requires enforced, denial-tested admission; otherwise broker. The runbook is not an included runner or policy implementation.

One active fault per workload, at most two cards per team per wave, verified recovery plus two-minute cooldown. Judge only two offense executions across the whole competition. Keep chosen cards/ledgers out of blue knowledge until readout. K8S-C is optional degraded rollout, not guaranteed outage. Anyone may STOP: close queue, cancel pending jobs, revoke and verify denial, preserve monitoring, restore only registered fields. No secret/data/destructive actions or downtime incentives. Reset outstanding faults and revoke wave access before readouts; cleanup inventories remaining resources with the authorized owner at 16:30-17:00.