# Source Fallbacks (Online Fetch)

Use this order for each symbol:

1. Eastmoney / Akshare public endpoints (preferred)
- Reason: stable A-share coverage and daily bars.

2. Sina Finance historical endpoints
- Reason: good backup for daily K data.

3. Tencent quote/history endpoints
- Reason: useful fallback when above sources fail.

4. Other reputable financial pages with machine-readable tables
- Example: exchange pages or major portal historical data tables.

## Symbol Normalization

Before fetching:
- Normalize symbol to market-qualified format when possible (for example, `600000.SH`, `000001.SZ`).
- Preserve the original user input in output as `symbol_input`.
- Use normalized symbol for source queries and audit logging.

## Query Guidance

For each symbol, use at least one query pattern:
- `<symbol> A股 日线 OHLCV 历史`
- `<symbol> Eastmoney 历史行情`
- `<symbol> 新浪 财经 K线`

## Completeness Checks

A valid symbol dataset must satisfy:
- Has columns equivalent to `date, open, high, low, close, volume`.
- Has at least 30 daily rows (target 60).
- Date sequence is parseable.
- No duplicate dates after normalization.
- Numeric columns are parseable after stripping commas/units if needed.

If checks fail, switch source immediately.

## Column Mapping Rules

Map source-specific columns into canonical schema:
- `date`
- `open`
- `high`
- `low`
- `close`
- `volume`

If a source cannot be safely mapped to this schema, treat it as failed and fallback.

## Post-Merge Hygiene

After selecting final source:
- Sort by `date` ascending.
- Deduplicate by `date` (keep the most complete row).
- Keep only canonical OHLCV columns for downstream analysis.
- Record final row count after cleaning as `rows_kept`.

## Audit Requirement

Track for each symbol:
- `symbol_input`
- `symbol_normalized`
- `source_used`
- `rows_kept`
- `window_end_date`
- `fallback_count`
