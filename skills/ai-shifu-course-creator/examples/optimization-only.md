# Optimization Only Example (Phase 4)

## Minimal Input

```json
{
  "existing_mdf_script": "## Objective\nUnderstand retry policy.\n---\n?[%{{answer}} yes | no]\n---\nGreat job.",
  "course_material": "Learner must differentiate transient vs permanent failure and choose a matching retry stop rule.",
  "optimization_constraints": {
    "max_interactions": 4,
    "require_branching_feedback": true
  },
  "course_profile": {
    "audience_level": "beginner"
  }
}
```

## Output Snapshot

```json
{
  "risk_and_issue_report": {
    "overall_risk": "medium",
    "blocking_issues": ["interaction_no_branching"],
    "suggestions": ["add explicit stop-condition task"]
  },
  "change_list": [
    {
      "issue_class": "interaction_no_branching",
      "change": "branch feedback by learner option and add next-step action"
    }
  ]
}
```

```md
## Objective
Differentiate transient and permanent failures before choosing retry policy.
---
?[%{{failure_type}} transient failure | permanent failure]
---
If {{failure_type}} is transient, apply bounded retries with backoff.
If {{failure_type}} is permanent, stop retries and open a corrective task.
```

## Edge Case: Missing Source Material

```json
{
  "existing_mdf_script": "## Goal\nPick a fix.\n---\n?[%{{fix_choice}} option A | option B]\n---\n?[%{{choose_fix}} option A | option B]\n---\nUse {{unknown_variable}} now.",
  "course_material": "",
  "optimization_constraints": {
    "fallback_mode": true,
    "minimize_scope": true
  },
  "delivery_constraints": {
    "platform_limits": ["markdown_only"]
  }
}
```

```json
{
  "risk_and_issue_report": {
    "overall_risk": "high",
    "blocking_issues": [
      "variable_or_syntax_risk",
      "semantic_duplicate_interactions"
    ],
    "coverage_status": "unknown_without_source"
  },
  "change_list": [
    {
      "issue_class": "variable_or_syntax_risk",
      "change": "remove unknown variable reference and keep one canonical interaction variable"
    }
  ],
  "follow_up": [
    "Provide source material for full coverage and meaning audit."
  ]
}
```

```md
## Goal
Pick one safe first fix.
---
?[%{{fix_choice}} option A | option B]
---
You selected {{fix_choice}}. Apply one verification step before rollout.
```

## Acceptance Notes

- Syntax stays runnable after edits.
- Coverage and meaning are closer to source material.
- Runtime safety fixes are applied first.
- Missing-source uncertainty is explicit in the report.
- Edits stay minimal and avoid broad rewrites.
