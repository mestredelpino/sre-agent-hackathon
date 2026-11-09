---
marp: true
theme: default
size: 16:9
paginate: true
title: Observability With SRE Agent
description: A two-slide introduction to observability signals, evidence limits and the SRE Agent architecture.
header: 'Azure SRE Agent Workshop | Observability'
footer: 'Day 1 | Lab 3 | Observability'
style: |
  section {
    width: 1280px;
    height: 720px;
    padding: 90px 64px 66px;
    justify-content: flex-start;
    background: #faf9f8;
    color: #201f1e;
    font-family: 'Segoe UI', 'Segoe UI Variable', sans-serif;
    font-size: 26px;
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
  figure { margin: 0; }
  .diagram { display: block; width: 1152px; height: 408px; }
  figcaption { margin-top: 12px; font-size: 20px; color: #605e5c; }
  .sources { margin-top: 12px; font-size: 20px; }
  @media print { section { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
---

# Signals become evidence in context

<div class="question">Observability connects a service's behavior to evidence about its internal state.</div>

1. **Metrics describe patterns.** Rates, errors and saturation show change over time.
2. **Logs describe events.** Workload context and timestamps connect individual observations.
3. **Evidence has provenance.** Executed reads, sources and sample times support a claim.
4. **Every signal has limits.** Running pods do not prove successful customer orders.

<p class="small">Grafana and the supplied main agent offer different views of the same sources.<br>Missing samples are unknown, not zero; agreement depends on scope, time and units.</p>

<!--
TIME: 90 seconds.
Lab 3 occupies 13:15-14:00; this introduction uses three and a half minutes within it. Observability is the ability to reason about internal behavior from emitted signals, not simply the presence of a dashboard. Metrics summarize change over intervals; logs preserve individual events and their context. A low CPU average can coexist with failed orders, and a running pod can still serve errors. Evidence becomes useful when its target, UTC sample window, source, units and aggregation are known. A suggested query is not a result: executed reads establish what was actually observed. Grafana is a human view of connected sources, while the supplied main agent produces an interpretation through its own tools and identity. Their conclusions are comparable only when scope and time align. Neither view is complete, and missing samples are not a measured zero. The useful distinction is between an observation, an inference supported by it, and an unanswered question. The session remains read-only, with no manual queries or changes; missing access stays BLOCKED rather than prompting broader permissions.
-->

---

# Where the answer comes from

<figure>
<img class="diagram" src="../../diagrams/07-sre-agent-architecture.svg" width="1152" height="408" alt="SRE Agent workshop architecture: human chat starts with the main agent. Explicitly selected custom triage delegates to the AKS specialist, receives evidence, then requests analyst synthesis and owns the final response. Skills, knowledge and approved tools remain distinct; read-only policy, identity, authorization and network bounds apply independently of Review." />
<figcaption>Workshop logical architecture, focused from the full diagram. Configured intent, not runtime proof.</figcaption>
</figure>

<p class="sources"><a href="../../diagrams/sre-agent-architecture.svg">Full-size architecture</a> | <a href="../../exercises/sre-agent-architecture.md">Guide</a> | <a href="../../exercises/labs/03-observability.md">Lab 3</a></p>

<!--
TIME: 120 seconds.
This focused view explains where an agent answer comes from; it is a workshop logical architecture, not measured runtime topology or a replacement product architecture. The supplied main agent is the initial chat entry point. The custom workflow is a separate, explicitly selected entry point introduced in Lab 4: triage receives AKS specialist evidence, requests analyst synthesis and owns the final response. A human role call remains MANUAL HANDOVER unless native Task or supported handoff traces demonstrate automation. Skills provide procedures; knowledge provides retrieved references. Neither grants permission or proves loading. Each role has its own tools and connections, and the analyst reasons over returned evidence rather than needing every diagnostic tool. The actual execution identity, effective RBAC or data-plane authorization, network reachability and read-only tool policy are independent prerequisites. Grafana's identity differs from the agent identity; configuration authors and authorized change operators have other responsibilities. Review governs supported Azure infrastructure approvals, not every connector call or Kubernetes operation: it is not a universal gate. Lab 5 supplies runtime evidence for reads, retrieval, delegation and denials, with a separate correlated alert, thread and handler chain for conditional incident intake. Matching response plans stay paused with Review explicitly selected until acceptance. The full-size link contains the additional routes and identity detail; neither this diagram nor saved settings proves execution.
-->