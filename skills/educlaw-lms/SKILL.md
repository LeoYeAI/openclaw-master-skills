---
name: educlaw-lms
version: 1.0.0
description: LMS sync, assignments, course materials, and online gradebook for EduClaw. Bridges the authoritative SIS with Canvas, Moodle, Google Classroom, and OneRoster CSV. 25 actions across 4 domains -- lms_sync, assignments, online_gradebook, course_materials. FERPA/COPPA compliant. DPA hard-gated. Credentials AES-256 encrypted at rest.
author: AvanSaber / Nikhil Jathar
homepage: https://www.educlaw.ai
source: https://github.com/avansaber/educlaw-lms
tier: 4
category: education
requires: [erpclaw, erpclaw-people, educlaw]
database: ~/.openclaw/erpclaw/data.sqlite
scripts: scripts/db_query.py
user-invocable: true
tags: [educlaw, lms, canvas, moodle, google-classroom, oneroster, sync, gradebook, assignments, course-materials, ferpa, coppa, sis, education]
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/db_query.py --action status"},"requires":{"bins":["python3"],"env":["EDUCLAW_LMS_ENCRYPTION_KEY"],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
---

# educlaw-lms

You are an LMS Integration Specialist for EduClaw, an AI-native Student Information System.
You bridge EduClaw's authoritative SIS with external Learning Management Systems: Canvas, Moodle,
Google Classroom, and OneRoster 1.1 CSV export.

The SIS is always the source of truth for rosters. Grades flow LMS→SIS by default (configurable).
Every student roster push logs a FERPA disclosure. COPPA-applicable students require verified LMS
consent before syncing. A signed Data Processing Agreement (DPA) is a hard gate on all sync operations.
Credentials (OAuth secrets, tokens) are AES-256 encrypted before storage — never stored in plaintext.

## Security Model

- **Local-only data**: All records stored in `~/.openclaw/erpclaw/data.sqlite`
- **Encrypted credentials**: LMS API secrets encrypted via `EDUCLAW_LMS_ENCRYPTION_KEY` env var (AES-256)
- **DPA hard gate**: `has_dpa_signed = 0` blocks ALL sync operations — returns `E_DPA_REQUIRED`
- **COPPA guard**: Students with `is_coppa_applicable=1` are skipped (logged as `E_COPPA_UNVERIFIED`) unless `is_coppa_verified=1` on the connection
- **FERPA auto-logging**: Every roster push logs a disclosure to `educlaw_data_access_log`; every grade pull logs an API access
- **Immutable audit tables**: `educlaw_lms_sync_log` and `educlaw_lms_grade_sync` are append-only
- **Submitted grade lock**: Grades with `is_grade_submitted=1` are never overwritten automatically — must use `apply-grade-resolution` with explicit resolution
- **SQL injection safe**: All queries use parameterized statements

### Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `EDUCLAW_LMS_ENCRYPTION_KEY` | **Required** | Passphrase for AES-256 credential encryption. Min 16 chars. |
| `ERPCLAW_DB_PATH` | Optional | Override default DB path (`~/.openclaw/erpclaw/data.sqlite`) |

### Skill Activation Triggers

Activate this skill when the user mentions: LMS, Canvas, Moodle, Google Classroom, OneRoster,
roster sync, grade sync, assignment push, online gradebook, course materials, DPA, COPPA consent
for LMS, sync log, grade conflict, oneroster export, close course.

### Setup (First Use Only)

```
# 1. Set encryption key (add to shell profile)
export EDUCLAW_LMS_ENCRYPTION_KEY="your-secure-passphrase-here"

# 2. Initialize database (erpclaw + educlaw must already be installed)
python3 {baseDir}/../erpclaw/scripts/db_query.py --action initialize-database
python3 {baseDir}/../educlaw/scripts/db_query.py --action status

# 3. Initialize LMS tables and verify
python3 {baseDir}/scripts/db_query.py --action status
```

---

## Quick Start (Tier 1)

### Workflow 1: Connect an LMS (Canvas Example)

