# Yatta! API Reference

Complete documentation of all API operations, their behaviors, network calls, and security implications.

## Quick Reference

| API | Endpoints | Read-Only | Destructive | Real-time Sync |
|-----|-----------|-----------|-------------|----------------|
| **Tasks** | 6 | List, Get | Create, Update, Archive, Batch | ✅ |
| **Projects** | 4 | List, Get Tasks | Create, Update | ✅ |
| **Contexts** | 5 | List, Get Tasks | Create, Assign | ✅ |
| **Comments** | 4 | List | Create, Update, Delete | ✅ |
| **Follow-Ups** | 4 | List, Get by Date | Mark Complete, Update Schedule | ✅ |
| **Calendar** | 4 | List Subscriptions, List Events | Create, Sync | ✅ |
| **Capacity** | 3 | Get Today, Get Range | Trigger Compute | ✅ |
| **Analytics** | 5 | All (read-only) | None | N/A |
| **Matrix** | 1 | Get View | None | N/A |

**Total:** 36 operations (24 read-only, 12 destructive)

---

## Operation Details

### Tasks API (6 operations)

#### 1. List Tasks (Read-Only) ✅

**Endpoint:** `GET /tasks`

**Purpose:** Retrieve tasks with optional filtering

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks?status=todo&priority=high" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Query Parameters:**
- `status` - Filter by status (todo, doing, done)
- `priority` - Filter by priority (high, medium, low, none)
- `project_id` - Filter by project UUID
- `context_id` - Filter by context UUID
- `matrix_state` - Filter by Eisenhower state (active, delegated, waiting, someday)
- `due_date_gte/lte` - Date range filters
- `archived` - Include archived tasks (true/false)
- `limit` - Pagination limit (default: 100)
- `offset` - Pagination offset (default: 0)

**Response:** Array of task objects

---

#### 2. Get Task (Read-Only) ✅

**Endpoint:** `GET /tasks/:id`

**Purpose:** Get single task by ID

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks/$TASK_ID" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Single task object with all fields

---

#### 3. Create Task (Destructive) ⚠️

**Endpoint:** `POST /tasks`

**Purpose:** Create new task

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task name","priority":"high"}'
```

**Side Effects:**
- ⚠️ Creates new task in your account
- ⚠️ Appears in UI immediately
- ⚠️ Affects capacity calculations
- ⚠️ Can trigger notifications

**Required Fields:** `title`

**Optional Fields:** `description`, `priority`, `status`, `due_date`, `effort_points`, `project_id`, `matrix_state`, `delegated_to`, `follow_up_schedule`, `recurrence_rule`

**Undo:** Archive the task

---

#### 4. Update Task (Destructive) ⚠️

**Endpoint:** `PUT /tasks`

**Purpose:** Update existing task

**Network Call:**
```bash
curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$TASK_ID'","status":"done"}'
```

**Side Effects:**
- ⚠️ Modifies task data
- ⚠️ Changes appear in UI immediately
- ⚠️ Affects analytics and capacity
- ⚠️ Updating status to "done" marks task complete
- ⚠️ Can trigger recurrence if task has recurrence rule

**Required Fields:** `id`

**Updateable Fields:** Any task field except `id`, `created_at`, `user_id`

**Undo:** Update again with previous values (no version history)

---

#### 5. Batch Update Tasks (Destructive) ⚠️

**Endpoint:** `PUT /tasks` (with `ids` array)

**Purpose:** Update multiple tasks at once

**Network Call:**
```bash
curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ids":["uuid1","uuid2"],"priority":"high"}'
```

**Side Effects:**
- ⚠️ **AFFECTS MULTIPLE TASKS** - Be very careful
- ⚠️ All specified tasks updated with same values
- ⚠️ Changes appear in UI immediately
- ⚠️ Can accidentally change many tasks if IDs wrong

**Required Fields:** `ids` (array of UUIDs)

**Updateable Fields:** Same as single update

**Undo:** Batch update again with previous values (tedious)

---

#### 6. Archive Task (Destructive) ⚠️

**Endpoint:** `DELETE /tasks`

**Purpose:** Archive (soft-delete) a task

**Network Call:**
```bash
curl -s -X DELETE "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$TASK_ID'"}'
```

**Side Effects:**
- ⚠️ Archives the task (sets `archived=true`)
- ⚠️ Removes from active views
- ⚠️ Affects analytics (completion metrics)
- ⚠️ Can be recovered via UI

**Required Fields:** `id`

**Undo:** Update task with `archived=false`

---

### Projects API (4 operations)

#### 1. List Projects (Read-Only) ✅

**Endpoint:** `GET /projects`

**Purpose:** Get all projects

**Network Call:**
```bash
curl -s "$YATTA_API_URL/projects?with_counts=true" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Query Parameters:**
- `with_counts` - Include task counts (true/false)
- `archived` - Include archived projects (true/false)

