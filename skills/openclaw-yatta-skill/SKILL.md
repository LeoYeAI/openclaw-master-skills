---
name: yatta
description: Personal productivity system for task and capacity management. Create and organize tasks with rich attributes (priority, effort, complexity, tags), track time and streaks, manage capacity across projects and contexts, view Eisenhower Matrix prioritization, sync calendar subscriptions, handle delegation and follow-ups, and get AI-powered insights. Supports batch operations, multi-project workflows, and real-time capacity planning to prevent overcommitment. Security: v0.2.0 eliminates RCE vulnerability from v0.1.3 (shell/JSON injection in examples), adds endpoint verification, safe jq patterns throughout.
homepage: https://github.com/chrisagiddings/openclaw-yatta-skill
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"✅","requires":{"env":["YATTA_API_KEY","YATTA_API_URL"],"bins":["curl","jq"],"anyBins":["openssl","dig"]},"primaryEnv":"YATTA_API_KEY","disable-model-invocation":true,"capabilities":["task-management","project-management","context-management","comment-management","calendar-management","destructive-operations"],"credentials":{"type":"env","variables":[{"name":"YATTA_API_KEY","description":"Yatta! API key (yatta_...)","required":true},{"name":"YATTA_API_URL","description":"Yatta! API base URL","required":false,"default":"https://zunahvofybvxpptjkwxk.supabase.co/functions/v1"}]}}}
---

# Yatta! Skill

Interact with Yatta! task management system via API. Requires an API key from your Yatta! account.

## ⚠️ Security Warning

**This skill can perform DESTRUCTIVE operations on your Yatta! account:**

- **Task Management:** Create, update, archive, and batch-modify tasks
- **Project Management:** Create, update, and archive projects
- **Context Management:** Create contexts and assign them to tasks
- **Comment Management:** Add, update, and delete task comments
- **Calendar Management:** Create, sync, and modify calendar subscriptions
- **Follow-Up Management:** Update delegation schedules and mark complete
- **Capacity Management:** Trigger capacity computations

**Operation Types:**

**Read-Only Operations** (✅ Safe):
- List tasks, projects, contexts, comments
- Get analytics, insights, streaks
- View capacity and calendar data
- Get Eisenhower Matrix view
- All GET requests

**Destructive Operations** (⚠️ Modify or delete data):
- Create/update/archive tasks (POST, PUT, DELETE)
- Batch update tasks
- Create/update projects
- Create/assign contexts
- Add/update/delete comments
- Add/sync calendar subscriptions
- Update follow-up schedules
- All POST, PUT, DELETE requests

**Best Practices:**
1. **Review commands before running** - Check what the API call will do
2. **No undo for deletions** - Archived tasks can be recovered, but some operations are permanent
3. **Test on non-critical data first** - Create test tasks/projects to verify behavior
4. **Batch operations affect multiple items** - Be extra careful with batch updates
5. **Real-time sync** - Changes appear in Yatta! UI immediately

For detailed API operation documentation, see [API-REFERENCE.md](API-REFERENCE.md).

## Setup

### ⚠️ API Key Security

**Your Yatta! API key provides FULL access to your account:**
- Can create, read, update, and delete ALL tasks, projects, contexts
- Can modify calendar subscriptions and follow-up schedules
- Can archive data and trigger computations
- **No read-only scopes available** - keys have full permissions

**Security Best Practices:**
- Store keys in a secure password manager (1Password CLI recommended)
- Use environment variables, never hardcode keys in scripts
- Rotate keys regularly (every 90 days recommended)
- Create separate keys for different integrations
- Revoke unused keys immediately
- **Never commit keys to version control**

### 1. Get Your API Key

1. Log into Yatta! app
2. Go to Settings → API Keys
3. Create new key (e.g., "OpenClaw Integration")
4. Copy the `yatta_...` key
5. Store it securely

### 2. Configure the Skill

**Option A: Environment Variables (Recommended)**
```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc)
export YATTA_API_KEY="yatta_your_key_here"
export YATTA_API_URL="https://zunahvofybvxpptjkwxk.supabase.co/functions/v1"  # Default
```

