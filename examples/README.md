# Agent And Skill Examples

For the [two-day workshop](../exercises/two-day-workshop.md), follow [Lab 4's portal instructions](../exercises/labs/04-agent-configuration.md): start with triage, the Kubernetes specialist and the analyst, using investigation, Kubernetes and evidence-packet skills. Prove runtime behavior in [Lab 5](../exercises/labs/05-agent-validation.md). Lab 3 uses the supplied main agent before custom configuration.

These are adaptable source examples, not mandatory installed IDs or a role-count target. Network/VM procedures and upstream additions are optional when relevant; the current workshop platform is AKS Store, not a separately supplied VM lab.

## Source Catalog

The role worksheets share canonical definitions with the [optional advanced CLI bootstrap](bootstrap/README.md), which documents pinned downloads and the full five-agent/twelve-skill library. Attendees do not run it in Lab 4. Triage invokes relevant specialists, collects returned evidence and invokes the analyst; specialists never delegate to each other.

| Source | Purpose |
| --- | --- |
| [Skill catalog](skills/README.md) | Seven local procedures, capability boundaries and domain acceptance cases |
| [Investigation intake](skills/evidence-led-investigation.md) | Scope, hypotheses and bounded routing |
| [Network procedure](skills/network-troubleshooting.md) | DNS, reachability, NSGs, routes and gateway evidence |
| [VM procedure](skills/vm-troubleshooting.md) | Resource, guest and application health evidence |
| [Kubernetes procedure](skills/kubernetes-troubleshooting.md) | Namespaced workloads, events, Services and endpoints |
| [Evidence synthesis](skills/evidence-packet.md) | Contradictions, gaps, approval and recovery handoff |
| [Mermaid diagrams](skills/mermaid-diagram.md) | Evidence-based timelines, dependency diagrams and recovery charts |
| [Editable draw.io diagrams](skills/drawio-diagram.md) | Evidence-grounded XML for local review and editing; optional portal-authored skill |
| [Triage agent](agents/lab-triage.md) | Example incident intake and routing worksheet |
| [Network specialist](agents/lab-network-specialist.md) | DNS, routes, NSGs, gateway probes and backend paths |
| [VM specialist](agents/lab-vm-specialist.md) | VM platform, resource and collected application evidence |
| [Kubernetes specialist](agents/lab-k8s-specialist.md) | Example workload/path investigation worksheet |
| [Incident analyst](agents/lab-incident-analyst.md) | Evidence synthesis, recovery handoff and blameless postmortems |

The three `lab-*` skill migration pointers and the old [recorder worksheet](agents/lab-incident-recorder.md) are historical only, not additional publishable definitions or instructions to change live resources. The recorder file still contains old instructions rather than the pointer emitted by the generator; see the [worksheet drift audit](../MAINTENANCE.md#validation). Existing published definitions are unchanged by these source updates.

## Adapt And Publish

Record your chosen role/skill names, revisions, discovery descriptions, procedure ownership and runtime in the private facilitator-approved environment record. Keep incident scope and resource bindings outside reusable procedures. Role count and names may differ; maintain explicit evidence transfer and approval boundaries.

Follow the [Azure SRE Agent publishing checklist](../SRE-AGENT-SETUP.md) and [configuration guide](../AGENT-CONFIGURATION.md). Skill frontmatter is source metadata, not a deployment schema. Copy the Markdown body into the supported skill content field; include frontmatter only if the offered whole-document editor supports it. Agent worksheets supply Instructions and Handoff Description fields, not an import bundle. Repository links may need approved, accessible citations in the saved content. Opening, moving or copying files does not publish or install anything, and does not configure VS Code discovery. Other runtimes need their own supported format, discovery rules and validation.

Examples grant no permissions or automatic tool access. Independently enforce identity, own-resource/namespace scope, connector credentials and read-only tool policies. Keep every used response plan/task explicitly in Review; it is not a universal write gate. Repairs require a separately authorized operator, approval, rollback and fresh recovery verification. Do not attach arbitrary execution, secret access or write-capable tools to make an example work.

## Acceptance And Evidence

Apply the [acceptance matrix](skills/README.md#acceptance-matrix) to your own definitions and selected domain: healthy, fault, missing permissions/collection, stale evidence, injected instructions and out-of-scope requests. Also test contradictory evidence and bounded routing where used. Use only approved disposable fixtures or sanitized supplied evidence; these tests authorize no cloud writes. Supplied evidence cannot prove live access.

Retain actual discovery/load evidence for at least one relevant skill procedure, an actual scoped read with UTC/sample freshness, and evidence synthesis/handoff wherever used. Record custom names/revisions and the runtime's supported trace references; a name in an answer is not activation proof. Mark unsupported or unobservable activation BLOCKED/unverified, and unrelated domains not requested. No requirement exists to load all five example skills in one investigation.

Review custom definitions by the same observable behavior, not exact example IDs or role count. Inspect evidence passed and results at each claimed transition. An explicitly labeled, verified manual chain remains a valid workshop approach; it is not native automation. Never claim handoffs, tool use or approval that did not occur.

## Local Source Checks

Run `node examples/skills/verify.mjs` and `python3 examples/bootstrap/bootstrap.py worksheets --check` from the repository root. They validate the local skill sources, imported skill IDs, five worksheet bindings, manual/CLI parity and local links, not attendee naming choices or Azure installation. The optional draw.io skill is published manually through the portal; it does not change the bootstrap's publication set. Regenerate supplied worksheets with `python3 examples/bootstrap/bootstrap.py worksheets`; edit the bootstrap definitions first, not the generated worksheets. Live publishing, loading, authorization and behavior still require the acceptance evidence above.