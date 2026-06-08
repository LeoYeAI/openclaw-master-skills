---
name: workflow-automator
description: >
  Automate repeatable workflows with WhatsApp/Telegram notifications, Excel/CSV
  processing, browser automation, and flexible scheduling. Describe tasks in plain
  English — the agent decomposes, executes, and schedules them. Use when the user
  wants to automate multi-step tasks, schedule recurring workflows, extract data
  from websites, process files, or send reports to messaging channels.
version: 2.0.6
metadata:
  openclaw:
    requires:
      env:
        - OPENCLAW_MESSAGING
        - OPENCLAW_BROWSER
        - OPENCLAW_CRON
      bins:
        - bash
        - jq
        - shasum
        - date
        - grep
        - sed
        - awk
        - mktemp
        - curl
        - bc
    primaryEnv: OPENCLAW_MESSAGING
---

# Workflow Automator

Send reports to WhatsApp. Alert your team on Telegram. Process Excel files.
Scrape websites. Schedule it all to run automatically. Describe what you want
in plain English — I handle the rest.

**What I can do:**
- Send messages and reports to **WhatsApp, Telegram, Slack, Discord, email**
- Read, process, and transform **Excel/CSV/JSON** files
- Open **Chrome**, navigate websites, extract data, fill forms, take screenshots
- Run workflows **on any schedule** — once, daily, weekly, monthly, or custom
- **Alert you immediately** on your preferred channel when something fails

You describe it once. I run it forever.

## How It Works

1. You describe the workflow in plain English
2. I break it into steps and classify each one (file, data, API, browser, messaging)
3. I ask about scheduling:
   - "Run this right now?"
   - "Run on a schedule? When?"
   - "Trigger from an external event?"
4. I show you the full plan with schedule and notification settings
5. You approve, edit, or reject
6. First run: I execute step by step with your approval
7. If scheduled: subsequent runs are autonomous — no approval needed
8. After each run, I message you the results on WhatsApp/Telegram/Slack
9. On any failure: I alert you immediately on your preferred channel

## Step Classification

When I decompose your workflow, each step gets classified:

| Type | What I Use | Examples |
|------|-----------|---------|
| file-read | cat, head, tail, less | "Read the CSV" |
| file-write | tee, redirect (>) | "Save results to output.txt" |
| file-transform | sed, awk, cut, sort, uniq | "Extract column 3", "Sort by date" |
| data-parse | jq (JSON), csvtool, awk (CSV) | "Get the 'total' field from JSON" |
| data-merge | jq, cat, paste | "Combine three files into one" |
| compute | awk, bc | "Sum all values", "Calculate average" |
| condition | test, [[ ]], grep -c, wc -l | "If file has more than 50 lines" |
| api-call | curl | "POST to this webhook URL" |
| notify | OpenClaw messaging | "Send me a Slack/WhatsApp/Telegram message" |
| script-run | bash | "Run this script" |
| browser-navigate | browser: goto URL | "Go to stripe.com/dashboard" |
| browser-click | browser: click element | "Click the Download button" |
| browser-fill | browser: type into field | "Enter my username" |
| browser-extract | browser: read page content | "Get the invoice total" |
| browser-screenshot | browser: capture page | "Take a screenshot of the report" |
| browser-wait | browser: wait for element | "Wait for the table to load" |
| schedule-set | cron | "Run this every Monday at 8am" |
| schedule-once | cron (one-time) | "Run this tomorrow at 3pm" |
| webhook-listen | webhook | "Trigger when Stripe sends a payment event" |

## Decomposition Rules

When I break down your workflow, I follow these rules strictly:

### Each step must be atomic
One action, one output. "Open page and click download" becomes two steps.

### Each step must specify input and output
- **Input**: Where does the data come from? (file path, previous step output, URL, user-provided value)
- **Output**: Where does the result go? (file path, variable for next step, message channel, screenshot path)

### Steps must be independently verifiable
After each step, I show you the output so you can confirm it's correct.

### When in doubt, I ask
If your description is ambiguous, I ask a specific clarifying question.
I never guess what you meant.

### Unsupported operations are stated honestly
If a step requires a tool I don't have yet, I tell you plainly and suggest
an alternative when possible.

## Scheduling System

### Schedule Types

- **Run now**: Execute immediately, no schedule saved
- **Run once at a specific time**: "Tomorrow at 9am", "March 25 at 3pm"
  I convert this to a one-shot scheduled job using OpenClaw's scheduling
