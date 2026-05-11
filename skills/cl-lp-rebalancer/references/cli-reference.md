# onchainos CLI Reference for CL LP Rebalancer

本文档覆盖 CL LP 自动调仓策略使用的所有 `onchainos` CLI 命令。

## Prerequisites

```bash
which onchainos  # must be installed
# Auth via environment variables (from 1Password or .env)
OKX_API_KEY=...
OKX_SECRET_KEY=...
OKX_PASSPHRASE=...
```

---

## DeFi Commands

### `onchainos defi search`

搜索 DeFi 协议中的投资机会（池子）。

```bash
onchainos defi search --chain base --keyword "ETH USDC"
```

| Parameter | Required | Description |
|---|---|---|
| `--chain` | Yes | Chain name or ID (e.g., `base`, `8453`) |
| `--keyword` | Yes | Search keyword (e.g., `"ETH USDC"`) |

**Returns**:
```json
[
  {
    "investmentId": "uniswap-v3-base-eth-usdc-3000",
    "investmentName": "ETH/USDC 0.3%",
    "platform": "Uniswap V3",
    "chainId": "8453",
    "tokenSymbols": ["ETH", "USDC"],
    "tvl": "12345678.90",
    "apy": "15.5"
  }
]
```

---

### `onchainos defi detail`

获取投资池的详细信息（token 地址、fee tier、tick spacing 等）。

```bash
onchainos defi detail --investment-id uniswap-v3-base-eth-usdc-3000 --chain base
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |

**Returns**:
```json
{
  "investmentId": "uniswap-v3-base-eth-usdc-3000",
  "platform": "Uniswap V3",
  "token0": {
    "address": "0x4200000000000000000000000000000000000006",
    "symbol": "WETH",
    "decimals": 18
  },
  "token1": {
    "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "symbol": "USDC",
    "decimals": 6
  },
  "feeTier": 3000,
  "tickSpacing": 60,
  "currentTick": -197760,
  "sqrtPriceX96": "..."
}
```

---

### `onchainos defi calculate-entry`

根据指定的 tick 范围计算最优入金比例。

```bash
onchainos defi calculate-entry \
  --investment-id uniswap-v3-base-eth-usdc-3000 \
  --chain base \
  --tick-lower -198120 \
  --tick-upper -197400
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |
| `--tick-lower` | Yes | Lower tick boundary |
| `--tick-upper` | Yes | Upper tick boundary |

**Returns**:
```json
{
  "token0Amount": "0.05",
  "token1Amount": "100.0",
  "token0Ratio": 0.52,
  "token1Ratio": 0.48
}
```

**Usage**: 调仓前先调用此命令，计算需要 swap 多少代币才能达到正确比例。

---

### `onchainos defi deposit`

向 Uniswap V3 池添加集中流动性。

```bash
onchainos defi deposit \
  --investment-id uniswap-v3-base-eth-usdc-3000 \
  --chain base \
  --amount0 50000000000000000 \
  --amount1 100000000 \
  --tick-lower -198120 \
  --tick-upper -197400
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |
| `--amount0` | Yes | Token0 amount (smallest unit, e.g., wei for ETH) |
| `--amount1` | Yes | Token1 amount (smallest unit, e.g., 1e6 for USDC) |
| `--tick-lower` | Yes | Lower tick boundary |
| `--tick-upper` | Yes | Upper tick boundary |

**Returns**:
```json
{
  "tokenId": "123456",
  "txHash": "0x...",
  "liquidity": "1234567890"
}
```

**Note**: amount0/amount1 使用最小单位。ETH = wei (1e18), USDC = 1e6。

---

### `onchainos defi redeem`

移除流动性（部分或全部）。

```bash
onchainos defi redeem \
  --investment-id uniswap-v3-base-eth-usdc-3000 \
  --chain base \
  --token-id 123456 \
  --percent 100
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |
| `--token-id` | Yes | NFT position token ID |
| `--percent` | Yes | Percentage to redeem (1-100) |

