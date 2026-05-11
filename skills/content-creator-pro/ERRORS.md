# ERRORS.md — Content Creator Pro Error Log

> Auto-maintained by content-creator-pro.
> Each error is logged with date, type, action taken, and resolution.
> Review weekly alongside LEARNINGS.md.

---

## Format

```
[YYYY-MM-DD] ERROR_TYPE
  Description: what happened
  Action taken: what the agent did
  Resolution: resolved / workaround / pending
```

---

## Error Log

<!-- Entries added automatically by content-creator-pro -->

---

## Error Types Reference

```
VOICE_MISSING        voice.md not found — created with defaults
CALENDAR_EMPTY       No slot found for today — fallback used
AI_PATTERN_DETECTED  Post failed human writing checklist — rewritten
PERFORMANCE_CORRUPT  performance.json unreadable — rebuilt from library/
QUEUE_ORPHAN         Post in queue with no matching calendar slot
REPURPOSE_FAILED     Source post not found in library/ for repurposing
```

---

## Resolution Status

| Status | Meaning |
|---|---|
| resolved | Fixed and confirmed working |
| workaround | Temporary fix applied — needs proper fix |
| pending | Not yet resolved |