**Response:** Array of project objects

---

#### 2. Create Project (Destructive) ⚠️

**Endpoint:** `POST /projects`

**Purpose:** Create new project

**Network Call:**
```bash
curl -s "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Project Name","color":"#3b82f6"}'
```

**Side Effects:**
- ⚠️ Creates new project
- ⚠️ Appears in UI immediately
- ⚠️ Can be assigned to tasks

**Required Fields:** `name`

**Optional Fields:** `description`, `color`, `icon`, `archived`

**Undo:** Archive the project

---

#### 3. Update Project (Destructive) ⚠️

**Endpoint:** `PUT /projects`

**Purpose:** Update existing project

**Network Call:**
```bash
curl -s -X PUT "$YATTA_API_URL/projects" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$PROJECT_ID'","name":"New Name"}'
```

**Side Effects:**
- ⚠️ Modifies project data
- ⚠️ Changes appear in UI and all associated tasks
- ⚠️ Renaming affects task organization

**Required Fields:** `id`

**Updateable Fields:** `name`, `description`, `color`, `icon`, `archived`

**Undo:** Update again with previous values

---

#### 4. Get Project Tasks (Read-Only) ✅

**Endpoint:** `GET /projects/:id/tasks`

**Purpose:** Get all tasks in a project

**Network Call:**
```bash
curl -s "$YATTA_API_URL/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of task objects

---

### Contexts API (5 operations)

#### 1. List Contexts (Read-Only) ✅

**Endpoint:** `GET /contexts`

**Purpose:** Get all contexts

**Network Call:**
```bash
curl -s "$YATTA_API_URL/contexts?with_counts=true" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Query Parameters:**
- `with_counts` - Include task counts (true/false)

**Response:** Array of context objects

---

#### 2. Create Context (Destructive) ⚠️

**Endpoint:** `POST /contexts`

**Purpose:** Create new context tag

**Network Call:**
```bash
curl -s "$YATTA_API_URL/contexts" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"@office","color":"#8b5cf6"}'
```

**Side Effects:**
- ⚠️ Creates new context
- ⚠️ Appears in UI immediately
- ⚠️ Can be assigned to tasks

**Required Fields:** `name`

**Optional Fields:** `color`, `icon`

**Undo:** Delete context (not implemented in API yet)

---

#### 3. Assign Context to Task (Destructive) ⚠️

**Endpoint:** `POST /contexts/assign`

**Purpose:** Tag task(s) with context(s)

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/contexts/assign" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_id":"'$TASK_ID'","context_ids":["'$CONTEXT_ID'"]}'
```

**Side Effects:**
- ⚠️ Adds context tags to task
- ⚠️ Affects task filtering and organization
- ⚠️ Changes appear in UI immediately

**Required Fields:** `task_id`, `context_ids` (array)

**Undo:** Manually remove context assignments (via UI)

---

#### 4. Get Task Contexts (Read-Only) ✅

**Endpoint:** `GET /tasks/:id/contexts`

**Purpose:** Get contexts assigned to a task

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks/$TASK_ID/contexts" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of context objects

---

#### 5. Get Context Tasks (Read-Only) ✅

**Endpoint:** `GET /contexts/:id/tasks`

**Purpose:** Get all tasks with a context

**Network Call:**
```bash
curl -s "$YATTA_API_URL/contexts/$CONTEXT_ID/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of task objects

---

### Comments API (4 operations)

#### 1. List Task Comments (Read-Only) ✅

