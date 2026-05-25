# VNClaw — Odoo Integration Skill

A GitHub Copilot skill that lets you interact with **Odoo 17** via the XML-RPC API directly from your AI assistant. Supports reading, creating, and updating records across the most common Odoo modules.

> **No delete operations are supported** — by design, to prevent accidental data loss.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Scripts](#scripts)
- [Common Flags](#common-flags)
- [Usage Examples](#usage-examples)
- [Security](#security)

---

## Overview

This skill translates natural language requests into Python XML-RPC commands against your Odoo 17 instance. It covers:

| Module | Script | Odoo Model |
|---|---|---|
| Tasks | `tasks.py` | `project.task` |
| Projects | `projects.py` | `project.project` |
| Timesheets | `timesheets.py` | `account.analytic.line` |
| Calendar Events | `calendar_events.py` | `calendar.event` |
| Helpdesk Tickets | `helpdesk.py` | `helpdesk.ticket` |
| Time Off | `time_off.py` | `hr.leave` |
| Knowledge Articles | `knowledge.py` | `knowledge.article` |
| Documents | `documents.py` | `documents.document` |
| Any Custom Model | `custom_app.py` | *(any)* |
| Connection Test | `odoo_core.py` | — |

---

## Installation

The skill can be installed in two locations:

| Type | Path |
|---|---|
| Workspace skill | `<git-root>/.github/skills/vnclaw-odoo-skill/` |
| User global (vnclaw) | `~/.vnclaw/skills/vnclaw-odoo-skill/` |
| User global (openclaw) | `~/.openclaw/skills/vnclaw-odoo-skill/` |

The skill auto-detects its location at runtime — no path configuration needed.

---

## Configuration

Credentials are loaded from **environment variables**. Never hardcode them.

| Variable | Description | Example |
|---|---|---|
| `ODOO_URL` | Base URL of your Odoo instance (no trailing slash) | `https://mycompany.odoo.com` |
| `ODOO_DB` | Database name (case-sensitive) | `mycompany-production` |
| `ODOO_USERNAME` | Login username (email) | `admin@mycompany.com` |
| `ODOO_API_KEY` | API key or password | `abc123...` |

Copy [`assets/example.env`](assets/example.env) to `.env` and fill in your values:

```bash
cp assets/example.env .env
# Edit .env with your credentials
```

> Generate an API key in Odoo: **Settings → Users → Select user → Account Security → API Keys**

**Never commit `.env` to version control.**

### Test your connection

```bash
python3 scripts/odoo_core.py test-connection
```

---

## Scripts

### `tasks.py` — Tasks

```bash
# List my tasks
python3 scripts/tasks.py list --my

# Tasks I created this week
python3 scripts/tasks.py list --my --this-week --date-field created

# Tasks with a deadline this week
python3 scripts/tasks.py list --my --this-week

# Overdue tasks
python3 scripts/tasks.py list --overdue

# Create a task
python3 scripts/tasks.py create --name "Fix login bug" --project "Website" --assign "Alice" --deadline 2026-04-01

# Update task stage and assignee
python3 scripts/tasks.py update 42 --stage "Done" --assign "Bob"

# Log an internal note
python3 scripts/tasks.py log-note 42 --body "Waiting for client feedback"
```

---

### `projects.py` — Projects

```bash
# Projects I manage
python3 scripts/projects.py list --my

# Create a project
python3 scripts/projects.py create --name "Website Redesign" --manager "Alice"

# Update project stage and dates
python3 scripts/projects.py update 1 --stage "In Progress" --date-start 2026-04-01 --date-end 2026-06-30
```

---

### `timesheets.py` — Timesheets

```bash
# My timesheets this week
python3 scripts/timesheets.py list --my --this-week

# Summary grouped by project/task
python3 scripts/timesheets.py summary --my --this-month

# Log 2.5 hours
python3 scripts/timesheets.py log --project "Website Redesign" --hours 2.5 --description "Code review"
```

---

### `calendar_events.py` — Calendar Events

```bash
# My events today
python3 scripts/calendar_events.py list --my --today

# Create a meeting with attendees
python3 scripts/calendar_events.py create \
  --name "Sprint Planning" \
  --start "2026-03-20 09:00:00" \
  --stop "2026-03-20 10:00:00" \
  --attendees "Alice, Bob, Carol" \
  --location "Room A"
```

---

### `helpdesk.py` — Helpdesk Tickets

```bash
# My assigned tickets
python3 scripts/helpdesk.py list --my

# Create a ticket
python3 scripts/helpdesk.py create --name "Login page broken" --team "Support" --assign "Alice" --customer "Acme Corp"

# Update ticket stage
python3 scripts/helpdesk.py update 5 --stage "Solved"
```

---

### `time_off.py` — Time Off

```bash
# My leave requests this year
python3 scripts/time_off.py list --my --this-year

# List available leave types
python3 scripts/time_off.py leave-types

# Create a leave request
python3 scripts/time_off.py create \
  --date-from "2026-03-25 08:00:00" \
  --date-to "2026-03-26 17:00:00" \
  --leave-type "Paid Time Off"
```

---

### `knowledge.py` — Knowledge Articles

```bash
# My published articles
python3 scripts/knowledge.py list --my --published

# Create an article
python3 scripts/knowledge.py create --name "Setup Guide" --parent-name "Engineering" --body "<h1>Getting Started</h1>"
```

---

### `documents.py` — Documents

```bash
# Documents in a folder
python3 scripts/documents.py list --folder "HR Documents"

# List available folders
python3 scripts/documents.py folders

# Create a URL document
python3 scripts/documents.py create --name "Design Spec" --folder "Engineering" --url "https://example.com/spec"
```

---

### `custom_app.py` — Any Odoo Model

Use this for CRM, Sales, Purchase, Inventory, or any custom app not covered by the dedicated scripts.

```bash
# Discover model technical names
python3 scripts/custom_app.py models --search "CRM"

# Inspect available fields
python3 scripts/custom_app.py fields crm.lead

# List records
python3 scripts/custom_app.py list crm.lead --my --this-month
```

---

## Common Flags

These flags work across all module scripts:

| Flag | Description |
|---|---|
| `--my` | Filter to the authenticated user's records |
| `--user "Name"` | Filter by user name |
| `--today` | Records for today |
| `--yesterday` | Records for yesterday |
| `--this-week` | Records for this week |
| `--last-week` | Records for last week |
| `--this-month` | Records for this month |
| `--last-month` | Records for last month |
| `--this-year` | Records for this year |
| `--date-from YYYY-MM-DD` | Custom date range start |
| `--date-to YYYY-MM-DD` | Custom date range end |

### `tasks.py` — `--date-field` flag

By default, date filters on tasks apply to `date_deadline`. Use `--date-field` to change this:

| Value | Filters on |
|---|---|
| `deadline` *(default)* | `date_deadline` |
| `created` | `create_date` |
| `updated` | `write_date` |

---

## Security

- **No delete operations** — only `search_read`, `read`, `create`, and `write` are permitted.
- **Blocked models** — security-sensitive models (`ir.rule`, `ir.model.access`, `res.groups`, etc.) cannot be accessed.
- **Read-only models** — `res.users`, `hr.employee`, and similar models cannot be written to.
- **Credentials via environment variables only** — never hardcoded.
- **All output goes to stdout as JSON** — logs go to stderr for clean piping.
