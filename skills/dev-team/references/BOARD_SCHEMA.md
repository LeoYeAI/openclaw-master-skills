# `board.json` — portfolio index (schema v1)

**Path:** `TEAM_ROOT/team/board.json`

**Purpose:** One structured, machine-friendly overview of **which customer has which active task** and **what phase** it is in. Narrative detail stays in **`SPEC.md`**, **`HANDOFF.md`**, and **`QA_NOTES.md`** under each task folder — not duplicated here or in a bloated `PROJECT_STATUS.md`.

See [SKILL.md — Portfolio index](../SKILL.md#portfolio-index-project_status-and-boardjson) for rules alongside `PROJECT_STATUS.md`.

---

## Root object

| Field | Type | Required | Notes |
|-------|------|----------|--------|
| `schema` | string | yes | Must be `"dev_team_board"`. |
| `version` | number | yes | Must be `1` for this spec. |
| `updated` | string | no | ISO-8601 timestamp, e.g. `2026-03-25T12:00:00Z`. |
| `customers` | array | yes | May be empty `[]`. |

## `customers[]` entries

Each element:

| Field | Type | Required | Notes |
|-------|------|----------|--------|
| `customer_id` | string | yes | Slug, same as `team/customers/<customer_id>/`. |
| `active_task` | object or `null` | yes | `null` = no in-flight task for that customer. |

### `active_task` object (when not `null`)

| Field | Type | Required | Notes |
|-------|------|----------|--------|
| `task_id` | string | yes | Same as folder name under `tasks/`. |
| `path` | string | yes | **Relative to `team/`**, POSIX slashes only. Example: `customers/acme-shop/tasks/top-bar-v1`. |
| `phase` | string | yes | One of: `spec`, `build`, `qa`, `done`. |

**PR URLs, branches, long prose:** keep in **`HANDOFF.md`** — do not mirror as required fields here.

**When a task is done:** set `active_task` to `null` for that customer (or remove the customer row if you prefer a minimal file). Record closure in **`DECISIONS.md`** and/or final **`HANDOFF.md`**.

---

## When to update

- **New task opened:** add or update the customer row; set `path`, `task_id`, `phase` (usually `spec`).
- **Phase change** (e.g. spec → build → qa): update `phase` and set `updated`.
- **Handoff to another role:** the sending role **should** ensure `phase` and paths still match reality; **Lead** reconciles if unsure.
- **Task completed:** `active_task: null`, bump `updated`.

---

## Example (copy-paste)

```json
{
  "schema": "dev_team_board",
  "version": 1,
  "updated": "2026-03-25T14:30:00Z",
  "customers": [
    {
      "customer_id": "acme-shop",
      "active_task": {
        "task_id": "top-bar-v1",
        "path": "customers/acme-shop/tasks/top-bar-v1",
        "phase": "build"
      }
    },
    {
      "customer_id": "other-corp",
      "active_task": null
    }
  ]
}
```

## Empty bootstrap

```json
{
  "schema": "dev_team_board",
  "version": 1,
  "customers": []
}
```

No JSON Schema file ships with the skill; this markdown is the contract.
