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
title: AI and Agents Fundamentals
description: ReAct loops, agent configuration, tools, MCP servers, skills, and runtime controls.
header: 'AI and Agents | Fundamentals'
footer: 'ReAct | Tools | MCP | Skills'
---

<!-- _class: title -->

# Agentic AI Fundamentals
## What an agent can do, and how to check its work

**For everyone** | 09:30-10:15 | 45 minutes, welcome included

<!--
TIME: 60 seconds
Welcome everyone and identify the facilitator and STOP signal. We'll use ReAct, tools, MCP servers, skills and guardrails to describe an agent run. Ask who has already tried a tool-using agent. These are examples, not live operations or Azure SRE Agent configuration. L100 follows this session, then lunch.
-->

---

<!-- _class: title -->

# What changes when AI gets tools?

## It can do more than suggest the next command

An agent might fetch logs, check a configuration, then suggest a repair.
We need to know what it read and whether the result supports that repair.

<!--
TIME: 120 seconds
Ask the room to name a task where the next step depends on the previous result. Log investigation is a useful example: which query would you run after seeing a timeout? Keep examples separate from executed operations. After fundamentals, L100 introduces Azure SRE Agent. After lunch we'll explain the supplied architecture, then check access before configuring the agent.
-->

---

# Chat, tools and autonomy

| Level | What It Does | Examples |
|---|---|---|
| **Chatbot / LLM** | Answers questions, generates text | *"Explain what an NSG is"* · *"What's our SLA target?"* |
| **Tool-using agent** | Calls functions to act on your behalf | *"List my VMs"* · *"Draft a CAB request"* |
| **Autonomous system** | Plans and executes multi-step goals | *"Audit NSG rules"* · *"Prepare the QBR"* |

All three need validation. Tool access adds permissions and side effects;
greater autonomy adds planning and stopping responsibilities.

> In this workshop, the agent investigates. An authorized human handles recovery.

<!--
TIME: 120 seconds
Read the rows as examples, not a maturity ladder. A chatbot returns text; incorrect advice and disclosure of supplied data are still risks. A tool-using agent can call an API or command, so permissions now matter too. An autonomous system chooses more of its own steps, which makes stopping rules important. Ask which kind of system participants have used. More autonomy is not automatically better; a fixed workflow may be enough. Our workshop agent stays read-only and proposes recovery to an authorized human.
-->

---

# A few terms we'll use

| Term | What It Is | Everyday Analogy |
|---|---|---|
| **LLM** | Model that generates text from input | A draft written from a briefing |
| **Prompt** | What you ask | The Teams message you send them |
| **Context** | Material actually supplied to the model | The briefing pack you hand them |
| **Agent** | Model + instructions + tools + feedback loop | An investigation using a runbook |
| **Skill** | Reusable "how-to" instructions | A well-written runbook |
| **Tool** | A capability it can invoke | Access to ServiceNow, Azure, M365 |
| **MCP server** | Standard "plug" exposing tools | Plugging them into a corporate system |
| **Guardrails** | Instructions plus enforced runtime controls | A policy backed by access checks |

> A skill describes a procedure. A tool lets the agent carry out a step.

<!--
TIME: 120 seconds
Use the table as a reference rather than reading every cell. Context means material actually supplied to the model, not everything in your repository or company. A skill might explain how to prepare a CAB request; a tool might retrieve the service record it needs. MCP is one way to expose tools. Guardrails need particular care: an instruction saying "do not delete" is not the same as a permission that prevents deletion. Ask for an example of a skill and a tool from the room.
-->

---

# What goes into a run?

```
   You ──prompt──▶ Agent ──reads──▶ Context
                     │              (services, infra, vendors, SLAs)
                     │
                     ├──follows──▶ Rules / Guardrails
                     │              (no prod deletes · no change during freeze)
                     │
                     ├──uses─────▶ Skills
                     │              (CAB request · NSG audit · QBR slide)
                     │
                     └──calls────▶ Tools  (via MCP servers)
                                    (Azure · ServiceNow · M365 · Learn)
                     ▼
                  Response  (action only if authorized)
```