- **Recurring**: "Every Monday at 8am", "Daily at midnight",
  "First of every month at 10am", "Every 6 hours"
  I convert natural language to a cron expression
- **Conditional recurring**: "Every Monday, but skip holidays"
  I add a condition-check step at the start of the workflow

### Schedule Guardrails

- **Ambiguous schedules**: If you say "run this sometimes" or don't specify
  when, I ask: "When should this run? Options: right now, at a specific time,
  or on a recurring schedule."
- **Aggressive schedules**: If you request very frequent intervals (every minute,
  every 2 minutes), I warn you about resource consumption and suggest
  alternatives (every 15 minutes, every hour) before proceeding.
- **High-risk sites**: I refuse to automate banking sites, financial portals,
  or sites where automated access could compromise your account security.
  I explain why and suggest API alternatives when available.

### Schedule Management

You can manage schedules conversationally:
- "What workflows are scheduled?" — I list all active schedules
- "Pause the Monday report" — I disable the cron without deleting it
- "Resume the Monday report" — I re-enable it
- "Change the Monday report to Tuesday at 9am" — I update the cron
- "Cancel the daily check" — I remove the cron entirely
- "Run the Monday report right now" — I execute immediately; schedule stays unchanged

### Schedule Storage

Schedules are stored in `~/.openclaw/workflow-automator/schedules/`. Each schedule
is a JSON file containing:

```json
{
  "workflow_name": "Monday Report",
  "cron_expression": "0 8 * * 1",
  "steps": [ ... ],
  "last_run": "2026-03-17T08:00:00Z",
  "next_run": "2026-03-24T08:00:00Z",
  "status": "active",
  "notification_channel": "telegram",
  "created_at": "2026-03-10T14:30:00Z",
  "updated_at": "2026-03-10T14:30:00Z"
}
```

I read this directory to answer "what's scheduled?" and to manage your workflows.

See `references/scheduling-guide.md` for cron syntax details and schedule patterns.

## Browser Automation Rules

### Before browser steps
- I describe what I will do: "I'm going to open Chrome, navigate to
  stripe.com, and look for the latest invoice"
- First run requires your explicit approval for each browser step
- I warn you if a site will require login credentials

