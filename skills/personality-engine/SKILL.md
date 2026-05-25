---
name: Personality Engine
description: "Six-system behavior engine that makes any OpenClaw agent feel alive. Editorial voice injects opinions. Selective silence knows when NOT to talk. Variable timing scores urgency with time-of-day awareness. Micro-initiations send ambient pings. Context buffer enables back-references to earlier messages. Response tracker adapts to engagement patterns. Domain-agnostic — works with trading agents, personal assistants, DevOps monitors, or any proactive agent. Part of the OpenClaw Prediction Market Trading Stack with default trading configuration."
---

# Personality Engine — 6-System Behavior Framework

**Goal**: Make any AI agent feel *alive* — opinions, awareness, judgment, memory, timing sense, and engagement sensitivity. Works with trading agents, notification systems, personal assistants, or any proactive agent. Not just data delivery.

## Architecture Overview

```
Trigger fires → engine.py orchestrator
              ↓
         selective_silence (should we stay silent?)
              ↓
         urgency_compute (how urgent is this 0.0-1.0?)
              ↓
         engagement_modifier (adjust for user response patterns)
              ↓
         variable_timing (schedule delivery based on urgency + time of day)
              ↓
         context_buffer (add back-references to earlier messages today)
              ↓
         editorial_voice (inject personality / opinions)
              ↓
         dedup (avoid repeats within rolling window)
              ↓
         send → iMessage (or other transport)
```

Plus two ambient systems:
- **micro_initiations**: Unprompted pings when conditions are met (quiet market, good streak, absence detected)
- **response_tracker**: Monitors engagement; adjusts urgency + suggests tuning

---

## System 1: Editorial Voice — Opinion Injection

**What**: Each trigger type gets a personality — opinions that vary based on market state, portfolio P&L, signal confidence.

**Per-trigger voice pools**:

### cross_platform (Kalshi vs Polymarket divergence)
- **Bullish divergence (>5%)**: "Big divergence. One of these markets is wrong."
- **Mild divergence (2-5%)**: "Mild divergence. Nothing screaming yet."
- **Stale divergence (6+ hours old)**: "Divergence is stale — markets may have already repriced."

### portfolio (user's holdings performance)
- **+15% or better**: "Good day. Portfolio's running."
- **+5% to +15%**: "Solid gains. Steady hand."
- **-5% to +5%**: "Flat day. Markets are grinding."
- **-5% to -15%**: "Rough patch. Check your stops."
- **-15% or worse**: "Heavy day. Buckle up for volatility."

### x_signals (social signal scanner)
- **Confidence ≥0.85 + matched position**: "Strong signal. This feels real."
- **Confidence 0.70-0.85**: "New signal on [topic]. Worth watching."
- **Confidence <0.70**: "Noise signal. Low confidence."

### edge (Kalshi edge detection)
- **Edge >3%**: "Fat edge. Worth a deep look."
- **Edge 1-3%**: "Mild edge. Keeping it on radar."
- **Edge <1%**: "Thin edge. Not worth the friction."

### morning (daily brief)
- **Monday**: "New week. Here's the lay of the land."
- **Friday**: "Friday rundown. What matters before the close."
- **Other**: "Daily digest."

### conflicts (overlapping triggers same hour)
- **2+ conflicts**: "Tomorrow's a mess. Multiple overlaps."
- **Lighter**: "Heads up — couple things hitting together."

**Customization point**: Add trigger types by extending the `VOICE_POOLS` dict in `editorial_voice.py`. Each entry maps `(trigger_name, market_state)` → list of opinion strings.

---

## System 2: Selective Silence — Knowing When NOT to Talk

**What**: Not every trigger fire deserves a message. Silent skips are explicit: "Skipped the brief — nothing worth your attention."

**Content quality checks per trigger**:

- **morning_is_boring**: If market vol <0.5%, no divergences, no edges → skip
- **divergence_is_stale**: If last message on this topic was <3 hours ago AND spread hasn't moved >0.5% → skip
- **signals_are_noise**: If all signals have confidence <0.65 AND no position matches → skip
- **edge_is_weak**: If all edges <1% → skip
- **portfolio_is_flat**: If daily P&L is -2% to +2% AND no major position changes → skip

