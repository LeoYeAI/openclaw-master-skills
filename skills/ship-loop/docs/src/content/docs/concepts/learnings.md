---
title: Learnings Engine
description: How Ship Loop learns from failures
---

Every failure-then-fix cycle in Ship Loop creates a lesson. These lessons are stored in `learnings.yml` at the root of your project and automatically loaded into future agent prompts.

## How It Works

1. A segment fails preflight
2. The repair loop (or meta loop) eventually fixes it
3. Ship Loop records: what failed, the error signature, the root cause, and how it was fixed
4. On future runs, Ship Loop scores each learning against the current segment's prompt using keyword matching
5. Relevant learnings are prepended to the agent prompt

This means your pipeline gets smarter over time. The same class of error that took 3 repair attempts on the first run might be avoided entirely on the second.

## Learnings Format

```yaml
- id: L001
  date: "2026-03-23"
  segment: "dark-mode"
  error_signature: "abc123def456"
  failure: "Build failed: Cannot find module './ThemeToggle'"
  root_cause: "Component file was created but not exported from index"
  fix: "Added export to components/index.ts"
  tags: ["build", "import", "module", "component", "export"]
```

Each learning has:
- **id:** Auto-generated identifier
- **date:** When the failure occurred
- **segment:** Which segment triggered it
- **error_signature:** Hash of the error output (for dedup and convergence detection)
- **failure:** The actual error message
- **root_cause:** What caused it
- **fix:** How it was resolved
- **tags:** Keywords for matching against future prompts

## CLI Commands

```bash
# List all learnings
shiploop learnings list

# Search by keyword
shiploop learnings search "dark mode"
shiploop learnings search "lint import"
```

## Relevance Scoring

When loading learnings for a segment, Ship Loop scores each learning by counting keyword matches between the learning's tags/failure/fix text and the segment's prompt. Only learnings above a relevance threshold are included.

This prevents prompt bloat: a learning about CSS build errors won't be injected into a segment about API endpoints.

## Cross-Run Accumulation

Learnings persist across runs in `learnings.yml`. This file should be committed to your repo so the knowledge transfers across machines and CI environments.

```bash
git add learnings.yml
git commit -m "Add pipeline learnings"
```

## Inspired by Research

Meta's [Hyperagents](https://arxiv.org/abs/2603.19461) paper showed that self-improving AI agents independently invented persistent memory systems to store insights across generations. Ship Loop's learnings engine is the same pattern, built from engineering intuition before the research validated it.
