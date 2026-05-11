# Reference Draft — Source of Truth Layering

Status: draft-for-skill
Role: stable governance reference

## Purpose

Define how an OpenClaw workspace should decide which layer wins when current-state files, governance docs, memory layers, snapshots, and historical docs disagree.

The goal is not to average sources.
The goal is to route by layer and let the right layer win.

---

## Core Rule

When two layers disagree, do not merge them by intuition.

First decide:
1. what kind of fact is being asked for
2. which layer is supposed to answer that fact type
3. whether the “more current” layer or the “more authoritative” layer should win

---

## Main Layers

### 1. Canon
Use for:
- governance rules
- approval requirements
- hard safety boundaries
- formal role/responsibility definitions

Examples:
- workspace rules
- routing/governance canon
- safety restriction docs

Canon wins for:
- rule-boundary questions
- approval questions
- responsibility questions

---

### 2. Bridge / current-state layer
Use for:
- “what is true now?”
- current system posture
- current retrieval behavior
- current maintenance state

Bridge wins for:
- current-state questions
- operational status questions
- current maintenance posture

Important:
- bridge files are allowed to be narrower and more frequently updated than deeper memory layers

---

### 3. Health / consistency layer
Use for:
- health state
- consistency state
- risk posture
- degraded/improving domains

Health/consistency files often refine the bridge layer by giving explicit condition labels.

---

### 4. Runtime snapshot layer
Use for:
- current runtime/model/session arrangement
- runtime-specific point-in-time state

Snapshot wins when the question is specifically:
- how the system is currently running
- what runtime/model path is in use now

Snapshots do not override canon on rule questions.

---

### 5. Structured memory layer
Use for:
- topic cards
- topic index
- medium-durability context organization

Structured memory is useful for:
- historical framing
- recurring topic context
- discovery of likely context packs

Structured memory should not silently outrank fresher bridge/health/snapshot layers on current-state questions.

---

### 6. Long-term memory layer
Use for:
- durable facts that have proven stable over time
- persistent user/system facts that should survive many sessions

Long-term memory is not the right place to store fast-moving governance or current-state details too early.

---

### 7. Historical/background layer
Use for:
- old plans
- prior audits
- old manuals
- previous phase summaries
- archived explanations

Historical/background docs are valuable for traceability, but should not silently compete with live layers.

---

## Fact-Type Routing

### Governance / approval / role-boundary facts
Winner:
- Canon

Supporting layers:
- historical docs only for context
- long-term memory only as durable background

---

### Current system-state facts
Winner:
- Bridge + health/consistency

Supporting layers:
- runtime snapshot when runtime-specific detail is needed
- structured memory only later
- semantic search only in the role allowed by current query-class policy

---

### Runtime-now facts
Winner:
- Runtime snapshot

Supporting layers:
- bridge layer
- canon for boundary questions only

---

### Historical trace facts
Winner:
- discovered evidence + file-level verification

Supporting layers:
- structured memory for discovery
- semantic search for cross-file discovery
- long-term memory for durable implications only

---

### Preference / profile facts
Winner:
- curated profile/manual sources and durable memory

Supporting layers:
- structured memory and semantic search only as additional evidence

---

## Conflict Resolution

When there is conflict:

### Rule 1
Rule questions → canon beats everything else

### Rule 2
Current-state questions → fresh bridge/health beats older structured/long-term summaries

### Rule 3
Runtime-now questions → runtime snapshot beats older memory

### Rule 4
Historical questions → verify against underlying evidence before trusting summaries

### Rule 5
Do not let an unlabeled old doc pretend to be current truth

---

## Practical Anti-Drift Rule

A workspace should always know:
- what is live
- what is historical
- what is authoritative
- what is just supporting recall

If the workspace cannot answer those four questions, source-of-truth drift is already happening.

---

## Maintenance Rule

Whenever the system is upgraded or reorganized:
- refresh the bridge layer first
- refresh health/consistency next
- refresh snapshots if runtime changed
- refresh structured memory only where it overlaps heavily with current-state use
- promote to long-term memory only when facts prove durable

---

## v1 Boundary

This reference defines the layering model.
It does not automate all synchronization between layers.

That is intentional.

The first goal is to make the layering explicit and repeatable.
Automation can come later.
