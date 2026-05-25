# Odoo 17 Models Reference

Detailed field reference for the Odoo 17 models supported by OpenClaw.

---

## project.project — Projects

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Project name |
| `user_id` | Many2one → res.users | Project manager |
| `partner_id` | Many2one → res.partner | Customer |
| `date_start` | Date | Start date |
| `date` | Date | End date |
| `description` | Html | Project description |
| `tag_ids` | Many2many → project.tags | Tags |
| `task_count` | Integer | Number of tasks (computed) |
| `active` | Boolean | Active (archived if false) |
| `company_id` | Many2one → res.company | Company |
| `analytic_account_id` | Many2one → account.analytic.account | Analytic account |
| `allow_timesheets` | Boolean | Allow timesheets |
| `label_tasks` | Char | Task label (e.g., "Tasks", "Issues") |

---

## project.task — Tasks

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Task title |
| `project_id` | Many2one → project.project | Project |
| `user_ids` | Many2many → res.users | Assignees |
| `stage_id` | Many2one → project.task.type | Stage |
| `date_deadline` | Date | Deadline |
| `date_assign` | Datetime | Assignment date |
| `priority` | Selection | Priority: `0` (Normal), `1` (Important) |
| `tag_ids` | Many2many → project.tags | Tags |
| `description` | Html | Description |
| `parent_id` | Many2one → project.task | Parent task |
| `child_ids` | One2many → project.task | Sub-tasks |
| `timesheet_ids` | One2many → account.analytic.line | Timesheets |
| `effective_hours` | Float | Hours spent (computed) |
| `planned_hours` | Float | Initially planned hours |
| `remaining_hours` | Float | Remaining hours (computed) |
| `kanban_state` | Selection | `normal`, `done`, `blocked` |
| `active` | Boolean | Active |
| `partner_id` | Many2one → res.partner | Customer |
| `company_id` | Many2one → res.company | Company |

---

## calendar.event — Calendar Events

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Event summary |
| `start` | Datetime | Start date/time |
| `stop` | Datetime | End date/time |
| `allday` | Boolean | All-day event |
| `start_date` | Date | Start date (all-day events) |
| `stop_date` | Date | End date (all-day events) |
| `duration` | Float | Duration in hours |
| `description` | Html | Description |
| `location` | Char | Location |
| `partner_ids` | Many2many → res.partner | Attendees |
| `user_id` | Many2one → res.users | Organizer |
| `recurrency` | Boolean | Recurring event |
| `privacy` | Selection | `public`, `private`, `confidential` |
| `show_as` | Selection | `busy`, `free` |
| `alarm_ids` | Many2many → calendar.alarm | Reminders |
| `categ_ids` | Many2many → calendar.event.type | Tags |
| `videocall_location` | Char | Video call URL |

---

## hr.leave — Time Off (Leave Requests)

| Field | Type | Description |
|-------|------|-------------|
| `employee_id` | Many2one → hr.employee | Employee |
| `holiday_status_id` | Many2one → hr.leave.type | Leave type |
| `date_from` | Datetime | Start date/time |
| `date_to` | Datetime | End date/time |
| `number_of_days` | Float | Duration in days (computed) |
| `name` | Char | Description / reason |
| `state` | Selection | `draft`, `confirm`, `validate1`, `validate`, `refuse` |
| `user_id` | Many2one → res.users | User |
| `department_id` | Many2one → hr.department | Department |
| `request_date_from` | Date | Requested start date |
| `request_date_to` | Date | Requested end date |
| `request_hour_from` | Selection | Start hour (half-day) |
| `request_hour_to` | Selection | End hour (half-day) |
| `request_unit_half` | Boolean | Half-day request |

---

## helpdesk.ticket — Helpdesk Tickets

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Ticket subject |
| `team_id` | Many2one → helpdesk.team | Helpdesk team |
| `user_id` | Many2one → res.users | Assigned to |
| `partner_id` | Many2one → res.partner | Customer |
| `partner_email` | Char | Customer email |
| `description` | Html | Description |
| `stage_id` | Many2one → helpdesk.stage | Stage |
| `priority` | Selection | `0` (Low), `1` (Medium), `2` (High), `3` (Urgent) |
| `tag_ids` | Many2many → helpdesk.tag | Tags |
| `create_date` | Datetime | Created on |
| `close_date` | Datetime | Closed on |
| `assign_date` | Datetime | Assigned on |
| `sla_deadline` | Datetime | SLA deadline |
| `kanban_state` | Selection | `normal`, `done`, `blocked` |
| `ticket_type_id` | Many2one → helpdesk.ticket.type | Ticket type |

