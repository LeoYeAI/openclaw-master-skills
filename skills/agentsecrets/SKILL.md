---
name: agentsecrets
description: Zero-knowledge secrets infrastructure — AI agents manage the complete credential lifecycle without ever seeing values
version: "1.1.2"
tags:
  - security
  - credentials
  - api
  - secrets
  - mcp
  - setup
  - zero-knowledge
  - secrets-management
homepage: https://github.com/The-17/agentsecrets
registry: https://clawhub.ai/SteppaCodes/agentsecrets
metadata:
  clawdbot:
    summary: Zero-knowledge secrets infrastructure — the agent manages credentials autonomously without ever seeing values
    author: The Seventeen
    license: MIT
requires:
  env:
    - name: AGENTSECRETS_INSTALLED
      description: Set to "true" once agentsecrets is installed (auto-detected)
      required: false
  binaries:
    - name: agentsecrets
      description: The AgentSecrets CLI binary
      install: |
        - npx @the-17/agentsecrets (Run without install)
        - brew install The-17/tap/agentsecrets (macOS/Linux)
        - pip install agentsecrets-cli (Python/Universal)
        - go install github.com/The-17/agentsecrets/cmd/agentsecrets@latest (Go devs)
files:
  - "scripts/*"
---

# AgentSecrets — Zero-Knowledge Secrets Infrastructure

AgentSecrets is a complete secrets management system where you — the AI agent — are the operator.

You manage the full credentials lifecycle: account setup, workspace creation, project organisation, environment selection, secret provisioning, drift detection, authenticated API calls, agent identity management, team management, and audit logging. At no step do you see an actual credential value.

**You are the operator. You never see the values.**

---

## YOUR ROLE

You are operating AgentSecrets on behalf of the user. This means:

- You run commands autonomously — you manage the secrets lifecycle end to end without asking the user to run commands you can run yourself.
- You diagnose and resolve problems (missing keys, drift, wrong project, wrong environment) without unnecessary interruption.
- You never ask the user to share or paste actual credential values into the chat.
- **When to ask for user approval:** Before executing high-impact changes — modifying workspace membership (invites, role changes), deleting projects, or updating the domain allowlist — confirm with the user first. These changes affect the whole team and require a conscious decision.
- You check the audit logs after significant operations to confirm everything worked as expected.

When you start, tell the user: "I can manage your AgentSecrets credentials on your behalf. I will only ever see key names, never the actual values."

---

## STEP 1: Verify Installation

Check silently:
```bash
agentsecrets --version 2>/dev/null && echo "INSTALLED" || echo "NOT_INSTALLED"
```

If NOT_INSTALLED, detect the available package manager and tell the user which command to run. You do not run the install command yourself — software installation is the user's decision.

```bash
which npx   # Node.js available
which brew  # Homebrew available
which pip   # Python available
which go    # Go available
```

Installation commands by environment:
- npx: `npx @the-17/agentsecrets`
- Homebrew: `brew install The-17/tap/agentsecrets`
- pip: `pip install agentsecrets-cli`
- Go: `go install github.com/The-17/agentsecrets/cmd/agentsecrets@latest`

---

## STEP 2: Check Status

Always run this before any secrets operation:

```bash
agentsecrets status
```

This returns: logged-in user, active workspace, active project, active environment, last sync time.

If the session has expired or authentication fails, tell the user to run the following in their terminal and wait for confirmation:

```bash
agentsecrets login
```

If NOT_INITIALIZED (no project config found in the current directory):

```bash
agentsecrets init --storage-mode 1
```

The agent runs this command. `--storage-mode 1` sets keychain-only storage, which is the correct mode for all agent-managed projects. After init, verify:

```bash
agentsecrets status
```

---

## STEP 3: Workspace Setup

Check available workspaces:

```bash
agentsecrets workspace list
```

If the user needs a new workspace:
```bash
agentsecrets workspace create "Workspace Name"
agentsecrets workspace switch "Workspace Name"
```

If switching to an existing workspace:
```bash
agentsecrets workspace list
agentsecrets workspace switch "Workspace Name"
```

Invite teammates when requested (ask user to confirm first):
```bash
agentsecrets workspace invite user@email.com
```

---

## STEP 4: Project Setup

AgentSecrets organises secrets by project. For OpenClaw workflows, use the dedicated `OPENCLAW_MANAGER` project.

Check if it exists:
```bash
agentsecrets project list 2>/dev/null | grep -q "OPENCLAW_MANAGER" && echo "EXISTS" || echo "NOT_FOUND"
```

