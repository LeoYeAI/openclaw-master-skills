# Setting Up Claw Connector
### A plain-English guide for users — no technical background needed.

> **Note for Claude Code users:** The other files in this folder (`SKILL.md`, hook handlers, Python scripts) are instructions and code for your AI agent. This file is for **you** — the human — and tells you exactly what to run in your terminal to get everything working.

---

## What you'll need

- A Mac, Linux machine, or Windows with WSL2
- Python 3.10 or later (check: `python3 --version`)
- OpenClaw installed and running

---

## Step 1 — Install Python dependencies

Open your terminal and run this once:

```bash
pip3 install PyNaCl noiseprotocol websockets
```

This installs the three libraries the skill needs (encryption, the Noise protocol, and WebSockets). It's safe — all are standard, well-known packages on PyPI.

---

## Step 2 — Install the skill into your workspace

Copy the skill files into your OpenClaw workspace. Your workspace folder should end up looking like this:

```
your-workspace/
├── SOUL.md
├── MEMORY.md
├── HEARTBEAT.md
├── skills/
│   └── claw-bond/
│       ├── SKILL.md
│       ├── negotiate.py
│       └── listener.py
└── hooks/
    ├── diplomat-bootstrap/
    │   ├── HOOK.md
    │   └── handler.ts
    ├── diplomat-heartbeat/
    │   ├── HOOK.md
    │   └── handler.ts
    ├── diplomat-gateway/
    │   ├── HOOK.md
    │   └── handler.ts
    └── shared/
        └── parse-memory.ts
```

If you installed via ClawHub, this is done automatically. If you're installing manually, copy the files into the paths shown above.

---

## Step 3 — First run

Start a conversation with your agent. The first time you use the skill, your agent will generate your secure identity key automatically. You should see:

```
👋 Setting up Claw Connector for the first time...
Generating your secure identity key... ✓
```

Two files will be created in `skills/claw-bond/`:
- `diplomat.key` — your private key (never shared, never transmitted)
- `diplomat.pub` — your public key (safe to share)

---

## Step 4 — Generate your Diplomat Address

Tell your agent:
```
/claw-diplomat generate-address
```

Your agent will connect to the relay server and create a shareable address token. It looks like a long string of letters and numbers. **Copy it and share it with whoever you want to negotiate tasks with.**

---

## Step 5 — Connect with a peer

When someone shares their Diplomat Address with you, tell your agent:
```
/claw-diplomat connect <paste their token here>
```

Your agent will verify their identity cryptographically and confirm the connection.

---

## Step 6 — Propose a task

Once connected, start a negotiation:
```
/claw-diplomat propose <their name>
```

Your agent will ask you:
1. What you'll take on
2. What you're asking them to do
3. The deadline

You confirm before anything is sent. They confirm before anything is agreed. No auto-accepting.

---

## Useful commands (tell these to your agent)

| Say this | What happens |
|---|---|
| `/claw-diplomat status` | See all your active commitments and deadlines |
| `/claw-diplomat peers` | See who you're connected with |
| `/claw-diplomat checkin <id> done` | Mark a commitment as complete |
| `/claw-diplomat checkin <id> overdue` | Report something as overdue |
| `/claw-diplomat handoff <name>` | Pass completed work + context to a peer |
| `/claw-diplomat list` | See all sessions (active and past) |
| `/claw-diplomat revoke` | Revoke your current address and generate a new one |

---

## Optional: Use your own relay server

By default the skill uses a community relay (`claw-diplomat-relay-production.up.railway.app`). The relay **cannot read your messages** — everything is encrypted before it leaves your machine — but if you want full control, you can self-host:

```bash
# Requires Docker
docker build -t claw-diplomat-relay relay/
docker run -p 8080:8080 claw-diplomat-relay
```

Then set this environment variable before starting OpenClaw:
```bash
export DIPLOMAT_RELAY_URL=wss://your-server.example.com:443
```

---

## Security — what this skill can and cannot do

| ✅ It CAN | ❌ It CANNOT |
|---|---|
| Read your `MEMORY.md` commitments | Read your passwords, API keys, or secrets |
| Write new commitment entries to `MEMORY.md` | Modify `SOUL.md` or `AGENTS.md` |
| Connect to the declared relay server | Connect to any other external server |
| Generate and store a local keypair | Send your private key anywhere |
| Spawn a background listener for inbound connections | Execute any content sent by peers |

**About the background listener:** When OpenClaw starts, the skill launches a small background process (`listener.py`) that waits for inbound peer connections via the relay. It runs with a minimal set of environment variables — only `DIPLOMAT_*` settings and the bare essentials for Python. Your API keys, cloud credentials, and other secrets in your environment are **not** passed to it.

**About context injection:** The bootstrap hook reads your active commitments from `MEMORY.md` (up to 2,500 characters) and injects them into your agent's session at startup. This is how your agent knows what you've committed to. Only your own data is injected — nothing from peers.

---

## Troubleshooting

**"Missing dependency" error**
```bash
pip3 install PyNaCl noiseprotocol websockets
```

**Relay unreachable**
Check your internet connection. The relay is at `claw-diplomat-relay-production.up.railway.app`. You can verify it's up:
```bash
curl https://claw-diplomat-relay-production.up.railway.app/myip
```
Should return your IP address. If it doesn't, try again in a few minutes or set up your own relay.

**Listener not starting**
Check that `python3` is in your PATH:
```bash
python3 --version
```
Should show 3.10 or higher.

**Connection mismatch (peer key changed)**
Ask your peer to run `/claw-diplomat generate-address` and share their new token. Then reconnect with `/claw-diplomat connect <new token>`.

---

*Claw Connector v1.0.0 — Your agent. Their agent. One deal.*
