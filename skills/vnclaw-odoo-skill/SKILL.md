---
name: vnclaw-odoo-skill
description: "Integrate with Odoo 17 via XML-RPC API. Use when: managing projects, tasks, calendar events, time off requests, helpdesk tickets, knowledge articles, documents, or timesheets in Odoo 17. Supports read, create, and update operations only. No delete allowed."
argument-hint: "Describe what you want to do in Odoo 17 (e.g., 'list all open tasks in project X', 'create a time off request')"
---

# VNClaw — Odoo 17 Integration Skill

## Execution Rules (MUST follow)

1. **ALWAYS run the command immediately.** Never ask the user to confirm or explain what the command does before running it. Translate the request → pick the command → execute it in one step.
2. **Never say "Would you like me to execute this?"** — just execute it.
3. **Never ask "Do you want me to run this?"** — just run it.
4. **If the command fails**, show the error and try to fix it. Do not ask the user for help diagnosing unless you have exhausted all options.
5. **Credentials**: If env vars are missing, inform the user which variable is missing and stop. Do not ask for the value interactively.

## Path Resolution

**IMPORTANT:** All commands below use `SKILL_SCRIPTS` as shorthand for the absolute path to the scripts directory. The skill may be installed in two locations — resolve it by checking both:

```bash
# Resolve SKILL_SCRIPTS from workspace (.github/skills/) or global (~/.vscode/extensions/ or ~/skills/)
SKILL_SCRIPTS="$(
  # 1. Check workspace: .github/skills/vnclaw-odoo-skill/scripts
  _ws_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  _ws_path="$_ws_root/.github/skills/vnclaw-odoo-skill/scripts"
  # 2. Global fallback locations
  _global_path="$HOME/.vnclaw/skills/vnclaw-odoo-skill/scripts"
  _global_path2="$HOME/.openclaw/skills/vnclaw-odoo-skill/scripts"

  if [ -d "$_ws_path" ]; then
    echo "$_ws_path"
  elif [ -d "$_global_path" ]; then
    echo "$_global_path"
  elif [ -d "$_global_path2" ]; then
    echo "$_global_path2"
  else
    # Last resort: search filesystem
    find "$HOME" /opt -type d -name vnclaw-odoo-skill -path '*/skills/*' 2>/dev/null | head -1 | sed 's|$|/scripts|'
  fi
)"
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

Possible install locations:

| Location type | Path |
|---------------|------|
| Workspace skill | `<git-root>/.github/skills/vnclaw-odoo-skill/scripts/` |
| User global (vnclaw) | `~/.vnclaw/skills/vnclaw-odoo-skill/scripts/` |
| User global (openclaw) | `~/.openclaw/skills/vnclaw-odoo-skill/scripts/` |

## Environment Variables (Required)

Credentials are loaded from environment variables. **Never hardcode credentials.**

| Variable | Description |
|----------|-------------|
| `ODOO_URL` | Base URL (e.g., `https://mycompany.odoo.com`) |
| `ODOO_DB` | Database name |
| `ODOO_USERNAME` | Login username (email) |
| `ODOO_API_KEY` | API key or password |

## Common Features (All Modules)

All module scripts share these capabilities:

- **`--my`** — Filter to current authenticated user's records
- **Name-based lookups** — Use `--user "Alice"`, `--project "Website"` etc. instead of IDs
- **Date shortcuts** — `--today`, `--yesterday`, `--this-week`, `--last-week`, `--this-month`, `--last-month`, `--this-year`
- **Custom date range** — `--date-from 2026-03-01 --date-to 2026-03-31`
- **Log notes** — `log-note` action to post internal notes on records (where supported)
- **Notify** — `notify` action to schedule activity notifications by user name (where supported)
- **JSON output** — All scripts output JSON to stdout, logs go to stderr

> **DATE FIELD RULE for tasks.py**: Date shortcuts filter `date_deadline` by default.
> To filter by **when a task was created**, always add `--date-field created`.
> To filter by **when a task was last updated**, use `--date-field updated`.

## Natural Language → Command Mapping

Use this table to translate common user requests into the correct command:

