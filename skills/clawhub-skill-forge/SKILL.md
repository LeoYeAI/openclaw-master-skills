---
name: clawhub-skill-creator
description: "Create ClawhHub-ready OpenClaw skills with correct structure, scanner criteria, security rules & publish checklist. No credentials or binaries required."
metadata: {"openclaw":{"emoji":"🛠️"}}
---

# clawhub-skill-creator

Scaffold and publish ClawhHub-ready OpenClaw skills. Follow every rule below. Do not skip sections. Do not invent conventions not listed here.

Ask the user for the **skill name** and **purpose** if not already provided, then generate the files.

---

## Structure

Generate two files only — no README.md, no CHANGELOG.md, no auxiliary docs:

```
[skill-name]/
├── SKILL.md       (required)
└── _meta.json     (required)
```

---

## Understanding the ClawhHub Scanner

The scanner is the gatekeeper between publishing and availability. Know how it works before writing a single line:

**1. The description summary is the ONLY thing the scanner trusts at the registry level.**
`_meta.json` fields (`requiredConfigPaths`, `primaryCredential`, `requires`) are stored but NOT surfaced in the registry API. The scanner cannot read them. Everything the scanner needs to verify must be in the description — and in the FIRST ~160 characters, because that is where the registry truncates the summary.

**2. The scanner is iterative — it reveals one layer at a time.**
Each fix exposes the next issue. It will not give you all problems at once. Expect multiple publish cycles. This is by design — it is a progressive trust gate.

**3. The scanner cannot verify nested content.**
A worker script embedded inside a here-string inside a code block will be marked as truncated and unverifiable. All content the scanner needs to read must be flat and standalone.

**4. The scanner is semantic, not keyword-based.**
It understands the difference between what is logged vs transmitted, always:true vs always:false, handle vs userId, and required vs optional credentials. It catches logical inconsistencies, not just missing keywords.

**5. The scanner is conservative by default.**
It blocks and warns rather than approves. Every publish triggers a new scan. Do not publish until the checklist passes — each rejected version counts against the skill's history.

---

## Known OpenClaw Parser Gotchas (learned from real failures)

These will silently break skill detection — no error, skill just disappears from `openclaw skills list`:

- **Missing closing `---` in frontmatter**: If the frontmatter block is not closed with `---`, OpenClaw silently fails to parse the skill entirely. Always verify the closing delimiter exists.

- **`openclaw` in `metadata.openclaw.requires.bins`**: OpenClaw does not recognize itself as a bin to check and silently hides the skill. Never put `openclaw` in bins. Use `anyBins: ["powershell","pwsh"]` for OS gating — the openclaw runtime is implied.

- **Skills in `~/.openclaw/skills/` not auto-detected**: OpenClaw scans `<workspace>/skills/` by default. For skills in `~/.openclaw/skills/`, add `skills.load.extraDirs: ["~/.openclaw/skills"]` to `openclaw.json`. Also add `skills.entries.<name>.enabled: true` for each skill.

- **`clawhub install` path**: By default installs into `./skills` (cwd) or `<workspace>/skills`. Always pass `--workdir` explicitly or install directly to `~/.openclaw/skills/` and add extraDirs.

- **Encoding**: Always write SKILL.md with `[System.Text.UTF8Encoding]::new($false)` (no BOM). BOM or encoding artifacts in frontmatter break the YAML parser silently.

---

## ClawhHub Scanner Criteria

Address all five explicitly — in the description first, then in the body.

### 1. Purpose & Capability
- State exactly what APIs/services are called (e.g. "graph.facebook.com only")
- State what the skill does NOT do ("no data forwarded to third parties")
- If background process: state exactly what is READ, what is TRANSMITTED, what is LOGGED
- If long-lived tokens: state rotation guidance + immediate rotation if host is compromised
- If setup-only secrets (e.g. APP_SECRET): state "delete afterward" explicitly

### 2. Instruction Scope
- Required binaries and credentials at the START of the description (fits in ~160-char summary)
- Required CLIs declared in BOTH places:
  - `metadata.openclaw.requires.anyBins` in SKILL.md frontmatter (OpenClaw load-time gating)
  - `_meta.json requires.anyBinaries` (registry metadata)
- SKILL.md body and _meta.json must match — no features in one but not the other
- OS restriction in description if PowerShell-specific
- Least-privilege note: state "grant token minimal permissions only"

### 3. Install Mechanism
- No external script downloads at runtime — all worker code inline in SKILL.md
- Worker scripts extracted from SKILL.md at runtime, not constructed from string literals

