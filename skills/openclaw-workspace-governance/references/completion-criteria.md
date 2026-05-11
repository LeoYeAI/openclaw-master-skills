# Reference Draft — Completion Criteria

Status: draft-for-skill
Role: stable closure reference for deciding when a governance/improvement stream is landed, improving, deferred, or complete enough to close

## Scope

Use this reference when a workspace improvement stream risks turning into:
- endless phase sprawl
- endless "just one more doc" behavior
- constant refinement without closure
- unclear distinction between landed work and future work

This reference is for:
- classifying work as landed / improving / deferred
- deciding when the mainline is complete enough to close
- shifting from active construction into maintenance observation
- keeping deferred work explicit without letting it block closure

## Non-goals

This reference does **not**:
- force a single universal checklist for every workspace
- require perfection before closure
- automatically archive or remove workstreams
- treat all unfinished items as blockers

It exists to make closure explicit, not to demand zero remaining future work.

## Purpose

Define when a workspace-governance improvement stream should be treated as:
- landed
- improving
- deferred
- complete enough to close

The goal is to stop endless phase sprawl and force explicit closure decisions.

---

## Core Principle

Do not keep a phase open just because some future refinement is imaginable.

A phase can be complete enough to close even when:
- some parts still need observation
- some future tuning remains possible
- some work is intentionally deferred

The key distinction is whether the remaining work is:
- missing core structure
or
- post-landing refinement and observation

---

## Quick Start

Use this reference in five steps:
1. classify the stream's major capabilities
2. mark each one as landed, improving, or deferred
3. test whether the mainline closure conditions are met
4. separate blocking gaps from non-blocking future work
5. record the closure decision and move into maintenance observation when justified

If the remaining work is mostly tuning, observation, or explicit deferral, do not keep the whole phase artificially open.

---

## Completion Levels

### Level A — Landed
Use when:
- the capability exists
- it is wired into real operation
- it has survived at least one meaningful validation pass

Use rule:
- landed work belongs in the mainline result set
- landed does not mean "perfect forever"; it means operationally real and validated enough to count

---

### Level B — Improving
Use when:
- the capability exists and works
- but it still needs longer observation, repeated runs, or limited refinement

Use rule:
- improving work does not block mainline closure if core structure is already landed
- it should be tracked as observation/refinement, not as missing capability

---

### Level C — Deferred
Use when:
- the work is intentionally postponed
- doing it now would create sprawl, premature promotion, or poor signal

Use rule:
- deferred work must remain explicit
- deferred does not mean forgotten
- deferred work should not silently reopen a closed mainline unless it becomes necessary for core operation later

---

## Close-Mainline Criteria

A stream is complete enough to close its mainline when all of the following are true:
1. the main promised capabilities exist
2. those capabilities are connected into actual operation rather than only documentation
3. the most important paths have been validated at least once
4. the remaining open items are mostly observation, limited refinement, or explicit deferral
5. the workspace can shift into maintenance observation without needing another large construction burst immediately

If these conditions are met, the stream is ready to close even if some improving and deferred items remain.

---

## Blocking vs Non-blocking Work

### Blocking work
Treat as blocking when:
- a promised core capability is still missing
- the capability exists only on paper and is not wired into operation
- the main validation path has not been run at all
- unresolved issues still affect the stream's core claim

### Non-blocking work
Treat as non-blocking when:
- the main capability is landed but still being observed
- future tuning may improve signal/noise but is not required for operation
- broader expansion is intentionally deferred
- cleanup would be nice but does not change the mainline result

Without this distinction, every phase becomes endless pseudo-progress.

---

## Maintenance Observation

Once the mainline is complete enough to close:
- stop opening new process docs casually
- keep the live subset small
- monitor recurring checks
- make small refinements only when real drift, noise, or regression appears

Maintenance observation is not abandonment.
It is controlled continuation after mainline closure.

---

## Common Deferred Work

It is normal to defer work such as:
- long-term memory promotion
- large-scale topic-card rewrites
- broad migration/restructuring work
- fully automated versions of currently guided processes
- broader validation beyond the current high-value classes or paths

Deferred does not mean low value.
It means not worth destabilizing the mainline now.

---

## Closure Outputs

A clean closure should record:
- what is landed
- what is improving
- what is deferred
- why closure is justified now
- what remains in maintenance observation
- what would justify reopening the stream later

Closure should create a smaller, clearer state — not just a nicer way to avoid deciding.

---

## Validation Rule

A completion model is working if:
- core capabilities stop being relitigated after they are landed
- improving work is visible without blocking closure forever
- deferred work is explicit instead of leaking back into the mainline by accident
- the workspace can move from construction into maintenance observation without confusion

---

## Precedence and Conflict Handling

This reference governs closure discipline, not source-of-truth ranking.

Conflict order:
1. explicit local safety and approval rules
2. current governance and source-of-truth policy
3. this reference as default closure guidance

Do not use closure language to silently revoke rules, change authority boundaries, or erase still-live obligations.

---

## Minimal Examples

### Example 1 — Main capability landed, tuning remains
Situation:
- a freshness checker exists, is wired into operation, and passed a first validation run
- long-run threshold tuning may still improve later

Decision:
- mark checker as landed
- mark tuning as improving
- do not keep the whole stream open just for threshold tuning

### Example 2 — Broader expansion deferred
Situation:
- current high-value query classes are validated
- broader class coverage would be useful but is not required for current operation

Decision:
- mark current validated boundary as landed
- mark broader expansion as deferred or improving depending on intent
- close the mainline if the core promise is already met

### Example 3 — Capability exists only in docs
Situation:
- a governance process is described clearly
- but it is not yet used in real operation

Decision:
- do not mark as landed
- treat as blocking until it affects real operating behavior or receives a meaningful validation pass

### Example 4 — Stream ready for maintenance observation
Situation:
- live/current docs are reduced
- routing rules are established
- diagnostics exist and were validated at least once
- remaining work is observation and selective cleanup

Decision:
- close the mainline
- move into maintenance observation
- keep future cleanup explicit rather than reopening a broad construction phase

---

## v1 Boundary

This reference defines how to close phases cleanly.
It does not force one universal checklist for every workspace.

Use it to keep governance work finite, reviewable, and maintainable.
