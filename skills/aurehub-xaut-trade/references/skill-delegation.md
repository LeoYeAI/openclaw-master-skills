# Skill Delegation

xaut-trade delegates non-XAUT intents to specialized skills. This file is the single source of truth for the registry and delegation flow.

## Intent Priority Rules

When a message contains both xaut-trade signals and delegation keywords:

1. **Explicit `XAUT` or `USDT` token name present** → xaut-trade wins (e.g. "buy XAUT on polymarket" → buy flow; "buy XAUT when price reaches $3000" → limit order flow)
2. **No XAUT/USDT token, delegation keywords present** → delegation wins (e.g. "bet on Bitcoin above 100k" → Polymarket delegation)
3. **Ambiguous — no clear token, no clear keyword** → ask user to clarify

## Registry

| Slug | Trigger keywords | Install command | Description |
|------|-----------------|-----------------|-------------|
| `polymarket-trade` | polymarket, prediction market, bet on, bet that, will X happen, odds on, chances of, buy YES, buy NO, sell shares | `npx skills add aurehub/skills` | Trade on Polymarket prediction markets (Polygon, USDC.e) |
| `hyperliquid-trade` | hyperliquid, perp, perpetual, futures, long, short, open long, open short, close position, leverage | `npx skills add aurehub/skills` | Trade spot and perpetual futures on Hyperliquid |

## Skill Delegation Flow

When a delegation intent is matched:

1. Identify the `slug` from the registry row whose trigger keywords match the user's message.
2. Check if the skill is installed:
   ```bash
   ls ~/.claude/skills/<slug>/SKILL.md 2>/dev/null && echo "INSTALLED" || echo "NOT_FOUND"
   ```
   (`~/.claude/skills/` is the standard Claude Code skills directory; local dev symlinks installed via `ln -sfn` resolve to the same path.)
3. **If INSTALLED**: use the `Skill` tool with skill name `<slug>` to handle the user's request. Do not continue any xaut-trade flow.
4. **If NOT_FOUND**: hard-stop and output:

   > This request is for **[Description from registry]**, which requires the **[slug]** skill.
   >
   > Install it with:
   > ```
   > [install command]
   > ```
   > Then re-submit your request.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Skill not installed | Hard-stop with install command from registry |
| Skill installed but setup incomplete | Delegation hands off via Skill tool; target skill handles its own setup checks |
| XAUT/USDT token name present alongside delegation keywords | XAUT intent wins; run xaut-trade flow |
| No XAUT/USDT token, delegation keywords present | Delegation wins |
| Ambiguous — no clear token, no clear delegation keyword | Ask user to clarify |
| No registry match found for unrecognized intent | Fall through; reply "Only XAUT/USDT trading is supported" if still unmatched |

## Adding Future Skills

To integrate a new skill, add a single row to the Registry table above. No changes to `SKILL.md` are required.