**Option B: 1Password CLI (Most Secure)**
```bash
# Store key in 1Password
op item create --category=API_CREDENTIAL \
  --title="Yatta API Key" \
  api_key[password]="yatta_your_key_here"

# Use in commands
export YATTA_API_KEY=$(op read "op://Private/Yatta API Key/api_key")
```

### ⚠️ API Endpoint Verification

**The default API endpoint is hosted on Supabase:**

- **Default URL:** `https://zunahvofybvxpptjkwxk.supabase.co/functions/v1`
- **Project:** Yatta! production backend
- **Owner:** Chris Giddings (chris@chrisgiddings.net)
- **App:** https://yattadone.com

**Why Supabase?**
- Yatta! uses Supabase as its backend infrastructure
- The URL is a direct Supabase project endpoint
- Branded URL (api.yattadone.com) is on the roadmap

**Verification steps:**

1. **Verify app ownership:**
   - Visit https://yattadone.com
   - Check Settings → About or footer for API endpoint confirmation
   
2. **Check SSL certificate:**
   ```bash
   openssl s_client -connect zunahvofybvxpptjkwxk.supabase.co:443 \
     -servername zunahvofybvxpptjkwxk.supabase.co < /dev/null 2>&1 \
     | openssl x509 -noout -subject -issuer
   ```

3. **Run verification script:**
   ```bash
   # Automated endpoint verification
   bash scripts/verify-endpoint.sh
   ```

4. **Contact support if uncertain:**
   - Email: support@yattadone.com
   - Only send API keys to verified endpoints

**Branded URL (Coming Soon):**
- Future: `https://api.yattadone.com/v1`
- Current Supabase URL will continue to work
- Skill will auto-update default when branded URL is live

**Security note:**
Only send your API key to endpoints you trust and have verified.
If you prefer to wait for the branded API URL, that's a valid security choice.

### 3. Test Connection
   ```bash
   curl -s "$YATTA_API_URL/tasks" \
     -H "Authorization: Bearer $YATTA_API_KEY" \
     | jq '.[:3]'  # Show first 3 tasks
   ```

## 🔒 Security: Input Validation

**⚠️ CRITICAL: This skill is vulnerable to shell and JSON injection if user input is not properly sanitized.**

### Safe Coding Patterns (Required)

**ALL examples in this skill use safe patterns:**
- ✅ **JSON payloads:** Built with `jq -n --arg` (prevents JSON injection)
- ✅ **URL parameters:** Encoded with `jq -sRr @uri` (prevents shell injection)  
- ✅ **No direct string interpolation** in JSON or URLs

### Quick Reference

```bash
# ✅ SAFE: JSON construction
PAYLOAD=$(jq -n --arg title "$TITLE" '{title: $title}')
curl -d "$PAYLOAD" ...

# ✅ SAFE: URL encoding
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$API_URL/tasks/$TASK_ID_ENCODED" ...

# ✅ BEST: Use wrapper functions
source scripts/yatta-safe-api.sh
yatta_create_task "Finish report" "high"
```

### Why This Matters

**Unsafe patterns can lead to:**
- API key exfiltration
- Arbitrary command execution (RCE)
- Data manipulation and corruption

**See [SECURITY.md](SECURITY.md) for:**
- Detailed vulnerability examples
- Attack scenarios and impact
- Safe coding patterns
- Testing guidelines

**See [scripts/yatta-safe-api.sh](scripts/yatta-safe-api.sh) for:**
- Pre-built safe wrapper functions
- Ready-to-use examples
- Zero boilerplate

---

## 🎯 Invocation Policy

**This skill requires MANUAL invocation only.**

### Policy Details

**Setting:** `disable-model-invocation: true`

**What this means:**
- Agent will **NOT** automatically invoke Yatta! operations
- **User must explicitly request** each action
- No background task creation or modification
- All operations require clear user intent

### Why Manual-Only?

