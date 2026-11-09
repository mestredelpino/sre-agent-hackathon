# Azure SRE Agent Bootstrap

Optional advanced/operator CLI automation for the five-role example architecture, not the attendee setup route. For the [two-day workshop](../../exercises/two-day-workshop.md), use [Lab 4's portal instructions](../../exercises/labs/04-agent-configuration.md) and [Lab 5's runtime checks](../../exercises/labs/05-agent-validation.md); do not run this bootstrap as part of the lab.

Requires Python 3.10+, GitHub network access, and an authenticated Azure CLI for cloud commands. No third-party Python packages are needed. Azure Public Cloud only. Run commands from the repository root. The [example catalog](../README.md) links individual sources; this guide retains download, API, planning and recovery details for authorized operators.

## Architecture

`lab-triage` coordinates `lab-network-specialist`, `lab-vm-specialist`, `lab-k8s-specialist`, and `lab-incident-analyst`. Only triage has outgoing handoff destinations. Specialists return actual evidence to the invoking coordinator, never delegate to each other. Requests require incident key, exact scope/target, UTC window, baseline, evidence, competing hypotheses, a focused question and stopping condition. Replies require evidence provenance/freshness, confidence, gaps and next discriminating check. Triage permits one call and at most one evidence-driven follow-up per domain.

The bootstrap creates a triage **custom agent**, not a replacement for the product's built-in main agent. Invoke it explicitly using the offered agent selector or `/agent` surface. Existing main-agent instructions, incident response plans and alert routing are not modified; automatic alert-to-triage routing is a separate verified configuration step. A configured handoff is not proof that the runtime invokes a specialist and returns results to its caller: rehearse that behavior before relying on this topology.

For workspace-mode targets, set `delegationMode` to `task` and bind the actual native `Task` tool to triage. The target rejects new static handoff edges; this mode omits them and instructs triage to use Task-based specialist execution. The default `handoffs` mode remains for targets that support static edges. Task availability and actual specialist return behavior still require a runtime rehearsal.

The [manual worksheets](../README.md) are generated from the same `ROLES` and `CONTRACT` definitions as the API payloads. Run `python3 examples/bootstrap/bootstrap.py worksheets` to regenerate them, or append `--check` to detect drift without writing. Both commands are local and need neither Azure access nor downloaded skills. The old recorder worksheet is a deprecated migration pointer, not a sixth active role.

## Download And Validate

```bash
python3 examples/bootstrap/bootstrap.py download
python3 -m unittest discover -s examples/bootstrap -v
```

Downloads six upstream skills at exact commits, retaining every file within each selected skill directory, root licenses where provided, source URLs and SHA-256 hashes under `.state/`. Root-level skills are supported too. No downloaded script executes. Re-running download refreshes the cache from the same pins. Downloads use GitHub's unauthenticated API, so rate limits may apply. The lock is written only after all downloads complete; local validation checks inventory, pinned provenance and file hashes.