**Endpoint:** `GET /tasks/:id/comments`

**Purpose:** Get all comments on a task

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks/$TASK_ID/comments" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of comment objects

---

#### 2. Create Comment (Destructive) ⚠️

**Endpoint:** `POST /tasks/:id/comments`

**Purpose:** Add comment to task

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/tasks/$TASK_ID/comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content":"Progress note"}'
```

**Side Effects:**
- ⚠️ Adds comment to task
- ⚠️ Appears in UI immediately
- ⚠️ Helps track task progress

**Required Fields:** `content`

**Undo:** Delete the comment

---

#### 3. Update Comment (Destructive) ⚠️

**Endpoint:** `PUT /task-comments`

**Purpose:** Edit existing comment

**Network Call:**
```bash
curl -s -X PUT "$YATTA_API_URL/task-comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$COMMENT_ID'","content":"Updated text"}'
```

**Side Effects:**
- ⚠️ Modifies comment text
- ⚠️ Changes appear in UI immediately
- ⚠️ No edit history (overwrites previous content)

**Required Fields:** `id`, `content`

**Undo:** Update again with previous content (if you saved it)

---

#### 4. Delete Comment (Destructive) ⚠️

**Endpoint:** `DELETE /task-comments`

**Purpose:** Remove comment from task

**Network Call:**
```bash
curl -s -X DELETE "$YATTA_API_URL/task-comments" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$COMMENT_ID'"}'
```

**Side Effects:**
- ⚠️ **PERMANENTLY DELETES COMMENT**
- ⚠️ Cannot be recovered
- ⚠️ Removes from UI immediately

**Required Fields:** `id`

**Undo:** None - deletion is permanent

---

### Follow-Ups API (4 operations)

#### 1. Get Today's Follow-Ups (Read-Only) ✅

**Endpoint:** `GET /follow-ups`

**Purpose:** Get delegated tasks due for follow-up today

**Network Call:**
```bash
curl -s "$YATTA_API_URL/follow-ups" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of tasks with follow-ups due today

---

#### 2. Get Follow-Ups by Date (Read-Only) ✅

**Endpoint:** `GET /follow-ups?date=YYYY-MM-DD`

**Purpose:** Get follow-ups for specific date

**Network Call:**
```bash
curl -s "$YATTA_API_URL/follow-ups?date=2026-02-15" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of tasks with follow-ups due on date

---

#### 3. Mark Follow-Up Complete (Destructive) ⚠️

**Endpoint:** `POST /tasks/:id/follow-up`

**Purpose:** Mark follow-up as done, schedule next

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/tasks/$TASK_ID/follow-up" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Side Effects:**
- ⚠️ Marks current follow-up complete
- ⚠️ Schedules next follow-up based on recurrence rule
- ⚠️ Updates task's `next_follow_up` date
- ⚠️ Changes appear in UI immediately

**Required Fields:** None (empty JSON object)

**Undo:** Manually update follow-up schedule

---

#### 4. Update Follow-Up Schedule (Destructive) ⚠️

**Endpoint:** `PUT /tasks/:id/follow-up-schedule`

**Purpose:** Change how often to follow up

**Network Call:**
```bash
curl -s -X PUT "$YATTA_API_URL/tasks/$TASK_ID/follow-up-schedule" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"weekly","day_of_week":"monday","next_follow_up":"2026-02-17"}'
```

**Side Effects:**
- ⚠️ Changes follow-up recurrence pattern
- ⚠️ Affects when task appears in follow-up list
- ⚠️ Updates next follow-up date

**Required Fields:** `type`, schedule fields depend on type

**Schedule Types:**
- `once` - Single follow-up (requires `next_follow_up`)
- `daily` - Every day
- `weekly` - Specific day of week (requires `day_of_week`)
- `every_n_days` - Every N days (requires `interval`)

**Undo:** Update schedule again with previous values

---

### Calendar API (4 operations)

#### 1. List Calendar Subscriptions (Read-Only) ✅

**Endpoint:** `GET /calendar/subscriptions`

**Purpose:** Get all calendar integrations

**Network Call:**
```bash
curl -s "$YATTA_API_URL/calendar/subscriptions" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of calendar subscription objects

