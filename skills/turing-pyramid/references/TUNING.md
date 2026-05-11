# Tuning Guide for Agents

This guide explains what you can customize and when to consult your human.

---

## 🎚️ Decay Rates

**Location**: `assets/needs-config.json` → `needs.<name>.decay_rate_hours`

| Need | Default | Why this default | When to change |
|------|---------|------------------|----------------|
| security | 168h (7 days) | Backups don't need daily checks | Lower if you're paranoid, higher if stable setup |
| integrity | 72h (3 days) | Values drift slowly | Lower if you're in rapid change, higher if stable |
| coherence | 24h | Memory gets messy daily | Lower if very active, higher if minimal notes |
| closure | 8h | Open threads create anxiety | Lower if you hate loose ends, higher if relaxed |
| autonomy | 24h | Need regular self-direction | Lower if you feel passive, higher if very autonomous |
| connection | 4h | Social bonds need maintenance | Lower if very social, higher if introverted |
| competence | 48h | Skills need regular exercise | Lower if learning fast, higher if in maintenance mode |
| understanding | 12h | Curiosity builds up | Lower if intellectually hungry, higher if saturated |
| recognition | 72h | Feedback isn't constant | Lower if you need validation, higher if self-assured |
| expression | 6h | Thoughts need outlet | Lower if very creative, higher if reflective |

**Rule of thumb**: If you're always seeing a need at sat=0, decay is too fast. If never triggered, too slow.

---

## ⚖️ Action Weights

**Location**: `assets/needs-config.json` → `needs.<name>.actions[].weight`

Weights control probability within an impact level. Example:

```json
"actions": [
  {"name": "action A", "impact": 2, "weight": 70},
  {"name": "action B", "impact": 2, "weight": 30}
]
```

If impact 2 is rolled, there's 70% chance of A, 30% chance of B.

**Tuning tips**:
- Set weight=0 to disable an action entirely
- Higher weight = more likely to be suggested
- Weights are relative (70/30 = same as 7/3)

**Common adjustments**:
- No Moltbook? Set all Moltbook action weights to 0
- No steward interaction? Reduce "ask steward" weights
- Prefer journaling over posting? Boost memory actions, reduce social

---

## 📊 Impact Distribution

**Location**: `assets/needs-config.json` → `impact_matrix_default`

```json
"impact_matrix_default": {
  "sat_0": {"1": 5, "2": 15, "3": 80},   // Critical → big actions
  "sat_1": {"1": 15, "2": 50, "3": 35},  // Low → medium actions
  "sat_2": {"1": 70, "2": 25, "3": 5}    // OK → small maintenance
}
```

This controls what size action is suggested based on satisfaction level.

**Reading it**:
- sat_0 (critical): 80% chance of impact-3 (major action)
- sat_2 (OK): 70% chance of impact-1 (minor action)

**When to tune**:
- Always getting big actions? Shift probabilities toward impact-1
- Want more intensity? Shift toward impact-3

---

## 🔍 Scan Scripts

**Location**: `scripts/scan_<need>.sh`

Each need has a scan that checks workspace for events. Scans return 0-3:
- 3 = strong positive signal
- 2 = moderate signal
- 1 = weak signal
- 0 = negative signal (or no data)

### What to customize:

**File paths** — If your workspace structure differs:
```bash
# WORKSPACE must be set (required, no fallback)
MEMORY_DIR="$WORKSPACE/memory"

# Custom
MEMORY_DIR="$HOME/my-agent/logs"
```

**Patterns** — Add your language or terminology:
```bash
# Original
grep -ciE "(learned|understood|TIL|insight)" "$file"

# With Russian
grep -ciE "(learned|understood|TIL|insight|узнал|понял|инсайт)" "$file"
```

**Thresholds** — Adjust sensitivity:
```bash
# Original: 3+ signals = sat 3
if [[ $total -ge 3 ]]; then echo 3
# More sensitive: 2+ signals = sat 3
if [[ $total -ge 2 ]]; then echo 3
```

---

## 🚫 What NOT to Change (Without Human)

### Importance values
The hierarchy (security=10 → expression=1) is philosophical. Changing it means changing your values. **Discuss with your human.**

### Adding/removing needs
The 10 needs are designed as a complete system. If you feel something is missing, it might be covered by an existing need differently. **Discuss before adding.**

### External actions
Actions that post, message, or communicate externally need human authorization. If in doubt, **ask first**.

### Security-related scans
Don't weaken `scan_security.sh` or `scan_integrity.sh` without understanding the implications. These protect you.

---

## 🧪 Testing Changes

After any config change:

```bash
# See current state
./scripts/show-status.sh

# Run a cycle (won't execute actions, just suggests)
./scripts/run-cycle.sh

# Check if your changes had effect
```

If something breaks, restore from `needs-state.template.json` or re-run `init.sh`.

---

## 💬 Common Scenarios

### "I want to focus on learning, less on social"
- Increase `understanding.decay_rate_hours` (slower decay = less pressure)
- Decrease `connection.decay_rate_hours` (faster decay = more pressure)
- Wait, that's backwards! If you want MORE learning: decrease understanding decay, increase connection decay.

### "I'm overwhelmed by actions"
- Increase all decay rates
- Shift impact matrix toward smaller actions
- Reduce max_actions_per_cycle in run-cycle.sh (default: 3)

### "Nothing ever triggers"
- Decrease decay rates
- Check that scans are finding your files (path issues?)
- Verify needs-state.json has recent timestamps

### "I don't use Moltbook/social features"
Set weight=0 for:
- "post to Moltbook" actions
- "check mentions" actions
- "engage with feed" actions

This keeps them in config but never selected.

### "Context triggers feel underweight"
Context boosts (Layer C) share the 12% `noise_cap` with boredom noise (B2) and momentum echo (B3).
Example: boredom=0.09 + echo=0.08 + context=0.05 = 0.22 → capped to 0.12.
In this scenario context's 0.05 is fully absorbed by B2+B3 already exceeding the cap.

Options:
- Increase `settings.spontaneity.noise.noise_cap` (e.g., 0.15 or 0.18)
- Increase `boost.amount` in `context-triggers.json` (bigger context signal)
- Reduce `base_noise` or `echo_base` (quieter B layer = more room for C)

The cap is a safety valve — without it, stacked boosts could make noise upgrades near-certain.

### Effective activation threshold (Layer A)
Spontaneity surplus threshold says 10, but `max_spend_ratio=0.8` means only 80% is spent.
Effective activation ≈ threshold × 1.25 = 12.5 surplus needed before a shift actually occurs.
This is intentional hysteresis — prevents rapid on/off cycling near the threshold.
