# Dashboard Management API

The Dashboard API enables AI agents to programmatically manage widget instances on the Glance dashboard. Use this API to add, remove, reposition, and resize widgets—especially useful for optimizing layouts across different screen sizes (mobile, tablet, desktop).

## Table of Contents

- [When to Use This API](#when-to-use-this-api)
- [Quick Reference](#quick-reference)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [GET /api/dashboard](#get-apidashboard)
  - [POST /api/dashboard](#post-apidashboard)
  - [PATCH /api/dashboard/:instanceId](#patch-apidashboardinstanceid)
  - [DELETE /api/dashboard/:instanceId](#delete-apidashboardinstanceid)
  - [PUT /api/dashboard/layout](#put-apidashboardlayout)
- [Grid System](#grid-system)
- [Auto-Placement](#auto-placement)
- [Responsive Layout Examples](#responsive-layout-examples)
- [Common Workflows](#common-workflows)

---

## When to Use This API

Use the Dashboard API when:

- User wants to **reorganize their dashboard layout**
- User asks to **optimize for mobile/tablet/desktop**
- User wants to **add a widget to the dashboard** by its slug
- User wants to **resize or move widgets**
- User asks to **rearrange multiple widgets at once**
- User wants to **remove widgets from the dashboard**

---

## Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | List all widgets with positions |
| POST | `/api/dashboard` | Add widget with auto-placement |
| PATCH | `/api/dashboard/:id` | Update position/title |
| DELETE | `/api/dashboard/:id` | Remove widget |
| PUT | `/api/dashboard/layout` | Bulk update all positions |

---

## Authentication

All endpoints use the standard Glance authentication:

- **Localhost requests**: Automatically authorized (no token needed)
- **External requests**: Require `Authorization: Bearer <AUTH_TOKEN>` header

---

## Endpoints

### GET /api/dashboard

List all widget instances currently on the dashboard with their positions.

**Response:**
```json
{
  "widgets": [
    {
      "id": "abc123",
      "type": "custom",
      "title": "GitHub PRs",
      "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
      "config": {},
      "custom_widget_id": "def456",
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "grid": {
    "columns": 12,
    "rows": 6
  }
}
```

**Fields:**
- `widgets` - Array of widget instances
- `grid.columns` - Always 12 (fixed grid width)
- `grid.rows` - Current height of the grid (max Y + H of all widgets)

---

### POST /api/dashboard

Add a widget to the dashboard. Supports three ways to specify the widget:

1. **By slug** (preferred): `{ "widget": "github-prs" }`
2. **By custom widget ID**: `{ "custom_widget_id": "abc123" }`
3. **By built-in type**: `{ "type": "clock" }`

**Request:**
```json
{
  "widget": "github-prs",
  "title": "My PRs",
  "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
  "config": {}
}
```

**Fields:**
- `widget` - Custom widget slug (preferred)
- `custom_widget_id` - Custom widget ID (alternative)
- `type` - Built-in widget type (e.g., `clock`, `notes`, `bookmarks`)
- `title` - Optional title override
- `position` - Optional position; if omitted, uses [auto-placement](#auto-placement)
- `config` - Optional widget configuration

**Response (201 Created):**
```json
{
  "id": "xyz789",
  "type": "custom",
  "title": "My PRs",
  "widget_slug": "github-prs",
  "custom_widget_id": "def456",
  "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
  "config": {},
  "auto_placed": false,
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

**Note:** `auto_placed: true` indicates the position was automatically determined.

---

### PATCH /api/dashboard/:instanceId

Update a widget's position, title, or config.

**Request:**
```json
{
  "title": "Updated Title",
  "position": { "x": 4, "y": 0, "w": 6, "h": 4 },
  "config": { "showClosed": true }
}
```

All fields are optional. Only provided fields are updated.

**Response:**
```json
{
  "id": "xyz789",
  "type": "custom",
  "title": "Updated Title",
  "position": { "x": 4, "y": 0, "w": 6, "h": 4 },
  "config": { "showClosed": true },
  "custom_widget_id": "def456",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T11:00:00.000Z"
}
```

---

### DELETE /api/dashboard/:instanceId

Remove a widget from the dashboard.

**Response:**
```json
{
  "success": true,
  "deleted": "xyz789"
}
```

---

### PUT /api/dashboard/layout

Bulk update positions for multiple widgets in a single atomic transaction. Use this for reorganizing the entire dashboard layout.

**Request:**
```json
{
  "layout": [
    { "id": "abc123", "x": 0, "y": 0, "w": 4, "h": 3 },
    { "id": "def456", "x": 4, "y": 0, "w": 4, "h": 3 },
    { "id": "ghi789", "x": 8, "y": 0, "w": 4, "h": 3 }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "updated": 3
}
```

**Validation:**
- All widget IDs must exist
- Position values must be non-negative integers
- Width and height must be at least 1

---

## Grid System

The dashboard uses a **12-column grid** with unlimited vertical rows.

**Position object:**
```typescript
{
  x: number;  // Column (0-11)
  y: number;  // Row (0+)
  w: number;  // Width in columns (1-12)
  h: number;  // Height in rows (1+)
}
```

**Default widget sizes:**

| Widget Type | Width | Height |
|-------------|-------|--------|
| clock | 3 | 2 |
| weather | 3 | 2 |
| notes | 4 | 3 |
| bookmarks | 3 | 3 |
| stat_card | 2 | 2 |
| github_prs | 4 | 3 |
| custom (default) | 4 | 3 |
| table | 6 | 4 |
| line_chart | 6 | 3 |

---

## Auto-Placement

When you POST a widget without a `position`, the API uses smart auto-placement:

1. Scans the grid **top-to-bottom, left-to-right**
2. Finds the **first available slot** that fits the widget
3. Falls back to **bottom of grid** if no gaps exist

This fills gaps in the layout rather than always stacking at the bottom.

**Example:** If you have widgets at (0,0) and (8,0), adding a 4-wide widget will place it at (4,0) to fill the gap.

---

## Responsive Layout Examples

### Desktop Layout (12 columns)

Three widgets side-by-side:
```json
{
  "layout": [
    { "id": "w1", "x": 0, "y": 0, "w": 4, "h": 3 },
    { "id": "w2", "x": 4, "y": 0, "w": 4, "h": 3 },
    { "id": "w3", "x": 8, "y": 0, "w": 4, "h": 3 }
  ]
}
```

### Tablet Layout (8 columns effective)

Two widgets per row:
```json
{
  "layout": [
    { "id": "w1", "x": 0, "y": 0, "w": 6, "h": 3 },
    { "id": "w2", "x": 6, "y": 0, "w": 6, "h": 3 },
    { "id": "w3", "x": 0, "y": 3, "w": 6, "h": 3 }
  ]
}
```

### Mobile Layout (stacked)

Full-width stacked widgets:
```json
{
  "layout": [
    { "id": "w1", "x": 0, "y": 0, "w": 12, "h": 3 },
    { "id": "w2", "x": 0, "y": 3, "w": 12, "h": 3 },
    { "id": "w3", "x": 0, "y": 6, "w": 12, "h": 3 }
  ]
}
```

---

## Common Workflows

### Add a widget by slug

```bash
curl -X POST http://localhost:3333/api/dashboard \
  -H "Content-Type: application/json" \
  -d '{"widget": "github-prs"}'
```

### Move a widget to a new position

```bash
curl -X PATCH http://localhost:3333/api/dashboard/abc123 \
  -H "Content-Type: application/json" \
  -d '{"position": {"x": 0, "y": 0, "w": 6, "h": 4}}'
```

### Reorganize entire dashboard

```bash
curl -X PUT http://localhost:3333/api/dashboard/layout \
  -H "Content-Type: application/json" \
  -d '{
    "layout": [
      {"id": "w1", "x": 0, "y": 0, "w": 6, "h": 3},
      {"id": "w2", "x": 6, "y": 0, "w": 6, "h": 3}
    ]
  }'
```

### Remove a widget

```bash
curl -X DELETE http://localhost:3333/api/dashboard/abc123
```

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": "Description of what went wrong"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Invalid request (missing fields, bad values) |
| 401 | Unauthorized (missing/invalid auth token) |
| 404 | Widget not found |
| 500 | Server error |