| Source | Selected skills | Revision |
| --- | --- | --- |
| [MicrosoftDocs/agent-skills](https://github.com/MicrosoftDocs/agent-skills) | Virtual Machines, Kubernetes Service, Network Watcher, Application Gateway | `6ecdaf59cde880d0ef3d1715357b6c0b0c6696d8` |
| [Azure/sre-agent-plugins](https://github.com/Azure/sre-agent-plugins) | `incident_postmortem_generator` | `3783a11f2f6e3c9b47c6dd9f5b39720ef66b37a3` |
| [microsoft/azure-skills](https://github.com/microsoft/azure-skills) | `azure-diagnostics` operational procedures, references and scripts | `3c89228484f4a9241d255ec7c703976d13277c2d` |

MicrosoftDocs documentation is CC BY 4.0, code MIT; the SRE plugin and Azure Diagnostics are MIT. Source attribution is appended to imported skills and downloaded license files are retained where provided. Six local procedures, including the original incident visualization skill, bring the total to twelve skills. The three diagnostic specialists select `azure-diagnostics`, and the incident analyst selects `mermaid-diagram`; each role has no more than five selected skills.

## Mermaid Diagrams

The original local [incident charts and diagrams skill](../skills/mermaid-diagram.md) replaces the previously inspected third-party skill, whose pinned revision had no license declaration. No third-party Mermaid skill content or scripts are included in the deployment. Historical private downloads are not deployment inputs; no skills.sh provenance is claimed.

The analyst can produce UTC incident timelines, client-to-backend dependency maps, troubleshooting decision trees and recovery metric comparisons. Diagrams distinguish observed traffic, configured dependencies and hypotheses. Charts require actual measurements, consistent buckets/units and rate denominators; missing data is not zero, and percentiles must not be averaged into misleading aggregates. Return Mermaid source or a data table when the host lacks chart support.

No renderer is installed or granted. Mark rendering and visual validation unverified unless separately performed with an authorized tool. This local skill needs no unlicensed-source permission confirmation; the generic `approvedUnlicensedSources` guard remains available for future imports.

The documentation skills require a working Microsoft Learn fetch capability. The local domain procedures need scoped resource/telemetry reads and Kubernetes access where applicable. These dependencies are **not installed or granted** by downloading content. Relative references outside a selected upstream skill directory are not bundled; provide an accessible approved reference if encountered. Only the diagnostic skill from `microsoft/azure-skills` is imported, not the whole deployment/Foundry plugin or its MCP server configuration.

## Diagnostic Dependency Assessment

The pinned Azure Diagnostics skill (upstream version `1.2.14`) has 53 supporting files, including 12 scripts. All are downloaded unchanged under `.state/vendor/azure-diagnostics/` and included as supporting-file content in the skill payload. Local inspection found no missing or out-of-directory relative Markdown links. Imported supporting files are not proof that the runtime exposes them as executable filesystem paths.

| Capability | Dependency and qualification |
| --- | --- |
| Supplied-evidence analysis | Explicitly supported upstream; no live Azure tools needed. Do not claim fresh observations. |
| Resource health, logs and metrics | References Azure MCP AppLens, Monitor and Resource Health areas, with Azure CLI fallbacks. Bind only verified equivalent tools. `az resource show` is resource metadata, not Resource Health, despite the upstream quick-reference label; use the actual health capability. |
| VM diagnosis | The dedicated guide focuses on RDP/SSH, NSGs, credentials and VM agent issues, not comprehensive application/CPU/memory diagnosis. Retain the local VM procedure for that coverage. Guest Run Command, password resets and Serial Console/offline repair paths require separate permissions and are not enabled here. |
| AKS diagnosis | Requires Azure metadata plus Kubernetes reads, ordinarily through `az` and `kubectl`. Some baseline paths inspect nodes, `kube-system`, all-namespace events or acquire credentials/install tools; these exceed the current namespace-only contract. Use supplied evidence or separately permitted focused reads, and mark other checks BLOCKED. |
| Bundled scripts | Bash/PowerShell and their CLI/tool dependencies need an explicitly approved runtime and script review. Download/import alone neither executes them nor authorizes guest commands, credential operations, capture or resource mutations. |
| Deeper AKS operations | The optional `aks-skills` plugin and Inspektor Gadget are not installed. No skill-inventory claim, tool installation, packet capture or tracing execution is implied. Continue baseline analysis where evidence is sufficient. |

Downloading is separate from permission grants. Upstream instructions remain intact; the scoped agent contract governs which operations may actually run. Enabling remediation later requires a deliberate permission, tool-policy and approval design, not merely removing a sentence from a prompt. Native Azure SRE Agent live compatibility remains unverified until tool access, supporting-file retrieval and real specialist execution are tested on the target.

## Configure The Target

Create an untracked `examples/bootstrap/target.local.json` using [target.example.json](target.example.json) as the shape. Replace every placeholder with the approved agent/workload scope, telemetry sources, repository revisions and client vantage points. This example includes both VM and Kubernetes specialists, so it requires an explicitly approved AKS cluster and namespace.

Populate each role's tool list only with actual tool IDs inspected on the target agent. Include documentation-fetch tools on relevant specialists and a verified native delegation capability where required by that runtime. Skill-level tool lists are empty intentionally: importing an upstream skill cannot silently attach tools. Empty role tool lists are suitable for supplied-evidence analysis only, not live diagnosis. Do not copy generic tool names or enable guest execution, writes, credentials, secrets or broad cluster reads to resolve missing capabilities.

Independently verify downstream identity scopes, connector credentials and enforced read-only tool policies; shared subagent identities do not isolate access. Only then set `readOnlyBoundariesVerified` to `true`. This is an operator attestation, not an automated permission test. Keep applicable response plans/tasks in Review; this script does not change run modes, RBAC, connectors, tools, resources or alert subscriptions.

## Plan, Apply And Verify

```bash
python3 examples/bootstrap/bootstrap.py validate --config examples/bootstrap/target.local.json
python3 examples/bootstrap/bootstrap.py plan --config examples/bootstrap/target.local.json
python3 examples/bootstrap/bootstrap.py apply --config examples/bootstrap/target.local.json --confirm '/subscriptions/REAL-GUID/resourceGroups/AGENT-RG/providers/Microsoft.App/agents/AGENT-NAME'
python3 examples/bootstrap/bootstrap.py verify --config examples/bootstrap/target.local.json
```

`validate` is entirely local and writes the assembled payloads to `.state/desired.json`. `plan` performs Azure GETs only, exports the current versions of the seventeen managed definitions and writes a private plan and desired payloads. Inspect `.state/plan.json`, `.state/export.json` and `.state/desired.json` before applying. `export` takes the same scoped snapshot without a plan. Set `AZURE_CLI` to the Azure CLI executable path if it is not `az` on PATH. The authenticated principal needs appropriate configuration read/write permissions on the agent.

`apply` requires exact full agent-ID confirmation, unchanged desired content and an unchanged preflight snapshot. It backs up all managed definitions before any PUT, writes skills first and triage last, skips identical resources, and reads back managed properties afterward. Existing definitions with these names can be overwritten: review the plan carefully, particularly the existing `lab-*` agents. Unrelated definitions are untouched and nothing is deleted. This is not a transaction: API failure stops immediately; inspect the backup and `.state/applied.json` journal, including live reads of a failed/timed-out write, before recovery or replanning. There is no automatic rollback. The preflight check cannot prevent concurrent changes between GET and PUT; use a quiet change window.

State can contain private incident instructions and resource identifiers; keep `.state/` and `target.local.json` out of source control. Files are created with owner-only permissions where supported; verify ACLs separately on Windows-mounted paths. Azure tokens remain in memory and are not written to plans/backups or passed as CLI arguments.

## Acceptance And Limits

The API is preview. Serialization follows [Microsoft's apply-extras implementation](https://github.com/microsoft/sre-agent/blob/main/sreagent-templates/bicep/apply-extras.sh), not portal snake_case YAML. See the [API reference](https://learn.microsoft.com/en-us/azure/sre-agent/api-reference) and [skills documentation](https://learn.microsoft.com/en-us/azure/sre-agent/skills). Unsupported schemas fail rather than falling back to guessed endpoints. Do not treat successful read-back as activation, authorization or reasoning proof.

Live compatibility corrections verified on the hackathon target: supporting files use `filePath` plus `content`, skill names can be returned only in the outer envelope, and handoff descriptions are limited to 500 characters. Complete instructions and supporting-file content remain compared on read-back. ARM extension endpoints were unavailable for this tenant; data-plane publication succeeded. See the [deployment record](DEPLOYMENT.md) for what was and was not verified.

Before use, test healthy and faulty VM/AKS examples, missing telemetry/access, stale or contradictory evidence, injected instructions, out-of-scope requests and domain-routing loops. Capture an actual triage-to-specialist call, its returned evidence, a real scoped read and a recovery check; otherwise mark those capabilities BLOCKED/unverified. Test namespace denial independently of prompt wording. Postmortems must label unknown times/impact and unassigned action owners rather than inventing them. No cloud deployment, skill activation or live delegation was validated during authoring.