### 4. Credentials
- All credential requirements named in the description (file path + field names)
- Distinguish required vs optional fields (e.g. APP_SECRET: setup only, delete afterward)
- No token literals in any script — credentials always read fresh from disk at runtime
- All runtime files permission-restricted (icacls/chmod 600): config, worker, log, pid, state
- Worker stored in ~/.config/[skill]/worker.ps1 — never in system temp
- Logs contain metadata only — no secrets, no message content
- Long-lived tokens: include rotation guidance and immediate-rotation-if-compromised note

### 5. Persistence & Privilege
- `always:true` is forbidden in community skills — high blast radius, scanner flags it
- Background processes opt-in only — never autonomous
- Declare in _meta.json persistence: type, code, optional:true, description
- Description must state: what is read, transmitted, logged, and to where
- Worker content must be fully readable by scanner — own dedicated section, plain code block
- Pid file cleaned up on stop

---

## File Specifications

### SKILL.md Frontmatter

```yaml
---
name: [skill-name]
description: "[What it does in plain English — action-focused, no 'AI' prefix]. Requires: [binaries]. Reads [credentials file] ([FIELDS]). [Setup-only secrets: delete afterward.] [Long-lived tokens: rotate periodically; rotate immediately if host compromised.] Grant token minimal permissions only. No data forwarded to third parties; all calls go to [domain] only."
metadata: {"openclaw":{"emoji":"[icon]","requires":{"anyBins":["powershell","pwsh"]}}}
---
```

Rules:
- Description is a QUOTED single-line string
- **Lead with a value hook** — describe what the skill does in plain, action-focused language (e.g. "Facebook Page manager: post, schedule, reply & get insights"). This is what users searching ClawhHub will read first. Do NOT start with "AI". Do NOT start with "Requires:".
- **Technical requirements follow the hook** — after the value hook, include: `Requires: [binaries]. Reads [credentials file] ([FIELDS]).`
- Keep the combined hook + requirements within ~160 characters so both appear in the registry summary
- NEVER put `openclaw` in `bins` or `anyBins` — it silently hides the skill
- Do NOT use `always:true` — scanner flags it as high blast radius
- Do NOT add any other frontmatter fields (no runtime, clawdbot, credentials blocks)
- Frontmatter MUST end with a closing `---` line — verify it exists before publishing

**Good description example:**
```
"Facebook Page manager: post, schedule, reply & get insights. Requires: powershell/pwsh. Reads ~/.config/fb-page/credentials.json (FB_PAGE_TOKEN, FB_PAGE_ID). FB_APP_SECRET for one-time setup only — delete afterward. Long-lived token; rotate periodically and immediately if host is compromised. Grant minimal permissions only. No data forwarded to third parties; all calls go to graph.facebook.com only."
```

**Bad description example (do not do this):**
```
"Requires: powershell/pwsh. Reads ~/.config/fb-page/credentials.json (FB_PAGE_TOKEN, FB_PAGE_ID). Interact with any Facebook Page feature via the Meta Graph API..."
```
The bad example leads with dry technical info — users scanning ClawhHub skip it.

### _meta.json

> CRITICAL: ownerId must be your ClawhHub internal userId — NOT your handle.
> Get it: `clawhub inspect <one-of-your-skills> --json`
> Look for `owner.userId` (e.g. "kn7824yf4srh3akes6axhmqf5n81q7dh") — NOT "seph1709"
> Using the handle causes registry owner verification mismatch — scanner flags it.

```json
{
  "ownerId": "[registry-userId-not-handle]",
  "slug": "[skill-name]",
  "version": "1.0.0",
  "publishedAt": "YYYY-MM-DDTHH:MM:SSZ",
  "requiredEnvVars": [],
  "requiredConfigPaths": ["~/.config/[skill]/credentials.json"],
  "primaryCredential": {
    "type": "file",
    "path": "~/.config/[skill]/credentials.json",
    "fields": ["FIELD_ONE", "FIELD_TWO"],
    "required": ["FIELD_ONE"],
    "optional": ["FIELD_TWO"],
    "sensitive": true,
    "notes": "Which fields are required vs optional. Credentials read fresh from disk at runtime — never embedded as literals. Setup-only fields (e.g. APP_SECRET): delete after one-time exchange. Rotation guidance for long-lived tokens."
  },
  "persistence": {
    "type": "background-process",
    "code": "inline",
    "optional": true,
    "description": "What is READ, TRANSMITTED (to where, via what), and LOGGED. Worker stored in ~/.config/[skill]/worker.ps1 with restricted permissions. Listener never starts autonomously."
  },
  "credentialSetup": {
    "type": "manual",
    "description": "One-time setup instructions summary."
  },
  "requires": {
    "anyBinaries": ["powershell", "pwsh"],
    "os": ["windows", "macos", "linux"]
  }
}
```

