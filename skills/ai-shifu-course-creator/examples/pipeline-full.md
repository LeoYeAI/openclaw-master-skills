# Full Pipeline Example (Phase 1 → 2 → 3 → 4)

## Input Payload (example)

```json
{
  "course_material": "Module transcript: observe metric drift, classify causes, apply one fix, review impact.",
  "generation_constraints": {
    "persona": "practical coach",
    "lesson_granularity": "short"
  },
  "course_profile": {
    "audience_level": "beginner",
    "lesson_duration_minutes": 10,
    "lesson_count_target": 3,
    "assessment_mode": "project"
  },
  "delivery_constraints": {
    "interaction_density": "medium",
    "must_cover_topics": ["diagnosis", "verification"]
  },
  "target_language": "en-US"
}
```

## Phase 1 Output (Segmentation)

```json
{
  "structured_segments_json": [
    {
      "segment_id": "S01",
      "segment_type": "concept",
      "core_point": "Metric drift signals a systemic shift, not just noise.",
      "preserve_block": "no",
      "source_span": {"start": 0, "end": 42}
    },
    {
      "segment_id": "S02",
      "segment_type": "concept",
      "core_point": "Classify causes before applying fixes.",
      "preserve_block": "no",
      "source_span": {"start": 43, "end": 78}
    }
  ],
  "preserve_block_index": [],
  "lesson_cut_candidates": [
    {
      "lesson_id": "L01",
      "segment_ids": ["S01", "S02"],
      "core_question": "Which signal separates symptom from root cause?"
    }
  ]
}
```

## Phase 2 + 3 Output (Orchestration + Generation)

```json
{
  "course_index": [
    {
      "lesson_id": "L01",
      "lesson_title": "Observe and Classify",
      "core_question": "Which signal separates symptom from root cause?",
      "source_span_map": [{"source_id": "course_material", "start": 0, "end": 78}]
    }
  ],
  "global_variable_table": [
    {
      "name": "diagnosis_choice",
      "collected_in": "L01",
      "used_in": ["L01", "L02"],
      "effect_scope": "cross_lesson"
    }
  ]
}
```

```md
## L01 Objective
Identify the highest-signal diagnostic step.
---
?[%{{diagnosis_choice}} check workload shape | check lock wait | check cache hit ratio]
---
Based on {{diagnosis_choice}}, we run one focused verification next.
```

## Phase 4 Output (Optimization)

```json
{
  "risk_and_issue_report": {
    "overall_risk": "low",
    "blocking_issues": [],
    "suggestions": ["add boundary framing after diagnosis interaction"]
  },
  "change_list": [
    {
      "issue_class": "explanation_clarity",
      "change": "add brief boundary note after diagnosis selection"
    }
  ]
}
```

## Acceptance Notes

- All four phases executed end-to-end.
- One core question per lesson, variables collected before use.
- Optimization pass found no blockers, only enhancement suggestions.
