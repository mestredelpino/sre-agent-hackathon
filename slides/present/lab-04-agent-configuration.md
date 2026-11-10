---
marp: true
theme: default
size: 16:9
paginate: true
title: SRE Agent Configuration
description: A two-slide introduction to skills, agents, connections and independent permission boundaries.
header: 'Azure SRE Agent Workshop | Configuration'
footer: 'Day 1 | Lab 4 | Configuration'
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

# Skills, agents and connections

<div class="question">Configuration defines how an agent reasons, where it gets context and what it can access.</div>

1. **Skills supply procedures.** Reusable methods guide investigation and evidence reporting.
2. **Custom agents define roles.** Triage coordinates; specialists investigate; analysts synthesize.
3. **Connections expose sources.** Resource, telemetry and repository access are distinct paths.
4. **Knowledge supplies reference context.** Retrieved documents inform reasoning, not permissions.

<p class="small"><a href="../../exercises/labs/04-agent-configuration.md">Lab 4</a> | <a href="../../examples/skills/README.md">Skill sources</a> | <a href="../../examples/README.md">Role examples</a></p>

<!--
TIME: 90 seconds.
Lab 4 runs from 14:00 to 15:00, including this three-minute introduction. It develops a model of four configuration elements that are easy to conflate. A skill describes a method, such as evidence-led investigation. A custom agent gives that method a role, scope and responsibility. A connection exposes a source through tools and authorization. Knowledge supplies retrieved reference material rather than access rights. A Kubernetes specialist might use a troubleshooting skill, read telemetry through an approved connection and consult a runbook. Those are independent dependencies: a stored runbook does not make telemetry accessible, and a selected skill does not prove use. Understanding these distinctions explains what configuration can express and why Lab 5 needs separate runtime evidence.
-->

---

# Coordination is not authorization

<div class="question">A role describes responsibility; identity and tool policy determine effective access.</div>

1. **Triage owns coordination.** lab-triage receives specialist evidence before analyst synthesis.
2. **Tools and identity bound execution.** A role name or skill grants no permission.
3. **Response plans route incidents.** Filters select an intended handler; Review is not a universal gate.
4. **Configuration is intent, not proof.** Saved roles do not demonstrate reads or delegation.

<p class="small">The main agent and explicitly selected custom agents are separate entry points.<br><a href="../../exercises/sre-agent-architecture.md">Architecture and permission boundaries</a> | <a href="../../exercises/labs/05-agent-validation.md">Runtime evidence in Lab 5</a></p>

<!--
TIME: 90 seconds.
Coordination and authorization solve different problems. Triage owns the conversation, specialists return evidence and an analyst synthesizes it. The analyst needs those returns rather than a duplicate set of diagnostic tools. lab-triage is a separate, explicitly selected entry point from normal main-agent chat. Native Task or handoff traces can demonstrate delegation; human role calls remain MANUAL HANDOVER. Effective access depends on execution identity, scoped authorization, reachable connections and tool policy, including inherited access. The configuration author's identity and Grafana's identity are separate. Response-plan filters express intended incident routing, while Review governs supported approval paths rather than every external call. This model explains why clear instructions, stored settings and enforced permissions are different claims.
-->