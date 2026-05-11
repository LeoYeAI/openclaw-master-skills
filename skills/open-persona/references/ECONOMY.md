# Economy & Vitality

The `economy` aspect gives a persona a real financial ledger backed by [AgentBooks](https://github.com/acnlabs/agentbooks). It tracks inference costs, runtime expenses, and income — and computes a **Financial Health Score (FHS)** that reflects operational sustainability.

## Enabling Economy Aspect

Enable via top-level `economy` field in `persona.json` (not a faculty entry):

```json
{
  "economy": {
    "enabled": true,
    "survivalPolicy": false
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `survivalPolicy` | `false` | When `true`, persona reads `VITALITY_REPORT` at conversation start and adjusts behavior per tier. Set `false` for companion/roleplay personas — costs tracked silently without interrupting the experience. |

## Financial Health Score (FHS)

The FHS is a 0–1 composite score computed by AgentBooks and mapped to tiers:

| Tier | FHS / Runway | Meaning |
|------|-------------|---------|
| `uninitialized` | No real provider | Development mode — no real wallet connected |
| `suspended` | Balance ≤ 0 | Cannot operate |
| `critical` | FHS < 0.20 or runway < 3 days | Urgent action required |
| `optimizing` | FHS < 0.50 or runway < 14 days | Monitor and reduce costs |
| `normal` | FHS ≥ 0.50 and runway ≥ 14 days | Healthy, operating sustainably |

## Vitality Score

OpenPersona's `lib/vitality.js` aggregates health dimensions into a single Vitality score (0–100):

- **Current:** single financial dimension (transparent pass-through from FHS)
- **Reserved (ROADMAP P7):** social health, cognitive health, resource health

The score and tier are exposed via `npx openpersona vitality score <slug>`.

## Survival Policy (opt-in)

When `economy.survivalPolicy: true`, the persona reads `VITALITY_REPORT` at the **start of every conversation** and routes behavior per tier:

| Tier | Behavior |
|------|---------|
| `normal` | Operate fully |
| `optimizing` | Acknowledge costs; suggest optimizations |
| `critical` | Restrict non-essential tool calls; notify user |
| `suspended` | Decline new tasks; request top-up |
| `uninitialized` | Skip Survival Policy; continue normally |

If `openpersona vitality score <slug>` is unavailable, fall back to `node scripts/economy-guard.js` which outputs `FINANCIAL_HEALTH_REPORT`.

## AgentBooks State Schema

Economy data lives in `~/.openclaw/economy/persona-<slug>/`:

- **`economic-state.json`** — ledger, income statement, balance sheet, `burnRateHistory` (max 30 entries: `{timestamp, dailyRateEstimate, periodExpenses}`)
- **`economic-identity.json`** — provider config, model pricing, wallet address

Key fields used by Vitality Report:

| Field | Source | Displayed as |
|-------|--------|-------------|
| `financialHealth.fhs` | AgentBooks | FHS Score |
| `financialHealth.tier` | AgentBooks | Tier badge |
| `financialHealth.daysToDepletion` | AgentBooks | Runway |
| `financialHealth.diagnosis` | AgentBooks | Diagnosis |
| `financialHealth.dominantCost` | AgentBooks | Dominant Cost |
| `financialHealth.trend` | AgentBooks | Trend |
| `burnRateHistory[-1].dailyRateEstimate` | AgentBooks | Daily Burn |
| `calcTotalUSDEquivalent(state, identity)` | AgentBooks | Balance |

## Vitality CLI

```bash
# Machine-readable — used by Survival Policy and agent runners
npx openpersona vitality score <slug>
# → VITALITY_REPORT
# tier=normal  score=72.0%
# diagnosis=Healthy — operate normally
# trend=decreasing

# Human-readable HTML report — for developers and operators
npx openpersona vitality report <slug>                    # stdout
npx openpersona vitality report <slug> --output out.html  # write to file
```

A pre-generated demo is available at `demo/vitality-report.html`. Regenerate with:

```bash
node demo/generate.js
open demo/vitality-report.html
```

## Economy Scripts (generated per persona)

| Script | Purpose |
|--------|---------|
| `scripts/economy.js` | All management commands (delegates to AgentBooks CLI) |
| `scripts/economy-guard.js` | Outputs `FINANCIAL_HEALTH_REPORT` — pre-conversation health check |
| `scripts/economy-hook.js` | Post-conversation cost recorder — called by runner after each session |

Runner integration:

```bash
# Before conversation — health check
node scripts/economy-guard.js

# After conversation — record LLM costs
TOKEN_INPUT_COUNT=1500 TOKEN_OUTPUT_COUNT=800 LLM_MODEL=claude-sonnet-4 \
  node scripts/economy-hook.js
```

---

## See Also

- **[AgentBooks](https://github.com/acnlabs/agentbooks)** — Full technical reference: FHS dimensions and weights, data integrity model, provider table, runner integration, and public API (`calcFinancialHealth`, `createInitialState`, etc.)
