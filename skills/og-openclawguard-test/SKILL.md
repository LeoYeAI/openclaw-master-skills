---
name: openguardrails
description: "Runtime security plugin for AI agents. Provides local-first protection against data exfiltration, credential theft, command injection, and sensitive data leakage. Includes a free AI Security Gateway that sanitizes PII before it reaches LLM providers. Fully open source (Apache 2.0) — all detection and sanitization logic is auditable on GitHub. Source: github.com/openguardrails/openguardrails"
metadata: {"openclaw":{"emoji":"🛡️","homepage":"https://github.com/openguardrails/openguardrails","keywords":["security","prompt-injection","data-exfiltration","pii","credential-theft","command-injection","guardrails","safety","agent-security"]}}
---

# OpenGuardrails

> **What this skill is:** This is the installation and usage guide for the OpenGuardrails security plugin. The plugin code itself lives in the open-source repository at [github.com/openguardrails/openguardrails](https://github.com/openguardrails/openguardrails) (subdirectory `openclaw-security/`). This skill does not execute code on its own — it documents how to install, configure, and verify the plugin.
>
> **ClawHub ↔ GitHub identity:** This skill is published on ClawHub as [`ThomasLWang/openguardrails`](https://clawhub.ai/ThomasLWang/openguardrails). The upstream source is at [`github.com/openguardrails/openguardrails`](https://github.com/openguardrails/openguardrails), maintained by the same author (Thomas Wang). The npm package is [`@openguardrails/openclaw-security`](https://www.npmjs.com/package/@openguardrails/openclaw-security). All three point to the same codebase.

Runtime security guard for OpenClaw agents. Protects against the most critical AI agent threats:

- **Data exfiltration defense** — detects and blocks when an agent reads sensitive files then attempts to send them to external servers
- **Sensitive data leakage prevention** — sanitizes PII, credentials, and secrets before they reach LLM providers
- **Prompt injection protection** — identifies crafted inputs designed to hijack agent behavior
- **Command injection blocking** — catches shell escapes, backtick substitution, and command chaining in tool parameters
- **Content safety** — filters NSFW content and enforces minor protection policies

## Security & Trust

**Open source and auditable.** All code is Apache 2.0 licensed at [github.com/openguardrails/openguardrails](https://github.com/openguardrails/openguardrails). You can audit every line before installing — especially the tool-event hooks, sanitization logic, and network calls. Key files to review:

- `agent/sanitizer.ts` — what gets sanitized before any cloud transmission
- `agent/content-injection-scanner.ts` — local-only regex patterns for injection detection
- `gateway/src/sanitizer.ts` — AI Security Gateway sanitization (fully local)
- `index.ts` — plugin entry point showing all event hooks

**What is transmitted to the cloud API (and what is not):**

- **Sent:** sanitized tool metadata only — tool names, parameter keys, session signals (tool ordering, timing). All sensitive values (PII, credentials, file contents, secrets) are replaced with category placeholders (`<EMAIL>`, `<SECRET>`, `<CREDIT_CARD>`, etc.) locally before transmission.
- **Never sent:** raw file contents, user messages, conversation history, actual credential values, or any unsanitized parameter values.
- **Data retention:** Detection request payloads (sanitized tool metadata) are not retained after the response is returned. Account data is stored persistently for billing: agent ID and API key (created at registration in Step 2), plus email (provided by you in Step 3 via the claim web form), plan tier, and per-agent usage counts.

**Local-only mode.** The plugin works without any cloud connection. Local fast-path detection (shell escape blocking, read-then-exfil patterns, content injection redaction) operates entirely on your machine with no network calls. Cloud assessment is only used for borderline behavioral patterns and is opt-in via registration. If you skip registration, you still get all local protections.

**No install-time network calls.** The plugin makes zero network requests at install time. It loads a local `BehaviorDetector` and waits until you explicitly run `/og_activate`.

**Registration sends minimal data.** The `/og_activate` command sends exactly `{ name, description }` to register — no email, no machine identifiers, no file paths, no user data. Your email is only collected later in Step 3, when you voluntarily visit the claim URL in your browser and enter it yourself. See the "Step 2: Register" section for the full request/response specification.

**Fail-open design.** If the cloud API is unreachable or times out, tool calls are allowed — the plugin never blocks your workflow due to network issues.

**This skill is documentation-only.** This SKILL.md file contains no executable code. It is an installation and usage guide for the open-source plugin at [github.com/openguardrails/openguardrails](https://github.com/openguardrails/openguardrails). You are encouraged to audit the source before installing.

---

## How It Works

The plugin hooks into `before_tool_call`, `after_tool_call`, and `tool_result_persist` events. It classifies every tool call in real time — tracking sensitive file reads, external network calls, credential access, and shell commands across the session. Critical patterns are blocked instantly on the local fast path; borderline signals are assessed via the cloud API.

Additionally, when the agent reads files or fetches web pages, the plugin scans the content for injection patterns across 7 categories and **automatically redacts** them in-place before the agent processes the content.

```
Agent calls tool
      ↓
[openguardrails] classifies tool + updates session state
  • sensitive file read → then network call?      → BLOCK (local)
  • shell escape in params ($(), backtick)?        → BLOCK (local)
  • prompt injection in file/web content?          → REDACT in-place (local)
  • credential access + low intent overlap?        → assess via cloud
  • external domains + intent mismatch?            → assess via cloud
      ↓
Allow, redact, alert, or block — with explanation returned to agent
```

No content is sent externally until the plugin is registered and activated.

---

## Step 1: Install

Install from npm or directly from source:

```bash
# From npm
openclaw plugins install @openguardrails/openclaw-security

# From source (audit first, then install)
git clone https://github.com/openguardrails/openguardrails.git
openclaw plugins install -l ./openguardrails/openclaw-security
```

**Installation completes immediately — no network calls are made at install time.** The plugin loads, creates a `BehaviorDetector`, and waits.

Verify it's loaded:
```bash
/og_status
```

Expected output when not yet registered:
```
OpenGuardrails Status

- Status:    not registered — run `/og_activate` to register
- Platform:  https://www.openguardrails.com/core

- blockOnRisk: true
```

---

## Step 2: Register (optional — local-only mode works without this)

Registration is triggered by running `/og_activate`. It enables cloud-based behavioral assessment on top of the local protections you already have.

### What the registration request sends

The plugin calls `POST /api/v1/agents/register` with exactly two fields:

```json
{ "name": "OpenClaw Agent", "description": "" }
```

That's it — an agent display name and an optional description. No machine identifiers, no file paths, no user data. See `agent/config.ts:65-68` in the source.

### What gets stored locally

The response is saved to `~/.openclaw/credentials/openguardrails/credentials.json`:

```json
{
  "apiKey": "sk-og-<32 hex chars>",
  "agentId": "<uuid>",
  "claimUrl": "https://www.openguardrails.com/core/claim/<token>",
  "verificationCode": "word-XXXX"
}
```

These credentials are generated server-side and stored as plaintext JSON on your machine (consistent with how CLI tools like `gh`, `aws`, and `gcloud` store credentials). The `apiKey` authenticates subsequent detection requests. You can revoke it anytime from the account portal or by deleting the credentials file.

### Run registration

```bash
/og_activate
```

If the platform is reachable, you'll see:

```
OpenGuardrails: Claim Your Agent

Agent ID: <uuid>

Complete these steps to activate behavioral detection:

  1. Visit:  https://www.openguardrails.com/core/claim/<token>
  2. Code:   <word-XXXX>  (e.g. reef-X4B2)
  3. Email:  your email becomes your login for the account portal

After claiming you get 30,000 free detections.
Platform: https://www.openguardrails.com/core
```

### Using an existing API key

If you already have a key (e.g. from a previous registration or from the account portal), set it directly — no `/og_activate` needed:

```json
{
  "plugins": {
    "entries": {
      "openguardrails": {
        "config": {
          "apiKey": "sk-og-<your-key>"
        }
      }
    }
  }
}
```

---

## Step 3: Activate (this is where your email is collected)

After registration, complete these steps in your browser to activate cloud assessment. **This is the only step that collects your email** — the registration API call in Step 2 does not send or collect any email.

1. **Visit the claim URL** shown by `/og_activate`
2. **Enter the verification code** (the `word-XXXX` code displayed in the terminal)
3. **Enter your email** — you type this into the web form yourself; it becomes your account identity and is stored for billing
4. **Click the verification link** sent to your email

Once your email is verified, the agent status changes to `active` and behavioral detection begins. The plugin polls for activation status automatically — no restart needed.

Check status anytime:

```bash
/og_status
```

Active output:
```
OpenGuardrails Status

- Agent ID:  <uuid>
- API Key:   sk-og-xxxxxxxxxxxx...
- Email:     you@example.com
- Platform:  https://www.openguardrails.com/core
- Status:    active

- blockOnRisk: true
```

---

## Step 4: Test Detection

After email verification, the platform **automatically sends you a test email** containing a hidden prompt injection. This lets you immediately verify that OpenGuardrails is working.

### How to test

1. Check your inbox for the test email from OpenGuardrails (subject: "Design Review Request")
2. Save it as a `.txt` file (e.g. `~/test-email.txt`)
3. Ask the agent to read the file: *"Read ~/test-email.txt and summarize it"*
4. OpenGuardrails should detect and **redact** the hidden injection before the agent processes it

The test email looks like a normal design review request but contains an embedded injection payload in an HTML comment. With OpenGuardrails active, the injected content is replaced with:
```
__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__
```

### Alternative: use a sample file

You can also test with a sample file from the repository:

```
https://raw.githubusercontent.com/openguardrails/openguardrails/main/openclaw-security/samples/popup-injection-email.txt
```

Download it and ask the agent to read it. OpenGuardrails will detect and redact the injection.

### What the detection looks like

When the agent reads a file containing an injection payload, OpenGuardrails:
1. Scans the content for known injection pattern categories (see detection table above)
2. Redacts the matched content in-place — the agent never sees the raw payload
3. Logs a warning with the detected pattern category

---

## Account & Portal

After activation, sign in to the account portal with your **email + API key**:

```
https://www.openguardrails.com/core/login
```

The portal shows:

- **Account overview** — plan, quota usage, all agents under your email
- **Agent management** — view API keys, regenerate keys
- **Usage logs** — per-agent request history with latency and endpoint breakdown
- **Plan upgrades** — upgrade from Free to Starter, Pro, or Business

### Plans

| Plan | Price | Detections/mo |
|------|-------|---------------|
| Free | $0 | 30,000 |
| Starter | $19/mo | 100,000 |
| Pro | $49/mo | 300,000 |
| Business | $199/mo | 2,000,000 |

If you register multiple agents with the same email, they all share one account and quota.

---

## Commands

| Command | Description |
|---------|-------------|
| `/og_status` | Show registration status, email, platform URL, blockOnRisk setting |
| `/og_activate` | Register (if needed) and show claim URL and activation instructions |

---

## Configuration Reference

All options go in `~/.openclaw/openclaw.json` under `plugins.entries.openguardrails.config`:

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `true` | Enable/disable the plugin |
| `blockOnRisk` | `true` | Block the tool call when risk is detected |
| `apiKey` | `""` | Explicit API key (`sk-og-...`). Run `/og_activate` if empty |
| `agentName` | `"OpenClaw Agent"` | Name shown in the dashboard |
| `coreUrl` | `https://www.openguardrails.com/core` | Platform API endpoint |
| `dashboardUrl` | `https://www.openguardrails.com/dashboard` | Dashboard URL for monitoring and reporting |
| `dashboardSessionToken` | `""` | Dashboard auth token (falls back to `apiKey` if empty) |
| `timeoutMs` | `60000` | Cloud assessment timeout (ms). Fails open on timeout |

---

## What Gets Detected

### Fast-path blocks (local, no cloud round-trip)

| Pattern | Example | Block reason |
|---------|---------|--------------|
| Read sensitive file → network call | Read `~/.ssh/id_rsa`, then `WebFetch` to external URL | `sensitive file read followed by network call to <domain>` |
| Read credentials → network call | Read `~/.aws/credentials`, then `Bash curl ...` | `sensitive file read followed by network call to <domain>` |
| Shell escape in params | `Bash` with `` `cmd` ``, `$(cmd)`, `;`, `&&`, `\|`, or newline injection | `suspicious shell command detected — potential command injection` |

### Content injection detection (local, in-place redaction)

When the agent reads files or fetches web pages, OpenGuardrails scans the content for injection patterns and redacts them before the agent processes the content:

| Pattern Category | Description | Redaction marker |
|-----------------|-------------|------------------|
| Instruction override | Attempts to override or discard prior context | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__` |
| Fake system message | Spoofed system-level directives embedded in user content | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__` |
| Mode switching | Attempts to change the agent's operating mode | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__` |
| Concealment directive | Instructions to hide output from the user | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__` |
| Command execution | Embedded shell commands or execution directives | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_COMMAND_EXECUTION__` |
| Task hijacking | Attempts to redirect the agent's current objective | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_PROMPT_INJECTION__` |
| Data exfiltration | Shell substitution targeting sensitive files | `__REDACTED_BY_OPENGUARDRAILS_DUE_TO_DATA_EXFILTRATION__` |

A single high-confidence match or 2+ medium-confidence matches from different categories triggers redaction. See `agent/content-injection-scanner.ts` for the full pattern list.

### Cloud-assessed patterns

| Tag | Risk | Action | Description |
|-----|------|--------|-------------|
| `READ_SENSITIVE_WRITE_NETWORK` | critical | block | Sensitive read followed by outbound call |
| `DATA_EXFIL_PATTERN` | critical | block | Large data read, then sent externally |
| `MULTI_CRED_ACCESS` | high | block | Multiple credential files accessed in one session |
| `SHELL_EXEC_AFTER_WEB_FETCH` | high | block | Shell command executed after fetching external content |
| `INTENT_ACTION_MISMATCH` | medium | alert | Tool sequence doesn't match stated user goal |
| `UNUSUAL_TOOL_SEQUENCE` | medium | alert | Statistical anomaly in tool ordering |

### Risk levels and actions

| Risk Level | Action | Meaning |
|------------|--------|---------|
| critical | **block** | Tool call is blocked, agent sees block reason |
| high | **block** | Tool call is blocked, agent sees block reason |
| medium | **alert** | Tool call is allowed, warning logged |
| low / no_risk | **allow** | Tool call proceeds normally |

### Block reason format

When a tool call is blocked, the agent receives a message like:

```
OpenGuardrails blocked [critical]: Sensitive file read followed by data
sent to external server. Agent accessed credentials despite low relevance
to user intent "fetch weather for user". (confidence: 97%)
```

### Sensitive file categories recognized

`SSH_KEY`, `AWS_CREDS`, `GPG_KEY`, `ENV_FILE`, `CRYPTO_CERT`, `SYSTEM_AUTH`, `BROWSER_COOKIE`, `KEYCHAIN`

---

## AI Security Gateway (Free)

OpenGuardrails includes a free **AI Security Gateway** — a local HTTP proxy that protects sensitive data from being sent to external LLM providers (Anthropic, OpenAI, Gemini, and compatible APIs like Kimi and DeepSeek).

### How it works

The gateway runs locally on your machine. It intercepts LLM API calls, sanitizes sensitive data before sending to the provider, and restores original values in responses. The entire process is transparent — you use your agent normally, and your data stays protected.

```
Your prompt: "My card is 6222021234567890, book a hotel"
      ↓ Gateway sanitizes locally
LLM sees: "My card is __bank_card_1__, book a hotel"
      ↓ LLM responds
LLM: "Booking with card __bank_card_1__"
      ↓ Gateway restores locally
You see: "Booking with card 6222021234567890"
```

The LLM provider never sees the real card number. You see the correct response. No impact on functionality.

### Data types sanitized by the gateway

| Data Type | Placeholder | Examples |
|-----------|-------------|----------|
| Email addresses | `__email_N__` | `user@example.com` |
| Credit cards | `__credit_card_N__` | `1234-5678-9012-3456` |
| Bank cards | `__bank_card_N__` | 16-19 digit card numbers |
| Phone numbers | `__phone_N__` | `+1-555-123-4567`, `+86-138-1234-5678` |
| API keys & secrets | `__secret_N__` | `sk-...`, `ghp_...`, Bearer tokens, high-entropy tokens |
| IP addresses | `__ip_N__` | `192.168.1.1` |
| SSN | `__ssn_N__` | `123-45-6789` |
| IBAN | `__iban_N__` | `GB82WEST12345698765432` |
| URLs | `__url_N__` | `https://example.com/path` |

More data types will be added based on user needs. Contact us if you need a specific type.

### Setup

1. Set your LLM API keys as environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`)
2. Start the gateway: `npx @openguardrails/gateway` (runs on port 8900 by default)
3. Point your agent's API base URL to `http://127.0.0.1:8900`

The gateway supports Anthropic (`/v1/messages`), OpenAI (`/v1/chat/completions`), and Gemini (`/v1/models/{model}:generateContent`) endpoints, including streaming.

### Key properties

- **100% local** — the gateway runs on localhost, sensitive data never leaves your machine unsanitized
- **Zero dependencies** — no npm dependencies beyond Node.js
- **Stateless** — placeholder-to-original mappings exist only during the request cycle and are discarded after the response is restored
- **Free** — no registration, no API key, no usage limits

---

## Privacy & Data Protection

**OpenGuardrails does not collect or sell your content.** The detection engine is rule-driven and operates on structured signals — it has no LLM to train and no use for your content. Detection request payloads are not retained. Account data (agent ID, email, plan, usage counts) is stored for billing.

### Local-first sanitization

All sensitive data is replaced with category placeholders **on your machine** before anything is sent to the cloud API:

| Data Type | Placeholder |
|-----------|-------------|
| Email addresses | `<EMAIL>` |
| Credit card numbers | `<CREDIT_CARD>` |
| SSNs | `<SSN>` |
| IBANs | `<IBAN>` |
| IP addresses | `<IP_ADDRESS>` |
| Phone numbers | `<PHONE>` |
| URLs | `<URL>` |
| API keys & secrets | `<SECRET>` |
| High-entropy tokens | `<SECRET>` |

The sanitization logic is in `agent/sanitizer.ts` — audit it yourself.

### What stays local (no network calls)

- Injection redaction — regex-based scanning, fully local
- Fast-path blocks — shell escape detection, read-then-exfil patterns
- AI Security Gateway — sanitization and restoration
- Credentials — stored at `~/.openclaw/credentials/openguardrails/credentials.json`
- Low-risk / no-risk tool calls — never leave the machine

### Verification guide

Before installing in production, we recommend:

1. **Audit the source** — clone the repo and review these files:
   - `index.ts` — all event hooks (`before_tool_call`, `after_tool_call`, `tool_result_persist`); confirm no unexpected side effects
   - `agent/sanitizer.ts` — the sanitization logic that strips PII before any cloud call
   - `platform-client/` — every outbound network call the plugin makes; confirm all go to `openguardrails.com/core` only
   - `agent/config.ts:65-68` — the registration request; confirm it sends only `{ name, description }`
2. **Install from source** — clone from GitHub, inspect the code, then install locally:
   ```bash
   git clone https://github.com/openguardrails/openguardrails.git
   # Audit the code, then:
   openclaw plugins install -l ./openguardrails/openclaw-security
   ```
3. **Run in local-only mode first** — skip `/og_activate` to use all local protections (injection redaction, shell escape blocking, read-then-exfil detection) with zero cloud connectivity
4. **Monitor network traffic** — after registration, the plugin only contacts `openguardrails.com/core` for behavioral assessment; verify with your network monitor of choice
5. **Use a disposable email** for initial testing if you prefer not to use your primary email during evaluation
6. **Revoke anytime** — each agent gets its own API key; revoke from the account portal or delete `~/.openclaw/credentials/openguardrails/credentials.json`

---

## Contact

Have questions, feature requests, or need enterprise deployment support?

- **Email**: thomas@openguardrails.com
- **GitHub**: [github.com/openguardrails/openguardrails](https://github.com/openguardrails/openguardrails)

We welcome feedback on detection accuracy, requests for new sanitized data types, and enterprise inquiries for private deployment, custom rules, and dedicated support.

---

## Uninstall

```bash
rm -rf ~/.openclaw/extensions/openguardrails
# Then manually delete openguardrails config in ~/.openclaw/openclaw.json
# Optionally remove credentials
rm -rf ~/.openclaw/credentials/openguardrails
```
