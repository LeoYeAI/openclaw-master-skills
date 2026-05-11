# BTC Signals Pro for OpenClaw

Empower your OpenClaw AI agent with institutional-grade Bitcoin trading intelligence. This skill connects your local agent to over 50+ real-time data sources, providing AI-driven market analysis, derivatives flow, liquidation heatmaps, and macroeconomic calendars entirely through natural conversation.

## 🚀 What Your Agent Can Do Now

Instead of staring at charts and scanning Twitter, just ask your OpenClaw agent:

* **Market Snapshot:** *"What's Bitcoin doing right now? Give me the current trade score and Fear & Greed index."*
* **Contrarian Intel:** *"Are retail traders mostly long or short on Binance right now? Where are the nearest liquidation pools?"*
* **Trade Setups:** *"Give me a short-term scalp trade setup for BTC right now including stop loss, take profit targets, and the AI rationale."*
* **Macro & News:** *"Are there any high-impact economic events on the calendar today? Summarize the latest breaking crypto news."*
* **Deep Technicals:** *"Where is the strongest price confluence acting as a magnet below the current price?"*

## 🔒 Security & Privacy

We know crypto tools require the highest level of trust. 
* **Zero File System Access:** This skill only requests network access to query the secure `api.btcsignals.pro` endpoints. It cannot read, write, or access your local files.
* **Local Execution:** All AI processing of the data happens locally through your OpenClaw instance.
* **Credential Safety:** Your API key is stored securely in your OpenClaw config and is never printed in chat or shared with third parties.

## ⚙️ Installation & Setup

1. Install the skill via ClawHub:
   `clawhub install ricklaughhunn/btc-signals-pro`
2. This skill requires a Pro data plan to access the API endpoints. Get your API key at [btcsignals.pro/pricing](https://btcsignals.pro/pricing).
3. Add the key to your OpenClaw config when prompted, or manually update your config:
   `BTC_SIGNALS_API_KEY: "your_api_key_here"`

## 📊 Features Under the Hood

* **Unified Confluence Engine:** Maps ~49 weighted levels (pivots, fibs, VP).
* **Derivatives Flow:** Tracks CVD, Open Interest, Funding Rates, and ETF flows.
* **Live Economic Calendar:** FMP-powered macroeconomic event tracking (FOMC, CPI, NFP) to protect against sudden volatility.

---

**Disclaimer:** *This skill and the data provided by the BTC Signals Pro API are for informational, educational, and entertainment purposes only. It does not constitute financial advice, and should not be used as the sole basis for business or investment decisions. Always do your own research.*

---
**Tags:** `finance`, `crypto`, `bitcoin`, `trading`, `data-analysis`, `market-data`, `automation`, `investing`