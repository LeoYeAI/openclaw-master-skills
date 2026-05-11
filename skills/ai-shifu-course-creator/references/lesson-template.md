# Lesson Output Template

## Required Fields

- `lesson_id`
- `lesson_title`
- `mdf_script`
- `used_variables`
- `depends_on_lessons`

## Field Types

- `lesson_id`: string (stable, deterministic, required)
- `lesson_title`: string (learner-facing, required)
- `mdf_script`: markdown string (runnable MarkdownFlow, required)
- `used_variables`: array of strings (required)
- `depends_on_lessons`: array of lesson ids (required)

## Guidance

- `lesson_id`: stable and deterministic.
- `lesson_title`: concise learner-facing title.
- `mdf_script`: runnable MarkdownFlow content.
- `used_variables`: includes collection point and effect scope.
- `depends_on_lessons`: explicit list; empty list if none.

## Minimal Example

```json
{
  "lesson_id": "L03",
  "lesson_title": "Diagnose the Bottleneck",
  "mdf_script": "## Objective\nFind the bottleneck and test one fix.\n---\n?[%{{bottleneck_guess}} CPU bound | IO bound | Lock contention]\n---\nBased on {{bottleneck_guess}}, run the matching test first.",
  "used_variables": ["bottleneck_guess"],
  "depends_on_lessons": ["L02"]
}
```
