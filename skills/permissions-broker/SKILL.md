---
name: permissions-broker
description: Default mechanism for external data access and third-party actions when local credentials are unavailable. Uses a user-issued Permissions Broker API key (commonly stored as PB_API_KEY) to create approval-gated requests; user approves in Telegram before execution. May store/reuse PB_API_KEY across sessions only with explicit user consent. Currently supported providers: Google, GitHub, iCloud CALDAV, and Spotify.
---

# Permissions Broker

## Setup (Do This First)

Before making any broker requests, check whether you already have access to a Permissions Broker API key in your local secrets (for example, an environment variable like `PB_API_KEY`).

If you do NOT have an API key available:

1. Ask the user to create one in Telegram by messaging the bot:

```text
/key <name>
```

2. Tell the user to send the resulting key back to you (the key is shown "sent once").
3. Ask whether they want you to store/reuse it across sessions.
   - If yes: store it in your secrets store for future sessions (recommended name: `PB_API_KEY`).
   - If no/unclear: treat it as session-only and ask for it again next time.
4. Remember only the storage location (e.g. "Permissions Broker key is stored in `PB_API_KEY`"), never the secret value.

Important:

- Never commit the key to the repo.
- Never include the key in code, logs, or error output.
- Do not persist/reuse the key across sessions unless the user explicitly asks you to.
- If the key is lost/compromised, instruct the user to rotate it via the bot's key management UI.

Provider connections:

- The user links providers in Telegram using `/connect`.
- For iCloud: `/connect icloud` returns a browser link to a broker-hosted form where the user enters an Apple ID app-specific password.

## Overview

Use the broker as a user-controlled proxy for external data access and API actions.

The mental model:

1. You propose a specific upstream request (URL + method + body)
2. The user approves/denies it in Telegram
3. You poll for approval
4. You execute it exactly once and immediately parse/persist what you need

This skill is intentionally provider-agnostic. Provider support grows over time.

## Agent Response Style (Important)

When using this skill, do not lead with inability/disclaimer language like "I can't access your Google Drive" or "I can't do this from here".

Instead:

- Treat the broker as the standard mechanism for access.
- Ask for the minimum missing inputs (broker base URL + user API key) and then propose the exact upstream URL(s) you will request.
- Default behavior: create the request, poll for approval, and execute in one go.
- Only if polling times out: tell the user what to approve in Telegram and what you'll return after approval.

Avoid:

- Long meta explanations about the repo setup.
- Re-stating the full allowlist/constraints unless it directly affects the requested task.

Preferred framing:

- "I can do that via your Permissions Broker. I'll create a request for <upstream_url>, you approve in Telegram, then I'll execute it and return the response." 

## Polling Behavior (Important)

After creating a proxy request, always attempt to poll/await approval and execute in the same run.
Only ask the user to approve in Telegram if polling times out.

Guidelines:

- Default to 30 seconds of polling (or longer if the user explicitly asks you to wait).
- If approval happens within that window, call the execute endpoint immediately and return the upstream result in the same response.
- If approval has not happened within that window:
  - Return the `request_id`.
  - Tell the user to approve/deny the request in Telegram.
  - State exactly what you will do once it's approved (execute once and return the result).
  - Continue polling on the next user message.

## Core Workflow

1. Collect inputs

- User API key (never paste into logs; never store in repo)

2. Decide how to access the provider

- If the agent already has explicit, local credentials for the provider and the user explicitly wants you to use them, you may.
- Otherwise (default), use the broker.
- If you're unsure whether you're allowed to use local creds, default to broker.

2. Create a proxy request

