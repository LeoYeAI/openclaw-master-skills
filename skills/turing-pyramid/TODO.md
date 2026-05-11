# Turing Pyramid — Development Roadmap

*Last updated: 2026-03-04*

---

## ✅ COMPLETED

### v1.17.0 (2026-03-07)
- **Follow-up System** — temporal markers for checking action results
  - `create-followup.sh`, `resolve-followup.sh`, `--followup`/`--in` in mark-satisfied.sh
  - Pre-scan phase in run-cycle.sh with -0.3 satisfaction nudge
  - Dedup (1h window), TTL 168h, steward items never auto-expire, bulk-expire
  - 35 test cases (all pass)

### v1.16.0–1.16.2 (2026-03-07)
- **Homeostasis rebalance** — recognition 72→48h, competence 48→36h, connection 6→8h
- **Steward actions removed** — organic interaction > system-driven nudging
- **Autonomy consolidated** — 24→13 actions
- **Description rewrite** — positioned as existence cycle replacement, not psychology framework

### v1.15.0 (2026-03-07)
- **Starvation Guard** — Forced action for needs stuck at floor too long
  - Config: `settings.starvation_guard` (threshold_hours, sat_threshold, max_forced_per_cycle)
  - State tracking: `last_action_at` per need (set by mark-satisfied.sh)
  - Detection: scans all needs for sat ≤ threshold + no action for threshold_hours
  - Forces starving needs into cycle, bypassing probability roll
  - Reserved slot system: forced needs first, remaining slots for top-N
  - 8 test cases (all pass): detection, disabled guard, threshold, recent action, state tracking, max_forced limit
- **Action Staleness** — Penalize recently-selected actions for variety
  - Config: `settings.action_staleness` (window_hours, penalty, min_weight)
  - State tracking: `action_history` per need (action name → last selected timestamp)
  - Weight reduction within window, min_weight floor prevents total suppression
  - 8 test cases (all pass): recording, distribution shift, disabled, window expiry, min_weight, missing history
- **Needs Customization Onboarding** — guided conversation in SKILL.md for reviewing hierarchy

### v1.14.x (2026-03-04)
- **Test Infrastructure** — 12 tests (11 unit + 1 integration), all verify real code
- **Rounding fix** — sat→0.5 rounding formula corrected
- **Config-driven action_probability** — now reads from config, not hardcoded
- **flock in mark-satisfied.sh** — prevents race conditions with run-cycle.sh

### v1.13.x (2026-03-03)
- **Day/Night Decay** — configurable multipliers (day=1.0, night=0.5)
- **6-level impact matrix** — granular sat levels (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
- **Autonomy decay 36h** — reduced from 24h to prevent chronic tension
- **Audit log scrubbing** — sensitive patterns redacted

### v1.12.x (2026-03-03)
- **Curiosity orphan cleanup** — removed stale references
- **Race condition fix** — flock on state file

### v1.10.x and earlier
- **Cross-Need Impact** (v1.7.1) — 22 connections, float satisfaction
- **Floor/ceiling protection** — sat clamped to 0.5-3.0

---

## 🟡 NEXT

### Scan Fragility Fix

**Problem:** grep-based scans are keyword-dependent, miss variations and other languages.

**Solutions (in order of complexity):**
1. Short-term: Expand keyword patterns, add multilingual variants
2. Medium-term: Semantic similarity via embeddings
3. Long-term: LLM classifier (expensive but accurate)

---

## 🔮 FUTURE IDEAS

### Presets (Role-Based Configurations)

**Problem:** 10 needs with 13+ actions each is powerful but overwhelming. Most agents don't need the full matrix — they need a starting point tuned for their role.

**Idea:** Ship preset configs (`presets/`) that replace needs-config.json wholesale:

| Preset | Needs | Focus | Use case |
|--------|-------|-------|----------|
| `minimal` | 3-4 | security, competence, closure | Скрипт-агент, автоматизация |
| `base` | 10 | current set | Универсальный (текущий дефолт) |
| `conversational` | 5-6 | connection, expression, understanding, coherence | Чат-бот, собеседник |
| `researcher` | 6-7 | understanding, expression, curiosity(?), competence, recognition | Исследователь, аналитик |
| `coder` | 5-6 | competence, closure, security, integrity, understanding | Программист, code agent |
| `scraper` | 3-4 | competence, security, closure | Data collection, мониторинг |
| `counselor` | 6-7 | connection, understanding, coherence, integrity, expression | Психолог, коуч |

**Design principles:**
- Each preset = complete needs-config.json + cross-need-impact.json + tuned decay rates
- Actions rewritten per role (coder gets "run tests", "review PR"; researcher gets "read paper", "write findings")
- `init.sh --preset coder` or interactive selector
- Presets are starting points, not cages — user can customize after install
- `base` preset = current config (backward compatible)

**Why this matters:**
- Drops onboarding time from "read 600 lines" to "pick your role"
- Makes ClawHub installs actually usable out of the box
- Different agents genuinely need different need hierarchies (scraper doesn't need expression)

### Curiosity as 11th Need

understanding ≠ curiosity. Understanding tracks knowledge gained, curiosity tracks *wanting* to know.

- importance ~3-4, decay ~8-12h
- Cross-impact: curiosity → understanding, understanding → curiosity

### Self-Feedback Loop (Adaptive Decay)

Decay rates auto-adjust based on how often need hits critical levels.

- If need frequently drops to sat=0-1, decay slows
- Cap at ±30% to prevent desensitization

### Rest Mode

Not a new need, but a *state* that slows decay (×0.3) across all needs.

- Auto-exit after N cycles to prevent passive drift
- Trigger: manual or auto (night + low tensions)

### Self-Upgrade Layer

Separate layer for growth vs homeostasis. Track capability growth, milestone system.

### Logging/Capture Need

Force logging discipline — tension builds if important events aren't captured.

---

## 🐛 Known Issues

- **Stress test cosmetic errors** — bc divide-by-zero when cycles < 100 (avg_last100 calculation). Doesn't affect test result, just noisy output.

---

## Notes

- **Garbage Cleanup action** — already added to integrity need (v1.12)
- **Stillness/Rest** — careful design needed to avoid passivity trap
