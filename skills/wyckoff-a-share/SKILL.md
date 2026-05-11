---
name: akshare-online-alpha
description: Run Wyckoff master-style analysis from stock codes, holdings (symbol/cost/qty), cash, CSV data, and optional chart images. Use when users want online multi-source data fetching with source switching, strict Beijing-time trading-session checks, fixed system prompt analysis, single-stock analysis, holding rotation, holding add/reduce suggestions, or empty-position cash deployment suggestions.
---

# Akshare Online Alpha

Use this skill when the user wants Wyckoff-style analysis with online data fetch and source fallback.

## Input Schema

Single/multi symbol analysis:
- Inputs: stock code(s), optional CSV, optional chart image, text goals.

Portfolio decision analysis:
- `holdings` (can be empty): `[股票A+成本+数量, 股票B+成本+数量, ...]`
- `cash`: available cash amount
- `candidate` (optional): stock code not currently in holdings
- Optional CSV/image/text instructions are still supported.

Portfolio example:
- `holdings = [600519+1450+100, 000001+10.2+3000]`
- `cash = 80000`
- `candidate = 300750`

## When To Use / Not Use

Use this skill when at least one condition is true:
- User provides stock code(s) and asks for current/near-current analysis.
- User provides holdings + cash + candidate and asks whether to switch positions.
- User asks whether current holdings should be increased/reduced/kept.
- User has no holdings and asks how to act with available cash.
- User asks to combine CSV + online validation.
- User provides chart image and asks for Wyckoff interpretation.

Do not use this skill when:
- User only asks for generic Python/chart debugging unrelated to market analysis.
- User requests purely offline historical analysis with no online data requirement.

## Auto Intent Inference

When `holdings/cash/candidate` are provided, do not require the user to say "switch / add / reduce / empty-position".

Infer automatically from provided fields:
- `holdings` non-empty + `candidate` provided: include rotation comparison and per-holding actions.
- `holdings` non-empty + no `candidate`: provide per-holding add/reduce/hold/exit suggestions.
- `holdings` empty + `cash` provided: provide empty-position cash deployment suggestion.

## Required Execution Order

1. Validate input and parse structured fields:
- Determine symbol-only flow or portfolio flow from input fields.
- CSV (if provided): main source for historical structure.
- Text instructions: constraints and goals.
- Image (if provided): supplemental intraday/micro-structure signal.
- In portfolio flow, parse `holdings/cash/candidate(optional)` before analysis.

2. Resolve current Beijing time before any trading suggestion:
- Fetch actual current time from tool/system.
- Convert to `Asia/Shanghai`.
- Print `当前北京时间：YYYY-MM-DD HH:MM（UTC+8）`.
- Determine if in A-share continuous auction window.

3. Enforce trading-session rules:
- If not in tradable session, only provide post-market review/next-day plan/order strategy.
- Do not output immediate intraday execution commands.

4. Fetch data with online source switching:
- Use `rules/source-fallbacks.md` order.
- For each symbol, keep source audit log.
- If source fails, schema check fails, or rows are insufficient, switch source.
- In portfolio flow, fetch all holding symbols and candidate symbol when provided.

5. Perform Wyckoff analysis first:
- Analyze latest 500 days structure with MA50/MA200.
- Identify phases/events without forcing full phase set.
- Allow event-date news checks only for verification, not as decision basis.

6. In portfolio flow, produce a Wyckoff-style portfolio recommendation:
- For each holding, give one action: `add / reduce / hold / exit`.
- If candidate is provided, compare candidate vs current holdings from structure strength, phase position, and event quality.
- If candidate is provided, identify which current holding is structurally weakest and whether rotation is needed.
- If holdings are empty, provide an empty-position suggestion using available cash and current structure context.
- Use `cost/qty/cash` to give concrete action suggestions in narrative form.
- Keep final recommendation in Wyckoff tone and clearly state action labels such as `switch / partial switch / hold / add / reduce`.

7. Plot only when allowed:
- If current time is intraday trading time, skip plotting.
- Otherwise generate plotting code/result using hard rendering constraints from system prompt.

## Fixed Output Contract

Always output in this order:
1. `当前北京时间：YYYY-MM-DD HH:MM（UTC+8）`
2. Trading verdict:
- `当前是否可盘中交易：是/否`
- If no: `当前不可盘中交易（原因：...）`
3. Data audit table per symbol:
- `symbol`
- `source_used`
- `rows_kept`
- `window_end_date`
- `fallback_count`
4. Wyckoff analysis result:
- Current cycle background and phase (only what is evidenced).
- Key events (SC/ST/Spring/LPS/SOS/UTAD if present) with concise rationale.
- Action boundaries respecting T+1 and current session status.
5. Portfolio action section (portfolio flow only):
- Holdings snapshot from provided `cost/qty/cash`.
- Per-holding action suggestions (`add / reduce / hold / exit`) with reasoning.
- Candidate vs weakest holding comparison (if candidate is provided).
- Empty-position cash action suggestion (if holdings are empty).
- Final action summary in Wyckoff tone.
6. Plotting section (only when allowed by session rules):
- Python code and/or generated chart result with Chinese annotation constraints.

## Failure And Degrade Rules

- If all data sources fail for a symbol, report that symbol as `data_unavailable` and continue with remaining symbols.
- If fewer than 30 valid rows are available, do not force phase labeling; return "insufficient structure depth".
- If image is unreadable, explicitly state parse failure reason and continue with text/CSV path.
- Never invent OHLCV rows, event timestamps, or trading-day status.

## Hard Constraints

- Do not change the fixed prompt wording unless explicitly requested.
- Do not fabricate missing OHLCV rows.
- Do not ignore image input if image is parseable.
- Do not use opaque white text boxes in chart annotations.
- If fetching data requires running Python scripts, run them only in a sandboxed environment.
- Prefer direct web/API fetch first; use Python scripts only when needed for fallback, parsing, or normalization.

## Resources

- `rules/alpha-system-prompt.md`: fixed role and hard rules.
- `rules/source-fallbacks.md`: online source switching policy.
