# JSON Output Format Reference

Every Sol CLI command supports `--json` for structured output. For
most use cases the default human-readable output is preferable — it
shows tables, signposts next actions, and is easy for both humans and
LLM agents to read. Use `--json` when chaining commands in automation
pipelines or parsing results programmatically in code.

## Response Envelope

All responses use the `CommandResult<T>` envelope:

```json
{
  "ok": true,
  "data": { ... },
  "meta": {
    "elapsed_ms": 450
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | `boolean` | `true` on success, `false` on failure |
| `data` | `T` | Command-specific response data (present on success) |
| `error` | `string` | Error code in `UPPER_SNAKE_CASE` (present on failure) |
| `message` | `string` | Human-readable error description (present on failure) |
| `meta` | `object` | Metadata — always includes `elapsed_ms` |

## Error Response

```json
{
  "ok": false,
  "error": "SWAP_FAILED",
  "message": "Insufficient balance: need 50 USDC, have 12.5 USDC",
  "meta": { "elapsed_ms": 150 }
}
```

## Error Code Convention

Error codes follow `NOUN_VERB_FAILED` format in `UPPER_SNAKE_CASE`:

| Code | When |
|------|------|
| `WALLET_CREATE_FAILED` | Wallet creation fails |
| `BALANCE_FAILED` | Balance lookup fails |
| `SWAP_FAILED` | Token swap fails |
| `SEND_FAILED` | Token send fails |
| `STAKE_NEW_FAILED` | Stake creation fails |
| `STAKE_WITHDRAW_FAILED` | Stake withdrawal fails |
| `LEND_DEPOSIT_FAILED` | Lending deposit fails |
| `LEND_WITHDRAW_FAILED` | Lending withdrawal fails |
| `LEND_BORROW_FAILED` | Borrowing fails |
| `LEND_REPAY_FAILED` | Loan repayment fails |
| `PORTFOLIO_FETCH_FAILED` | Portfolio fetch fails |
| `CONFIG_SET_FAILED` | Config update fails |
| `NETWORK_FAILED` | Network info fetch fails |
| `TOKEN_LIST_FAILED` | Token list fetch fails |

## Exit Codes

- `0` — Success
- `1` — Command failed (error details in JSON response)

## Global Flags

These flags work with any command:

```bash
sol <command> --json                      # structured output
sol <command> --rpc https://my-rpc.com    # override RPC
sol <command> --verbose                   # debug logging
sol <command> --wallet trading            # override wallet
```
