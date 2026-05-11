# ADR-010: Smart Session Trim

**Status:** Proposed
**Date:** 2026-03-22
**Author:** CyberClaw
**Triggered by:** Real-world context loss in creative agent sessions (Ray/Music), user feedback from multiple OpenClaw users

## Context

OpenClaw does not trim sessions by default — sessions grow until the model's context window is full, then the API silently drops oldest messages. This is by design: OpenClaw can't know what the user considers important.

We built a custom trim system (3 cron jobs, safe-trim.py, graceful-session-end.py) that cuts sessions to 60 lines on schedule. This solves token costs but creates a worse problem: **blind context loss**. The trim has no awareness of what's been captured to persistent memory and what hasn't.

### The Problem (real incident, 2026-03-22)

Ray (music agent) was co-writing lyrics with Christian. After ~30 messages of iterative work, the session was trimmed to 60 lines. Ray lost the "1st anchor" — a hook line he had written himself, just a few messages earlier. Christian had to re-explain Ray's own work to Ray. Quote: "Das ist gerade sehr mühsam mit Dir zu arbeiten."

Root causes:
1. **Trim is Palaia-unaware** — cuts without checking if content is captured
2. **Auto-Capture misses creative work** — significance tags (decision, lesson, fact...) don't cover iterative creative output (drafts, lyrics, design iterations)
3. **Agent didn't save manually** — Ray admitted "Ich habe den Kontext verloren — schlicht vergessen"
4. **Images are irretrievably lost** — screenshots in trimmed sessions are marked "omitted"

### Current State

- 3 uncoordinated trim mechanisms (Nightly Step 4, 6h trim job, TARS heartbeat)
- All blind — no Palaia integration
- Learnings hardcoded in cron job prompts (trim at user-message boundary, never mid-tool-call)
- No per-agent or per-channel configuration

## Decision

Replace all custom trim logic with a Palaia-managed `before_session_trim` hook in the OpenClaw plugin, analogous to existing hooks:

| Hook | When | Purpose |
|------|------|---------|
| `before_prompt_build` | Before each LLM call | Auto-Recall |
| `agent_end` | After each agent turn | Auto-Capture |
| **`before_session_trim`** | **Before session truncation** | **Delta-Capture + Safe Trim** |

## Design

### 1. Trim Modes (configurable per agent/channel)

```json
{
  "plugins": {
    "entries": {
      "palaia": {
        "config": {
          "sessionTrim": {
            "mode": "smart",
            "maxLines": 120,
            "inactivityMinutes": 360
          }
        }
      }
    }
  }
}
```

| Mode | Behavior |
|------|----------|
| `"off"` | No trimming (OpenClaw default behavior) |
| `"fixed"` | Trim to `maxLines` after `inactivityMinutes` — no capture, backward-compatible |
| `"smart"` | **Default.** Delta-capture unsaved content, then trim to `maxLines` |

### 2. Delta-Capture (the core innovation)

The `before_session_trim` hook:

1. **Reads the last capture marker** — a timestamp/index stored per session marking the last successful Auto-Capture point
2. **Identifies delta messages** — everything between last-capture-marker and trim-point
3. **Checks for uncaptured significant content** in the delta using the same LLM extraction as Auto-Capture
4. **Captures only the delta** — never re-captures already-saved content
5. **Updates the capture marker** after successful capture
6. **Proceeds with trim** regardless of capture success (no hangs)

### 3. Dedup Gate (critical — prevents store explosion)

The #1 risk is duplicate entries. Three safeguards:

- **Capture marker**: Only content after the last capture point is examined
- **Content hash check**: Before writing, check existing entries for similarity (score > 0.8, same session, last 24h)
- **Idempotency**: If `before_session_trim` runs twice on the same content, the second run is a no-op (marker already advanced)

### 4. Trim Safety Rules (codified learnings)

Hard rules from our production experience:

- Never cut mid-tool-call (check last message role/type)
- Never start at a thinking block
- Always start at a user-message boundary
- Create .bak backup before every trim
- Never trim sessions active in last N minutes (configurable, default: 360)
- Log trim event with before/after line count

### 5. No-Hang Guarantee

```
trim_timeout = 10s (configurable)

try:
    delta_capture(session, timeout=trim_timeout)
except Timeout:
    log.warn("Delta capture timed out, proceeding with trim")
    
# Trim always executes, even if capture failed
execute_trim(session)
```

### 6. Significance Tags Extension

New tags for creative/iterative work:

| Tag | Pattern | Example |
|-----|---------|---------|
| `draft` | Iterative versions, options A/B | "Option A: ..." / "Variante 1: ..." |
| `artifact` | Named creative outputs | "1. Anker: ..." / "Hook: ..." |
| `iteration` | Refinement of previous output | "Überarbeitet: ..." / "v2: ..." |

These supplement existing tags (decision, lesson, fact...) and improve Auto-Capture coverage for creative workflows.

## Migration

1. New Palaia plugin version with `before_session_trim` hook
2. OpenClaw needs to call this hook before any session truncation (requires upstream hook point — or we implement trim inside the plugin itself)
3. Remove custom trim cron jobs (d5f472ca Step 4, 73bb606f, TARS heartbeat trim tasks)
4. Document trim config in SKILL.md

## Alternative: Plugin-internal trim

If OpenClaw doesn't expose a `before_session_trim` hook, the plugin can implement trim internally:
- Monitor session file sizes via `agent_end` hook (already fires after every turn)
- When session exceeds threshold: delta-capture + trim in the same hook invocation
- Advantage: No OpenClaw upstream change needed
- Disadvantage: Trim only happens after agent turns, not on schedule

## Risks

- **Store explosion from bad dedup**: Mitigated by capture marker + hash check + 24h window
- **Trim hangs**: Mitigated by hard timeout + trim-always-executes
- **Lost images**: Images in trimmed content are still lost — Palaia stores text, not binary. Future: image description capture before trim.
- **LLM cost**: Delta-capture uses the same cheap model as Auto-Capture (captureModel config). Minimal per-trim.

## Success Criteria

- Zero "I lost context" incidents after deployment
- No duplicate entries from trim-capture (measurable via `palaia list --tags auto-capture` dedup rate)
- Token cost reduction vs. untrimmed sessions (measurable via session token tracking)
- Ray can continue a lyrics session across trims without context loss
