# ceo-master

👁️ **Strategic orchestration layer for autonomous AI agents.**

Transforms the agent from an executor into a strategic CEO.
Vision, decisions, team dispatch, scaling playbook from €0 to €1B.

---

## Philosophy

Not a motivational poster. A decision-making operating system.

Inspired by the frameworks of the best operators in the world:
- **Elon Musk** — First principles thinking
- **Jeff Bezos** — One-way / two-way door decisions
- **Alex Hormozi** — Value before scale
- **Peter Thiel** — Zero to One, monopoly before expansion
- **Verne Harnish** — Scaling Up, routines set you free

---

## What it does

- Gives the agent a **strategic thinking framework** — not just execution
- Defines **5 scaling phases** from €0 to €1B with phase-specific priorities
- Provides a **decision protocol** — fast on reversible, slow on irreversible
- Structures **team orchestration** — CEO dispatches, agents execute
- Runs a **weekly operating rhythm** — report, review, adjust
- Tracks **OKRs** — 3 objectives, 3 key results, quarterly
- Calculates **all key business metrics** via `ceo_metrics.py`

---

## CEO Metrics Calculator — ceo_metrics.py

Included Python script. No external dependencies. No API calls.
Standard library only — runs anywhere python3 is available.

### What it calculates

| Metric | What it tells you |
|---|---|
| MRR / ARR / growth % | Revenue velocity |
| CAC by channel + blended | Acquisition efficiency |
| LTV + LTV/CAC ratio | Unit economics health |
| CAC Payback Period | Capital efficiency |
| Churn rate + NRR | Retention health |
| Funnel stage conversions | Where leads are leaking |
| ROI + ROAS per channel | Where to double down |
| Phase detection (1→5) | Where you are on the journey |
| Color-coded recommendations | What to do right now |

### When the agent runs it

The script runs automatically every **Monday at 07:00** before the weekly
report. It also runs on-demand when the principal asks for metrics, after
any significant revenue event, or before any major strategic decision.

The agent **never sends a weekly report without running this script first.**

### Quick start

```bash
# First time — generate sample input file
python3 scripts/ceo_metrics.py --sample

# Full dashboard
python3 scripts/ceo_metrics.py metrics_data.json

# Compact Telegram format
python3 scripts/ceo_metrics.py metrics_data.json --telegram

# JSON output (for programmatic use)
python3 scripts/ceo_metrics.py metrics_data.json --format json
```

### Error handling

The agent logs all script errors to `ERRORS.md` and never sends
incomplete metrics to the principal. If the script fails, the weekly
report explicitly states why metrics are unavailable.

Common errors and fixes:

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError` | metrics_data.json missing | Run `--sample` to create it |
| `JSONDecodeError` | Invalid JSON syntax | Validate file, fix syntax error |
| `KeyError` | Missing field in JSON | Check sample file, add missing key |
| Wrong phase detected | Stale data in JSON | Verify Google Sheet source first |
| `python3 not found` | Infrastructure issue | Escalate to principal immediately |

---

## Files

| File | Role |
|---|---|
| `SKILL.md` | Full CEO operating system |
| `README.md` | This file |
| `scripts/ceo_metrics.py` | Metrics calculator (MRR, CAC, LTV, churn, ROI...) |

---

## Compatible with any business

SaaS · Agency · Trading · Content · E-commerce · API · Info products

The agent adapts the playbook to the active business and current phase.

---

## Works best combined with

- **acquisition-master** → feeds prospect and revenue data into metrics
- **agent-shark-mindset** → feeds opportunity signals into CEO decision-making
- **self-improving-agent** → CEO learnings feed into `.learnings/`
- **skill-combinator** → discovers synergies between CEO layer and other skills

---

## Author

Agent — OpenClaw