---

## knowledge.article — Knowledge Articles

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Article title |
| `body` | Html | Article content |
| `parent_id` | Many2one → knowledge.article | Parent article |
| `child_ids` | One2many → knowledge.article | Child articles |
| `category` | Selection | `workspace`, `private`, `shared` |
| `create_uid` | Many2one → res.users | Author |
| `write_date` | Datetime | Last modified |
| `is_published` | Boolean | Published |
| `icon` | Char | Emoji icon |
| `sequence` | Integer | Sort order |
| `internal_permission` | Selection | `write`, `read`, `none` |
| `article_member_ids` | One2many → knowledge.article.member | Members |
| `favorite_count` | Integer | Favorite count |
| `is_article_item` | Boolean | Is article item |

---

## documents.document — Documents

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Document name |
| `folder_id` | Many2one → documents.folder | Workspace/folder |
| `owner_id` | Many2one → res.users | Owner |
| `partner_id` | Many2one → res.partner | Contact |
| `type` | Selection | `binary` (file), `url`, `empty` |
| `url` | Char | URL (if type=url) |
| `datas` | Binary | File content (base64) |
| `mimetype` | Char | MIME type |
| `file_size` | Integer | File size in bytes |
| `tag_ids` | Many2many → documents.tag | Tags |
| `description` | Text | Description |
| `create_date` | Datetime | Upload date |
| `lock_uid` | Many2one → res.users | Locked by |
| `is_locked` | Boolean | Is locked |

---

## account.analytic.line — Timesheets

| Field | Type | Description |
|-------|------|-------------|
| `employee_id` | Many2one → hr.employee | Employee |
| `project_id` | Many2one → project.project | Project |
| `task_id` | Many2one → project.task | Task |
| `name` | Char | Description of work |
| `date` | Date | Date |
| `unit_amount` | Float | Duration in hours |
| `user_id` | Many2one → res.users | User |
| `company_id` | Many2one → res.company | Company |
| `amount` | Monetary | Cost (computed) |
| `product_uom_id` | Many2one → uom.uom | Unit of measure |

---

## res.partner — Contacts

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Name |
| `email` | Char | Email |
| `phone` | Char | Phone |
| `mobile` | Char | Mobile |
| `street` | Char | Street |
| `city` | Char | City |
| `country_id` | Many2one → res.country | Country |
| `company_type` | Selection | `person`, `company` |
| `is_company` | Boolean | Is a company |
| `parent_id` | Many2one → res.partner | Parent company |
| `child_ids` | One2many → res.partner | Contacts |
| `category_id` | Many2many → res.partner.category | Tags |

---

## Domain Filter Syntax

Odoo uses a Polish-notation domain filter:

```json
[["field", "operator", "value"]]
```

**Operators:** `=`, `!=`, `>`, `>=`, `<`, `<=`, `like`, `ilike`, `in`, `not in`, `child_of`, `parent_of`

**Logic:** `&` (AND, default), `|` (OR), `!` (NOT)

**Examples:**
```json
// Tasks assigned to user 2 in project 1
[["project_id", "=", 1], ["user_ids", "in", [2]]]

// Open helpdesk tickets with high priority
["&", ["stage_id.is_close", "=", false], ["priority", ">=", "2"]]

// Calendar events this month
[["start", ">=", "2026-03-01"], ["start", "<", "2026-04-01"]]

// Time off requests pending approval
[["state", "in", ["confirm", "validate1"]]]
```

---

## Many2many Write Syntax

When writing Many2many fields, use command tuples:

| Command | Syntax | Description |
|---------|--------|-------------|
| Add | `[[4, id, 0]]` | Link existing record |
| Remove | `[[3, id, 0]]` | Unlink (don't delete) |
| Replace | `[[6, 0, [id1, id2]]]` | Replace all links |

Example — set attendees on a calendar event:
```json
{"partner_ids": [[6, 0, [1, 2, 3]]]}
```
