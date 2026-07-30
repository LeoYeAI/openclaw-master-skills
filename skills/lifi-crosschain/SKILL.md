---
name: lifi
description: Cross-chain token swaps and bridges via the LI.FI protocol. Get quotes, execute transfers, track progress, and compose DeFi operations across 35+ blockchains.
user-invocable: true
argument-hint: "[swap|bridge|track|routes|zap] <details>"
metadata: {"openclaw":{"emoji":"🔗","requires":{"bins":["curl"]},"primaryEnv":"LIFI_API_KEY"}}
---

# /lifi — Cross-Chain Swaps & Bridges

LI.FI is a cross-chain bridge and DEX aggregation protocol. It finds optimal routes across 35+ blockchains, comparing dozens of bridges (Stargate, Hop, Across, etc.) and DEXes (Uniswap, SushiSwap, 1inch, etc.) to execute token swaps and cross-chain transfers.

## Arguments: `$ARGUMENTS`

Parse the arguments:
- **First positional arg**: Action — `swap`, `bridge`, `track`, `routes`, `zap`, or a natural language request
- **Remaining args**: Details (token names, amounts, chains, tx hashes, etc.)

If no arguments are provided, ask the user what they want to do.

## Key Concepts

- **Base URL**: `https://li.quest/v1`
- The API returns `transactionRequest` objects (to, data, value, gasLimit, gasPrice) ready to sign — provide these to the agent's wallet
- **Native token address**: `0x0000000000000000000000000000000000000000` (for ETH, MATIC, BNB, etc.)
- Amounts are always in the token's **smallest unit** (wei): 1 ETH = `1000000000000000000` (18 decimals), 1 USDC = `1000000` (6 decimals)
- Optional API key via `x-lifi-api-key` header for higher rate limits (not required)

---

## API Reference

### Discovery Endpoints

#### GET /v1/chains — List supported blockchains
```bash
curl -s "https://li.quest/v1/chains"
# Optional: ?chainTypes=EVM or ?chainTypes=SVM
```

#### GET /v1/tokens — List supported tokens
```bash
curl -s "https://li.quest/v1/tokens?chains=1,137"
# Optional: chainTypes, minPriceUSD
```

#### GET /v1/token — Get specific token details
```bash
curl -s "https://li.quest/v1/token?chain=1&token=USDC"
# chain (required): chain ID or name. token (required): address or symbol
```

#### GET /v1/connections — Check available swap routes
```bash
curl -s "https://li.quest/v1/connections?fromChain=1&toChain=137&fromToken=0x0000000000000000000000000000000000000000"
# Optional: toToken, chainTypes, allowBridges
```

#### GET /v1/tools — List available bridges and DEXes
```bash
curl -s "https://li.quest/v1/tools"
# Returns {bridges: [{key, name}], exchanges: [{key, name}]}
```

### Quote & Swap Endpoints

#### GET /v1/quote — Get optimal route + transaction data
The primary endpoint for initiating any swap or bridge.
```bash
curl -s "https://li.quest/v1/quote?\
fromChain=1&toChain=137\
&fromToken=0x0000000000000000000000000000000000000000\
&toToken=0x0000000000000000000000000000000000000000\
&fromAddress=0xYOUR_WALLET\
&fromAmount=1000000000000000000\
&slippage=0.03"
```
**Required**: fromChain, toChain, fromToken, toToken, fromAddress, fromAmount
**Optional**: toAddress, slippage (decimal, e.g. 0.03 = 3%), integrator, order (RECOMMENDED|FASTEST|CHEAPEST|SAFEST), allowBridges, allowExchanges

Returns: `action`, `estimate` (toAmount, fees, executionDuration), and `transactionRequest` (to, data, value, gasLimit).

#### GET /v1/status — Track cross-chain transfer
```bash
curl -s "https://li.quest/v1/status?txHash=0xTX_HASH"
# Optional: bridge, fromChain, toChain
```
Returns: `status` (NOT_FOUND, PENDING, DONE, FAILED), `substatus` (COMPLETED, PARTIAL, REFUNDED), source/destination tx details.

### Advanced Routing