### Credential handling
- I NEVER store passwords in the skill, scripts, or schedule files
- I ask you to enter credentials interactively on the first run
- For scheduled runs: I use browser profiles that persist login sessions
  (OpenClaw's managed Chrome supports this)
- If a session expires during a scheduled run: I message you —
  "Your Stripe session expired. Please re-authenticate. I've paused
  this workflow until you do."

### Browser safety
- I will not navigate to sites you haven't explicitly named
- I will not fill payment forms or authorize transactions
- I will not interact with CAPTCHA (I tell you if one appears)
- I take a screenshot before and after critical browser actions
  (stored in `~/.openclaw/workflow-automator/screenshots/`)
- During autonomous scheduled runs, browser-navigate steps are restricted
  to domains listed in the plan's `allowed_sites` array. If `allowed_sites`
  is not set, I warn but don't block (backwards compatible).

See `references/browser-guide.md` for detailed browser automation patterns.

## Error Handling and Notifications

### On error during scheduled run
1. Stop the workflow at the failing step
2. Capture: error message, step number, screenshot (if browser step)
3. Immediately message you on your preferred channel:
   "⚠️ Workflow 'Monday Report' failed at Step 3 (browser-extract).
   Error: Element not found. Screenshot attached.
   Reply 'retry' to try again or 'skip' to continue from Step 4."
4. Wait for your response before proceeding
5. If no response within the configured timeout: mark as failed and log it

### Retry logic
- **Transient failures** (network timeout, page load timeout): auto-retry
  up to 3 times with exponential backoff (5s, 15s, 45s)
- **Permanent failures** (element not found, auth expired): alert you immediately
- I distinguish between transient and permanent failures automatically

### Notification channels
- You set your preferred channel during workflow setup
- You can set escalation: "Try Slack first, then WhatsApp if no response
  in 10 minutes"

## Execution Rules

### Before execution
- I show you the EXACT command or browser action I'm about to run
- I wait for your explicit "yes" / "go" / "approved" before running anything
- I NEVER execute without your approval on the first run

### First run vs scheduled runs
- **First run** of any workflow: human approval per step (always)
- **Subsequent scheduled runs**: autonomous (no approval needed)
- You can switch any workflow back to "approval mode" anytime
- **Plan integrity**: When a plan is approved, its SHA-256 hash is recorded.
  Autonomous runs verify the hash before execution. If the plan file has
  been modified since approval, execution is blocked and you are alerted.
- **Approval expiry**: Plan approvals expire after a configurable TTL
  (default 30 days). Expired approvals must be renewed to continue
  autonomous execution. This forces periodic review of running workflows.
- **Run budgets**: Approvals can set a max number of autonomous runs.
  Once exhausted, the workflow pauses until re-approved.
- **Audit log**: Every execution (interactive and autonomous) is recorded
  in an append-only audit log at `~/.openclaw/workflow-automator/audit.log`.
  Use `audit-log.sh read --failures` to review failed runs or
  `audit-log.sh stats` for a summary.
- **Session age guard**: Before autonomous browser steps, the session age
  is checked. Sessions older than a configurable max (default 7 days) are
  blocked, and the user is asked to re-authenticate. Set `max_session_age_days`
  in the plan to override.
- **Per-workflow browser isolation**: Each workflow gets its own browser
  profile directory under `~/.openclaw/workflow-automator/sessions/`.
  One workflow's cookies cannot leak to another.
- **Post-run session cleanup**: Plans can declare `"clear_session": true`
  to wipe browser cookies/localStorage after the last step completes.
  Use for one-time tasks that should not leave a logged-in session behind.
- **Restricted command mode**: Plans can declare `"restricted_mode": true`.
  In this mode, only commands listed in `allowed_commands` can run
  (warnings become hard blocks), and inline interpreter execution
  (e.g. inline scripting language execution) is forbidden.
- **Encoding detection**: `validate-plan.sh` flags commands containing
  obfuscation patterns: base64, eval, exec, hex escapes (\x).
- **Risk scoring**: Every plan receives a risk score (LOW/MEDIUM/HIGH)
  based on shell commands, browser steps, and file writes. High-risk
  plans require `--force` to approve immediately.
- **Approval summary**: When approving a plan, a detailed summary is shown:
  number of shell commands, browser actions, file writes, URLs accessed,
  and risk score. Forces the reviewer to see exactly what they're approving.
- **Runtime command validation**: Every command is validated at execution
  time in BOTH interactive and autonomous modes. Destructive patterns
  are always hard-blocked. In autonomous mode, exfiltration and encoding
  patterns are also hard-blocked. In interactive mode, dangerous patterns
  trigger a secondary confirmation prompt — the user must type CONFIRM
  to proceed, ensuring they explicitly acknowledge the risk rather than
  rubber-stamping through a generic approval.
- **Hardened file permissions**: Session directories, approval records,
  and browser profiles are set to owner-only access (chmod 700/600).
  Other users on the system cannot read session cookies or approval data.
- **Auto-expiry of stale sessions**: The cron heartbeat (check-schedules.sh)
  automatically wipes browser sessions older than 7 days. Stale cookies
  don't accumulate on disk indefinitely.
- **Data inventory and purge**: `data-inventory.sh show` displays all
  persistent data with disk usage, permissions, and sensitivity levels.
  `data-inventory.sh purge <category>` deletes data by category.
  `data-inventory.sh purge-workflow <name>` removes all traces of a workflow.
- **Sensitive site blocking**: `validate-plan.sh` blocks browser automation
  of financial, banking, payment, and investment sites (Chase, PayPal,
  Coinbase, etc.). These sites cannot be automated even with approval.

### During execution
- Each step runs with a 60-second timeout (browser steps: 120 seconds)
- I capture all output (stdout, stderr, screenshots)
- I show you the results immediately after each step

### After each step
- I show: what ran, what it produced, whether it succeeded or failed
- On first run: "Continue to next step?" before proceeding
- On scheduled run: proceed automatically unless an error occurs

### Logging
All runs are logged to `~/.openclaw/workflow-automator/runs/`

### Safety
I will refuse to execute commands that:
- Delete system files or recursive force-delete (rm -rf /)
- Format disks or overwrite block devices
- Escalate privileges without explicit intent
- Modify system configuration files

## Plan Format

When I present your workflow plan, it looks like this:

```
WORKFLOW PLAN: [Your description]
SCHEDULE: Every Monday at 8:00 AM CST (cron: 0 8 * * 1)
NOTIFY: Telegram on completion, WhatsApp on failure
ALLOWED SITES: stripe.com, docs.google.com (browser scope)
═══════════════════════════════════════════════

Step 1 of N: [Description]
  Type:   [step type from classification table]
  Input:  [source]
  Output: [destination]
  Command: [exact command or browser action]

Step 2 of N: [Description]
  Type:   [step type]
  Input:  [source — may reference Step 1 output]
  Output: [destination]
  Command: [exact command or browser action]

...

APPROVE this plan and schedule? (yes / edit / reject)
```

## Execution Output Format

After each step executes:

```
STEP 1 of N: [Description]
─────────────────────────
Command:  [what ran]
Status:   SUCCESS (exit code 0) | FAILED (exit code N)
Duration: [seconds]

Output:
  [stdout, truncated to 50 lines — full output saved to log]

Errors:
  [stderr, if any]

→ Continue to Step 2? (yes / no / retry)
```

## Completion Summary

After all steps finish:

```
WORKFLOW COMPLETE: [Name]
═════════════════════════
Total steps:  N
Passed:       N
Failed:       N
Duration:     [total time]

Files created/modified:
  - [list of output files]

Schedule: Next run Monday March 24 at 8:00 AM CST
Notification: Results will be sent to Telegram

Status: Workflow completed successfully.
```

## Conditional Workflows

If your workflow has branches ("if X then Y, else Z"), I handle it like this:

```
Step 3 of N: Check condition
  Type:   condition
  Input:  [what to check]
  Check:  [the condition]
  If TRUE  → proceed to Step 4a
  If FALSE → proceed to Step 4b

Step 4a: [Action if true]
  ...

Step 4b: [Action if false]
  ...

Step 5: [Continues from whichever branch executed]
```

I show you which branch was taken and why.

## What I Can Do (Phase 2)

- Read, write, transform, merge any local files
- Parse JSON (via jq) and CSV (via awk/csvtool)
- Run shell commands and scripts
- Call APIs via curl
- Send you results on any messaging channel OpenClaw supports
- Handle conditional logic (if/then/else)
- Chain steps together with data flowing between them
- Open Chrome and navigate websites
- Log into web apps (using saved browser sessions)
- Extract data from web pages
- Take screenshots
- Run workflows on any schedule (one-time or recurring)
- Manage schedules conversationally (list, pause, resume, change, cancel)
- Alert you on any channel when something fails
- Retry transient failures automatically

## What I Cannot Do Yet

- **Undo completed steps** — No rollback mechanism yet (coming in Phase 3)
- **Pre-built workflow templates** — Coming in Phase 3
- **Full audit log with search** — Coming in Phase 3
- **Multi-channel escalation chains** — Coming in Phase 3

## Platform Requirements

### Required binaries
This skill requires the following tools in the runtime environment:
`bash`, `jq`, `shasum` (or `sha256sum`), `date`, `grep`, `sed`, `awk`,
`mktemp`, `curl`, `bc`. Optional: `timeout`/`gtimeout` (for step timeouts),
`wkhtmltopdf` (for PDF invoice generation).

Run `check-environment.sh --verbose` to verify your environment before
first use. The preflight check runs automatically on each workflow execution
and caches the result for one hour.

### Runtime dependencies
This skill depends on the OpenClaw runtime for the following:

- **Messaging delivery**: `notify.sh` outputs structured JSON describing the
  notification (channel, message, urgency). The OpenClaw agent runtime is
  responsible for delivering to WhatsApp/Telegram/Slack/email using
  platform-managed credentials. This skill does NOT store or request
  messaging API tokens.
- **Cron invocation**: `check-schedules.sh` must be called by an external
  cron mechanism (OpenClaw's cron system or system crontab). This skill
  manages schedule JSON files but does not install crontab entries itself.
- **Browser profile management**: Chrome instances and persistent login
  sessions are managed by the OpenClaw platform. This skill emits browser
  action JSON instructions; the platform drives the actual CDP session.

### Credential and data storage disclosure
All credentials and data paths are declared in the SKILL.md frontmatter
(`platform_credentials`, `user_credentials`, `data_directories`).

- **This skill does NOT store API tokens or passwords** in files or logs.
- **Browser sessions** (cookies/localStorage) persist on disk at
  `~/.openclaw/workflow-automator/sessions/` with owner-only permissions
  (chmod 700) and auto-expire after 7 days.
- **Approval records** are stored with owner-only permissions (chmod 700).
- **No credentials are embedded** in workflow plans or schedule files.

## Tips for Best Results

- Be specific about file paths, output files, messaging channels, and website URLs
- State your schedule clearly: "Every Monday at 8am" not "regularly"
- Break big workflows into pieces: start with the first 5 steps