**Returns**:
```json
{
  "txHash": "0x...",
  "amount0": "50000000000000000",
  "amount1": "100000000"
}
```

---

### `onchainos defi claim`

领取累积的交易手续费。

```bash
onchainos defi claim \
  --investment-id uniswap-v3-base-eth-usdc-3000 \
  --chain base \
  --token-id 123456
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |
| `--token-id` | Yes | NFT position token ID |

**Returns**:
```json
{
  "txHash": "0x...",
  "fees0": "1000000000000000",
  "fees1": "2500000"
}
```

**Note**: fees0/fees1 为最小单位。ETH fees0 = 0.001 ETH, USDC fees1 = 2.5 USDC。

---

### `onchainos defi positions`

查询当前钱包在指定链上的所有 DeFi 头寸。

```bash
onchainos defi positions --chain base
```

| Parameter | Required | Description |
|---|---|---|
| `--chain` | Yes | Chain name or ID |

**Returns**:
```json
[
  {
    "investmentId": "uniswap-v3-base-eth-usdc-3000",
    "tokenId": "123456",
    "tickLower": -198120,
    "tickUpper": -197400,
    "liquidity": "1234567890",
    "token0Amount": "0.05",
    "token1Amount": "100.0",
    "unclaimedFees0": "0.001",
    "unclaimedFees1": "2.5"
  }
]
```

---

### `onchainos defi position-detail`

获取单个头寸的详细信息。

```bash
onchainos defi position-detail \
  --investment-id uniswap-v3-base-eth-usdc-3000 \
  --chain base \
  --token-id 123456
```

| Parameter | Required | Description |
|---|---|---|
| `--investment-id` | Yes | Pool investment ID |
| `--chain` | Yes | Chain name or ID |
| `--token-id` | Yes | NFT position token ID |

**Returns**:
```json
{
  "tokenId": "123456",
  "tickLower": -198120,
  "tickUpper": -197400,
  "priceLower": "1950.00",
  "priceUpper": "2150.00",
  "liquidity": "1234567890",
  "token0Amount": "0.05",
  "token1Amount": "100.0",
  "token0ValueUsd": "105.0",
  "token1ValueUsd": "100.0",
  "totalValueUsd": "205.0",
  "unclaimedFees0": "0.001",
  "unclaimedFees1": "2.5",
  "unclaimedFeesUsd": "4.60",
  "inRange": true
}
```

---

## Market Commands

### `onchainos market price`

获取代币当前价格。

```bash
onchainos market price --address 0x4200000000000000000000000000000000000006 --chain base
```

| Parameter | Required | Description |
|---|---|---|
| `--address` | Yes | Token contract address |
| `--chain` | Yes | Chain name or ID |

**Returns**:
```json
{
  "price": "2090.45",
  "symbol": "WETH",
  "timestamp": 1710000000
}
```

---

### `onchainos market kline`

获取 K 线（OHLCV）数据，用于 ATR 计算。

```bash
onchainos market kline \
  --address 0x4200000000000000000000000000000000000006 \
  --chain base \
  --bar 1H \
  --limit 24
```

| Parameter | Required | Description |
|---|---|---|
| `--address` | Yes | Token contract address |
| `--chain` | Yes | Chain name or ID |
| `--bar` | Yes | Candle interval: `1m`, `5m`, `15m`, `1H`, `4H`, `1D` |
| `--limit` | No | Number of candles (default: 100, max: 1000) |

**Returns**:
```json
[
  {
    "ts": 1710000000,
    "open": "2080.00",
    "high": "2095.50",
    "low": "2075.30",
    "close": "2090.45",
    "volume": "1234.56"
  }
]
```

**ATR Calculation**:
```python
def calc_atr(candles):
    trs = []
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    return sum(trs) / len(trs) if trs else 0
```

---

## Swap Commands

### `onchainos swap quote`

获取 swap 报价（不执行）。

```bash
onchainos swap quote \
  --from 0x4200000000000000000000000000000000000006 \
  --to 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --amount 1000000000000000000 \
  --chain base
