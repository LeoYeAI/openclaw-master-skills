---
name: timedoctor
description: Integrates with TimeDoctor API to pull employee time tracking data, worklogs, statistics, and productivity metrics using simple Python scripts
version: 1.0.0
author: JehadurRE
metadata:
  clawdbot:
    emoji: "⏱️"
    requires:
      bins: ["python3"]
    install:
      pip: ["httpx>=0.27.0"]
    homepage: "https://github.com/JehadurRE/timedoctor-openclaw-skill"
    keywords: ["timetracking", "productivity", "employee-monitoring", "timedoctor", "workforce-analytics"]
---

# TimeDoctor Skill

Interact with TimeDoctor API for employee time tracking, activity logs, productivity statistics, and workforce analytics using simple Python CLI commands.

## What This Skill Does

Provides direct access to TimeDoctor's time tracking API through a Python CLI tool. Execute commands, get JSON data, present formatted results to users.

## Setup Instructions

### For Users: Getting TimeDoctor Credentials

**Option 1: Easy Setup (Recommended)**

Just provide your TimeDoctor email and password:

```bash
python3 timedoctor.py login --email "your-email@company.com" --password "your-password"
```

This returns a JWT token valid for 6 months. Copy the token and set it:

```bash
export TIMEDOCTOR_TOKEN="your-jwt-token-from-login-response"
```

**Option 2: Manual Token Setup**

If you already have a token or prefer manual setup:

```bash
# Required
export TIMEDOCTOR_TOKEN="your-jwt-token"

# Optional (can be discovered via get_authorization)
export TIMEDOCTOR_COMPANY_ID="your-company-id"
```

**For Multiple Accounts**: Users can switch accounts by changing the token:

```bash
# Account 1
export TIMEDOCTOR_TOKEN="token-for-account-1"
export TIMEDOCTOR_COMPANY_ID="company-id-1"

# Account 2  
export TIMEDOCTOR_TOKEN="token-for-account-2"
export TIMEDOCTOR_COMPANY_ID="company-id-2"
```

**Quick Setup Workflow**:
```bash
# 1. Login to get token
python3 timedoctor.py login --email "user@company.com" --password "password"

# 2. Copy token from response and set it
export TIMEDOCTOR_TOKEN="1jxExVs9WGsWccrq2ysMKMZVZlTVyTZc15tlgcWF_Qns"

# 3. Discover available companies
python3 timedoctor.py get_authorization

# 4. Set company ID (optional)
export TIMEDOCTOR_COMPANY_ID="aFtR8crWxHTeLzIm"

# 5. Start using commands
python3 timedoctor.py get_today_worklog --company-id $TIMEDOCTOR_COMPANY_ID
```

## How to Use This Skill

### Core Command Pattern

All commands follow this pattern:
```bash
python3 timedoctor.py COMMAND [--company-id ID] [OPTIONS]
```

The script is located in the skill directory and returns JSON output.

### Key Commands

**Login** (Get JWT Token):
```bash
python3 timedoctor.py login --email "user@company.com" --password "password"
```
Returns: JWT token valid for 6 months

**Discover Available Companies**:
```bash
python3 timedoctor.py get_authorization
```
Returns: User info and list of accessible companies with IDs

**Today's Activity**:
```bash
python3 timedoctor.py get_today_worklog --company-id COMPANY_ID
```

**This Week's Stats**:
```bash
python3 timedoctor.py get_this_week_stats --company-id COMPANY_ID
```

**This Month's Stats**:
```bash
python3 timedoctor.py get_this_month_stats --company-id COMPANY_ID
```

**Custom Date Range**:
```bash
python3 timedoctor.py get_worklog \
  --company-id COMPANY_ID \
  --from-date "2024-03-01T00:00:00Z" \
  --to-date "2024-03-31T00:00:00Z"
```

**List Users**:
```bash
python3 timedoctor.py get_users --company-id COMPANY_ID
```

**List Projects**:
```bash
python3 timedoctor.py get_projects --company-id COMPANY_ID
```

**Filter by Users**:
```bash
python3 timedoctor.py get_today_worklog --company-id COMPANY_ID --user-ids "123,456,789"
```

## Understanding TimeDoctor Account Structure

### Account Hierarchy

```
TimeDoctor User Account (requires TIMEDOCTOR_TOKEN)
  └── Company A (ID: 12345)
      ├── User 1
      ├── User 2
      └── Projects...
  └── Company B (ID: 67890)
      ├── User 3
      ├── User 4
      └── Projects...
  └── Company C (ID: 11111)
      └── Users...
```

### Key Concepts

1. **One Token = One User Account**
   - Each TIMEDOCTOR_TOKEN represents one TimeDoctor user login
   - Example: john@acme.com has one token

