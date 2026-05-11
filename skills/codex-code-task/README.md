# openclaw-skill-codex-cli

**Async OpenAI Codex task runner for OpenClaw — delegate heavy work to Codex, get results delivered automatically to your chat.**

An OpenClaw skill that lets your agent run OpenAI Codex CLI tasks in the background. The agent sends work to Codex, goes back to chatting, and gets notified automatically when the work is done — with heartbeat pings every minute while it runs.

---

## Why This Exists

### 1. Codex is a full-powered AI agent

Codex is not just a code editor assistant. In `codex exec` mode it is a full autonomous agent: it can read and write files, run shell commands, optionally search the web, and produce detailed results without human interaction.

This makes it ideal for delegating complex tasks: background research, codebase analysis, multi-file refactoring, document generation, data processing. You write a prompt, launch it, and come back to the result.

### 2. Multi-layer agent orchestration

OpenClaw acts as your technical PM — it understands the goal, breaks it down, and decides what to delegate. Codex acts as a senior developer who can execute complex tasks autonomously, spawn its own sub-agents for parallel work, and deliver structured results back.

This is **the first practical layer of real agent orchestration**:

```
You (human)
    ↓
OpenClaw agent (PM — coordinates, prioritizes, communicates)
    ↓
OpenAI Codex CLI (executor — executes, codes, researches)
```

The result comes back up the chain automatically.

### 3. Cost efficiency

OpenClaw tokens are not spent while Codex is running in the detached background process. You only pay OpenClaw cost for the short turn that launches the task and the short turn that processes the result when it comes back.

Codex billing follows your Codex authentication/setup.

---

## How It Works

```
┌──────────────────┐      nohup       ┌──────────────────────┐
│   OpenClaw        │ ───────────────▶ │   run-task.py         │
│   (your agent)    │                  │   (detached process)  │
└──────────────────┘                  └──────────┬───────────┘
         ▲                                        │
         │                                        ▼
         │                             ┌──────────────────────┐
         │                             │   OpenAI Codex CLI    │
         │                             │   codex exec "task"   │
         │                             │   --experimental-json │
         │                             └──────────┬───────────┘
         │                                        │
         │                          ┌─────────────┼─────────────┐
         │                          ▼             ▼             ▼
         │                     Every 60s     On complete    On error/timeout
         │                     ┌─────────┐  ┌──────────┐  ┌────────────┐
         │                     │ 📡 ping  │  │ ✅ result │  │ ❌/⏰ notif│
         │                     │ channel  │  │ channel   │  │  channel   │
         │                     └─────────┘  └─────┬────┘  └─────┬──────┘
         │                                        │              │
         └────────────────────────────────────────┴──────────────┘
                              sessions_send → agent wakes with result
```

**Notification flow:**

1. Task launches — the originating channel gets a launch confirmation with task details
2. Every 60 seconds — a background heartbeat ping (📡 prefix) shows live status: tool calls, token count when available, current activity
3. On completion — result delivered two ways:
   - direct message to the originating channel (human sees it immediately)
   - `sessions_send` or equivalent wake path to the OpenClaw session (agent wakes up, processes the result, sends a summary)
4. Same behavior on error, timeout, or crash — you always get notified

The dual delivery ensures both you and your agent see the result.

### In Action

Real WhatsApp chat showing the full flow this project is based on — task launch, progress updates, and result delivery:

| Task Launch & Progress | Result Delivery | Agent Verification |
|:---:|:---:|:---:|
| ![Launch](docs/screenshot-demo.jpg) | ![Result](docs/screenshot-result.jpg) | ![Verification](docs/screenshot-verification.jpg) |

---

## Requirements

