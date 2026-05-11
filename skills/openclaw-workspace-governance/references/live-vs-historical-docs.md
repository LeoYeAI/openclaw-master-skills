# Reference Draft — Live vs Historical Docs

Status: draft-for-skill
Role: stable doc-governance reference for live/current vs historical/background boundaries

## Scope

Use this reference when a workspace has:
- too many docs that look current at the same time
- old plans, audits, or phase summaries competing with current bridge files
- no clear rule for which docs must stay maintained
- special-case safety docs that should not be casually downgraded

This reference is for:
- separating live maintenance docs from historical/background docs
- bounding the authority of partially stale docs
- defining a minimal live subset
- handling special-case active safety docs separately
- making doc status labeling repeatable

## Non-goals

This reference does **not**:
- automate all status changes
- decide truth by filename age alone
- replace source-of-truth layering
- automatically archive or delete documents

It exists to make doc authority clearer, not to remove human judgment.

## Purpose

Define how a workspace should separate:
- active maintenance docs
- historical/background docs
- stale-but-still-useful docs
- special-case docs that should not be casually downgraded

The goal is to stop old docs from silently acting as current truth.

---

## Core Principle

Not every document should remain live.

A workspace becomes harder to trust when:
- too many docs look current
- old plans and audits compete with current bridge files
- no one knows which docs are supposed to be maintained

The fix is not "rewrite everything."
The fix is to define which docs stay live, which become historical, and which need explicit authority limits.

---

## Quick Start

Use this reference in five steps:
1. classify the doc role
2. decide whether it belongs in the live subset
3. assign a status label or special-case handling
4. define its use rule
5. confirm it does not outrank fresher/current sources by accident

If a doc can mislead current-state answers when read alone, it should not remain an unlabeled live default.

---

## Main Doc Roles

### 1. Active maintenance docs
These are docs that should remain current because they directly support ordinary operation.

Typical examples:
- health/consistency docs
- bridge/current-state docs
- current runtime/entrypoint/index docs
- working set / refresh rule docs

Properties:
- small in number
- regularly refreshed
- used in ordinary maintenance and status answers

Use rule:
- these docs may participate in the default live subset
- they should be maintained on purpose, not merely left behind from earlier phases

---

### 2. Historical-reference docs
These preserve value for:
- background
- traceability
- prior decisions
- earlier phase context

But they should not silently compete as the current authority.

Typical examples:
- old plans
- prior audits
- phase summaries
- older role docs
- archived analyses

Use rule:
- preserve for context and evidence
- do not use as the primary current-state source unless no fresher current layer exists

---

### 3. Needs-refresh docs
These are docs that still have practical value but are no longer trustworthy enough to act as unquestioned current truth.

Use this when a doc is:
- still useful
- partially outdated
- likely to mislead if read alone

This label says:
- keep the doc
- bound its authority
- do not let it outrank fresher/current sources

Use rule:
- support material only until refreshed
- do not treat as self-sufficient current truth

---

### 4. Special-case active safety docs
Some docs are not ordinary explanation/background docs.

Examples:
- safety restriction docs
- service-lifecycle restriction docs
- hard operational boundary docs

These should not be casually downgraded into historical/background labels just because they are not updated often.

Treat them as a separate category with explicit caution.

Use rule:
- treat as active restriction material
- classify through special-case policy rather than ordinary docs cleanup rules

---

## Recommended Status Labels

Recommended public labels:
- `historical-reference`
- `needs-refresh`
- active/live maintenance docs (may be managed as a known set rather than a literal in-file status string)
- `special-case active safety restriction`

Important:
- labels are not decorative
- they exist to prevent authority confusion
- unlabeled docs should not automatically be treated as live authority

---

## Minimal Live Subset

A workspace should keep its active maintenance docs as small as possible.

The preferred minimal live subset should be just large enough to answer:
- current system-state
- maintenance priorities
- retrieval posture
- current live-vs-historical boundaries

If a doc is not needed for those ordinary questions, it probably should not stay in the default live set.

A good minimal live subset is:
- intentionally maintained
- small enough to review regularly
- strong enough to answer common operational questions without dragging old phase docs back into the default path

---

## Labeling Rules

### Mark `historical-reference` when:
- the doc mainly preserves prior reasoning or history
- a fresher/current layer now exists for its topic
- keeping it live adds confusion more than operational value
- it remains useful for traceability but should not lead current-state answers

### Mark `needs-refresh` when:
- the doc still has practical value
- but reading it alone would likely mislead someone
- parts remain useful, but the whole doc is not current enough to stand as current authority

### Keep in the live subset when:
- the doc is actively maintained
- the doc is needed for ordinary maintenance or status work
- removing it from the live subset would make current-state answers weaker

### Route to special-case handling when:
- the doc is an active safety restriction or hard operational boundary
- downgrading it casually would create risk
- its authority comes from safety function, not from being a general explanation layer doc

---

## Validation Rule

A live-vs-historical model is working if:
- users/operators can tell which docs are still live
- old docs stop hijacking current-state answers
- the default maintenance surface gets smaller
- historical docs remain available without masquerading as current truth
- special-case safety docs remain visible without being forced into the wrong label bucket

---

## Precedence and Conflict Handling

This reference defines doc-governance defaults.

Conflict order:
1. explicit local safety and approval rules
2. source-of-truth layering and current-state rules
3. this reference as default doc-status guidance

Never use a historical or needs-refresh doc to override a fresher live source just because the older doc is more detailed.

---

## Minimal Examples

### Example 1 — Old implementation plan
Situation:
- a phase-1 implementation plan is still informative
- newer bridge/current-state docs now exist

Decision:
- mark it `historical-reference`
- keep it for background and traceability
- do not let it answer "what is true now?"

### Example 2 — Useful but partially stale manual
Situation:
- an execution manual still explains major steps correctly
- some runtime assumptions are outdated

Decision:
- mark it `needs-refresh`
- keep it as support material
- require operators to defer to fresher current-state docs for active behavior

### Example 3 — Current health file
Situation:
- a small health summary is updated regularly and used in ordinary maintenance

Decision:
- keep it in the live subset
- treat it as a current maintenance doc
- do not bury it under older, longer design docs

### Example 4 — Service-lifecycle restriction doc
Situation:
- a safety restriction doc is rarely edited but still actively governs dangerous actions

Decision:
- classify it as `special-case active safety restriction`
- do not downgrade it through normal historical cleanup
- keep its authority explicit

---

## v1 Boundary

This reference defines the separation model.
It does not automate every status label change.

The first release goal is to make the live/historical boundary explicit, repeatable, and small enough to maintain.