---

#### 2. Add Calendar Subscription (Destructive) ⚠️

**Endpoint:** `POST /calendar/subscriptions`

**Purpose:** Connect external calendar (iCal/Google)

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/calendar/subscriptions" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Work Cal","ical_url":"https://..."}'
```

**Side Effects:**
- ⚠️ Creates calendar integration
- ⚠️ Fetches events from external calendar
- ⚠️ Can create tasks from calendar events
- ⚠️ May trigger initial sync

**Required Fields:** `name`, `ical_url`

**Optional Fields:** `default_context_id`, `auto_create_tasks`

**Undo:** Delete subscription (not in API yet, use UI)

---

#### 3. Trigger Calendar Sync (Destructive) ⚠️

**Endpoint:** `POST /calendar/subscriptions/:id/sync`

**Purpose:** Force sync with external calendar

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/calendar/subscriptions/$SUB_ID/sync" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:**
- ⚠️ Fetches latest events from external calendar
- ⚠️ May create new tasks from events
- ⚠️ May update existing calendar-linked tasks
- ⚠️ Changes appear in UI immediately

**Required Fields:** None

**Undo:** Delete auto-created tasks manually

---

#### 4. List Calendar Events (Read-Only) ✅

**Endpoint:** `GET /calendar/events?start=YYYY-MM-DD&end=YYYY-MM-DD`

**Purpose:** Get calendar events for date range

**Network Call:**
```bash
curl -s "$YATTA_API_URL/calendar/events?start=2026-02-10&end=2026-02-17" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of calendar event objects

---

### Capacity API (3 operations)

#### 1. Get Today's Capacity (Read-Only) ✅

**Endpoint:** `GET /capacity/today`

**Purpose:** Check today's capacity status

**Network Call:**
```bash
curl -s "$YATTA_API_URL/capacity/today" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Capacity object (utilization, status, minutes used/total)

---

#### 2. Get Capacity for Date Range (Read-Only) ✅

**Endpoint:** `GET /capacity?start=YYYY-MM-DD&end=YYYY-MM-DD`

**Purpose:** Check capacity for multiple days

**Network Call:**
```bash
curl -s "$YATTA_API_URL/capacity?start=2026-02-10&end=2026-02-17" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Array of capacity objects (one per day)

---

#### 3. Trigger Capacity Computation (Destructive) ⚠️

**Endpoint:** `POST /capacity/compute`

**Purpose:** Recalculate capacity for all days

**Network Call:**
```bash
curl -s -X POST "$YATTA_API_URL/capacity/compute" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:**
- ⚠️ Recalculates capacity metrics
- ⚠️ Updates capacity status for all days
- ⚠️ Changes appear in UI immediately
- ⚠️ May affect capacity bar colors/percentages

**Required Fields:** None

**Undo:** None needed (recomputation is safe)

---

### Analytics API (5 operations - All Read-Only) ✅

#### 1. Get Summary Insights

**Endpoint:** `GET /analytics/summary`

**Purpose:** Overview of tasks, completion rate, priorities

**Network Call:**
```bash
curl -s "$YATTA_API_URL/analytics/summary" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

---

#### 2. Get Velocity Metrics

**Endpoint:** `GET /analytics/velocity`

**Purpose:** Task completion rate over time

**Network Call:**
```bash
curl -s "$YATTA_API_URL/analytics/velocity" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

---

#### 3. Get Task Distribution

**Endpoint:** `GET /analytics/distribution`

**Purpose:** Task breakdown by status, priority, matrix state, effort

**Network Call:**
```bash
curl -s "$YATTA_API_URL/analytics/distribution" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

---

#### 4. Get Streaks

**Endpoint:** `GET /analytics/streaks`

**Purpose:** Completion streak tracking

**Network Call:**
```bash
curl -s "$YATTA_API_URL/analytics/streaks" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

---

#### 5. Get AI Insights

**Endpoint:** `GET /analytics/insights`

**Purpose:** AI-generated productivity insights

**Network Call:**
```bash
curl -s "$YATTA_API_URL/analytics/insights" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

---

### Matrix API (1 operation - Read-Only) ✅