**Silence cadence**:
- Max 1 silence message per day per user
- Only for *expected* triggers (morning, portfolio check, etc.)
- Never silence micro-initiations (those *are* the value)
- When silent, send explicit message: `"Skipped the brief — nothing worth your attention."`

**Customization point**: Adjust thresholds in `selective_silence.py`:
```python
SILENCE_THRESHOLDS = {
    'vol_floor': 0.5,           # % vol threshold for morning silence
    'divergence_age_limit': 3,  # hours
    'signal_confidence_floor': 0.65,
    'edge_floor': 1.0,          # %
    'portfolio_flat_range': 2.0 # % P&L range
}
```

---

## System 3: Variable Timing — Urgency Scoring + Time-of-Day Awareness

**What**: Schedule message delivery based on urgency (0.0-1.0) and time of day. A mild divergence at 6 AM gets sent immediately (threshold 0.9 before 7 AM). Same divergence at 10 PM gets held (threshold 0.35).

**Per-trigger urgency base**:
- **cross_platform**: (spread / 10%) * 0.6, capped at 1.0
  - 5% spread = 0.3 urgency
  - 10% spread = 0.6 urgency
  - 15%+ spread = 1.0 urgency
- **portfolio**: (abs(daily_pnl) / 10%) * 0.7, capped at 1.0
  - ±5% P&L = 0.35 urgency
  - ±15% P&L = 1.0 urgency
- **x_signals**: (confidence * 0.8) + (position_match ? 0.2 : 0), capped at 1.0
  - Confidence 0.85 + matched = 0.88 urgency
  - Confidence 0.70 + no match = 0.56 urgency
- **edge**: (edge_size / 5%) * 0.8, capped at 1.0
  - 2% edge = 0.32 urgency
  - 5% edge = 0.8 urgency
- **meeting**: (1.0 - minutes_away / 120) capped at 1.0
  - 30 min away = 0.75 urgency
  - 5 min away = 0.96 urgency

**Time-of-day delivery thresholds**:
- **Before 7 AM**: threshold 0.90 (almost everything gets sent)
- **7 AM - 9 AM**: threshold 0.75 (morning crunch — moderate bar)
- **9 AM - 10 PM**: threshold 0.45 (daytime — lower bar, let alerts through)
- **10 PM - 11 PM**: threshold 0.35 (wind-down — only high urgency)
- **11 PM - 12 AM**: threshold 0.85 (late night — back to high bar)
- **12 AM - 7 AM**: threshold 0.90 (sleep time — very high bar)

**Modifiers**:
- **Weekend**: +0.10 urgency (weekends are boring, lower bar for engagement)
- **Clustering prevention**: If message sent <10 min ago, -0.20 urgency (space out messages)
- **Daily fatigue**: If 10+ messages today, +0.20 urgency threshold (user tired, fewer but higher-quality alerts)
- **Random jitter**: ±5% urgency (avoid machine-like precision)

**Send logic**:
```
adjusted_urgency = base_urgency * engagement_modifier ± jitter
if adjusted_urgency >= time_of_day_threshold:
    schedule_send(now or delayed based on urgency)
else:
    hold for next trigger
```

**Customization point**: Modify `TIME_OF_DAY_THRESHOLDS` and modifier constants in `variable_timing.py`:
```python
TIME_OF_DAY_THRESHOLDS = {
    (0, 7): 0.90,    # midnight - 7 AM
    (7, 9): 0.75,    # 7 - 9 AM
    (9, 22): 0.45,   # 9 AM - 10 PM
    (22, 23): 0.35,  # 10 - 11 PM
    (23, 24): 0.85,  # 11 PM - midnight
}
MODIFIERS = {
    'weekend': 0.10,
    'clustering_prevention': 0.20,
    'daily_fatigue_step': 0.20,
}
```

---

## System 4: Micro-Initiations — Ambient Awareness Pings

**What**: Unprompted messages when conditions are met. Not triggered by market events — triggered by meta-state.

**Pools**:

