# 🎯 Roundtable

**Adaptive multi-model AI debate orchestration for OpenClaw.**

Roundtable spawns a panel of different AI models — Claude, GPT, Gemini, Grok — to debate your topic across multiple rounds, then synthesizes the result via a neutral model that didn't participate.

What makes it different: a **Meta-Panel** of 4 premium models first designs the optimal *workflow* for your specific task — parallel debate, sequential pipeline, or hybrid — before any panelist speaks.

---

## Quickstart

```
roundtable Should we migrate our monolith to microservices?
roundtable --quick What's the best approach to cold email outreach?
roundtable --redteam Our startup's business model
roundtable --build Design a rate-limiting system for a public API
roundtable --vote Redis vs PostgreSQL for session storage
```

### Presets

| Preset | Command | When to use |
|--------|---------|-------------|
| ⚡ **Fast** | `--quick` | Quick opinion, informal topic, no need for deep critique |
| ⚖️ **Balanced** | *(default)* | Most topics — meta-panel + 2 rounds + neutral synthesis |
| 🔒 **High-Confidence** | `--validate` | High-stakes decisions, publishing, final architecture choices |
| 💰 **Budget** | `--panel budget` | No Blockrun configured — uses only Anthropic + OpenAI fallbacks |
| 🔴 **Adversarial** | `--redteam` | Stress-test an idea, product, or plan against real attacks |

---

## Modes

| Flag | What it does |
|------|-------------|
| *(none)* | Auto-detects best mode |
| `--debate` | Parallel opinions, cross-critique, synthesis |
| `--build` | Sequential: implement → review → integrate |
| `--redteam` | Adversarial: Attacker / Defender / Auditor |
| `--vote` | 4-way vote with tie-breaker |
| `--quick` | Skip meta-panel, 1 round, fast output |
| `--validate` | Add Round 3 where agents validate the synthesis |
| `--panel m1,m2,m3` | Manual panel — skip meta-panel entirely |
| `--no-search` | Skip web search (pure reasoning mode) |

---

## How it works

```
Step -1 → Create Discord thread for this roundtable
Step 0  → Web search: all agents get current context
Step 0b → Meta-panel (4 premium): designs optimal workflow
Step 1  → Detect mode (if not flagged)
Step 2  → Spawn 4 panel agents as persistent thread-bound sessions
          Round 1 (independent positions) + Round 2 (cross-critique)
Step 3  → Consensus scoring (formal 1–5 matrix)
Step 4  → Round 3 validation (--validate only)
Step 5  → Synthesis via neutral thread-bound model
Step 6  → Persist to ~/clawd/memory/roundtables/
```

Each roundtable gets its own thread with 4 live agents — you can keep talking to them after the rounds end.

---

## Requirements

**Full experience (recommended):** Blockrun configured at `localhost:8402`
→ Provides: Claude Opus 4.6, GPT-5.3 Codex, Gemini 3.1 Pro, Grok 4 via unified proxy

**Without Blockrun:** Skill degrades gracefully to available providers:
- `anthropic` provider → Claude Opus/Sonnet as fallback
- `openai-codex` provider → GPT-5.3 Codex as fallback

---

## Output format

Every roundtable produces a structured synthesis:

```
🎯 ROUNDTABLE: [topic]
📋 Panel: [models] | Mode: [mode] | Rounds: [N]

📊 CONSENSUS (XX%)
⚡ DIVERGENCES
🔍 BLIND SPOTS
🏆 RECOMMENDATION
💡 OUTLIER
⚠️ RED FLAGS
📈 ACTION PLAN
🔧 META
```

Results are also saved to `~/clawd/memory/roundtables/YYYY-MM-DD-[topic].json`.

---

## Cost estimate

| Mode | Approx. spawns | Estimated cost |
|------|---------------|----------------|
| `--quick` | 3–4 | ~$0.10–0.30 |
| `--debate` (full) | 9–11 | ~$0.50–1.50 |
| `--build` | 5–7 | ~$0.30–0.80 |
| `--validate` | +3 | +$0.20–0.50 |

Costs depend on topic length and active providers.

---

## Example output

See [`examples/`](./examples/) for real completed roundtable outputs.

> **Topic**: Should we use AI agents to replace manual QA testing?
>
> **📊 CONSENSUS (58%)** — All agents agreed automated agents excel at regression testing; all disagreed about edge-case coverage.
>
> **⚡ DIVERGENCES** — GPT-5.3 Codex argued for full automation now; Opus argued hybrid human+AI is safer for 3+ years; Grok challenged the premise entirely ("QA is the wrong question — design for testability first").
>
> **🏆 RECOMMENDATION** — Adopt AI agents for regression and smoke testing immediately. Keep human QA for exploratory and acceptance testing until hallucination rates drop below 2%.

---

## Configuration

Customize panels in `panels.json` — each mode (`debate`, `build`, `redteam`, `vote`) has its own model list, roles, and fallbacks. Edit to match your available providers.

---

Built with [OpenClaw](https://openclaw.ai) · [View on ClawHub](https://clawhub.ai/JimmyClanker/roundtable-adaptive)
