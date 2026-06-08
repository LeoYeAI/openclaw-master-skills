---
name: horizon-trader
version: 0.4.16
description: "v0.4.16 - Trade prediction markets (Polymarket, Kalshi) - positions, orders, risk management, Kelly sizing, wallet analytics, Monte Carlo, arbitrage, quantitative analytics, AFML (bars, labeling, fractional differentiation, HRP, denoising), multi-strategy orchestration, alpha research, tier-gated features, and market discovery."
emoji: "\U0001F4C8"
metadata:
  openclaw:
    requires:
      env:
        - HORIZON_API_KEY
    primaryEnv: HORIZON_API_KEY
    install:
      - id: pip
        kind: uv
        formula: horizon-sdk
        label: "Horizon SDK (pip install horizon-sdk)"
    homepage: https://docs.openclaw.ai/tools/clawhub
---

# Horizon Trader

You are a prediction market trading assistant powered by the Horizon SDK.

## When to use this skill

Use this skill when the user asks about:
- Checking their **positions**, **PnL**, or **portfolio status**
- **Submitting** or **canceling** orders on prediction markets
- **Discovering** or **searching** for markets or events on Polymarket or Kalshi
- Computing **Kelly-optimal** position sizes
- Managing **risk** controls (kill switch, stop-loss, take-profit)
- Checking **feed** prices or market data
- Looking up **wallet** activity, trades, positions, or profiles on Polymarket
- Analyzing **trade flow** or **top holders** for a market
- Running **Monte Carlo simulations** on portfolio risk
- Executing **cross-exchange arbitrage**
- Anything related to **prediction market trading**

## How to use

Run commands via the CLI script. All output is JSON.

```bash
python3 {baseDir}/scripts/horizon.py <command> [args...]
```

## Available commands

### Portfolio & Status
```bash
# Engine status: PnL, open orders, positions, kill switch, uptime
python3 {baseDir}/scripts/horizon.py status

# List all open positions
python3 {baseDir}/scripts/horizon.py positions

# List open orders (optionally for a specific market)
python3 {baseDir}/scripts/horizon.py orders [market_id]

# List recent fills
python3 {baseDir}/scripts/horizon.py fills
```

### Trading
```bash
# Submit a limit order: quote <market_id> <side> <price> <size> [market_side]
# side: buy or sell, price: 0-1 (probability), market_side: yes or no (default: yes)
python3 {baseDir}/scripts/horizon.py quote <market_id> buy 0.55 10
python3 {baseDir}/scripts/horizon.py quote <market_id> sell 0.40 5 no

# Cancel a single order
python3 {baseDir}/scripts/horizon.py cancel <order_id>

# Cancel all orders
python3 {baseDir}/scripts/horizon.py cancel-all

# Cancel all orders for a specific market
python3 {baseDir}/scripts/horizon.py cancel-market <market_id>
```

### Market Discovery
```bash
# Search for markets on an exchange
python3 {baseDir}/scripts/horizon.py discover <exchange> [query] [limit] [market_type] [category]
# market_type: "all" (default), "binary", or "multi"
# category: tag filter (e.g., "crypto", "politics", "sports") - uses server-side filtering

# Examples:
python3 {baseDir}/scripts/horizon.py discover polymarket "bitcoin"
python3 {baseDir}/scripts/horizon.py discover kalshi "election" 5
python3 {baseDir}/scripts/horizon.py discover polymarket "election" 10 multi
python3 {baseDir}/scripts/horizon.py discover polymarket "" 10 binary
python3 {baseDir}/scripts/horizon.py discover polymarket "" 20 all crypto

# Get comprehensive detail for a single market
python3 {baseDir}/scripts/horizon.py market-detail <slug_or_id> [exchange]

# Examples:
python3 {baseDir}/scripts/horizon.py market-detail will-bitcoin-reach-100k
python3 {baseDir}/scripts/horizon.py market-detail KXBTC-25FEB28 kalshi
```

### Kelly Sizing
```bash
# Compute optimal position size: kelly <prob> <price> <bankroll> [fraction] [max_size]
python3 {baseDir}/scripts/horizon.py kelly 0.65 0.50 1000
python3 {baseDir}/scripts/horizon.py kelly 0.70 0.55 2000 0.5 50
```

