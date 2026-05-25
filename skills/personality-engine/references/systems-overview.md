# Personality Engine — 6-System Architecture Overview

## High-Level Pipeline

```
Trigger fires
    ↓
[1] SelectiveSilence ────→ should_silence()
    (Content quality checks)
    ↓
[2] VariableTiming ───→ compute_base_urgency()
    (Spread-based, P&L-based, confidence-based, edge-based)
    ↓
[3] ResponseTracker ──→ get_urgency_multiplier()
    (Engagement rate: 1.3x if high, 0.5x if low)
    ↓
[4] VariableTiming ───→ should_send_now()
    (Time-of-day thresholds + modifiers)
    ↓
[5] ContextBuffer ───→ generate_backreference()
    (Add context from earlier messages today)
    ↓
[6] EditorialVoice ──→ inject_opinion()
    (Add personality/opinions)
    ↓
Engine.dedup ────→ _is_duplicate()
    (Avoid repeats in 6-hour window)
    ↓
Send → iMessage/transport
```

Plus ambient:
- **MicroInitiations**: Separate evaluation loop every 30 min
- **ResponseTracker**: Continuous engagement monitoring

---

## System 1: Selective Silence

**Purpose**: Filter out noise before it becomes a message.

**Mechanism**:
- Per-trigger type content quality checks
- Thresholds (vol, spread age, signal confidence, edge size, portfolio flatness)
- If all conditions indicate "boring content", return `should_silence=True`
- When silencing, send explicit message: "Skipped the brief — nothing worth your attention."

**State**: `silence_state.json`
- Tracks per-trigger silence sends today
- Max 1 silence per trigger per day
- Auto-reset at midnight

**Key Methods**:
- `should_silence(trigger_type, data)` → bool
- `_can_send_silence_message(trigger_type)` → bool

**Customization**:
```python
SILENCE_THRESHOLDS = {
    'vol_floor': 0.5,
    'divergence_age_limit': 3,
    'signal_confidence_floor': 0.65,
    'edge_floor': 1.0,
    'portfolio_flat_range': 2.0,
}
```

---

## System 2 & 4: Variable Timing (Urgency + Scheduling)

**Purpose**: Score triggers for importance; schedule delivery based on time-of-day awareness.

**Phase 1: Urgency Compute** (0.0-1.0)
- Per-trigger base urgency calculation
- `cross_platform`: (spread / 10%) * 0.6
- `portfolio`: (abs(pnl) / 10%) * 0.7
- `x_signals`: (confidence * 0.8) + (position_match ? 0.2 : 0)
- `edge`: (edge_size / 5%) * 0.8
- `meeting`: max(0, 1.0 - minutes_away / 120)

**Phase 2: Time-of-Day Thresholds**
- Hour-based delivery gates
- Before 7 AM: 0.90 (sleep — high bar)
- 7-9 AM: 0.75 (morning crunch)
- 9 AM - 10 PM: 0.45 (daytime — lower bar)
- 10-11 PM: 0.35 (wind-down)
- 11 PM - midnight: 0.85 (late night)
- Midnight - 7 AM: 0.90 (sleep)

**Phase 3: Modifiers**
- **Weekend**: -0.10 threshold (send more)
- **Clustering prevention**: +0.20 threshold if sent <10 min ago
- **Daily fatigue**: +0.20 threshold per 10 messages today
- **Random jitter**: ±5% urgency

**Send Logic**:
```
adjusted_urgency = base_urgency * engagement_multiplier ± jitter
if adjusted_urgency >= time_of_day_threshold:
    send_now()
else:
    hold_for_next_trigger()
```

**Key Methods**:
- `compute_base_urgency(trigger_type, data)` → float
- `should_send_now(adjusted_urgency)` → (bool, delay_seconds)
- `_get_time_of_day_threshold(datetime)` → float

**Customization**:
```python
TIME_OF_DAY_THRESHOLDS = {
    (0, 7): 0.90,
    (7, 9): 0.75,
    (9, 22): 0.45,
    (22, 23): 0.35,
    (23, 24): 0.85,
}

WEEKEND_MODIFIER = 0.10
CLUSTERING_PREVENTION = 0.20
DAILY_FATIGUE_STEP = 0.20
JITTER_RANGE = 0.05
```

