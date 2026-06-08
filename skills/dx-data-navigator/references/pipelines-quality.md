# Pipelines and Code Quality

## Overview
CI/CD pipeline data and code quality metrics (e.g., SonarCloud).

## pipeline_runs
CI/CD pipeline execution records.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| reference_id | text | External reference |
| source_id | text | Source system ID |
| pipeline_source_id | bigint | FK to pipeline_sources |
| name | text | Pipeline name |
| status | text | Run status (success, failure, etc.) |
| started_at | timestamp | Start time |
| finished_at | timestamp | End time |
| duration | integer | Duration in seconds |
| repository | text | Repository name |
| commit_sha | text | Commit SHA |
| head_branch | text | Branch name |
| pr_number | bigint | Related PR number |
| pull_id | bigint | FK to github_pulls |
| source_url | text | Link to pipeline run |
| dx_user_id | bigint | FK to dx_users (triggering user) |
| email | text | User email |
| github_repository_id | bigint | FK to github_repositories |
| github_username | text | GitHub username |

**Common queries:**
```sql
-- Pipeline success rate
SELECT
    COUNT(*) as total_runs,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'success' THEN 1 END)::float / COUNT(*) * 100 as success_rate
FROM pipeline_runs
WHERE started_at > NOW() - INTERVAL '30 days';

-- Average pipeline duration
SELECT name, COUNT(*) as runs, AVG(duration)/60 as avg_minutes
FROM pipeline_runs
WHERE finished_at IS NOT NULL AND started_at > NOW() - INTERVAL '30 days'
GROUP BY name ORDER BY runs DESC;

-- Flaky pipelines (high failure rate)
SELECT name,
       COUNT(*) as total,
       COUNT(CASE WHEN status != 'success' THEN 1 END) as failures,
       COUNT(CASE WHEN status != 'success' THEN 1 END)::float / COUNT(*) * 100 as failure_rate
FROM pipeline_runs
WHERE started_at > NOW() - INTERVAL '30 days'
GROUP BY name
HAVING COUNT(*) > 10
ORDER BY failure_rate DESC;

-- CI wait time (time from commit to pipeline completion)
SELECT
    AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) as avg_duration_seconds,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))) as median_seconds
FROM pipeline_runs
WHERE finished_at IS NOT NULL AND started_at > NOW() - INTERVAL '30 days';
```

## pipeline_sources
Pipeline source definitions (e.g., CI/CD platforms).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| name | text | Source name |
| source_type | text | Source type |

## pipeline_stage_names
Pipeline stage definitions for detailed analysis.

---

## Code Quality

### sonarcloud_projects
Code quality project definitions (e.g., SonarCloud).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_key | varchar | SonarCloud project key |
| name | text | Project name |
| organization_id | bigint | FK to sonarcloud_organizations |

### sonarcloud_issues
Code quality issues detected by static analysis tools.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_key | varchar | Issue key |
| component | text | File/component path |
| rule | varchar | Rule that triggered issue |
| severity | varchar | Severity (BLOCKER, CRITICAL, MAJOR, MINOR, INFO) |
| project_id | bigint | FK to sonarcloud_projects |
| effort | varchar | Remediation effort |
| debt | varchar | Technical debt |
| status | varchar | Issue status |
| issue_type | varchar | Type (BUG, VULNERABILITY, CODE_SMELL) |
| issue_status | text | Current status |
| clean_code_attribute_category | varchar | Clean code category |
| clean_code_attribute | varchar | Clean code attribute |
| created_at | timestamp | Detection time |
| updated_at | timestamp | Last update |

**Common queries:**
```sql
-- Issue summary by severity
SELECT severity, issue_type, COUNT(*) as count
FROM sonarcloud_issues
WHERE status NOT IN ('RESOLVED', 'CLOSED')
GROUP BY severity, issue_type
ORDER BY severity, issue_type;

-- Technical debt by project
SELECT p.name, COUNT(i.id) as issues, SUM(CAST(REPLACE(i.debt, 'min', '') AS INTEGER)) as debt_minutes
FROM sonarcloud_issues i
JOIN sonarcloud_projects p ON i.project_id = p.id
WHERE i.status NOT IN ('RESOLVED', 'CLOSED')
GROUP BY p.name ORDER BY debt_minutes DESC;

-- New issues trend
SELECT DATE(created_at) as day, COUNT(*) as new_issues
FROM sonarcloud_issues
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at) ORDER BY day;
```

### sonarcloud_security_hotspots
Security-specific findings requiring review.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_key | varchar | Hotspot key |
| component | text | File path |
| security_category | varchar | Security category |
| vulnerability_probability | varchar | Risk level |
| status | varchar | Review status |
| project_id | bigint | FK to sonarcloud_projects |

### sonarcloud_metrics / sonarcloud_project_metrics
Code metrics (coverage, duplications, complexity, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | varchar | Metric ID |
| name | varchar | Metric name |
| domain | varchar | Metric domain |

**Common metrics:**
- `coverage`: Test coverage percentage
- `duplicated_lines_density`: Code duplication percentage
- `sqale_index`: Technical debt in minutes
- `reliability_rating`: Bug-based rating (A-E)
- `security_rating`: Vulnerability-based rating (A-E)
- `sqale_rating`: Maintainability rating (A-E)

### sonarcloud_tags / sonarcloud_issue_tags
Issue tagging for categorization.

### sonarcloud_organizations
SonarCloud organization data.

## Quality Metrics Integration

```sql
-- Correlate code quality with team velocity
WITH team_quality AS (
    SELECT t.name as team,
           COUNT(si.id) as open_issues,
           COUNT(CASE WHEN si.severity IN ('BLOCKER', 'CRITICAL') THEN 1 END) as critical_issues
    FROM sonarcloud_issues si
    JOIN sonarcloud_projects sp ON si.project_id = sp.id
    -- Link projects to teams via naming convention or catalog
    JOIN dx_teams t ON sp.name ILIKE '%' || t.name || '%'
    WHERE si.status NOT IN ('RESOLVED', 'CLOSED')
    GROUP BY t.name
),
team_velocity AS (
    SELECT t.name as team, COUNT(p.id) as prs_merged
    FROM pull_requests p
    JOIN dx_users u ON p.dx_user_id = u.id
    JOIN dx_teams t ON u.team_id = t.id
    WHERE p.merged IS NOT NULL AND p.created > NOW() - INTERVAL '30 days'
    GROUP BY t.name
)
SELECT tq.team, tq.open_issues, tq.critical_issues, tv.prs_merged
FROM team_quality tq
JOIN team_velocity tv ON tq.team = tv.team
ORDER BY tq.critical_issues DESC;
```
