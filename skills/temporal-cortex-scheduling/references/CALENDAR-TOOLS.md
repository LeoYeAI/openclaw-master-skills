# Calendar Tools Reference

Complete input/output schemas for the 6 calendar tools documented below. All are read-only and idempotent. TOON is the default output format for tools that support it (~40% fewer tokens than JSON).

## Tool Annotations

| Tool | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` |
|------|:-:|:-:|:-:|:-:|
| `list_calendars` | true | false | true | true |
| `list_events` | true | false | true | true |
| `find_free_slots` | true | false | true | true |
| `expand_rrule` | true | false | true | false |
| `check_availability` | true | false | true | true |
| `get_availability` | true | false | true | true |

`expand_rrule` is closed-world (no external API calls). All others make external API calls to calendar providers.

---

## list_calendars

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | No | Filter by provider: `"google"`, `"outlook"`, `"caldav"` |
| `format` | string | No | `"toon"` (default) or `"json"` |

**Output:** Array of calendars, each with: `id` (provider-prefixed), `provider`, `name`, `label` (optional, user-assigned), `primary` (boolean), `access_role`

---

## list_events

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID (supports provider prefix) |
| `start` | string | Yes | Range start (RFC 3339) |
| `end` | string | Yes | Range end (RFC 3339) |
| `format` | string | No | `"toon"` (default, ~40% fewer tokens) or `"json"` |

**Output:** `content`, `format`, `count`

---

## find_free_slots

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID (supports provider prefix) |
| `start` | string | Yes | Window start (RFC 3339) |
| `end` | string | Yes | Window end (RFC 3339) |
| `min_duration_minutes` | integer | No | Minimum slot length (default: 30) |
| `format` | string | No | `"toon"` (default) or `"json"` |

**Output:** `slots` (array of `{start, end, duration_minutes}`), `count`

---

## expand_rrule

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `rrule` | string | Yes | RFC 5545 RRULE string |
| `dtstart` | string | Yes | Local datetime (no timezone suffix) |
| `timezone` | string | Yes | IANA timezone |
| `duration_minutes` | integer | No | Instance duration (default: 60) |
| `count` | integer | No | Max instances to return |
| `format` | string | No | `"toon"` (default) or `"json"` |

**Output:** `instances` (array of `{start, end}`), `count`

---

## check_availability

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `calendar_id` | string | Yes | Calendar ID (supports provider prefix) |
| `start` | string | Yes | Slot start (RFC 3339) |
| `end` | string | Yes | Slot end (RFC 3339) |

**Output:** `available` (boolean)

---

## get_availability

**Input:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | string | Yes | Window start (RFC 3339) |
| `end` | string | Yes | Window end (RFC 3339) |
| `calendar_ids` | string[] | No | Calendar IDs (default: `["primary"]`) |
| `min_free_slot_minutes` | integer | No | Min free slot (default: 30) |
| `privacy` | string | No | `"opaque"` (default) or `"full"` |
| `format` | string | No | `"toon"` (default) or `"json"` |

**Output:** `busy` (array of `{start, end, source_count}`), `free` (array of `{start, end, duration_minutes}`), `calendars_merged`, `privacy`
