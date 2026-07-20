# SHIFT — Multi-Identity Delegation Skill

**One agent. Many specialists. One conversation.**

SHIFT turns a single OpenClaw agent into a multi-identity system — a master personality (the assistant) that delegates tasks to specialized sub-identities, each powered by a different AI model.

> **TL;DR:** You talk to the assistant. the assistant decides if a task needs a specialist. If it does, the assistant delegates to Codex (coding), Researcher (analysis), or Runner (quick tasks), gets their result, and speaks it back in his own voice. You get one seamless conversation with the quality of multiple specialists.

---

## Installation

```bash
clawhub install shift
```

Or manually:
```bash
git clone <repo> ~/.openclaw/skills/shift
```

After installation, run the setup script:
```bash
bash ~/.openclaw/skills/shift/scripts/setup.sh
```

---

## Quick Configuration

After installation, edit `~/.openclaw/workspace/.shift/config.yaml`:

```yaml
personas:
  codex:
    model: openai-codex/gpt-5.3-codex   # ← your coding model
  researcher:
    model: openai/gpt-5.4               # ← your research model
  runner:
    model: minimax/MiniMax-M2.5-Lightning  # ← your fast model
```

SHIFT is **model-agnostic** — it works with any model from any provider. Configure it with whatever you have access to.

---

## Recommended Models

These are tested configurations that work well:

### Budget-Conscious

| Persona | Model | Notes |
|---|---|---|
| Codex | `openai/gpt-5.4` | Good general-purpose coding |
| Researcher | `openai/gpt-5.4` | Reuse same model if needed |
| Runner | `minimax/MiniMax-M2.5-Lightning` | Fast, cheap |

### Performance-Focused

| Persona | Model | Notes |
|---|---|---|
| Codex | `openai-codex/gpt-5.3-codex` | Best for code |
| Researcher | `openai/gpt-5.4-pro` | Deeper analysis |
| Runner | `minimax/MiniMax-M2.7` | Fast + reasoning |

### Mixed Providers

| Persona | Model | Notes |
|---|---|---|
| Codex | `anthropic/claude-sonnet-4-5` | Excellent code + reasoning |
| Researcher | `openai/gpt-5.4` | Good all-rounder |
| Runner | `minimax/MiniMax-M2.5-Lightning` | Fast |

---

## How It Works

```
User: implement a binary search tree in Python
         ↓
    the assistant (master) routes → Codex
         ↓
    Codex writes code
         ↓
    Codex may consult Researcher for approach
         ↓
    Codex writes OUTBOUND.md
         ↓
    the assistant synthesizes → speaks in the assistant's voice
         ↓
User: here's the implementation... + plain-English explanation
```

---

## Commands

```
/delegate <persona> <task>
  Explicitly delegate a task to a specific sub-identity.
  Example: /delegate codex write a REST API in FastAPI

/shift mode hidden|transparent
  Toggle delegation visibility.
  - hidden: seamless (default) — you only see the assistant's response
  - transparent: educational — you see when the assistant delegates and consults

/shift fastpath on|off
  Toggle conservative fast-path mode.
  - on (default): only trivial greetings bypass delegation
  - off: master handles everything

/shift status
  Show active personas and current cost budget status.
```

---

## Sub-Identities

### Codex (Coding Specialist)

**When it triggers:** code, function, implement, debug, refactor, API, script, error, etc.

**What it does:**
- Writes clean, working code
- Debugs with root-cause analysis
- Explains code in plain English
- May consult Researcher for approach context

**Model recommendation:** `openai-codex/gpt-5.3-codex` or any coding-specialized model

### Researcher (Analysis Specialist)

**When it triggers:** research, analyze, compare, explain, evaluate, what is, how does, etc.

**What it does:**
- Structured analysis with key insights
- Pros/cons with nuanced conclusions
- Multi-source synthesis
- Surface tradeoffs and context

**Model recommendation:** `openai/gpt-5.4` or any strong reasoning model

### Runner (Quick Tasks)

**When it triggers:** quick, simple, just, check, look up, what is, define, remind me, etc.

**What it does:**
- Fast, concise answers
- Quick lookups and definitions
- Reminders and follow-ups
- Escalates to master if task is too complex

**Model recommendation:** `minimax/MiniMax-M2.5-Lightning` or any fast model

---

## Consultation (Sub-Identity ↔ Sub-Identity)

Codex can consult Researcher when it needs specialized context:

```
User: build a trading bot that uses Twitter sentiment
         ↓
    Codex: I need context on sentiment analysis approaches
         ↓
    Codex consults Researcher
         ↓
    Researcher: use VADER + FinBERT hybrid, weighted toward FinBERT
         ↓
    Codex implements with that context
```

Consultation is **always visible** to the user (not gated by display mode). This is intentional — it shows the system being thorough.

---

## Cost Management

SHIFT tracks delegation spend per rolling hour:

```yaml
costManagement:
  enabled: true
  costBudgetPerHour: 2.00    # USD — master handles everything above this
  trackOnly: false           # true = only log, don't enforce
  alertThreshold: 0.75      # warn when 75% of budget used
```

When the budget is exceeded, the assistant handles all tasks directly without delegating. This prevents unexpected bills.

To check current spend:
```
/shift status
```

---

## Display Modes

### Hidden (Default — Seamless)

```
User: write a BST in Python
[Assistant]: Here's a binary search tree implementation... (+ explanation)
```

### Transparent (Educational)

```
User: write a BST in Python
[Assistant] → [Codex] working on this...
[Assistant] ← [Codex] implementation complete.
[Assistant]: Here's a BST implementation... (+ explanation)
```

Consultation is always visible in both modes.

---

## Adding a New Persona (v1 Extendable to 5)

Want to add a fourth sub-identity? Here's how:

1. Create `personas/MYNEW.yaml` from the template:
   ```bash
   cp shift/personas/CODEX.yaml shift/personas/ANALYST.yaml
   ```

2. Edit `config.yaml`:
   ```yaml
   personas:
     analyst:
       enabled: true
       model: your-model-here
       personaFile: personas/ANALYST.yaml
       # ... configure routing, timeout, consults
   ```

3. Update MAX personas check (code enforces 5 max).

---

## How SHIFT Different from OpenClaw Multi-Agent?

| | OpenClaw Multi-Agent | SHIFT |
|---|---|---|
| Routing | by channel (different bots) | by task (same conversation) |
| Memory | siloed per agent | shared context bridge |
| Identity | different bots | one master unifies |
| Context | no continuity | context flows between layers |
| Cost control | none | delegation budget |

---

## Privacy

SHIFT does **NOT**:
- Exfiltrate data to external services beyond your configured model providers
- Store API keys (reads your OpenClaw config)
- Share context between different users

SHIFT does:
- Run entirely within your OpenClaw gateway
- Store delegation metadata locally
- Write session context files to your workspace

## ⚠️ Security Considerations

### What Gets Transmitted

When delegation is enabled, the following are sent to your configured model providers:
- Your message and conversation history (last N turns, controlled by `contextBridge.historyTurns`)
- Active file contents and MEMORY.md excerpts in scope
- Delegation metadata (runId, timestamps, persona)

**You control which model providers are used.** SHIFT uses your OpenClaw model config — it has no own credentials. Review your provider's data handling policy.

### Data Exposure

If your workspace files or MEMORY.md contain secrets (API keys, credentials), delegating tasks that reference those files will transmit that content to your model provider.

**Mitigations:**
- Do not delegate tasks referencing sensitive file paths
- Set `contextBridge.historyTurns` to a low number (5 or less)
- Use `costManagement.trackOnly: true` to evaluate before enforcing
- Use trusted or self-hosted models for sensitive work

### Setup Script

`scripts/setup.sh` only creates local directories and copies files. No network calls, no privilege escalation.

---

## Troubleshooting

**Sub-identity not triggering when expected:**
- Check keyword matching — increase `minConfidence` or add more keywords
- Runner requires `requireExplicit: true` — it only triggers on keyword match

**Delegation happening too often:**
- Set `fastPath: off` to have master handle everything
- Or tune keyword lists to be more selective

**Budget being hit too quickly:**
- Lower `costBudgetPerHour`
- Set `trackOnly: true` to monitor before enforcing

**Consultation not working:**
- Check that target persona is in `consults` list
- Check that target persona is NOT in `consultsNever` list
- Check consultation timeout isn't too short

---

## Files

```
~/.openclaw/workspace/.shift/
├── config.yaml           ← your configuration
├── cost-tracking.json    ← cost tracking (auto-managed)
└── sessions/
    └── <runId>/
        ├── INBOUND.json      ← delegation input
        ├── CONTEXT.md        ← project context
        ├── OUTBOUND.md       ← sub-identity result
        └── ESCALATE.md       ← Runner escalation (if any)
```