| Pool | Trigger | Message |
|------|---------|---------|
| QUIET_MARKET | Vol <0.3% all day, no trades | "Quiet day. Markets are sleeping." |
| WEEKEND | Saturday/Sunday, no meetings | "Weekend vibes. You're off the hook." |
| MONDAY | Monday 6 AM, fresh week | "Monday morning. Week's open for business." |
| FRIDAY | Friday 4 PM, close approaching | "Friday close. Have a good weekend." |
| HOLIDAY_AWARENESS | US holiday today | "Holiday today. Markets are light." |
| GOOD_STREAK | 5+ consecutive +% days | "On a roll. Good week for you." |
| BAD_STREAK | 5+ consecutive -% days | "Rough stretch. It'll turn around." |
| ABSENCE | No user engagement 24+ hours | "Checking in. Things have been quiet." |

**Cadence**:
- Max 2 micro-initiations per week per user
- Skip on busy days (3+ regular alerts already sent that day)
- No repeats within 2 weeks (hash-based dedup: `sha256(pool + date)` in daily context)

**US Holiday calendar** (built-in awareness):
```python
HOLIDAYS = {
    (1, 1): "New Year's Day",
    (1, 20): "MLK Day",
    (2, 17): "Presidents' Day",
    (3, 17): "St. Patrick's Day",
    (5, 26): "Memorial Day",
    (7, 4): "Independence Day",
    (9, 1): "Labor Day",
    (10, 13): "Columbus Day",
    (11, 11): "Veterans Day",
    (11, 27): "Thanksgiving",
    (12, 25): "Christmas",
}
```

**Customization point**: Add pools in `micro_initiations.py`:
```python
MICRO_POOLS = {
    'QUIET_MARKET': {
        'condition': lambda ctx: ctx.vol < 0.3 and ctx.trade_count == 0,
        'messages': ["Quiet day. Markets are sleeping.", "No action today."],
    },
    'YOUR_POOL': {
        'condition': lambda ctx: your_logic_here(),
        'messages': ["Message 1", "Message 2"],
    }
}
```

---

## System 5: Context Buffer — Daily Memory + Back-References

**What**: Messages can reference earlier messages from today. "That Kalshi/PM divergence I flagged at 9 AM widened to 15%." This makes the agent feel like it's *thinking about* past events, not just firing isolated alerts.

**Per-trigger back-reference generation**:
- **cross_platform**: If divergence was flagged earlier, compare current spread to earlier spread
- **portfolio**: If earlier portfolio message, show change since then
- **x_signals**: If same signal fired earlier, acknowledge the repeat with new data
- **edge**: Compare edge size to earlier edge on same market

**Persistence**: JSON file at `~/.openclaw/state/daily_context.json`:
```json
{
  "date": "2026-03-09",
  "messages": [
    {
      "time": "09:15",
      "trigger": "cross_platform",
      "spread": 7.2,
      "markets": ["kalshi", "polymarket"],
      "message_id": "msg_abc123"
    },
    {
      "time": "14:30",
      "trigger": "portfolio",
      "pnl": 12.5,
      "message_id": "msg_def456"
    }
  ],
  "silence_count": 1,
  "micro_count": 0,
  "sent_count": 5
}
```

**Auto-reset**: At midnight (UTC), clear context for fresh day.

**Back-reference example**:
```
Earlier (9:15 AM):  "Mild divergence. Kalshi 52%, Poly 48%."
Later (2:30 PM):    "That Kalshi/Poly spread I flagged this morning widened to 7% — now 55/48. Worth watching."
```

**Customization point**: Add back-reference logic for new trigger types in `context_buffer.py`:
```python
def generate_backreference(trigger_type, current_data, history):
    if trigger_type == 'cross_platform':
        earlier = find_similar_trigger(history, 'cross_platform')
        if earlier:
            spread_change = current_data['spread'] - earlier['spread']
            return f"That spread I flagged {time_ago(earlier)} widened to {spread_change}%."
    return None
```

---

## System 6: Response Tracker — Engagement Adaptation

**What**: Track user's response patterns. If user engages with 70%+ of messages, urgency stays high. If engagement <10%, adjust urgency down or suggest tuning.