### Risk Management
```bash
# Activate kill switch (emergency stop - cancels all orders)
python3 {baseDir}/scripts/horizon.py kill-switch on "market crash"

# Deactivate kill switch
python3 {baseDir}/scripts/horizon.py kill-switch off

# Add stop-loss: stop-loss <market_id> <side> <order_side> <size> <trigger_price>
# side: yes or no, order_side: buy or sell
python3 {baseDir}/scripts/horizon.py stop-loss <market_id> yes sell 10 0.40

# Add take-profit: take-profit <market_id> <side> <order_side> <size> <trigger_price>
python3 {baseDir}/scripts/horizon.py take-profit <market_id> yes sell 10 0.80
```

### Feed Data & Health
```bash
# Get snapshot for a named feed
python3 {baseDir}/scripts/horizon.py feed <feed_name>

# List all feeds
python3 {baseDir}/scripts/horizon.py feeds

# Start a live data feed: start-feed <name> <feed_type> [config_json]
# feed_type: binance_ws, polymarket_book, kalshi_book, predictit,
#            manifold, espn, nws, chainlink, rest_json_path, rest
# Note: URL-based feeds (chainlink, rest_json_path, rest) require HTTPS public URLs.
python3 {baseDir}/scripts/horizon.py start-feed eth_usd chainlink '{"contract_address":"0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419","rpc_url":"https://eth.llamarpc.com"}'
python3 {baseDir}/scripts/horizon.py start-feed mf manifold '{"slug":"will-btc-hit-100k"}'

# Check feed staleness and health (optional threshold in seconds, default 30)
python3 {baseDir}/scripts/horizon.py feed-health [threshold]

# Get connection metrics for a feed (or all feeds)
python3 {baseDir}/scripts/horizon.py feed-metrics [feed_name]

# Check YES/NO price parity (optionally specify feed)
python3 {baseDir}/scripts/horizon.py parity <market_id> [feed_name]
```

### Contingent Orders
```bash
# List pending stop-loss/take-profit orders
python3 {baseDir}/scripts/horizon.py contingent
```

### Event Discovery
```bash
# Discover multi-outcome events on Polymarket
python3 {baseDir}/scripts/horizon.py discover-events "election"
python3 {baseDir}/scripts/horizon.py discover-events "" 5

# Get top markets by volume
python3 {baseDir}/scripts/horizon.py top-markets polymarket 10
python3 {baseDir}/scripts/horizon.py top-markets kalshi 5 "KXBTC"
```

### Wallet Analytics (Polymarket - no auth required)
```bash
# Trade history for a wallet
python3 {baseDir}/scripts/horizon.py wallet-trades 0x1234... [limit] [condition_id]

# Trade history for a market
python3 {baseDir}/scripts/horizon.py market-trades 0xabc... [limit] [side] [min_size]

# Open positions for a wallet (sort: TOKENS, CURRENT, CASHPNL, PERCENTPNL, etc.)
python3 {baseDir}/scripts/horizon.py wallet-positions 0x1234... 50 CURRENT

# Total portfolio value in USD
python3 {baseDir}/scripts/horizon.py wallet-value 0x1234...

# Public profile (pseudonym, bio, X handle)
python3 {baseDir}/scripts/horizon.py wallet-profile 0x1234...

# Top holders in a market
python3 {baseDir}/scripts/horizon.py top-holders 0xabc... [limit]

# Trade flow analysis (buy/sell volume, net flow, top buyers/sellers)
python3 {baseDir}/scripts/horizon.py market-flow 0xabc... [trade_limit] [top_n]
```

### Monte Carlo Simulation
```bash
# Simulate portfolio risk (uses current engine positions)
python3 {baseDir}/scripts/horizon.py simulate [scenarios] [seed]
python3 {baseDir}/scripts/horizon.py simulate 50000
python3 {baseDir}/scripts/horizon.py simulate 10000 42
```

### Arbitrage
```bash
# Execute atomic cross-exchange arb: arb <market_id> <buy_exchange> <sell_exchange> <buy_price> <sell_price> <size>
python3 {baseDir}/scripts/horizon.py arb will-btc-hit-100k kalshi polymarket 0.48 0.52 10
```

