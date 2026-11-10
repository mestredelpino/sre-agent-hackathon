# Azure SRE Agent Hackathon

## Start Here

Follow the [pre-provisioned workshop handover](exercises/pre-provisioned-workshop.md)
and the [agenda](AGENDA.md). The facilitator provides the infrastructure,
deployed Store application and observability resources. Participants inspect
that environment; they do not redeploy the platform or application.

**The SRE Agent resource is not provided.** Participants create it in Lab 4
using the approved subscription, resource group, agent name and region, then
configure its identity and read-only workload access. Lab 5 validates runtime
behavior; supplied infrastructure is not proof of working agent access.

## Participant Labs

| Lab | Guide | Focus |
| --- | --- | --- |
| 1 | [Platform](exercises/labs/01-platform.md) | Confirm supplied scope, architecture and access. |
| 2 | [Application](exercises/labs/02-application.md) | Inspect Store health and the request/order paths. |
| 3 | [Observability](exercises/labs/03-observability.md) | Inspect supplied telemetry, dashboard evidence and notification boundaries before agent creation. |
| 4 | [Agent Configuration](exercises/labs/04-agent-configuration.md) | Create the SRE Agent resource and configure approved capabilities. |
| 5 | [Agent Validation](exercises/labs/05-agent-validation.md) | Verify live reads, delegation and denied operations. |

Continue with [Lab 6: Autoscaling](exercises/labs/06-autoscaling.md),
[Lab 7: Challenge](exercises/labs/07-challenge.md) and
[Lab 8: Closeout](exercises/labs/08-closeout.md) as directed by the agenda.

## Supporting Material

- [Presentation index](slides/README.md): workshop decks and lab introductions.
- [Agent and skill examples](examples/README.md): source material for Lab 4.
- [Skill catalog](examples/skills/README.md): investigation procedures and evidence handling.
- [Facilitator preparation](facilitator/README.md): operator-only deployment references.

## Safety And Evidence

Use only the facilitator-approved scope. Keep participant, agent execution,
configuration and recovery identities separate; the agent's workload access
remains read-only. Human changes require explicit authorization.

Set **Review** explicitly on incident response plans and scheduled tasks, and
leave untested automation paused. Review is not a universal write gate:
identity permissions and tool policies must also enforce the boundary.

The setup Reader label is not sufficient: inspect generated/inherited roles,
OBO elevation paths and hooks that can override tool denies. Native Azure Monitor
intake acknowledges alerts and requires Monitoring Contributor, so it remains
BLOCKED under this workshop's strict read-only boundary. Manual alert evidence
does not pass automated intake. New response plans are documented to start On;
record proposed settings or inspect owner-prepared Off plans, rather than
assuming creation can be paused.

Never share credentials or upload secrets, private keys, Terraform state or
fault ledgers as knowledge. Do not inject faults before Lab 7; use only its
approved challenge procedure and recovery operator. Anyone may STOP.

Record observed evidence and label supplied evidence or blocked checks honestly.
Reading these documents does not provision resources or prove live readiness.

See the [official documentation review](exercises/official-documentation-review.md)
for Microsoft Learn sources, documentation conflicts and unresolved runtime gates.
