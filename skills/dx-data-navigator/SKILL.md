---
name: dx-data-navigator
description: Query Developer Experience (DX) data via the DX Data MCP server PostgreSQL database. Use this skill when analyzing developer productivity metrics, team performance, PR/code review metrics, deployment frequency, incident data, AI tool adoption, survey responses, DORA metrics, or any engineering analytics. Triggers on questions about DX scores, team comparisons, cycle times, code quality, developer sentiment, AI coding assistant adoption, sprint velocity, or engineering KPIs.
---

# DX Data Navigator

## Install

```bash
npx skills add pskoett/pskoett-ai-skills/dx-data-navigator
```

Query the DX Data Cloud PostgreSQL database using the `mcp__dx-mcp-server__queryData` tool.

## Tool Usage

```
mcp__dx-mcp-server__queryData(sql: "SELECT ...")
```

Always query `information_schema.columns` first if uncertain about table/column names:
```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'table_name' ORDER BY ordinal_position;
```

## Critical: Team Tables

Three team table types exist - use the right one:

| Table | Use Case |
|-------|----------|
| `dx_teams` | Current org structure, linking users to teams for PR/deployment metrics |
| `dx_snapshot_teams` | Teams within DX survey snapshots (use for DX scores) |
| `dx_versioned_teams` | Historical team structure at specific dates |

**For DX survey scores:** Join through `dx_snapshot_teams`. Use GROUP BY to avoid duplicates (team names can appear multiple times across snapshot history):
```sql
SELECT st.name as team, i.name as metric, MAX(ts.score) as score, MAX(ts.vs_industry50) as vs_industry
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
  AND st.name = 'Your Team Name'
  AND i.item_type = 'core4'
GROUP BY st.name, i.name;
```

**For PR/deployment metrics by team:** Join through `dx_users` to `dx_teams`:
```sql
SELECT t.name, COUNT(*) as prs
FROM pull_requests p
JOIN dx_users u ON p.dx_user_id = u.id
JOIN dx_teams t ON u.team_id = t.id
WHERE p.merged IS NOT NULL GROUP BY t.name;
```

## Discovering Team Names

Query the database to find available teams:
```sql
SELECT name FROM dx_teams WHERE deleted_at IS NULL ORDER BY name;
```

## Data Domains

### Core DX Metrics
Survey snapshots with team scores, benchmarks, and sentiment data.

**Key tables:** `dx_snapshots`, `dx_snapshot_teams`, `dx_snapshot_items`, `dx_snapshot_team_scores`

**dx_snapshots columns:** id, account_id, contributors, participation_rate, start_date (date), end_date (date)

**dx_snapshot_teams columns:** id, snapshot_id, team_id, name, parent (boolean), flattened_parent, contributors, participation_rate

**dx_snapshot_items columns:** id, snapshot_id, name, item_type, prompt, target_label

**dx_snapshot_team_scores columns:** id, snapshot_id, snapshot_team_id (FK to dx_snapshot_teams.id), team_id (FK to dx_teams.id), item_id (FK to dx_snapshot_items.id), score, vs_org, vs_prev, vs_industry50, vs_industry75, vs_industry90, unit

**Item types in dx_snapshot_items:**
- `core4`: Effectiveness, Impact, Quality, Speed
- `kpi`: Ease of delivery, Engagement, Weekly time loss, Quality, Speed
- `sentiment`: Deep work, Change Confidence, Documentation, Cross-team collaboration, Customer focus, Decision-making, etc.
- `workflow`: Review wait time, CI wait time, Deploy frequency, PR merge frequency, AI time savings, Red tape, etc.
- `workflow_averages`: Raw average values for workflow metrics (actual numbers, not percentiles)
- `csat`: Tool satisfaction scores (e.g., code editors, issue trackers, CI/CD tools)