#### POST /v1/advanced/routes — Compare multiple route options
```bash
curl -s -X POST "https://li.quest/v1/advanced/routes" \
  -H "Content-Type: application/json" \
  -d '{
    "fromChainId": "1",
    "toChainId": "137",
    "fromTokenAddress": "0x0000000000000000000000000000000000000000",
    "toTokenAddress": "0x0000000000000000000000000000000000000000",
    "fromAddress": "0xYOUR_WALLET",
    "fromAmount": "1000000000000000000",
    "options": {"order": "RECOMMENDED"}
  }'
```
**Required**: fromChainId, toChainId, fromTokenAddress, toTokenAddress, fromAddress, fromAmount
**Optional**: toAddress, slippage, options.order

Returns: `routes[]` array — each route has steps, estimated output, fees, and execution time.

#### POST /v1/advanced/stepTransaction — Get tx data for a route step
```bash
curl -s -X POST "https://li.quest/v1/advanced/stepTransaction" \
  -H "Content-Type: application/json" \
  -d '{ ...step object from routes response... }'
```
Pass the entire step object from a route. Returns `transactionRequest` ready to sign.

#### POST /v1/quote/contractCalls — Zaps (multi-action DeFi composition)
```bash
curl -s -X POST "https://li.quest/v1/quote/contractCalls" \
  -H "Content-Type: application/json" \
  -d '{
    "fromChain": "1",
    "toChain": "137",
    "fromToken": "0x0000000000000000000000000000000000000000",
    "toToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "fromAddress": "0xYOUR_WALLET",
    "fromAmount": "1000000000000000000",
    "contractCalls": [
      {
        "toContractAddress": "0xTARGET_CONTRACT",
        "toContractCallData": "0xENCODED_FUNCTION_CALL",
        "toContractGasLimit": "200000"
      }
    ]
  }'
```
**Required**: fromChain, toChain, fromToken, toToken, fromAddress, fromAmount, contractCalls[]
**Optional**: slippage

### Gas Information

#### GET /v1/gas/prices — Gas prices across all chains
```bash
curl -s "https://li.quest/v1/gas/prices"
```

#### GET /v1/gas/suggestion/{chainId} — Recommended gas params for a chain
```bash
curl -s "https://li.quest/v1/gas/suggestion/1"
```

---

## Guided Workflows

### Workflow 1 — Swap or Bridge Tokens

Use this for any "swap X for Y" or "bridge tokens to chain" request.

