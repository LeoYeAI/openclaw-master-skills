# Scenario Tests

## Scenario 1: Happy Path — Pay and Verify

1. Agent generates invoice: amount `1000000` (1 USDC), memo `42`, startTime `1700000000`, endTime `1700086400`.
2. Server calls `buildAcceptPaymentInstructions` and serializes the instructions as JSON.
3. Client reconstructs instructions, signs, and submits the transaction on Solana via `sendTransaction`.
4. Server calls `validateInvoicePayment` with the same params.
5. Returns `true`. Agent delivers the service.

## Scenario 2: Verify Before Payment

1. Agent generates invoice: amount `500000`, memo `7777`, valid for 1 hour.
2. Server immediately calls `validateInvoicePayment` (user hasn't paid yet).
3. Returns `false`.
4. Agent tells the user payment is not confirmed and to try again after paying.

## Scenario 3: Duplicate Payment Rejection

1. Agent generates invoice with memo `99`.
2. User pays successfully. `validateInvoicePayment` returns `true`.
3. A second attempt to submit the same `acceptPayment` transaction is rejected by the on-chain program because the Invoice ID PDA is already initialized.

## Scenario 4: Mismatched Parameters

1. Agent generates invoice: amount `1000000`, memo `555`.
2. User pays with a different amount (`2000000`) but same memo.
3. `validateInvoicePayment` with original params returns `false` — the on-chain event has a different amount.

## Scenario 5: Expired Invoice

1. Agent generates invoice with `endTime` in the past.
2. The on-chain program rejects the transaction (timestamp outside validity window).
3. Agent should generate a new invoice with a valid time window.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `validateInvoicePayment` returns `false` but user claims they paid | Transaction may still be confirming, or params don't match | Wait a few seconds and retry. Double-check that `amount`, `memo`, `startTime`, `endTime`, and `user` all match exactly. |
| Invoice already paid | The Invoice ID PDA is already initialized | Generate a new invoice with a different `memo`. |
| Insufficient balance | User's token account doesn't have enough tokens | Tell the user to fund their wallet before paying. |
| Currency not supported | The `currencyMint` is not in the protocol's `GlobalConfig` | Use a supported currency (USDC, wSOL). |
