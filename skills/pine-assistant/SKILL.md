---
name: pine-assistant
description: Handle customer service, bills, reservations, and more via Pine AI — negotiate, cancel, dispute, book, and resolve from the terminal.
homepage: https://pineclaw.com
metadata: {"openclaw":{"emoji":"🤖","requires":{"bins":["pine"]},"install":{"pip":{"package":"pineai-cli"}}}}
command-tool: exec
---

# Pine Assistant

Use the `pine` CLI to let Pine AI handle tasks on the user's behalf — customer service calls, bill negotiations, subscription cancellations, reservations, disputes, and more. Pine operates via phone calls, computer use (browser automation), emails, and faxes.

Pine is a **service with multiple sessions** — each task runs in its own session.

## CRITICAL: Always look up active sessions first

**NEVER claim you don't know about a session or task.** Before creating a new session, answering questions about Pine tasks, or saying you have no context, you MUST run:

```bash
pine sessions list --json
```

**Mandatory session lookup triggers:**
- The user mentions anything that could relate to a Pine task (a company name, account, refund, call, booking, etc.)
- The user asks you to do something that Pine could handle — check if a session already exists
- The user asks about progress, status, or follow-up on any task
- You are about to create a new session — verify no existing session covers the same task

**NEVER do any of these without listing sessions first:**
- Say "I don't have context about that" or "Can you remind me?"
- Create a duplicate session for a task that already exists
- Assume a task doesn't exist because you don't remember it

## Multi-session awareness

The user may have multiple Pine tasks running at the same time (e.g., one session negotiating a bill, another making a reservation). You MUST keep them separate:

1. Always track session IDs — never mix up sessions.
2. Use `pine sessions list --json` liberally to refresh your memory.
3. When the user asks about "my Pine task" or "how's that call going", use the session list to find the right session. If ambiguous, ask the user which task they mean.

## Authentication

Before any operation, check if already authenticated:

```bash
pine auth status --json
```