> We'll look for each of these in Azure SRE Agent after this session.

<!--
TIME: 120 seconds
Walk through one request: "Why is this service slow?" Which context is available? Which procedure should guide the investigation? Which tool can read the relevant metrics? MCP is one source of tools, not the only one. Instructions influence behavior; the runtime and downstream services enforce permissions and any required approval. The response may be a diagnosis or proposal. Nothing in this diagram grants permission to execute a repair.
-->

---

# The Agent Loop (ReAct)

An agent isn't a one-shot response. It runs a short loop: plan something, do it, look at the result, decide what's next.

```
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  THINK  │───>│   ACT   │───>│ OBSERVE │──┐
    │ (Plan)  │    │ (Tool)  │    │(Result) │  │
    └─────────┘    └─────────┘    └─────────┘  │
         ^                                     │
         └───────────────────────────────────────┘
                         │
                    ┌─────────┐
                    │ RESPOND │
                    └─────────┘
```

> Inspect tool requests, results, errors, and stopping decisions in the trace. Do not assume access to internal reasoning.

<!--
TIME: 180 seconds
This is a common agent pattern, not a requirement for every agent implementation. It's called ReAct, short for reason and act.

The agent thinks about what to do next. It picks a tool and calls it. It looks at what came back. Then it thinks again. And it keeps doing that until it has an answer or it's hit some limit.

The useful observable evidence is the tool request, the actual result, and the next action. Products expose different traces; a displayed plan is not a transcript of internal reasoning. Stop when the goal is met, access is denied, approval is required, or the runtime reaches its step, time, or cost limit.

Use a loop when the next step depends on observations. A single call or fixed workflow can be simpler when the path is already known.
-->

---

# Two examples of the loop

**InfraOps:**
```
  Think     Check this subnet's NSG rules
  Act       az network nsg rule list --nsg-name nsg-web-01
  Observe   One rule allows 0.0.0.0/0 on port 22
  Respond   Flag exposed SSH; propose a scoped fix
```

**Service Owner:**
```
  Think     Assess this firewall change
  Act       Read service catalog and change policy
  Observe   1,200 users; valid window; CAB approval required
  Respond   Draft CAB submission, risk, and rollback
```

> Different tools and outputs; the same feedback loop. Illustrative results, not executed reads.

<!--
TIME: 180 seconds
These are illustrative results, not reads we've executed. In the first example, finding an open SSH rule supports a risk report; it does not authorize changing the rule. In the second, service and policy records support a CAB draft, not approval of the change. The Think labels describe intended next steps, not exposed internal reasoning. Ask what else you would check before acting on either recommendation. A trace should show the real tool request and result, including errors.
-->

---

# A custom agent in VS Code

In **VS Code Copilot**, a custom agent can be configured in a Markdown file:

```yaml
---
name: My Assistant
description: Helps me with a specific job
tools: ['read/readFile']
---
You are an assistant for [your role].
You help with [your work].

## Rules
### Auto (do immediately)
- Read-only operations · drafts · summaries
### Confirm first
- Anything with side effects · external comms · approvals
### Hard rejects
- Changes during freeze · actions without rollback · prod deletes
```

<!--
TIME: 180 seconds
This example is for VS Code Copilot, not the Azure SRE Agent configuration format. Copilot supplies the model and execution runtime. The frontmatter names the agent and selects tools; the body describes the work and rules. Read the three groups as intended behavior: do now, confirm first, never do. They still need runtime authorization and approval enforcement. A supported .agent.md file goes in .github/agents and can be selected in Copilot. Tool identifiers and supported configuration depend on the host.
-->

---

# The file is configuration, not the runtime

Copilot Chat runs the agent. The file tells it how you'd like it to work.

- **YAML frontmatter** declares which tools the agent can use
- **Written rules** describe what to do, confirm or reject
- **Runtime controls** enforce permissions and approvals
- **Version control** lets teammates review changes to the configuration

