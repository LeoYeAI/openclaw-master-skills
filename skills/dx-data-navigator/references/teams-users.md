# Teams and Users

## Overview
Organization structure including teams, users, groups, tags, and hierarchies.

## dx_teams
Team definitions with contributor counts.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | External identifier |
| source_parent_id | text | Parent team external ID |
| source_manager_id | text | Manager external ID |
| name | text | Team name |
| parent | boolean | Is this a parent team? |
| flattened_parent | text | Flattened parent hierarchy |
| contributors | integer | Number of contributors |
| deleted_at | timestamp | Soft delete timestamp |
| reference_id | text | Reference identifier |

**Common queries:**
```sql
-- Get all active teams with contributors
SELECT name, contributors FROM dx_teams
WHERE deleted_at IS NULL ORDER BY contributors DESC;

-- Get team hierarchy
SELECT t.name, p.name as parent_name
FROM dx_teams t
LEFT JOIN dx_teams p ON t.source_parent_id = p.source_id
WHERE t.deleted_at IS NULL;
```

## dx_users
Individual developers/users.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | External identifier |
| team_id | bigint | FK to dx_teams |
| name | text | User name |
| email | text | Email address |
| github_username | text | GitHub username |
| gitlab_username | text | GitLab username |
| additional_github_username | text | Secondary GitHub username |
| developer | text | Developer classification |
| avatar | text | Avatar URL |
| start_date | timestamp | Employment start date |
| ai_light_adoption_date | date | Light AI tool adoption date |
| ai_moderate_adoption_date | date | Moderate AI tool adoption date |
| ai_heavy_adoption_date | date | Heavy AI tool adoption date |
| tz | text | Timezone |
| protected | boolean | Protected user flag |
| deleted_at | timestamp | Soft delete timestamp |

**Common queries:**
```sql
-- Get users by team
SELECT u.name, u.email, u.github_username, t.name as team
FROM dx_users u
JOIN dx_teams t ON u.team_id = t.id
WHERE u.deleted_at IS NULL;

-- AI adoption tracking
SELECT name, ai_light_adoption_date, ai_moderate_adoption_date, ai_heavy_adoption_date
FROM dx_users WHERE ai_light_adoption_date IS NOT NULL;
```

## dx_team_hierarchies
Closure table for team hierarchy traversal.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| ancestor_id | bigint | Ancestor team ID |
| descendant_id | bigint | Descendant team ID |
| generations | bigint | Number of generations between |

**Common queries:**
```sql
-- Get all descendants of a team
SELECT d.name FROM dx_team_hierarchies h
JOIN dx_teams d ON h.descendant_id = d.id
WHERE h.ancestor_id = :team_id AND h.generations > 0;
```

## dx_groups
User groups for permissions/organization.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | text | External identifier |
| name | text | Group name |
| owner_id | bigint | Owner user ID |

## dx_group_memberships
Group membership associations.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| dx_group_id | bigint | FK to dx_groups |
| dx_user_id | bigint | FK to dx_users |

## dx_tags / dx_tag_groups / dx_user_tags
Tagging system for categorizing users.

**dx_tag_groups:** Categories of tags
**dx_tags:** Individual tags within groups
**dx_user_tags:** User-tag associations

```sql
-- Get users with specific tags
SELECT u.name, t.name as tag
FROM dx_users u
JOIN dx_user_tags ut ON u.id = ut.user_id
JOIN dx_tags t ON ut.tag_id = t.id;
```

## dx_versioned_teams / dx_versioned_team_members
Point-in-time team snapshots for historical analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| versioned_team_date_id | bigint | Date version reference |
| team_id | bigint | FK to dx_teams |
| parent_id | bigint | Parent team at that time |
| name | text | Team name at that time |
| is_parent | boolean | Was parent team at that time |

## identities
Cross-platform identity mapping.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| dx_user_id | bigint | FK to dx_users |
| source_id | bigint | External source ID |
| source | text | Source platform (github, jira, etc.) |
