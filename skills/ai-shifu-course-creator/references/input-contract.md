# Input Contract

## Required

Provide one of:
- A single long transcript or course document.
- A set of topic-aligned documents with intended order.

## Optional

- Learner persona.
- Lesson granularity preference (`short`, `medium`, `long`).
- Terminology and tone constraints.
- Non-negotiable source fragments.
- `course_profile` object.
- `delivery_constraints` object.
- `target_language` (BCP-47 recommended, for example `fr-FR`, `ja-JP`, `zh-CN`).
- `bilingual_output` (`true|false`).
- `term_policy` (`preserve|translate|mixed`).
- `quote_policy` (`translate_only|original_plus_translation`).

## Recommended Object Shapes

### `course_profile`

```json
{
  "audience_level": "beginner|intermediate|advanced",
  "prerequisite_level": "none|basic|strong",
  "lesson_duration_minutes": 12,
  "lesson_count_target": 8,
  "assessment_mode": "quiz|project|discussion|mixed"
}
```

### `delivery_constraints`

```json
{
  "interaction_density": "low|medium|high",
  "platform_limits": ["no_iframe", "markdown_only"],
  "must_cover_topics": ["topic-a", "topic-b"],
  "avoid_topics": ["topic-x"],
  "non_negotiable_fragments": ["exact quote or code block id"]
}
```

## Minimal Input Payload Example

```json
{
  "course_material": "long transcript or merged markdown",
  "generation_constraints": {
    "persona": "hands-on mentor",
    "lesson_granularity": "short"
  },
  "course_profile": {
    "audience_level": "beginner",
    "lesson_duration_minutes": 10,
    "lesson_count_target": 6,
    "assessment_mode": "project"
  },
  "delivery_constraints": {
    "interaction_density": "medium",
    "must_cover_topics": ["core workflow", "failure handling"]
  }
}
```

## Language Resolution Priority

If language signals conflict, resolve with this strict order:
1. explicit output language request
2. `target_language` parameter
3. session language preference
4. prompt language detection
5. source-material dominant language
6. default fallback language (`en-US`)

## Validation Rules

- Input files must be readable text or markdown.
- If multiple files are provided, ordering must be explicit.
- Source language and expected output language should be specified when multilingual content exists.
- Explicit output language requests must not be overridden by source-language mixes.
