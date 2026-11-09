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

<p class="small">Demonstrated trust is bounded: one working connection does not validate every source.<br><a href="../../exercises/labs/05-agent-validation.md#suggested-prompts-and-queries">Lab 5 evidence examples</a></p>

<!--
TIME: 90 seconds.
Lab 5 runs from 15:00 to 16:00, including these three minutes. Validation is the bridge between configured intent and demonstrated behavior. An executed tool read establishes a particular observation under a particular identity, connection and UTC sample window. A plausible answer, suggested query or person's terminal result does not establish that the agent performed that read. Retrieval has its own evidence: a known document and version establish which reference was available, while skill loading or use is another distinct claim. Delegation similarly needs a call and return, not merely specialist headings in a response. Human role calls remain MANUAL HANDOVER. Trust therefore grows capability by capability rather than as one global pass for the entire agent. Azure resources, logs, Prometheus, Grafana and repository access can have different outcomes. Permission enforcement also differs from model behavior: a polite refusal is not proof that a write would be denied by authorization or tool policy. Only owner-approved non-mutating checks or effective-permission evidence belong here, never destructive denial tests. Missing traces or unavailable safe tests remain BLOCKED rather than being inferred from another successful path.
-->

---

# Incident intake is an evidence chain

<div class="question">A Fired alert proves an evaluation outcome, not delivery to an investigating agent.</div>

1. **Evaluation produces an alert.** Rule state and timestamps describe the detected condition.
2. **Delivery connects systems.** Notification and automatic thread or merge link the alert to intake.
3. **Handling begins investigation.** A handler and tool trace show what executed after intake.
4. **Correlation supports the claim.** Shared alert identity and UTC times connect the stages.

<p class="small">Email plus a manually opened chat demonstrates manual intake, not automation.<br><a href="../../exercises/labs/05-agent-validation.md">Lab 5</a> | <a href="../../exercises/two-day-workshop.md#day-1-checkpoint-1550-1600-within-lab-5">Handover reference</a></p>

<!--
TIME: 90 seconds.
An incident crosses several boundaries before an agent investigates it. A rule evaluates data and enters Fired state; notification delivery is another event. The incident connection then creates an automatic thread or a documented merge, selects a handler and starts tool execution. An alert ID and UTC timestamps correlate these stages. Without that continuity, several individually plausible screenshots do not prove one end-to-end path. Email plus a manually opened chat establishes manual intake only. Evaluation and ingestion delay also differ from investigation duration, so timing claims need the appropriate starting event. A fresh Fired alert matters because re-enabling a still-Fired instance may not emit another notification. During the session, the approved operator owns temporary rule changes without fault injection; a matching plan is enabled only after handler acceptance with explicit Review. Temporary rules are disabled and test plans paused after capture, never bypassed with improvised connections. The final 15:50-16:00 checkpoint records PASS/FAIL/BLOCKED per capability and an overnight owner, budget and disposal deadline. Optional Day 2 follow-up does not replace first validation or consume scaling time.
-->