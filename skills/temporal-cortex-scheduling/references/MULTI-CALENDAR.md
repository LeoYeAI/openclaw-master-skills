# Multi-Calendar Operations

Temporal Cortex supports simultaneous connections to Google Calendar, Microsoft Outlook, and CalDAV (iCloud, Fastmail). All calendars are merged into a unified view.

## Discovering Connected Calendars

Use `list_calendars` as the first step to discover all connected calendars:

```
list_calendars()
→ [
    { id: "google/primary", provider: "google", name: "Personal", label: "Main", primary: true, access_role: "owner" }
    { id: "google/work", provider: "google", name: "Work Calendar", primary: false, access_role: "writer" }
    { id: "outlook/AAA123", provider: "outlook", name: "Outlook Calendar", primary: true, access_role: "owner" }
  ]
```

Filter by provider if needed: `list_calendars(provider: "google")`.

Use the returned `id` values as `calendar_id` in all subsequent tool calls. This eliminates guessing at calendar IDs.

## Calendar Labels

Labels are user-assigned nicknames for calendars. They help agents and users identify calendars by purpose rather than cryptic IDs:

| Calendar ID | Name (from provider) | Label (user-assigned) |
|------------|---------------------|----------------------|
| `google/primary` | "Personal" | "Main" |
| `google/abc123` | "billy@work.com" | "Work" |
| `outlook/AAA123` | "Calendar" | "Outlook Work" |

Labels are set during `cortex-mcp setup` or via configuration. When presenting calendars to users, prefer the label (if set) over the raw name.

## Provider-Prefixed Calendar IDs

All calendar IDs returned by `list_calendars` use provider-prefixed format:

| Format | Example | Routes to |
|--------|---------|-----------|
| `google/<id>` | `"google/primary"` | Google Calendar |
| `outlook/<id>` | `"outlook/work"` | Microsoft Outlook |
| `caldav/<id>` | `"caldav/personal"` | CalDAV (iCloud, Fastmail) |
| `<id>` (bare) | `"primary"` | Default provider |

Bare IDs (without prefix) route to the default provider configured during setup. Prefer using the full provider-prefixed IDs from `list_calendars` for clarity.

CalDAV calendar IDs can contain slashes (e.g., path-style IDs). The router splits on the first `/` only — everything after the prefix slash is the calendar ID.

## Cross-Calendar Availability

Use `get_availability` with the calendar IDs from `list_calendars` to get a merged view:

```
1. list_calendars() → discover connected calendars
2. get_availability(
     start: "2026-03-16T00:00:00-04:00",
     end: "2026-03-17T00:00:00-04:00",
     calendar_ids: ["google/primary", "outlook/AAA123", "caldav/personal"],
     privacy: "full"
   ) → merged free/busy blocks across all calendars
```

The server fetches events from all providers in parallel and merges them into unified busy/free blocks.

## Privacy Modes

| Mode | `source_count` | Use case |
|------|---------------|----------|
| `"opaque"` (default) | Always `0` | Sharing availability externally — hides which calendars are busy |
| `"full"` | Actual count | Internal use — shows how many calendars contribute to each busy block |

## Provider Authentication

Each provider requires a one-time authentication:

```bash
# Google Calendar (OAuth2, browser-based consent)
npx @temporal-cortex/cortex-mcp auth google

# Microsoft Outlook (Azure AD OAuth2 with PKCE)
npx @temporal-cortex/cortex-mcp auth outlook

# CalDAV (app-specific password, presets for iCloud/Fastmail)
npx @temporal-cortex/cortex-mcp auth caldav
```

Credentials are stored locally at `~/.config/temporal-cortex/credentials.json`. Provider registrations are saved in `~/.config/temporal-cortex/config.json`.

## Environment Variables

| Variable | When Needed | Description |
|----------|-------------|-------------|
| `GOOGLE_CLIENT_ID` | Custom OAuth app only | Google OAuth Client ID (built-in default available) |
| `GOOGLE_CLIENT_SECRET` | Custom OAuth app only | Google OAuth Client Secret (built-in default available) |
| `MICROSOFT_CLIENT_ID` | Custom OAuth app only | Azure AD application (client) ID (built-in default available) |
| `MICROSOFT_CLIENT_SECRET` | Custom OAuth app only | Azure AD client secret (built-in default available) |
| `TIMEZONE` | Optional | IANA timezone override (auto-detected if not set) |
| `WEEK_START` | Optional | `"monday"` (default) or `"sunday"` |

CalDAV providers need no environment variables — authentication is interactive.

## Single-Provider Shortcuts

If only one provider is configured (visible via `list_calendars`), you can use bare calendar IDs:

```json
{ "calendar_id": "primary" }
```

This routes to whichever provider is configured. No prefix needed.

## Booking Across Providers

`book_slot` works with any provider. Use the provider prefix to specify where to create the event:

```json
{
  "calendar_id": "google/primary",
  "start": "2026-03-16T14:00:00-04:00",
  "end": "2026-03-16T15:00:00-04:00",
  "summary": "Team Sync"
}
```

The conflict check queries the specified calendar. For cross-calendar conflict detection, use `get_availability` first.
