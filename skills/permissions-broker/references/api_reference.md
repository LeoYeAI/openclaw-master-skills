# Permissions Broker - Agent Reference

Keep this file as a quick reference for how an agent should call the broker.

## Broker API

Base URL: the broker service URL `https://permissions-broker.steer.fun`.

Auth

- Header: `Authorization: Bearer <USER_API_KEY>`
- The API key label (set by the user at key creation time) is the caller identity shown in Telegram approvals.

Create request

- `POST /v1/proxy/request`
- JSON body:
  - `upstream_url` (required): full https URL targeting an allowed upstream host
  - `method` (optional, default `GET`): `GET` | `POST` | `PUT` | `PATCH` | `DELETE`
    - For iCloud CalDAV, WebDAV methods like `PROPFIND` and `REPORT` are supported.
  - `headers` (optional): forwarded upstream request headers
    - `authorization` is always ignored; the broker injects an OAuth bearer token from the linked account
    - typical safe keys: `accept`, `content-type`, `if-match`, `if-none-match`
    - GitHub-specific: `x-github-api-version`
    - Broker-only (not forwarded upstream):
      - `x-pb-timezone`: rendering hint for human-readable approvals (e.g. `America/Los_Angeles`)
  - `body` (optional): request body
    - interpretability comes from `headers.content-type`
    - JSON (`application/json` or `+json`): `body` can be an object/array OR a JSON string
    - Text (`text/*`, `application/x-www-form-urlencoded`, XML): `body` must be a string
    - Other content types (binary): `body` must be a base64 string representing raw bytes
  - `consent_hint` (optional): short explanation for the user
  - `idempotency_key` (optional): stable token to dedupe retries
- Response:
  - `request_id`
  - `status` (typically `PENDING_APPROVAL`)
  - `approval_expires_at`

Poll / retrieve

Status (poll)

- `GET /v1/proxy/requests/:id`
- This endpoint is status-only and returns JSON.
- While the request is still actionable (`PENDING_APPROVAL`, `APPROVED`, or `EXECUTING`), it returns HTTP `202` with `Retry-After: 1` and a JSON body like:

```json
{ "request_id": "...", "status": "APPROVED", "approval_expires_at": "..." }
```

- Terminal states return HTTP `200` with JSON describing the terminal state (`SUCCEEDED` / `FAILED`).

Execute (retrieve upstream bytes)

- `POST /v1/proxy/requests/:id/execute`
- Executes the request (must be APPROVED) and returns the upstream response bytes.
- Must be called using the same API key that created the request.
- One-time execution: subsequent calls return HTTP 410.
- Response behavior:
  - Mirrors the upstream HTTP status code (e.g. upstream 201 -> broker 201; upstream 422 -> broker 422).
  - Sets `Content-Type` to the upstream `content-type` when present.
  - Adds `X-Proxy-Request-Id: <id>`.
  - If the broker rejects execution (not approved/expired/forbidden/etc.), it returns JSON `{error: ...}`.

Debug

- `GET /v1/whoami` returns the authenticated key label and ids.

Connected services

- `GET /v1/accounts/`
- Response:
  - `accounts`: list of linked accounts for the authenticated user
    - `provider` (e.g. `google`)
    - `scopes`
    - `status`
    - other non-secret metadata
    - for iCloud, the broker may include CalDAV discovery bounds (hostnames + path prefixes) to help agents form valid requests

## Upstream URL Rules (MVP)

- Scheme: https only
- Allowed hosts:
  - Google: `www.googleapis.com`, `docs.googleapis.com`, `sheets.googleapis.com`
  - GitHub: `api.github.com`
  - iCloud (CalDAV): discovered on connect (starts at `caldav.icloud.com`)

Provider selection

- The broker infers which linked account to use from `upstream_url.hostname`.
- If no linked account exists for that provider, execution fails with `NO_LINKED_ACCOUNT`.

iCloud allowlisting

- For iCloud CalDAV, the broker enforces a strict per-user allowlist derived during connect:
  - allowed hostnames (e.g. `pXX-caldav.icloud.com`)
  - allowed path prefixes (principal + home-set)
- Requests outside that scope are rejected.

Practical guidance

- Prefer small, targeted responses; always use `fields` where supported.
- Prefer paginated list endpoints with small page sizes.

## Useful Google API URL Patterns

Drive list/search

- Host: `www.googleapis.com`
- Path: `/drive/v3/files`
- Query params:
  - `q` (Drive query language)
  - `pageSize`
  - `fields`

Drive get file metadata

- `/drive/v3/files/{fileId}?fields=...`

Drive export (Docs/Sheets to text formats)

- `/drive/v3/files/{fileId}/export?mimeType=text/plain`
- `/drive/v3/files/{fileId}/export?mimeType=text/csv`

Docs structured read

- Host: `docs.googleapis.com`
- Path: `/v1/documents/{documentId}`
- Query params:
  - `fields` (partial response)

Sheets read values

- Host: `sheets.googleapis.com`
- Path: `/v4/spreadsheets/{spreadsheetId}/values/{range}`
- Practical ranges:
  - `Sheet1!A1:Z100`
- Query params (optional):
  - `majorDimension`
  - `valueRenderOption`
  - `dateTimeRenderOption`

## One-time Retrieval Gotchas

Always parse and persist what you need on the first successful execution.

If you need the same upstream content again, you must create a new proxy request (and the user must approve again).

## Recommended Agent Wording

Use short, action-forward phrasing. Do not lead with inability/disclaimer language.

Good:

- "I'll do that via your Permissions Broker. I'll request <upstream_url>, you approve in Telegram, then I'll fetch the result."
- "To read that Sheet in MVP, I'll export it via Drive as CSV and parse it."

Avoid:

- "I can't access your Google Drive" (the broker is the intended access mechanism)
- Long repo/setup explanations

## Safety / Secret Handling

- Never paste API keys into chat logs or commit them.
- Do not log full upstream responses if they may contain sensitive data.

## Common Error Shapes

These errors are returned as JSON from the broker (not upstream bytes).

- `403 {"error":"forbidden"}`: wrong API key or request not accessible to this key
- `403 {"error":"denied"}`: user denied the request in Telegram
- `408 {"error":"approval_expired"}`: approval TTL elapsed
- `409 {"error":"executing"}`: someone else is executing; retry shortly
- `410 {"error":"already_executed"}`: one-time request already consumed; create a new one

## GitHub API Examples

Create pull request

- Upstream:
  - `POST https://api.github.com/repos/<owner>/<repo>/pulls`
- Body (via `body` + `content-type: application/json`):
  - `title` (string)
  - `head` (string): source branch (e.g. `feature-branch`)
  - `base` (string): target branch (e.g. `main`)
  - `body` (string, optional)

Example broker request body:

```json
{
  "upstream_url": "https://api.github.com/repos/OWNER/REPO/pulls",
  "method": "POST",
  "headers": { "content-type": "application/json" },
  "body": {
    "title": "My PR",
    "head": "feature-branch",
    "base": "main",
    "body": "Opened via Permissions Broker"
  },
  "consent_hint": "Open a PR from feature-branch to main"
}
```