1. **Identify parameters** from the user's request:
   - Source chain and token (e.g., "ETH on Ethereum")
   - Destination chain and token (e.g., "USDC on Polygon")
   - Amount in human-readable form (e.g., "1.5 ETH")
   - Wallet address (the agent's wallet or user-specified)

2. **Look up token addresses** if the user gave symbols:
   ```bash
   curl -s "https://li.quest/v1/token?chain=1&token=USDC"
   ```
   Extract `address` and `decimals` from the response.

3. **Convert amount to smallest unit**:
   - Multiply human amount by 10^decimals
   - 1.5 ETH (18 decimals) → `1500000000000000000`
   - 100 USDC (6 decimals) → `100000000`

4. **Get a quote**:
   ```bash
   curl -s "https://li.quest/v1/quote?fromChain=1&toChain=137&fromToken=0x0000000000000000000000000000000000000000&toToken=0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359&fromAddress=0xWALLET&fromAmount=1500000000000000000&slippage=0.03"
   ```

5. **Present summary to user** (REQUIRED before returning tx data):
   ```
   Swap: 1.5 ETH (Ethereum) → ~2,850 USDC (Polygon)
   Route: Stargate bridge → Uniswap V3
   Fees: ~$2.50 (gas) + $0.50 (bridge)
   Estimated time: ~2 minutes
   Slippage: 3%
   ```

6. **If ERC20 token**: Check if the LiFi contract has sufficient allowance. The spender address is `transactionRequest.to` from the quote response. If allowance < fromAmount, guide the user to approve the token first.

7. **Return `transactionRequest`** for signing by the agent's wallet.

8. **If cross-chain**: Explain that bridging is asynchronous — the source chain tx will confirm first, then the bridge delivers tokens to the destination. Offer to track with Workflow 3.

### Workflow 2 — Compare Routes

Use when the user wants to see options or find the best deal.

1. **Gather parameters** (same as Workflow 1, steps 1-3).

2. **Request multiple routes**:
   ```bash
   curl -s -X POST "https://li.quest/v1/advanced/routes" \
     -H "Content-Type: application/json" \
     -d '{
       "fromChainId": "1",
       "toChainId": "137",
       "fromTokenAddress": "0x0000000000000000000000000000000000000000",
       "toTokenAddress": "0x0000000000000000000000000000000000000000",
       "fromAddress": "0xWALLET",
       "fromAmount": "1000000000000000000",
       "options": {"order": "RECOMMENDED"}
     }'
   ```

3. **Present comparison table**:
   ```
   #  Route                     Output       Fees     Time    Bridge
   1  Stargate → Uniswap V3    2,850 USDC   $3.00    2 min   Stargate
   2  Hop → SushiSwap          2,845 USDC   $2.80    5 min   Hop
   3  Across → 1inch           2,848 USDC   $3.20    3 min   Across
   ```

4. **User picks a route**. Extract the chosen route's steps.

5. **Get transaction data** for each step:
   ```bash
   curl -s -X POST "https://li.quest/v1/advanced/stepTransaction" \
     -H "Content-Type: application/json" \
     -d '{ ...step object... }'
   ```

6. **Return `transactionRequest`** for signing.

### Workflow 3 — Track a Transfer

Use when the user wants to check status of a cross-chain transfer.

1. **Get details from user**: transaction hash, source chain, destination chain.

2. **Check status**:
   ```bash
   curl -s "https://li.quest/v1/status?txHash=0xTX_HASH&fromChain=1&toChain=137"
   ```

3. **Interpret and report status**:
   - `NOT_FOUND` — Transaction not yet indexed. Wait a minute and retry.
   - `PENDING` — Transfer in progress. Suggest polling every 30 seconds.
   - `DONE` with substatus `COMPLETED` — Transfer complete. Report destination tx hash.
   - `DONE` with substatus `PARTIAL` — User received the bridged token on the destination chain but NOT the final target token (e.g., got USDC.e instead of native USDC). The user may need to swap manually.
   - `DONE` with substatus `REFUNDED` — Transfer failed and funds were returned to the source address.
   - `FAILED` — Transfer failed. Report error details and advise the user to check the source chain tx on a block explorer.

4. **If PENDING**: Offer to poll periodically. Wait 30 seconds between checks.

### Workflow 4 — Zap (Contract Call Composition)

Use for multi-step DeFi operations like "bridge ETH to Polygon and deposit into Aave" or "swap to USDC and stake in a vault."

1. **Understand the multi-step operation** — identify:
   - Source chain/token/amount
   - Destination chain/token (the intermediate token before contract calls)
   - Target contract and function to call on the destination

2. **Gather contract call data**:
   - `toContractAddress`: The destination contract (e.g., Aave lending pool)
   - `toContractCallData`: ABI-encoded function call (e.g., `deposit(address,uint256,address,uint16)`)
   - `toContractGasLimit`: Gas limit for the contract call (e.g., "200000")

3. **Request zap quote**:
   ```bash
   curl -s -X POST "https://li.quest/v1/quote/contractCalls" \
     -H "Content-Type: application/json" \
     -d '{
       "fromChain": "1",
       "toChain": "137",
       "fromToken": "0x0000000000000000000000000000000000000000",
       "toToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
       "fromAddress": "0xWALLET",
       "fromAmount": "1000000000000000000",
       "contractCalls": [{
         "toContractAddress": "0xTARGET",
         "toContractCallData": "0xENCODED_CALL",
         "toContractGasLimit": "200000"
       }]
     }'
   ```

4. **Present summary** showing all operations in the zap (bridge + swap + deposit/stake/etc.).

5. **Return `transactionRequest`** for signing.

### Workflow 5 — Discovery

Use when the user asks "what chains are supported?", "what tokens can I swap?", "what bridges are available?", etc.

1. **Determine what the user wants to know**:
   - Supported chains → `GET /v1/chains`
   - Tokens on a chain → `GET /v1/tokens?chains={chainId}`
   - Token details → `GET /v1/token?chain={chainId}&token={symbol}`
   - Available routes → `GET /v1/connections?fromChain={id}&toChain={id}`
   - Available bridges/DEXes → `GET /v1/tools`
   - Gas prices → `GET /v1/gas/prices` or `GET /v1/gas/suggestion/{chainId}`

2. **Call the appropriate endpoint**.

3. **Present results** in a readable table format. For large responses (e.g., all tokens), summarize the most relevant results and offer to filter further.

---

## Safety Protocol

These rules are **mandatory** — never skip them.

### Address Validation
- **ALWAYS** verify `fromAddress` is a valid hex address: starts with `0x`, 42 characters total, valid hex characters
- **NEVER** send to the zero address (`0x0000000000000000000000000000000000000000`) as `toAddress` — this burns funds permanently. The zero address is ONLY valid as a `fromToken`/`toToken` to represent native tokens.

### Amount Validation
- **ALWAYS** convert human-readable amounts to the token's smallest unit before calling the API
  - Check the token's `decimals` field (ETH=18, USDC=6, WBTC=8, DAI=18)
  - Formula: `amount_wei = human_amount × 10^decimals`
- Amounts must be positive integers (no decimals, no negatives, no zero)
- Maximum 78 digits (uint256 max)
- If the user says "1 ETH", send `1000000000000000000`, NOT `1`

### Slippage Validation
- Default to `0.03` (3%) if the user doesn't specify
- **WARN** the user if slippage > 3% — explain they may receive significantly fewer tokens
- **REJECT** slippage > 50% (`0.5`) — this is almost certainly an error
- Slippage must be between 0 and 1 (0% to 100%)

### ERC20 Token Approvals
- **ALWAYS** check token allowance before executing ERC20 swaps
- If allowance < fromAmount, guide the user to approve the token first
- **NEVER** approve unlimited amounts (MaxUint256 / `0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`) unless the user explicitly requests it — approve only the needed amount
- The spender address is `transactionRequest.to` from the quote response

### Transaction Presentation
- **ALWAYS** present a human-readable summary before returning any `transactionRequest` data
- The summary must include: tokens and amounts, route/bridge used, estimated fees, estimated time, slippage setting
- **NEVER** return raw transaction data without explanation

### Cross-Chain Safety
- Explain that cross-chain bridges are **non-atomic** — funds may be in transit for minutes to hours
- After submitting a source chain tx, always offer to track the transfer status
- If a transfer shows `PARTIAL` status, explain the user received bridged tokens but not the final target token

### No Route Found
- If a quote returns no route: suggest trying different tokens, a smaller amount, or an alternative chain pair
- Use `GET /v1/connections` to verify the route is supported before retrying

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| HTTP 429 | Rate limited | Wait 30s, retry with exponential backoff (30s → 60s → 120s). Suggest user set `LIFI_API_KEY` for higher limits. |
| No route found | Route unsupported or amount too small/large | Check `/v1/connections` for valid pairs. Suggest different tokens, smaller amount, or alternative chains. |
| Slippage error | Price moved beyond tolerance | Increase slippage (e.g., 0.03 → 0.05) and retry. Warn user about the trade-off. |
| Insufficient balance | Wallet lacks funds | Report the shortfall amount. Check balance with the agent's wallet tools. |
| Transaction reverted | Price moved, liquidity drained, or gas too low | Explain possible causes. Suggest retrying with higher slippage or gas. |
| PARTIAL completion | Bridge delivered token but not final swap | User has the bridged asset on the destination chain. They can swap it manually or retry. |
| REFUNDED | Bridge failed, funds returned | Confirm refund on source chain. Suggest trying a different bridge via `allowBridges`. |
| Invalid address | Malformed hex address | Verify address format: `0x` prefix, 42 characters, valid hex. |

---

## Chain Quick Reference

| Chain | ID | Native Token |
|-------|----|-------------|
| Ethereum | 1 | ETH |
| Polygon | 137 | MATIC |
| Arbitrum One | 42161 | ETH |
| Optimism | 10 | ETH |
| BSC | 56 | BNB |
| Base | 8453 | ETH |
| Avalanche | 43114 | AVAX |
| Fantom | 250 | FTM |
| zkSync Era | 324 | ETH |
| Gnosis | 100 | xDAI |
| Scroll | 534352 | ETH |
| Linea | 59144 | ETH |
| Blast | 81457 | ETH |
| Mode | 34443 | ETH |
| Solana | 1151111081099710 | SOL |

For the full list of supported chains, call `GET /v1/chains`.

Native token address on all EVM chains: `0x0000000000000000000000000000000000000000`