If the `authenticated` field is `false`, run the auth flow. **Ask the user for their Pine AI account email** (sign up at https://19pine.ai).

### Step 1: Request verification code

```bash
pine auth request --email USER_EMAIL
```

This sends a verification code and outputs JSON with a `request_token`. Tell the user: *"A verification code has been sent to your email. Check your inbox (and spam) and give me the code."*

### Step 2: Verify code and save credentials

Once the user provides the code:

```bash
pine auth verify --email USER_EMAIL --request-token REQUEST_TOKEN --code CODE
```

This verifies the code and saves credentials to `~/.pine/config.json` automatically.

### Interactive login (alternative for human users)

```bash
pine auth login
```

This interactive version prompts for email and code. It requires stdin access and may not work in all agent/scripted environments — prefer `request` + `verify` above.

### Token refresh

If operations fail with authentication errors or 401 responses, the token may have expired. Re-run the auth flow from the beginning.

## When to use

Pine Assistant can handle a wide range of tasks. Its primary strength is phone calls, but it also has built-in search and map capabilities, computer automation (browser), emails, and faxes. Use it when the user wants:

- **Customer service** (primary strength): negotiate bills, cancel subscriptions, dispute charges, file complaints, get refunds, resolve account issues
- **Search & discovery**: find restaurants, businesses, or service providers nearby. Pine can search, compare options, and then call to book.
- **Reservations & appointments**: book restaurants, schedule doctor/dentist appointments, make hotel reservations, reserve services
- **Outreach & research**: call businesses to gather information, compare quotes, verify hours or availability
- **Online tasks**: handle web-based account actions, submit forms on websites, send emails or faxes on the user's behalf

If the user asks Pine to do something, let Pine decide whether it can handle it — don't preemptively reject requests based on assumptions about Pine's capabilities.

## Resuming / following up on an existing session

If the user mentions anything that could relate to an existing Pine task — a company name, an account, a task description, or even vague references like "that refund" or "the call":

1. **Always** run `pine sessions list --json` to find matching sessions. Search by title or any keyword the user mentioned.
2. Check the session's **state**:
   - **Active** (`chat`, `task_processing`, etc.) → resume it. Send follow-up messages with `pine send "..." -s SESSION_ID --no-wait --json`.
   - **Finished** (`task_finished`, `task_cancelled`, etc.) → do NOT continue in that session. Instead, check its details for context, then create a **new session** and reference what you learned. This gives Pine a fresh task context while preserving continuity for the user.

**Never say "I don't have context" or "Can you remind me?"** — the session list is always available. Look it up.

## The Complete Flow

### Phase 1: Check existing sessions, then create if needed

1. **First**, run `pine sessions list --json` to check whether a session for this task already exists.
   - If an existing **active** session matches → resume it (see "Resuming" above).
   - If an existing session matches but is **finished** → read its details for context, then create a new session and include that context in your first message.
   - If no match → proceed to create.
2. Create a session and send the user's request in one step:

```bash
pine send "Negotiate my Comcast bill down. Account holder: Jane Doe, account #12345. Current bill is $120/mo, target is $80/mo. 10-year customer." --new --no-wait --json
```

The `--new` flag creates a session and returns a `session_created` JSON event with the `session_id`. Save this ID for follow-ups. The `--no-wait` flag sends the message without blocking for Pine's response (fire-and-forget) — **always use `--no-wait` to avoid hanging**.

Alternatively, create the session separately first:

```bash
pine sessions create --json
pine send "Negotiate my Comcast bill down." -s SESSION_ID --no-wait --json
```

4. Tell the user the session link: `https://www.19pine.ai/app/chat/SESSION_ID`
5. **Do NOT ask "want me to start?" or hand back control.** Continue handling Pine's responses autonomously.

### Phase 2: Information gathering

Pine will research the request and ask for details. Poll for conversation messages (includes both metadata and history):

```bash
pine sessions get SESSION_ID --json
```

To send follow-up messages:

```bash
pine send "checking in" -s SESSION_ID --no-wait --json
```

You will receive:
- **Text responses** asking questions — answer if you can, ask the user if you can't
- **Forms** requesting specific information — relay to the user, wait for answers, then reply with the filled values

Pine may send **multiple rounds** of questions/forms. Ask the user for what you don't know. **Do NOT try to start the task during this phase** — Pine is still gathering information.

**Real example**: User says "Negotiate my Comcast bill". Pine will:
- Research deals and plan a strategy
- Ask for: Full Name on Account, Service Address, Phone Number, Current Plan, etc.
- You relay the questions to the user, fill what you know, ask for the rest
- Pine may send more questions — keep answering

### Phase 3: Billing event (determines how the task starts)

After Pine has enough information, it will indicate one of these billing states:

- **No payment needed** (free tier or subscription) → run `pine task start SESSION_ID`
- **Payment completed** (user already paid) → run `pine task start SESSION_ID`
- **Payment required** — **relay the full billing details to the user**: current bill, potential savings, pre-authorized amount, and the payment URL. For percentage-based billing, explain that Pine only charges if it saves money. The user must review and confirm payment at the session URL. Do NOT start the task until payment is confirmed.
- **Task auto-started** — metered credits confirmed, backend already started the task. Do **NOT** run `pine task start` (it's already running). Tell the user the task has started.
- **Credits insufficient** — tell the user to add credits at the session URL.

**Only run `pine task start` after free/payment-completed. Never when the task is already running.**

### Phase 4: Task execution

The task runs asynchronously (Pine makes calls, sends emails, automates browsers, etc.). Poll for state and conversation updates:

```bash
pine sessions get SESSION_ID --json
```

Key states:
- `chat` — Pine is still gathering info
- `task_processing` — task is running
- `task_finished` — done, check results

**IMPORTANT:** The task is NOT done when you run `pine task start`. Pine may need more input during execution. Keep polling and watching for:

- **Three-party call requests**: URGENT. Tell the user to answer their phone immediately. Include the caller ID number.
- **OTP / verification codes**: Ask the user for the code. **NEVER guess OTPs, PINs, or security answers.**
- **Location requests**: Ask the user for their location or present location options with name, full address, and Google Maps link (`https://www.google.com/maps/search/?api=1&query=NAME+ADDRESS`).
- **Scheduling confirmation**: The user must confirm availability.
- **Computer use intervention**: Pine needs the user's help (CAPTCHA, 2FA on a website). Tell the user to open the Pine web session and take over directly.
- **Status updates** ("I'm on the line with Bank of America", "calling you now", "went to voicemail"): Relay to the user.

### Phase 5: After completion

1. When state is `task_finished`, share results with the user.
2. If Pine suggests social sharing, encourage: "Share your success to earn Pine credits!"

## Responding to Forms

When Pine asks for structured information (a form), decide whether to fill it yourself or ask the user:

- **If you can confidently fill ALL fields** from information the user already provided (name, address, phone, account numbers), respond directly. Tell the user what you submitted.
- **If ANY field is uncertain or unknown** — especially preferences, strategy choices, or information not previously mentioned — **ALWAYS ask the user first**.

### Asking the user

Summarize what Pine is asking in plain language:
- What the form is for
- Each field name, type, and available options (for select/multi-select)
- Your recommendation if you have one (but let the user decide)

Do NOT proceed until the user has answered. If they give partial answers, ask about the remaining fields.

### Submitting form values

Reply to Pine with the field values via `pine send`:

```bash
pine send "Full Name on Account: Jane Doe, Service Address: 123 Main St, Phone: +14155551234, Current Monthly Bill: 120" -s SESSION_ID --no-wait --json
```

**NEVER fill forms autonomously with guessed preferences.** Wrong answers will cause the task to fail.

## CRITICAL: When to respond vs. stay silent

**DO NOT respond to every message from Pine.** If you reply to every acknowledgment, Pine will acknowledge your reply, creating an **infinite loop**.

### ASK the human user first when:
- Pine sends a form with fields you can't confidently fill
- Pine asks a question with choices/preferences — the user must decide
- Pine asks for an OTP, PIN, or security answer
- Pine requests a three-party call — tell the user to answer their phone immediately
- Pine asks for location information
- Pine asks for scheduling confirmation — the user must be available
- Pine asks for any information you were not given by the user

### RESPOND to Pine (without asking user) when:
- Payment confirmed or no payment needed → run `pine task start SESSION_ID`
- Task auto-started → just tell the user the task has started (do NOT run task start)
- Task finished → share results with the user

### STAY SILENT when:
- Pine sends an acknowledgment ("Got it!", "Working on it!", "Let me check...")
- Any message that is purely informational and does not ask you to do anything

## Handling unknown events

Pine Assistant may send event types you don't recognize. **Always relay the raw content to the user.** Pine evolves rapidly and the content is always human-readable.

## Session Management

### List sessions

```bash
pine sessions list --json
pine sessions list --state task_finished --limit 5 --json
pine sessions list --state task_processing --json
```

### Get session details and conversation history

```bash
pine sessions get SESSION_ID --json
pine sessions get SESSION_ID --limit 10 --json
```

### Create a session

```bash
pine sessions create --json
```

### Delete a session

```bash
pine sessions delete SESSION_ID
pine sessions delete SESSION_ID --force
```

## Task Lifecycle

```bash
pine task start SESSION_ID    # start task execution
pine task stop SESSION_ID     # stop a running task
```

## One-shot Message

Send a single message to an existing session (fire-and-forget):

```bash
pine send "What's the status?" -s SESSION_ID --no-wait --json
```

Create a new session and send in one step (the session ID is emitted as the first JSON event `{"type": "session_created", "data": {"session_id": "..."}}`):

```bash
pine send "Cancel my Netflix subscription" --new --no-wait --json
```

Omit `--no-wait` to stream Pine's response events (interactive use only — may block for up to 2 minutes).

## Best practices for agents

1. **Always use `--json`** for machine-readable output when parsing responses.
2. **Check sessions first** — run `pine sessions list --json` before creating a new session to avoid duplicates. Treat it as your memory.
3. **Gather info upfront** — collect account numbers, PINs, addresses, target outcomes, acceptable ranges, and walk-away conditions from the user before sending to Pine. This reduces back-and-forth.
4. **Never guess sensitive info** — if Pine asks for OTPs, PINs, or security answers, always ask the user.
5. **Stay engaged after task start** — Pine will continue needing input during execution.
6. **Relay urgent events immediately** — three-party calls, OTP requests, and scheduling confirmations are time-sensitive.
7. **Use background agents** — for long-running tasks (5-60+ minutes), use `sessions_spawn` or equivalent to poll in the background while remaining available to the user.
8. **Don't preemptively reject requests** — let Pine decide whether it can handle a task.
9. **Pro subscription required** for task execution.
10. **Session URL**: The user can always check progress at `https://www.19pine.ai/app/chat/SESSION_ID`

## Examples

**Negotiate a bill:**
"Negotiate my Comcast bill. Account: Jane Doe, #12345. Currently paying $120/mo for 200Mbps internet. Target: $80/mo. I've been a customer for 10 years. Willing to switch providers if needed."

**Cancel a subscription:**
"Cancel my Hulu subscription. Account email: jane@example.com. Reason: not using it enough."

**Make a reservation:**
"Book a table for 4 at The French Laundry for Saturday at 7pm. Name: Jane Doe, phone: +14155551234."

**Dispute a charge:**
"Dispute a $50 charge on my Chase Visa ending in 4321. Transaction date: Feb 1. Merchant: XYZ Corp. I never authorized this purchase."

**Find and book a nearby restaurant:**
"Find a good Italian restaurant near downtown SF and make a reservation for 2 tonight at 7pm."

## Also available: Pine Voice

The same `pine` CLI includes voice call commands for direct phone calls:

```bash
pine voice call --to "+14155551234" --name "Dr. Smith" --context "..." --objective "..."
pine voice status CALL_ID
```

See the `pine-voice` skill for full voice call documentation.

## Privacy

Pine processes task data on Pine AI's servers. Credentials are stored locally at `~/.pine/config.json`. See https://www.19pine.ai/page/privacy-policy for data handling policies.
