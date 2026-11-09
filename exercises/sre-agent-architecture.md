# Azure SRE Agent Logical Architecture

This attendee reference connects [Lab 3 main-agent exploration](labs/03-observability.md),
[Lab 4 portal configuration](labs/04-agent-configuration.md) and
[Lab 5 runtime validation](labs/05-agent-validation.md). It describes the
**workshop logical architecture**, not Azure backend internals or evidence that
your team's connections already work. The supplied handover and actual traces
take precedence over example names and product navigation labels.

[![Azure SRE Agent workshop logical architecture: human chat and main agent are separate from explicitly invoked custom triage; AKS evidence returns to triage before analyst synthesis. Skills, knowledge, conditional incident plans, approved tools and four distinct identity responsibilities are shown.](../diagrams/sre-agent-architecture.svg)](../diagrams/sre-agent-architecture.svg)

[Open full-size SVG](../diagrams/sre-agent-architecture.svg) |
[Editable draw.io source](../diagrams/sre-agent-architecture.drawio) |
[Generation and icon provenance](../diagrams/README.md).

## Legend And Scope

Solid blue arrows show intended interactions, not measured execution. Dashed
green arrows show conditional intake, optional routes or retrieval, as named by
their endpoints. The shaded bands group workshop responsibilities; they are
not claims about vendor services, process isolation, physical networks or
the order of Azure authorization internals. The permission box is a checklist
of independent requirements, not a reverse-engineered Azure call sequence.

Retrieval arrows are representative, not exclusive ownership: the main agent
and custom agents can use permitted skills and knowledge. Each custom agent's
actual selections and tool bindings remain separate. The lower read boundary
applies to the main agent, triage and relevant specialists; it does not grant
every role every tool. The analyst only needs returned thread evidence.

## Chat And Custom Workflow

Start Lab 3 in normal chat with the **product main agent**. Creating
`lab-triage` does not replace that agent or make triage the default chat route.
For Labs 4-5, explicitly select triage through `/agent` or the supported
playground selector. A separately accepted response plan can also name triage
as its incident handler; that route is not established by creating the role.

The intended workshop sequence is **triage -> AKS specialist -> return to
triage -> analyst synthesis -> triage final response**. Only triage coordinates.
Inspect native Task or supported handoff traces, including the returned
evidence, before claiming automation. If native delegation is unavailable,
invoke the roles explicitly and label the result **MANUAL HANDOVER**.
Multiple role headings in one answer do not prove delegation.

The starter route uses `lab-triage`, `lab-k8s-specialist` and
`lab-incident-analyst`. The dashed network/VM branch is an optional library
extension, not a requirement to publish all five examples, a parallel fan-out
guarantee or permission for specialist-to-specialist loops. Relevant specialists
must return findings to triage before synthesis.

## Skills And Knowledge

Select the Lab 4 starter skills for the appropriate roles:
`evidence-led-investigation` and `evidence-packet` for triage,
`kubernetes-troubleshooting` and `evidence-packet` for the AKS specialist,
and `evidence-packet` for the analyst. Descriptions guide relevant skill
discovery and retrieval; selection/publication does not prove runtime loading.
Inspect actual skill-load/use references. No invented `/skill` command is needed.

Knowledge files are separately retrieved reference material: sanitized topology,
baseline manifests and runbooks with source revisions. They are not executable
skills, live telemetry or permission grants. Retrieve a known fact and inspect
its source reference independently of the skill test. Repository-relative links
do not upload their targets. Keep credentials, state, private logs, fault
instructions and fault answers out of both knowledge and skill supporting files.
For this workshop, skill tool attachments stay empty; inspected read tools are
bound to the custom agents instead.

## Tools, Connections And Identities

An available tool, saved connection, visible dashboard or successful human read
is not proof of an agent read. Inspect the actual offered inventory, bind only
approved capabilities, and retain the executed tool/query, target, resolved
source revision or UTC sample time. Missing or unsupported routes are BLOCKED.

- **Azure resources:** approved management-plane metadata reads, including AKS
  and Application Gateway. These do not prove Kubernetes namespace access.
- **Log Analytics (LAW):** scoped KQL through an authorized tool against the
  supplied workspace. Built-in Azure tools can read authorized LAW data without
  a separate external connector; an explicit workspace connection adds context.
  A connection does not turn on collection or establish fresh ingestion.
- **Managed Prometheus:** a separate supported query route and scoped PromQL
  result are required; do not substitute a LAW query or dashboard screenshot.
- **Managed Grafana:** dashboard metadata retrieval, Grafana data-query execution
  and direct Prometheus access are different tests. Do not invent a Grafana
  connector if the tenant does not offer one.
- **Repository:** approved read access to a known file at a resolved revision.
  A public fetch or uploaded copy does not prove private connector access.

The four identity boxes are distinct responsibilities, not four agent roles:

- **Signed-in configuration user:** authors settings and supplies approved
  connector consent where needed; portal access does not prove agent access.