```sql
-- Latest snapshot info
SELECT id, start_date, end_date, contributors, participation_rate
FROM dx_snapshots ORDER BY end_date DESC LIMIT 1;

-- Team scores for specific metric (use GROUP BY to dedupe)
SELECT st.name as team, i.name as metric, MAX(ts.score) as score, MAX(ts.vs_industry50) as vs_industry
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
  AND st.name = 'Your Team Name'
  AND i.item_type = 'core4'
GROUP BY st.name, i.name;

-- All teams comparison on one metric
SELECT st.name as team, MAX(ts.score) as score, MAX(ts.vs_industry50) as vs_industry
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
  AND i.name = 'Effectiveness' AND i.item_type = 'core4'
  AND st.parent = false
GROUP BY st.name
ORDER BY score DESC NULLS LAST;
```

### Teams and Users
Organization structure, team hierarchies, user profiles.

**Key tables:** `dx_teams`, `dx_users`, `dx_team_hierarchies`, `dx_groups`

**dx_teams columns:** id, name, contributors, deleted_at

**dx_users key columns:** id, name, email, team_id, ai_light_adoption_date, ai_moderate_adoption_date, ai_heavy_adoption_date

```sql
-- Teams with contributor counts
SELECT name, contributors FROM dx_teams WHERE deleted_at IS NULL ORDER BY contributors DESC;

-- Users with AI adoption status
SELECT name, email, ai_heavy_adoption_date FROM dx_users
WHERE ai_heavy_adoption_date IS NOT NULL ORDER BY ai_heavy_adoption_date DESC;

-- Team members
SELECT u.name, u.email FROM dx_users u
JOIN dx_teams t ON u.team_id = t.id
WHERE t.name = 'Your Team Name';
```

### Pull Requests
PR metrics including cycle times, review wait times, and throughput.

**Key tables:** `pull_requests`, `pull_request_reviews`, `repos`

**pull_requests key columns:** id, dx_user_id, repo_id, title, base_ref, head_ref, additions, deletions, created, merged, closed, draft, bot_authored

**Key metrics (all in seconds, divide by 3600 for hours):**
- `open_to_merge`: Total PR cycle time
- `open_to_first_review`: Time to first review
- `open_to_first_approval`: Time to approval
- Business hour variants: add `_business_hours` suffix

```sql
-- PR metrics by team last 30 days
SELECT t.name, COUNT(*) as prs,
       AVG(p.open_to_merge)/3600 as avg_hours_to_merge,
       AVG(p.open_to_first_review)/3600 as avg_hours_to_first_review
FROM pull_requests p
JOIN dx_users u ON p.dx_user_id = u.id
JOIN dx_teams t ON u.team_id = t.id
WHERE p.merged IS NOT NULL AND p.created > NOW() - INTERVAL '30 days'
GROUP BY t.name ORDER BY prs DESC;

-- PR size distribution
SELECT
    CASE
        WHEN additions + deletions < 50 THEN 'XS (<50)'
        WHEN additions + deletions < 200 THEN 'S (50-199)'
        WHEN additions + deletions < 500 THEN 'M (200-499)'
        ELSE 'L (500+)'
    END as size_bucket,
    COUNT(*) as count,
    AVG(open_to_merge)/3600 as avg_hours
FROM pull_requests
WHERE merged IS NOT NULL AND created > NOW() - INTERVAL '90 days'
GROUP BY size_bucket ORDER BY avg_hours;
```

### Deployments and Incidents
Deployment frequency, success rates, and incident tracking for DORA metrics.

**Key tables:** `deployments`, `incidents`, `incident_services`

**deployments columns:** id, service, repository, environment, deployed_at, success, commit_sha

**incidents columns:** id, name, priority, source, source_url, started_at, resolved_at, started_to_resolved (seconds), deleted

**Deployment environments:** dev, stage, prod, production
**Incident priorities:** '1 - Critical', '2 - High', '3 - Moderate', '4 - Low', '5 - Planning'
**Incident source:** Check `SELECT DISTINCT source FROM incidents` for available sources