---

## System 3: Response Tracker (Engagement Adaptation)

**Purpose**: Learn from user's response patterns; adapt urgency over time.

**Metrics per trigger type**:
- `sends`: Total messages sent
- `engagements`: User responded within 60 minutes
- `ignores`: User did not respond within 60 minutes
- `avg_response_time`: Average response time (minutes)
- `last_send_time`, `last_engagement`: Timestamps

**Engagement Rate Calculation**:
```
engagement_rate = engagements / (engagements + ignores)
```

**Urgency Multiplier**:
- ≥70% engagement → 1.3x (user loves these alerts)
- 40-70% engagement → 1.0x (baseline)
- <10% engagement → 0.5x (user ignoring, tone down)

**Auto-Suggestions**:
- After 10+ sends with <20% engagement, log adjustment suggestion
- Suggests: lower confidence floor, reduce frequency, check voice fit

**State**: `response_tracker.json`
- Persistent across sessions
- Survives agent restarts

**Key Methods**:
- `log_send(trigger_type)`
- `log_engagement(trigger_type, response_time_seconds)`
- `log_ignore(trigger_type)`
- `get_urgency_multiplier(trigger_type)` → float
- `get_adjustment_suggestion(trigger_type)` → str or None
- `export_metrics(output_file)` → CSV

**Customization**:
```python
ENGAGEMENT_THRESHOLDS = {
    'high': 0.70,
    'low': 0.10,
}
URGENCY_MULTIPLIERS = {
    'high': 1.3,
    'baseline': 1.0,
    'low': 0.5,
}
SUGGESTION_TRIGGERS = {
    'min_sends': 10,
    'max_engagement_for_suggestion': 0.20,
}
```

---

## System 5: Context Buffer (Daily Memory)

**Purpose**: Enable back-references to earlier messages today. "That spread I flagged at 9 AM widened to 15%."

**Daily State**: `daily_context.json`
```json
{
  "date": "2026-03-09",
  "messages": [
    {
      "time": "09:15",
      "trigger": "cross_platform",
      "spread": 7.2,
      "message": "Mild divergence..."
    }
  ],
  "silence_count": 1,
  "micro_count": 0,
  "sent_count": 5
}
```

**Back-Reference Generation**:
- Per-trigger type (cross_platform, portfolio, x_signals, edge)
- Compares current data to last similar message
- Formats: "That [X] I flagged [TIME] [DIRECTION] to [VALUE]."

**Auto-Reset**: Midnight UTC

**Key Methods**:
- `generate_backreference(trigger_type, data)` → str or None
- `log_message(trigger_type, data, message)`
- `get_today_summary()` → str (for system prompt injection)

**Back-Reference Examples**:
- Cross-platform: "That Kalshi/Poly spread I flagged 2h ago widened to 7%."
- Portfolio: "Portfolio is up 3.5% since I checked 1h ago."
- Signals: "That Tesla signal I flagged 45m ago is still active."
- Edge: "That AAPL edge I found 3h ago is now 2.1%."

---

## System 6: Editorial Voice (Personality Injection)

**Purpose**: Inject opinions that vary by trigger type and market state.

**Voice Pools**:
- Each `(trigger_type, market_state)` → list of opinion strings
- Randomly selected per fire

**Per-Trigger Voice Pools**:
- `cross_platform`: big/mild/stale divergence
- `portfolio`: excellent/good/flat/bad/terrible P&L
- `x_signals`: strong/moderate/weak signal
- `edge`: fat/mild/thin edge
- `morning`: monday/friday/other
- `conflicts`: heavy/light overlap
- `meeting`: imminent countdown

**Example Opinion Injection**:
```
Base message: "Divergence detected: Kalshi 52%, Poly 48%."
Opinion (mild): "Mild divergence. Nothing screaming yet."
Final: "Divergence detected: Kalshi 52%, Poly 48%.

Mild divergence. Nothing screaming yet."
```

**Key Methods**:
- `inject_opinion(trigger_type, data)` → str or None
- `add_opinion_pool(trigger_type, subpool_name, opinions)`
- `add_trigger_voice(trigger_type, voice_dict)`
- `list_available_voices()` → dict