- **Actual execution UAMI:** the user-assigned managed identity used for the
  workshop's Azure reads. Verify its principal, effective and inherited RBAC,
  data-plane authorization and tool-policy restrictions independently of prompts.
- **Grafana managed identity:** can authorize Grafana's data sources. Its
  successful dashboard query does not give the agent equivalent access.
- **Separate authorized operator:** owns approved infrastructure changes and
  recovery. Do not give the agent operator credentials or treat a person's
  successful `kubectl` command as agent runtime proof.

External connectors can use their own approved OAuth or service authentication;
do not assume every repository or Grafana request authenticates as the Azure
UAMI. The signed-in author is not automatically the execution principal. The
product also documents temporary on-behalf-of authorization, but this workshop
does not use elevation to bypass missing read access: stop and ask the scope
owner. Inspect actual authentication for each route.

Usable tools, effective RBAC/data-plane permissions, connector authorization
and **network reachability** must all hold. Reader on an Azure resource does
not establish access to a private Kubernetes API or any particular telemetry
endpoint. Read-only tool policy must independently deny mutations, credentials,
Secrets, guest execution and unapproved external posts. Instructions are not
an enforcement boundary.

## Incident And Scheduled Triggers

The intended incident route is **incident platform -> matching response plan
-> lab-triage**. The baseline uses the approved Azure Monitor incident connection
and scoped test title/severity filters. Keep response plans **Off (paused)**
with **Review** explicitly selected until Lab 5 handler acceptance. See the
[example plan payloads](../examples/bootstrap/response-plans.json) for intent,
not an instruction to import JSON or run the bootstrap.

Rule existence, a Fired alert, receiver/email delivery, automatic thread creation
or documented merge, correct handler selection and executed agent tools are
separate observations. Runtime intake requires correlation of a fresh alert
ID/time with the thread/merge, handler and tool trace. Only after acceptance may
the approved test procedure enable a plan; pause it again after the test. An
email plus a manually opened chat proves manual intake only. A response plan
creates neither Azure Monitor rules nor action-group receivers.

Optional scheduled tasks are a **separate trigger**, not an incident response
plan or a required workshop component. If one is used, explicitly set Review,
inspect its selected handler and test it separately. Do not create a task just
to populate the canvas.

**Review is not a universal gate.** It governs approval for Azure infrastructure
operations; it is not a blanket approval prompt for reads, connector calls,
emails or external posts. Set it on each response plan or task rather than
assuming agent instructions or a global fallback enforce it. Tool policies,
authorization and reachability remain independent, including for chat.

## Known Unknowns And Acceptance

The diagram establishes no live health, skill retrieval, native delegation,
safe denial, private endpoint reachability, authenticated connector access or
automatic incident intake. Product navigation, tool IDs and supported handoff
mechanisms vary by tenant/rollout. Task support and static handoffs are not
interchangeable assumptions. No model topology, hidden planner, internal vendor
agents or backend deployment arrangement is asserted here.

Use [Lab 5](labs/05-agent-validation.md) to record PASS/FAIL/BLOCKED per source,
skill retrieval, specialist return, analyst synthesis, independent denial and
alert correlation. Preserve actual trace/source references and observation
times; saved settings and this diagram are not substitutes. Do not perform
mutations or retrieve secrets to test a denial.

## Sources And Attribution

Microsoft Learn references checked on 2026-11-09; these describe product
capabilities, not proof of availability or configuration in this workshop:

- [Custom agents](https://learn.microsoft.com/en-us/azure/sre-agent/sub-agents)
  and [skills](https://learn.microsoft.com/en-us/azure/sre-agent/skills): explicit
  custom-agent invocation, selected skills and knowledge distinctions.
- [Connectors](https://learn.microsoft.com/en-us/azure/sre-agent/connectors)
  and [agent permissions](https://learn.microsoft.com/en-us/azure/sre-agent/permissions):
  built-in Azure reads, external authorization, UAMI and on-behalf-of flow.
- [Incident response](https://learn.microsoft.com/en-us/azure/sre-agent/incident-response),
  [run modes](https://learn.microsoft.com/en-us/azure/sre-agent/run-modes) and
  [scheduled tasks](https://learn.microsoft.com/en-us/azure/sre-agent/scheduled-tasks):
  separate triggers and the limits of Review approval.

Workshop roles, starter selections and acceptance rules come from Labs 3-5
linked above and the [role worksheets](../examples/README.md). This is an
original workshop diagram, not a Microsoft backend architecture illustration.
Unmodified Azure Monitor, AKS, LAW, Prometheus and Grafana icons come from the
existing bundled draw.io assets; their original paths, hashes and notices are
retained in [icon provenance](../diagrams/icons/provenance.json) and the
[diagram license notes](../diagrams/README.md#icon-provenance). Azure SRE Agent
uses neutral labeled boxes, not a fabricated product logo. Names and marks
remain their owners' property; inclusion does not imply endorsement.