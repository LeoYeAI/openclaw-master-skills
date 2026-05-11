# Market Signal Fusion Skill for OpenClaw

This skill teaches OpenClaw how to run a structured stock-analysis workflow with:

1. Macro / political / economic news interpretation
2. Reddit WSB and retail sentiment reading
3. Fusion of macro tailwinds with sentiment signals
4. Quantified value-investing fallback screening
5. Quantamental and technical analysis with buy/sell zones
6. Automatic single-language output plus fixed JSON schema for downstream agents
7. Market regime detection, confidence gates, and reason codes for auditability

## What's new in this version

- **WSB / retail sentiment module contract**: clear input/output expectations and graceful degradation when only attention data is available
- **Market regime detector**: top-down style control such as risk-off defensive vs inflation reflation
- **Confidence gates + reason codes**: auditable pass/fail logic for downstream agents
- **Automatic language switching**: Chinese prompt -> Chinese output; English prompt -> English output; bilingual only when requested
- **Fixed JSON schema**: easier for downstream agent pipelines
- **Harder value fallback**: explicit composite score using:
  - PEG
  - Forward P/E relative
  - FCF Yield
  - Revision Momentum
  - Balance-sheet / quality guardrail

## Local install

Put this folder in one of these locations:

- `./skills/market-signal-fusion`
- `~/.openclaw/skills/market-signal-fusion`

OpenClaw loads skills from workspace or user skill folders.

## Publish to ClawHub

Example:

```bash
clawhub publish ./market-signal-fusion-skill \
  --slug market-signal-fusion \
  --name "Market Signal Fusion" \
  --version 1.2.0 \
  --tags latest,finance,stocks,macro,sentiment
```

Or scan and publish updates for all local skills:

```bash
clawhub sync --all
```

## Suggested invocation prompts

- `Use market-signal-fusion to analyze this week's market and give me the best 5 stocks.`
- `Use market-signal-fusion for AI infrastructure stocks with a value bias.`
- `Use market-signal-fusion for tariff beneficiaries and short-term trading setups.`
- `Use market-signal-fusion and return Chinese report plus JSON.`
- `Use market-signal-fusion with macro + sentiment overlap only.`

## Notes

This skill is instruction-only. It works best when your OpenClaw setup has good web/search/browser tools and market-data access.

Recommended runtime capabilities:
- web / browser
- news search
- market data API
- optional Reddit or social-data plugin

If social sentiment data is unavailable, the skill can still run with fallback logic and reduced confidence.


## New structured capabilities

This version is better suited for multi-agent or downstream processing because the JSON schema now includes:
- `market_regime`
- sentiment `confidence_gate`
- ticker-level `reason_codes` and `rejection_codes`
- candidate-level `confidence_gate`
- optional `strict_mode`