**Security rationale:**

1. **Full account access:** Yatta! API keys grant complete account access
2. **No read-only scopes:** No way to limit API key permissions
3. **Destructive operations:** Can delete/archive/modify data permanently
4. **User oversight required:** Changes should be reviewed before execution

### Examples

**❌ Autonomous (NOT allowed):**
```
User: "I should probably archive old tasks"
Agent: *silently archives tasks without confirmation*
```

**✅ Manual (Required):**
```
User: "Please archive tasks older than 30 days"
Agent: *executes explicit request, shows results*
```

### Policy Enforcement

**How it works:**
1. Skill metadata declares `disable-model-invocation: true`
2. OpenClaw respects this setting
3. Agent requires explicit user commands
4. No autonomous background operations

**Verification:**
```bash
# Check package.json
jq '.openclaw["disable-model-invocation"]' package.json
# Should output: true

# Check SKILL.md frontmatter
grep "disable-model-invocation" SKILL.md
# Should show: "disable-model-invocation":true
```

### If You See Unexpected Operations

**If Yatta! operations happen without your explicit request:**

1. **Stop immediately** - This indicates a policy violation
2. **Revoke API key** - Create new key in Yatta! Settings → API Keys
3. **File issue** - https://github.com/chrisagiddings/openclaw-yatta-skill/issues
4. **Report to OpenClaw** - Policy enforcement bug

**This should never happen** - manual invocation is a security requirement.

---

## Tasks API

### List Tasks

**All tasks:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

**Filter by status:**
```bash
# TODO tasks only
curl -s "$YATTA_API_URL/tasks?status=todo" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'

# Doing (active) tasks
curl -s "$YATTA_API_URL/tasks?status=doing" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'

# Completed tasks
curl -s "$YATTA_API_URL/tasks?status=done" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

**Filter by priority:**
```bash
# High priority tasks
curl -s "$YATTA_API_URL/tasks?priority=high" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {title, due_date, priority}'
```

**Filter by project:**
```bash
# Get project ID first
PROJECT_ID=$(curl -s "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | select(.name=="Website Redesign") | .id')

# Get tasks for that project (URL-encode query parameter)
PROJECT_ID_ENCODED=$(printf %s "$PROJECT_ID" | jq -sRr @uri)
curl -s "$YATTA_API_URL/tasks?project_id=$PROJECT_ID_ENCODED" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

**Filter by matrix state:**
```bash
# Delegated tasks
curl -s "$YATTA_API_URL/tasks?matrix_state=delegated" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {title, delegated_to, follow_up_date}'

# Waiting tasks
curl -s "$YATTA_API_URL/tasks?matrix_state=waiting" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

**Date range queries:**
```bash
# Tasks due this week
WEEK_END=$(date -v+7d "+%Y-%m-%d")
curl -s "$YATTA_API_URL/tasks?due_date_lte=$WEEK_END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {title, due_date}'

# Overdue tasks
TODAY=$(date "+%Y-%m-%d")
curl -s "$YATTA_API_URL/tasks?due_date_lte=$TODAY&status=todo" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {title, due_date}'
```

**Pagination:**
```bash
# First 50 tasks
curl -s "$YATTA_API_URL/tasks?limit=50&offset=0" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'

# Next 50 tasks
curl -s "$YATTA_API_URL/tasks?limit=50&offset=50" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

**Archived tasks:**
```bash
curl -s "$YATTA_API_URL/tasks?archived=true" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Create Task

**Simple task:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Finish report",
    "priority": "high"
  }' \
  | jq '.'
```

**Task with full details:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review Q1 numbers",
    "description": "Go through revenue, costs, and projections",
    "priority": "high",
    "due_date": "2026-02-15",
    "effort_points": 5,
    "project_id": "uuid-of-project",
    "matrix_state": "active"
  }' \
  | jq '.'
```

**Delegated task with follow-up:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Website redesign",
    "delegated_to": "Dev Team",
    "matrix_state": "delegated",
    "follow_up_schedule": {
      "type": "weekly",
      "day_of_week": "monday",
      "next_follow_up": "2026-02-17"
    }
  }' \
  | jq '.'
```