**Customization**:
```python
VOICE_POOLS = {
    'cross_platform': {
        'big_divergence': ["...", "..."],
        'mild_divergence': ["...", "..."],
        ...
    },
    ...
}
```

---

## System 7: Micro-Initiations (Ambient Awareness)

**Purpose**: Unprompted pings when conditions are met (quiet market, good streak, absence detected).

**Pools**:
- `QUIET_MARKET`: Vol <0.3%, no trades → "Quiet day. Markets are sleeping."
- `WEEKEND`: Weekend, no meetings → "Weekend vibes. You're off the hook."
- `MONDAY`: Monday morning → "New week. Here's the lay of the land."
- `FRIDAY`: Friday → "Friday close. Have a good weekend."
- `HOLIDAY_AWARENESS`: US holiday → "Holiday today. Markets are light."
- `GOOD_STREAK`: 5+ consecutive +% days → "On a roll. Good week for you."
- `BAD_STREAK`: 5+ consecutive -% days → "Rough stretch. It'll turn around."
- `ABSENCE`: 24+ hours no engagement → "Checking in. Things have been quiet."

**Cadence Limits**:
- Max 2 per week per user
- Skip on busy days (3+ alerts already sent)
- No repeats within 2 weeks (hash-based dedup)

**State**: `micro_state.json`
- Tracks weekly sends and pool history
- Auto-respects holiday calendar

**Key Methods**:
- `evaluate_pools(context)` → str or None
- `should_send_micro_initiation(alert_count_today)` → bool
- `log_send(pool_name, message)`
- `add_pool(pool_name, condition, messages)`

**Customization**:
```python
MICRO_POOLS = {
    'QUIET_MARKET': {
        'condition': lambda ctx: ctx['vol'] < 0.3,
        'messages': ["...", "..."],
    },
    'YOUR_POOL': {
        'condition': lambda ctx: your_logic(),
        'messages': ["...", "..."],
    },
}

MICRO_CADENCE = {
    'max_per_week': 2,
    'skip_if_alerts_today': 3,
    'no_repeat_days': 14,
}
```

---

## State Files

All persistence in `~/.openclaw/state/`:

| File | Purpose | Size | Reset |
|------|---------|------|-------|
| `silence_state.json` | Per-trigger silence cadence today | <1KB | Daily |
| `daily_context.json` | Messages logged today + back-refs | 5-10KB | Daily |
| `response_tracker.json` | Engagement metrics per trigger | 2-5KB | Persistent |
| `micro_state.json` | Weekly micro-init cadence + pool history | 2-5KB | Rolling window |

---

## Integration Checklist

- [ ] Import `PersonalityEngine` in your proactive agent
- [ ] Call `engine.process_trigger()` for each trigger fire
- [ ] Hook `log_user_engagement()` when user responds
- [ ] Hook `log_user_ignore()` after 1-hour window
- [ ] Run micro-initiations check every 30 minutes
- [ ] Monitor logs for adjustment suggestions
- [ ] Test with different time-of-day thresholds
- [ ] Review engagement metrics weekly

---

## Performance Notes

Total pipeline overhead per trigger: ~60ms
- Editorial voice: <5ms (dict lookup)
- Selective silence: <10ms (threshold checks)
- Variable timing: <15ms (urgency + time)
- Micro-initiations: <20ms (condition eval)
- Context buffer: <5ms (history lookup)
- Response tracker: <5ms (metric lookup)

All I/O async-safe. JSON persistence non-blocking in separate thread.

---

## Debug Utilities

```python
# Get engine summary
summary = engine.get_engine_summary()
print(summary)

# Export engagement metrics
csv = engine.response_tracker.export_metrics()
print(csv)

# Check silence state
print(engine.selective_silence.get_summary())

# Check micro cadence
print(engine.micro_initiations.get_summary())

# Get today's context
print(engine.context_buffer.get_all_messages())
print(engine.context_buffer.get_today_summary())
```

---

## Error Handling

All systems graceful on missing data:
- Missing market data → default urgency 0.5
- Missing engagement history → baseline multiplier 1.0
- Corrupted state files → auto-reset to fresh state
- Invalid thresholds → clamp to 0.0-1.0

Logs warnings, never silently fails. Production-ready.