2. **One Account Can Access Multiple Companies**
   - A user can be part of multiple companies
   - Same token works for all companies they have access to
   - Switch companies using different `--company-id`

3. **Different User Accounts Need Different Tokens**
   - john@acme.com has token A
   - jane@beta.com has token B
   - To switch from John to Jane, change TIMEDOCTOR_TOKEN

### Example Scenarios

**Scenario 1: User with Multiple Companies**
```
User: "Show my companies"
Agent: Runs get_authorization
Response shows:
  - Acme Corp (12345)
  - Beta Startup (67890)
  - Gamma LLC (11111)

Agent: "You have access to 3 companies. Which one?"
User: "Acme Corp"
Agent: Uses --company-id 12345 for all subsequent requests
```

**Scenario 2: Switching Companies**
```
User: "Now show me Beta Startup's data"
Agent: Remembers Beta Startup = 67890 from earlier
Agent: Uses --company-id 67890
No token change needed!
```

**Scenario 3: Switching User Accounts**
```
User: "I want to use my other TimeDoctor account"
Agent: "You need to update your token. Run:
        export TIMEDOCTOR_TOKEN='your-other-token'"
User: Updates token
Agent: Runs get_authorization with new token
Agent: Shows new list of companies for that account
```

## Agent Instructions

### When User Asks About TimeDoctor Data

Follow this workflow:

1. **Check if User Has Token**
   - If `TIMEDOCTOR_TOKEN` is not set, help them login:
     ```
     "To get started, I need your TimeDoctor credentials.
     
     I'll run: python3 timedoctor.py login --email YOUR_EMAIL --password YOUR_PASSWORD
     
     What's your TimeDoctor email and password?"
     ```
   - After getting credentials, run login command
   - Extract token from response
   - Tell user to set: `export TIMEDOCTOR_TOKEN="extracted-token"`
   - Explain token is valid for 6 months

2. **Discover and Present Available Companies**
   - ALWAYS run `get_authorization` first if company_id is not known
   - Parse the response to extract all accessible companies
   - Present to user in a clear format:
     ```
     You have access to these TimeDoctor companies:
     1. Company A (ID: 12345)
     2. Company B (ID: 67890)
     3. Company C (ID: 11111)
     
     Which company would you like to use?
     ```
   - Wait for user to select
   - Remember the selected company_id for subsequent requests in this session

3. **Execute Appropriate Command**
   - Match user's request to the right command
   - Use convenience commands when possible (get_today_worklog, get_this_week_stats, etc.)
   - Always include `--company-id` parameter with the selected company

4. **Handle Multiple Accounts**
   - One TIMEDOCTOR_TOKEN = One user account
   - One user account can have access to multiple companies
   - To switch to a completely different TimeDoctor user account, user must update TIMEDOCTOR_TOKEN
   - To switch between companies under same account, just use different --company-id

5. **Parse and Format Output**
   - Check for `{"error": "..."}` first
   - Convert JSON to readable format (tables, lists, summaries)
   - Highlight key metrics (total hours, productive time, etc.)
   - Format durations as "X hours Y minutes"

6. **Error Recovery**
   - `"TIMEDOCTOR_TOKEN environment variable not set"` → Help user login with email/password
   - `"company_id required"` → Run get_authorization to discover companies
   - `"401 Unauthorized"` → Token expired, user needs to login again (6-month validity)

### Date Format Rules

ALWAYS use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

**Examples**:
- Start of day: `2024-03-22T00:00:00Z`
- End of day: `2024-03-23T00:00:00Z`
- For single day: from `2024-03-22T00:00:00Z` to `2024-03-23T00:00:00Z`

**Calculating Dates**:
- Today: Use `get_today_worklog` (automatic)
- This week: Use `get_this_week_stats` (automatic, Monday to today)
- This month: Use `get_this_month_stats` (automatic, 1st to today)
- Custom: Calculate dates and use `get_worklog` or `get_stats_total`

### Response Formatting Guidelines

**For Worklogs**:
- Show as table: User | Start Time | End Time | Duration | Activity
- Group by user or by date depending on context
- Summarize total hours at bottom

**For Statistics**:
- Show key metrics: Total Time, Productive Time, Unproductive Time, Idle Time
- Calculate percentages (e.g., "75% productive")
- Highlight outliers or unusual patterns

**For Lists** (users, projects, tasks):
- Show as numbered or bulleted list
- Include relevant IDs for follow-up queries
- Limit to top 10-20 unless user asks for more

## Common Workflows

### Workflow 0: First Time Setup - Login and Get Token

