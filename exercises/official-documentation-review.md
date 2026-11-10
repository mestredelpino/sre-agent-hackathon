# Microsoft Learn Review

Reviewed on 2026-11-10 using the configured Microsoft Learn MCP server: search
followed by full-page fetches before substantive corrections. This is a source
review, not proof of live tenant behavior. No provisioning, permission changes,
cloud mutations, staging or commits were performed.

## Workshop Decisions

Infrastructure, Store and observability are supplied; participants create the
SRE Agent in Lab 4. Lab 3 establishes a human telemetry baseline first. Its agent
prompts are a deferred follow-up after creation, not a prerequisite. Investigation
identities stay read-only; authorized operators own changes and publishing.
Triage alone coordinates specialist returns and analyst synthesis. These are
workshop choices, not restrictions on the product's supported handoff patterns.

## Official Sources And Corrections

| Source | Consequence for this workshop |
| --- | --- |
| [Create and set up](https://learn.microsoft.com/en-us/azure/sre-agent/create-and-set-up) | Create agent > Basics > Review > Deploy; creation needs Owner, or Contributor plus User Access Administrator. Adding Azure scopes requires active Owner or User Access Administrator on each scope. Review provider, monitoring resources and identity choices. |
| [Supported regions](https://learn.microsoft.com/en-us/azure/sre-agent/supported-regions) | Use the current reference and subscription's Region picker, not an old three-region list. Empty picker is a registration blocker. Region is immutable and need not match workloads. |
| [General FAQ](https://learn.microsoft.com/en-us/azure/sre-agent/faq) | Owner checks Microsoft.App provider registration separately from subscription registration/allowlisting. Older region and permission summaries conflict with dedicated pages; do not treat them as a complete creation contract. |
| [Agent permissions](https://learn.microsoft.com/en-us/azure/sre-agent/permissions) | Reader setup can include Monitoring Contributor and OBO elevation. Inspect actual generated/inherited roles; do not authorize OBO to pass investigation checks. |
| [Tool access policies](https://learn.microsoft.com/en-us/azure/sre-agent/tool-access-policies) and [Run modes](https://learn.microsoft.com/en-us/azure/sre-agent/run-modes) | Review is not universal enforcement. User-defined hook Allow can override global deny. Inspect hooks, tool rules, connector permissions and RBAC together. |
| [Create a skill](https://learn.microsoft.com/en-us/azure/sre-agent/create-skill) and [Skills](https://learn.microsoft.com/en-us/azure/sre-agent/skills) | Agent Canvas > Create > Skill; preserve synchronized editor frontmatter. Skill selection/publication does not establish activation or tool authorization. |
| [Upload knowledge](https://learn.microsoft.com/en-us/azure/sre-agent/tutorial-upload-knowledge-document) and [Custom agents](https://learn.microsoft.com/en-us/azure/sre-agent/sub-agents) | Wait for Indexed, inspect source access and test in a new conversation. Test playground, /agent selection and actual call/return evidence are separate from saved definitions. |
| [Create a response plan](https://learn.microsoft.com/en-us/azure/sre-agent/response-plan) | Agent Canvas > Create > Trigger > Incident response plan. Defaults are Autonomous and On after Create, not a guaranteed paused create. Keep proposed settings or owner-prepared Off plans. |
| [Incident platforms](https://learn.microsoft.com/en-us/azure/sre-agent/incident-platforms) | Incidents > Connect an incident platform is distinct from outbound connectors. Inspect all routes, including Autonomous quickstart_handler; one incident platform can be active. Never delete another team's plan. |
| [Azure Monitor intake](https://learn.microsoft.com/en-us/azure/sre-agent/azure-monitor-alerts) | Native intake acknowledges alerts and requires subscription Monitoring Contributor. It remains BLOCKED under the strict read-only workshop boundary. Manual supplied alert evidence cannot pass automated intake. |
| [AKS kubeconfig access](https://learn.microsoft.com/en-us/azure/aks/control-kubeconfig-access) and [API authorization](https://learn.microsoft.com/en-us/azure/aks/entra-id-authorization) | User credentials are not workload authorization. Namespace reads and cluster-scoped node/CRD reads need separate approved authorization or labeled supplied evidence. |
| [Grafana permissions](https://learn.microsoft.com/en-us/azure/managed-grafana/how-to-permissions) | Human Viewer access and the backend identity's metrics/log permissions differ. Inspect the supplied dashboard; do not republish monitoring. |
| [Container logs schema](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-logs-schema) | ContainerLog support retired September 30, 2026. Owner migration to ContainerLogV2 and fresh-query validation are required; legacy panels remain BLOCKED. |
| [AGIC architecture](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview) | Service/Ingress relationships identify endpoints; Application Gateway forwards to backend pod IPs, not an extra ClusterIP proxy hop. Existing diagrams retain logical Service relationships. |
| [Managed KEDA](https://learn.microsoft.com/en-us/azure/aks/keda-about) | KEDA supplies the external metric and HPA handles positive replica scaling. Lab 6's one-worker minimum does not demonstrate scale-to-zero cooldown. |
| [NAP default pools](https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-node-pools) and [Disruption](https://learn.microsoft.com/en-us/azure/aks/node-auto-provisioning-disruption) | None does not delete existing default pools. Inspect actual pools/classes. Use managed Karpenter APIs, not a second standalone installation; deletion can terminate capacity. |

## Unresolved And Preview-Dependent

- Official pages differ: the older FAQ lists three regions, while the dedicated
  supported-regions page lists more. The create/setup and permission references
  also describe monitoring grants differently. Use the dedicated current route
  plus actual offered scopes, identity assignments and owner review; never infer
  least privilege from a UI label.
- Learn uses both Builder and Build + setup, and both Skill builder and Canvas
  authoring. Screenshots are examples, not evidence that a particular tenant has
  the same controls. Missing controls are BLOCKED; do not invent APIs or labels.
- Native Task IDs, static-handoff rejection, bootstrap endpoint/schema behavior
  and previously recorded tool IDs are tenant observations, not portable product
  contracts. The optional CLI path is not the participant baseline. Revalidate
  supported interfaces and actual child execution/returns before relying on it.
- Native intake requires a separately approved boundary outside this workshop.
  Read-only manual investigation may pass independently, but automated intake
  stays BLOCKED. Do not silently relax the read-only decision or call alert
  acknowledgement a read.
- The provisioning owner must confirm the approved infra release contains the
  migrated tools/store-demo helpers, supported log schema, fresh panels and rules,
  expected NodePools and working gateway TLS. A historical source pin or rehearsal
  does not establish today's configuration or health.
- Permissions, hook decisions, knowledge retrieval, skill loads, runtime reads,
  native delegation, public HTTPS/orders, notifications and disposal/cost outcomes
  still require current dated evidence from their respective identities.

## Local Validation Boundaries

Focused source/link and presentation export/browser checks do not prove Azure
runtime behavior. Existing general validators still refer to intentionally
deleted setup/route documents and to a recorder deprecation contract inconsistent
with the current worksheet. Preserve these failures as maintenance findings;
do not restore deleted guides or weaken assertions to manufacture a pass.

Results from this review:

- PASS: 29 priority Markdown files, balanced code fences and 156 local
  links/heading anchors; all eight lab guides retain no workshop scheduling
  labels. Technical durations and evidence timestamps remain.
- PASS: all seven lab decks' source contracts, exact HTML/notes/image parity,
  negative task/clock/link controls, 50 desktop/mobile bounds checks and negative
  overflow control, with zero browser runtime/asset errors. Four changed decks
  have regenerated matching HTML; sample desktop/mobile screenshots were reviewed.
- PASS: 20 offline bootstrap unit tests, editor diagnostics and `git diff --check`.
- Existing failures retained: examples/skills/verify.mjs expects the recorder to
  be deprecated; worksheets --check reports generator drift; exercises/verify-two-day.mjs
  opens the intentionally deleted route document; slides/verify-architecture-and-challenge.mjs
  --all expects older exact agenda labels. No assertions were changed.
- Working-tree boundaries preserved: nothing staged or committed; labs 6-8 and
  their presentation sources/HTML remain untracked and uncommitted. The supplied
  L100 PowerPoint remains ignored and untouched. No cloud actions were run.