---
name: dashtask
version: "1.9.1"
description: Manage tasks, CRM leads, contacts, and settings via the DashTask REST API
homepage: https://dashtask.ai
metadata:
  clawdbot:
    emoji: "✅"
    requires:
      env:
        - DASHTASK_API_KEY
        - DASHTASK_ENDPOINT
    primaryEnv: "DASHTASK_API_KEY"
---

> **Note:** This file is for **API Key (OpenClaw / custom bot)** setups only.
> For the ChatGPT OAuth GPT Builder setup, see `/dashtask-gpt-oauth/`.

# DashTask Agent API — Skills File (API Key Setup)

## Overview

DashTask is a collaborative task management and CRM platform. Each organization has its own tasks, projects, CRM leads, contacts, companies, activities, quotes, and configurable dimensions. AI agents interact with DashTask via a single REST endpoint.

## Quick Start

### 1. Get Organization Context (call ONCE per conversation — never repeat in the same session)
```bash
curl -s -X POST "$DASHTASK_ENDPOINT" \
  -H "X-API-Key: $DASHTASK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "get_org_context"}'
```

### 2. List Tasks
```bash
curl -s -X POST "$DASHTASK_ENDPOINT" \
  -H "X-API-Key: $DASHTASK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "list_tasks", "filters": {"status": "open", "limit": 20}}'
```

### 3. Create a Task
```bash
curl -s -X POST "$DASHTASK_ENDPOINT" \
  -H "X-API-Key: $DASHTASK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "create_task", "title": "Follow up with client", "urgency": 7}'
```

### 4. Create a CRM Lead
```bash
curl -s -X POST "$DASHTASK_ENDPOINT" \
  -H "X-API-Key: $DASHTASK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "create_lead", "lead_name": "Acme Corp", "lead_status": "new_lead", "priority": 5}'
```

