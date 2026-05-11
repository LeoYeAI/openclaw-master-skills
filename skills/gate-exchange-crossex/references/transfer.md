# Gate CrossEx Transfer - Scenarios and Prompt Examples

Gate CrossEx cross-exchange fund transfer scenarios.

## Workflow

### Step 1: Validate the asset and supported route

Call `cex_crx_list_crx_transfer_coins` with:

- `coin`: target asset when the user specifies a coin

Key data to extract:

- whether the coin is transferable
- supported transfer route
- route limits when available

### Step 2: Check source account balance

Call `cex_crx_get_crx_account` with:

- no required parameters for the default account overview

Key data to extract:

- available balance for the selected coin
- source account status
- whether the requested amount is sufficient

### Step 3: Create the transfer after explicit confirmation

Call `cex_crx_create_crx_transfer` with:

- `from`
- `to`
- `coin`
- `amount`
- `text` when a memo is needed

Key data to extract:

- transfer id
- submitted route
- submitted amount
- initial transfer status

### Step 4: Verify transfer status or history

Call `cex_crx_list_crx_transfers` with:

- `coin` when the user wants a filtered history view
- `order_id` when tracking a single transfer record

Key data to extract:

- final transfer status
- completion time
- resulting record id

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Transfer Summary
- From: {from_exchange}
- To: {to_exchange}
- Asset: {coin}
- Amount: {amount}
- Status: {status}
- Transfer ID: {transfer_id}
```

## API Call Parameters

### Transfer Route Format

```text
{FROM_EXCHANGE} -> {TO_EXCHANGE} : {COIN}
```

**Examples**:

- `GATE -> BINANCE : USDT`
- `BINANCE -> OKX : BTC`
- `OKX -> GATE : ETH`

### Transfer Parameters

| Parameter | Description                                                                             |
|-----------|-----------------------------------------------------------------------------------------|
| `from`    | Source exchange (CROSSEX_GATE, CROSSEX_BINANCE, CROSSEX_OKX, CROSSEX_BYBIT, SPOT)       |
| `to`      | Destination exchange ((CROSSEX_GATE, CROSSEX_BINANCE, CROSSEX_OKX, CROSSEX_BYBIT, SPOT) |
| `coin`    | Currency (USDT, BTC, ETH, etc.)                                                         |
| `amount`  | Transfer quantity                                                                       |
| `text`    | Optional memo                                                                           |

### Data Sources

- **Supported Coins**: Call `cex_crx_list_crx_transfer_coins` → List of coins supporting cross-exchange transfer
- **Account Balance**: Call `cex_crx_get_crx_account` → `available_balance`
- **Create Transfer**: Call `cex_crx_create_crx_transfer` → Execute transfer
- **Transfer History**: Call `cex_crx_list_crx_transfers` → Transfer records

### Pre-checks

1. **Coin Verification**: Call `cex_crx_list_crx_transfer_coins` to verify coin support
2. **Balance Check**: Confirm the source account has sufficient balance
3. **Minimum Amount Check**: Validate transfer minimum and single-limit requirements
4. **Route Check**: Confirm the requested source and destination exchanges are supported

### Pre-transfer Confirmation

**Before transfer**, display **transfer summary**, only call transfer API after user confirmation.

- **Summary**: Source exchange, destination exchange, currency, quantity, estimated arrival time
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** execute the transfer

### Error Handling

| Error Code                  | Handling                                          |
|-----------------------------|---------------------------------------------------|
| `COIN_NOT_SUPPORTED`        | Currency does not support cross-exchange transfer |
| `BALANCE_NOT_ENOUGH`        | Insufficient available balance                    |
| `TRANSFER_AMOUNT_MIN_ERROR` | Amount below minimum                              |
| `TRANSFER_AMOUNT_MAX_ERROR` | Amount exceeds single limit                       |
| `TRANSFER_FAILED`           | Transfer failed, retry later or contact support   |

---

## Scenario 1: Cross-Exchange Fund Transfer

**Context**: User wants to transfer funds between different exchanges.

**Prompt Examples**:

- "Transfer 100 USDT from Gate to Binance"
- "Transfer 50 USDT to OKX"
- "Move ETH from OKX to Gate"

**Expected Behavior**:

1. Parse parameters: Source exchange, destination exchange, currency, quantity.
2. Check supported coins via `cex_crx_list_crx_transfer_coins`.
3. Check source account balance via `cex_crx_get_crx_account`.
4. Display transfer plan and require confirmation.
5. Call `cex_crx_create_crx_transfer` with the confirmed parameters.
6. Query transfer status via `cex_crx_list_crx_transfers` and output the result.

**Report Template**:

```text
Transfer Plan:
- From: GATE
- To: BINANCE
- Coin: USDT
- Amount: 100
- Est. Arrival: 1-5 minutes

Reply 'confirm' to execute the above operation.

(After user confirmation)

Transfer submitted.
- Transfer ID: TRANSFER_123456
- Status: Processing
```

---

## Scenario 2: Query Transfer History

**Context**: User wants to view cross-exchange transfer history records.

**Prompt Examples**:

- "Query transfer history"
- "Show recent transfer records"
- "Transfer records"

**Expected Behavior**:

1. Identify the request as transfer history.
2. Call `cex_crx_list_crx_transfers` with optional asset or record filters.
3. Display recent transfer records in reverse chronological order.

**Report Template**:

```text
Recent Transfer Records
- Total Records: 2
- Latest Status: Completed
```
