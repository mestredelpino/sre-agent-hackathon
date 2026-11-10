---
marp: true
theme: default
size: 16:9
paginate: true
title: Lab 3 - Observability
description: A brief introduction to the observability lab.
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
  .diagram { display: block; width: 960px; height: 340px; object-fit: contain; margin: 0 auto; }
  figcaption { margin-top: 12px; font-size: 20px; color: #605e5c; }
  .sources { margin-top: 12px; font-size: 20px; }
  @media print { section { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
---

# Lab 3: Observability

Understand the health of the supplied Store through its telemetry.

<figure>
<img class="diagram" src="../../diagrams/07-sre-agent-architecture.svg" width="1152" height="408" alt="SRE Agent workshop architecture: human chat starts with the main agent. Explicitly selected custom triage delegates to the AKS specialist, receives evidence, then requests analyst synthesis and owns the final response. Skills, knowledge and approved tools remain distinct; read-only policy, identity, authorization and network bounds apply independently of Review." />
<figcaption>The telemetry baseline supports the agent investigations in later labs.</figcaption>
</figure>

<p class="sources"><a href="../../exercises/labs/03-observability.md">Lab 3 guide</a></p>

<!--
TIME: 30 seconds.
This lab introduces the observability available for the already-deployed Store. Its purpose is to build a shared understanding of application health before the agent is created in Lab 4. The image places that baseline in the wider workshop context; it is not a claim that an agent is already running. All activities and detailed guidance are in the linked lab guide.
-->