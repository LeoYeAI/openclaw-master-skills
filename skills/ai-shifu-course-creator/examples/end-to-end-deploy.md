# End-to-End Deploy Example (Phase 1 → 2 → 3 → 4 → 5)

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
  "platform_region": "cn",
  "target_language": "zh-CN"
}
```

## Phase 1–4 (Author)

Produces optimized MDF lesson scripts (see `pipeline-full.md` for detailed output).

## Phase 5 Output (Deployment)

### Step 1: Build Course Directory

```
my-course/
  README.md
  system-prompt.md
  structure.json
  lessons/
    lesson-01.md
    lesson-02.md
    lesson-03.md
```

### Step 2: Build Import File

```bash
python3 {skillDir}/scripts/shifu-cli.py build --course-dir ./my-course/ --title "Metric Drift Diagnosis"
```

Output: `my-course/shifu-import.json`

### Step 3: Import and Publish

```bash
python3 {skillDir}/scripts/shifu-cli.py import --new --json-file ./my-course/shifu-import.json
# Returns: shifu_bid = abc123-def456

python3 {skillDir}/scripts/shifu-cli.py publish abc123-def456
```

### Step 4: Verify

```bash
python3 {skillDir}/scripts/shifu-cli.py show abc123-def456
```

Platform URLs:
- Admin: `https://app.ai-shifu.cn/shifu/abc123-def456`
- Preview: `https://app.ai-shifu.cn/c/abc123-def456?preview=true`

## Acceptance Notes

- All five phases executed end-to-end.
- MDF files written to course directory, built, imported, and published.
- Course is live and accessible via platform URL.
