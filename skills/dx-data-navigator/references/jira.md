# Issue Tracking Integration

## Overview
Project management data including issues, sprints, boards, and workflow tracking (e.g., Jira).

## jira_issues
Jira issue/ticket data.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| connection_id | bigint | Jira connection reference |
| source_id | text | Jira issue ID |
| issue_type_id | bigint | FK to jira_issue_types |
| project_id | bigint | FK to jira_projects |
| resolution_id | bigint | FK to jira_resolutions |
| status_id | bigint | FK to jira_statuses |
| priority_id | bigint | FK to jira_priorities |
| user_id | bigint | Assignee (FK to jira_users) |
| creator_id | bigint | Creator (FK to jira_users) |
| reporter_id | bigint | Reporter (FK to jira_users) |
| source_url | text | Jira URL |
| summary | text | Issue title |
| key | text | Issue key (e.g., PROJ-123) |
| parent_key | text | Parent issue key |
| story_points | numeric | Story points estimate |
| resolution_date | timestamp | When resolved |
| due_date | timestamp | Due date |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last update |
| started_at | timestamp | Work started |
| completed_at | timestamp | Work completed |
| cycle_time | integer | Cycle time in seconds |
| deleted_at | timestamp | Soft delete |

**Common queries:**
```sql
-- Issue throughput by project
SELECT p.name as project, COUNT(*) as completed_issues,
       AVG(i.cycle_time)/3600 as avg_cycle_hours
FROM jira_issues i
JOIN jira_projects p ON i.project_id = p.id
WHERE i.completed_at IS NOT NULL AND i.completed_at > NOW() - INTERVAL '30 days'
GROUP BY p.name ORDER BY completed_issues DESC;

-- Story points delivered by team
SELECT t.name as team, SUM(i.story_points) as points_delivered
FROM jira_issues i
JOIN jira_users ju ON i.user_id = ju.id
JOIN dx_users u ON ju.email = u.email
JOIN dx_teams t ON u.team_id = t.id
WHERE i.completed_at > NOW() - INTERVAL '30 days'
GROUP BY t.name ORDER BY points_delivered DESC;

-- Cycle time distribution
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cycle_time)/3600 as median_hours,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY cycle_time)/3600 as p75_hours,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cycle_time)/3600 as p95_hours
FROM jira_issues
WHERE completed_at > NOW() - INTERVAL '90 days' AND cycle_time IS NOT NULL;
```

## jira_projects
Jira project definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira project ID |
| key | varchar | Project key |
| name | text | Project name |
| project_type_key | text | Project type |
| private | boolean | Is private |
| archived_at | timestamp | Archive time |
| deleted_at | timestamp | Soft delete |

## jira_sprints
Sprint definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira sprint ID |
| name | text | Sprint name |
| state | text | Sprint state (active, closed, future) |
| start_date | timestamp | Sprint start |
| end_date | timestamp | Sprint end |
| complete_date | timestamp | Actual completion |
| activated_date | timestamp | When activated |
| deleted_at | timestamp | Soft delete |

**Common queries:**
```sql
-- Sprint velocity
SELECT s.name, COUNT(i.id) as issues_completed, SUM(i.story_points) as points
FROM jira_sprints s
JOIN jira_issue_sprints jis ON s.id = jis.sprint_id
JOIN jira_issues i ON jis.issue_id = i.id
WHERE s.state = 'closed' AND i.completed_at IS NOT NULL
GROUP BY s.id, s.name ORDER BY s.complete_date DESC LIMIT 10;
```

## jira_issue_types
Issue type definitions (Story, Bug, Task, Epic, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira type ID |
| name | text | Type name |
| description | text | Type description |

## jira_statuses
Workflow status definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira status ID |
| name | text | Status name |
| category | text | Status category |

## jira_priorities
Priority definitions.

## jira_resolutions
Resolution definitions.

## jira_issue_status_changes
Status change history for cycle time analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| issue_id | bigint | FK to jira_issues |
| from_status_id | bigint | Previous status |
| to_status_id | bigint | New status |
| changed_at | timestamp | Change time |

## jira_boards
Agile boards.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira board ID |
| name | text | Board name |
| type | text | Board type (scrum, kanban) |

## jira_board_issues
Issues on boards.

## jira_issue_sprints
Issue-sprint associations.

## jira_issue_links
Issue relationships/links.

## jira_issue_labels / jira_labels
Issue labeling.

## jira_users
Jira user profiles.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | Jira user ID |
| account_id | text | Atlassian account ID |
| display_name | text | Display name |
| email | text | Email address |

## jira_custom_fields / jira_issue_custom_field_values
Custom field definitions and values.

## jira_allocations (Time tracking)

### jira_allocation_rules
Allocation rule definitions.

### jira_issue_allocations
Time allocations per issue.

### jira_daily_issue_allocations
Daily allocation tracking.

### jira_allocation_limits
Allocation limits/budgets.