**Recurring task:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team standup",
    "recurrence_rule": {
      "frequency": "daily",
      "interval": 1,
      "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    },
    "effort_points": 1
  }' \
  | jq '.'
```

### Update Task

**Update single task:**
```bash
# ✅ SAFE: Use jq to build JSON payload
TASK_ID="uuid-of-task"
PAYLOAD=$(jq -n \
  --arg id "$TASK_ID" \
  --arg status "done" \
  --arg completed_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  '{id: $id, status: $status, completed_at: $completed_at}')

curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

**Batch update tasks:**
```bash
curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["uuid-1", "uuid-2", "uuid-3"],
    "priority": "high",
    "project_id": "project-uuid"
  }' \
  | jq '.'
```

### Archive Task

```bash
# ✅ SAFE: Use jq to build JSON payload
TASK_ID="uuid-of-task"
PAYLOAD=$(jq -n --arg id "$TASK_ID" '{id: $id}')

curl -s -X DELETE "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

## Projects API

### List Projects

```bash
# All projects
curl -s "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'

# With task counts
curl -s "$YATTA_API_URL/projects?with_counts=true" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {name, task_count, open_count}'
```

### Create Project

```bash
curl -s "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "description": "Complete overhaul of company site",
    "color": "#3b82f6",
    "icon": "🌐"
  }' \
  | jq '.'
```

### Update Project

```bash
# ✅ SAFE: Use jq to build JSON payload
PROJECT_ID="uuid-of-project"
PAYLOAD=$(jq -n \
  --arg id "$PROJECT_ID" \
  --arg name "Website Redesign v2" \
  --argjson archived false \
  '{id: $id, name: $name, archived: $archived}')

curl -s -X PUT "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

### Get Project Tasks

```bash
# ✅ SAFE: URL-encode path parameter
PROJECT_ID="uuid-of-project"
PROJECT_ID_ENCODED=$(printf %s "$PROJECT_ID" | jq -sRr @uri)

curl -s "$YATTA_API_URL/projects/$PROJECT_ID_ENCODED/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

## Contexts API

### List Contexts

```bash
# All contexts
curl -s "$YATTA_API_URL/contexts" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'

# With task counts
curl -s "$YATTA_API_URL/contexts?with_counts=true" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {name, task_count}'
```

### Create Context

```bash
curl -s "$YATTA_API_URL/contexts" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "@deep-focus",
    "color": "#8b5cf6",
    "icon": "🧠"
  }' \
  | jq '.'
```

### Assign Context to Task

```bash
# ✅ SAFE: Use jq to build JSON payload with arrays
TASK_ID="uuid-of-task"
CONTEXT_ID="uuid-of-context"

PAYLOAD=$(jq -n \
  --arg task_id "$TASK_ID" \
  --arg context_id "$CONTEXT_ID" \
  '{task_id: $task_id, context_ids: [$context_id]}')

curl -s -X POST "$YATTA_API_URL/contexts/assign" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

### Get Task Contexts

```bash
# ✅ SAFE: URL-encode path parameter
TASK_ID="uuid-of-task"
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)

curl -s "$YATTA_API_URL/tasks/$TASK_ID_ENCODED/contexts" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Get Context Tasks

```bash
# ✅ SAFE: URL-encode path parameter
CONTEXT_ID="uuid-of-context"
CONTEXT_ID_ENCODED=$(printf %s "$CONTEXT_ID" | jq -sRr @uri)

curl -s "$YATTA_API_URL/contexts/$CONTEXT_ID_ENCODED/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

## Comments API

### List Task Comments

```bash
# ✅ SAFE: URL-encode path parameter
TASK_ID="uuid-of-task"
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)

curl -s "$YATTA_API_URL/tasks/$TASK_ID_ENCODED/comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Add Comment

```bash
# ✅ SAFE: URL-encode path + jq for JSON
TASK_ID="uuid-of-task"
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
PAYLOAD=$(jq -n \
  --arg content "Waiting on client feedback before proceeding" \
  '{content: $content}')