```
# Step 1 — Create connection in draft status
--action add-lms-connection \
  --lms-type canvas \
  --display-name "Jefferson High — Canvas" \
  --endpoint-url "https://canvas.jefferson.edu" \
  --client-id "your-canvas-client-id" \
  --client-secret "your-canvas-client-secret" \
  --grade-direction lms_to_sis \
  --has-dpa-signed 1 \
  --dpa-signed-date 2026-01-15 \
  --is-coppa-verified 1 \
  --company-id {company_id}

# Step 2 — Test credentials and activate
--action activate-lms-connection --connection-id {connection_id}

# Step 3 — View connection details (credentials masked)
--action get-lms-connection --connection-id {connection_id}
```

### Workflow 2: Sync a Term's Roster to LMS

```
# Push all sections + students + instructors for a term
--action apply-course-sync \
  --connection-id {connection_id} \
  --academic-term-id {term_id} \
  --company-id {company_id}

# Check sync results
--action get-sync-log --sync-log-id {sync_log_id}

# List all sync runs
--action list-sync-logs --connection-id {connection_id}
```

### Workflow 3: Push Assignments and Pull Grades

```
# Push a SIS assessment to Canvas
--action submit-assessment-to-lms \
  --assessment-id {assessment_id} \
  --connection-id {connection_id}

# Pull grades from LMS into staging
--action import-grades \
  --connection-id {connection_id} \
  --section-id {section_id}

# Review the unified gradebook
--action get-online-gradebook \
  --section-id {section_id} \
  --connection-id {connection_id}

# Resolve any grade conflicts
--action list-grade-conflicts --connection-id {connection_id} --section-id {section_id}
--action apply-grade-resolution \
  --grade-sync-id {grade_sync_id} \
  --resolution lms_wins \
  --resolved-by {user_id}
```

### Workflow 4: Add Course Materials

```
# Add a syllabus URL
--action add-course-material \
  --section-id {section_id} \
  --name "Course Syllabus Fall 2026" \
  --material-type syllabus \
  --access-type url \
  --external-url "https://docs.example.com/syllabus.pdf" \
  --company-id {company_id}

# List all materials for a section
--action list-course-materials --section-id {section_id}
```

### Workflow 5: Export OneRoster CSV

```
# Export full term roster (6 CSV files, zipped)
--action generate-oneroster-csv \
  --academic-term-id {term_id} \
  --output-dir /tmp/oneroster_export \
  --company-id {company_id}

# Export with grades (adds lineItems.csv + results.csv)
--action generate-oneroster-csv \
  --academic-term-id {term_id} \
  --output-dir /tmp/oneroster_export \
  --include-grades \
  --company-id {company_id}
```

### Workflow 6: Close LMS Course After Grade Submission

```
# After running submit-grades in educlaw, close the LMS mapping
--action complete-lms-course \
  --section-id {section_id} \
  --connection-id {connection_id}
```

---

## All Actions (Tier 2)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### LMS Sync Domain (`lms_sync.py`)

| Action | Key Parameters | Description |
|---|---|---|
| `add-lms-connection` | --lms-type --display-name --company-id | Create LMS connection in `draft` status. Encrypts credentials before storage. No API call. |
| `update-lms-connection` | --connection-id [fields] | Update connection settings. Re-encrypts credentials if provided. Cannot update inactive/error connections without first resetting. |
| `get-lms-connection` | --connection-id | Get full connection record. Credentials masked (last 4 chars only). Shows `last_sync_at`, `connection_status`. |
| `list-lms-connections` | --company-id [--lms-type --connection-status] | List all connections. Returns id, display_name, lms_type, status, last_sync_at, has_dpa_signed, is_coppa_verified. |
| `activate-lms-connection` | --connection-id | Make live API call to validate credentials. On success: sets `status = 'active'`, populates `lms_version`/`lms_site_name`. On failure: sets `status = 'error'`. Requires `has_dpa_signed = 1`. |
| `apply-course-sync` | --connection-id --academic-term-id --company-id [--section-id] | Full roster push for a term. Syncs: term→sections→users→enrollments. Creates sync log. FERPA disclosure per student. COPPA-restricted students skipped. Blocks concurrent runs. |
| `list-sync-logs` | --connection-id [--sync-type --sync-status --from-date --to-date] | List sync run history. Returns summary stats per run (sections, students, grades, conflicts, errors). |
| `get-sync-log` | --sync-log-id | Get full sync run details including `error_summary` JSON array. |
| `apply-sync-resolution` | --connection-id --entity-type --entity-id --resolution | Resolve user/course mapping conflict. Resolution: `sis_wins` (re-push), `lms_wins` (accept LMS state), `dismiss` (mark reviewed). |

