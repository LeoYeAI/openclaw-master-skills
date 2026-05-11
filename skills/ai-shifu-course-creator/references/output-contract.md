# Output Contract

## Required Artifacts

1. `lesson_mdf_scripts`
- One MarkdownFlow file per lesson.
- Learner-facing language only.

2. `course_index`
- `lesson_id`
- `lesson_title`
- `core_question`
- `source_span_map`

3. `global_variable_table`
- Variable name
- Collection point
- Downstream usage
- Cross-lesson dependencies

## Artifact Schemas

### `lesson_mdf_scripts` (array, required)

Each item:

- `lesson_id` (string, required)
- `lesson_title` (string, required)
- `mdf_script` (string, required)
- `used_variables` (array, required)
- `depends_on_lessons` (array, required)

### `course_index` (array, required)

Each item:

- `lesson_id` (string, required)
- `lesson_title` (string, required)
- `core_question` (string, required)
- `source_span_map` (array of `{source_id, start, end}`, required)

### `global_variable_table` (array, required)

Each item:

- `name` (string, required)
- `collected_in` (string, required)
- `used_in` (array of lesson ids, required)
- `effect_scope` (string enum: `local|cross_lesson`, required)

## Minimal Output Example

```json
{
  "lesson_mdf_scripts": [
    {
      "lesson_id": "L01",
      "lesson_title": "Core Loop Setup",
      "mdf_script": "## Objective\n...\n?[%{{learner_goal}} Option A | Option B]\n---\n...",
      "used_variables": ["learner_goal"],
      "depends_on_lessons": []
    }
  ],
  "course_index": [
    {
      "lesson_id": "L01",
      "lesson_title": "Core Loop Setup",
      "core_question": "What makes this loop stable in production?",
      "source_span_map": [{"source_id": "doc-1", "start": 120, "end": 286}]
    }
  ],
  "global_variable_table": [
    {
      "name": "learner_goal",
      "collected_in": "L01",
      "used_in": ["L01", "L02"],
      "effect_scope": "cross_lesson"
    }
  ]
}
```

## Phase 5 Artifacts

4. `deployed_course_url`
- Platform URL of the deployed course.

5. `shifu_bid`
- Course BID on the AI-Shifu platform.

### `deployment_result` (object, optional)

- `shifu_bid` (string, required)
- `deployed_course_url` (string, required)
- `lesson_count` (number, required)
- `status` (string enum: `published|draft`, required)

## Delivery Guarantees

- Stable schema across reruns.
- Deterministic references for lesson ids and source spans.
- Partial rerun support for changed lessons.