Remove `persistence` if no background process.
Remove `primaryCredential` / `requiredConfigPaths` if no secrets.
Do NOT include `openclaw` in `requires.binaries` — it silently gates the skill against itself.

---

## SKILL.md Content Structure

Follow this exact order:

### STEP 1 — Load Credentials

```powershell
$cfg = Get-Content "$HOME/.config/[skill]/credentials.json" -Raw | ConvertFrom-Json
```

If missing, show full setup flow:
1. Detect available resources (e.g. `openclaw channels list`)
2. Ask user to choose and provide required values
3. Save config file
4. Immediately restrict permissions on ALL files in config dir:

```powershell
$dir = "$HOME/.config/[skill-name]"
if ($env:OS -eq "Windows_NT") {
    "credentials.json","worker.ps1","listener.log","listener.pid","listener-state.json" | ForEach-Object {
        $f = "$dir/$_"
        if (Test-Path $f) { icacls $f /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null }
    }
} else {
    Get-ChildItem $dir | ForEach-Object { & chmod 600 $_.FullName }
}
```

Include note: never commit any file in ~/.config/[skill]/ to version control.

For setup-only secrets (e.g. APP_SECRET): include explicit instruction to delete the field from credentials.json after the one-time token exchange is complete.

### STEP 2 — Core Functionality

- Table of supported actions (method, endpoint, params)
- Reusable call patterns per request type
- All code inline — no external script downloads
- Wrap all API calls in try/catch

### STEP 3 — Error Handling

- try/catch on every API call
- Error code table with exact fixes
- Tell user exactly what to do for each error

### WORKER SCRIPT (if background process)

This section is MANDATORY if the skill has a background process.
The worker script MUST be in its own dedicated section as a plain readable code block.
Do NOT embed it in a here-string inside another code block — the scanner marks nested content as truncated and unverifiable.

Start the section with explicit disclosure:
```
External contacts: [list every domain — no others]
Outbound data: [exactly what is sent, to where, via what method]
Logs: [exactly what is written — metadata only, no message content, no tokens]
No other endpoints. No token literals.
```

Then the full worker as a plain code block with line-by-line comments on every sensitive operation.

The Start procedure must write the worker by extracting it from SKILL.md — not constructing it from string literals:

```powershell
$workerContent = Get-Content "$HOME/.openclaw/skills/[skill]/SKILL.md" -Raw
$workerContent = ($workerContent -split "## WORKER SCRIPT")[1]
$workerContent = [regex]::Match($workerContent, '(?s)```powershell\r?\n(.*?)```').Groups[1].Value
Set-Content "$HOME/.config/[skill]/worker.ps1" -Value $workerContent -Encoding UTF8
```

### BACKGROUND LISTENER section header template:

```
> OPTIONAL - never start without explicit user request.
>
> WHAT IS READ: [credential fields] from [file path].
> WHAT IS TRANSMITTED: [exact fields] via openclaw message send to NOTIFY_CHANNEL/NOTIFY_TARGET.
>   [Field X] goes to channel destination only — never written to disk.
> WHAT IS LOGGED: [fields only] — no [sensitive content], no tokens.
> WORKER SCRIPT: exact content shown in WORKER SCRIPT section above.
> AUTONOMOUS START: never. Only starts when the user explicitly requests it.
```

### AGENT RULES

Always include these:
- Load credentials first; if missing, guide setup
- Never embed tokens as literals — read from disk at runtime
- Restrict permissions on all runtime files immediately after creation
- Logs must not contain secrets or message content — metadata only
- Background processes opt-in only — never start without explicit user request
- Worker content is fixed as shown in WORKER SCRIPT section — do not modify at runtime
- Before starting listener: confirm destination is trusted with user
- Inform user exactly what will be forwarded (full content, not just metadata)
- On any error: parse error code, map to table, tell user exactly what to do
- OS detection: env:OS eq Windows_NT -> powershell; otherwise -> pwsh
- No hardcoded IDs, tokens, or targets — all from config files
- For setup-only secrets (e.g. APP_SECRET): remind user to delete from credentials.json after setup
- For long-lived tokens: remind user to rotate periodically and immediately if host is compromised

---

## After Publishing

```powershell
# Set GitHub repo About description and homepage URL (run after every push)
gh repo edit seph1709/[skill-name] `
  --description "OpenClaw skill: [one-line purpose]" `
  --homepage "https://clawhub.ai/seph1709/[skill-name]"
```

This resolves the "no homepage / opaque owner" scanner flag — the GitHub repo is the audit trail, and the ClawhHub URL links back to the published registry record.

