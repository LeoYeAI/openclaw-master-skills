# refinORE API Endpoints — Updated Mar 11, 2026

**Base URL:** `https://automine.refinore.com/api`

All authenticated endpoints require: `x-api-key: rsk_...` header

---

### Risk Tolerance Values
| Value | EV Threshold | Description |
|-------|-------------|-------------|
| degen | -Infinity | Mine every round regardless of EV |
| risky | -30% | Skip only when EV < -30% |
| less-risky | -15% | Skip when EV < -15% |
| positive-ev | 0% | Only mine when EV is positive |

Legacy mappings: `high` → `risky`, `medium` → `less-risky`, `low` → `positive-ev`

---

## Account

### GET /account/me ✅
Get account info including wallet address and deposit instructions.

**Response:**
```json
{
  "privy_user_id": "did:privy:...",
  "email": "user@example.com",
  "wallet_address": "5Eze...mpek",
  "wallet_chain": "solana",
  "wallet_type": "embedded",
  "created_at": "2025-11-17T03:44:12.019Z",
  "deposit_instructions": {
    "network": "Solana",
    "address": "5Eze...mpek",
    "supported_tokens": ["SOL", "USDC", "ORE", "stORE", "SKR"],
    "minimum_sol_for_gas": "0.005 SOL"
  }
}
```

---

## Wallet

### GET /wallet/balances?wallet=ADDRESS ✅
Get all token balances. **Requires `wallet` query parameter.**

**Response:**
```json
{
  "success": true,
  "balances": {
    "sol": 0.084,
    "ore": 0,
    "usdc": 0,
    "store": 0,
    "skr": 68.21
  },
  "address": "5Eze...mpek"
}
```

> ⚠️ The old endpoint `/wallet/balance` (no 's', no wallet param) does NOT exist.

---

## Mining

### POST /mining/start ✅
Start a new mining session.

**Required fields:** `wallet_address`, `sol_amount`, `num_squares`

```json
{
  "wallet_address": "5Eze...mpek",
  "sol_amount": 0.002,
  "num_squares": 5,
  "risk_tolerance": "positive-ev",
  "mining_token": "SOL",
  "tile_selection_mode": "optimal",
  "auto_restart": true,
  "frequency": "every_round"
}
```