See the full [Actions Reference](#actions-reference) below for all 60+ available actions.

## Authentication

This integration uses an **API Key** passed in the `X-API-Key` header. Set it once in your environment:

```bash
export DASHTASK_API_KEY="your_key_here"
export DASHTASK_ENDPOINT="https://fgkytboizxksqustdfuc.supabase.co/functions/v1/agent-api"
```

All requests must include:
```
POST $DASHTASK_ENDPOINT
Content-Type: application/json
X-API-Key: $DASHTASK_API_KEY
```

Generate your key in DashTask → **Settings → Team → Invite AI Agent**. The key is scoped to specific permissions at the time of creation.

### Scopes

- `tasks` — Tasks, projects, assignees, tags, discussions, notifications, team members
- `crm` — Leads, contacts, companies, activities, quotes, lead discussions
- `settings` — Dimension management (categories, entities, departments, types, tags, CRM dimensions)

## Request Format

All requests are `POST` with a JSON body. All fields are **top-level** (no nesting under `params`):

```json
{
  "action": "<action_name>",
  "title": "My task title",
  "id": "<uuid>",
  "filters": { ... }
}
```

- `action` (required): The operation to perform
- All create/update fields go at the top level alongside `action`
- `id`: UUID of the record for update/delete operations
- `filters`: Optional filters for list operations

## Response Format

```json
{
  "success": true,
  "data": { ... }
}
```

On error:
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

---

## IMPORTANT: Discovery-First Pattern

**Dimensions are dynamic.** Organizations can add, rename, and remove dimension options at any time. Before creating or updating tasks/leads, you must discover what values are valid for this organization.

### Recommended: `get_org_context` (call ONCE per conversation session, never again)

Call `get_org_context` **only on your very first message in a conversation**. Store the result in your memory for the entire session.

> **RULE: If you have already called `get_org_context` at any point in this conversation, DO NOT call it again. Use the cached response you already have. This applies to every subsequent message in the same session.**

**Decision logic (follow strictly):**
1. Has `get_org_context` been called earlier in this conversation? → **Use cached data. Skip the call entirely.**
2. Is this the very first message in the conversation? → **Call `get_org_context` once, then cache.**
3. Did the API return an "Invalid dimension" error? → **Call `get_org_context` once to refresh, then stop.**

**NEVER call `get_org_context`:**
- Before every action or tool call
- When the user asks a follow-up question
- When checking task status or listing tasks
- In the same conversation where it was already called

**Only call `get_org_context` again if:**
- You receive an "Invalid dimension" or "Invalid entity" error from the API
- It has been more than 24 hours since the last call in a long-running session

The response includes:
- `projects` — all active projects with IDs
- `task_dimensions` — entity, category, department, type options
- `custom_task_dimensions` — custom dimension types and their items
- `crm_dimensions` — lead_source, industry, lead_quality, lead_action_status options
- `lead_stages` — pipeline stages
- `team_members` — IDs, names, emails
- `tags` — tag IDs and names
- `dimension_visibility` — which dimensions are visible/hidden
- `fetched_at` — ISO timestamp for cache expiry tracking

### Alternative: Individual Discovery Calls

You can still call individual discovery actions if you only need a specific subset:

If you provide an invalid dimension value, the API returns an error with the list of valid options so you can self-correct.

---

## Actions Reference

### Discovery Actions

#### `get_org_context`
**Scope:** any (tasks, crm, or settings) — returns data scoped to your permissions
Returns all organization context in a single call. **Recommended for first call — cache the result.**

#### `list_task_dimensions`
**Scope:** tasks
Lists the 4 fixed task dimensions (entity, category, department, type) with their current options.

#### `list_custom_task_dimensions`
**Scope:** tasks
Lists custom dimension types (max 4 per org) and their items.

#### `list_crm_dimensions`
**Scope:** crm
Lists CRM dimension types (lead_source, industry, lead_quality, lead_action_status) with options.

#### `list_lead_stages`
**Scope:** crm
Lists custom lead pipeline stages for the organization.

#### `list_dimension_visibility`
**Scope:** settings
Returns which dimensions are visible/hidden for the organization.

---

### Task Actions

#### `list_tasks`
**Scope:** tasks | **Filters:** `status`, `project_id`, `limit`

#### `create_task`
**Scope:** tasks
```json
{
  "action": "create_task",
  "title": "Follow up with client",
  "description": "Send proposal draft",
  "status": "open",
  "urgency": 7,
  "entity": "acme_corp",
  "category": "marketing",
  "department": "sales",
  "task_type": "task",
  "project_id": "uuid-or-null",
  "parent_task_id": "uuid-or-null",
  "due_date": "2026-03-01",
  "start_date": "2026-02-15",
  "estimated_cost": 500,
  "sales": 1000,
  "hours": 4,
  "budget_hours": 8
}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |
| status | string | No | `open`, `in-progress`, `approval`, or `done` (default: `open`) |
| urgency | integer | No | 1-10 scale, 10 = most urgent (default: 5) |
| entity | string | No | Must be valid entity name (discover via `list_task_dimensions`) |
| category | string | No | Must be valid category name |
| department | string | No | Must be valid department name |
| type | string | No | Must be valid type name |
| project_id | uuid | No | Associate with a project |
| parent_task_id | uuid | No | Parent task UUID — creates this as a subtask |
| due_date | string | No | ISO date |
| start_date | string | No | ISO date |
| estimated_cost | number | No | Estimated cost |
| sales | number | No | Sales value |
| hours | number | No | Hours spent |
| budget_hours | number | No | Budgeted hours |

#### `update_task`
**Scope:** tasks | **Requires:** `id`
Same fields as create_task (including `parent_task_id`). Only include fields you want to change.

#### `delete_task`
**Scope:** tasks | **Requires:** `id`

#### `list_subtasks`
**Scope:** tasks | **Requires:** `parent_task_id` or `id` (parent task UUID)
Returns all subtasks of a given parent task.
```json
{ "action": "list_subtasks", "parent_task_id": "uuid" }
```

#### `assign_task`
**Scope:** tasks
```json
{ "action": "assign_task", "task_id": "uuid", "team_member_id": "uuid" }
```

#### `unassign_task`
**Scope:** tasks
```json
{ "action": "unassign_task", "task_id": "uuid", "team_member_id": "uuid" }
```

#### `list_task_assignees`
**Scope:** tasks | **Requires:** `id` (task id)

#### `add_task_tag`
**Scope:** tasks
```json
{ "action": "add_task_tag", "task_id": "uuid", "tag_id": "uuid" }
```

#### `remove_task_tag`
**Scope:** tasks

#### `add_task_discussion`
**Scope:** tasks
```json
{ "action": "add_task_discussion", "task_id": "uuid", "message": "Progress update: completed phase 1" }
```

---

### Project Actions

#### `list_projects`
**Scope:** tasks

#### `create_project`
**Scope:** tasks
```json
{ "action": "create_project", "name": "Q1 Campaign", "description": "Marketing campaign" }
```

#### `update_project`
**Scope:** tasks | **Requires:** `id`

#### `archive_project`
**Scope:** tasks | **Requires:** `id`

---

### CRM Lead Actions

#### `list_leads`
**Scope:** crm | **Filters:** `lead_status`, `deal_status`, `lead_stage`, `limit`

#### `create_lead`
**Scope:** crm
```json
{
  "action": "create_lead",
  "lead_name": "Acme Corp Deal",
  "lead_status": "new_lead",
  "lead_stage": "new_existing",
  "deal_status": "active",
  "priority": 5,
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "lead_source": "website",
  "probability": 50,
  "annual_deal_value": 50000
}
```

**Fixed enum fields:**
| Field | Values |
|-------|--------|
| lead_status | `existing_customer`, `new_lead`, `attempted_contact`, `contacted`, `unqualified`, `qualified` |
| lead_stage | `new_existing`, `demo_discovery`, `proposal_quote`, `negotiation_asks`, `closed_lost`, `closed_won` |
| deal_status | `active`, `won`, `lost`, `stale` |

**Dynamic fields (discover via `list_crm_dimensions`):**
- `lead_source` — e.g., "website", "referral" (org-specific)
- `lead_action_status` — org-specific action statuses

| Field | Type | Description |
|-------|------|-------------|
| lead_name | string | Required. Lead/deal name |
| priority | integer | 1-5 scale |
| probability | integer | 0-100 win probability |
| monthly_deal_value | number | Monthly recurring value |
| annual_deal_value | number | Annual deal value |
| one_time_deal_value | number | One-time payment value |
| lifetime_deal_value | number | Total lifetime value |
| next_steps | string | Next action description |
| next_step_date | string | ISO date for next action |
| company_id | uuid | Link to company |
| primary_contact_id | uuid | Link to primary contact |
| assignee_id | uuid | Team member UUID |
| timezone | string | IANA timezone |

#### `update_lead`
**Scope:** crm | **Requires:** `id`

#### `delete_lead`
**Scope:** crm | **Requires:** `id`

#### `assign_lead` / `unassign_lead`
**Scope:** crm
```json
{ "action": "assign_lead", "lead_id": "uuid", "team_member_id": "uuid" }
```

#### `add_lead_party` / `remove_lead_party`
**Scope:** crm

#### `add_lead_discussion`
**Scope:** crm
```json
{ "action": "add_lead_discussion", "lead_id": "uuid", "message": "Client requested revised timeline" }
```

---

### CRM Company Actions

#### `list_companies` / `create_company` / `update_company` / `delete_company`
**Scope:** crm

```json
{
  "action": "create_company",
  "company_name": "Acme Corp",
  "website": "https://acme.com",
  "industry": "Technology",
  "employee_count": 500,
  "headquarters": "New York, NY"
}
```

---

### CRM Contact Actions

#### `list_contacts` / `create_contact` / `update_contact` / `delete_contact`
**Scope:** crm

```json
{
  "action": "create_contact",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@acme.com",
  "phone": "+1234567890",
  "title": "VP Sales",
  "priority": "high",
  "company_id": "uuid"
}
```

| Field | Values |
|-------|--------|
| priority | `low`, `medium`, `high` |

---

### CRM Activity Actions

#### `list_activities`
**Scope:** crm | **Filters:** `lead_id`, `contact_id`, `company_id`, `type`, `limit`

#### `create_activity`
**Scope:** crm
```json
{
  "action": "create_activity",
  "activity_type": "call",
  "direction": "outbound",
  "subject": "Discovery call",
  "content": "Discussed requirements and timeline",
  "lead_id": "uuid",
  "contact_id": "uuid"
}
```

| Field | Values |
|-------|--------|
| type | `email`, `call`, `text`, `demo`, `meeting`, `note` |
| direction | `inbound`, `outbound` |

---

### CRM Quote Actions

#### `list_quotes` / `create_quote` / `update_quote`
**Scope:** crm

```json
{
  "action": "create_quote",
  "lead_id": "uuid",
  "plan": "Enterprise",
  "seats": 50,
  "billing_cycle": "annual",
  "price": 25000,
  "status": "draft"
}
```

| Field | Values |
|-------|--------|
| status | `draft`, `sent`, `accepted`, `rejected` |
| billing_cycle | `monthly`, `annual`, `one-time` |

---

### Communication Actions

#### `send_nudge`
**Scope:** tasks
Sends a nudge email to a team member about a specific task.
```json
{
  "action": "send_nudge",
  "task_id": "uuid",
  "recipient_email": "john@example.com",
  "recipient_name": "John Doe",
  "sender_name": "Sales Bot",
  "tone": "professional"
}
```

#### `send_crm_email`
**Scope:** crm
Sends an email related to a CRM lead.
```json
{
  "action": "send_crm_email",
  "lead_id": "uuid",
  "recipient_email": "client@acme.com",
  "subject": "Follow-up on our discussion",
  "body": "Hi, just following up..."
}
```

---

### Settings & Dimension Management Actions

#### `list_tags` / `create_tag`
**Scope:** settings

#### `create_task_dimension_option`
**Scope:** settings
Add a new option to entity, category, department, or type.
```json
{
  "action": "create_task_dimension_option",
  "dimension": "entity",
  "name": "new_client",
  "label": "New Client"
}
```

#### `delete_task_dimension_option`
**Scope:** settings | **Requires:** `id`, `dimension`

#### `create_custom_task_dimension`
**Scope:** settings (max 4 per org)
```json
{
  "action": "create_custom_task_dimension",
  "name": "region",
  "label": "Region"
}
```

#### `delete_custom_task_dimension`
**Scope:** settings | **Requires:** `id`

#### `create_custom_task_dimension_item` / `delete_custom_task_dimension_item`
**Scope:** settings

#### `create_crm_dimension_option`
**Scope:** settings
```json
{
  "action": "create_crm_dimension_option",
  "dimension_type": "lead_source",
  "name": "linkedin",
  "label": "LinkedIn"
}
```

#### `update_crm_dimension_option` / `delete_crm_dimension_option`
**Scope:** settings (locked options cannot be deleted)

---

### Team & Notification Actions

#### `list_team_members`
**Scope:** tasks (read-only)

#### `create_notification`
**Scope:** tasks
```json
{
  "action": "create_notification",
  "user_id": "uuid",
  "title": "New task assigned",
  "message": "You've been assigned to 'Follow up with client'",
  "type": "info"
}
```

---

## Restricted Actions (Bot Cannot)

- Transfer admin privileges
- Change member roles
- Manage billing or subscriptions
- Access platform admin operations
- Delete the organization
- Access data outside the authorized organization

---

## Error Handling

**Invalid dimension value:**
```json
{
  "success": false,
  "error": "Invalid entity 'xyz'. Valid values: [\"acme_corp\", \"beta_inc\"]"
}
```

**Missing scope:**
```json
{
  "success": false,
  "error": "Missing scope: crm"
}
```

**Missing required field:**
```json
{
  "success": false,
  "error": "title is required"
}
```

## Rate Limiting

Be respectful of API usage. Recommended: max 60 requests per minute per key.

## Workflow Examples

### Full Lead Lifecycle
1. `get_org_context` — **first message only** — discover all dimensions, stages, and team members (cache for entire session)
2. `create_company` — create the company
3. `create_contact` — create the primary contact
4. `create_lead` — create the lead linked to company and contact
5. `create_activity` — log a discovery call
6. `update_lead` — update stage to `demo_discovery`
7. `create_quote` — generate a quote
8. `update_lead` — update stage to `proposal_quote`, set probability
9. `add_lead_discussion` — add internal notes
10. `send_crm_email` — send follow-up email

### Task Management Pipeline
1. `get_org_context` — **first message only** — discover all dimensions, projects, and team members (cache for entire session)
2. `create_project` — create a project
4. `create_task` — create tasks within the project
5. `assign_task` — assign team members
6. `send_nudge` — nudge assignees about overdue tasks
7. `update_task` — mark as done