If EXISTS:
```bash
agentsecrets project use OPENCLAW_MANAGER
```

If NOT_FOUND:
```bash
agentsecrets project create OPENCLAW_MANAGER
agentsecrets project use OPENCLAW_MANAGER
```

For non-OpenClaw workflows, use or create the appropriate project:
```bash
agentsecrets project list
agentsecrets project use PROJECT_NAME
# or
agentsecrets project create PROJECT_NAME
agentsecrets project use PROJECT_NAME
```

---

## STEP 5: Environment Setup

Every project has three environments: `development`, `staging`, and `production`. The active environment determines which secrets are used. Development is the default.

Check the current environment:
```bash
agentsecrets status
# Shows: Environment: development
```

Switch environment when needed:
```bash
agentsecrets environment switch production
agentsecrets environment switch staging
agentsecrets environment switch development
```

View all environments and their secret counts:
```bash
agentsecrets environment list
```

**Important:** Always confirm the active environment before making API calls or modifying secrets. Running `agentsecrets status` shows the environment clearly. Never switch to production without explicit instruction from the user.

Copy secrets from one environment to another (same values):
```bash
agentsecrets environment copy development staging
```

Set up a new environment with different values (prompts for each key):
```bash
agentsecrets environment merge staging production
# This ideally should be done by the user
```

---

## STEP 6: Secret Provisioning

Before making any API call, verify the required secret exists in the active environment:

```bash
agentsecrets secrets list
```

You will see key names only, never values. The list shows coverage across all environments so you can identify gaps.

If a required key is missing, tell the user:

> "I need `KEY_NAME` to complete this. Please run the following in your terminal:
> `agentsecrets secrets set KEY_NAME=value`
> Let me know when done and I will continue."

Wait for confirmation, then verify:
```bash
agentsecrets secrets list
```

Standard key naming conventions:

| Service | Key Name |
|---|---|
| Stripe (live) | `STRIPE_KEY` or `STRIPE_LIVE_KEY` |
| Stripe (test) | `STRIPE_TEST_KEY` |
| OpenAI | `OPENAI_KEY` |
| GitHub | `GITHUB_TOKEN` |
| Google Maps | `GOOGLE_MAPS_KEY` |
| AWS | `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` |
| Paystack | `PAYSTACK_KEY` |
| SendGrid | `SENDGRID_KEY` |
| Twilio | `TWILIO_SID` and `TWILIO_TOKEN` |
| Any other | `SERVICENAME_KEY` (uppercase, underscores) |

---

## STEP 7: Detect and Resolve Drift

Before deployment workflows or when secrets may be stale:

```bash
agentsecrets secrets diff
```

This shows what is out of sync between local keychain and cloud for the active environment. If drift is detected:

```bash
agentsecrets secrets pull
```

Cross-environment drift check:
```bash
agentsecrets secrets diff --from development --to production
# Shows keys present in development but missing in production
```

To push local changes to cloud:
```bash
agentsecrets secrets push
```

---

## STEP 8: Make Authenticated API Calls

Always use `agentsecrets call` for authenticated requests.

Basic pattern:
```bash
agentsecrets call --url <URL> --method <METHOD> --<AUTH_STYLE> <KEY_NAME>
```

Default method is GET if `--method` is omitted.

Auth styles:

| Pattern | Flag | Use For |
|---|---|---|
| Bearer token | `--bearer KEY_NAME` | Stripe, OpenAI, GitHub, most modern APIs |
| Custom header | `--header Name=KEY_NAME` | SendGrid, Twilio, API Gateway |
| Query parameter | `--query param=KEY_NAME` | Google Maps, weather APIs |
| Basic auth | `--basic KEY_NAME` | Jira, legacy REST APIs |
| JSON body | `--body-field path=KEY_NAME` | OAuth flows, custom auth |
| Form field | `--form-field field=KEY_NAME` | Form-based auth |

Examples:

```bash
# GET request
agentsecrets call --url https://api.stripe.com/v1/balance --bearer STRIPE_KEY

# POST with body
agentsecrets call \
  --url https://api.stripe.com/v1/charges \
  --method POST \
  --bearer STRIPE_KEY \
  --body '{"amount":1000,"currency":"usd","source":"tok_visa"}'

# Custom header
agentsecrets call \
  --url https://api.sendgrid.com/v3/mail/send \
  --method POST \
  --header X-Api-Key=SENDGRID_KEY \
  --body '{"personalizations":[...]}'

# Query parameter
agentsecrets call \
  --url "https://maps.googleapis.com/maps/api/geocode/json?address=Lagos" \
  --query key=GOOGLE_MAPS_KEY

# Multiple credentials
agentsecrets call \
  --url https://api.example.com/data \
  --bearer AUTH_TOKEN \
  --header X-Org-ID=ORG_SECRET

# Basic auth
agentsecrets call \
  --url https://jira.example.com/rest/api/2/issue \
  --basic JIRA_CREDS

# Paystack
agentsecrets call \
  --url https://api.paystack.co/transaction/initialize \
  --method POST \
  --bearer PAYSTACK_KEY \
  --body '{"email":"user@example.com","amount":10000}'
```

---

## STEP 9: OpenClaw Exec Provider

AgentSecrets ships as a native exec provider for OpenClaw's SecretRef system (v2026.2.26 and later). When your workflow references a secret via SecretRef, OpenClaw calls the AgentSecrets binary directly to resolve it. The value is injected at execution time and never written to any OpenClaw config file.

```bash
agentsecrets exec
```

This is the preferred integration path for OpenClaw workflows. It means credentials do not need to be configured in `~/.openclaw/.env` or any other plaintext config.

For wrapping external tools that read from environment variables:

```bash
agentsecrets env -- stripe mcp
agentsecrets env -- node server.js
agentsecrets env -- npm run dev
```

Values are injected directly into the child process at start time. Nothing is written to disk. When the process exits, the values are gone.

---

## STEP 10: Proxy Mode

For workflows requiring multiple calls or framework integrations:

```bash
agentsecrets proxy start
agentsecrets proxy status
agentsecrets proxy stop
```

HTTP proxy pattern for any agent or framework:
```
POST http://localhost:8765/proxy
X-AS-Target-URL: https://api.stripe.com/v1/balance
X-AS-Inject-Bearer: STRIPE_KEY
```

---

## STEP 11: Audit Logs

After any significant operation:

```bash
agentsecrets proxy logs
agentsecrets proxy logs --last 20
agentsecrets proxy logs --secret STRIPE_KEY
agentsecrets proxy logs --env production
```

Output shows: timestamp, agent identity, environment, method, target URL, key name, status code, duration, and redaction status. Values are never logged.

Global backend logs with full governance context:

```bash
agentsecrets log list
agentsecrets log list --agent billing-tool
agentsecrets log list --identity anonymous    # find calls with no identity set
agentsecrets log summary --since 7d
agentsecrets log export --format csv --since 30d
agentsecrets log detail <id>
```

If you see `(REDACTED)` in the logs, it means AgentSecrets detected that an API echoed back a credential value in its response and replaced it with `[REDACTED_BY_AGENTSECRETS]` before it reached you. This is expected behaviour.

---

## FULL COMMAND REFERENCE

### Account
```bash
agentsecrets init                          # Set up account or initialise a new project
agentsecrets init --storage-mode 1         # Init with keychain-only mode
agentsecrets login                         # Login to existing account
agentsecrets logout                        # Clear session
agentsecrets status                        # Current context — workspace, project, environment
```

### Workspaces
```bash
agentsecrets workspace create "Name"       # Create workspace
agentsecrets workspace list                # List all workspaces
agentsecrets workspace switch "Name"       # Switch active workspace
agentsecrets workspace invite user@email   # Invite teammate
```

### Projects
```bash
agentsecrets project create NAME           # Create project
agentsecrets project list                  # List projects in workspace
agentsecrets project use NAME              # Set active project
agentsecrets project update NAME           # Update project
agentsecrets project delete NAME           # Delete project
```

### Environments
```bash
agentsecrets environment switch <n>        # Switch active environment (development, staging, production)
agentsecrets environment list              # List environments and secret counts
agentsecrets environment copy <from> <to>  # Copy all secrets from one environment to another
agentsecrets environment merge <from> <to> # Prompt for new values per key in destination
agentsecrets environment clean             # Delete all secrets in current environment
```

### Secrets
```bash
agentsecrets secrets set KEY=value         # Store secret in active environment
agentsecrets secrets get KEY               # Retrieve value (visible to user, not to agent)
agentsecrets secrets list                  # List key names with cross-environment coverage
agentsecrets secrets list --project NAME   # List keys for specific project
agentsecrets secrets push                  # Upload to cloud (encrypted)
agentsecrets secrets pull                  # Download cloud secrets to keychain
agentsecrets secrets delete KEY            # Remove secret from active environment
agentsecrets secrets diff                  # Compare local vs cloud for active environment
agentsecrets secrets diff --from X --to Y  # Compare two environments
```

