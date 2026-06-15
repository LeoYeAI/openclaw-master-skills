# Event & Rule Formats

## Event Format

```json
{
  "ts": "ISO-8601 timestamp",
  "type": "mistake|success|debug_session|feedback|discovery",
  "category": "shell|auth|memory|cron|social|communication|config|...",
  "tags": ["searchable", "tags", "for", "clustering"],
  "problem": "What went wrong or what was attempted",
  "solution": "What fixed it or what was learned",
  "confidence": "testing|proven",
  "source": "Where this happened (session, cron, skill-build, etc.)",
  "greg_feedback": "Optional: exact quote from human if feedback event"
}
```

## Rule Format (v1.4.0)

```json
{
  "id": "R-001",
  "type": "MUST|NEVER|PREFER|CHECK",
  "category": "Category matching event categories",
  "rule": "The behavioral constraint in plain language",
  "reason": "Why this rule exists",
  "created": "YYYY-MM-DD",
  "source_lesson": "L-XXX (traceability)",
  "violations": 0,
  "last_checked": "YYYY-MM-DD",
  "last_validated": "YYYY-MM-DD",      // NEW in v1.4.0
  "validation_count": 0,               // NEW in v1.4.0
  "confidence_score": 0.9,             // NEW in v1.4.0
  "review_flagged": false              // NEW in v1.4.0
}
```

**Rule types:**
- **MUST** - Always do this. Non-negotiable.
- **NEVER** - Never do this. Hard stop.
- **PREFER** - Default unless specific reason not to.
- **CHECK** - Verify before proceeding.

**Confidence Score (v1.4.0):**
- Range: 0.0 to 1.0
- Default for new rules: 0.9
- Decays over time via `confidence-decay.sh`
- Rules below 0.5 are flagged for review
- Validating a rule resets confidence to 0.9

**Validation Fields (v1.4.0):**
- `last_validated` - Date of last successful validation
- `validation_count` - Number of times rule has been validated
- Used by confidence decay algorithm

## Lesson Format (v1.4.0)

```json
{
  "id": "L-001",
  "created": "YYYY-MM-DD",
  "category": "shell|auth|memory|...",
  "subcategory": "optional sub-category",
  "lesson": "The lesson text",
  "context": "Background information",
  "trigger": "What triggers this lesson",
  "action": "What to do",
  "confidence": "testing|proven",
  "confidence_score": 0.9,          // NEW in v1.4.0 (numeric)
  "times_applied": 0,
  "times_saved": 0,
  "promoted_to_rule": "R-001",      // Filled when promoted
  "source_events": ["timestamp"],
  "last_validated": "YYYY-MM-DD",   // NEW in v1.4.0
  "validation_count": 0,            // NEW in v1.4.0
  "review_flagged": false           // NEW in v1.4.0
}
```

## Parse Error Format (v1.4.0)

Errors from JSON parsing are logged to `parse-errors.jsonl`:

```json
{
  "ts": "2026-02-11T10:30:00",
  "error": "Expecting property name enclosed in double quotes",
  "line": "{bad json here...}",
  "script": "detect-patterns.sh"
}
```

## Export Format (v1.4.0)

Rules exported via `export-rules.sh` use this format:

```json
{
  "metadata": {
    "export_version": "1.4.0",
    "export_format": "learning-loop-rules",
    "agent_handle": "agent-name",
    "exported_at": "2026-02-11T10:30:00Z",
    "source_workspace": "/path/to/workspace",
    "filter_applied": false,
    "filter_category": null,
    "total_rules_in_source": 25,
    "exported_rules_count": 25,
    "manifest_hash": "a1b2c3d4"
  },
  "statistics": {
    "categories": {"shell": 5, "auth": 3, "memory": 4},
    "rule_types": {"MUST": 10, "NEVER": 8, "PREFER": 5, "CHECK": 2},
    "avg_confidence": 0.85
  },
  "rules": [
    {
      "id": "R-001",
      "type": "MUST",
      "category": "memory",
      "rule": "...",
      "reason": "...",
      "created": "2026-02-01",
      "source_lesson": "L-001",
      "confidence_score": 0.9,
      "last_validated": "2026-02-01",
      "validation_count": 0,
      "_hash": "e5f6g7h8",              // Integrity hash
      "_original_id": "R-001"          // ID in source agent
    }
  ]
}
```

## Metrics Format

```json
{
  "version": "1.4.0",
  "started": "2026-02-01",
  "weekly": [
    {
      "week": "2026-W06",
      "generated": "2026-02-11T10:30:00",
      "events": {
        "total": 15,
        "mistakes": 2,
        "successes": 8,
        "debug_sessions": 3,
        "feedback": 2,
        "discoveries": 0
      },
      "regressions": 0,
      "rules_active": 12,
      "lessons_total": 18,
      "lessons_promoted": 10,
      "total_violations": 3,
      "satisfaction": 0.75
    }
  ],
  "totals": {
    "events": 150,
    "lessons": 25,
    "rules": 12,
    "total_violations": 15,
    "total_saves": 42,
    "total_applied": 68,
    "promoted": 10
  }
}
```

## Guard Log Format

```json
{
  "id": "g-103052-a1b2c3",
  "ts": "2026-02-11T10:30:52Z",
  "action": "post to moltbook",
  "matched_rules": ["R-020", "R-022"],
  "scores": {"R-020": 0.85, "R-022": 0.72},
  "save_logged": true,
  "outcome": "success"
}
```
