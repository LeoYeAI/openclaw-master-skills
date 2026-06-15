# Web Autopilot 🤖

**Record once. Automate forever.**

Web Autopilot is an [OpenClaw](https://github.com/openclaw/openclaw) skill that turns any manual web application workflow into a reusable automation script — powered by AI.

## The Problem

Knowledge workers spend hours every week on repetitive web tasks inside enterprise applications:

- 📑 **Expense reports** — Fill the same form fields, attach receipts, submit for approval
- 📊 **Data extraction** — Navigate dashboards, export CSVs, copy-paste into spreadsheets
- ✈️ **Travel requests** — Enter dates, destinations, project codes, wait for approval flows
- 💰 **Payment submissions** — Match invoices to POs, fill amounts, route through workflows
- 📋 **Status updates** — Pull data from one system, summarize it in another

These tasks follow the same pattern every time, but they're trapped behind login walls, SSO portals, and complex multi-step UIs that resist traditional automation.

## The Solution

Web Autopilot takes a **record-and-replay** approach enhanced by AI:

1. **You do it once** in a real browser — login, click through the workflow, submit the form
2. **AI analyzes** the captured network traffic and classifies every field
3. **A reusable script** is generated with parameterized inputs
4. **Next time**, just run the script — or let your AI assistant handle it entirely

```
 You (once)                    AI (every time after)
┌──────────────┐              ┌──────────────────────┐
│ Open browser │              │ $ npx ts-node run.ts │
│ Login to SSO │   ──────►   │   --amount 2500      │
│ Fill forms   │   Record    │   --date 2026-03-15  │
│ Click submit │              │   --reason "Q1 trip" │
└──────────────┘              └──────────────────────┘
     15 min                         3 seconds
```

## Key Features

### 🔐 Universal Login Support
Works with any authentication method — SSO (OIDC, SAML, CAS), OAuth, username/password forms, multi-step login (Google, Microsoft, Okta), or manual login for sites with CAPTCHA/2FA. Sessions are persisted and auto-refreshed.

### 🧠 AI-Powered Field Analysis
Automatically classifies every API field into:
- **FIXED** — Same every time (approval flow IDs, company codes) → hardcoded
- **DYNAMIC** — Changes per run (amounts, dates, reasons) → CLI parameters
- **SESSION** — Auth tokens/cookies → managed automatically
- **RELATIONAL** — Needs a lookup first (project ID from name) → auto-resolved

### 📊 Two Task Types

**Query / Export** — Extract data from enterprise apps into structured formats (JSON, CSV). Great for building reports, dashboards, and cross-system summaries.

**Submit** — Automate form submissions with parameterized inputs. Includes `--dry-run` mode to preview the request before committing, and field confirmation to ensure nothing is misclassified.

### 🔄 Self-Healing Test Loop
Generated scripts go through up to 5 rounds of automated testing. When something breaks (expired session, changed field name, wrong URL), the AI diagnoses and fixes it automatically.

### 🔧 Register as a Tool
Once a task is tested and working, register it as an OpenClaw tool. Your AI assistant can then call it directly — "submit my expense report" becomes a single natural-language command.

## How It Works

```
🎬 Record         Operate the browser once (works after any login method)
🔍 Analyze        AI examines network traffic, classifies fields
✅ Confirm         Review field classifications (mandatory for submit tasks)
📝 Generate        Produce reusable TypeScript script + field mapping
🧪 Test            Iterative test loop with auto-fix (up to 5 rounds)
🔧 Register        Register as an OpenClaw tool for direct invocation
```

## Quick Start

### Prerequisites

- [OpenClaw](https://github.com/openclaw/openclaw) installed and configured
- Node.js v18+
- Playwright (`npx playwright install chromium`)

### 1. Record a Workflow

```bash
# Start from a login page
npx ts-node scripts/record.ts --name "expense-report" --sso-url "https://sso.company.com"

# Or start from the app directly (if no login needed)
npx ts-node scripts/record.ts --name "sales-report" --app-url "https://crm.company.com/reports"
```

A browser window opens. Perform the workflow as you normally would. Type `done` in the terminal when finished.

### 2. AI Analyzes & Generates

OpenClaw's AI reads the captured network traffic, identifies the core APIs, classifies fields, and generates a parameterized script.

For **submit** tasks, you'll be asked to confirm field classifications before script generation.

### 3. Run It

```bash
# Query task — just run it
npx ts-node ~/.openclaw/rpa/tasks/sales-report/run.ts --year 2026

# Submit task — preview first, then submit
npx ts-node ~/.openclaw/rpa/tasks/expense-report/run.ts --dry-run --amount 2500 --date 2026-03-15
npx ts-node ~/.openclaw/rpa/tasks/expense-report/run.ts --amount 2500 --date 2026-03-15 --reason "Client visit"
```

## Real-World Examples

| Task | Type | What It Automates |
|------|------|-------------------|
| Pull sales contracts | Query | Login to CRM → navigate to contracts → extract all records → output JSON/CSV |
| Submit travel request | Submit | Login to expense system → fill travel form → attach docs → submit for approval |
| Generate monthly report | Query | Login to BI dashboard → query metrics → export structured data |
| Process payment request | Submit | Read invoice PDF → fill payment form → match to PO → route for approval |
| Extract service projects | Query | Login to project management → filter by date → export project list |

## Architecture

```
~/.openclaw/rpa/
├── recordings/<task>/          # Raw browser recordings
│   ├── recording.json          # Network traffic + browser actions
│   └── summary.txt             # Human-readable overview
├── tasks/<task>/               # Generated automation scripts
│   ├── run.ts                  # Main executable script
│   ├── task-meta.json          # Task config (login flow, field mapping, usage)
│   └── field-mapping.json      # Field names → human-readable labels
├── sessions/<domain>.json      # Persisted login sessions (cookies/tokens)
└── credentials.enc             # Encrypted credentials (AES-256-GCM)
```

## Security

- **Credentials are encrypted** at rest (AES-256-GCM) — never stored in plaintext
- **Recordings are sanitized** — passwords redacted after analysis
- **Sessions and credentials are never committed** to version control
- **Generated scripts contain no hardcoded passwords**
- **File permissions** are restricted (0600 for sensitive files)

## Tech Stack

- **[Playwright](https://playwright.dev/)** — Browser automation and network interception
- **TypeScript** — Generated scripts are fully typed
- **OpenClaw** — AI orchestration, tool registration, and natural-language invocation

## License

MIT

---

Built for [OpenClaw](https://openclaw.ai) · [Documentation](https://docs.openclaw.ai) · [Community](https://discord.com/invite/clawd)
