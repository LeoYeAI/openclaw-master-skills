---
name: stock-market-pro
description: >-
  Yahoo Finance (yfinance) powered stock analysis skill: quotes, fundamentals,
  ASCII trends, high-resolution charts (RSI/MACD/BB/VWAP/ATR), plus optional
  web add-ons (news + browser-first options/flow).
---

# Stock Market Pro

**Stock Market Pro** is a fast, local-first market research toolkit.
Get clean price + fundamentals, generate publication-ready charts with indicator panels (RSI/MACD/BB/VWAP/ATR), and run a one-shot report that outputs both a summary and a high-res PNG.
Optional add-ons: quick news link sweep (DDG) + browser-first options/flow (Unusual Whales).

## What you can do
- Get **real-time quotes** (price + change)
- Summarize **fundamentals** (Market Cap, Forward PE, EPS, ROE)
- Print **ASCII trends** (terminal-friendly)
- Generate **high-resolution PNG charts** with overlays/panels:
  - RSI / MACD / Bollinger Bands / VWAP / ATR
- Run a **one-shot report** that prints a compact summary and emits a chart path
- Search **news links** via DuckDuckGo (ddgs)
- Open **options / flow pages** (browser-first, Unusual Whales)

---

## Commands (Local)

> This skill uses `uv run --script` for dependency handling.
> If you don't have `uv`: install from https://github.com/astral-sh/uv

### 1) Quotes
```bash
uv run --script scripts/yf.py price TSLA
# shorthand
uv run --script scripts/yf.py TSLA
```

### 2) Fundamentals
```bash
uv run --script scripts/yf.py fundamentals NVDA
```

### 3) ASCII trend
```bash
uv run --script scripts/yf.py history AAPL 6mo
```

### 4) Pro chart (PNG)
```bash
# candlestick (default)
uv run --script scripts/yf.py pro 000660.KS 6mo

# line chart
uv run --script scripts/yf.py pro 000660.KS 6mo line
```

#### Indicators (optional)
```bash
uv run --script scripts/yf.py pro TSLA 6mo --rsi --macd --bb
uv run --script scripts/yf.py pro TSLA 6mo --vwap --atr
```

- `--rsi` : RSI(14)
- `--macd`: MACD(12,26,9)
- `--bb`  : Bollinger Bands(20,2)
- `--vwap`: VWAP (cumulative over the selected range)
- `--atr` : ATR(14)

### 5) One-shot report
Prints a compact text summary and generates a chart PNG.

```bash
uv run --script scripts/yf.py report 000660.KS 6mo
# output includes: CHART_PATH:/tmp/<...>.png
```

> Optional web add-ons (news/options) can be appended by the agent workflow.

---

## Web Add-ons (Optional)

### A) News search (DuckDuckGo via `ddgs`)
This skill vendors a helper script (`scripts/ddg_search.py`).

Dependency:
```bash
pip3 install -U ddgs
```

Run:
```bash
python3 scripts/news.py NVDA --max 8
# or
python3 scripts/ddg_search.py "NVDA earnings guidance" --kind news --max 8 --out md
```

### B) Options / Flow (browser-first)
Unusual Whales frequently blocks scraping/headless access.
So the recommended approach is: **open the pages in a browser and summarize what you can see**.

Quick link helper:
```bash
python3 scripts/options_links.py NVDA
```

Common URLs:
- `https://unusualwhales.com/stock/{TICKER}/overview`
- `https://unusualwhales.com/live-options-flow?ticker_symbol={TICKER}`
- `https://unusualwhales.com/stock/{TICKER}/options-flow-history`

---

## Subcommands (yf.py)
`yf.py` supports:
- `price`
- `fundamentals`
- `history`
- `pro`
- `chart` (alias)
- `report`
- `option` (best-effort; browser fallback recommended)

Check:
```bash
python3 scripts/yf.py --help
```

## Ticker examples
- US: `AAPL`, `NVDA`, `TSLA`
- KR: `005930.KS`, `000660.KS`
- Crypto: `BTC-USD`, `ETH-KRW`
- FX: `USDKRW=X`