#### 1. Get Eisenhower Matrix View

**Endpoint:** `GET /tasks/matrix`

**Purpose:** Get tasks organized by urgent/important quadrants

**Network Call:**
```bash
curl -s "$YATTA_API_URL/tasks/matrix" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

**Side Effects:** None

**Response:** Object with quadrants: `do_first`, `schedule`, `delegate`, `eliminate`

---

## Security Best Practices

### Before Running ANY API Call:

1. **Read the operation type** - Is it read-only or destructive?
2. **Check what will change** - Understand side effects
3. **Verify task/project IDs** - Make sure you're modifying the right thing
4. **Test with non-critical data** - Try on test tasks first
5. **Be extra careful with batch operations** - Affects multiple items
6. **Remember real-time sync** - Changes appear immediately

### Safe Workflow:

```bash
# 1. Get task details first (read-only)
curl -s "$YATTA_API_URL/tasks/$TASK_ID" \
  -H "Authorization: Bearer $YATTA_API_KEY" | jq '.'

# 2. Review what you'll change
echo "About to update task: $TASK_ID to status: done"

# 3. Make the change (destructive)
curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"'$TASK_ID'","status":"done"}'

# 4. Verify the change
curl -s "$YATTA_API_URL/tasks/$TASK_ID" \
  -H "Authorization: Bearer $YATTA_API_KEY" | jq '.status'
```

### Batch Operations - Extra Caution:

```bash
# ⚠️ DANGER: This updates ALL tasks with these IDs
# Always list the tasks first to verify what you're changing

# 1. Get the tasks
curl -s "$YATTA_API_URL/tasks?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[].id' > task_ids.txt

# 2. Review the IDs
echo "About to update $(wc -l < task_ids.txt) tasks"
cat task_ids.txt

# 3. Only proceed if correct
IDS=$(cat task_ids.txt | jq -R . | jq -s .)
curl -s -X PUT "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ids":'$IDS',"priority":"high"}'
```

---

## Error Handling

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not found (task/project doesn't exist)
- `429` - Rate limit exceeded (100 req/min)
- `500` - Server error

**Error Response Format:**
```json
{
  "error": "Description of what went wrong",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Rate Limiting:**
- **Limit:** 100 requests per minute per API key
- **Headers:** Check `X-RateLimit-Remaining` and `X-RateLimit-Reset`
- **Handling:** Implement exponential backoff

---

## Network Operations Summary

**All API calls go to:**
- `$YATTA_API_URL` (environment variable)
- Default: `https://zunahvofybvxpptjkwxk.supabase.co/functions/v1`
- HTTPS only (encrypted)
- Authenticated with Bearer token (YATTA_API_KEY)

**No other external services:**
- No analytics sent to third parties
- No telemetry
- All data stays in your Yatta! account

---

## Undo/Recovery Guide

| Operation | Undo Method |
|-----------|-------------|
| Create task | Archive the task |
| Update task | Update again with old values (no history) |
| Batch update | Update each task individually (tedious) |
| Archive task | Update with `archived=false` |
| Create project | Archive the project |
| Update project | Update again with old values |
| Create context | Delete via UI (not in API) |
| Assign context | Remove via UI (not in API) |
| Create comment | Delete the comment |
| Update comment | Update with old text (if saved) |
| Delete comment | **Cannot undo** - permanent |
| Calendar sync | Delete auto-created tasks |
| Follow-up complete | Update follow-up schedule manually |

**Important:** Most operations have no version history. Save data before modifying if you might need to revert!

---

## Tips for Safe API Usage

1. **Store responses before updates:** `curl ... | tee before.json | jq '.'`
2. **Use jq for safety:** Filter and verify before piping to destructive operations
3. **Start with read-only:** Get comfortable with List/Get operations first
4. **Test IDs:** Always verify UUIDs before using in updates/deletes
5. **Batch operations last:** Master single operations before trying batch
6. **Monitor rate limits:** Check response headers, implement delays
7. **Handle errors:** Check HTTP status codes, don't assume success

---

**Last Updated:** February 10, 2026  
**Skill Version:** 0.1.0  
**API Coverage:** 9/9 APIs (100%)