### Quantitative Analytics
```bash
# Shannon entropy for a probability
python3 {baseDir}/scripts/horizon.py entropy 0.65

# KL divergence between two distributions (comma-separated)
python3 {baseDir}/scripts/horizon.py kl-divergence 0.3,0.7 0.5,0.5

# Hurst exponent for a price series (comma-separated)
python3 {baseDir}/scripts/horizon.py hurst 0.50,0.52,0.48,0.55,0.53

# Variance ratio test for returns (comma-separated) [period]
python3 {baseDir}/scripts/horizon.py variance-ratio 0.01,-0.02,0.03,-0.01,0.02

# Cornish-Fisher VaR/CVaR (comma-separated returns) [confidence]
python3 {baseDir}/scripts/horizon.py cf-var 0.01,-0.02,0.03,-0.05,0.02 0.95

# Prediction Greeks: greeks <price> <size> [is_yes] [t_hours] [vol]
python3 {baseDir}/scripts/horizon.py greeks 0.55 100 true 24 0.2

# Deflated Sharpe ratio: deflated-sharpe <sharpe> <n_obs> <n_trials> [skew] [kurt]
python3 {baseDir}/scripts/horizon.py deflated-sharpe 1.5 252 10

# Signal diagnostics (comma-separated predictions and outcomes)
python3 {baseDir}/scripts/horizon.py signal-diagnostics 0.6,0.3,0.8 1,0,1

# Market efficiency test (comma-separated prices)
python3 {baseDir}/scripts/horizon.py market-efficiency 0.50,0.52,0.48,0.55,0.53,0.51

# Stress test on current positions [scenarios] [seed]
python3 {baseDir}/scripts/horizon.py stress-test 10000
```

### Portfolio Management
```bash
# Get portfolio metrics (value, PnL, exposure, diversification)
python3 {baseDir}/scripts/horizon.py portfolio

# Compute optimal portfolio weights
python3 {baseDir}/scripts/horizon.py portfolio-weights equal
python3 {baseDir}/scripts/horizon.py portfolio-weights kelly
python3 {baseDir}/scripts/horizon.py portfolio-weights risk_parity
python3 {baseDir}/scripts/horizon.py portfolio-weights min_variance
```

### Hot-Reload Parameters
```bash
# Update runtime parameters (hot-reload, takes effect next cycle)
python3 {baseDir}/scripts/horizon.py update-params '{"spread": 0.05, "gamma": 0.3}'

# Get all current runtime parameters
python3 {baseDir}/scripts/horizon.py get-params
```

### Tearsheet Analytics
```bash
# Generate comprehensive tearsheet from equity curve CSV
python3 {baseDir}/scripts/horizon.py tearsheet path/to/equity.csv
```

### Bayesian Optimization
```bash
# Run GP-based Bayesian optimization for strategy parameters
# param_space: {name: [min, max]}
python3 {baseDir}/scripts/horizon.py bayesian-opt '{"spread": [0.01, 0.10], "gamma": [0.1, 1.0]}' 20 5
```

### Hawkes Process
```bash
# Compute Hawkes self-exciting intensity from event timestamps
python3 {baseDir}/scripts/horizon.py hawkes 1000.0,1000.5,1001.2 0.1 0.5 1.0
```

### Ledoit-Wolf Correlation
```bash
# Compute shrinkage covariance matrix from returns (rows=observations, cols=assets)
python3 {baseDir}/scripts/horizon.py correlation '[[0.01,0.02],[-0.01,0.03],[0.02,-0.01]]'
```

## Maker/Taker Fees (v0.4.6)

Split fees by liquidity role for more realistic paper trading and backtesting:

```python
from horizon import Engine

# Flat fee (backward compatible)
engine = Engine(paper_fee_rate=0.001)

# Split maker/taker fees
engine = Engine(
    paper_maker_fee_rate=0.0002,  # 2 bps for makers
    paper_taker_fee_rate=0.002,   # 20 bps for takers
)
```

Each `Fill` now includes an `is_maker` field (`True`/`False`) indicating whether the order was a maker or taker. Works with both the paper exchange and BookSim (L2 backtesting).

## Chainlink On-Chain Oracle Feed (v0.4.7)

Read prices directly from Chainlink aggregator contracts on any EVM chain:

