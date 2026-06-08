# AI Tools and Adoption

## Overview
Tracking AI coding assistant usage, adoption rates, and impact metrics (e.g., GitHub Copilot).

## ai_tools
AI tool definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| built_in_key | text | Tool key (e.g., "copilot") |
| name | text | Tool display name |
| bespoke | boolean | Is custom/bespoke tool |
| enabled | boolean | Is enabled |

## ai_tool_daily_metrics
Daily AI tool usage per user.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| dx_user_id | bigint | FK to dx_users |
| ai_tool_id | bigint | FK to ai_tools |
| login | text | User login |
| date | date | Usage date |
| is_active | boolean | Was active on this day |
| source_table_id | bigint | Source record ID |

**Common queries:**
```sql
-- Daily active AI tool users
SELECT date, COUNT(DISTINCT dx_user_id) as active_users
FROM ai_tool_daily_metrics
WHERE is_active = true AND date > NOW() - INTERVAL '30 days'
GROUP BY date ORDER BY date;

-- AI adoption by team
SELECT t.name as team,
       COUNT(DISTINCT m.dx_user_id) as users_with_activity,
       COUNT(DISTINCT CASE WHEN m.is_active THEN m.dx_user_id END) as active_users
FROM ai_tool_daily_metrics m
JOIN dx_users u ON m.dx_user_id = u.id
JOIN dx_teams t ON u.team_id = t.id
WHERE m.date > NOW() - INTERVAL '30 days'
GROUP BY t.name ORDER BY active_users DESC;
```

## bespoke_ai_tool_daily_metrics
Custom AI tool metrics (same structure as ai_tool_daily_metrics).

## github_copilot_daily_usages
AI coding assistant daily usage (GitHub Copilot example).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| login | varchar | GitHub username |
| date | date | Usage date |
| enterprise_slug | varchar | Enterprise identifier |
| active | boolean | Was active |

**Common queries:**
```sql
-- Copilot adoption trend
SELECT date, COUNT(CASE WHEN active THEN 1 END) as active_users, COUNT(*) as total_users
FROM github_copilot_daily_usages
WHERE date > NOW() - INTERVAL '90 days'
GROUP BY date ORDER BY date;

-- Copilot activation rate
SELECT
    COUNT(DISTINCT CASE WHEN active THEN login END)::float /
    COUNT(DISTINCT login) * 100 as activation_rate
FROM github_copilot_daily_usages
WHERE date > NOW() - INTERVAL '30 days';
```

## github_copilot_usages
Aggregated AI assistant usage metrics.

## github_copilot_usage_breakdowns
Detailed AI assistant usage breakdowns (by language, editor, etc.).

## AI Adoption Tracking via dx_users

The dx_users table tracks adoption milestones:

| Column | Description |
|--------|-------------|
| ai_light_adoption_date | Date of light AI tool usage |
| ai_moderate_adoption_date | Date of moderate AI tool usage |
| ai_heavy_adoption_date | Date of heavy AI tool usage |

**Common queries:**
```sql
-- AI adoption stages by team
SELECT t.name,
       COUNT(*) as total_users,
       COUNT(u.ai_light_adoption_date) as light_adopters,
       COUNT(u.ai_moderate_adoption_date) as moderate_adopters,
       COUNT(u.ai_heavy_adoption_date) as heavy_adopters
FROM dx_users u
JOIN dx_teams t ON u.team_id = t.id
WHERE u.deleted_at IS NULL
GROUP BY t.name;

-- Time to adoption
SELECT
    AVG(ai_moderate_adoption_date - ai_light_adoption_date) as avg_days_light_to_moderate,
    AVG(ai_heavy_adoption_date - ai_moderate_adoption_date) as avg_days_moderate_to_heavy
FROM dx_users
WHERE ai_heavy_adoption_date IS NOT NULL;
```

## AI Impact Correlation

Correlate AI adoption with productivity metrics:

```sql
-- Compare PR metrics for AI adopters vs non-adopters
WITH user_adoption AS (
    SELECT id,
           CASE WHEN ai_moderate_adoption_date IS NOT NULL THEN 'adopter' ELSE 'non-adopter' END as status
    FROM dx_users WHERE deleted_at IS NULL
)
SELECT ua.status,
       COUNT(p.id) as prs,
       AVG(p.open_to_merge)/3600 as avg_cycle_hours,
       AVG(p.additions + p.deletions) as avg_lines_changed
FROM pull_requests p
JOIN user_adoption ua ON p.dx_user_id = ua.id
WHERE p.merged IS NOT NULL AND p.created > NOW() - INTERVAL '90 days'
GROUP BY ua.status;
```