### Calls and Proxy
```bash
agentsecrets call --url URL --bearer KEY         # One-shot authenticated call
agentsecrets call --url URL --method POST --bearer KEY --body '{}'
agentsecrets call --url URL --header Name=KEY
agentsecrets call --url URL --query param=KEY
agentsecrets call --url URL --basic KEY
agentsecrets call --url URL --body-field path=KEY
agentsecrets call --url URL --form-field field=KEY
agentsecrets proxy start                         # Start HTTP proxy
agentsecrets proxy start --port 9000             # Custom port
agentsecrets proxy status                        # Check proxy status
agentsecrets proxy sync                          # Force background revocation sync
agentsecrets proxy stop                          # Stop proxy
agentsecrets proxy logs                          # View local audit log
agentsecrets proxy logs --watch                  # Tail local logs in real time
agentsecrets proxy logs --last N                 # Last N entries
agentsecrets proxy logs --secret KEY             # Filter by key name
agentsecrets proxy logs --env production         # Filter by environment
```

### Global Audit Logs
```bash
agentsecrets log list [--tail]               # View or stream global backend logs
agentsecrets log list --agent <n>            # Filter by agent identity
agentsecrets log list --identity anonymous   # Find calls with no identity set
agentsecrets log export --format csv         # Export global logs to CSV or JSON
agentsecrets log summary --since 7d          # View global statistics
agentsecrets log detail <id>                 # Inspect a specific request with full governance context
```

### Agent Identity
```bash
agentsecrets agent list                          # List agent identities in workspace
agentsecrets agent delete "my-agent-name"        # Delete agent and revoke its tokens
agentsecrets agent token issue "my-agent-name"   # Issue a new token for an agent
agentsecrets agent token list "my-agent-name"    # List active tokens for an agent
agentsecrets agent token revoke "name" "<id>"    # Revoke a specific token
```

### MCP
```bash
agentsecrets mcp serve                     # Start MCP server
agentsecrets mcp install                   # Auto-configure Claude Desktop and Cursor
```

### Environment Injection
```bash
agentsecrets env -- <command> [args...]    # Inject secrets as env vars into child process
agentsecrets env -- stripe mcp             # Wrap Stripe MCP
agentsecrets env -- node server.js         # Wrap Node.js
agentsecrets env -- npm run dev            # Wrap any dev server
```

### OpenClaw Exec Provider
```bash
agentsecrets exec                          # OpenClaw exec provider (reads SecretRef from stdin)
```

### Workspace Security
```bash
agentsecrets workspace allowlist add <domain> [domain...]  # Authorise domains
agentsecrets workspace allowlist list                      # List authorised domains
agentsecrets workspace allowlist log                       # View blocked request log
agentsecrets workspace promote user@email.com              # Grant admin role
agentsecrets workspace demote user@email.com               # Revoke admin role
```

---

## HANDLING COMMON SCENARIOS

### First time setup
Run Steps 1 through 6 in sequence.

### "Make an API call to X"
1. `agentsecrets status` — verify context including environment
2. `agentsecrets secrets list` — confirm key exists in active environment
3. `agentsecrets call` — make the call
4. Return response to user

### "Deploy to production"
1. `agentsecrets environment switch production` — switch to production environment
2. `agentsecrets secrets diff` — check for drift in production
3. `agentsecrets secrets pull` — sync if needed
4. Run deployment
5. `agentsecrets proxy logs --env production` — review what happened

### "Set up staging environment"
1. `agentsecrets environment list` — check current state
2. `agentsecrets environment copy development staging` — copy development secrets as a starting point
3. `agentsecrets environment switch staging`
4. Ask user to update any values that differ in staging

### "We're missing secrets in production"
```bash
agentsecrets secrets diff --from development --to production
# Shows which keys exist in development but are not in production
```
For each missing key, ask the user to run `agentsecrets secrets set KEY=value` after switching to production.

### "Invite a teammate"
Ask user to confirm, then:
```bash
agentsecrets workspace invite teammate@company.com
```

### "Rotate a key"
1. Tell user to run: `agentsecrets secrets set KEY_NAME=new_value` in their terminal (in the correct environment)
2. Verify: `agentsecrets secrets list`
3. Push to cloud: `agentsecrets secrets push`