```python
import horizon as hz

hz.run(
    feeds={
        "eth_usd": hz.ChainlinkFeed(
            contract_address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
            rpc_url="https://eth.llamarpc.com",
        ),
    },
    ...
)
```

Common contract addresses (Ethereum mainnet):
- ETH/USD: `0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419`
- BTC/USD: `0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c`
- LINK/USD: `0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c`

Works with Ethereum, Arbitrum, Polygon, BSC — just change `rpc_url`.

## New Data Feeds (v0.4.5)

Five new feed types for cross-market signals beyond crypto:

- **PredictItFeed** - PredictIt market prices (lastTradePrice, bestBuyYesCost, bestSellYesCost)
- **ManifoldFeed** - Manifold Markets probability and volume
- **ESPNFeed** - Live sports scores (home/away score, period, game status)
- **NWSFeed** - National Weather Service forecasts (temperature, wind, precip) and alerts
- **RESTJsonPathFeed** - Flexible JSON path extraction from any REST API

Setup in `hz.run()`:
```python
import horizon as hz

hz.run(
    feeds={
        "pi": hz.PredictItFeed(market_id=7456, contract_id=28562),
        "manifold": hz.ManifoldFeed("will-btc-hit-100k-by-2026"),
        "nba": hz.ESPNFeed("basketball", "nba"),
        "weather": hz.NWSFeed(state="FL", mode="alerts"),
        "custom": hz.RESTJsonPathFeed(
            url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            price_path="bitcoin.usd",
        ),
    },
    ...
)
```

## Execution Algorithms (v0.4.4)

Three execution algorithms for splitting large orders with minimal market impact:

- **TWAP** (`hz.TWAP`) - Time-Weighted Average Price: equal slices at regular intervals
- **VWAP** (`hz.VWAP`) - Volume-Weighted Average Price: slices proportional to a volume profile
- **Iceberg** (`hz.Iceberg`) - Shows only a small visible portion, auto-replenishes on fill

All use the same interface: `algo.start(request)`, `algo.on_tick(price, time)`, `algo.is_complete`, `algo.total_filled`.

## Signal Combiner + Market Maker (v0.4.8)

Compose multi-signal strategies with automatic pipeline chaining:

```python
hz.run(
    pipeline=[
        hz.signal_combiner([
            hz.price_signal("book", weight=0.5),
            hz.imbalance_signal("book", levels=5, weight=0.3),
            hz.flow_signal("book", window=30, weight=0.2),
        ]),
        hz.market_maker(feed_name="book", gamma=0.5, size=5.0),
    ],
    ...
)
```

Available signals: `price_signal`, `imbalance_signal`, `spread_signal`, `momentum_signal`, `flow_signal`. The `market_maker` accepts an upstream signal value as fair value when chained after `signal_combiner`.

## Pipeline Features (v0.4.4)

The Horizon SDK also includes advanced pipeline components for automated strategies:

- **Markov Regime Detection** (`markov_regime`) - Rust HMM (Hidden Markov Model) for real-time regime classification. Baum-Welch training, Viterbi decoding, O(N^2) online forward filter per tick. Supports pre-trained models or auto-train with warmup.
- **Regime Detection** (`regime_signal`) - volatility/trend regime classification (0=calm, 1=volatile)
- **Feed Guard** (`feed_guard`) - auto-activates kill switch when feeds go stale
- **Inventory Skew** (`inventory_skewer`) - shifts quotes to reduce position risk
- **Adaptive Spread** (`adaptive_spread`) - dynamically widens/narrows spread based on fill rate, volatility, and order imbalance
- **Execution Tracker** (`execution_tracker`) - monitors fill rate, slippage, and adverse selection
- **Multi-Strategy** - run different pipelines per market via dict config
- **Cross-Market Hedging** (`cross_hedger`) - generates hedge quotes when portfolio delta exceeds threshold

### Quantitative Analytics (v0.4.4)

