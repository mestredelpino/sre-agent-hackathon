# Workshop Architecture Diagrams

Use the [two-day lab route](../exercises/two-day-workshop.md) for attendee steps
and the [slide index](../slides/README.md) for delivery order.

The four handout diagrams and nine focused slide views are genuine editable
draw.io graphs: named mxGraph vertices, connected edges, editable text, and
embedded original icons. The SVGs are presentation exports made by the installed
draw.io extension's mxGraph renderer, not hand-drawn SVGs renamed as draw.io.
Each generated SVG includes a title, description and the matching editable `mxfile` in its
`content` attribute. Both sources and exports work offline without the icon library.

There are 13 matching draw.io/SVG pairs, checked against [views.mjs](views.mjs)
and the [asset contract](contract.mjs), including the focused observability view.
Sources and exports serve editing and offline presentation respectively; keep both.

## Edit And Export

Open any `.drawio` file in the VS Code draw.io extension or diagrams.net.
For a one-off edit, save the source and export an SVG with **Include a copy of
my diagram** enabled, embedded images, and the original page dimensions.
Keep the accessible title and description when replacing an export.
The shared validators reject source/export drift, missing icons and wrong sizes.

The repeatable baseline is [views.mjs](views.mjs). Change its node labels,
positions or connected routes, then run from the repository root in Windows
PowerShell with the existing Node, Marp and Edge installation:

```powershell
node diagrams/generate.mjs
node diagrams/verify.mjs --browser
node exercises/verify-two-day.mjs
```

Generation overwrites the generated source/export pairs. Transfer GUI edits
back to the baseline before regenerating. `DRAWIO_WEBAPP` selects the extension's
`drawio/src/main/webapp` directory; `MARP_CLI_ROOT` and `BROWSER_PATH` select a
compatible Puppeteer installation and browser. Defaults match the local workshop
installation. No draw.io CLI or network service is required. The source is built
with mxGraph's structured model and XML codec, decoded again, then rendered with
`mxImageExport` and `mxSvgCanvas2D`; icon image references become base64 data URLs.

Handout: [platform.drawio](platform.drawio), [application.drawio](application.drawio),
[observability.drawio](observability.drawio), and
[sre-agent-architecture.drawio](sre-agent-architecture.drawio). The dedicated
[SRE Agent SVG](sre-agent-architecture.svg) is an 1800x1580 workshop logical
overview, not Azure backend internals. Its
[attendee guide](../exercises/sre-agent-architecture.md) explains chat/custom
entry points, skill versus knowledge retrieval, conditional incident intake,
approved tools and independent identity boundaries. It is not a slide-deck
asset and makes no live execution claim. Generate just this pair with
`node diagrams/generate.mjs --view=sre-agent-architecture`, without rebuilding
slide assets or decks. Use `node diagrams/verify.mjs --source-only` to check intent
before generating, then the full check above to validate exports.

Canonical deck 05 architecture uses
five assets: [05-platform.svg](05-platform.svg), [05-ingress.svg](05-ingress.svg),
[05-application.svg](05-application.svg) and [05-observability.svg](05-observability.svg)
at 1152x338, plus [06-control.svg](06-control.svg) at 1152x300. Canonical deck 06
challenge briefing has no diagrams. The other generated `06-*` pairs remain
available; see the [maintenance audit](../MAINTENANCE.md#decision-required) for
unused-view candidates, not an instruction to delete them. The handout views are larger.
Slide HTML uses the SVG assets by relative path; keep `diagrams/` alongside
`slides/` when distributing the ready-to-present HTML. After diagram changes,
refresh dependent decks using the [slide build instructions](../slides/BUILD.md).

## Observability Presentation View

The two-slide observability intro uses
[07-sre-agent-architecture.svg](07-sre-agent-architecture.svg) and its
[editable source](07-sre-agent-architecture.drawio), a **1152x408** focused view
derived from the existing full SRE Agent architecture. It retains chat versus
explicit custom triage, specialist returns before synthesis, distinct retrieval
sources and independent read boundaries. Optional triggers and identity details
remain in the linked full diagram and guide. The same original AKS icon is used;
no new icon provenance or license is introduced. Generate only this pair with
`node diagrams/generate.mjs --view=07-sre-agent-architecture`, then run
`node slides/verify-observability.mjs --browser` after exporting the deck.
The shared diagram contract checks route parity with the full view and minimum
20px labels. Both architecture views describe configured intent, not execution.

## Icon Provenance

Only the nine used original Azure SVG assets are copied into [icons/](icons/).
[icons/provenance.json](icons/provenance.json) records their original bundle paths,
package version `hediet.vscode-drawio` 1.19.0 and SHA-256 hashes. The generator
copies original bytes, including any embedded notices, without recoloring or
tracing. Application Gateway, AKS, Log Analytics, Grafana, Prometheus, Azure
Monitor, ACR, Key Vault and Storage use these real bundled icons. Prometheus
represents managed Prometheus collection in AMW, not an invented AMW product logo.
Application components, RabbitMQ, DocumentDB, cert-manager, KEDA, NAP and SRE Agent
use neutral labeled nodes: no substitute vendor or managed-database logos.

The local draw.io distribution carries Apache License 2.0 in
[icons/LICENSE-drawio.txt](icons/LICENSE-drawio.txt), retained in full, and the icon
notice in [icons/NOTICE-drawio.txt](icons/NOTICE-drawio.txt), also retained verbatim.
That notice restricts icon/stencil software assets in Atlassian products and
explicitly exempts end-user diagram output, such as these workshop documents.
This repository does not distribute an icon library or Atlassian integration.
Product names and marks remain their owners' property; inclusion describes the
architecture and does not imply endorsement or grant trademark rights.

## Reading The Routes

Solid blue arrows are configured request, telemetry or notification relationships,
not measured traffic. Dashed green means control/support, intended authorized
reads or explicitly conditional intake. AGIC is not an inline proxy. TLS ends at
Application Gateway; frontend Services remain ClusterIP and administration private.
Queue arrows mean message delivery; makeline initiates its broker connection.
KEDA replicas and NAP capacity are separate. LAW, AMW, Grafana, receiver delivery
and agent intake need independent runtime proof. The prose, notes and handover
remain authoritative for revisions, identity scopes and known unknowns.