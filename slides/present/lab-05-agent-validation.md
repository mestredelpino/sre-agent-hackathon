---
marp: true
theme: default
size: 16:9
paginate: true
title: Lab 5 - Agent Validation
description: A brief introduction to the agent validation lab.
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

# Lab 5: Agent Validation

<div class="question">From a configured agent to confidence in its behavior.</div>

This lab brings the agent from Lab 4 into the workshop environment.

Its purpose is to understand what the agent can reliably support before the
scaling lab and incident challenge.

<p class="small"><a href="../../exercises/labs/05-agent-validation.md">Lab 5 guide</a></p>

<!--
TIME: 30 seconds.
Lab 5 follows configuration on Day 1. Its purpose is to build confidence in the agent through its actual behavior, rather than through configuration alone. The outcome is a clearer understanding of the agent's usefulness and remaining limitations before the later workshop activities. This introduction does not define acceptance criteria or add tasks; the linked lab guide contains the validation sequence, evidence requirements and safety boundaries.
-->