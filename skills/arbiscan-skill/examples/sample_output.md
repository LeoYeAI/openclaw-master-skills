# ArbiScan v0.2.0 Sample Output

> Scanned at 2026-03-14 05:30 UTC | 12 scan types | 4 exchanges

## Arbitrage Scans

### Funding Rate Arbitrage

| Symbol    | Long (低费率)        | Short (高费率)      | Rate Diff   | Est. APY%   | Risk   | Window |
|-----------|---------------------|---------------------|-------------|-------------|--------|--------|
| FILUSDT   | Binance -0.0799%    | Bitget -0.0104%     | 0.0695%     | 76.1%       | HIGH   | ~8h    |
| SEIUSDT   | Binance -0.0317%    | OKX -0.0026%        | 0.0291%     | 31.9%       | MEDIUM | ~8h    |
| BTCUSDT   | Binance -0.0027%    | OKX 0.0064%         | 0.0091%     | 10.0%       | LOW    | ~8h    |
| SOLUSDT   | Binance -0.0103%    | Bybit -0.0004%      | 0.0100%     | 10.9%       | LOW    | ~8h    |

> 28 opportunities found

### Basis Arbitrage (Spot vs Futures)

| Symbol    | Exchange | Spot Price | Futures Price | Basis%   | Direction     | Risk   |
|-----------|----------|------------|---------------|----------|---------------|--------|
| WIFUSDT   | Binance  | $0.16      | $0.16         | -0.5488% | Backwardation | MEDIUM |
| LINKUSDT  | Binance  | $8.93      | $8.91         | -0.1904% | Backwardation | MEDIUM |
| ETHUSDT   | Binance  | $2021.11   | $2020.06      | -0.0520% | Backwardation | LOW    |

> 25 opportunities found

### Cross-Exchange Futures Spread

| Symbol    | Buy From          | Sell To            | Low Price  | High Price | Spread% | Risk   |
|-----------|-------------------|--------------------|------------|------------|---------|--------|
| LTCUSDT   | Bitget $53.89     | Binance $53.96     | $53.89     | $53.96     | 0.1298% | MEDIUM |
| BNBUSDT   | OKX $641.00       | Binance $641.50    | $641.00    | $641.50    | 0.0780% | LOW    |

> 24 opportunities found

## Monitoring Scans

### Open Interest Monitor

| Symbol    | Total OI (USDT) | Top Exchange     | Share% | Status       |
|-----------|-----------------|------------------|--------|--------------|
| BTCUSDT   | $2,979,093      | OKX (95.6%)      | 95.6%  | CONCENTRATED |
| DOGEUSDT  | $2,935,208,407  | Binance (64.4%)  | 64.4%  | CONCENTRATED |
| SOLUSDT   | $18,601,879     | Binance (51.4%)  | 51.4%  | MODERATE     |

### 24h Price Movers

| Symbol    | Exchange | Price       | 24h Change% | 24h Volume (USDT) | Direction |
|-----------|----------|-------------|-------------|-------------------|-----------|
| ARBUSDT   | Binance  | $0.1017     | -2.59%      | $41,804,011       | DUMP      |
| FILUSDT   | Binance  | $0.8700     | -2.47%      | $103,375,262      | DUMP      |
| SEIUSDT   | Bybit    | $0.0664     | +0.54%      | $15,798,499       | PUMP      |

### Volume Anomaly Detection

| Symbol    | Total Vol (USDT) | Top Exchange | Vol Share% | 24h Change% | Signal       |
|-----------|------------------|--------------|------------|-------------|--------------|
| DOGEUSDT  | $2,100,000,000   | OKX          | 85.5%      | -1.10%      | VOLUME SPIKE |
| BTCUSDT   | $25,000,000,000  | Binance      | 58.2%      | -0.78%      | ACCUMULATION |

### Stablecoin Depeg Monitor

| Stablecoin | Exchange | Price (USDT) | Depeg%  | Status |
|------------|----------|--------------|---------|--------|
| TUSD       | Binance  | $0.999700    | -0.0300%| STABLE |
| USDC       | Binance  | $1.000000    | +0.0000%| STABLE |

## Signal Scans

### Funding Rate History Trend

| Symbol    | Exchange | Streak     | Direction | Avg Rate | Est. APY% | Stability  |
|-----------|----------|------------|-----------|----------|-----------|------------|
| BTCUSDT   | Binance  | 20 periods | NEGATIVE  | -0.0050% | 5.5%      | VERY STABLE|
| ETHUSDT   | OKX      | 12 periods | POSITIVE  | 0.0080%  | 8.8%      | STABLE     |
| FILUSDT   | Binance  | 7 periods  | NEGATIVE  | -0.0900% | 98.6%     | EMERGING   |

> 22 trending symbols found

### Long/Short Ratio

| Symbol    | Exchange | Long%  | Short% | Ratio | Signal                        |
|-----------|----------|--------|--------|-------|-------------------------------|
| WIFUSDT   | Binance  | 72.3%  | 27.7%  | 2.61  | LONG HEAVY                    |
| DOGEUSDT  | Bybit    | 31.5%  | 68.5%  | 0.46  | SHORT HEAVY                   |
| BTCUSDT   | Binance  | 54.5%  | 45.5%  | 1.20  | MODERATE                      |

> 41 extreme ratios found

### New Listing Detection

| Symbol       | Available On     | Missing From              | Exclusivity | Signal                     |
|--------------|------------------|---------------------------|-------------|----------------------------|
| NEWTOKENUSDT | Bitget           | Binance, Bybit, OKX       | 1/4         | EXCLUSIVE - high premium   |
| ALPHATOKEN   | Binance, Bybit   | OKX, Bitget               | 2/4         | LIMITED - moderate premium |

> 522 exclusive/limited listings found

## How to Read This

- **Risk**: LOW (major coin + APY<10%), MEDIUM (APY 10-50% or non-major), HIGH (APY>50% or non-major + APY>20%)
- **Status** (OI): BALANCED (<45%), MODERATE (45-60%), CONCENTRATED (>60%)
- **Signal** (Volume): NORMAL, ACCUMULATION (high vol + low change), VOLUME SPIKE (>70% share), MOMENTUM (high change)
- **Stability** (Funding Trend): EMERGING (5-9 periods), STABLE (10-14), VERY STABLE (15+)
- **Exclusivity** (New Listing): 1/4 = only on 1 exchange, 2/4 = on 2 exchanges

## Disclaimer

These are **theoretical opportunities**. Actual returns depend on execution costs, slippage, transfer times, and exchange risks. This is not financial advice.
