# Issues

## Overview
Issue tracking data from multiple sources including the normalized `issues` table and source control issue data (e.g., GitHub Issues).

## issues
Normalized issue data across sources.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source | text | Source platform |
| source_id | text | External ID |
| source_url | text | Link to issue |
| dx_user_id | bigint | FK to dx_users (assignee) |
| creator_id | bigint | FK to dx_users (creator) |
| title | text | Issue title |
| state | text | Current state |
| created | timestamp | Creation time |
| started | timestamp | Work started |
| updated | timestamp | Last update |
| completed | timestamp | Completion time |
| cycle_time | integer | Cycle time in seconds |
| cycle_time_business_hours | integer | Business hours cycle time |
| tz | text | Timezone |
| cancelled | boolean | Was cancelled |
| deleted | boolean | Soft delete flag |
| external_id | text | External identifier |
| external_url | text | External URL |

**Common queries:**
```sql
-- Issue throughput
SELECT DATE_TRUNC('week', completed) as week, COUNT(*) as completed_issues
FROM issues
WHERE completed IS NOT NULL AND completed > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;

-- Average cycle time by source
SELECT source, COUNT(*) as issues, AVG(cycle_time)/3600 as avg_hours
FROM issues
WHERE completed IS NOT NULL AND cycle_time IS NOT NULL
GROUP BY source;

-- Issues by assignee
SELECT u.name, COUNT(*) as assigned, COUNT(i.completed) as completed
FROM issues i
JOIN dx_users u ON i.dx_user_id = u.id
WHERE i.created > NOW() - INTERVAL '30 days'
GROUP BY u.name ORDER BY assigned DESC;
```

## issue_collections / issue_collection_issues
Groupings of issues for tracking/reporting.

## issue_lifecycle_statistics
Aggregated issue lifecycle metrics.

---

## Source Control Issues

### github_issues
Source control issue data (e.g., GitHub Issues).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | varchar | GitHub issue ID |
| source_url | text | GitHub URL |
| repository_id | bigint | FK to github_repositories |
| state | varchar | State (open, closed) |
| title | text | Issue title |
| number | bigint | Issue number |
| creator_id | bigint | FK to github_users |
| type | text | Issue type |
| cycle_time | integer | Cycle time in seconds |
| created_at | timestamp | Creation time |
| started_at | timestamp | Work started |
| updated_at | timestamp | Last update |
| closed_at | timestamp | Close time |
| deleted_at | timestamp | Soft delete |

**Common queries:**
```sql
-- Open issues by repository
SELECT r.name, COUNT(*) as open_issues
FROM github_issues gi
JOIN github_repositories r ON gi.repository_id = r.id
WHERE gi.state = 'open' AND gi.deleted_at IS NULL
GROUP BY r.name ORDER BY open_issues DESC;

-- Issue close rate
SELECT
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as created,
    COUNT(closed_at) as closed
FROM github_issues
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;

-- Average time to close
SELECT AVG(EXTRACT(EPOCH FROM (closed_at - created_at)))/3600 as avg_hours_to_close
FROM github_issues
WHERE closed_at IS NOT NULL AND created_at > NOW() - INTERVAL '90 days';
```

### github_issue_assignees
Issue assignment tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| issue_id | bigint | FK to github_issues |
| user_id | bigint | FK to github_users |

### github_issue_labels
Labels applied to issues.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| issue_id | bigint | FK to github_issues |
| label_id | bigint | FK to github_labels |

### github_labels
Label definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | varchar | GitHub label ID |
| name | text | Label name |
| color | text | Label color |
| description | text | Label description |
| repository_id | bigint | FK to github_repositories |

**Common queries:**
```sql
-- Issues by label
SELECT l.name as label, COUNT(*) as issue_count
FROM github_issue_labels gil
JOIN github_labels l ON gil.label_id = l.id
JOIN github_issues gi ON gil.issue_id = gi.id
WHERE gi.state = 'open'
GROUP BY l.name ORDER BY issue_count DESC;
```

### github_issue_projects
Issues linked to GitHub Projects.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| issue_id | bigint | FK to github_issues |
| project_id | bigint | FK to github_projects |

### github_projects
GitHub Projects (project boards).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | varchar | GitHub project ID |
| name | text | Project name |
| organization_id | bigint | FK to github_organizations |
| state | text | Project state |

## Linking Issues to PRs

```sql
-- Issues with linked PRs
SELECT gi.number as issue, gi.title, gp.number as pr_number, gp.merged
FROM github_issues gi
JOIN github_pulls gp ON gp.jira_issue_id = gi.id
WHERE gi.created_at > NOW() - INTERVAL '30 days';
```

## Issue Metrics Summary

```sql
-- Comprehensive issue metrics
SELECT
    COUNT(*) FILTER (WHERE state = 'open') as open_issues,
    COUNT(*) FILTER (WHERE closed_at > NOW() - INTERVAL '7 days') as closed_this_week,
    AVG(cycle_time) FILTER (WHERE closed_at IS NOT NULL)/3600 as avg_cycle_hours,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as created_this_week
FROM github_issues
WHERE deleted_at IS NULL;
```