curl -s -X POST "$YATTA_API_URL/tasks/$TASK_ID_ENCODED/comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

### Update Comment

```bash
# ✅ SAFE: Use jq to build JSON payload
COMMENT_ID="uuid-of-comment"
PAYLOAD=$(jq -n \
  --arg id "$COMMENT_ID" \
  --arg content "Client responded, moving forward" \
  '{id: $id, content: $content}')

curl -s -X PUT "$YATTA_API_URL/task-comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

### Delete Comment

```bash
# ✅ SAFE: Use jq to build JSON payload
COMMENT_ID="uuid-of-comment"
PAYLOAD=$(jq -n --arg id "$COMMENT_ID" '{id: $id}')

curl -s -X DELETE "$YATTA_API_URL/task-comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

## Follow-Ups API

### Get Today's Follow-Ups

```bash
curl -s "$YATTA_API_URL/follow-ups" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {title, delegated_to, follow_up_date}'
```

### Get Follow-Ups for Date

```bash
DATE="2026-02-15"
curl -s "$YATTA_API_URL/follow-ups?date=$DATE" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Mark Follow-Up Complete

```bash
# ✅ SAFE: URL-encode path parameter
TASK_ID="uuid-of-task"
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)

curl -s -X POST "$YATTA_API_URL/tasks/$TASK_ID_ENCODED/follow-up" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | jq '.'
```

### Update Follow-Up Schedule

```bash
# ✅ SAFE: URL-encode path + jq for JSON
TASK_ID="uuid-of-task"
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)

PAYLOAD=$(jq -n \
  --arg type "every_n_days" \
  --argjson interval 3 \
  --arg next_follow_up "2026-02-12" \
  '{type: $type, interval: $interval, next_follow_up: $next_follow_up}')

curl -s -X PUT "$YATTA_API_URL/tasks/$TASK_ID_ENCODED/follow-up-schedule" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | jq '.'
```

## Calendar API

### List Calendar Subscriptions

```bash
curl -s "$YATTA_API_URL/calendar/subscriptions" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Add Calendar Subscription

```bash
curl -s -X POST "$YATTA_API_URL/calendar/subscriptions" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Calendar",
    "ical_url": "https://calendar.google.com/calendar/ical/...",
    "default_context_id": "context-uuid"
  }' \
  | jq '.'
```

### Trigger Calendar Sync

```bash
# ✅ SAFE: URL-encode path parameter
SUBSCRIPTION_ID="uuid-of-subscription"
SUBSCRIPTION_ID_ENCODED=$(printf %s "$SUBSCRIPTION_ID" | jq -sRr @uri)

curl -s -X POST "$YATTA_API_URL/calendar/subscriptions/$SUBSCRIPTION_ID_ENCODED/sync" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### List Calendar Events

```bash
# Events for date range
START="2026-02-10"
END="2026-02-17"
curl -s "$YATTA_API_URL/calendar/events?start=$START&end=$END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

## Capacity API

### Get Today's Capacity

```bash
curl -s "$YATTA_API_URL/capacity/today" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '{date, utilization_percent, status, used_minutes, total_minutes}'
```

### Get Capacity for Date Range

```bash
START="2026-02-10"
END="2026-02-17"
curl -s "$YATTA_API_URL/capacity?start=$START&end=$END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.[] | {date, status, utilization_percent}'
```

### Trigger Capacity Computation

```bash
curl -s -X POST "$YATTA_API_URL/capacity/compute" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

## Analytics API

### Get Summary Insights

```bash
curl -s "$YATTA_API_URL/analytics/summary" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Get Velocity Metrics

```bash
curl -s "$YATTA_API_URL/analytics/velocity" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Get Task Distribution

```bash
curl -s "$YATTA_API_URL/analytics/distribution" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '{by_status, by_priority, by_matrix_state}'
```

### Get Streaks

```bash
curl -s "$YATTA_API_URL/analytics/streaks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