Note: `clawhub edit --homepage` does not exist as a CLI command. GitHub repo About is the only place to surface a homepage URL for the skill.

---

## Security Rules (non-negotiable)

- NEVER hardcode user IDs, channel IDs, tokens, or personal identifiers
- All secrets in user-owned config files — never in scripts
- Worker reads credentials fresh from disk at runtime
- Worker stored in ~/.config/[skill]/worker.ps1 — never in system temp
- icacls/chmod 600 on ALL runtime files immediately after creation
- Logs: metadata only — no secrets, no message content, no full bodies
- Long-lived tokens: rotation guidance required; immediate rotation if host compromised
- Setup-only secrets (e.g. APP_SECRET): include instructions to delete after use
- Background processes opt-in and declared in _meta.json persistence
- always:true forbidden — use metadata.openclaw.requires or openclaw.json entries instead
- ownerId must be registry userId, not handle
- Least privilege: explicitly state "grant token minimal permissions only" in description

---

## Validation Checklist (before publishing to ClawhHub)

### DESCRIPTION / SUMMARY (scanner reads only ~160 chars — hook + requirements must fit)
- [ ] Starts with a plain-English value hook (what it does, action-focused, no "AI" prefix)
- [ ] Hook is followed by: "Requires: [binaries]. Reads [credentials file] ([fields])."
- [ ] Hook + requirements combined fit within ~160 chars (registry summary truncation point)
- [ ] Required binaries in first ~160 chars
- [ ] Credentials file path and field names in first ~160 chars
- [ ] APIs/services called named explicitly (e.g. "graph.facebook.com only")
- [ ] "No data forwarded to third parties; all calls go to [domain] only" stated
- [ ] Background: TRANSMITTED / LOGGED breakdown in description
- [ ] Setup-only secrets: "delete afterward" stated
- [ ] Long-lived tokens: rotation + immediate-rotation-if-compromised stated
- [ ] Least privilege: "grant token minimal permissions only" stated

### FRONTMATTER (parser gotchas — all silent failures)
- [ ] Closing `---` exists after the metadata line
- [ ] name and description only (plus metadata line) — no other frontmatter fields
- [ ] metadata.openclaw.requires uses `anyBins` — NOT `bins: ["openclaw"]`
- [ ] No `openclaw` anywhere in bins or anyBins
- [ ] No always:true
- [ ] File written with UTF-8 no-BOM encoding

### _meta.json
- [ ] ownerId is registry userId (not handle) — verify via `clawhub inspect --json`
- [ ] requiredConfigPaths lists all credential files
- [ ] primaryCredential.fields lists all fields; required/optional split
- [ ] Notes: read-fresh-from-disk, delete-after-use fields, rotation guidance
- [ ] persistence block present if background process (with full read/transmit/log description)
- [ ] requires.anyBinaries declared (NOT binaries: ["openclaw"])
- [ ] No install field unless real install step exists

### WORKER SCRIPT (if background process)
- [ ] Worker in own dedicated ## WORKER SCRIPT section — NOT nested in here-string
- [ ] Section starts with explicit: external contacts, outbound data, logs disclosure
- [ ] Every sensitive line has a comment
- [ ] Start procedure extracts worker from SKILL.md — not constructed from string literals
- [ ] No token literals anywhere in worker
- [ ] Logs write metadata only (verified line by line in worker)

### CREDENTIALS
- [ ] No token literals in any script
- [ ] Worker reads from disk at runtime
- [ ] icacls/chmod 600 on all files: config, worker, log, pid, state
- [ ] Setup-only secrets have delete-after-use instructions
- [ ] Rotation guidance for long-lived tokens
- [ ] Never commit config dir to version control

### PERSISTENCE & PRIVILEGE
- [ ] Listener opt-in — requires explicit user request
- [ ] Agent Rules: confirm destination trusted before starting
- [ ] Agent Rules: inform user of full content being forwarded
- [ ] Agent Rules: worker content fixed — do not modify at runtime
- [ ] Pid file cleaned up on stop

### GENERAL
- [ ] No README.md or auxiliary docs
- [ ] No hardcoded personal IDs, tokens, channel names
- [ ] No .git folder in skill dir before uploading
- [ ] SKILL.md and _meta.json are consistent — no features in one missing from the other

### POST-PUBLISH
- [ ] GitHub repo About description set (`gh repo edit --description "..."`)
- [ ] GitHub repo homepage set to ClawhHub URL (`gh repo edit --homepage "https://clawhub.ai/..."`)
- [ ] `openclaw skills list` confirms skill is ✓ ready (not missing, not absent)
- [ ] `clawhub inspect [slug]` summary starts with value hook and shows credentials path