| User says... | Command |
|---|---|
| "my tasks" | `tasks.py list --my` |
| "my tasks this week" / "tasks with deadline this week" | `tasks.py list --my --this-week` |
| "tasks I created this week" / "tasks created this week" | `tasks.py list --my --this-week --date-field created` |
| "tasks created today" | `tasks.py list --my --today --date-field created` |
| "tasks created this month" | `tasks.py list --my --this-month --date-field created` |
| "tasks updated today" / "recently modified tasks" | `tasks.py list --my --today --date-field updated` |
| "my timesheets this week" | `timesheets.py list --my --this-week` |
| "log 2 hours on project X" | `timesheets.py log --project "X" --hours 2 --description "..."` |
| "my timesheet summary this month" | `timesheets.py summary --my --this-month` |
| "my calendar today" / "my meetings today" | `calendar_events.py list --my --today` |
| "my tickets" / "tickets assigned to me" | `helpdesk.py list --my` |
| "my leave requests this year" | `time_off.py list --my --this-year` |

## Quick Decision: Which Script to Use

| User wants to... | Script | Example |
|-------------------|--------|---------|
| List/view/create/update **tasks** | `tasks.py` | `python3 $SKILL_SCRIPTS/tasks.py list --my --this-week` |
| List/view/create/update **projects** | `projects.py` | `python3 $SKILL_SCRIPTS/projects.py list --my` |
| Log/view/update **timesheets** | `timesheets.py` | `python3 $SKILL_SCRIPTS/timesheets.py log --project "Website" --hours 2 --description "review"` |
| List/view/create/update **calendar events** | `calendar_events.py` | `python3 $SKILL_SCRIPTS/calendar_events.py list --my --today` |
| List/view/create/update **helpdesk tickets** | `helpdesk.py` | `python3 $SKILL_SCRIPTS/helpdesk.py list --my --this-week` |
| List/view/create/update **time off requests** | `time_off.py` | `python3 $SKILL_SCRIPTS/time_off.py list --my --this-year` |
| List/view/create/update **knowledge articles** | `knowledge.py` | `python3 $SKILL_SCRIPTS/knowledge.py list --my --published` |
| List/view/create/update **documents** | `documents.py` | `python3 $SKILL_SCRIPTS/documents.py list --folder "HR"` |
| Access **any user-defined / custom model** | `custom_app.py` | `python3 $SKILL_SCRIPTS/custom_app.py list crm.lead --my --this-month` |
| **Test connection** to Odoo | `odoo_core.py` | `python3 $SKILL_SCRIPTS/odoo_core.py test-connection` |

---

## Module: Tasks (`tasks.py`)

Manages `project.task`. Actions: `list`, `get`, `create`, `update`, `log-note`, `notify`, `stages`.

**Date filter field** — use `--date-field` to choose which date to filter on:
- `deadline` *(default)* — filters by `date_deadline`
- `created` — filters by `create_date` (when the task was created)
- `updated` — filters by `write_date` (when the task was last modified)

```bash
# My tasks
python3 $SKILL_SCRIPTS/tasks.py list --my

# My tasks CREATED this week  ← "created" requires --date-field created
python3 $SKILL_SCRIPTS/tasks.py list --my --this-week --date-field created

# My tasks CREATED today
python3 $SKILL_SCRIPTS/tasks.py list --my --today --date-field created

# My tasks CREATED this month
python3 $SKILL_SCRIPTS/tasks.py list --my --this-month --date-field created

# Tasks with a DEADLINE this week (default behavior, --date-field deadline is implicit)
python3 $SKILL_SCRIPTS/tasks.py list --my --this-week

# Tasks assigned to a specific user (by name) created this week
python3 $SKILL_SCRIPTS/tasks.py list --user "Alice" --this-week --date-field created

# Tasks in a project (by name)
python3 $SKILL_SCRIPTS/tasks.py list --project "Website Redesign"

# Search tasks by keyword
python3 $SKILL_SCRIPTS/tasks.py list --search "login bug"

# Overdue tasks
python3 $SKILL_SCRIPTS/tasks.py list --overdue

# Tasks in a stage (by name)
python3 $SKILL_SCRIPTS/tasks.py list --stage "In Progress"

# Tasks by tag
python3 $SKILL_SCRIPTS/tasks.py list --tag "urgent"

# Get task detail
python3 $SKILL_SCRIPTS/tasks.py get 42

# Create a task (project and assignee by name)
python3 $SKILL_SCRIPTS/tasks.py create --name "Fix login bug" --project "Website" --assign "Alice" --deadline 2026-04-01

# Update task stage (by name) and assignee (by name)
python3 $SKILL_SCRIPTS/tasks.py update 42 --stage "Done" --assign "Bob"

# Log an internal note on a task
python3 $SKILL_SCRIPTS/tasks.py log-note 42 --body "Waiting for client feedback"

# Notify a user via activity
python3 $SKILL_SCRIPTS/tasks.py notify 42 --user "Alice" --summary "Please review this task"

# List available stages
python3 $SKILL_SCRIPTS/tasks.py stages
```