### Get AI Insights

```bash
curl -s "$YATTA_API_URL/analytics/insights" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '.'
```

## Matrix Endpoint

### Get Eisenhower Matrix View

```bash
curl -s "$YATTA_API_URL/tasks/matrix" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq '{do_first, schedule, delegate, eliminate}'
```

## Common Patterns

### Daily Workflow Automation

**Morning briefing:**
```bash
#!/bin/bash
echo "=== Today's Tasks ==="
curl -s "$YATTA_API_URL/tasks?status=todo&due_date_lte=$(date +%Y-%m-%d)" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "- [\(.priority)] \(.title)"'

echo ""
echo "=== Follow-Ups Due ==="
curl -s "$YATTA_API_URL/follow-ups" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "- \(.title) (delegated to: \(.delegated_to))"'

echo ""
echo "=== Capacity Status ==="
curl -s "$YATTA_API_URL/capacity/today" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '"Utilization: \(.utilization_percent)% - \(.status)"'
```

### Create Task from Email

```bash
#!/bin/bash
# Extract email subject and body
SUBJECT="$1"
BODY="$2"

curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "'"$SUBJECT"'",
    "description": "'"$BODY"'",
    "priority": "medium",
    "import_source": "email"
  }' \
  | jq -r '"Task created: \(.title)"'
```

### Weekly Planning Report

```bash
#!/bin/bash
WEEK_START=$(date -v+mon "+%Y-%m-%d")
WEEK_END=$(date -v+sun "+%Y-%m-%d")

echo "=== Week of $WEEK_START ==="
curl -s "$YATTA_API_URL/capacity?start=$WEEK_START&end=$WEEK_END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "\(.date): \(.status) (\(.utilization_percent)%)"'

echo ""
echo "=== Tasks Due This Week ==="
curl -s "$YATTA_API_URL/tasks?due_date_gte=$WEEK_START&due_date_lte=$WEEK_END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "[\(.due_date)] \(.title)"'
```

## Error Handling

**Check response status:**
```bash
RESPONSE=$(curl -s -w "\n%{http_code}" "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY")

STATUS=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$STATUS" -eq 200 ]; then
  echo "$BODY" | jq '.'
else
  echo "Error: HTTP $STATUS"
  echo "$BODY" | jq '.error'
fi
```

**Rate limit handling:**
```bash
RESPONSE=$(curl -s -i "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY")

# Check X-RateLimit headers
REMAINING=$(echo "$RESPONSE" | grep -i "X-RateLimit-Remaining" | cut -d' ' -f2)
RESET=$(echo "$RESPONSE" | grep -i "X-RateLimit-Reset" | cut -d' ' -f2)

if [ "$REMAINING" -lt 10 ]; then
  echo "Warning: Only $REMAINING requests remaining"
  echo "Rate limit resets at: $(date -r $RESET)"
fi
```

## Tips

- **Store API key securely:** Use 1Password CLI, env vars, or secrets manager
- **Use jq for filtering:** Pipe responses through `jq` for clean output
- **Batch operations:** Update multiple tasks at once when possible
- **Rate limits:** 100 requests/minute per API key
- **Date formats:** Always use ISO 8601 (YYYY-MM-DD for dates, YYYY-MM-DDTHH:MM:SSZ for timestamps)
- **Error responses:** Include `error` field with description

## Resources

- **API Documentation:** [Yatta! API Docs](https://yattadone.com/docs/api) (coming soon)
- **GitHub Repo:** https://github.com/chrisagiddings/openclaw-yatta-skill
- **Report Issues:** https://github.com/chrisagiddings/openclaw-yatta-skill/issues

## API URL Note

Currently using the direct Supabase Edge Functions URL for reliability:
```
https://zunahvofybvxpptjkwxk.supabase.co/functions/v1
```

Branded URLs (`yattadone.com/api`) will be available in a future release once proxy configuration is resolved with the hosting provider.