### Assignments Domain (`assignments.py`)

| Action | Key Parameters | Description |
|---|---|---|
| `submit-assessment-to-lms` | --assessment-id --connection-id [--section-id] | Push SIS assessment to LMS as assignment. Idempotent (skips if already mapped). Creates `educlaw_lms_assignment_mapping`. Logs FERPA disclosure. |
| `import-lms-assignments` | --connection-id --section-id [--create-assessments --plan-id --category-id] | Pull LMS assignments not yet in EduClaw. Optionally creates stub `educlaw_assessment` records. Sets `push_direction = 'lms_to_sis'`. |
| `apply-assessment-update` | --assessment-id --connection-id | Push updated assessment fields (name, max_points, due_date, is_published) to LMS. Warns if max_points changed. |
| `list-lms-assignments` | --connection-id [--section-id --assignment-sync-status] | List assessments with LMS mappings. Shows SIS details + LMS URL, `is_published_in_lms`, `assignment_sync_status`. |
| `delete-lms-assignment` | --assessment-id --connection-id | Remove LMS mapping (soft delete via `sync_status = 'error'`). Does NOT delete LMS assignment. |

### Online Gradebook Domain (`online_gradebook.py`)

| Action | Key Parameters | Description |
|---|---|---|
| `import-grades` | --connection-id --section-id [--assessment-id --academic-term-id] | Pull LMS grades into staging (`educlaw_lms_grade_sync`). Auto-applies new grades if `grade_direction = 'lms_to_sis'` and no SIS score. Submitted grades flagged as `submitted_grade_locked` conflict — never auto-overwritten. Logs FERPA pull per student. |
| `get-online-gradebook` | --section-id --connection-id | Return unified SIS+LMS gradebook matrix. Student rows × Assessment columns. Each cell: SIS score, LMS score, conflict flag, LMS URL. |
| `list-grade-conflicts` | --connection-id [--section-id --conflict-type --conflict-status] | List grade conflicts for review. Shows student name, assessment, SIS score, LMS score, `is_grade_submitted`. |
| `apply-grade-resolution` | --grade-sync-id --resolution --resolved-by [--new-score --push-to-lms] | Resolve grade conflict. Options: `lms_wins` (apply LMS score), `sis_wins` (dismiss; optionally push SIS back), `manual` (enter custom score via `--new-score`). Submitted-grade conflicts route through amendment workflow. |
| `generate-oneroster-csv` | --academic-term-id --output-dir --company-id [--include-grades] | Generate OneRoster 1.1 CSV zip package. Base: 6 files (orgs, academicSessions, courses, classes, users, enrollments). With `--include-grades`: adds lineItems.csv + results.csv. COPPA minimization applied. |
| `complete-lms-course` | --section-id --connection-id | Mark LMS course mapping as `closed`. Blocks further grade pulls. Call after `submit-grades` in parent educlaw. |

### Course Materials Domain (`course_materials.py`)

| Action | Key Parameters | Description |
|---|---|---|
| `add-course-material` | --section-id --name --material-type --access-type --company-id | Create course material. For `url`: requires `--external-url`. For `file_attachment`: requires `--file-path`. For `lms_linked`: requires `--lms-connection-id`. |
| `update-course-material` | --material-id [fields] | Update material metadata. Cannot change `section_id`. |
| `list-course-materials` | --section-id [--material-type --is-visible-to-students --include-archived] | List materials for section. Ordered by `sort_order` ASC. Excludes archived by default. |
| `get-course-material` | --material-id | Get full material record including LMS link details. |
| `delete-course-material` | --material-id | Archive material (soft delete). Sets `status = 'archived'`. Idempotent. |

---

### Grade Direction Behavior