```

| Parameter | Required | Description |
|---|---|---|
| `--from` | Yes | Source token address |
| `--to` | Yes | Destination token address |
| `--amount` | Yes | Amount in smallest unit |
| `--chain` | Yes | Chain name or ID |

**Returns**:
```json
{
  "fromTokenAmount": "1000000000000000000",
  "toTokenAmount": "2090450000",
  "priceImpact": "0.01",
  "estimatedGas": "150000"
}
```

**Note**: 可用于获取价格（quote 1 ETH → 得到 USDC 价格）。

---

### `onchainos swap swap`

执行代币兑换。

```bash
onchainos swap swap \
  --from 0x4200000000000000000000000000000000000006 \
  --to 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --amount 50000000000000000 \
  --chain base \
  --wallet 0xYourWalletAddress \
  --slippage 1
```

| Parameter | Required | Description |
|---|---|---|
| `--from` | Yes | Source token address |
| `--to` | Yes | Destination token address |
| `--amount` | Yes | Amount in smallest unit |
| `--chain` | Yes | Chain name or ID |
| `--wallet` | Yes | Wallet address for signing |
| `--slippage` | No | Slippage tolerance in % (default: 1) |

**Returns**:
```json
{
  "txHash": "0x...",
  "fromAmount": "50000000000000000",
  "toAmount": "104500000"
}
```

---

### `onchainos swap approve`

授权代币给 DEX router（ERC-20 approve）。

```bash
onchainos swap approve \
  --token 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --amount 115792089237316195423570985008687907853269984665640564039457584007913129639935 \
  --chain base
```

| Parameter | Required | Description |
|---|---|---|
| `--token` | Yes | Token contract address to approve |
| `--amount` | Yes | Approval amount (use max uint256 for unlimited) |
| `--chain` | Yes | Chain name or ID |

**Returns**:
```json
{
  "txHash": "0x...",
  "approved": true
}
```

**Note**: 通常在首次 deposit 或 swap 前调用一次，之后缓存 approval 状态。

---

## Common Patterns

### Full Rebalance Flow

```bash
# 1. Claim accumulated fees
onchainos defi claim --investment-id $POOL --chain base --token-id $NFT

# 2. Remove all liquidity
onchainos defi redeem --investment-id $POOL --chain base --token-id $NFT --percent 100

# 3. Calculate optimal ratio for new range
onchainos defi calculate-entry --investment-id $POOL --chain base \
  --tick-lower $NEW_LOWER --tick-upper $NEW_UPPER

# 4. Swap to correct ratio (if needed)
onchainos swap swap --from $TOKEN_A --to $TOKEN_B --amount $SWAP_AMT \
  --chain base --wallet $WALLET --slippage 1

# 5. Deposit at new range
onchainos defi deposit --investment-id $POOL --chain base \
  --amount0 $AMT0 --amount1 $AMT1 \
  --tick-lower $NEW_LOWER --tick-upper $NEW_UPPER
```

### Price Check via Quote

```bash
# Get ETH price in USDC
onchainos swap quote \
  --from 0x4200000000000000000000000000000000000006 \
  --to 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --amount 1000000000000000000 \
  --chain base
# Parse: toTokenAmount / 1e6 = ETH price in USD
```

### Error Handling

All commands may return errors. Common patterns:

| Error | Cause | Resolution |
|---|---|---|
| `insufficient_balance` | Not enough tokens | Check balances, reduce amount |
| `slippage_exceeded` | Price moved during execution | Retry with higher slippage or fresh quote |
| `gas_estimation_failed` | TX would revert | Check approval, amounts, tick alignment |
| `rate_limited` | Too many API calls | Wait 300-500ms between calls |
| `position_not_found` | Invalid token-id | Re-fetch positions list |
| `tick_not_aligned` | Tick not divisible by tick_spacing | Round to nearest multiple of tick_spacing |