```sql
-- Deploy frequency by environment
SELECT environment, COUNT(*) FROM deployments
WHERE deployed_at > NOW() - INTERVAL '30 days' GROUP BY environment;

-- Deployment success rate
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE success) as successful,
    COUNT(*) FILTER (WHERE success)::float / COUNT(*) * 100 as success_rate
FROM deployments WHERE deployed_at > NOW() - INTERVAL '30 days';

-- Mean Time to Recovery (MTTR)
SELECT AVG(started_to_resolved)/3600 as avg_hours_to_resolve
FROM incidents
WHERE resolved_at IS NOT NULL AND priority IN ('1 - Critical', '2 - High');

-- Incidents by priority
SELECT priority, COUNT(*) FROM incidents
WHERE started_at > NOW() - INTERVAL '90 days' AND deleted = false
GROUP BY priority ORDER BY priority;
```

### AI Tools
AI coding assistant adoption tracking (e.g., GitHub Copilot).

**Key tables:** `ai_tools`, `ai_tool_daily_metrics`, `github_copilot_daily_usages`, `github_users`

**github_copilot_daily_usages columns:** id, login, date, enterprise_slug, active (boolean)

**github_users columns:** id, login, verified_emails, bot, active

**Linking Copilot to teams:** GitHub logins don't match DX user emails directly. Use `github_users.verified_emails` to link:
```sql
-- Copilot usage by team (via github_users email linking)
SELECT t.name as team, COUNT(DISTINCT c.login) as active_copilot_users
FROM github_copilot_daily_usages c
JOIN github_users gu ON c.login = gu.login
JOIN dx_users u ON gu.verified_emails = u.email
JOIN dx_teams t ON u.team_id = t.id
WHERE c.date > NOW() - INTERVAL '30 days' AND c.active = true
GROUP BY t.name ORDER BY active_copilot_users DESC;
```

```sql
-- Daily Copilot active users (overall)
SELECT date, COUNT(*) FILTER (WHERE active) as active_users
FROM github_copilot_daily_usages
WHERE date > NOW() - INTERVAL '30 days'
GROUP BY date ORDER BY date;

-- Copilot adoption rate (latest day)
SELECT
    COUNT(DISTINCT login) FILTER (WHERE active) as active_users,
    COUNT(DISTINCT login) as total_users,
    COUNT(DISTINCT login) FILTER (WHERE active)::float / COUNT(DISTINCT login) * 100 as adoption_pct
FROM github_copilot_daily_usages
WHERE date = (SELECT MAX(date) FROM github_copilot_daily_usages);

-- Weekly trend
SELECT DATE_TRUNC('week', date) as week,
       COUNT(DISTINCT login) FILTER (WHERE active) as active_users
FROM github_copilot_daily_usages
WHERE date > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;
```

### Issue Tracking
Project management data including issues, sprints, and cycle times (e.g., Jira).

**Key tables:** `jira_issues`, `jira_projects`, `jira_sprints`, `jira_issue_sprints`, `jira_issue_types`, `jira_statuses`

**jira_issues key columns:** id, key, summary, story_points, cycle_time (seconds), created_at, completed_at, project_id, status_id, issue_type_id, user_id

**jira_sprints columns:** id, name, state ('active', 'closed', 'future'), start_date, end_date, complete_date

```sql
-- Sprint velocity (last 5 closed sprints)
SELECT s.name, SUM(i.story_points) as points, COUNT(*) as issues
FROM jira_sprints s
JOIN jira_issue_sprints jis ON s.id = jis.sprint_id
JOIN jira_issues i ON jis.issue_id = i.id
WHERE s.state = 'closed' AND i.completed_at IS NOT NULL
GROUP BY s.id, s.name ORDER BY s.complete_date DESC LIMIT 5;

-- Issue cycle time by type
SELECT it.name as issue_type, COUNT(*) as issues, AVG(i.cycle_time)/3600 as avg_hours
FROM jira_issues i
JOIN jira_issue_types it ON i.issue_type_id = it.id
WHERE i.completed_at IS NOT NULL AND i.completed_at > NOW() - INTERVAL '90 days'
GROUP BY it.name ORDER BY issues DESC;
```