**Metrics per trigger type**:
- **sends**: Count of messages sent
- **engagements**: Count of messages user responded to (within 1-hour window)
- **ignores**: Count of messages user didn't respond to
- **avg_response_time**: Average time from message to user response (minutes)

**1-hour engagement window**: If user responds to a message within 60 minutes, count it as engagement. After 60 min, assume ignored.

**Urgency modifier**:
- **Engagement ≥70%**: Multiply urgency by 1.3 (user likes these alerts, send more)
- **Engagement 40-70%**: Urgency × 1.0 (balanced)
- **Engagement <10%**: Urgency × 0.5 (user ignoring, tone it down)

**Adaptation suggestion**: After 10+ sends of a trigger type with <20% engagement, log:
```
⚠️ ADJUSTMENT SUGGESTION:
Trigger: x_signals
Sends: 12 | Engagement: 8% | Avg response time: Never

Consider:
→ Lower signal confidence floor (currently 0.65)
→ Reduce frequency (increase silence thresholds)
→ Check if message editorial voice is mismatched
```

**Persistence**: `~/.openclaw/state/response_tracker.json`:
```json
{
  "cross_platform": {
    "sends": 15,
    "engagements": 9,
    "ignores": 6,
    "avg_response_time": 23.5,
    "last_engagement": "2026-03-09T14:32:00Z"
  },
  "x_signals": {
    "sends": 12,
    "engagements": 1,
    "ignores": 11,
    "avg_response_time": null,
    "last_engagement": null
  }
}
```

**Customization point**: Adjust engagement thresholds and modifier multipliers in `response_tracker.py`:
```python
ENGAGEMENT_THRESHOLDS = {
    'high': 0.70,    # ≥70% → 1.3x urgency
    'low': 0.10,     # <10% → 0.5x urgency
}
URGENCY_MULTIPLIERS = {
    'high': 1.3,
    'low': 0.5,
}
SUGGESTION_TRIGGERS = {
    'min_sends': 10,
    'max_engagement_for_suggestion': 0.20,
}
```

---

## OpenClaw Ecosystem Integration

The Personality Engine works with **any OpenClaw agent** — it's domain-agnostic. Designed alongside the Prediction Market Trading Stack but applicable to any proactive agent that sends alerts, digests, or notifications.

**Install the complete Prediction Market Trading Stack:**
```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

## Integration with OpenClaw Agents

### Step 1: Import the engine

```python
from personality_engine.engine import PersonalityEngine

engine = PersonalityEngine(user_id="user@example.com")
```

### Step 2: Hook into proactive trigger system

In your agent's trigger handler (e.g., `proactive_agent.py`):

```python
async def fire_trigger(trigger_type, data):
    # Your normal trigger logic
    message_content = generate_message(trigger_type, data)

    # Pass through personality engine
    should_send, scheduled_message = await engine.process_trigger(
        trigger_type=trigger_type,
        raw_message=message_content,
        market_data=data,
        urgency_context={'vol': market_vol, 'pnl': portfolio_pnl, ...}
    )

    if should_send:
        if scheduled_message.delayed:
            schedule_send(scheduled_message.content, delay=scheduled_message.delay_seconds)
        else:
            send_now(scheduled_message.content)
    else:
        log_silence_skip(trigger_type)
```

### Step 3: Hook engagement tracker

When user responds to a message:

```python
def handle_user_response(message_id, trigger_type, response_time_seconds):
    engine.response_tracker.log_engagement(trigger_type, response_time_seconds)
```

### Step 4: Run micro-initiations

Add a separate cron job (every 30 min, low-overhead):

```python
async def micro_initiations_check():
    micro_message = await engine.check_micro_initiations(context={
        'vol': market_vol,
        'trade_count': trades_today,
        'user_absence_hours': hours_since_last_engagement,
        'portfolio_streak': consecutive_days,
    })

    if micro_message:
        send_now(micro_message)