## Module: Projects (`projects.py`)

Manages `project.project`. Actions: `list`, `get`, `create`, `update`, `log-note`, `notify`, `stages`.

```bash
# Projects I manage
python3 $SKILL_SCRIPTS/projects.py list --my

# Filter by manager name
python3 $SKILL_SCRIPTS/projects.py list --manager "Alice"

# Search projects
python3 $SKILL_SCRIPTS/projects.py list --search "Website"

# Active projects only + favorites
python3 $SKILL_SCRIPTS/projects.py list --active-only --favorites

# Get project details
python3 $SKILL_SCRIPTS/projects.py get 1

# Create a project with manager by name
python3 $SKILL_SCRIPTS/projects.py create --name "Website Redesign" --manager "Alice"

# Update project stage and dates
python3 $SKILL_SCRIPTS/projects.py update 1 --stage "In Progress" --date-start 2026-04-01 --date-end 2026-06-30

# Log note on project
python3 $SKILL_SCRIPTS/projects.py log-note 1 --body "Kickoff meeting completed"

# Notify project manager
python3 $SKILL_SCRIPTS/projects.py notify 1 --user "Alice" --summary "Budget review needed"

# List project stages
python3 $SKILL_SCRIPTS/projects.py stages
```

## Module: Timesheets (`timesheets.py`)

Manages `account.analytic.line`. Actions: `list`, `summary`, `log`, `update`.

```bash
# My timesheets this week
python3 $SKILL_SCRIPTS/timesheets.py list --my --this-week

# Timesheets by user name
python3 $SKILL_SCRIPTS/timesheets.py list --user "Alice" --this-month

# Timesheets by employee name
python3 $SKILL_SCRIPTS/timesheets.py list --employee "Alice Smith"

# Timesheets for a project (by name)
python3 $SKILL_SCRIPTS/timesheets.py list --project "Website Redesign"

# Custom date range
python3 $SKILL_SCRIPTS/timesheets.py list --date-from 2026-03-01 --date-to 2026-03-31

# Summary (hours grouped by project/task)
python3 $SKILL_SCRIPTS/timesheets.py summary --my --this-month

# Log a timesheet entry (project by name)
python3 $SKILL_SCRIPTS/timesheets.py log --project "Website Redesign" --hours 2.5 --description "Code review"

# Log for specific date
python3 $SKILL_SCRIPTS/timesheets.py log --project "Website" --hours 3 --description "Dev" --date 2026-03-17

# Update a timesheet entry
python3 $SKILL_SCRIPTS/timesheets.py update 15 --hours 4 --description "Updated"
```

## Module: Calendar Events (`calendar_events.py`)

Manages `calendar.event`. Actions: `list`, `get`, `create`, `update`.

```bash
# My events today
python3 $SKILL_SCRIPTS/calendar_events.py list --my --today

# My events this week
python3 $SKILL_SCRIPTS/calendar_events.py list --my --this-week

# Events where a specific person is attending (by name)
python3 $SKILL_SCRIPTS/calendar_events.py list --attendee "Alice"

# Events by organizer
python3 $SKILL_SCRIPTS/calendar_events.py list --organizer "Bob"

# Search events
python3 $SKILL_SCRIPTS/calendar_events.py list --search "Sprint"

# Custom date range
python3 $SKILL_SCRIPTS/calendar_events.py list --date-from 2026-03-20 --date-to 2026-03-25

# Get event details
python3 $SKILL_SCRIPTS/calendar_events.py get 10

# Create a meeting with attendees by name
python3 $SKILL_SCRIPTS/calendar_events.py create --name "Sprint Planning" --start "2026-03-20 09:00:00" --stop "2026-03-20 10:00:00" --attendees "Alice, Bob, Carol" --location "Room A"

# Reschedule
python3 $SKILL_SCRIPTS/calendar_events.py update 10 --start "2026-03-20 14:00:00" --stop "2026-03-20 15:00:00"
```

## Module: Helpdesk (`helpdesk.py`)

Manages `helpdesk.ticket`. Actions: `list`, `get`, `create`, `update`, `log-note`, `notify`, `stages`.