| Setting | Effect |
|---|---|
| `lms_to_sis` (default) | New grades auto-applied to `educlaw_assessment_result`. Existing grades create conflicts. Submitted grades always conflict. |
| `sis_to_lms` | Grade pull is skipped entirely — no `educlaw_lms_grade_sync` records created. |
| `manual` | All pulled grades remain `sync_status = 'pulled'` pending admin review via `list-grade-conflicts`. |

### Conflict Types

| Conflict Type | Cause | Resolution Path |
|---|---|---|
| `score_mismatch` | LMS score ≠ existing SIS score | `lms_wins`, `sis_wins`, or `manual` |
| `submitted_grade_locked` | SIS grade has `is_grade_submitted = 1` | `lms_wins` routes through grade amendment; `sis_wins` dismisses |
| `student_not_found` | LMS user not in `educlaw_lms_user_mapping` | Re-run `apply-course-sync` to remap; then `apply-grade-resolution` |
| `assignment_not_found` | LMS assignment not in `educlaw_lms_assignment_mapping` | Run `import-lms-assignments --create-assessments`; then retry |

### Sync Log Statuses

| Status | Meaning |
|---|---|
| `pending` | Sync log created; sync not yet started |
| `running` | Sync in progress (new sync calls for same connection blocked) |
| `completed` | All records processed successfully |
| `completed_with_errors` | Some records succeeded, some failed — enables targeted re-sync |
| `failed` | Critical error; zero records processed |

### Course Material Types and Access Types

| Material Type | Use Case |
|---|---|
| `syllabus` | Course syllabus document |
| `reading` | Assigned reading (URL or file) |
| `video_link` | Video resource link |
| `assignment_guide` | Instructions for a specific assessment |
| `rubric` | Grading rubric |
| `other` | Catch-all for other resources |

| Access Type | Required Parameter | Notes |
|---|---|---|
| `url` | `--external-url` | External website, video, or document link |
| `file_attachment` | `--file-path` | Local file path relative to data directory |
| `lms_linked` | `--lms-connection-id` | File stored in LMS; `lms_file_id` + `lms_download_url` populated on save |

### Important Constraints

- **DPA Required**: `has_dpa_signed = 0` → all `apply-course-sync`, `import-grades`, `submit-assessment-to-lms`, `generate-oneroster-csv` calls return `{"error": "E_DPA_REQUIRED"}`. Update with `update-lms-connection --has-dpa-signed 1 --dpa-signed-date YYYY-MM-DD`.
- **COPPA Students**: Students with `is_coppa_applicable = 1` are silently skipped in roster sync unless the connection has `is_coppa_verified = 1`. Each skipped student is logged as `E_COPPA_UNVERIFIED` in the sync log's `error_summary`.
- **Concurrent Sync Prevention**: If a `apply-course-sync` or `import-grades` run is already `running` for the same connection, a new call returns an error. Check with `list-sync-logs --sync-status running`.
- **Closed Course Lock**: After `complete-lms-course`, no further grade pulls are accepted for that section/connection pair. Create a new course mapping to re-enable (advanced; contact admin).
- **Immutable Sync Records**: `educlaw_lms_sync_log` and `educlaw_lms_grade_sync` records are never deleted or fully updated. Only `educlaw_lms_grade_sync` resolution fields (`resolved_by`, `resolved_at`, `resolution`) may be updated by `apply-grade-resolution`.
- **OneRoster COPPA Minimization**: Under-13 students (`is_coppa_applicable = 1`) have email omitted from `users.csv`. Students with `directory_info_opt_out = 1` have names blanked in the export.

### OneRoster Export File Structure

| File | Always Included | Content |
|---|---|---|
| `orgs.csv` | ✅ | Institution record |
| `academicSessions.csv` | ✅ | Term and school year |
| `courses.csv` | ✅ | Course catalog |
| `classes.csv` | ✅ | Course sections |
| `users.csv` | ✅ | Students and instructors |
| `enrollments.csv` | ✅ | Section enrollments |
| `lineItems.csv` | With `--include-grades` | Assessment definitions |
| `results.csv` | With `--include-grades` | Grade records |

All 8 files are zipped into `oneroster_{term_name}_{date}.zip` in `--output-dir`.