Save a supported `.agent.md` file under `.github/agents/`, then select it in Copilot Chat.

<!--
TIME: 120 seconds
Point back to the file. Changing its instructions changes guidance, not the permissions of an Azure identity. Copilot Chat supplies execution; no separate deployment is needed for this example. A teammate can review the file in a pull request, but a review alone does not prove that the agent loaded it or followed it. Test a representative request and inspect the tool result after a change. Ask where a rejected operation should be enforced.
-->

---

# How Agents Get Tools

Tools let the model request work from another system.

| Source | How | Example |
|---|---|---|
| **Built-in** | YAML `tools:` | Read files, edit docs, run terminal |
| **MCP Servers** | `.vscode/mcp.json` | Azure, ServiceNow, M365, Microsoft Learn |
| **Extensions** | Extension tool IDs | Azure MCP, Resource Graph, Teams notifier |

> MCP connects the host to tool servers. Trust, enabled tools, agent configuration, and authorization still determine access.

<!--
TIME: 120 seconds
Use the table to distinguish built-in tools, configured MCP servers and extension-provided tools. These routes can overlap; an extension may configure an MCP server. A tool appearing in discovery does not mean every agent can use it or that its credentials can reach every resource. Check trust, enabled tools, agent configuration and downstream authorization. We'll look at MCP next without assuming any particular extension is installed for the workshop.
-->

---

# Example `mcp.json`

Example VS Code workspace configuration, subject to server trust and tool enablement.

```json
{
  "servers": {
    "microsoft-learn": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"

    }
  }
}
```

Use HTTP for remote APIs, stdio for local scripts. Tool availability still depends on host configuration and permissions.

<!--
TIME: 120 seconds
This example points to Microsoft's hosted Learn documentation server. Save it as .vscode/mcp.json, review server trust, then verify discovery and enabled tools before claiming the agent can query it. HTTP connects to a remote service. With stdio, the host starts a configured local process and exchanges protocol messages through standard input and output. Only run trusted server code: a local process may have access to your credentials and files. Never commit secrets in the configuration.
-->

---

<!-- _class: title -->

# Model Context Protocol (MCP)
## How agents discover and use tools

<!--
TIME: 120 seconds
Pause for questions about the distinction between instructions and tools. MCP gives hosts and tool servers a common protocol; it is not required for every tool integration. Next we'll follow discovery and a tool call, then discuss the access checks that still have to happen.
-->

---

# MCP in One Slide

MCP is an open standard for connecting AI hosts to tools and context.
A server can expose more than callable functions:

| Capability | What It Exposes | Example |
|---|---|---|
| **Tools** | Functions the agent can call | `create_change_request`, `query_metrics` |
| **Resources** | Data the agent can read | Service catalog, runbooks, configs |
| **Prompts** | Pre-built prompt templates | *"Draft a QBR for {service}"* |

Compatible hosts can reuse servers. Supported capabilities, authentication, and configuration differ between products.

<!--
TIME: 120 seconds
Tools are callable functions. Resources provide data such as a service catalog, while prompts provide reusable templates. A compatible host can reuse a server rather than implementing a separate integration for each tool. Don't promise identical behavior across products: supported capabilities, configuration and authentication vary. Ask which of the three capabilities would suit a runbook lookup and which would suit submitting a change request. Neither capability bypasses the target system's permissions.
-->

---

# How MCP Works

```
  ┌──────────┐    JSON-RPC     ┌──────────────┐
  │  Copilot  │ ───────────>   │  MCP Server   │
  │  (Client) │                │               │
  │           │ <───────────   │  - Tools      │
  │           │   Results      │  - Resources  │
  └──────────┘                 │  - Prompts    │
                               └──────────────┘
```

1. **Discovery** — Copilot asks the server *"what tools do you have?"*
2. **Schema** — server responds with tool names, descriptions, parameters
3. **Invocation** — Copilot calls a tool with structured arguments
4. **Result** — server returns the output, or refuses if the input is invalid