```bash
# My assigned tickets
python3 $SKILL_SCRIPTS/helpdesk.py list --my

# Tickets assigned to a user (by name)
python3 $SKILL_SCRIPTS/helpdesk.py list --user "Alice"

# Tickets from a customer (by name)
python3 $SKILL_SCRIPTS/helpdesk.py list --customer "Acme Corp"

# Search + date filter
python3 $SKILL_SCRIPTS/helpdesk.py list --search "login" --this-week

# High-priority tickets by team
python3 $SKILL_SCRIPTS/helpdesk.py list --priority 2 --team "Support"

# Filter by stage name
python3 $SKILL_SCRIPTS/helpdesk.py list --stage "In Progress"

# Get ticket details
python3 $SKILL_SCRIPTS/helpdesk.py get 5

# Create a ticket (assign and customer by name)
python3 $SKILL_SCRIPTS/helpdesk.py create --name "Login page broken" --team "Support" --assign "Alice" --customer "Acme Corp"

# Update ticket stage and assignee (by name)
python3 $SKILL_SCRIPTS/helpdesk.py update 5 --stage "Solved" --assign "Bob"

# Log note on ticket
python3 $SKILL_SCRIPTS/helpdesk.py log-note 5 --body "Escalated to engineering"

# Notify a user
python3 $SKILL_SCRIPTS/helpdesk.py notify 5 --user "Alice" --summary "Please investigate"

# List available stages
python3 $SKILL_SCRIPTS/helpdesk.py stages
```

## Module: Time Off (`time_off.py`)

Manages `hr.leave`. Actions: `list`, `get`, `create`, `update`, `leave-types`.

```bash
# My leave requests
python3 $SKILL_SCRIPTS/time_off.py list --my

# Leave requests by user name
python3 $SKILL_SCRIPTS/time_off.py list --user "Alice"

# By employee name
python3 $SKILL_SCRIPTS/time_off.py list --employee "Alice Smith"

# Filter by state
python3 $SKILL_SCRIPTS/time_off.py list --state validate

# Filter by leave type name
python3 $SKILL_SCRIPTS/time_off.py list --leave-type "Sick Time Off"

# This year's leaves
python3 $SKILL_SCRIPTS/time_off.py list --my --this-year

# List available leave types
python3 $SKILL_SCRIPTS/time_off.py leave-types

# Create a leave request (employee and type by name)
python3 $SKILL_SCRIPTS/time_off.py create --date-from "2026-03-25 08:00:00" --date-to "2026-03-26 17:00:00" --leave-type "Paid Time Off" --name "Personal day"

# Get leave details
python3 $SKILL_SCRIPTS/time_off.py get 12
```

## Module: Knowledge (`knowledge.py`)

Manages `knowledge.article`. Actions: `list`, `get`, `create`, `update`.

```bash
# My articles
python3 $SKILL_SCRIPTS/knowledge.py list --my

# Articles by author name
python3 $SKILL_SCRIPTS/knowledge.py list --author "Alice"

# Published articles only
python3 $SKILL_SCRIPTS/knowledge.py list --published

# Root-level articles only
python3 $SKILL_SCRIPTS/knowledge.py list --root-only

# Search articles
python3 $SKILL_SCRIPTS/knowledge.py list --search "onboarding"

# Filter by category
python3 $SKILL_SCRIPTS/knowledge.py list --category workspace

# Get article with body content
python3 $SKILL_SCRIPTS/knowledge.py get 5

# Create an article under a parent (by name)
python3 $SKILL_SCRIPTS/knowledge.py create --name "Setup Guide" --parent-name "Engineering" --body "<h1>Getting Started</h1>"

# Update article content
python3 $SKILL_SCRIPTS/knowledge.py update 5 --body "<p>Updated content</p>"
```

## Module: Documents (`documents.py`)

Manages `documents.document`. Actions: `list`, `get`, `create`, `update`, `folders`.

```bash
# My documents
python3 $SKILL_SCRIPTS/documents.py list --my

# Documents by owner name
python3 $SKILL_SCRIPTS/documents.py list --owner "Alice"

# Documents in a folder (by name)
python3 $SKILL_SCRIPTS/documents.py list --folder "HR Documents"

# Search documents
python3 $SKILL_SCRIPTS/documents.py list --search "invoice"

# Filter by type and date
python3 $SKILL_SCRIPTS/documents.py list --type binary --this-month

# Filter by tag
python3 $SKILL_SCRIPTS/documents.py list --tag "contracts"

# List available folders
python3 $SKILL_SCRIPTS/documents.py folders

# Get document details
python3 $SKILL_SCRIPTS/documents.py get 3

# Create a URL-type document (folder by name, owner by name)
python3 $SKILL_SCRIPTS/documents.py create --name "Design Spec" --folder "Engineering" --owner "Alice" --url "https://example.com/spec"

# Update document folder
python3 $SKILL_SCRIPTS/documents.py update 3 --folder "Archive"
```

