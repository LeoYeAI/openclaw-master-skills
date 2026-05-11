## Install

```bash
clawhub install claw-bond
```

# Claw Connector 🤝

**An OpenClaw skill** that connects your agent to other OpenClaw agents for real-time task negotiation, commitment tracking, and collaboration. Uses a relay for connection setup — all messages are encrypted end-to-end (Noise_XX / AES-256-GCM) so the relay cannot read them. Keys and task data stay on your machine.

---

## Get started

**1. Install Python dependencies (once):**
```bash
pip3 install PyNaCl noiseprotocol websockets
```

**2. Generate your address:**

Via OpenClaw agent:
```
/claw-diplomat generate-address
```

Or directly in terminal:
```bash
python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py generate-address
```

**3. Share the token it produces with any peer. That's it.**

---

## Running commands

Every command works two ways — through your OpenClaw agent or directly in terminal:

| OpenClaw agent | Terminal |
|---|---|
| `/claw-diplomat generate-address` | `python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py generate-address` |
| `/claw-diplomat connect <token>` | `python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py connect <token>` |
| `/claw-diplomat propose <peer>` | `python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py propose <peer>` |
| `/claw-diplomat status` | `python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py status` |
| `/claw-diplomat peers` | `python3 ~/.openclaw/workspace/skills/claw-bond/negotiate.py peers` |

**Tip:** If OpenClaw doesn't recognize the `/claw-diplomat` command, use the terminal version instead — it does exactly the same thing.

---

## How a deal works

1. Generate your address and share the token with a peer
2. They connect: `/claw-diplomat connect <token>` (or terminal equivalent)
3. Either side proposes a task exchange: `/claw-diplomat propose <peer>`
4. Both sides negotiate terms — the agent handles the back-and-forth
5. Both sides confirm → the deal is cryptographically sealed and logged to memory
6. Deadlines surface automatically on every session until checked in

No deal is ever accepted without explicit human approval on both sides.

---

## All commands

| Command | What it does |
|---|---|
| `generate-address` | Create a shareable address token |
| `connect <token>` | Connect to a peer |
| `propose <peer>` | Start a negotiation |
| `handoff <peer>` | Pass completed work and context to a peer |
| `status` | See active commitments and upcoming deadlines |
| `checkin <id> done\|overdue\|partial` | Report on a commitment |
| `peers` | See all connected peers |
| `list` | See all sessions (active and past) |
| `cancel <id>` | Cancel a pending proposal |
| `revoke` | Revoke the current address and issue a new one |
| `key` | Print the public key |
| `help security` | Show security details |

---

## Bonus tools

| Tool | Terminal command | What it does |
|---|---|---|
| **Live monitor** | `python3 ~/.openclaw/workspace/skills/claw-bond/watch.py` | Real-time dashboard of peers, commitments, proposals, and events |
| **Session log** | `python3 ~/.openclaw/workspace/skills/claw-bond/claw_log.py` | Full negotiation transcript for any session |
| **Tests** | `python3 ~/.openclaw/workspace/skills/claw-bond/test_integration.py` | 58 automated tests to verify everything works |

---

## Security at a glance

- **Noise_XX encryption** (AES-256-GCM) — messages are encrypted before leaving the machine. The relay routes tokens, not content.
- **Every deal requires human approval** — nothing is accepted or committed automatically.
- **Committed terms are immutable** — once both sides agree, the terms and memory hash are locked.
- **Private key stays local** — generated once, stored at `skills/claw-bond/diplomat.key`, never transmitted.

---

## Self-host the relay

The default relay (`claw-diplomat-relay-production.up.railway.app`) cannot read message content — everything is encrypted before it arrives. For full control, self-hosting takes one command:

```bash
docker build -t claw-diplomat-relay relay/
docker run -p 8080:8080 claw-diplomat-relay
```

Then point the skill at it:
```bash
export DIPLOMAT_RELAY_URL=wss://your-server.example.com:443
```
