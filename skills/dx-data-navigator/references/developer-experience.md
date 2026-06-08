# Developer Experience (DX) Core Tables

## Overview
These tables contain DX survey data, snapshots, scores, and sentiment metrics collected from developer surveys.

## dx_snapshots
Survey snapshot periods with participation metrics.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | External identifier |
| account_id | bigint | Account reference |
| contributors | integer | Number of contributors in snapshot |
| participation_rate | numeric | Survey participation rate (0-1) |
| start_date | date | Snapshot period start |
| end_date | date | Snapshot period end |

**Common queries:**
```sql
-- Get latest snapshot
SELECT * FROM dx_snapshots ORDER BY end_date DESC LIMIT 1;

-- Get participation trends
SELECT start_date, end_date, participation_rate, contributors
FROM dx_snapshots ORDER BY end_date;
```

## dx_snapshot_items
Defines the metrics/items measured in each snapshot.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| snapshot_id | bigint | FK to dx_snapshots |
| name | text | Item name (e.g., "Effectiveness", "Code comprehension") |
| item_type | text | Category: core4, kpi, sentiment, workflow, workflow_averages, csat |
| prompt | text | Survey question text |
| target_label | text | Target description |

**Item types:**
- `core4`: Core DX metrics (Effectiveness, Impact, Quality, Speed)
- `kpi`: Key performance indicators (Ease of delivery, Engagement, Weekly time loss)
- `sentiment`: Developer sentiment scores (Deep work, Change Confidence, etc.)
- `workflow`: Workflow-specific metrics (Review wait time, CI wait time, etc.)
- `workflow_averages`: Aggregated workflow metrics
- `csat`: Customer satisfaction for tools (e.g., code editors, issue trackers, CI/CD tools)

## dx_snapshot_team_scores
Scores per team per snapshot item with benchmarks.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| snapshot_id | bigint | FK to dx_snapshots |
| snapshot_team_id | bigint | FK to dx_snapshot_teams |
| team_id | bigint | FK to dx_teams |
| item_id | bigint | FK to dx_snapshot_items |
| score | numeric | The score value |
| vs_org | numeric | Comparison vs organization average |
| vs_prev | numeric | Comparison vs previous snapshot |
| vs_industry50 | numeric | Comparison vs industry 50th percentile |
| vs_industry75 | numeric | Comparison vs industry 75th percentile |
| vs_industry90 | numeric | Comparison vs industry 90th percentile |
| unit | varchar | Score unit |

**Common queries:**
```sql
-- Get all scores for a team in latest snapshot
SELECT i.name, i.item_type, ts.score, ts.vs_org, ts.vs_industry50
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
JOIN dx_snapshots s ON ts.snapshot_id = s.id
WHERE st.name = 'Team Name'
ORDER BY s.end_date DESC, i.item_type, i.name;

-- Compare teams on a specific metric
SELECT st.name as team, ts.score, ts.vs_org
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE i.name = 'Effectiveness' AND ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
ORDER BY ts.score DESC;
```

## dx_platform_surveys
Survey definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| project_id | bigint | Project reference |
| name | text | Survey name |
| created_at | timestamp | Creation time |

## dx_platform_questions
Questions within surveys.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| survey_id | bigint | FK to dx_platform_surveys |
| question_type | text | Type: rating_scale, multiple_choice, short_text, long_text, prequalifier |
| key | text | Question identifier |
| label | text | Question text |
| position | integer | Order in survey |

## dx_platform_responses
Individual survey responses.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| survey_id | bigint | FK to dx_platform_surveys |
| user_id | bigint | FK to dx_users |
| prequalified_at | timestamp | Prequalification time |
| responded_at | timestamp | Response submission time |

## dx_platform_response_answers
Individual answers within responses.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| response_id | bigint | FK to dx_platform_responses |
| question_id | bigint | FK to dx_platform_questions |
| option_id | bigint | Selected option (for multiple choice) |
| value | text | Answer value |

## dx_studies
Custom studies/research conducted.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| name | text | Study name |
| created_at | timestamp | Creation time |

## dx_study_questions / dx_study_responses / dx_study_response_answers
Similar structure to platform surveys but for custom studies.
