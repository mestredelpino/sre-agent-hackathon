# Lab 4: Configure Azure SRE Agent

Create your SRE Agent resource before configuring it.
Infrastructure and the Store are pre-provisioned, but the SRE Agent resource is not.
Use the approved scopes from the handover and configure it in the portal;
no bootstrap script is needed.

## Steps

### 1. Create Your Team SRE Agent Resource

Sign in to [Azure SRE Agent](https://sre.azure.com) with your approved authoring
identity and confirm the tenant. The owner must confirm an active subscription,
**Owner**, or **Contributor** plus **User Access Administrator**, on the creation
scope, and browser access to `*.azuresre.ai`. Adding Azure resource scopes later
requires active Owner or User Access Administrator on every selected scope;
activate approved PIM assignments before setup. These are authoring permissions,
not investigation permissions.

Have the owner confirm `Microsoft.App` resource-provider registration, also
listed in the [official FAQ prerequisites](https://learn.microsoft.com/en-us/azure/sre-agent/faq#getting-started).
Registration and subscription allowlisting are separate checks. Missing either
is an owner blocker, not permission for participants to register providers or
expand their roles.

Select **Create agent**. In **Basics**, select the approved subscription and existing
resource group, enter the approved agent name and choose an offered region.
Use the [supported-regions reference](https://learn.microsoft.com/en-us/azure/sre-agent/supported-regions)
and the selected subscription's Region dropdown, not an old three-region list.
An empty list is a registration blocker for the owner; do not change subscription
to bypass it. The agent region cannot be changed after creation and need not
match the workload region. Select the approved offered model provider and
Application Insights option; provider availability and data residency vary.
Review the offered identity and resource-access settings with the authorized
owner before submitting. If creation requires permissions, consent or an identity
assignment that is not already approved, STOP and ask that owner; do not grant
yourself roles or invent RBAC assignments to proceed.

Select **Next**, review the target and proposed settings, then submit **Create**
only with the authorized human's approval. Wait for deployment **Succeeded**,
then select **Set up your agent**. Record any newly created monitoring resources
and both identities: the UAMI is used for connectors/RBAC; the SAMI supports
agent infrastructure. Record the agent workspace URL, full resource ID,
name, tenant, subscription, region and actual execution identity in the handover.
If resuming an existing attempt, inspect the recorded resource before retrying
so you do not create a duplicate. Failed provisioning is BLOCKED, not readiness.

Resource creation and configuration are authorized human writes, distinct from
the investigator's read-only workload access. Creation success does not prove
scoped reads or enforcement; inspect those independently below and in Lab 5.

Source: [Microsoft Learn: Create and set up](https://learn.microsoft.com/en-us/azure/sre-agent/create-and-set-up).

Locate Quickstart, Skill builder and Agent Canvas in the navigation. Newer
navigation uses **Build + setup**, while older navigation uses **Builder**.
If a feature is missing, record it and ask for help rather than guessing an API.

Before replacing an existing shared definition, preserve its previous content
in approved private notes and get approval; do not assume undo or automatic
rollback. If saving fails, reopen the stored version before retrying. Do not
delete another team's definitions or upload connector credentials into knowledge.

### 2. Connect Resources, Logs, Code And Knowledge

Inspect existing connection entries first; do not create duplicate connectors
or replace shared credentials. Use the controls in the table to connect only
the assigned resources, workspace and repository, then add a small sanitized
knowledge document. Save and reopen each entry to check its stored settings.
Keep its name, approved scope, execution identity and check result in a private
source list for Lab 5.

These are separate connections. A successful resource read does not prove log,
repository or private Kubernetes access. Your signed-in configuration identity
is also not necessarily the identity executing the agent's reads.

#### Portal Permissions Checklist

- Confirm the team agent resource ID, resource groups, AKS ID, namespace,
  telemetry sources and repository revision against your handover. Scope text
  in instructions does not grant or enforce access.
- Inspect the execution managed identity and inherited assignments in the
  resource's identity and access-control settings. The recorded deployment used
  Reader on approved agent/workload groups and Log Analytics Reader on its
  workspace. Adapt to the team's approved scopes. Report unwanted broader
  inherited grants through an authorized owner, not by copying private principal
  IDs. Grafana's identity and your signed-in authoring identity are separate.
- Ask the authorized policy owner to confirm an independently enforced read-only
  tool policy denying mutations, guest/command execution, credential retrieval,
  secrets, direct Kubernetes operations unless specifically authorized, and
  external posts/integrations not needed for reads. Verify effective denial with
  safe non-mutating tests; prompt instructions and an allow list cannot neutralize
  a broader inherited role by themselves. Record untested boundaries as unproven.
- In **Build + setup > Extensions > Tools > Advanced permissions**, have the
   administrator inspect global denies and all applicable user-defined hooks.
   A hook returning Allow can bypass even a global deny. Review hook decisions,
   connector governance and effective RBAC together before accepting enforcement.
   Source: [Tool access policies](https://learn.microsoft.com/en-us/azure/sre-agent/tool-access-policies).
- Broad deny aliases such as `bash`, `shell` and `execute_bash` can also match
  approved Azure read tools. Rehearse permitted reads and denials together; do
  not blindly copy a policy and call it proven.

The setup **Reader** label is not a strict read-only guarantee. The
[permissions reference](https://learn.microsoft.com/en-us/azure/sre-agent/permissions)
documents subscription-level Monitoring Contributor among the preconfigured
roles, and temporary on-behalf-of (OBO) elevation. Inspect actual generated and
inherited grants before connecting workloads; do not authorize OBO elevation.
If the offered setup adds writes, stop and have the authorized owner establish
and verify the approved read-only configuration before investigation. Do not
silently accept alert-lifecycle writes as read-only access.

| In the portal | What to enter or select | Check after saving |
| --- | --- | --- |
| **Quickstart > Azure resources**, or the offered managed-resources settings | Select only the assigned resource groups and approved Reader permission level. Inspect existing assignments first. | Correct scope and execution identity; ask the authorized owner about missing or broader inherited access. Do not grant subscription Contributor. |
| **Quickstart > Logs**, or the offered logging-provider connection | Choose the supplied Log Analytics workspace by full resource ID. Add Application Insights only if supplied. | Correct workspace/identity and a bounded query against a populated table. Connecting does not enable collection. |
| **Quickstart > Code**, **Code Access**, or repository connections | Select the approved GitHub organization/repository and read-only access. Consent only within the assigned installation scope. | Retrieve a known file and record its actual revision. Do not grant issue, workflow or PR writes just to read code. |
| **Build + setup > Context > Knowledge sources**, or **Full setup > Knowledge files** | Select **Add file**, choose the sanitized architecture/runbook document and select **Add file** to upload. Record its source revision. | Wait for **Indexed**, not Pending, then retrieve a known fact in a new conversation with a source reference. Confirm Knowledge settings and the custom agent's source access are enabled. |

For knowledge, use approved architecture prose, baseline manifests or telemetry
notes. Do not upload state, tfvars, credentials, private logs, fault instructions
or fault answers, including local target configuration and operator instructions.
Knowledge files are reference material, not executable skills. Relative repository
links do not automatically upload their targets. Downloading supporting files
does not execute scripts or install a renderer, MCP server or extra troubleshooting
plugin.

Prometheus, Grafana and direct Kubernetes reads need their own supported tools
and permissions if used. Do not invent a connector where none is offered. Record
unsupported routes for Lab 5 instead of attaching a generic privileged shell.

### 3. Create Skills In Skill Builder

Open **Build + setup > Workflows > Agent Canvas > Create > Skill**, the
[documented creation route](https://learn.microsoft.com/en-us/azure/sre-agent/create-skill).
Other documented surfaces expose Skill builder; use it only if offered. Create
`evidence-led-investigation`, `kubernetes-troubleshooting` and `evidence-packet`
using the [local catalog](../../examples/skills/README.md) as the content source.

Screenshots are Microsoft Learn examples, not your team's environment. They
need internet access and may show different labels or settings. Follow the
lab's scope and tool selections; select an image to view it full size.

[![Microsoft Learn screenshot of the create-skill dialog, showing skill authoring controls.](https://learn.microsoft.com/en-us/azure/sre-agent/media/skills/portal-create-skill.png)](https://learn.microsoft.com/en-us/azure/sre-agent/media/skills/portal-create-skill.png)

Source: [Microsoft Learn: Create skills](https://learn.microsoft.com/en-us/azure/sre-agent/skills#create-skills).

| Field | What to put there |
| --- | --- |
| Name | The source's `name`, for example `evidence-led-investigation`. Use a consistent team prefix if sharing an authoring workspace. |
| Description | The source's discovery description: when this procedure should be used, not just its title. |
| SKILL.md/content | Keep the editor's YAML frontmatter synchronized with the Name, Description and Tools fields. Replace the procedure below it with the source's Markdown body. Do not remove the editor frontmatter or paste a role worksheet as a deployment manifest. |
| Supporting files, if available | Attach only the approved referenced files. Otherwise replace relative references with reachable approved repository/knowledge citations. |
| Tools | For this exercise, leave skill tool attachments empty and assign the necessary inspected read tools to the custom agents below. Check effective available tools rather than assuming this constrains all inherited capabilities. |

Choose Save/Create, reopen the saved skill and check its description and full
procedure. Repeat for the other two starter skills. A saved skill is not yet proof
that the agent loaded it; descriptions guide automatic discovery, and Lab 5
checks actual retrieval/use. You do not need an invented `/skill` command.

### 4. Create Custom Agents In Agent Canvas

Open **Build + setup > Workflows > Agent Canvas**, or **Builder > Agent Canvas**.
Choose **Create > Custom Agent** where offered. Use the role worksheets as
copy-and-adapt references, not an import file. Create the Kubernetes specialist
and analyst first, then triage:

[![Microsoft Learn screenshot of Agent Canvas with custom agents, tools and trigger connections.](https://learn.microsoft.com/en-us/azure/sre-agent/media/sub-agents/portal-sub-agent-canvas-full.png)](https://learn.microsoft.com/en-us/azure/sre-agent/media/sub-agents/portal-sub-agent-canvas-full.png)

Source: [Microsoft Learn: Custom agents](https://learn.microsoft.com/en-us/azure/sre-agent/sub-agents).
The canvas is an example, not a graph you must reproduce; your tenant may use
Task delegation without static handoff edges.

| Agent | Instructions source and purpose | Choose Skills | Tools |
| --- | --- | --- | --- |
| `lab-k8s-specialist` | [Kubernetes worksheet](../../examples/agents/lab-k8s-specialist.md): investigate scheduling, readiness and dependencies within the assigned scope. | `kubernetes-troubleshooting`, `evidence-packet` | Approved AKS metadata/log reads; namespace object reads only if independently authorized. |
| `lab-incident-analyst` | [Analyst worksheet](../../examples/agents/lab-incident-analyst.md): synthesize returned evidence and separate facts from hypotheses. | `evidence-packet` | None needed for thread-evidence synthesis. |
| `lab-triage` | [Triage worksheet](../../examples/agents/lab-triage.md): own intake, scoped investigation and final response. | `evidence-led-investigation`, `evidence-packet` | Approved resource/log reads and verified delegation capability where available. |

In **Instructions**, copy and adapt the worksheet's instruction content, not
its explanation or unsupported YAML fields. Include approved scope references
and evidence/uncertainty rules. In **Handoff Description**, write when to use
this role, for example: "Investigates AKS workload readiness and dependency
failures using approved namespace evidence; returns findings to triage."

In **Choose Skills**, select the skills you saved. In **Built-in Tools** or
**Custom Tools**, inspect the actual offered capabilities. A read-only Azure CLI
tool and Log Analytics query tool may be appropriate, but names are not portable
permission guarantees. Do not select write commands, guest execution, Secret
reads or broad Kubernetes tools. Keep the analyst evidence-only.

The recorded deployment used `RunAzCliReadCommands`,
`QueryLogAnalyticsByResourceId` and `FetchWebpage`, plus native Task on triage.
These are observed IDs, not portable guarantees. Bind only equivalent inspected
capabilities. Skill tool lists stay empty so upstream content cannot silently
grant tools.

Save each agent, then use Table view or the offered list to reopen it. Check its
stored instructions, skill selections, read-tool bindings and supporting files.
Keep private notes or sanitized screenshots of changed settings.

If your tenant supports native
handoffs with return to triage, configure only triage's relevant specialist and
analyst routes. Some workspace targets reject static handoffs and instead expose
native Task delegation; use it only if available and independently tested.
Do not draw imaginary canvas edges or assume a portal setting installs Task.
If neither works, invoke each role explicitly and label it MANUAL HANDOVER.
Only triage coordinates; specialists do not delegate to each other.

Add network/VM specialists and further skills only when relevant; completing
every example definition is not required for the baseline.

### 5. Review Proposed Response Plans In The Portal

Native Azure Monitor intake acknowledges alerts and requires subscription-level
Monitoring Contributor. That conflicts with this workshop's strict read-only
investigator boundary. Leave native intake **BLOCKED**; do not connect it or grant
that role to pass the lab. Manually supplied alert evidence is not automated
intake proof. Source: [Azure Monitor integration](https://learn.microsoft.com/en-us/azure/sre-agent/azure-monitor-alerts).

The documented connection route is **Incidents > Connect an incident platform >
Azure Monitor**; inspect an existing connection only, without disconnecting a
shared platform. Only one incident platform can be active. Before any separately
authorized connection or activation, the owner must inspect **Incidents >
Triggers & response plans**, including `quickstart_handler` and all overlapping
plans. The quickstart plan defaults to Autonomous and can run alongside custom
plans. Do not enable it or delete another team's plan.

The documented authoring route is **Build + setup > Workflows > Agent Canvas >
Create > Trigger > Incident response plan**. Record proposed settings below;
inspect an owner-prepared Off plan if supplied. Creation requires an incident
platform and is documented to save a plan **On**, followed by **Turn off > Yes**;
there is no documented initially-disabled creation guarantee. Do not create a
plan merely to turn it off afterward in this lab. The
[example payloads](../../examples/bootstrap/response-plans.json) explain field
values; do not paste JSON into a chat or assume the portal imports it.

Record the plan name, Azure Monitor source, title/severity filters and
`lab-triage` as **Response subagent**. Choose **Review** for **Agent autonomy level**,
not in the custom agent's instructions; new plans default to Autonomous.
Record **Reinvestigation cooldown** enabled with a three-hour window. Inspect
stored values and Off status only if an owner-prepared plan already exists.
Start with the AKS plan below; add the gateway plan for that additional route.

| Plan | Source/filter | Handler and initial state |
| --- | --- | --- |
| `lab-gateway-incident` | Azure Monitor; title contains `[TEST] gateway`; Sev0-Sev3 | Proposed `lab-triage`, Review; existing prepared plan Off; cooldown three hours |
| `lab-aks-workload-incident` | Azure Monitor; title contains `[TEST] aks`; Sev0-Sev3 | Proposed `lab-triage`, Review; existing prepared plan Off; cooldown three hours |

Match Lab 3's real test title/severity and connection, and ensure the connector
does not expose another team's incidents. Mark an unused gateway route not
exercised rather than inventing evidence. Response plans create neither Azure
Monitor alert rules nor receivers. Leave prepared plans Off. Lab 5 runtime
acceptance does not resolve the native intake permission conflict; that needs a
separately approved boundary outside this workshop. Keep Review explicit on any
used scheduled task too. If no task is needed,
do not create one just to fill a checklist.

Sources: [Create a response plan](https://learn.microsoft.com/en-us/azure/sre-agent/response-plan),
[Incident platforms](https://learn.microsoft.com/en-us/azure/sre-agent/incident-platforms).

### 6. Try Your Agent In The Playground

1. In Agent Canvas, select the saved `lab-triage` agent and open **Test playground**.
   If that surface is unavailable, open the offered chat agent selector and
   choose `lab-triage`, or use the supported `/agent` picker. Confirm the selected
   agent name before sending. Creating it does not replace the main agent or
   automatically route existing incidents. If no supported selector is available,
   record the blocked check and ask for help.
2. In the message box, paste the example below. Replace the scope and UTC
   placeholders with your handover values and name the known document you added.
   Select Send and let the read finish; do not approve a write, credential request
   or broader scope to make the test pass.
3. Expand the returned tool/activity trace or execution details offered by your
   portal. Inspect the actual tool name, query scope, time range and result. Open
   the source reference for the retrieved fact and compare it with your known
   document and revision. A prose claim of a read is not proof. If traces or source
   references are unavailable, record that limitation rather than claiming success.
4. Save the conversation link or ID in private notes, plus sanitized trace/source
   screenshots where supported. Record the selected agent, UTC test time, source
   revision, read result, unknowns and blocked checks. Use the offered Save action
   for any configuration changes, then reopen the agent from its list to confirm
   they persisted. Leave all response plans Off.

[![Microsoft Learn screenshot of the agent playground with instructions and a test chat side by side.](https://learn.microsoft.com/en-us/azure/sre-agent/media/common/playground-agent-selected.png)](https://learn.microsoft.com/en-us/azure/sre-agent/media/common/playground-agent-selected.png)

Source: [Microsoft Learn: Test and develop custom agents](https://learn.microsoft.com/en-us/azure/sre-agent/sub-agents#test-and-develop-custom-agents).

Suggested first playground prompt:

```text
Within <approved resource groups, AKS ID and namespace>, investigate the healthy
baseline over <UTC start/end>. Retrieve <known architecture document and revision>
and run one bounded inventory or log query through an approved connection.
Compare two possible explanations for any missing data. Report actual tool/source
references, sample times and unknowns. Do not change resources, obtain credentials
or widen access. If a connection is missing, say which check is blocked.
```

## Checkpoint

Keep your source list, three saved starter skills, three saved custom agents,
a proposed Review plan matching the AKS test alert (or an owner-prepared Off
plan), and evidence of one real scoped
read or its recorded blocker. Add the gateway plan only for its intended route,
noting whether it is exercised. Saved configuration is not proof of skill
activation, delegation or alert intake; those are tested in Lab 5. No bootstrap
execution or full-library import is required.

In Lab 5 capture triage -> relevant specialist -> triage -> incident analyst ->
final output, a scoped live query, safe denials and a manual alert-evidence
investigation. Keep native intake BLOCKED, not passed by the manual thread. Capture
evidence-packet synthesis as actual agent work. Mermaid is optional; renderer availability and
visual verification are separate gates. Those are the artifacts retained for
the facilitator's common-fault challenge, not a participant-written substitute.

## Go Further: Make The Agent Useful Between Incidents

Once the baseline works, choose one extension below. These are optional stretch
activities, not extra baseline requirements. Use supplied approved
integrations or continue afterward; leave the core checkpoint intact if
consent, permissions or a supported product feature is unavailable. Record
configured, manually tested and scheduled execution as separate results.

### Draw The Investigation With Mermaid

Create the [Mermaid skill](../../examples/skills/mermaid-diagram.md) using Skill
builder, then select it on the analyst in Choose Skills and save the agent.
Ask it to produce a dependency diagram or incident timeline from returned
evidence, with source references and uncertain relationships labeled. For example:

> Draw the request and order-processing paths supported by this thread. Return
> Mermaid source and list which links are configuration, observations or still
> unknown. Do not turn a configured dependency into a measured traffic claim.

Check that the analyst actually retrieves/uses the skill. Use the supported
renderer if one is available, or preview the source in an approved local tool.
Skill publication does not install a renderer or MCP server. Do not send private
incident data to a public rendering service. Keep the source alongside the image
so another person can review or correct it.

### Create An Editable draw.io Diagram

1. Open **Skill builder** and create a skill from
   [drawio-diagram](../../examples/skills/drawio-diagram.md), using Step 3's
   field mapping. Copy its name, discovery description and procedure. Leave tool
   attachments empty, save and reopen the skill.
2. Open **Agent Canvas > lab-incident-analyst > Choose Skills**, select
   `drawio-diagram`, save and reopen the agent. Keep its tools unchanged;
   producing XML from supplied evidence needs no diagnostic or file-write tool.
   Stay within the tenant's skill limit; replace an unused optional diagram
   skill rather than selecting the entire catalog.
3. Open the analyst in **Test playground**. Supply a small sanitized evidence
   packet with component names, relationships, source references and UTC window.
   Then send a request such as:

   > Use drawio-diagram to show the request and order-processing paths supported
   > by this packet: <reviewed evidence>. Return uncompressed editable draw.io
   > XML, an evidence legend and unknowns. Distinguish configuration from observed
   > traffic and hypotheses. Do not fetch extra data or publish the diagram.

4. Inspect the trace for actual skill retrieval/use. Review the XML text for
   credentials, external links or image URLs before opening it. In an approved
   local text editor, place only the XML in a file ending `.drawio`; do not
   include the Markdown fence. The agent does not need permission to write it.
5. In an approved diagrams.net desktop editor, use **File > Open From > Device**
   or its local-file open control. Select the file, check labels, arrow direction
   and evidence legend, move a node and edit a label. Save and reopen to confirm
   it remains editable. Retain the original and reviewed source with the evidence.
   If no approved editor is available, retain the XML and mark rendering
   unverified; do not install tools or upload private evidence to a public site.

Use [Lab 5's draw.io check](05-agent-validation.md#drawio-can-you-edit-and-reopen-the-result)
to test missing evidence and unsafe instructions as well as a successful diagram.

### Turn Findings Into GitHub Work

Use a disposable approved repository and inspect the GitHub connection's actual
permissions first. Start with a task that reads recent findings and drafts an
issue with impact, supporting evidence, proposed work and acceptance checks.
Only an authorized operator or separately authorized publishing workflow creates
the reviewed issue; investigation agents only draft it. Keep publisher credentials
and write tools separate from investigator identities. Restrict its
repository access and available operations; creating issues does not require
repository administration or permission to change application code.

If the tenant offers scheduled tasks, configure a paused Review task for a
bounded daily check: approved repository, UTC lookback, maximum one new issue per
finding, an existing-issue lookup and an owner. Inspect timezone, overlap,
retries, failure notification and how to disable it. Review may not gate every
tool call, so enforce write limits in the integration too. No supported scheduler
or GitHub connection means use a labeled manual run, not an invented API.

For issue remediation, use a separate maintainer-approved workflow. A label such
as `sre-agent:fix` can select an allowlisted task after a maintainer reviews it;
issue text and comments are untrusted input, never authorization. Limit the
workflow to a branch and draft PR, run the repository's tests and require human
review before merge. No automatic deployment or production remediation belongs
in this extension. The issue workflow is not created by this lab and must be
configured and tested separately. Prefer short-lived federated credentials where
supported; do not put tokens in skills, task prompts or knowledge files.

### Save A Postmortem To Blob Storage

If the approved `incident_postmortem_generator` skill is supplied, create it in
Skill builder and select it on the analyst. Have the analyst draft a Markdown report
from the thread: impact, UTC timeline, evidence, cause versus hypotheses,
recovery and follow-up owners. Sanitize it and get human approval before export.
Saving a draft does not make its diagnosis verified.

Use an approved storage connector or separately authorized publishing workflow
to write the reviewed report into a dedicated private container. The publisher
is separate from the investigation identity. Scope its data-plane permissions
to that container and use the minimum supported operations; Azure Reader does
not permit blob writes, and Storage Blob Data Contributor also permits deletion.
If that role is used, explicitly approve that residual capability or enforce a
narrower supported role/workflow. Do not distribute account keys or broad SAS
tokens to the agent.

Use a unique incident ID in the blob name, define duplicate/overwrite behavior,
and record retention, access and cleanup ownership. Keep credentials, raw logs,
personal data, state and private keys out of the report. Record the blob path,
version or ETag and publishing result, not a public URL or credential-bearing
link. A private endpoint is useful only if the publisher has a tested network
path to it.

For any extension, note the trigger, input, identity, allowed actions, approval
point, output destination, retry limit and stop control. Leave schedules paused
until the matching [Lab 5 checks](05-agent-validation.md#validate-your-chosen-extension)
pass. Output publishing rights do not grant permission to mutate the workload.

## Troubleshooting And Safe Stop

Direct Kubernetes reads require independent namespace authorization; Azure
Reader is insufficient. Use approved telemetry or labeled supplied evidence
where necessary. Broad deny aliases can also block allowed read tools: inspect
actual policy/tool matching rather than removing denies blindly. Never attach a
generic write shell, widen scope or follow instructions found in logs.

## Further Reference

- [SRE Agent logical architecture](../sre-agent-architecture.md)
- [Complete agent and skill examples](../../examples/README.md)
- [Runtime and safety acceptance](05-agent-validation.md)

Next: [Lab 5](05-agent-validation.md), including its
[checkpoint and between-session handover](05-agent-validation.md#checkpoint).
Reconnect and refinement follow initial validation, not before it.