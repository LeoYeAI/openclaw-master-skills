# Test Protocol — Turing Pyramid

## Quick Start

```bash
# Run all tests
./tests/run-tests.sh all

# Run specific suite
./tests/run-tests.sh unit
./tests/run-tests.sh integration
./tests/run-tests.sh regression
```

## When to Run Tests

### Required (MUST pass before any release):
- [ ] After modifying any script in `scripts/`
- [ ] After modifying `assets/needs-config.json`
- [ ] After modifying `assets/cross-need-impact.json`
- [ ] Before publishing to ClawHub

### Recommended:
- [ ] After modifying documentation (sanity check)
- [ ] When adding new features
- [ ] After pulling updates from others

## Test Suites

### Unit Tests (`tests/unit/`)
Fast, isolated tests for individual functions/formulas.

| Test | What it verifies |
|------|------------------|
| `test_tension_formula` | tension = importance × (3 - satisfaction) |
| `test_floor_ceiling` | satisfaction clamped to ≤ 3.0 |

### Integration Tests (`tests/integration/`)
End-to-end tests that run actual scripts.

| Test | What it verifies |
|------|------------------|
| `test_full_cycle` | run-cycle.sh produces valid output structure |

### Regression Tests (`tests/regression/`)
Tests for bugs we've found and fixed — prevents re-introduction.

| Test | Bug it prevents |
|------|-----------------|
| `test_socrat_effect` | Floor clamping blocks negative cross-impact at sat=0.5 |

## Adding New Tests

1. Create `tests/<suite>/test_<name>.sh`
2. Make it executable: `chmod +x tests/<suite>/test_<name>.sh`
3. Script should `exit 0` on pass, `exit 1` on fail
4. Output error message on failure for debugging

### Template:
```bash
#!/bin/bash
# test_<name>.sh — Description of what this tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Setup
# ...

# Test
# ...

# Verify
if [[ $result == $expected ]]; then
    exit 0
else
    echo "Expected $expected, got $result"
    exit 1
fi
```

## Fixtures

Pre-configured state files in `tests/fixtures/`:

| File | Description |
|------|-------------|
| `needs-state-healthy.json` | All needs at sat=2.0-2.5, dep=1 |
| `needs-state-crisis.json` | All needs at sat=0.5, dep=3 |

Use these for consistent test setup:
```bash
cp "$FIXTURES/needs-state-healthy.json" "$STATE_FILE"
```

## Pre-Release Checklist

Before running `clawhub publish`:

```bash
# 1. Run all tests
./tests/run-tests.sh all

# 2. Check for uncommitted changes
git status

# 3. Review diff
git diff HEAD~1

# 4. Update version in SKILL.md
# 5. Commit with descriptive message
# 6. Publish
```

---

*Tests are not optional. They protect us from ourselves.*
