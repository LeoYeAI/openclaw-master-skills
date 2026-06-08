# Pull Requests and Code Review

## Overview
Pull request data from source control platforms (e.g., GitHub), including review metrics and cycle times.

## pull_requests
Normalized pull request data across sources.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source | text | Source platform (github) |
| repo_id | bigint | FK to repos |
| dx_user_id | bigint | FK to dx_users (author) |
| bot_authored | boolean | PR created by bot |
| title | text | PR title |
| base_ref | text | Target branch |
| head_ref | text | Source branch |
| merge_commit_sha | text | Merge commit SHA |
| open_to_merge | integer | Seconds from open to merge |
| open_to_first_review | integer | Seconds from open to first review |
| open_to_first_approval | integer | Seconds from open to first approval |
| open_to_merge_business_hours | integer | Business hours from open to merge |
| open_to_first_review_business_hours | integer | Business hours to first review |
| open_to_first_approval_business_hours | integer | Business hours to first approval |
| additions | integer | Lines added |
| deletions | integer | Lines deleted |
| created | timestamp | PR creation time |
| updated | timestamp | Last update time |
| merged | timestamp | Merge time |
| closed | timestamp | Close time |
| draft | boolean | Is draft PR |
| reverted | boolean | Was reverted |
| ready_for_review_at | timestamp | When marked ready for review |
| weight | numeric | PR weight/size metric |
| classification | text | PR classification |
| tz | text | Timezone for business hours calc |
| deleted | boolean | Soft delete flag |

**Key metrics:**
- `open_to_merge`: Total cycle time in seconds
- `open_to_first_review`: Time waiting for first review
- `open_to_first_approval`: Time to get approval
- Business hour variants exclude non-working hours

**Common queries:**
```sql
-- PR cycle time metrics for last 90 days
SELECT
    COUNT(*) as total_prs,
    AVG(open_to_merge)/3600 as avg_hours_to_merge,
    AVG(open_to_first_review)/3600 as avg_hours_to_first_review,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY open_to_merge)/3600 as median_hours_to_merge
FROM pull_requests
WHERE merged IS NOT NULL AND created > NOW() - INTERVAL '90 days';

-- PR throughput by team
SELECT t.name, COUNT(*) as pr_count, AVG(p.open_to_merge)/3600 as avg_cycle_hours
FROM pull_requests p
JOIN dx_users u ON p.dx_user_id = u.id
JOIN dx_teams t ON u.team_id = t.id
WHERE p.merged IS NOT NULL AND p.created > NOW() - INTERVAL '30 days'
GROUP BY t.name ORDER BY pr_count DESC;

-- Large PRs (potential review bottlenecks)
SELECT title, additions, deletions, open_to_merge/3600 as hours_to_merge
FROM pull_requests
WHERE merged IS NOT NULL AND (additions + deletions) > 500
ORDER BY created DESC LIMIT 20;
```

## pull_request_reviews
Code reviews on pull requests.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source | text | Source platform |
| dx_user_id | bigint | FK to dx_users (reviewer) |
| pull_request_id | bigint | FK to pull_requests |
| repo_id | bigint | FK to repos |
| time_since_request | integer | Seconds since review requested |
| time_since_request_business_hours | integer | Business hours since request |
| comment_count | integer | Number of comments |
| review_type | text | Review outcome type |
| created | timestamp | Review submission time |
| bot_authored | boolean | Review by bot |

**Common queries:**
```sql
-- Review response times by reviewer
SELECT u.name, COUNT(*) as reviews, AVG(r.time_since_request)/3600 as avg_response_hours
FROM pull_request_reviews r
JOIN dx_users u ON r.dx_user_id = u.id
WHERE r.created > NOW() - INTERVAL '30 days'
GROUP BY u.name ORDER BY reviews DESC;
```

## pull_request_commits
Commits within pull requests.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| pull_request_id | bigint | FK to pull_requests |
| sha | text | Commit SHA |
| message | text | Commit message |
| authored_at | timestamp | Authoring time |

## repos
Repository definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source | text | Source platform (github) |
| name | text | Repository name |
| default_branch | text | Default branch name |
| organization | text | Organization name |
| api_accessible | boolean | Can access via API |
| archived | boolean | Is archived |
| external_id | text | External identifier |

## GitHub-specific tables

### github_pulls
Raw GitHub PR data with additional GitHub-specific fields.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| source_id | bigint | GitHub PR ID |
| repository_id | bigint | FK to github_repositories |
| user_id | bigint | FK to github_users |
| number | bigint | PR number |
| title | text | PR title |
| head_ref / base_ref | text | Branch references |
| created / merged / closed | timestamp | Lifecycle timestamps |
| additions / deletions / changed_files | integer | Change metrics |
| commits | integer | Commit count |
| draft | boolean | Is draft |
| jira_issue_id | bigint | Linked Jira issue |
| issue_tracker_key | text | Issue tracker reference |

### github_reviews
Raw GitHub review data.

### github_review_requests
Review request tracking.

### github_pull_files
Files changed in PRs.

### github_pull_commits
Commits in GitHub PRs.

### github_pull_labels
Labels on PRs.

### github_repositories
GitHub repository details including sync status.

### github_organizations
GitHub organization data.

### github_users
GitHub user profiles.

### github_teams / github_team_memberships
GitHub team structure.
