---
name: web-autopilot
description: >
  Record any web app operation once, AI turns it into a reusable automation tool.
  Use when: (1) automating repetitive tasks on any web application (reports, submissions,
  data extraction), (2) creating no-code automation for any logged-in web app,
  (3) building callable tools from recorded browser sessions.
  Supports REST, GraphQL, form submissions, file uploads, any login method.
  Task types: query/export (data extraction) and submit (form submissions like expense reports,
  travel requests, payment requests).
---

# Web Autopilot

> Record once in any web app, let AI handle it from now on.

## Overview

Record → Analyze → **Confirm Fields** → Generate → Test → Register as Tool

```
🎬 Record         User performs the workflow once in a real browser (after login)
🔍 Analyze        AI analyzes network traffic, classifies fixed/dynamic/session fields
✅ Confirm Fields  [Required for submit tasks] User confirms field classifications
📝 Generate       Generates reusable TS script + field mapping
🧪 Test           Iterative test loop, up to 5 rounds of auto-fix
🔧 Register       Register as an OpenClaw tool for direct invocation
```

## Task Types

### 📊 Query / Export
Data extraction and report generation. Scripts run and output results automatically — no manual intervention needed.
Examples: pull sales reports, extract project data, export revenue details

### 📝 Submit
Submit forms such as expense reports, travel requests, payment requests, etc. **Each run requires dynamic parameters.**
Examples: submit travel request, submit expense report, submit payment request

The key challenge for submit tasks: **correctly distinguishing which fields are fixed vs. which change every time**, and confirming with the user before generating the script.

## Skill Directory

```
~/.openclaw/rpa/
├── recordings/<task-name>/recording.json
├── tasks/<task-name>/
│   ├── task-meta.json
│   ├── run.ts
│   └── field-mapping.json
└── sessions/<domain>.session.json
```

Skill scripts: `/opt/homebrew/lib/node_modules/openclaw/skills/web-autopilot/scripts/`

---

## Commands

### 1. `record` — Record a workflow

Ask user: task name, login URL or app URL.

```bash
cd /opt/homebrew/lib/node_modules/openclaw/skills/web-autopilot

# Option A: Start from login page (SSO, OAuth, username/password, etc.)
npx ts-node scripts/record.ts --name "my-task" --sso-url "https://login.example.com"

# Option B: Start directly from app (if already logged in or no login needed)
npx ts-node scripts/record.ts --name "my-task" --app-url "https://app.example.com"
```

Run in PTY mode (pty: true, background: true). User operates browser, types "done" when finished.

Note: `--sso-url` is a legacy parameter name; it works for **any** login URL (SSO, OAuth, plain login page, etc.).

### 2. `analyze` — Analyze the recording (AI does this)

Read recording.json, separate login traffic from business traffic, identify core APIs.

**Key steps:**
1. Read `~/.openclaw/rpa/recordings/<task>/summary.txt` for overview
2. Parse recording.json to extract all API calls to app domain
3. For each POST/PUT/PATCH with meaningful body:
   - Classify fields: FIXED / DYNAMIC / SESSION / RELATIONAL
   - Detect protocol: rest-json / graphql / form-urlencoded / multipart
4. Map the complete API sequence (prerequisites → main operation → follow-ups)
5. **Analyze ALL response fields and create field-mapping.json with human-readable labels**
6. Create task-meta.json
7. **[Submit tasks] After analysis, present the field classification confirmation table to the user (see below)**

#### Field Classification

| Type | Meaning | Handling |
|------|---------|----------|
| **FIXED** | Same value every submission (approval flow ID, company entity, currency, expense type enums…) | Hardcoded in script |
| **DYNAMIC** | Different each submission (amount, date, reason, attachment path…) | Becomes CLI `--parameter` |
| **SESSION** | Auth tokens/cookies, auto-managed | Injected by session.ts |
| **RELATIONAL** | Requires a lookup from another API to get the ID (e.g., project ID, person ID…) | Auto-queried in script, or exposed as DYNAMIC parameter |

#### Field Analysis Rules (MANDATORY)

**Every field must have a human-readable label.** Including system-generated field names.