## Module: Custom App (`custom_app.py`)

For **any Odoo model not covered by the dedicated scripts** — CRM, Sales, Purchase, Inventory, Manufacturing, Accounting, or any custom app installed in the Odoo instance.

Recommended workflow:
1. Discover the model technical name with `models`
2. Inspect available fields with `fields`
3. Then `list`, `get`, `create`, `update` as needed

```bash
# --- Discovery ---

# Search for models by name (find the technical model name)
python3 $SKILL_SCRIPTS/custom_app.py models --search "CRM"
python3 $SKILL_SCRIPTS/custom_app.py models --search "Sale Order"
python3 $SKILL_SCRIPTS/custom_app.py models --module crm

# Inspect fields of a model
python3 $SKILL_SCRIPTS/custom_app.py fields crm.lead
python3 $SKILL_SCRIPTS/custom_app.py fields crm.lead --search "stage"
python3 $SKILL_SCRIPTS/custom_app.py fields sale.order --type many2one

# --- Reading ---

# List records with auto-detected default fields
python3 $SKILL_SCRIPTS/custom_app.py list crm.lead

# My CRM leads this month
python3 $SKILL_SCRIPTS/custom_app.py list crm.lead --my --this-month

# Search by name + assigned user
python3 $SKILL_SCRIPTS/custom_app.py list crm.lead --search "Acme" --user "Alice"

# Custom domain + explicit fields
python3 $SKILL_SCRIPTS/custom_app.py list sale.order \
  --domain '[["state","=","sale"]]' \
  --fields '["id","name","partner_id","amount_total","date_order"]' \
  --order "date_order desc" --limit 20

# Filter by date field (custom field name)
python3 $SKILL_SCRIPTS/custom_app.py list sale.order --date-field date_order --this-month

# Get a single record (all fields)
python3 $SKILL_SCRIPTS/custom_app.py get crm.lead 42

# Count matching records
python3 $SKILL_SCRIPTS/custom_app.py count crm.lead --domain '[["stage_id.name","=","Won"]]'

# --- Writing ---

# Create a record
python3 $SKILL_SCRIPTS/custom_app.py create crm.lead \
  --values '{"name":"New Opportunity","partner_id":5,"expected_revenue":10000}'

# Update a single record
python3 $SKILL_SCRIPTS/custom_app.py update crm.lead 42 \
  --values '{"stage_id":3,"priority":"1"}'

# Update multiple records at once
python3 $SKILL_SCRIPTS/custom_app.py update crm.lead --ids '[42,43,44]' \
  --values '{"user_id":7}'

# --- Notes & Activities ---

# Log an internal note on any record
python3 $SKILL_SCRIPTS/custom_app.py log-note crm.lead 42 --body "Called the client, follow up next week"

# Schedule an activity notification (user resolved by name)
python3 $SKILL_SCRIPTS/custom_app.py notify crm.lead 42 \
  --user "Alice" --summary "Please follow up with this lead"
```

## Generic Client (`odoo_core.py`)

For raw low-level access or testing the connection:

```bash
# Test connection
python3 $SKILL_SCRIPTS/odoo_core.py test-connection

# Search/read with raw domain
python3 $SKILL_SCRIPTS/odoo_core.py search-read res.partner --fields '["name","email","phone"]' --limit 20

# Get field definitions
python3 $SKILL_SCRIPTS/odoo_core.py fields res.partner
```

## Security Rules

1. **No delete** — `unlink` is blocked in all scripts.
2. **Sensitive models blocked** — `ir.rule`, `ir.model.access`, `ir.config_parameter`, etc.
3. **Read-only models** — `res.users`, `hr.employee`, stage/type models cannot be modified.
4. **Credentials from environment only** — Never pass credentials as arguments.
5. **Audit logging** — All operations are logged to stderr with timestamps.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Access Denied` | Check all 4 env vars: `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY` |
| `Model not found` | Module may not be installed in your Odoo instance |
| `No module named odoo_core` | Run the script from the scripts directory or use absolute path |
| Script not found | Resolve `SKILL_SCRIPTS` path as shown in Path Resolution above |

## Field Reference

See [Odoo Models Reference](./references/odoo-models.md) for detailed field lists per model.