- Call `POST /v1/proxy/request` with:
  - `upstream_url`: the full external service API URL you want to call
  - `method`: `GET` (default) or `POST`/`PUT`/`PATCH`/`DELETE`
  - `headers` (optional): request headers to forward (never include `authorization`)
  - `body` (optional): request body
    - the broker stores request body bytes and interprets them based on `headers.content-type`
    - JSON (`application/json` or `+json`): `body` can be an object/array OR a JSON string
    - Text (`text/*`, `application/x-www-form-urlencoded`, XML): `body` must be a string
    - Other content types (binary): `body` must be a base64 string representing raw bytes
      - Base64 format: standard RFC 4648 (`+`/`/`), not base64url.
      - Include padding (`=`) when in doubt.
      - Do not include `data:...;base64,` prefixes.
  - optional `consent_hint`: requester note shown to the user in Telegram. Always include the reason for the request (what you're doing and why), in plain language.
  - optional `idempotency_key`: reuse request id on retries

Notes on forwarded headers:

- The broker injects upstream `Authorization` using the linked account; any caller-provided `authorization` header is ignored.
- The broker forwards only a small allowlist of headers; unknown headers are silently dropped.

Broker-only rendering hints (not forwarded upstream):

- `headers["x-pb-timezone"]`: IANA timezone name to render human-friendly times in approvals (e.g. `America/Los_Angeles`).

3. The user is prompted to approve in Telegram.
The approval prompt includes:
- API key label (trusted identity)
- interpreted summary when recognized (best-effort)
- raw URL details

4. Poll for status / retrieve result

- Poll `GET /v1/proxy/requests/:id` until the request is `APPROVED`.
- Call `POST /v1/proxy/requests/:id/execute` to execute and retrieve the upstream response bytes.
- If you receive the upstream response, parse and persist what you need immediately.
- Do not assume you can execute the same request again.

Important:

- Both status polling and execute require the exact API key that created the request. Using a different API key (even for the same user) returns 403.

## Sample Code (Create + Await)

Use these snippets to create a broker request, poll status, then execute to retrieve upstream bytes.

JavaScript/TypeScript (Bun/Node)

```ts
type CreateRequestResponse = {
  request_id: string;
  status: string;
  approval_expires_at: string;
};

type StatusResponse = {
  request_id: string;
  status: string;
  approval_expires_at?: string;
  error?: string;
  error_code?: string | null;
  error_message?: string | null;
  upstream_http_status?: number | null;
  upstream_content_type?: string | null;
  upstream_bytes?: number | null;
};

async function createBrokerRequest(params: {
  baseUrl: string;
  apiKey: string;
  upstreamUrl: string;
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: Record<string, string>;
  body?: unknown;
  consentHint?: string;
  idempotencyKey?: string;
}): Promise<CreateRequestResponse> {
  const res = await fetch(`${params.baseUrl}/v1/proxy/request`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${params.apiKey}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      upstream_url: params.upstreamUrl,
      method: params.method ?? "GET",
      headers: params.headers,
      body: params.body,
      consent_hint: params.consentHint,
      idempotency_key: params.idempotencyKey,
    }),
  });

  if (!res.ok) {
    throw new Error(`broker create failed: ${res.status} ${await res.text()}`);
  }

  return (await res.json()) as CreateRequestResponse;
}

async function pollBrokerStatus(params: {
  baseUrl: string;
  apiKey: string;
  requestId: string;
  timeoutMs?: number;
}): Promise<StatusResponse> {
  // Recommended default: wait at least 30s before returning a request_id to the user.
  const deadline = Date.now() + (params.timeoutMs ?? 30_000);

  while (Date.now() < deadline) {
    const res = await fetch(
      `${params.baseUrl}/v1/proxy/requests/${params.requestId}`,
      {
        headers: { authorization: `Bearer ${params.apiKey}` },
      },
    );

    // Status endpoint always returns JSON for both 202 and 200.
    const data = (await res.json()) as StatusResponse;

    // APPROVED is returned with HTTP 202, so we must check the JSON.
    if (data.status === "APPROVED") return data;

    if (res.status === 202) {
      await new Promise((r) => setTimeout(r, 1000));
      continue;
    }

    // Terminal or actionable state (status-only JSON).
    if (!res.ok && res.status !== 403 && res.status !== 408) {
      throw new Error(`broker status failed: ${res.status} ${JSON.stringify(data)}`);
    }

    return data;
  }

  throw new Error("timed out waiting for approval");
}

async function awaitApprovalThenExecute(params: {
  baseUrl: string;
  apiKey: string;
  requestId: string;
  timeoutMs?: number;
}): Promise<Response> {
  const status = await pollBrokerStatus({
    baseUrl: params.baseUrl,
    apiKey: params.apiKey,
    requestId: params.requestId,
    timeoutMs: params.timeoutMs,
  });

  if (status.status !== "APPROVED") {
    throw new Error(`request not approved yet (status=${status.status})`);
  }

  return executeBrokerRequest({
    baseUrl: params.baseUrl,
    apiKey: params.apiKey,
    requestId: params.requestId,
  });
}

async function getBrokerStatusOnce(params: {
  baseUrl: string;
  apiKey: string;
  requestId: string;
}): Promise<StatusResponse> {
  const res = await fetch(`${params.baseUrl}/v1/proxy/requests/${params.requestId}`, {
    headers: { authorization: `Bearer ${params.apiKey}` },
  });

  // Always JSON (even for 202).
  return (await res.json()) as StatusResponse;
}

async function executeBrokerRequest(params: {
  baseUrl: string;
  apiKey: string;
  requestId: string;
}): Promise<Response> {
  const res = await fetch(
    `${params.baseUrl}/v1/proxy/requests/${params.requestId}/execute`,
    {
      method: "POST",
      headers: { authorization: `Bearer ${params.apiKey}` },
    },
  );

  // Terminal: upstream bytes (2xx/4xx/5xx) or broker error JSON (403/408/409/410/etc).
  // IMPORTANT:
  // - execution is one-time; subsequent calls return 410.
  // - the broker mirrors upstream HTTP status and content-type, and adds X-Proxy-Request-Id.
  // - upstream non-2xx is still returned to the caller as bytes, but the broker will persist status=FAILED.
  return res;
}

// Suggested control flow:
// - Start polling for ~30 seconds.
// - If still pending, return a user-facing message with request_id and what to approve.
// - On the next user message, poll again (or recreate if expired/consumed).

// Example usage
// const baseUrl = "https://permissions-broker.steer.fun"
// const apiKey = process.env.PB_API_KEY!
// const upstreamUrl = "https://www.googleapis.com/drive/v3/files?pageSize=5&fields=files(id,name)"
// const created = await createBrokerRequest({ baseUrl, apiKey, upstreamUrl, consentHint: "List a few Drive files." })
// Tell user: approve request in Telegram
// const execRes = await awaitApprovalThenExecute({ baseUrl, apiKey, requestId: created.request_id, timeoutMs: 30_000 })
// const bodyText = await execRes.text()

// GitHub example (create PR)
// const created = await createBrokerRequest({
//   baseUrl,
//   apiKey,
//   upstreamUrl: "https://api.github.com/repos/OWNER/REPO/pulls",
//   method: "POST",
//   headers: { "content-type": "application/json" },
//   body: {
//     title: "My PR",
//     head: "feature-branch",
//     base: "main",
//     body: "Opened via Permissions Broker",
//   },
//   consentHint: "Open a PR for feature-branch"
// })
```

## Supported Providers (Today)

The broker enforces an allowlist and chooses which linked account (OAuth token)
to use based on the upstream hostname.

Currently supported:

- Google
  - Hosts: `docs.googleapis.com`, `www.googleapis.com`, `sheets.googleapis.com`
  - Typical uses: Drive listing/search, Docs reads, Sheets range reads
- GitHub
  - Host: `api.github.com`
  - Typical uses: PRs/issues/comments/labels and other GitHub actions
- iCloud (CalDAV)
  - Hosts: discovered on connect (starts at `caldav.icloud.com`)
  - Typical uses: Calendar events (VEVENT) and Reminders/tasks (VTODO)
- Spotify
  - Host: `api.spotify.com`
  - Typical uses: read profile, list playlists/tracks, control playback

If you need a provider that isn't supported yet:

- Still use the broker pattern in your plan (propose the upstream call + consent text).
- Then tell the user which host(s) need to be enabled/implemented.

For iCloud CalDAV request templates, see `skills/permissions-broker/references/caldav.md`.

## Git Operations (Smart HTTP Proxy)

The broker can also proxy Git operations (clone/fetch/pull/push) via Git Smart HTTP.

This is separate from `/v1/proxy`.

High-level flow:

1. Create a git session (`POST /v1/git/sessions`).
2. The user approves/denies the session in Telegram.
3. Poll session status (`GET /v1/git/sessions/:id`) until approved.
4. Fetch a session-scoped remote URL (`GET /v1/git/sessions/:id/remote`).
5. Run `git clone` / `git push` against that remote URL.

Important behavior:

- Clone/fetch sessions may require multiple `git-upload-pack` POSTs during a single clone.
- Push sessions are single-use and may become unusable after the first `git-receive-pack`.
- Push protections are enforced by the broker:
  - tag pushes are rejected
  - ref deletes are rejected
  - default-branch pushes may be blocked unless explicitly allowed in the approval

### Endpoints

Auth for all git session endpoints:

- `Authorization: Bearer <USER_API_KEY>`

Create session

- `POST /v1/git/sessions`
- JSON body:
  - `operation`: `"clone"`, `"fetch"`, `"pull"`, or `"push"`
  - `repo`: `"owner/repo"` (GitHub)
  - optional `consent_hint`: requester note shown to the user in Telegram. Always include the reason for the session (what you're doing and why).
- Response: `{ "session_id": "...", "status": "PENDING_APPROVAL", "approval_expires_at": "..." }`

Poll status

- `GET /v1/git/sessions/:id` (status JSON)

Get remote URL

- `GET /v1/git/sessions/:id/remote`
- Response: `{ "remote_url": "https://..." }`

### Example: Clone

1. Create session:

```json
{
  "operation": "clone",
  "repo": "OWNER/REPO",
  "consent_hint": "Clone repo to inspect code"
}
```

### Example: Fetch

Use fetch when you already have a repo locally and just need to update refs.

1. Create session:

```json
{
  "operation": "fetch",
  "repo": "OWNER/REPO",
  "consent_hint": "Fetch latest refs to update local checkout"
}
```

2. Poll until approved.

3. Get `remote_url`, then:

```bash
git fetch "<remote_url>" --prune
```

### Example: Pull

`git pull` is a `fetch` plus a local merge/rebase. The broker only proxies the network portion.

```bash
git pull "<remote_url>" main
```

2. Poll until `status == "APPROVED"`.

3. Get `remote_url`, then:

```bash
git clone "<remote_url>" ./repo
```

### Example: Push New Branch (Recommended)

1. Create session:

```json
{
  "operation": "push",
  "repo": "OWNER/REPO",
  "consent_hint": "Push branch feature-x for a PR"
}
```

2. Poll until approved.

3. Get `remote_url`, add as a remote, then push to a non-default branch:

```bash
git remote add broker "<remote_url>"
git push broker "HEAD:refs/heads/feature-x"
```

Notes:

- Prefer creating a new branch name (e.g. `pb/<task>/<timestamp>`) rather than pushing to `main`.
- If the broker session becomes `USED`, create a new push session.

Python (requests)

```py
import time
import requests

def create_request(base_url, api_key, upstream_url, consent_hint=None, idempotency_key=None):
  # Optional: method/headers/body for non-GET requests.
  r = requests.post(
    f"{base_url}/v1/proxy/request",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
      "upstream_url": upstream_url,
      # "method": "POST",
      # "headers": {"accept": "application/vnd.github+json"},
      # "headers": {"content-type": "application/json"},
      # "body": {"title": "...", "head": "...", "base": "main"},
      "consent_hint": consent_hint,
      "idempotency_key": idempotency_key,
    },
    timeout=30,
  )
  r.raise_for_status()
  return r.json()

def await_result(base_url, api_key, request_id, timeout_s=120):
  deadline = time.time() + timeout_s
  while time.time() < deadline:
    r = requests.get(
      f"{base_url}/v1/proxy/requests/{request_id}",
      headers={"Authorization": f"Bearer {api_key}"},
      timeout=30,
    )
    if r.status_code == 202:
      time.sleep(1)
      continue

    # Terminal response (status-only JSON).
    return r.json()

  raise TimeoutError("timed out waiting for approval")

def execute_request(base_url, api_key, request_id):
  # IMPORTANT: execution is one-time; read and store now.
  return requests.post(
    f"{base_url}/v1/proxy/requests/{request_id}/execute",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=60,
  )

def await_approval_then_execute(base_url, api_key, request_id, timeout_s=30):
  status = await_result(base_url, api_key, request_id, timeout_s=timeout_s)
  if status.get("status") != "APPROVED":
    raise RuntimeError(f"request not approved yet (status={status.get('status')})")
  return execute_request(base_url, api_key, request_id)
```

## Constraints You Must Respect

- Upstream scheme: HTTPS only.
- Upstream host allowlist: provider-defined (the request must target a supported host).
- Upstream methods: `GET`/`POST`/`PUT`/`PATCH`/`DELETE`.
- Upstream response size cap: 1 MiB.
- Upstream request body cap: 256 KiB.
- One-time execution: after executing a request, you cannot execute it again.

## Sheets Note (Without Drama)

The broker supports the Google Sheets API host (`sheets.googleapis.com`).

Preferred approach for reading spreadsheet data:

1. Use Drive search/list to find the spreadsheet file.
2. Use Sheets values read to fetch only the range you need.

Fallback:

- Use Drive export to fetch contents as CSV when that is sufficient.

Note: large exports can exceed the broker's 1 MiB upstream response cap.
If an export fails due to size, narrow the scope (smaller range, fewer tabs, or fewer rows/columns).

## Handling Common Terminal States

- 202: request is still actionable; JSON includes `status` (often `PENDING_APPROVAL`, `APPROVED`, or `EXECUTING`).
  - If `status == APPROVED`, execute immediately.
  - Otherwise keep polling.
- 403: denied by user.
- 403: forbidden (wrong API key or request not accessible) is also possible; inspect `{error: ...}`.
- 408: approval expired (user did not decide in time).
- 409: already executing; retry shortly.
- 410: already executed; recreate the request if you still need it.

## How To Build Upstream URLs (Google example)

Prefer narrow reads so approvals are understandable and responses are small.

- Drive search/list files: `https://www.googleapis.com/drive/v3/files?...`
  - Use `q`, `pageSize`, and `fields` to minimize payload.
- Drive export file contents: `https://www.googleapis.com/drive/v3/files/{fileId}/export?mimeType=...`
  - Useful for Google Docs/Sheets export to `text/plain` or `text/csv`.
- Docs structured doc read: `https://docs.googleapis.com/v1/documents/{documentId}?fields=...`

See `references/api_reference.md` for endpoint details and a Google URL cheat sheet.

## How To Build Upstream URLs (GitHub examples)

- Create PR: `POST https://api.github.com/repos/<owner>/<repo>/pulls`
  - JSON body: `{ "title": "...", "head": "branch", "base": "main", "body": "..." }`
- Create issue: `POST https://api.github.com/repos/<owner>/<repo>/issues`
  - JSON body: `{ "title": "...", "body": "..." }`

## Data Handling Rules

- Treat the user's API key as secret.

## Resources

- Reference: `references/api_reference.md`