### Service Catalog
Software catalog with services, teams, domains, and ownership.

**Key tables:** `dx_catalog_entities`, `dx_catalog_entity_owners`, `dx_catalog_entity_types`

**dx_catalog_entities columns:** id, name, identifier, entity_type_identifier, description

**Entity types:** service, team, domain (check `entity_type_identifier` column)

```sql
-- Services count by owning team
SELECT t.name as team, COUNT(*) as services
FROM dx_catalog_entity_owners eo
JOIN dx_catalog_entities e ON eo.entity_id = e.id
JOIN dx_teams t ON eo.team_id = t.id
WHERE e.entity_type_identifier = 'service'
GROUP BY t.name ORDER BY services DESC;

-- List services with owners
SELECT e.name as service, e.identifier, t.name as owner_team
FROM dx_catalog_entities e
JOIN dx_catalog_entity_owners eo ON e.id = eo.entity_id
JOIN dx_teams t ON eo.team_id = t.id
WHERE e.entity_type_identifier = 'service'
ORDER BY t.name, e.name;
```

### Pipelines and Code Quality
CI/CD pipeline runs and code quality metrics (e.g., SonarCloud).

**Key tables:** `pipeline_runs`, `sonarcloud_issues`, `sonarcloud_projects`, `sonarcloud_project_metrics`

**pipeline_runs columns:** id, status, started_at, completed_at, duration

```sql
-- Pipeline success rate
SELECT COUNT(*) as runs,
       COUNT(*) FILTER (WHERE status = 'success') as successful,
       COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*) as success_pct
FROM pipeline_runs WHERE started_at > NOW() - INTERVAL '30 days';

-- Pipeline duration trend
SELECT DATE_TRUNC('week', started_at) as week,
       AVG(duration)/60 as avg_minutes
FROM pipeline_runs WHERE started_at > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;
```

### Issues
Normalized issue data from source control platforms (e.g., GitHub Issues).

**Key tables:** `issues`, `github_issues`, `github_issue_labels`, `github_labels`

**issues columns:** id, source, dx_user_id, title, state, created, completed, cycle_time

```sql
-- Issue throughput
SELECT DATE_TRUNC('week', completed) as week, COUNT(*) as completed
FROM issues WHERE completed > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;
```

### Documentation
Documentation and knowledge base activity (e.g., Confluence, wikis).

**Key tables:** `confluence_spaces`, `confluence_pages`, `confluence_page_versions`, `confluence_users`, `confluence_page_labels`

**confluence_spaces columns:** id, name, external_key, space_type, status, source_url, created_at

**confluence_pages columns:** id, space_id, author_id, title, status, views_count, created_at, updated_at

**confluence_page_versions columns:** id, page_id, version_number, author_id, created_at

```sql
-- Most active Confluence spaces
SELECT s.name as space_name, s.external_key,
       COUNT(DISTINCT p.id) as page_count,
       COUNT(DISTINCT pv.id) as total_edits,
       MAX(pv.created_at) as last_activity
FROM confluence_spaces s
LEFT JOIN confluence_pages p ON s.id = p.space_id
LEFT JOIN confluence_page_versions pv ON p.id = pv.page_id
GROUP BY s.id, s.name, s.external_key
ORDER BY total_edits DESC LIMIT 15;

-- Recent documentation activity
SELECT p.title, s.name as space, pv.created_at
FROM confluence_page_versions pv
JOIN confluence_pages p ON pv.page_id = p.id
JOIN confluence_spaces s ON p.space_id = s.id
WHERE pv.created_at > NOW() - INTERVAL '7 days'
ORDER BY pv.created_at DESC LIMIT 20;
```

## Data Quality Notes

**Known issues:**
- Some team names may have typos - verify names by querying `dx_teams`
- `incident_services` table is empty - incidents cannot be linked to specific services
- `dx_users` AI adoption date fields are mostly NULL - use `github_copilot_daily_usages` instead
- DX survey scores may have duplicates - always use GROUP BY with MAX() aggregation

