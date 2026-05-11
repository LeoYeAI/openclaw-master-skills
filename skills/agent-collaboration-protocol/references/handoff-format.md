# Handoff Message Format

Use this template when spawning or messaging agents. Include ALL fields.

```
## Handoff: {Title}

**What:** {Specific task or deliverable — one sentence}

**Why:** {Context and priority — why this is needed now}

**Files:**
- `shared/build-{YYYYMMDD}/backend/router.py` — route handler
- `shared/build-{YYYYMMDD}/SPEC.md` — API contract

**Success criteria:** {Observable behavior — how we know it's done}

**ETA:** {YYYY-MM-DD HH:MM UTC}
```

## After Handoff

1. Verify agent acknowledges within 5 minutes
2. Check T+30min: Did they start? Files modified?
3. Check T+2hr: Progress? Blockers?
4. If no progress by ETA: mark STALE, alert orchestrator
