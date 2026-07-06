# DashTask Skill for OpenClaw

![Version](https://img.shields.io/badge/version-1.9.1-blue)
![Actions](https://img.shields.io/badge/actions-60%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> An [OpenClaw](https://openclaw.ai) skill that lets AI agents manage tasks, CRM leads, contacts, companies, activities, quotes, and settings in [DashTask](https://dashtask.ai) via a single REST API endpoint.

---

## What Is This?

This repository contains the **DashTask skill** for the OpenClaw agent framework. Once installed, any OpenClaw-compatible AI agent (ClawdBot, custom bots, or any LLM with tool-use) can:

- Create, update, and assign **tasks** and **projects**
- Manage a full **CRM pipeline** — leads, contacts, companies, activities, and quotes
- Configure **organization settings** — dimensions, tags, and custom fields
- Send **nudge emails** and **CRM emails** on behalf of your team
- Read **team members**, **notifications**, and **org context**

All operations go through a single consolidated REST endpoint using a simple `{ "action": "..." }` JSON payload pattern.

---

## Files in This Repo

| File | Purpose |
|------|---------|
| [`SKILL.md`](./SKILL.md) | Full API reference — 60+ actions with curl examples, field tables, enums, and workflow guides. This is the file agents read to learn the DashTask API. |
| [`clawfile.json`](./clawfile.json) | OpenClaw manifest — declares the skill name, version, required environment variables, and file list. OpenClaw reads this to register the skill. |
| `README.md` | This file — setup guide and architecture overview. |

---

## Quick Start

### Option A — Install via CLI (if published to ClawHub)

```bash
openclaw skills install dashtask
```

### Option B — Manual Installation

1. Clone this repo (or download the files) into your OpenClaw skills directory:

```bash
git clone https://github.com/YOUR_ORG/dashtask-skill.git ~/.openclaw/skills/dashtask
```

2. Enable the skill:

```bash
openclaw skills enable dashtask
```

### Set Environment Variables

Add the following to your `~/.openclaw/openclaw.json` under `"env"`, or export them as shell variables:

```json
{
  "env": {
    "DASHTASK_API_KEY": "dtsk_your_full_key_here",
    "DASHTASK_ENDPOINT": "https://your-dashtask-endpoint/functions/v1/agent-api"
  }
}
```

| Variable | Description |
|----------|-------------|
| `DASHTASK_API_KEY` | Your API key (starts with `dtsk_`). Generated in DashTask. |
| `DASHTASK_ENDPOINT` | The REST endpoint URL for your DashTask organization. |

### Verify Installation

```bash
openclaw skills list
```

You should see `dashtask` listed as **enabled**.

---

## Getting Your API Key

1. Log in to [DashTask](https://dashtask.ai)
2. Go to **Settings → Team**
3. Click **Invite AI Agent**
4. Choose **OpenClaw** as the agent type
5. Select the scopes you need (`tasks`, `crm`, `settings`)
6. Copy the generated API key (it will only be shown once)

---

## Available Scopes

| Scope | What It Covers |
|-------|----------------|
| `tasks` | Tasks, projects, subtasks, assignees, tags, discussions, notifications, team members |
| `crm` | Leads, contacts, companies, activities, quotes, lead discussions, lead parties |
| `settings` | Dimension management — categories, entities, departments, types, tags, CRM dimensions, custom dimensions |

Scopes are set when you generate your API key. An agent can only call actions within its granted scopes.

---

## What the Skill Can Do

### Discovery
| Action | Description |
|--------|-------------|
| `get_org_context` | Returns all org context in one call — projects, dimensions, stages, team members, tags. **Call once per session, then cache.** |
| `list_task_dimensions` | Lists the 4 fixed task dimensions (entity, category, department, type) |
| `list_custom_task_dimensions` | Lists custom dimension types (max 4 per org) |
| `list_crm_dimensions` | Lists CRM dimension types and their options |
| `list_lead_stages` | Lists custom pipeline stages |
| `list_dimension_visibility` | Shows which dimensions are visible/hidden |

### Tasks
| Action | Description |
|--------|-------------|
| `list_tasks` | List tasks with optional filters (status, project, limit) |
| `create_task` | Create a task with title, urgency, dimensions, dates, costs |
| `update_task` | Update any task field |
| `delete_task` | Delete a task |
| `list_subtasks` | List subtasks of a parent task |
| `assign_task` / `unassign_task` | Manage task assignees |
| `list_task_assignees` | List current assignees |
| `add_task_tag` / `remove_task_tag` | Manage task tags |
| `add_task_discussion` | Post a comment on a task |

### Projects
| Action | Description |
|--------|-------------|
| `list_projects` | List all projects |
| `create_project` | Create a new project |
| `update_project` | Update project details |
| `archive_project` | Archive a project |

### CRM — Leads
| Action | Description |
|--------|-------------|
| `list_leads` | List leads with filters (status, stage, deal_status) |
| `create_lead` | Create a lead with name, status, stage, values, contacts |
| `update_lead` / `delete_lead` | Modify or remove leads |
| `assign_lead` / `unassign_lead` | Manage lead assignees |
| `add_lead_party` / `remove_lead_party` | Link contacts/companies to leads |
| `add_lead_discussion` | Post internal notes on a lead |

### CRM — Companies & Contacts
| Action | Description |
|--------|-------------|
| `list_companies` / `create_company` / `update_company` / `delete_company` | Full CRUD for companies |
| `list_contacts` / `create_contact` / `update_contact` / `delete_contact` | Full CRUD for contacts |

### CRM — Activities & Quotes
| Action | Description |
|--------|-------------|
| `list_activities` / `create_activity` | Log calls, emails, meetings, demos, notes |
| `list_quotes` / `create_quote` / `update_quote` | Generate and manage quotes |

### Communication
| Action | Description |
|--------|-------------|
| `send_nudge` | Send a nudge email to a team member about a task |
| `send_crm_email` | Send an email related to a CRM lead |

### Settings & Dimensions
| Action | Description |
|--------|-------------|
| `list_tags` / `create_tag` | Manage tags |
| `create_task_dimension_option` / `delete_task_dimension_option` | Add/remove dimension options |
| `create_custom_task_dimension` / `delete_custom_task_dimension` | Manage custom dimension types |
| `create_custom_task_dimension_item` / `delete_custom_task_dimension_item` | Manage custom dimension items |
| `create_crm_dimension_option` / `update_crm_dimension_option` / `delete_crm_dimension_option` | Manage CRM dimensions |

### Team & Notifications
| Action | Description |
|--------|-------------|
| `list_team_members` | List all team members (read-only) |
| `create_notification` | Send an in-app notification to a user |

---

## How It Was Built

DashTask exposes a **single consolidated REST endpoint** (a serverless edge function) that accepts `POST` requests with an `{ "action": "..." }` JSON payload. This design means agents only need to know one URL — no route memorization or path construction required.

The **`SKILL.md`** file is the core of the skill. It teaches AI agents the full API surface using:
- **Curl examples** for every action so agents can construct requests immediately
- **Field tables** with types, required flags, and valid enum values
- **Workflow examples** (e.g., full lead lifecycle, task management pipeline) that demonstrate multi-step sequences
- A **discovery-first pattern** — agents call `get_org_context` once at the start of a conversation to learn the organization's custom dimensions, projects, stages, and team members, then cache that context for the entire session

The **`clawfile.json`** manifest declares the two required environment variables (`DASHTASK_API_KEY` and `DASHTASK_ENDPOINT`). When OpenClaw loads the skill, it reads this file and auto-prompts users to configure these variables — ensuring agents have credentials before attempting any API calls.

**Authentication** uses API keys passed via the `X-API-Key` header. Keys are scoped to specific permissions (`tasks`, `crm`, `settings`) at creation time, so organizations can grant agents exactly the access they need.

---

## Rate Limiting

Recommended maximum: **60 requests per minute** per API key. The API will return errors if this limit is exceeded.

---

## Restricted Actions

Agents **cannot**:
- Transfer admin privileges
- Change member roles
- Manage billing or subscriptions
- Access platform admin operations
- Delete the organization
- Access data outside the authorized organization

---

## Workflow Examples

### Full Lead Lifecycle

```
get_org_context        → discover dimensions, stages, team members (once per session)
create_company         → create the company record
create_contact         → create the primary contact
create_lead            → create the lead, link to company and contact
create_activity        → log a discovery call
update_lead            → advance stage to demo_discovery
create_quote           → generate a quote
update_lead            → advance stage to proposal_quote, set probability
add_lead_discussion    → add internal notes
send_crm_email         → send follow-up email
```

### Task Management Pipeline

```
get_org_context        → discover dimensions, projects, team members (once per session)
create_project         → create a project
create_task            → create tasks within the project
assign_task            → assign team members
send_nudge             → nudge assignees about overdue tasks
update_task            → mark tasks as done
```

---

## Links

- **DashTask** — [https://dashtask.ai](https://dashtask.ai)
- **SKILL.md** (API Reference) — [View SKILL.md](./SKILL.md)
- **clawfile.json** (Manifest) — [View clawfile.json](./clawfile.json)
- **ChatGPT OAuth Setup** — DashTask also supports a separate OAuth-based integration for ChatGPT GPT Builder. See the `/dashtask-gpt-oauth/` directory in the main DashTask project for that setup.

---

## License

MIT — see [LICENSE](./LICENSE) for details.