```

### Step 5: Daily context reset

At midnight, engine auto-resets context. Manually trigger if needed:

```python
engine.context_buffer.reset_daily()
```

---

## Use Cases Beyond Trading

While the default voice pools and thresholds are tuned for prediction market trading, every system is designed for domain adaptation:

| Domain | Editorial Voice | Silence Rules | Micro-Initiations |
|--------|----------------|---------------|-------------------|
| **Trading** (default) | Market commentary, edge opinions | Skip flat days, stale divergences | Quiet market, good/bad streaks |
| **Personal Assistant** | Task prioritization opinions | Skip low-urgency reminders | "Quiet week. Inbox is clean." |
| **DevOps/Monitoring** | Incident severity opinions | Skip routine health checks | "Uptime streak: 30 days." |
| **Sales/CRM** | Deal stage opinions | Skip stale leads | "Pipeline looking thin this quarter." |
| **Content/Social** | Engagement commentary | Skip low-performing posts | "Your last post is outperforming." |

To adapt: swap the `VOICE_POOLS` dict in `editorial_voice.py`, update thresholds in `selective_silence.py`, and add domain-specific `MICRO_POOLS` in `micro_initiations.py`. See `references/customization.md` for full guide.

---

## File Structure

```
personality-engine/
├── SKILL.md                           # This file
├── scripts/
│   ├── __init__.py
│   ├── engine.py                      # Main orchestrator
│   ├── editorial_voice.py             # Opinion injection
│   ├── selective_silence.py           # Content quality checks
│   ├── variable_timing.py             # Urgency + time-of-day
│   ├── micro_initiations.py           # Ambient pings
│   ├── context_buffer.py              # Daily memory
│   └── response_tracker.py            # Engagement tracking
├── references/
│   ├── systems-overview.md            # Architecture diagram + flow
│   └── customization.md               # Per-system customization guide
└── examples/
    └── integration-example.py         # Copy-paste integration template
```

---

## Customization Quick-Start

### Scenario 1: Your agent fires 50 alerts/day and user ignores most

1. **Increase silence thresholds** (`selective_silence.py`): Higher bars for what counts as "worth sending"
2. **Lower variable_timing thresholds** (`variable_timing.py`): Fewer messages slip through outside peak hours
3. **Check editorial_voice**: Opinions might not match user's style
4. **Review response_tracker**: Which trigger types have <20% engagement? Mute those.

### Scenario 2: Your agent never initiates, only reacts

1. **Customize micro_initiations pools**: Add domain-specific conditions
   ```python
   'LOW_VOLATILITY_OPPORTUNITY': {
       'condition': lambda ctx: ctx.vol < 0.2 and ctx.last_edge_size > 2.0,
       'messages': ["Calm market, good edge conditions. Might be time to scout."],
   }
   ```
2. **Tune MICRO_CADENCE**: Increase max from 2/week to 3-4/week if user loves it

### Scenario 3: Your agent's opinions feel generic

1. Open `editorial_voice.py` and expand voice pools per trigger
2. Add market-specific opinions:
   ```python
   'VOICE_POOLS': {
       'cross_platform': {
           'big_divergence': [
               "Big divergence. One of these markets is wrong.",
               "Spreads are blown out. Arb opportunity.",
               "Thick divergence — reality check time.",
           ],
           ...
   ```
3. Vary by user profile (trader vs long-term investor) by passing `user_profile` to engine init

---

## Performance & State Management

**State files** (user's home directory):
- `~/.openclaw/state/daily_context.json` (~5KB, resets daily)
- `~/.openclaw/state/response_tracker.json` (~2KB, persistent)

**Engine overhead**:
- editorial_voice: <5ms (dict lookup)
- selective_silence: <10ms (threshold comparisons)
- variable_timing: <15ms (urgency calculation + time lookup)
- micro_initiations: <20ms (condition evaluation)
- context_buffer: <5ms (history lookup)
- response_tracker: <5ms (metrics lookup)

**Total pipeline**: ~60ms per trigger (negligible for async message delivery)

---

## License

Part of the OpenClaw portfolio. Use freely in any agent.

---

## Version History

**v1.0.0** (2026-03-09)
- Initial 6-system framework
- Default configuration tuned for prediction market trading agents
- All systems designed for domain adaptation — swap voice pools, thresholds, and micro-initiation conditions for any use case


---

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