Inference priority:
1. **Data value type**: timestamp (10^12-13) / monetary amount (contextual) / enum (fixed values) / URL / JSON object
2. **Field name pattern**: *time/*date/*_at → datetime | *amount/*price/*cost → monetary | *id/*_key → ID | *status/*state → status
3. **Business context**: infer from related fields, API endpoint names
4. If uncertain → annotate as `(unknown meaning: sample value)`

#### Field Confirmation Step (MANDATORY for Submit tasks)

After analysis, **you must present the following confirmation table to the user and wait for confirmation before generating the script**:

```
📋 Field Classification Confirmation — <task name>

✅ FIXED (hardcoded):
  - approvalFlowId: "xxx"  → Approval Flow ID
  - companyId: "yyy"       → Company Entity
  - currency: "CNY"        → Currency

🔄 DYNAMIC (passed as parameters each run):
  - amount          → Amount (example: --amount 1500)
  - startDate       → Start Date (example: --startDate 2026-03-10)
  - endDate         → End Date (example: --endDate 2026-03-12)
  - destination     → Destination (example: --destination "New York")
  - reason          → Reason (example: --reason "Client visit")
  - attachments     → Attachment path (example: --attachments ~/Desktop/receipt.jpg)

🔗 RELATIONAL (auto-queried):
  - projectId       → Project ID (auto-looked up by project name, --projectName "Project X")

❓ Needs confirmation (AI uncertain):
  - field_abc123    → Unknown meaning (recorded value: "0"), suggest: FIXED("0") or DYNAMIC?

Please confirm the above classification or indicate any fields that need adjustment.
```

**Only proceed to the Generate step after user confirmation.**

#### CSV Export Rules (MANDATORY)

- **Keep ALL fields**, including hidden fields, dynamic fields, system fields — never crop
- Field order: preserve original order from data, **never sort** (sorting causes column misalignment)
- JSON/object fields → convert to JSON string for storage
- Use `csv.writer` + proper quoting to handle JSON fields containing commas

### 3. `generate` — Generate the task script

**Pre-generation checklist (Query/Export tasks)**:
- ✅ All fields are in field-mapping.json
- ✅ All fields have human-readable labels
- ✅ CSV export uses field-mapping.json for column headers
- ✅ Field order preserves original order

**Pre-generation checklist (Submit tasks)**:
- ✅ User has confirmed field classification (FIXED / DYNAMIC / RELATIONAL)
- ✅ All DYNAMIC fields converted to CLI parameters (with type, example value, required/optional)
- ✅ RELATIONAL fields have auto-query logic or corresponding parameters
- ✅ Script has `--dry-run` mode (prints request body without submitting, for testing)
- ✅ Script outputs submission result (success/failure + document number/link)

**Submit task invocation example** (written to task-meta.json `usage` field after generation):
```bash
# Preview (no actual submission)
npx ts-node run.ts --dry-run --amount 1500 --startDate 2026-03-10 ...

# Submit for real
npx ts-node run.ts --amount 1500 --startDate 2026-03-10 --destination "New York" --reason "Client visit"
```

### 4. `test` — Iterative test loop (max 5 rounds)

Run script → check output → if error: diagnose → fix → repeat.

| Error | Cause | Fix |
|-------|-------|-----|
| 401/403 | Session expired / wrong auth | Re-check auth headers, re-login |
| 400 | Wrong field name/type | Compare with recording |
| 404 | Wrong URL | Check URL exactly |
| JSON parse error | Response is HTML | Log resp.raw |

### 5. `run` — Execute a registered task

```bash
npx ts-node ~/.openclaw/rpa/tasks/<task>/run.ts --param1 value1
```

### 6. `list` — List all tasks

```bash
npx ts-node /opt/homebrew/lib/node_modules/openclaw/skills/web-autopilot/scripts/run-task.ts --list
```

---

## Session & Credential Management

### Session (Cookie/Token Storage)

Sessions are cookie-based and work with **any login method**:
- SSO (OIDC, SAML, CAS, etc.)
- OAuth / OAuth2
- Username + password forms
- Any browser-based authentication

Session files: `~/.openclaw/rpa/sessions/<domain>.session.json`

### Credentials (Encrypted Storage)

Login credentials are stored **encrypted** (AES-256-GCM) in a separate file — **never stored in plaintext**.

File: `~/.openclaw/rpa/credentials.enc`
- Encryption key = machine identity (hostname+username) + optional `RPA_CREDENTIAL_KEY` env var
- File permissions: 0600 (owner only)
- Supports automatic extraction and encrypted storage from recording.json

```bash
# Manage credentials
npx ts-node scripts/utils/credentials.ts list                    # List saved domains + usernames
npx ts-node scripts/utils/credentials.ts save <domain> <user> <pass>  # Save manually
npx ts-node scripts/utils/credentials.ts delete <domain>         # Delete
npx ts-node scripts/utils/credentials.ts extract <recording.json> # Extract from recording
```

### Auto-Login Flow

When a session expires, the auto-login flow kicks in:

```
1. Read encrypted credentials for the target domain from credentials.enc
2. Select login strategy based on loginFlow.type
3. Launch browser (headless if credentials exist, headed if not)
4. Execute login steps → follow redirects → reach target app
5. Capture cookies/tokens → save new session
6. If all else fails → open headed browser for manual login (fallback)
```

#### Login Flow Types

When generating scripts, **you must identify the login type from the recording** and write it to the `loginFlow` field in `task-meta.json`:

| type | Scenario | Auto-login method | Example |
|------|----------|-------------------|---------|
| **`api`** | SSO/app provides a REST login endpoint, single POST completes auth | Call API directly → follow redirects | Enterprise SSO (`POST /api/sso/login`) |
| **`form`** | Single-page login form (username + password on same page) | Fill form fields → click submit | Common admin dashboards |
| **`multi-step`** | Multi-step login (email → next page → password → next page → possible 2FA) | Execute step sequence | Google, Microsoft, Okta |
| **`manual-only`** | Has CAPTCHA/2FA/risk control, cannot be fully automated | Open headed browser directly | Banking systems, strong CAPTCHA sites |

#### loginFlow Schema (task-meta.json)

```jsonc
{
  "loginFlow": {
    "type": "api",              // api | form | multi-step | manual-only
    "loginUrl": "https://sso.example.com",
    "loginDomain": "sso.example.com",
    "appDomain": "app.example.com",

    // ── type=api specific fields ──
    "loginApiPath": "/api/sso/login",
    "authType": "passwordAuth",       // Optional, auth type field in API body
    "appId": "1234567890",            // Optional, SSO portal app ID (for forward redirect)
    "appForwardUrl": "...",           // Optional, direct redirect URL (alternative to appId)

    // ── type=form specific fields ──
    "usernameSelector": "input[name='email']",    // Optional, custom selectors
    "passwordSelector": "input[type='password']",
    "submitSelector": "button[type='submit']",

    // ── type=multi-step specific fields ──
    "steps": [
      { "action": "fill", "selector": "input[type=email]", "field": "username" },
      { "action": "click", "selector": "#identifierNext" },
      { "action": "wait", "selector": "input[type=password]", "timeoutMs": 5000 },
      { "action": "fill", "selector": "input[type=password]", "field": "password" },
      { "action": "click", "selector": "#passwordNext" }
    ],

    // ── Common fields ──
    "successIndicator": "url_contains:app.example.com",  // Condition to detect successful login
    "postLoginWaitMs": 3000          // Wait time after login success (for cookies to settle)
  }
}
```

#### Login Identification Guide for Analyze Step (MANDATORY)

During the analyze step, you **must** complete the following login analysis:

1. **Extract credentials** → `credentials.ts extract <recording.json>` (auto-detects username/password in POST body)
2. **Identify login type** → Inspect the login flow in the recording:
   - Has a clear `POST login/auth API` → type = `api`
   - Has form fill actions (password type input) on the same page → type = `form`
   - Has multiple form fill actions with page navigations in between → type = `multi-step`
   - Has CAPTCHA image requests or reCAPTCHA scripts → type = `manual-only`
3. **Document the SSO → app redirect path**:
   - Does it use an appId forward?
   - Does it use a redirect_uri callback?
   - Where is the token — in URL query / response body / cookie?
4. **Write loginFlow** → Write all fields to `task-meta.json`
5. **Sanitize** → Replace passwords in recording.json with `[REDACTED]`

**⚠️ If credentials.ts extract cannot extract credentials (e.g., Google multi-step login), prompt the user to save credentials manually:**
```bash
npx ts-node scripts/utils/credentials.ts save accounts.google.com user@gmail.com 'password'
```

#### Login Code Templates for Script Generation

Choose the auto-login implementation based on `loginFlow.type`:

**type=api (REST API login):**
```typescript
// API login → follow redirects → navigate to app
const resp = await page.evaluate(async (p) => {
  const r = await fetch(p.url, { method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify(p.body), credentials: 'include' });
  return { status: r.status, ok: r.ok };
}, { url: loginApiUrl, body: { authType, credential: { username, password } } });
```

**type=form:**
```typescript
await page.fill(loginFlow.usernameSelector || 'input[name="username"]', cred.username);
await page.fill(loginFlow.passwordSelector || 'input[type="password"]', cred.password);
await page.click(loginFlow.submitSelector || 'button[type="submit"]');
```

**type=multi-step:**
```typescript
for (const step of loginFlow.steps) {
  if (step.action === 'fill') {
    const value = step.field === 'username' ? cred.username : cred.password;
    await page.fill(step.selector, value);
  } else if (step.action === 'click') {
    await page.click(step.selector);
  } else if (step.action === 'wait') {
    await page.waitForSelector(step.selector, { timeout: step.timeoutMs || 10000 });
  }
}
```

**type=manual-only:**
```typescript
// Open headed browser, wait for user to complete login manually
const browser = await pw.chromium.launch({ headless: false });
// ... wait for successIndicator
```

**task-meta.json loginFlow example (SSO → enterprise app):**
```json
{
  "loginFlow": {
    "type": "api",
    "loginUrl": "https://sso.example.com",
    "loginDomain": "sso.example.com",
    "loginApiPath": "/api/sso/login",
    "authType": "passwordAuth",
    "appId": "1234567890",
    "appDomain": "app.example.com",
    "successIndicator": "url_contains:app.example.com"
  }
}
```

### ⚠️ Security Rules (MANDATORY)

1. **Passwords in recording.json must be sanitized immediately after analysis** (replace with `[REDACTED]`)
2. **credentials.enc is an encrypted binary file** — do not attempt to read or edit directly
3. **credentials.enc and sessions/ directory must never be committed to version control or shared**
4. **Skill packages (.skill) must not contain any credentials, sessions, or recording data**
5. **Generated task scripts (run.ts) must never hardcode any passwords**

---

## Known Issues & Lessons Learned

### 🔐 Login flow must match app — don't assume one-size-fits-all
- Current implemented scripts use `type=api` mode (enterprise SSO → business app)
- **Each new app recording must re-identify the login type** — do not reuse login logic from old scripts
- Google/Microsoft multi-step logins require `type=multi-step` + steps sequence
- Sites with CAPTCHA/2FA can only use `type=manual-only`
- Inlining login logic into run.ts (rather than importing external login.ts) is more stable due to Node ESM/CJS compatibility issues

### ⚠️ Node v25 ESM compatibility
- Node v25 defaults to ESM, `require()` is unavailable
- Solution: place `tsconfig.json` in the task directory to force `"module": "commonjs"`
- Dependencies like Playwright need full-path require: `require('/opt/.../node_modules/playwright')`
- Cross-directory .ts imports under ts-node are unstable — recommend inlining critical logic into run.ts

### ⚠️ Multi-tab traffic capture (fixed)
Some login flows or apps open new tabs. Recorder uses `context.on('request/response')` to capture ALL tabs.

### 📋 CSV must include ALL fields with human-readable labels
- Never crop fields — include everything from the API response
- System-generated field names (e.g. `field_*`, `attr_*`, `custom_*`) must be analyzed from sample data
- Create field-mapping.json for every task
- Field order: preserve original order from data, **never sort**
- Use proper CSV quoting to handle JSON fields with commas

### 📝 Submit tasks: always confirm field classification before generating
- Never skip the field confirmation step — wrong FIXED/DYNAMIC split breaks every future submission
- Fields that look fixed (e.g. a hardcoded project ID) might actually need to be dynamic in real use
- Always include `--dry-run` in generated scripts so users can verify the request body before committing
- RELATIONAL fields (e.g. approver ID looked up by name) should be auto-resolved in script, exposed as human-readable params

---

## File Locations

| Item | Path |
|------|------|
| Recorder | `scripts/record.ts` |
| Task runner | `scripts/run-task.ts` |
| Session utility | `scripts/utils/session.ts` |
| Login helper | `scripts/utils/login.ts` |
| Recordings | `~/.openclaw/rpa/recordings/<task>/` |
| Generated tasks | `~/.openclaw/rpa/tasks/<task>/` |
| Sessions | `~/.openclaw/rpa/sessions/<domain>.session.json` |