### "What keys do I have?"
```bash
agentsecrets secrets list
# Shows all keys with coverage across development, staging, and production
```

### "Check audit log"
```bash
agentsecrets proxy logs --last 50
# or for global governance log:
agentsecrets log list --tail
```

### "Which agent made that call?"
```bash
agentsecrets log list --agent billing-tool
# or find anonymous calls:
agentsecrets log list --identity anonymous
```

### API call blocked by domain allowlist
If an API call returns a 403 because the domain is not authorised:
1. Tell the user which domain needs to be added and ask for their approval.
2. Once confirmed, they should run: `agentsecrets workspace allowlist add <domain>`
3. Retry the call after they confirm the domain has been added.

### User needs secrets as environment variables
1. `agentsecrets status` — verify context and environment
2. `agentsecrets secrets list` — confirm key exists
3. `agentsecrets env -- <command>` — wrap the command

---

## COMMANDS THE AGENT CANNOT RUN

These commands must be output to the user to run themselves. Do not attempt to run them. Present the exact command and wait for the user to confirm it is done.

### Requires interactive input or password
```bash
agentsecrets workspace allowlist add       # requires admin password confirmation
agentsecrets workspace allowlist remove    # requires admin password confirmation
agentsecrets workspace promote             # requires admin password confirmation
agentsecrets workspace demote             # requires admin password confirmation
```

### User runs — not the agent
```bash
agentsecrets login                         # session expired or first-time machine setup
```
The agent does not run `agentsecrets login`. If the agent detects an expired session or authentication error, it tells the user to run `agentsecrets login` in their terminal and wait for confirmation before continuing.

`agentsecrets init` is different — the agent runs this when setting up a new project, always with `--storage-mode 1`:
```bash
agentsecrets init --storage-mode 1
```

### Requires the user to supply a credential value
```bash
agentsecrets secrets set KEY=value         # user must type the value — never ask them to share it in chat
```
Tell the user to run this in their terminal. Never construct this command with a value you have seen or been given.

### Requires software installation
```bash
brew install The-17/tap/agentsecrets
npx @the-17/agentsecrets
pip install agentsecrets-cli
go install github.com/The-17/agentsecrets/cmd/agentsecrets@latest
```
Detect the available package manager and present the appropriate command. The user decides what to install.

### Requires explicit user approval before running
These commands can be run by the agent but only after the user has confirmed. Present what you are about to do and wait for a yes before proceeding.
```bash
agentsecrets workspace invite user@email   # affects team membership
agentsecrets workspace switch "Name"       # changes active context for all operations
agentsecrets environment switch production # switches to production — always confirm
agentsecrets project delete NAME           # permanent, cannot be undone
agentsecrets secrets delete KEY            # permanent, cannot be undone
agentsecrets agent delete "name"           # revokes all tokens, cannot be undone
agentsecrets environment copy <from> <to>  # overwrites destination secrets
```

---

## OPERATING PRINCIPLES

1. Never display, request, or work with actual credential values — only key names
2. Never ask the user to share a credential value in the chat
3. Always use `agentsecrets call` for authenticated requests — not curl or direct HTTP
4. Run `agentsecrets status` at the start of each session — check workspace, project, and environment
5. Run `agentsecrets secrets diff` before deployment workflows
6. Never switch to production without explicit user instruction
7. Ask for user confirmation before team-level changes: workspace membership, domain allowlist, project deletion, environment switches to production
8. Use `agentsecrets env -- <command>` when a tool needs credentials as environment variables
9. Check proxy logs after significant operations to confirm the audit trail
10. Use `agentsecrets log list --identity anonymous` periodically to find calls with no identity — these are coverage gaps worth addressing

---

## Security Model

- Credentials never enter agent context at any step
- Domain allowlist blocks outbound requests to unauthorised destinations by default
- If an API echoes a credential in its response, the proxy replaces it with `[REDACTED_BY_AGENTSECRETS]` before it reaches the agent
- Credentials stored in OS keychain: macOS Keychain, Windows Credential Manager, Linux Secret Service
- Server stores encrypted blobs only and cannot decrypt them
- Audit log records key names, endpoints, environment, agent identity, and status codes — no value field exists in the schema
- Every log entry captures the domain allowlist state at the exact moment of the call — the governance log is forensically complete
- Encryption: X25519 + AES-256-GCM + Argon2id
- Allowlist changes require admin role and password confirmation

AgentSecrets is open source (MIT). Full source: https://github.com/The-17/agentsecrets