After adding a server, check trust, discovery and enabled tools in the host.
Then test a call with the intended identity.

<!--
TIME: 120 seconds
Follow one call through the diagram. The host discovers available tools and their argument schemas, then sends a structured request. The server checks the request and either returns a result or an error. Valid arguments can still be unauthorized, and downstream execution can fail. Adding mcp.json is only configuration: verify server trust, tool discovery, enabled-tool settings and agent eligibility in the actual host. Don't treat a new chat as proof that the connection works.
-->

---

# The Tool Schema

```json
{
  "name": "get_azure_pricing",
  "description": "Get current pricing for an Azure SKU",
  "inputSchema": {
    "type": "object",
    "properties": {
      "sku": { "type": "string" },
      "region": { "type": "string" }
    },
    "required": ["sku", "region"]
  }
}
```

Discovery supplies names, descriptions, and argument schemas. The model uses that context to choose a tool; the server must validate each call.

<!--
TIME: 180 seconds
Look at the description and required arguments. The model uses that description when choosing a tool, so say exactly what the tool does. The schema tells it which arguments to provide; the server must validate the call before executing the operation. Ask whether a well-formed request can still be unsafe. Yes: a valid SKU and region say nothing about the caller's authority. Schema validation checks argument shape, not identity, authorization, scope or required approval.
-->

---

# MCP and the Security Boundary

MCP is a connection protocol, not an authorization boundary by itself. The host, server, and downstream system must enforce access.

### What the server controls
- **Which actions exist** — only tools you define are discoverable
- **Parameter validation** — the schema rejects invalid inputs before the tool runs
- **Scope enforcement** — restrict to specific services, environments, regions
- **Credential isolation** — keep credentials out of model-visible inputs and results

When you design a new tool, start from the smallest permission that lets it do its job and only widen if you have to.

<!--
TIME: 120 seconds
An MCP server can restrict its tools, but another connector, a shell command or a direct API may provide a different route to the same system. Check the whole execution path, including shared identities. Validate inputs and enforce allowed scope on the server. Keep credentials out of model-visible inputs and results, and check logs for accidental exposure; MCP doesn't guarantee isolation. Start with the smallest permission the task needs. Ask how you would demonstrate that an out-of-scope request is actually denied.
-->

---

# A restart tool needs more than a name check

Constrain inputs, then authorize the resolved target on the server:

```json
{
  "name": "restart_service",
  "description": "Restart a service by name (non-prod only)",
  "inputSchema": {
    "properties": {
      "service_name": { "type": "string", "pattern": "^(dev|stg|test)-.*$" },
      "resource_group": { "type": "string" }
    },
    "required": ["service_name", "resource_group"]
  }
}
```

A naming pattern rejects malformed input; it does **not** prove environment or ownership. Resolve the resource, check an allowed non-production scope, and use a least-privilege identity before execution.

<!--
TIME: 120 seconds
Ask whether a production service could have a name beginning with dev-. It could, so the regex isn't enough. The backend must resolve the resource and reject production targets even if the name matches. Check the caller's permission and allowed scope, and bind any required approval to the exact operation. Schema checks belong alongside target allowlists, authorization and tested denials. This slide is a design example; we do not execute a restart.
-->

---

# Context, Memory, and Skills

### Short-term (the current conversation)
```
  Turn 1:  You: "List the backup service incidents"   → Agent: shows them
  Turn 2:  You: "Which one took longest?"             → Agent knows the list
  Turn 3:  You: "Draft a remediation plan for that"   → Agent knows which
```

### Reusable guidance (loaded when applicable)
```
  .github/instructions/team-defaults.instructions.md
    → "Always tag resources with env + team; frame comms in business impact"

  .github/skills/cab-request/SKILL.md
    → "CAB format: summary, risk, rollback, affected users, window"
```

