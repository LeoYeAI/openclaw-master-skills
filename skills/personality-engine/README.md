# Personality Engine

Six-system behavior engine that makes any OpenClaw agent feel alive — opinions, silence, timing, memory, engagement adaptation, and ambient pings.

## Install

```bash
clawhub install personality-engine
```

## Quick Start

```python
from personality_engine.engine import PersonalityEngine

engine = PersonalityEngine(user_id="user@example.com")

# Pass triggers through the engine
should_send, msg = await engine.process_trigger(
    trigger_type="cross_platform",
    raw_message="Divergence: Kalshi 52%, Poly 48%",
    market_data={"spread": 4.0},
    urgency_context={},
)

if should_send:
    send_message(msg.content)
```

## The 6 Systems

| System | What It Does |
|--------|-------------|
| **Editorial Voice** | Injects opinions that vary by trigger type and market state |
| **Selective Silence** | Knows when NOT to talk — skips flat days, stale data, noise |
| **Variable Timing** | Urgency scoring (0-1) with time-of-day delivery thresholds |
| **Micro-Initiations** | Unprompted ambient pings ("Quiet week. Enjoy it.") |
| **Context Buffer** | Daily memory with back-references to earlier messages |
| **Response Tracker** | Adapts to user engagement patterns over time |

## Domain-Agnostic

Default configuration is tuned for prediction market trading, but every system adapts to any domain: personal assistants, DevOps monitors, sales CRM, content management. Swap voice pools, thresholds, and micro-initiation conditions.

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including per-system architecture, customization guide, integration steps, and domain adaptation table.

## Part of the OpenClaw Prediction Market Trading Stack

```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

**Author**: KingMadeLLC
