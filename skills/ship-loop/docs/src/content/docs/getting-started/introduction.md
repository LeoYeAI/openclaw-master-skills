---
title: Introduction
description: What Ship Loop is and why it exists
---

Ship Loop is a self-healing build pipeline for AI coding agents. You define features as segments, point Ship Loop at your coding agent (Claude Code, Codex, Aider, or any CLI), and it builds, tests, deploys, and verifies each one autonomously.

When something breaks, it fixes itself. When fixes stall, it tries alternative approaches. It learns from every failure and feeds those lessons into future runs.

## The Problem

AI coding agents are good at writing code. They're terrible at shipping it. The typical workflow looks like:

1. Agent writes code ✅
2. You run the build... it fails ❌
3. You paste the error back to the agent
4. Agent fixes it, introduces a new bug
5. Repeat 3-7 times
6. You give up and fix it yourself

This doesn't scale. If you want to ship 10 features overnight, you need something that handles the failure loop automatically.

## The Solution

Ship Loop wraps your coding agent in three nested loops:

- **Loop 1 (Ship):** The happy path. Agent codes, preflight checks pass, code gets committed, pushed, and deploy-verified.
- **Loop 2 (Repair):** When preflight fails, Ship Loop captures the error context and asks the agent to fix it. Up to N attempts with convergence detection.
- **Loop 3 (Meta):** When repairs stall, Ship Loop runs a meta-analysis, spawns N experiment branches in git worktrees, and picks the simplest passing solution.

A **learnings engine** records every failure-then-fix cycle and injects relevant lessons into future agent prompts. A **budget tracker** monitors token usage so you don't wake up to a $200 bill.

## Who It's For

- Developers using AI coding agents who want to ship features autonomously
- Teams running overnight or CI-triggered coding pipelines
- Anyone tired of babysitting agent output

## Background

Ship Loop's architecture was designed from engineering intuition about how coding pipelines fail. Meta's [Hyperagents](https://arxiv.org/abs/2603.19461) research (March 2026) independently validated this approach: their self-improving agents autonomously invented persistent memory, performance tracking, and experiment branching, the same patterns Ship Loop uses.
