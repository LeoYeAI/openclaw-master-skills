# Reference Draft — Freshness Discipline

Status: draft-for-skill
Role: stable maintenance reference

## Purpose

Define how a workspace should keep its most important state/truth files fresh without trying to keep everything equally live.

The goal is not “update all docs.”
The goal is “keep the smallest important set fresh enough that drift becomes visible before it becomes dangerous.”

---

## Core Principle

Freshness discipline is about **controlled attention**.

A workspace should maintain a narrow working set of high-leverage files instead of pretending every document is equally current.

---

## Working Set Concept

A working set is the minimum set of files that must remain fresh for the workspace to answer ordinary current-state, maintenance, and routing questions well.

Typical working-set members:
- health / consistency files
- bridge/current-state files
- runtime snapshot
- entrypoint/index docs
- only the highest-value topic cards

Everything outside the working set should default to:
- historical/background
- needs-refresh
- or on-demand reference only

---

## Threshold Discipline

Do not use one blanket threshold for all files.

Example grouped thresholds:
- short threshold for health / bridge / runtime / entry docs
- longer threshold for structured topic/index docs

Reason:
- some files answer “what is true now?” and should age quickly
- others organize medium-durability context and can age more slowly without becoming misleading immediately

---

## Refresh Order

When time or attention is limited, refresh in this order:
1. health / consistency
2. bridge/current-state files
3. runtime snapshot
4. entry/index docs
5. topic cards
6. explanation/background docs

This keeps the truth chain alive before polishing context layers.

---

## Stale Triggers

Refresh immediately if:
- a governance/routing answer would differ from the current docs
- a current-state answer would be misleading from the existing bridge files
- runtime snapshot no longer matches current runtime reality
- a topic card appears fresher or more current than the actual bridge/health truth

---

## Low-Noise Check Principle

A freshness checker should:
- stay quiet when nothing needs action
- report only warned files when drift exists
- report age vs threshold clearly
- avoid long essays on healthy runs

The point is to create signal, not another source of noise.

---

## Human vs Automation Boundary

Freshness checks can be automated.

Freshness repair does not need to be fully automated in v1.

A valid v1 pattern is:
- the checker detects drift
- the operator/agent decides how to refresh the affected files

This still counts as a successful maintenance system, because it makes drift visible and routable.

---

## Minimal Live Subset

A working set can still be too large.

A workspace should define a **preferred minimal live subset** for everyday maintenance.
This subset should be just large enough to answer ordinary status/maintenance questions without reopening the full docs forest.

---

## Validation Rule

Do not assume a smaller live subset is good just because it is smaller.

Validate it against real questions such as:
- what is the system state now?
- what should be maintained first?
- which docs are still live?
- what is the current retrieval posture?

If the smaller subset answers these well enough, keep it.
If not, expand carefully.

---

## Maintenance Mode

Once the mainline upgrade work is complete enough to close:
- stop expanding the process docs
- keep the working set fresh
- observe recurring checks
- make only small refinements when the checks reveal real drift

This is maintenance observation mode.

---

## v1 Boundary

This reference defines freshness discipline and maintenance behavior.
It does not require fully automatic bridge rewriting or universal self-healing.

The first win is:
- define the working set
- define thresholds
- run checks repeatedly
- keep the live surface small
