# Personality Engine — Customization Guide

How to modify each system to fit your use case.

---

## System 1: Selective Silence — Content Quality Thresholds

### Scenario: Your agent fires 50 alerts/day but user ignores most

**Action**: Raise silence thresholds (be pickier about what's "worth sending")

```python
from personality_engine.selective_silence import SelectiveSilence

silence = SelectiveSilence(state_dir)

# Raise the bar for morning briefs
silence.SILENCE_THRESHOLDS['vol_floor'] = 1.0  # Was 0.5%

# Require edges to be bigger
silence.SILENCE_THRESHOLDS['edge_floor'] = 2.0  # Was 1.0%

# Require more signal confidence
silence.SILENCE_THRESHOLDS['signal_confidence_floor'] = 0.75  # Was 0.65
```

### Scenario: Your domain isn't financial (e.g., email assistant, real estate)

**Action**: Override silence logic completely

```python
# Add new trigger type with custom silence check
def custom_should_silence(self, trigger_type, data):
    if trigger_type == "email_spam_risk":
        # Silence if spam confidence <0.3 (not worth flagging)
        return data.get("spam_confidence", 0) < 0.3
    elif trigger_type == "property_price_drop":
        # Silence if drop <2% (noise)
        return data.get("price_drop_pct", 0) < 2.0
    # Fall back to parent logic
    return super()._should_silence(trigger_type, data)

# Monkey-patch at runtime
SelectiveSilence.should_silence = custom_should_silence
```

---

## System 2 & 4: Variable Timing — Urgency & Scheduling

### Scenario: You want different time-of-day thresholds

**Action**: Modify the threshold map

```python
from personality_engine.variable_timing import VariableTiming

timing = VariableTiming(state_dir)

# Very aggressive early morning (you wake up at 5 AM)
timing.TIME_OF_DAY_THRESHOLDS[(5, 9)] = 0.4  # Lower bar 5-9 AM

# Very quiet 9-5 PM (you're in meetings)
timing.TIME_OF_DAY_THRESHOLDS[(9, 17)] = 0.8  # Higher bar 9 AM - 5 PM

# Aggressive evening trading window 5-9 PM
timing.TIME_OF_DAY_THRESHOLDS[(17, 21)] = 0.3  # Very low bar
```

### Scenario: Customize urgency calculation per trigger

**Action**: Override compute_base_urgency

```python
# Subclass and override
class MyVariableTiming(VariableTiming):
    def _urgency_custom_trigger(self, data):
        # Custom urgency for your domain
        score = data.get("custom_score", 0)
        return min(1.0, score / 100.0)

timing = MyVariableTiming(state_dir)

# Register it
timing.compute_base_urgency = lambda t, d: (
    timing._urgency_custom_trigger(d) if t == "custom_trigger"
    else VariableTiming.compute_base_urgency(timing, t, d)
)
```

### Scenario: Disable weekend modifier

**Action**: Set modifier to 0

```python
timing.WEEKEND_MODIFIER = 0.0  # No extra sends on weekends
timing.CLUSTERING_PREVENTION = 0.0  # Send as fast as you want
```

---

## System 3: Response Tracker — Engagement Thresholds & Learning

### Scenario: Your user is very responsive; keep high bar

**Action**: Increase high-engagement threshold

```python
from personality_engine.response_tracker import ResponseTracker

tracker = ResponseTracker(state_dir)

# Only boost urgency if engagement ≥85% (not 70%)
tracker.ENGAGEMENT_THRESHOLDS['high'] = 0.85

# Make the boost more aggressive
tracker.URGENCY_MULTIPLIERS['high'] = 1.5
```

### Scenario: Suppress low-engagement triggers more aggressively

**Action**: Lower the multiplier

```python
tracker.URGENCY_MULTIPLIERS['low'] = 0.3  # Was 0.5x
```

### Scenario: Get alerts earlier

**Action**: Lower suggestion threshold

```python
# Alert after just 5 sends (not 10)
tracker.SUGGESTION_TRIGGERS['min_sends'] = 5

# Suggest if engagement <30% (not 20%)
tracker.SUGGESTION_TRIGGERS['max_engagement_for_suggestion'] = 0.30
```

### Scenario: Export metrics for external analysis

```python
# Export as CSV for spreadsheet/plotting
csv_data = tracker.export_metrics()
print(csv_data)

# Or save to file
from pathlib import Path
tracker.export_metrics(Path("engagement_metrics.csv"))
```

---

## System 5: Context Buffer — Back-References & Memory

### Scenario: Add back-references for new trigger type

**Action**: Add custom backreference method

```python
from personality_engine.context_buffer import ContextBuffer

buffer = ContextBuffer(state_dir)

# Add method for your trigger
def _backreference_custom(self, data):
    earlier = self._find_trigger_message("custom")
    if not earlier:
        return None

    value_change = data.get("value", 0) - earlier.get("value", 0)
    time_ago = self._format_time_ago(earlier.get("time"))

    return f"That was {value_change:+.1f} since {time_ago}."

# Patch it
buffer._backreference_custom = lambda d: _backreference_custom(buffer, d)

# And in generate_backreference, add:
# elif trigger_type == "custom":
#     return buffer._backreference_custom(data)
```

### Scenario: Inject context into system prompt

**Action**: Call get_today_summary() before each API call

```python
# In your agent loop
summary = buffer.get_today_summary()

system_prompt = f"""You are an AI assistant.
{summary}

Keep responses brief and actionable."""

# Pass to Claude API
response = claude.messages.create(
    system=system_prompt,
    messages=messages,
    ...
)
```

### Scenario: Keep longer history (not just today)

**Action**: Extend context file retention

```python
# By default, only today's context is kept
# To keep rolling 7-day history:

# Create wrapper that appends to historical log
class ExtendedContextBuffer(ContextBuffer):
    def __init__(self, state_dir):
        super().__init__(state_dir)
        self.history_file = state_dir / "context_history.json"

    def log_message(self, trigger_type, data, message):
        super().log_message(trigger_type, data, message)

        # Also append to rolling history
        import json
        history = []
        if self.history_file.exists():
            with open(self.history_file) as f:
                history = json.load(f)

        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger": trigger_type,
            "message": message[:100],
        })

        # Keep last 1000 messages
        history = history[-1000:]
        with open(self.history_file, "w") as f:
            json.dump(history, f)
```

---

## System 6: Editorial Voice — Opinion Customization

### Scenario: Add opinions for new trigger type

**Action**: Extend VOICE_POOLS

```python
from personality_engine.editorial_voice import EditorialVoice

voice = EditorialVoice()

# Add trigger type
voice.add_trigger_voice("email_volume", {
    "high": [
        "Your inbox is on fire.",
        "Lots of email today.",
    ],
    "moderate": [
        "Normal email day.",
    ],
    "low": [
        "Quiet inbox. Enjoy it.",
    ],
})
```

### Scenario: Make opinions more aggressive/casual

**Action**: Update opinion pools

```python
voice.VOICE_POOLS['portfolio']['excellent'] = [
    "Crushing it. Keep going.",
    "Absolute legend move.",
    "Money printer go brrr.",
]

voice.VOICE_POOLS['portfolio']['terrible'] = [
    "Ouch. That hurt.",
    "Oof. Rough day.",
    "This is fine.",  # 🔥
]
```

### Scenario: Make opinions match user's style

**Action**: Create user-specific voice profiles

```python
class PersonalityEngine:
    VOICE_PROFILES = {
        "aggressive_trader": {
            "portfolio": {
                "excellent": ["Crushing it.", "Money printer go brrr."],
                "bad": ["Oof. Cut the losers."],
            }
        },
        "conservative_investor": {
            "portfolio": {
                "excellent": ["Good steady gains.",],
                "bad": ["Stay the course.",],
            }
        },
    }

    def __init__(self, user_id, profile="conservative_investor"):
        # ...
        # Load profile
        profile_voice = self.VOICE_PROFILES.get(profile, {})
        for trigger, subpools in profile_voice.items():
            for subpool, opinions in subpools.items():
                self.editorial_voice.add_opinion_pool(trigger, subpool, opinions)
```

### Scenario: Include market data in opinions

**Action**: Make opinion generation data-aware

```python
def _opinion_portfolio(self, data):
    daily_pnl = data.get("daily_pnl", 0)
    market_state = data.get("market_state", "")  # e.g., "bull" or "bear"

    if market_state == "bull" and daily_pnl > 10:
        return "Bull market is treating you well."
    elif market_state == "bear" and daily_pnl > 5:
        return "Outperforming in a bear market. Nice."

    # Fall back to default
    return EditorialVoice._opinion_portfolio(self, data)
```

---

## System 7: Micro-Initiations — Custom Pools & Cadence

### Scenario: Add domain-specific pool

**Action**: Add to MICRO_POOLS

```python
from personality_engine.micro_initiations import MicroInitiations

micro = MicroInitiations(state_dir)

micro.add_pool(
    "EARNINGS_SEASON",
    condition=lambda ctx: ctx.get("earnings_today_count", 0) >= 5,
    messages=[
        "Earnings day. Volatility expected.",
        "Big earnings day. Markets could move.",
    ]
)

micro.add_pool(
    "USER_BIRTHDAY",
    condition=lambda ctx: ctx.get("is_user_birthday", False),
    messages=[
        "Happy birthday! Enjoy the day.",
    ]
)
```

### Scenario: Increase micro cadence

**Action**: Modify MICRO_CADENCE

```python
# If user loves micro-initiations, increase from 2/week to 4/week
micro.MICRO_CADENCE['max_per_week'] = 4

# Lower alert threshold for sending
micro.MICRO_CADENCE['skip_if_alerts_today'] = 5  # Was 3
```

### Scenario: Customize holiday calendar

**Action**: Add/remove holidays

```python
# Add custom holiday
micro.HOLIDAYS[(3, 15)] = "My Birthday"

# Remove a holiday
del micro.HOLIDAYS[(11, 27)]  # Remove Thanksgiving

# Completely custom calendar
micro.HOLIDAYS = {
    (1, 1): "New Year",
    (7, 4): "Independence Day",
    # Your company holidays...
}
```

### Scenario: Disable micro-initiations

**Action**: Set max to 0

```python
micro.MICRO_CADENCE['max_per_week'] = 0
```

---

## Cross-System Scenarios

### Scenario 1: "Only send when I'm actually paying attention"

Combine all 3 aggressive systems:

```python
# High silence bar
selective_silence.SILENCE_THRESHOLDS['signal_confidence_floor'] = 0.85

# Very high time-of-day thresholds (except prime hours)
timing.TIME_OF_DAY_THRESHOLDS[(9, 17)] = 0.8  # Work hours: high bar
timing.TIME_OF_DAY_THRESHOLDS[(17, 22)] = 0.4  # Evening: lower bar

# Suppress if engagement low
tracker.URGENCY_MULTIPLIERS['low'] = 0.2

# Disable micro-initiations
micro.MICRO_CADENCE['max_per_week'] = 0
```

### Scenario 2: "Overwhelm me with options, but only quality"

```python
# Low silence bar (send more)
selective_silence.SILENCE_THRESHOLDS['vol_floor'] = 0.2

# Low time-of-day thresholds (send almost everything)
for key in timing.TIME_OF_DAY_THRESHOLDS:
    timing.TIME_OF_DAY_THRESHOLDS[key] = 0.3

# Keep high-engagement alerts flowing
tracker.URGENCY_MULTIPLIERS['high'] = 1.5

# Add more micro-initiations
micro.MICRO_CADENCE['max_per_week'] = 5
```

### Scenario 3: "Tune to my engagement patterns"

```python
# Export metrics, analyze
csv = tracker.export_metrics()

# If email alerts have >70% engagement:
if engagement_rate_email > 0.70:
    silence.SILENCE_THRESHOLDS['email_confidence_floor'] = 0.5
    timing.TIME_OF_DAY_THRESHOLDS[(9, 17)] = 0.3

# If price alerts have <20% engagement:
if engagement_rate_price < 0.20:
    silence.SILENCE_THRESHOLDS['price_move_pct'] = 2.0
    tracker.URGENCY_MULTIPLIERS['low'] = 0.3

# Log suggestion
suggestion = tracker.get_adjustment_suggestion("email")
if suggestion:
    print(f"Adjust: {suggestion}")
```

---

## Testing & Iteration

### Test harness

```python
from personality_engine.engine import PersonalityEngine
import asyncio

engine = PersonalityEngine(user_id="test_user")

async def test_trigger():
    should_send, scheduled = await engine.process_trigger(
        trigger_type="cross_platform",
        raw_message="Divergence detected",
        market_data={
            "spread": 7.5,
            "vol": 0.8,
            "age_hours": 2,
        },
        urgency_context={},
    )

    if should_send:
        print(f"SEND: {scheduled.content}")
    else:
        print("HOLD")

asyncio.run(test_trigger())
```

### A/B test different thresholds

```python
# Version A: Conservative
engine_a = PersonalityEngine("user_a", state_dir="/tmp/a")
engine_a.variable_timing.TIME_OF_DAY_THRESHOLDS[(9, 17)] = 0.7

# Version B: Aggressive
engine_b = PersonalityEngine("user_b", state_dir="/tmp/b")
engine_b.variable_timing.TIME_OF_DAY_THRESHOLDS[(9, 17)] = 0.3

# Run both, compare metrics after 1 week
```

### Monitor and iterate

```python
# Weekly check
summary = engine.response_tracker.get_summary()
print(summary)

# If engagement drops:
for trigger, metrics in summary.items():
    if float(metrics['engagement_rate'].rstrip('%')) < 20:
        print(f"ALERT: {trigger} engagement too low")
        suggestion = engine.response_tracker.get_adjustment_suggestion(trigger)
        print(suggestion)
```

---

## Production Checklist

- [ ] Override default thresholds for your domain
- [ ] Test silence logic with 10-20 sample triggers
- [ ] Verify time-of-day thresholds match your schedule
- [ ] Create/test custom voice pools
- [ ] Set up engagement tracking (log_engagement hooks)
- [ ] Run micro-initiations loop (every 30 min)
- [ ] Monitor engagement metrics weekly
- [ ] Iterate based on low-engagement triggers
- [ ] Document your customizations for future reference