```
User: "I want to use TimeDoctor"

Steps:
1. Check if TIMEDOCTOR_TOKEN is set
2. If not, ask for credentials:
   
   "To get started, I need your TimeDoctor login credentials.
   
   What's your TimeDoctor email and password?"

3. User provides: "email@company.com" and "password123"
4. Run: python3 timedoctor.py login --email "email@company.com" --password "password123"
5. Parse response and extract token
6. Tell user:
   
   "Great! I got your token. It's valid for 6 months (until September 2026).
   
   Please set it in your environment:
   export TIMEDOCTOR_TOKEN='1jxExVs9WGsWccrq2ysMKMZVZlTVyTZc15tlgcWF_Qns'
   
   Once set, I can pull your TimeDoctor data."

7. After user confirms, proceed to Workflow 1 to discover companies
```

### Workflow 1: First Time Setup - Discover Companies

```
User: "Show me today's activity"

Steps:
1. Check if you know the company_id for this session
2. If not, run: python3 timedoctor.py get_authorization
3. Parse response and present companies:
   
   "I found these TimeDoctor companies you have access to:
   
   1. Acme Corp (ID: 12345) - 45 users
   2. Beta Inc (ID: 67890) - 12 users
   3. Gamma LLC (ID: 11111) - 8 users
   
   Which company would you like to check?"

4. User responds: "Acme Corp" or "1" or "12345"
5. Remember company_id = 12345 for this session
6. Run: python3 timedoctor.py get_today_worklog --company-id 12345
7. Parse JSON and create table:
   | User | Hours Worked | Productive % | Projects |
8. Add summary: "Total: X hours across Y users"
```

### Workflow 2: Daily Team Report (Company Already Known)

```
User: "Show today's activity for the team"

Steps:
1. Use remembered company_id from session
2. Run: python3 timedoctor.py get_today_worklog --company-id COMPANY_ID
3. Parse JSON and create table:
   | User | Hours Worked | Productive % | Projects |
4. Add summary: "Total: X hours across Y users"
```

### Workflow 3: Switching Between Companies

```
User: "Show me stats for Beta Inc instead"

Steps:
1. Run: python3 timedoctor.py get_authorization
2. Find "Beta Inc" in the companies list
3. Extract company_id (67890)
4. Update session to remember new company_id
5. Confirm: "Switched to Beta Inc (ID: 67890)"
6. Run requested command with new company_id
```

### Workflow 4: Individual User Report

```
User: "Show today's activity for the team"

Steps:
1. Check if TIMEDOCTOR_COMPANY_ID is set in environment
2. If not, run: python3 timedoctor.py get_authorization
3. Extract company_id from response
4. Run: python3 timedoctor.py get_today_worklog --company-id COMPANY_ID
5. Parse JSON and create table:
   | User | Hours Worked | Productive % | Projects |
6. Add summary: "Total: X hours across Y users"
```

### Workflow 2: Individual User Report

```
User: "How much did John work this week?"

Steps:
1. Run: python3 timedoctor.py get_users --company-id COMPANY_ID
2. Find John's user_id in response
3. Run: python3 timedoctor.py get_this_week_stats --company-id COMPANY_ID --user-ids "JOHN_ID"
4. Parse and present:
   - Total hours: X
   - Productive time: Y (Z%)
   - Top projects: ...
   - Daily breakdown: Mon: X hrs, Tue: Y hrs, ...
```

### Workflow 5: Project Time Analysis

```
User: "How much time was spent on Project Alpha last month?"

Steps:
1. Run: python3 timedoctor.py get_projects --company-id COMPANY_ID
2. Find "Project Alpha" and get its project_id
3. Calculate last month's date range (1st to last day)
4. Run: python3 timedoctor.py get_stats_total \
   --company-id COMPANY_ID \
   --from-date "YYYY-MM-01T00:00:00Z" \
   --to-date "YYYY-MM-31T23:59:59Z" \
   --project-id PROJECT_ID
5. Present breakdown by user and total
```

### Workflow 6: Switching TimeDoctor User Accounts

```
User: "I want to use my other TimeDoctor account"

Steps:
1. Explain: "To switch to a different TimeDoctor user account, you need to update your token."
2. Provide instructions:
   
   "Please run these commands with your other account's token:
   
   export TIMEDOCTOR_TOKEN="your-other-account-token"
   
   Then let me know when you're ready."

3. After they confirm, run: python3 timedoctor.py get_authorization
4. Present available companies for the new account:
   
   "Now connected as [User Name]. You have access to:
   
   1. Company X (ID: 99999)
   2. Company Y (ID: 88888)
   
   Which company would you like to use?"

5. Remember the selected company_id for this session
```

## Session Management

### Remember Company Selection

Once a user selects a company, remember it for the entire conversation session:

```
Session State:
- current_company_id: 12345
- current_company_name: "Acme Corp"
- current_token_user: "john@acme.com"
```

### When to Re-prompt for Company

Ask user to select company again when:
- First request in a new session
- User explicitly asks to switch companies
- User says "use a different company"
- Error indicates wrong company access

