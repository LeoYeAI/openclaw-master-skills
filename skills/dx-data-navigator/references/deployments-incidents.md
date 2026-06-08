# Deployments and Incidents

## Overview
Deployment tracking, incident management, and change failure metrics.

## deployments
Deployment records across environments.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| reference_id | text | External reference |
| service_id | bigint | Service being deployed |
| deployment_service_id | bigint | FK to deployment_services |
| repository | text | Repository name |
| commit_sha | text | Deployed commit |
| merge_commit_shas | array | Related merge commits |
| environment | text | Target environment (dev, stage, prod, production) |
| deployed_at | timestamp | Deployment time |
| success | boolean | Deployment success status |
| service | text | Service name |
| source_url | text | Source URL |
| source_name | text | Source system |
| integration_branch | text | Branch deployed |
| attributed_at | timestamp | Attribution time |
| deployment_inference_rule_id | bigint | Inference rule used |

**Common queries:**
```sql
-- Deployment frequency by environment
SELECT environment, COUNT(*) as deploys,
       COUNT(CASE WHEN success THEN 1 END) as successful
FROM deployments
WHERE deployed_at > NOW() - INTERVAL '30 days'
GROUP BY environment;

-- Daily deployment count (deploy frequency metric)
SELECT DATE(deployed_at) as day, COUNT(*) as deploys
FROM deployments
WHERE deployed_at > NOW() - INTERVAL '90 days'
GROUP BY DATE(deployed_at) ORDER BY day;

-- Deployments by team
SELECT t.name as team, COUNT(*) as deploys
FROM deployments d
JOIN deployment_services ds ON d.deployment_service_id = ds.id
JOIN dx_catalog_entity_owners eo ON ds.service_id = eo.entity_id
JOIN dx_teams t ON eo.team_id = t.id
WHERE d.deployed_at > NOW() - INTERVAL '30 days'
GROUP BY t.name ORDER BY deploys DESC;
```

## deployment_services
Services that can be deployed.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| service_id | bigint | FK to catalog entity |
| name | text | Service name |
| source | text | Source system |

## deployment_metadata
Additional deployment metadata.

## deployment_inference_rules
Rules for inferring deployments from other data.

## incidents
Incident records from external sources.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| name | text | Incident title/name |
| priority | text | Priority level (1 - Critical, 2 - High, 3 - Moderate, 4 - Low, 5 - Planning) |
| source | text | Source system |
| source_id | text | External ID |
| source_url | text | Link to incident |
| started_at | timestamp | Incident start time |
| resolved_at | timestamp | Resolution time |
| started_to_resolved | integer | Resolution time in seconds |
| deleted | boolean | Soft delete flag |

**Common queries:**
```sql
-- Incident metrics
SELECT
    COUNT(*) as total_incidents,
    COUNT(CASE WHEN priority = '1 - Critical' THEN 1 END) as critical,
    COUNT(CASE WHEN priority = '2 - High' THEN 1 END) as high,
    AVG(started_to_resolved)/3600 as avg_resolution_hours
FROM incidents
WHERE started_at > NOW() - INTERVAL '90 days' AND deleted = false;

-- Mean time to resolution by priority
SELECT priority, COUNT(*) as count, AVG(started_to_resolved)/3600 as avg_hours
FROM incidents
WHERE resolved_at IS NOT NULL AND deleted = false
GROUP BY priority ORDER BY priority;

-- Incidents over time
SELECT DATE_TRUNC('week', started_at) as week, COUNT(*) as incidents
FROM incidents
WHERE started_at > NOW() - INTERVAL '6 months' AND deleted = false
GROUP BY week ORDER BY week;
```

## incident_services
Links incidents to affected services.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| incident_id | bigint | FK to incidents |
| service_id | bigint | FK to catalog entity |

## incident_metadata
Additional incident metadata.

## DORA Metrics Calculations

### Deploy Frequency
```sql
SELECT COUNT(*)::float / 30 as daily_deploy_frequency
FROM deployments
WHERE deployed_at > NOW() - INTERVAL '30 days'
  AND environment IN ('prod', 'production');
```

### Change Fail Percentage
```sql
WITH deploys AS (
    SELECT COUNT(*) as total FROM deployments
    WHERE deployed_at > NOW() - INTERVAL '30 days'
    AND environment IN ('prod', 'production')
),
failures AS (
    SELECT COUNT(*) as failed FROM incidents
    WHERE started_at > NOW() - INTERVAL '30 days'
    -- Add logic to link incidents to deployments
)
SELECT (failures.failed::float / NULLIF(deploys.total, 0)) * 100 as change_fail_pct
FROM deploys, failures;
```

### Mean Time to Recovery (MTTR)
```sql
SELECT AVG(started_to_resolved)/3600 as mttr_hours
FROM incidents
WHERE resolved_at IS NOT NULL
  AND started_at > NOW() - INTERVAL '90 days'
  AND priority IN ('1 - Critical', '2 - High');
```