> ⚠️ `wallet_address` is **required** — omitting it returns `{"error":"Missing required fields"}`

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "51f09bba-...",
    "status": "active",
    "started_at": "2026-02-04T18:14:21.147+00:00"
  }
}
```

### POST /mining/start-strategy ✅
Start mining using a saved strategy. **Requires `strategy_id`.**

```json
{
  "strategy_id": "cb5d46f3-..."
}
```

### POST /mining/stop ✅
Stop the active mining session.

**Response:** `{"success": true}`

### POST /mining/reload-session
Reload/restart a session. **Requires `session_id` in body.**

### GET /mining/session ✅
Get current active session status.

**Response (active):**
```json
{
  "session": {
    "id": "51f09bba-...",
    "status": "active",
    "total_rounds": 3,
    "total_rounds_deployed": 3,
    "total_wins": 0,
    "total_losses": 3,
    "total_sol_deployed": 0.006,
    "total_sol_won": 0
  }
}
```

**Response (inactive):** `{"hasActiveSession": false}`

### GET /mining/session-rounds?session_id=ID ✅
Get round-by-round results. **Requires `session_id` query parameter.**

**Response:**
```json
{
  "rounds": [
    {
      "round_number": 145897,
      "sol_amount": 0.002,
      "num_squares": 5,
      "amount_per_block": 0.0004,
      "deployed_block_indices": [23, 8, 22, 15, 11],
      "deployed_at": "2026-02-04T18:17:04.437+00:00",
      "result_recorded_at": "2026-02-04T18:17:48.695+00:00"
    }
  ]
}
```

### GET /mining/history?limit=N ✅
Get historical mining round data. Default limit: 20.

### GET /mining/last-config ✅
Get the last mining configuration used.

**Response:**
```json
{
  "hasLastConfig": true,
  "config": {
    "sol_amount": 0.002,
    "num_squares": 5,
    "risk_tolerance": "positive-ev",
    "mining_token": "SOL",
    "tile_selection_mode": "optimal"
  }
}
```

### GET /mining/round/:roundNumber
Get details for a specific round. Returns `{"deployed": false}` if user didn't participate.

### `PATCH /mining/session/edit`
Live-edit an active manual mining session between rounds. Changes take effect on the next deployment.

**Auth:** `x-api-key: rsk_...`

**Body (all optional):**
| Field | Type | Description |
|-------|------|-------------|
| sol_amount | number | SOL per round (0-100) |
| num_squares | number | Number of tiles (1-25) |
| tile_selection_mode | string | optimal, random, custom, odd, even, hot, cold |
| custom_tiles | number[] | Tile indices 0-24 (0-indexed: 0=tile 1 in UI, 24=tile 25). For custom mode. |
| skip_last_winning_square | boolean | Skip last round's winning tile |
| mining_token | string | SOL, USDC, ORE, stORE, SKR |
| deployment_timing_seconds | number | Deploy timing 0-60s |
| risk_tolerance | string | degen, risky, less-risky, positive-ev |
| custom_ev_threshold | number | Custom EV % threshold |
| motherlode_threshold | number | Min motherlode ORE |
| max_sol_deployed_threshold | number | Max total SOL deployed |

**Response:**
```json
{
  "success": true,
  "sessionId": "uuid",
  "changedFields": ["sol_amount", "num_squares"],
  "message": "Changes will take effect on the next deployment round."
}
```

Note: For strategy-based sessions, use `PATCH /auto-strategies/:id/live` instead.

---

## Rounds

### GET /rounds/current ✅ (No auth required)
Get current active round information.

**Response:**
```json
{
  "round_number": 145901,
  "motherlode_formatted": 16.8,
  "motherlode_hit": false,
  "total_deployed_sol": 2.729,
  "num_winners": 0,
  "network": "mainnet"
}
```

### GET /rounds/tile-stats?limit=100 ✅ (No auth required)
Get hot and cold tile statistics from the last N rounds. Shows which tiles have won the most/least — useful for building predictive tile strategies.

**Query params:** `limit` (10–500, default: 100)

**Response:**
```json
{
  "tileStats": [
    { "tile": 0, "wins": 5 },
    { "tile": 1, "wins": 3 }
  ],
  "hotTiles": [
    { "tile": 12, "wins": 8 },
    { "tile": 7, "wins": 7 }
  ],
  "coldTiles": [
    { "tile": 20, "wins": 1 },
    { "tile": 3, "wins": 1 }
  ],
  "roundsAnalyzed": 100,
  "avgWinsPerTile": 4
}
```

> `hotTiles` = top 5 most-won tiles. `coldTiles` = bottom 5 least-won tiles.

### GET /rounds/my-history?limit=50 ✅
Get your personal mining round history — every round you deployed in with full details including tiles used, amounts, results, and winnings.

**Query params:**
- `limit` (1–500, default: 50) — number of rounds to return
- `offset` (default: 0) — for pagination
- `session_id` — optional, filter to a specific mining session

**Response:**
```json
{
  "rounds": [
    {
      "id": "abc123",
      "session_id": "def456",
      "round_number": 145901,
      "deployed_at": "2026-02-04T18:17:04Z",
      "sol_amount": 0.005,
      "num_squares": 10,
      "amount_per_block": 0.0005,
      "deployed_block_indices": [3, 7, 12, 15, 19, 0, 1, 5, 8, 22],
      "ev_percent": 5.2,
      "total_deployed_sol": 28.5,
      "motherlode_ore": 45.2,
      "ore_price_usd": 0.30,
      "sol_price_usd": 198.50,
      "skipped": false,
      "winning_block_index": 12,
      "user_won": true,
      "sol_won": 0.012,
      "ore_won": 0.5,
      "used_tile_selection_mode": "optimal",
      "used_skip_last_winning_square": false
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### GET /rounds/recent?limit=50 (No auth required)
Get recent global round data (not user-specific). Default limit: 50.

### GET /rounds/:roundNumber (No auth required)
Get a specific round by number.

---

## Strategies

### GET /auto-strategies ✅
List all saved strategies.

### POST /auto-strategies
Create a new strategy.

```json
{
  "name": "Conservative Grinder",
  "solAmount": 0.005,
  "numSquares": 10,
  "tileSelectionMode": "optimal",
  "riskTolerance": "positive-ev",
  "miningToken": "SOL"
}
```

### PUT /auto-strategies/:id
Full update of a strategy. All fields required.

### PATCH /auto-strategies/:id/live ✅
**Live-edit a strategy between rounds without stopping/starting the mining session.** Only send the fields you want to change — everything else stays the same. Changes take effect on the next deployment round automatically.

> This is the key endpoint for AI agents that want to dynamically adjust strategy mid-session (e.g., switch tiles, change SOL amount, adjust thresholds).

**Body (all fields optional — send only what you want to change):**
```json
{
  "sol_amount": 0.01,
  "num_squares": 15,
  "tile_selection_mode": "custom",
  "custom_tiles": [0, 3, 7, 12, 18],
  "skip_last_winning_square": true,
  "mining_token": "SOL",
  "risk_tolerance": "positive-ev",
  "deployment_timing": 45,
  "motherlode_threshold": 100,
  "max_sol_deployed_threshold": 500,
  "else_deploy_sol_amount": 0.005,
  "else_deploy_num_squares": 5,
  "rules": [
    {
      "name": "High ML",
      "conditions": [{ "field": "motherlode", "operator": "gt", "value": 100 }],
      "conditionLogic": "AND",
      "deploySolAmount": 0.02,
      "deployNumSquares": 25,
      "tileSelectionMode": "optimal"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "strategy": { "...updated strategy object..." },
  "changedFields": ["sol_amount", "custom_tiles", "tile_selection_mode"],
  "activeSession": {
    "id": "51f09bba-...",
    "status": "active",
    "message": "Changes will take effect on the next deployment round."
  }
}
```

> `activeSession` is null if no session is currently using this strategy.

### DELETE /auto-strategies/:id
Delete a strategy.

---

## DCA / Limit Orders

### GET /auto-swap-orders ✅
List active orders.

### POST /auto-swap-orders
Create a DCA or limit order.

**DCA:** `{"type":"dca","input_token":"SOL","output_token":"ORE","amount":0.1,"interval_hours":24,"total_orders":30}`

**Limit:** `{"type":"limit","input_token":"SOL","output_token":"ORE","amount":1.0,"target_price":60.00,"direction":"buy"}`

### DELETE /auto-swap-orders/:id
Cancel/delete an active order.

### GET /auto-swap-orders/history ✅
Get execution history for completed and partially-filled orders.

**Query params:** `limit` (default: 50), `offset` (default: 0)

**Response:**
```json
{
  "orders": [
    {
      "id": "order-123",
      "type": "dca",
      "input_token": "SOL",
      "output_token": "ORE",
      "amount": 0.1,
      "status": "completed",
      "executions": 30,
      "total_input": 3.0,
      "total_output": 145.2,
      "created_at": "2026-01-15T10:00:00Z",
      "completed_at": "2026-02-14T10:00:00Z"
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0
}
```

---

## Staking

### GET /staking/info?wallet=ADDRESS ✅
Get stake info. **Requires `wallet` query parameter.**

**Response:**
```json
{
  "success": true,
  "stakingInfo": {
    "balance": 50000000000,
    "rewards": 487316076,
    "lifetimeRewards": 130949148134,
    "lastClaimAt": 1768177848,
    "lastDepositAt": 1768498844
  }
}
```

---

## Rewards

### GET /rewards?wallet=ADDRESS ✅
Get mining rewards summary. **Requires `wallet` query parameter.**

**Response:**
```json
{
  "success": true,
  "rewards": {
    "unclaimedSol": 0,
    "unrefinedOre": 111.45,
    "bonusRefinedOre": 12.27,
    "solDeployed": 0.002
  }
}
```

---

## Tile Presets

### GET /tile-presets ✅
List saved tile presets.

### POST /tile-presets
Save a new preset. `{"name":"Diagonal","tile_ids":[0,6,12,18,24]}`

---

## Public Endpoints (No Auth)

### GET /refinore-apr ✅
Current staking APR.

**Response:** `{"success":true,"apr":113.21,"asOf":"2026-02-04T18:16:13.830Z"}`

---

## Non-Functional Endpoints (removed from docs)

The following were previously documented but do **not exist** on the current backend:
- ~~GET /sse~~ — No SSE route
- ~~GET /wallet/balance~~ — Use `/wallet/balances?wallet=X` instead
- ~~GET /wallet/transactions~~ — Not implemented
- ~~POST /coinbase-onramp~~ — Not on backend (frontend only)
- ~~GET /unsubscribe~~ — Uses token-based auth, not API key
- ~~POST /resubscribe~~ — Returns 500

---

## Error Handling

| HTTP Code | Meaning | Agent Action |
|-----------|---------|-------------|
| `200` | Success | Process response |
| `400` | Bad request / missing fields | Check required params |
| `401` | Invalid API key | Alert owner to regenerate key |
| `404` | Not found (no session) | Handle gracefully |
| `429` | Rate limited | Back off, retry after delay |
| `500` | Server error | Retry after 30s, alert if persistent |