- [OpenClaw](https://docs.openclaw.ai) running locally (default port `18789`)
- [OpenAI Codex CLI](https://developers.openai.com/codex) (`codex`) installed and authenticated
- Python 3.10+ with `requests` (`pip install requests`)
- WhatsApp and Telegram connected to OpenClaw
- Other channels may work in principle, but may require lightweight AI-assisted adaptation in `notify_session()` / channel routing logic

---

## Security Considerations

This section addresses the same types of concerns as the original project. All behaviors described here are intentional, necessary, and declared in the skill metadata.

### Gateway Token Access

**What happens:** `run-task.py` and `scripts/openclaw_notify.py` read the OpenClaw gateway authentication token from `~/.openclaw/openclaw.json` (JSON key path: `gateway.auth.token`).

**Why it's needed:** The token authenticates HTTP API calls to the local OpenClaw gateway (`http://localhost:18789`) for two purposes:
1. Sending channel notifications (heartbeats, results, errors)
2. Waking the agent with results via `sessions_send`

**Scope:** The token is used only for localhost API calls within the current machine. It is never logged, stored in a secondary location, or transmitted to any external host or service.

**Declared in:** `SKILL.md` frontmatter `requires.config`

---

### Config Changes Required

**What's needed:** Two values in `~/.openclaw/openclaw.json` must be set by the user:

```json
{
  "gateway": { "tools": { "allow": ["sessions_send"] } },
  "tools": { "sessions": { "visibility": "all" } }
}
```

**Why:** By default, the OpenClaw HTTP API blocks `sessions_send` for safety. Allowing it enables the skill to inject results into the agent's session queue so the agent wakes up and processes the result. `tools.sessions.visibility: "all"` makes sessions addressable by session key.

**Who makes these changes:** The **user**, manually, one time during setup. The skill itself does NOT read or write `openclaw.json` (except reading the auth token).

**Scope:** Both settings affect only the local OpenClaw gateway.

**Declared in:** `SKILL.md` frontmatter `requires.config`

---

### Persistent Files Written

The skill writes to these locations:

| File | Purpose | Permissions |
|------|---------|-------------|
| `~/.openclaw/codex_sessions.json` | Session registry for task tracking and resumption | `0o600` (owner r/w only) |
| `<skill-dir>/pids/<timestamp>.pid` | PID file for the running task | Default umask |
| `/tmp/codex-<timestamp>.txt` | Final output file from Codex | Default umask |

**Session registry (`codex_sessions.json`):** Stores task labels, project directories, session IDs, output file paths, and completion status. Used to resume previous Codex sessions. Auto-created if missing. Permissions set to `0o600` on every write.

**PID files (`pids/`):** One file per running task, containing the process PID, task description, and start timestamp. Automatically deleted when the task completes or exits. Stale PID files are cleaned up on next task launch.

No data is sent to any external service by this registry/pid mechanism.

**Declared in:** `SKILL.md` frontmatter `config.stateDirs: ["~/.openclaw"]`

---

### `--dangerously-bypass-approvals-and-sandbox` Flag

**What it does:** Disables Codex CLI's approval prompts and sandbox restrictions for tool use
(file writes, bash commands, etc.).

**Why it's required:** The skill launches Codex in non-interactive `exec` mode via `nohup`,
detached from any terminal. There is no user present to answer prompts. Any prompt that
appears would stall the process indefinitely until the timeout kills it.
`--dangerously-bypass-approvals-and-sandbox` is the mechanism Codex provides for running in
fully automated/unattended mode in an externally trusted environment.

**Scope:** Grants Codex autonomy within the project directory you specify. The autonomy applies
only to the task and project directory you provide.

**Important:** Only use this skill with prompts and project directories you trust. Running
arbitrary untrusted prompts with this flag can cause unintended filesystem changes.

---

### Network Endpoints

The skill itself makes HTTP requests only to localhost:

| Endpoint | Tool | Purpose |
|----------|------|---------|
| `http://localhost:18789/tools/invoke` | `message` | Send heartbeats and results |
| `http://localhost:18789/tools/invoke` | `sessions_send` | Wake agent with task result |

Codex (the subprocess) may make external network calls as part of executing the task you give it — web search, OpenAI/Codex backend calls, API calls, etc. That is Codex's own behavior, separate from this skill's local notification behavior.

---

### Trusted Environment Requirement

This skill is designed for **single-user, local, trusted environments**:

- The machine runs OpenClaw and Codex for your own use
- You control the prompts sent to Codex
- The project directories you specify are your own

It is not designed for multi-user setups, public-facing servers, or environments where prompt content comes from untrusted sources.

---

## Installation

Clone into your OpenClaw skills directory:

```bash
git clone https://github.com/sbrin/openclaw-skill-codex-cli.git \
  ~/.openclaw/workspace/skills/codex-cli-task
```

Copy the notification helper to your scripts directory:

```bash
mkdir -p ~/.openclaw/workspace/scripts
cp ~/.openclaw/workspace/skills/codex-cli-task/scripts/openclaw_notify.py \
   ~/.openclaw/workspace/scripts/openclaw_notify.py
```

Install Python dependency:

```bash
pip install requests
```

Add the skill to your OpenClaw workspace by including `SKILL.md` in your agent's context — either via `workspace.files` in `openclaw.json` or by loading it in your bootstrap context.

---

## Configuration

### OpenClaw config (openclaw.json)

For `sessions_send` to work (required for agent wake-up on task completion), add to your `~/.openclaw/openclaw.json`:

```json
{
  "gateway": {
    "tools": {
      "allow": ["sessions_send"]
    }
  },
  "tools": {
    "sessions": {
      "visibility": "all"
    }
  }
}
```

**Why:** `sessions_send` is blocked by default in the HTTP API. These two settings enable it for localhost-only use.

### Session key format

The `--session` flag takes an OpenClaw session key, which encodes where to deliver the result.

WhatsApp example:

```text
agent:main:whatsapp:group:123456789012345678@g.us
```

Telegram thread example:

```text
agent:main:main:thread:369520
```

Find your session key in OpenClaw logs or by running the relevant sessions command/tooling.

---

## Usage

### The golden rules

**Rule 1: Always use `nohup`**

OpenClaw's `exec` tool has a 2-minute timeout. Any task longer than that gets killed. `nohup` detaches the process so it runs independently.

**Rule 2: Never inline the task in the shell command**

Complex prompts contain quotes, backticks, newlines, and markdown. These break shell argument parsing. Always write the prompt to a file first:

```bash
# ✅ Correct
cat > /tmp/codex-prompt.txt << 'EOF'
Your task here, with any quotes "or" 'symbols' you need
EOF
nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  -t "$(cat /tmp/codex-prompt.txt)" \
  ...

# ❌ Wrong — will break on quotes or newlines
nohup python3 run-task.py -t "Do 'this' and "that"" ...
```

---

### Basic task

```bash
cat > /tmp/codex-prompt.txt << 'EOF'
Create a Python script that monitors a directory for new files and prints their names with timestamps.
Save it as file-watcher.py with full error handling and a --help flag.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/file-watcher \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  > /tmp/codex-run.log 2>&1 &

echo "Launched PID $!"
```

### Research task

Use this prompt prefix to make Codex execute the research directly:

```bash
cat > /tmp/codex-prompt.txt << 'EOF'
You are being used as a Deep Research Tool. Your job is to EXECUTE the research below —
search the web thoroughly, read pages, and compile findings into a comprehensive report.
Do NOT ask for permission, do NOT propose a plan, do NOT ask clarifying questions.
Just DO the research and return the full detailed findings.

OUTPUT FORMAT: Return a comprehensive research report with all findings, organized by topic.
Include specific quotes, links, and concrete examples.

RESEARCH TASK:
Research the current landscape of open-source LLM inference servers (vLLM, Ollama, llama.cpp, TGI, etc.).
Compare performance benchmarks, supported models, deployment complexity, and community adoption.
What are practitioners actually using in production and why?
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project /tmp/codex-research \
  --session "agent:main:whatsapp:group:YOUR_GROUP_JID@g.us" \
  --session-label "LLM inference research" \
  --timeout 1800 \
  > /tmp/codex-run.log 2>&1 &
```

### Session resumption

Pick up where a previous task left off — full conversation context is preserved:

```bash
# Step 1: Run initial task (note the session ID from logs)
nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/research-prompt.txt)" \
  --project ~/projects/myapp \
  --session "SESSION_KEY" \
  --session-label "Architecture research" \
  > /tmp/codex-run.log 2>&1 &

# Step 2: Find the session ID when it completes
tail /tmp/codex-run.log
# → 📝 Session registered: 019cccab-3676-7860-8353-aaa69ba734f7

# Step 3: Resume with follow-up task
cat > /tmp/codex-implement.txt << 'EOF'
Based on your architecture research, now implement the authentication module.
Use the decisions you discussed previously.
Create the full implementation with tests.
EOF

nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-implement.txt)" \
  --project ~/projects/myapp \
  --session "SESSION_KEY" \
  --resume 019cccab-3676-7860-8353-aaa69ba734f7 \
  --session-label "Auth module implementation" \
  > /tmp/codex-run2.log 2>&1 &
```

### Long task with extended timeout

```bash
nohup python3 ~/.openclaw/workspace/skills/codex-cli-task/run-task.py \
  --task "$(cat /tmp/codex-prompt.txt)" \
  --project ~/projects/backend \
  --session "SESSION_KEY" \
  --timeout 7200 \
  > /tmp/codex-run.log 2>&1 &
```

Default timeout is 7200 seconds (2 hours). On timeout: SIGTERM → 10s grace → SIGKILL. Partial output is saved and delivered.

---

## Heartbeat Pings

While Codex works, you receive a ping every 60 seconds:

```text
📡 🟢 Codex (3min) | 1.2K tok | 8 calls | 📝 file: auth.py ✍️
📡 🟡 Codex (4min) | 1.4K tok | 8 calls | 🧠 Thinking...
📡 🟢 Codex (5min) | 2.1K tok | 12 calls | 💻 zsh -lc 'pytest tests/' ✍️
```

Status indicators:

- 🟢 Active in last 30s
- 🟡 Idle 30–120s (usually thinking/reasoning)
- 🔴 Idle 120s+ (deep reasoning or potential stall)

All background messages are prefixed with 📡 to distinguish them from your agent's replies.

---

## Session Registry

Every completed task is saved to `~/.openclaw/codex_sessions.json`:

```json
{
  "sessions": {
    "019cccab-3676-7860-8353-aaa69ba734f7": {
      "session_id": "019cccab-3676-7860-8353-aaa69ba734f7",
      "label": "Architecture research",
      "task_summary": "Research the codebase architecture...",
      "project_dir": "/home/user/projects/myapp",
      "created_at": "2026-03-08T09:08:41",
      "last_accessed": "2026-03-08T09:08:41",
      "status": "completed",
      "openclaw_session": "agent:main:whatsapp:group:...",
      "output_file": "/tmp/codex-20260308-090841.txt"
    }
  }
}
```

Use `session_registry.py` programmatically:

```python
from session_registry import list_recent_sessions, find_session_by_label

# All sessions from last 72 hours
for s in list_recent_sessions(hours=72):
    print(f"{s['session_id']}: {s['label']} ({s['status']})")

# Find by label (fuzzy match)
session = find_session_by_label("Architecture")
print(session['session_id'])
```

---

## Progress Updates from Codex

For long tasks, include this instruction in your prompt to have Codex send its own status updates:

```text
Send progress updates via bash (background, no agent wake):
python3 ~/.openclaw/workspace/skills/codex-cli-task/scripts/openclaw_notify.py \
  -g "YOUR_GROUP_JID@g.us" -m "YOUR_STATUS" --bg

Send updates at milestones: after each major step, every ~10 items processed, on errors.
Keep messages short and informational.
```

These updates also get the 📡 prefix, so your chat looks like:

```text
📡 🚀 OpenAI Codex started | Label: Refactor auth | PID: 12345
📡 🟢 Codex (1min) | 0.3K tok | 2 calls | 👁 read: auth.py
📡 Read all auth files, starting implementation
📡 🟢 Codex (2min) | 1.1K tok | 6 calls | 📝 file: jwt.py ✍️
📡 JWT module done, starting tests
📡 🟢 Codex (3min) | 2.0K tok | 11 calls | 💻 zsh -lc 'pytest tests/'
📡 All 23 tests passing, sending final report
📡 ✅ OpenAI Codex task complete! ...
```

For Telegram thread runs, `run-task.py` can also inject a temporary on-disk notification helper so Codex can send in-thread updates without exposing bot tokens in the prompt.

---

## Troubleshooting

### Task not delivering result to agent

Check that `sessions_send` is enabled in `openclaw.json`:

```json
{
  "gateway": { "tools": { "allow": ["sessions_send"] } },
  "tools": { "sessions": { "visibility": "all" } }
}
```

Verify the session key format is correct for the channel you are using.

Check logs for `sessions_send` errors:

```bash
tail -50 /tmp/codex-run.log
```

### Resume failed

If you get "Session ID not found or expired":

- Codex may no longer be able to resume that session
- Try finding the correct session ID: `cat ~/.openclaw/codex_sessions.json`
- If the session is no longer resumable, start fresh without `--resume`

### "No such file or directory: codex" when launched from cron

Cron doesn't inherit your shell's PATH. If `codex` is installed in a non-standard location, add the PATH to your crontab:

```bash
# Add at the top of crontab (crontab -e):
PATH=/opt/homebrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Or use the full path to `codex` in your cron scripts.

### Process was killed after 2 minutes

You forgot `nohup`. The `exec` tool's timeout killed it. Always use:

```bash
nohup python3 run-task.py ... > /tmp/codex-run.log 2>&1 &
```

### No heartbeat pings

Heartbeats only send if `--session` is provided and the target can be resolved from it.

### Check running tasks

```bash
ls ~/.openclaw/workspace/skills/codex-cli-task/pids/
# → 20260308-090841-Research-on-X.pid
```

To check if a task is still running:

```bash
cat ~/.openclaw/workspace/skills/codex-cli-task/pids/*.pid
ps aux | grep <PID>
```

---

## Channel Support

This skill is implemented for **WhatsApp and Telegram** notification flows.

- **WhatsApp:** launch, heartbeat, finish delivery, agent wake flow
- **Telegram:** thread-aware routing, including thread-safe delivery improvements in recent versions

Other channels (Slack, Discord, Signal, etc.) may work in principle if OpenClaw supports them, but may require lightweight adaptation in `notify_session()` and channel-specific routing parameters in `run-task.py`.

---

## File Structure

```text
openclaw-skill-codex-cli/
├── README.md              # This file
├── LICENSE                # MIT
├── SKILL.md               # OpenClaw skill definition (loaded into agent context)
├── agents/
│   └── openai.yaml        # UI metadata
├── run-task.py            # Main async runner
├── run-task.sh            # Minimal shell wrapper
├── session_registry.py    # Session metadata storage and retrieval
├── scripts/
│   └── openclaw_notify.py # Notification helper (for Codex to send progress updates)
└── examples/
    └── README.md          # Detailed usage examples and patterns
```

---

## License

MIT — see [LICENSE](LICENSE).

---

## Credits

Forked from [openclaw-skill-claude-code](https://github.com/VsevolodUstinov/openclaw-skill-claude-code).

*Built on top of [OpenClaw](https://docs.openclaw.ai) and [OpenAI Codex](https://developers.openai.com/codex).*
