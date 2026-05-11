# Gate CrossEx Convert Trading - Scenarios and Prompt Examples

Gate CrossEx flash convert scenarios.

## Workflow

### Step 1: Validate the convert request and balance

Call `cex_crx_get_crx_account` with:

- no required parameters for the default account overview

Key data to extract:

- available balance for the source coin
- whether the requested convert amount is sufficient
- exchange availability for the convert request

### Step 2: Request a convert quote

Call `cex_crx_create_crx_convert_quote` with:

- `exchange_type`
- `from_coin`
- `to_coin`
- `from_amount`

Key data to extract:

- quote id
- quoted rate
- expected receive amount
- quote expiry

### Step 3: Execute the convert after explicit confirmation

Call `cex_crx_create_crx_convert_order` with:

- `quote_id`

Key data to extract:

- convert order id
- submitted quote id
- initial convert status

### Step 4: Verify resulting balances

Call `cex_crx_get_crx_account` with:

- no required parameters for the default account overview

Key data to extract:

- updated source balance
- updated target balance
- whether the convert completed successfully

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Convert Trading Summary
- Exchange: {exchange_type}
- From: {from_amount} {from_coin}
- To: {to_coin}
- Rate: {rate}
- Expected Receive: {expected_receive}
- Status: {status}
- Convert Order ID: {order_id}
```

## API Call Parameters

### Convert Pair Format

```text
{FROM_COIN} -> {TO_COIN}
```

**Examples**:

- `USDT -> BTC`
- `BTC -> ETH`
- `USDT -> XRP`

### Convert Parameters

| Parameter       | Description                        |
|-----------------|------------------------------------|
| `exchange_type` | Exchange type (GATE, BINANCE, OKX) |
| `from_coin`     | Source currency                    |
| `to_coin`       | Target currency                    |
| `from_amount`   | Convert quantity                   |

### Data Sources

- **Account Balance**: Call `cex_crx_get_crx_account` → available balances
- **Convert Quote**: Call `cex_crx_create_crx_convert_quote` → quoted rate and expected receive amount
- **Execute Convert**: Call `cex_crx_create_crx_convert_order` → place the convert order

### Pre-checks

1. **Balance Check**: Confirm the source asset balance is sufficient
2. **Pair Check**: Confirm the requested convert pair is supported by the selected exchange
3. **Quote Freshness Check**: Use the returned quote within its validity window

### Pre-convert Confirmation

**Before conversion**, display **conversion summary**, only call the convert order API after user confirmation.

- **Summary**: Source coin, target coin, source amount, expected receive amount, rate, fee
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** execute the convert order

### Error Handling

| Error Code                                   | Handling                                                    |
|----------------------------------------------|-------------------------------------------------------------|
| `BALANCE_NOT_ENOUGH`                         | Insufficient source asset balance                           |
| `CONVERT_AMOUNT_MIN_ERROR`                   | Convert amount below minimum                                |
| `EXCHANGE_TYPE_REQUIRED`                     | Convert request must specify `exchange_type`                |
| `CONVERT_TRADE_QUOTE_EXCHANGE_INVALID_ERROR` | `exchange_type` must be a supported uppercase exchange code |
| `TRANSFER_FAILED`                            | Convert execution failed, retry later or contact support    |

---

## Scenario 1: Flash Convert

**Context**: User wants to convert one cryptocurrency to another within Gate CrossEx.

**Prompt Examples**:

- "Flash convert 10 USDT to BTC"
- "Convert 50 USDT to ETH on Gate"
- "Quote convert SOL to BTC"

**Expected Behavior**:

1. Parse parameters: source coin, target coin, amount, and exchange type.
2. Check source balance via `cex_crx_get_crx_account`.
3. Call `cex_crx_create_crx_convert_quote` to get a live quote.
4. Display the convert summary and require confirmation.
5. Call `cex_crx_create_crx_convert_order` with the returned `quote_id`.
6. Verify balances via `cex_crx_get_crx_account` and output the result.

**Report Template**:

```text
Flash Convert Quote:
- Exchange: GATE
- From: 10 USDT
- To: BTC
- Rate: 1 BTC = 50000 USDT
- Expected Receive: 0.0002 BTC

Reply 'confirm' to execute the above operation.

(After user confirmation)

Convert submitted.
- Convert Order ID: CONVERT_123456
- Status: Processing
```