### Don't Re-prompt When

- User makes multiple requests in same session
- Company is already known and working
- User hasn't indicated they want to change

## Presenting Company Lists

### Format 1: Numbered List (Preferred)

```
You have access to these TimeDoctor companies:

1. Acme Corporation (ID: 12345)
   - 45 active users
   - Role: Admin

2. Beta Startup (ID: 67890)
   - 12 active users
   - Role: Manager

3. Gamma Consulting (ID: 11111)
   - 8 active users
   - Role: User

Which company would you like to use? (Enter number, name, or ID)
```

### Format 2: Simple List

```
Available companies:
• Acme Corporation (12345)
• Beta Startup (67890)
• Gamma Consulting (11111)

Which one?
```

### Format 3: Single Company

```
You have access to: Acme Corporation (ID: 12345)

I'll use this company for your requests.
```

## Handling User Selection

Accept any of these formats:
- Number: "1" or "2"
- Name: "Acme Corporation" or "Acme" or "acme"
- ID: "12345"

Match flexibly:
- Case-insensitive name matching
- Partial name matching (if unambiguous)
- Direct ID matching

## Available Commands Reference

### Authentication
- `login` - Login with email/password to get JWT token (valid 6 months)
- `get_authorization` - Get user info and available companies
- `get_companies` - List all accessible companies
- `get_company` - Get specific company details

### Users
- `get_users` - List users in company
- `get_user` - Get specific user details
- `get_managed_users` - Get users managed by a manager

### Activity & Worklogs
- `get_activity_worklog` - Detailed work activity log
- `get_activity_timeuse_stats` - Time usage statistics
- `get_disconnectivity` - Offline/disconnected periods
- `get_today_worklog` - Today's worklog (convenience)

### Statistics
- `get_stats_total` - Aggregated total statistics
- `get_stats_category` - Stats by productivity category (4=Productive, 3=Neutral, 2=Unproductive, 0=Unrated)
- `get_stats_summary` - Summary stats over time
- `get_stats_work_life` - Work-life balance stats
- `get_stats_shift` - Shift compliance stats
- `get_stats_outliers` - Unusual activity patterns
- `get_this_week_stats` - This week's stats (convenience)
- `get_this_month_stats` - This month's stats (convenience)

### Timesheet
- `get_timesheet_total` - Timesheet totals
- `get_timesheet_summary` - Timesheet summary

### Projects & Tasks
- `get_projects` - List projects
- `get_project` - Get project details
- `get_tasks` - List tasks
- `get_task` - Get task details

### Groups & Schedules
- `get_groups` - List groups/teams
- `get_group` - Get group details
- `get_work_schedules` - List work schedules
- `get_work_schedule` - Get schedule details
- `get_work_schedule_issues` - Schedule violations
- `get_leave_stats` - Leave/time-off stats

### Payroll & Files
- `get_users_payroll` - User payroll info
- `get_company_payroll_settings` - Company payroll settings
- `get_files` - Screenshots/screencasts
- `get_categories` - Productivity categories
- `get_unrated_categories_count` - Count of unrated items

## Command Options

Common options across commands:
- `--company-id COMPANY_ID` - Required for most commands
- `--user-ids "123,456"` - Filter by specific users (comma-separated)
- `--from-date "2024-03-01T00:00:00Z"` - Start date (ISO 8601)
- `--to-date "2024-03-31T00:00:00Z"` - End date (ISO 8601)
- `--project-id PROJECT_ID` - Filter by project
- `--page 1` - Page number for pagination
- `--limit 100` - Results per page (max 1000)

## Tips for Effective Use

1. **Always check for errors first** - Look for `{"error": "..."}` in JSON output
2. **Use convenience commands** - `get_today_worklog` is easier than calculating today's dates
3. **Cache company_id** - Once discovered, remember it for the session
4. **Format for readability** - Convert JSON to tables, charts, or summaries
5. **Provide context** - When showing stats, explain what they mean
6. **Handle pagination** - For large datasets, use `--page` and `--limit`
7. **Multiple accounts** - Each token accesses one user account, but can access multiple companies under that account

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `TIMEDOCTOR_TOKEN environment variable not set` | Token not configured | User needs to set `export TIMEDOCTOR_TOKEN="..."` |
| `company_id required` | Missing company ID | Run `get_authorization` to discover company_id |
| `401 Unauthorized` | Token expired or invalid | User needs new token (6-month validity) |
| `httpx module not found` | Dependencies not installed | Run `pip3 install -r requirements.txt` |
| No data returned | No activity in date range | Check date range and verify users have activity |

## Author

**JehadurRE** (Jehadur Rahman Emran)
- Student, Developer, and Learner
- GitHub: https://github.com/JehadurRE
- Created simple Python CLI tool for TimeDoctor API integration

## License

MIT
