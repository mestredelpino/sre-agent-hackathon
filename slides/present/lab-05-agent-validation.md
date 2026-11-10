---
marp: true
theme: default
size: 16:9
paginate: true
title: SRE Agent Validation
description: A two-slide introduction to demonstrated trust, runtime evidence and incident intake.
header: 'Azure SRE Agent Workshop | Validation'
footer: 'Day 1 | Lab 5 | Validation'
style: |
  section { width: 1280px; height: 720px; padding: 90px 64px 66px; justify-content: flex-start; background: #faf9f8; color: #201f1e; font-family: 'Segoe UI', 'Segoe UI Variable', sans-serif; font-size: 26px; line-height: 1.34; letter-spacing: 0; }
  section::before { content: ''; position: absolute; top: 28px; left: 64px; width: 13px; height: 13px; background: #f25022; box-shadow: 16px 0 #7fba00, 0 16px #00a4ef, 16px 16px #ffb900; }
  header { position: absolute; top: 30px; left: 110px; right: 64px; font-size: 17px; color: #605e5c; }
  footer { left: 64px; bottom: 23px; font-size: 14px; color: #605e5c; }
  section::after { right: 42px; bottom: 22px; font-size: 15px; color: #605e5c; }
  h1 { margin: 0 0 20px; border: 0; color: #0078d4; font-size: 41px; font-weight: 600; line-height: 1.15; }
  p { margin: 0 0 18px; }
  strong, a { color: #0078d4; }
  strong { font-weight: 600; }
  a { text-decoration: none; }
  ol { margin: 0 0 22px; padding-left: 32px; }
  li { margin-bottom: 17px; padding-left: 5px; }
  li::marker { color: #0078d4; font-weight: 600; }
  .question { border-left: 4px solid #9a6700; background: #fff8e5; padding: 16px 22px; margin-bottom: 24px; font-size: 28px; }
  .small { font-size: 21px; color: #605e5c; }
  @media print { section { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
---

# Configured is not demonstrated

<div class="question">Trust is specific to a demonstrated capability, source and permission boundary.</div>

1. **An executed tool read supports an observation.** Target, source and sample time give it scope.
2. **Retrieval and skill use are separate claims.** Stored content does not prove runtime use.
3. **A call and return demonstrate delegation.** Role headings alone are only presentation.
4. **Enforced denial establishes a boundary.** A model refusal alone is not authorization evidence.

<p class="small">Lab 5 connects each capability to the runtime evidence that supports it.<br><a href="../../exercises/labs/05-agent-validation.md">Agent validation</a></p>

<!--
TIME: 90 seconds.
Lab 5 runs from 15:00 to 16:00, including these three minutes. Validation bridges configured intent and demonstrated behavior. An executed tool read establishes an observation under a particular identity, connection and UTC window. A plausible answer or person's terminal result does not establish an agent read. Retrieval has separate evidence about which reference and version was available; skill use is another claim. Delegation needs a call and return rather than specialist headings. Human role calls remain MANUAL HANDOVER. Trust grows capability by capability: Azure resources, logs, Prometheus, Grafana and repository access can have different outcomes. A model refusal is different from enforced authorization. Missing traces limit what is demonstrated, even when another capability works.
-->

---

# Incident intake is an evidence chain

<div class="question">A Fired alert proves an evaluation outcome, not delivery to an investigating agent.</div>

1. **Evaluation produces an alert.** Rule state and timestamps describe the detected condition.
2. **Delivery connects systems.** Notification and automatic thread or merge link the alert to intake.
3. **Handling begins investigation.** A handler and tool trace show what executed after intake.
4. **Correlation supports the claim.** Shared alert identity and UTC times connect the stages.

<p class="small">Native Azure Monitor intake stays BLOCKED under the read-only boundary.<br><a href="../../exercises/labs/05-agent-validation.md">Manual evidence is not automated intake</a></p>

<!--
TIME: 90 seconds.
An incident crosses several boundaries before investigation. Rule evaluation, notification delivery, automatic thread creation or merge, handler selection and tool execution are separate events. Alert identity and UTC timestamps connect them into one evidence chain. Individually plausible screenshots do not establish that continuity. Azure Monitor native intake acknowledges alerts and requires subscription Monitoring Contributor, conflicting with this workshop's strict read-only investigator boundary. It remains BLOCKED; the chain describes evidence needed in a separately authorized workflow, not an instruction to enable it here. Email plus a manually opened chat demonstrates manual intake only. Review does not remove this permission conflict. The handover retains which capabilities were demonstrated and which remain uncertain. Source: https://learn.microsoft.com/en-us/azure/sre-agent/azure-monitor-alerts.
-->