## Common Query Patterns

### DORA Metrics
```sql
-- Deployment Frequency (daily average, production only)
SELECT COUNT(*)::float / 30 as deploys_per_day FROM deployments
WHERE deployed_at > NOW() - INTERVAL '30 days' AND environment IN ('prod', 'production');

-- Lead Time for Changes (PR cycle time)
SELECT
    AVG(open_to_merge)/3600 as avg_hours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY open_to_merge)/3600 as median_hours
FROM pull_requests
WHERE merged IS NOT NULL AND created > NOW() - INTERVAL '30 days';

-- Mean Time to Recovery
SELECT AVG(started_to_resolved)/3600 as mttr_hours FROM incidents
WHERE resolved_at IS NOT NULL AND priority IN ('1 - Critical', '2 - High')
  AND started_at > NOW() - INTERVAL '90 days';

-- Change Failure Rate (requires correlating incidents with deployments)
```

### Time-based Trends
```sql
-- Weekly PR throughput trend
SELECT DATE_TRUNC('week', merged) as week, COUNT(*) as prs
FROM pull_requests WHERE merged > NOW() - INTERVAL '90 days'
GROUP BY week ORDER BY week;

-- Monthly deployment trend
SELECT DATE_TRUNC('month', deployed_at) as month, COUNT(*) as deploys
FROM deployments WHERE deployed_at > NOW() - INTERVAL '12 months'
GROUP BY month ORDER BY month;
```

### Historical DX Survey Comparison
```sql
-- Compare team scores across all surveys
SELECT s.end_date as survey_date, i.name as metric, ts.score
FROM dx_snapshot_team_scores ts
JOIN dx_snapshots s ON ts.snapshot_id = s.id
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id AND st.snapshot_id = s.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = s.id
WHERE st.name = 'Your Team Name'
  AND i.item_type = 'core4'
  AND ts.score IS NOT NULL
ORDER BY s.end_date, i.name;

-- Teams that improved most since last survey (use vs_prev)
SELECT st.name as team, i.name as metric, MAX(ts.score) as score, MAX(ts.vs_prev) as change
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
  AND i.name = 'Effectiveness' AND i.item_type = 'core4'
  AND st.parent = false
GROUP BY st.name, i.name
ORDER BY change DESC NULLS LAST;
```

### Tool Satisfaction Analysis
```sql
-- Tool satisfaction scores (csat)
SELECT i.name as tool, AVG(ts.score) as avg_satisfaction, COUNT(DISTINCT st.name) as teams_using
FROM dx_snapshot_team_scores ts
JOIN dx_snapshot_teams st ON ts.snapshot_team_id = st.id
JOIN dx_snapshot_items i ON ts.item_id = i.id AND i.snapshot_id = ts.snapshot_id
WHERE ts.snapshot_id = (SELECT id FROM dx_snapshots ORDER BY end_date DESC LIMIT 1)
  AND i.item_type = 'csat' AND st.parent = false AND ts.score IS NOT NULL
GROUP BY i.name ORDER BY avg_satisfaction ASC;
```

## Reference Files

For detailed schema documentation, read these files:

| Domain | File | When to read |
|--------|------|--------------|
| DX Surveys/Scores | references/developer-experience.md | Survey data, snapshots, team scores, sentiment |
| Teams/Users | references/teams-users.md | Team structure, user profiles, AI adoption dates |
| Pull Requests | references/pull-requests.md | PR metrics, reviews, cycle times |
| Deployments | references/deployments-incidents.md | Deploy frequency, incidents, DORA metrics |
| AI Tools | references/ai-tools.md | AI assistant usage, adoption tracking |
| Issue Tracking | references/jira.md | Issues, sprints, story points |
| Catalog | references/catalog.md | Services, ownership, domains |
| Pipelines/Quality | references/pipelines-quality.md | CI/CD runs, code quality issues |
| Issues | references/issues-github.md | Source control issues, labels |
