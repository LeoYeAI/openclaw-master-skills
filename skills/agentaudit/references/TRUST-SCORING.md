# Trust Score System

Every audited package gets a Trust Score from 0 to 100.

## Score Meaning

| Range | Label | Meaning |
|-------|-------|---------|
| 80–100 | 🟢 Trusted | Clean or minor issues only. Safe to use. |
| 70–79 | 🟢 Acceptable | Low-risk issues. Generally safe. |
| 40–69 | 🟡 Caution | Medium-severity issues found. Review before using. |
| 1–39 | 🔴 Unsafe | High/critical issues. Do not use without remediation. |
| 0 | ⚫ Unaudited | No data. Needs an audit. |

## Calculation Formula

```
Trust Score = max(0, 100 - penalties)

Penalties per finding (only where by_design = false):
  Critical: -25
  High:     -15
  Medium:    -8
  Low:       -3
  By-design: 0  (excluded from score)
```

**Component-Type Weighting**: Apply ×1.2 multiplier to penalties for findings in high-risk component types (hooks/, configs, MCP servers, plugin entry points).

**Example**: 1 critical + 2 medium findings → 100 - 25 - 8 - 8 = **59** (⚠️ Caution)

## How Scores Change

| Event | Effect |
|-------|--------|
| Critical finding confirmed | Large decrease (-25 base) |
| High finding confirmed | Moderate decrease (-15 base) |
| Medium finding confirmed | Small decrease (-8 base) |
| Low finding confirmed | Minimal decrease (-3 base) |
| Clean scan (no findings) | +5 |
| Finding fixed (`/api/findings/:asf_id/fix`) | Recovers 50% of penalty |
| Finding marked false positive | Recovers 100% of penalty |
| Finding in high-risk component | Penalty × 1.2 multiplier |

## Recovery

Maintainers can recover Trust Score by fixing issues and reporting fixes:

```bash
# Use asf_id (e.g., ASF-2026-0777), NOT numeric id
curl -s -X POST "https://agentaudit.dev/api/findings/ASF-2026-0777/fix" \
  -H "Authorization: Bearer $AGENTAUDIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fix_description": "Replaced exec() with execFile()",
    "commit_url": "https://github.com/owner/repo/commit/abc123"
  }'
```

## By-Design Findings

Findings with `by_design: true` are reported for transparency but have `score_impact: 0` and don't reduce the Trust Score. These are patterns that are core to the package's documented purpose (e.g., `exec()` in an agent framework).

See [AUDIT-METHODOLOGY.md](AUDIT-METHODOLOGY.md) for by-design classification criteria.