Instructions guide behavior; **skills package reusable procedures**, references, and optional scripts. Loading depends on the host and task. Neither grants permission or retrains the model.

<!--
TIME: 180 seconds
The conversation can supply the incident list for a follow-up question, but context windows are finite; don't assume every earlier turn is still available. Repository instructions and skills let teammates reuse guidance without pasting it into every request. Loading depends on the host, matching rules and task, so verify that the right file was loaded and followed. These files don't retrain the model or grant permissions. Persisted guidance can also become stale: review it when the underlying process changes.
-->

---

# What can go wrong?

| Failure | What Happens | Mitigation |
|---|---|---|
| **Hallucinated facts** | Invents an SLA number, command, or contact | Read from real catalog / validate first |
| **Tool misuse** | Right tool, wrong parameters | Schema validation in MCP server |
| **Infinite loops** | Agent retries a failing action | Set max iteration limits |
| **Scope creep** | Touches resources / services it doesn't own | Restrict tool permissions per agent |
| **Confidential leaks** | Repeats secrets in chat or reasoning | Filter sensitive output, server-side auth |
| **Over-confidence** | Approves something it shouldn't | Enforced approval and authorization |

> Two habits will save you: never let an agent execute without a safety boundary, and never approve a draft you haven't actually read.

<!--
TIME: 120 seconds
Ask which failure participants have already seen. A source lookup helps catch invented facts, but you still need to read the result. Schema validation catches malformed arguments, not every wrong target. Put retry limits in the runtime and scope restrictions in authorization, not just instructions. Filter sensitive results before they reach the model. Approval and denial must be enforced even when the answer sounds confident. Before approving a draft, check what it actually proposes and what evidence supports it.
-->

---

# What customization adds

| | Generic AI Chat | Your Custom Agent |
|---|---|---|
| **Context** | What you supply in the chat | Selected service records and references |
| **Process** | Explained in each request | Rules + skills; validate results |
| **Consistent output** | Varies per prompt | Reusable format; check adherence |
| **Boundaries** | Depend on host and permissions | Runtime checks + tested denials |
| **Reviewable configuration** | Often kept in individual chats | Shared Markdown in version control |
| **Reusable across the team** | Re-prompt every time | Shared files; verify loading |

> Shared configuration saves repeated setup. It doesn't guarantee a correct answer.

<!--
TIME: 120 seconds
Customization makes procedures and references easier to share and review. It does not mean the agent knows everything in the company or follows every instruction reliably. A general chat can also use supplied context; the useful difference here is reusable, reviewable configuration and tools. Version control shows configuration changes, while execution traces show what happened in a run. Ask which procedure participants would want to make reusable, and how they would test it.
-->

---


# What's Next

## Azure SRE Agent: the building blocks in a real product

**10:15-11:00 L100 | 11:00-12:00 lunch**

- In L100, look for the pieces we just discussed.
- After lunch: handover and architecture 12:00-12:45; access 12:45-13:00.
- Later, we'll follow a real tool call and check its result.

> Azure SRE Agent has its own runtime and configuration. The VS Code files above are examples, not its setup format.

<!--
TIME: 60 seconds
Finish at 10:15 and move to the unchanged supplied L100. Lunch is 11:00-12:00. The combined handover, scope, costs and platform/application/observability architecture block runs 12:00-12:45, including a 20-minute overview and 25 minutes for handover and guided walkthrough. Access and permission checks follow at 12:45-13:00 for Azure, AKS, Grafana and SRE Agent. Break is 13:00-13:15; Lab 3 explores metrics, logs and alerts 13:15-14:00, Lab 4 configures SRE Agent 14:00-15:00, and Lab 5 first validates it 15:00-16:00, including the 15:50-16:00 checkpoint and overnight handover. Day 2's 12:00-12:45 slot is optional agent refinement and validation follow-up, not first validation, with no faults; scaling remains 12:45-13:45. The facilitator provides the infrastructure, app and agent resource. No server, permission or cloud resource has been created by viewing these examples.
-->