- **Information Theory** - Shannon entropy, joint entropy, KL divergence, mutual information, transfer entropy
- **Microstructure** - Kyle's lambda, Amihud ratio, Roll spread, effective/realized spread, LOB imbalance, microprice
- **Risk Analytics** - Cornish-Fisher VaR/CVaR, prediction Greeks (delta, gamma, theta, vega for binary markets)
- **Signal Analysis** - information coefficient (Spearman), signal half-life, Hurst exponent, variance ratio test
- **Statistical Testing** - deflated Sharpe ratio, Bonferroni correction, Benjamini-Hochberg FDR control
- **Streaming Detectors** - VPIN toxic flow, CUSUM change-point, order flow imbalance (OFI) tracker
- **Pipeline Functions** - `toxic_flow()`, `microstructure()`, `change_detector()` for real-time analytics in `hz.run()`
- **Stress Testing** - Monte Carlo under adverse scenarios (correlation spike, all-resolve-no, liquidity shock, tail risk)
- **CPCV** - Combinatorial Purged Cross-Validation with Probability of Backtest Overfitting (PBO)

### Backtesting (v0.4.4)

- **L2 Book Simulation** - replay historical orderbook snapshots with `book_data` parameter
- **Fill Models** - `deterministic`, `probabilistic` (queue position), `glft` (Gueant-Lehalle-Fernandez-Tapia)
- **Market Impact** - temporary + permanent price impact simulation
- **Latency Simulation** - configurable order-to-fill delay in ticks
- **Calibration Analytics** - Rust-powered calibration curve, Brier score, log-loss, ECE
- **Edge Decay** - measure how edge decays vs time-to-resolution
- **Walk-Forward Optimization** - rolling/expanding window parameter optimization with purge gap

These are Python pipeline functions used with `hz.run()` and `hz.backtest()`. See the SDK documentation for usage.

## New Features (v0.4.16)

### AFML (Advances in Financial Machine Learning)
Rust-native implementations of Lopez de Prado's research:
- **Information-Driven Bars** (`hz.dollar_bars`, `hz.volume_bars`, `hz.tick_bars`, `hz.tick_imbalance_bars`) - Alternative bar types that sample on information arrival
- **Triple Barrier Labeling** (`hz.triple_barrier_labels`) - Path-dependent labels with profit-taking, stop-loss, and time barriers
- **Fractional Differentiation** (`hz.frac_diff_weights`, `hz.frac_diff_fixed`) - Make series stationary while preserving memory
- **Hierarchical Risk Parity** (`hz.hrp_weights`) - Tree-clustering portfolio allocation
- **Denoised Correlation** (`hz.marchenko_pastur_bounds`, `hz.denoise_correlation`) - Random matrix theory for cleaner covariance

### Multi-Strategy Orchestration
`hz.StrategyBook` for running and monitoring multiple strategies from a single process with per-strategy PnL tracking, pause/resume, and rebalancing.

### Alpha Research Tools
- `hz.feature_importance` - MDI/MDA feature importance via random forests
- `hz.compute_bet_sizing` - Probability-to-size via linear/sigmoid/discrete scaling

### Tier-Based Feature Gating
Pro/Ultra feature gating on all premium endpoints with API key validation.

## New Features (v0.4.14)

### Tearsheet Analytics
Generate comprehensive performance reports with monthly returns, rolling Sharpe/Sortino, drawdown analysis, trade statistics, and tail ratio.

### Bayesian Optimization
Zero-dependency GP-based parameter optimizer with Expected Improvement acquisition. Finds optimal strategy parameters efficiently.

### Portfolio Management
Portfolio object with position management, analytics, and optimization (equal, Kelly, risk parity, min variance weights).

### Hot-Reload Parameters
Update strategy parameters at runtime without restart. Supports file-based or dict-based parameter sources with automatic change detection.

### Hawkes Process Pipeline
Self-exciting point process for modeling trade arrival intensity. Triggers on fills and large price jumps. Per-market isolation.

### Ledoit-Wolf Correlation Pipeline
Shrinkage covariance estimation across multiple feeds. Optimal shrinkage intensity computed via Ledoit-Wolf formula.

## Output format

All commands return JSON. On success you get the data directly. On error you get `{"error": "message"}`.

## Important notes

- The `quote` command submits **real orders** (or paper orders depending on config). Always confirm with the user before submitting.
- The `kill-switch on` command is an **emergency stop** that cancels all orders immediately.
- Prices are **probabilities** between 0 and 1 (e.g., 0.65 = 65% implied probability).
- The exchange is configured via the `HORIZON_EXCHANGE` environment variable (default: paper).

Full documentation: https://docs.openclaw.ai/tools/clawhub
