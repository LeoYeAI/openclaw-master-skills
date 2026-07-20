---
name: archon-lightning
description: Lightning Network payments via Archon DIDs - create wallets, send/receive sats, verify payments, Lightning Address zaps
metadata:
  openclaw:
    requires:
      env:
        - ARCHON_WALLET_PATH
        - ARCHON_PASSPHRASE
        - ARCHON_GATEKEEPER_URL
      bins:
        - node
        - npx
      anyBins:
        - jq
    primaryEnv: ARCHON_PASSPHRASE
    emoji: "⚡"
---

# Archon Lightning - Lightning Network Payments for DIDs

Lightning Network integration for Archon decentralized identities. Send and receive Bitcoin over Lightning using your DID.

**Related skills:**
- `archon-keymaster` — Core DID identity management
- `archon-vault` — Encrypted backups

## Capabilities

- **Lightning Wallet Management** - Create Lightning wallets for DIDs
- **Invoice Generation** - Create BOLT11 invoices to receive payments
- **Invoice Payment** - Pay BOLT11 invoices
- **Payment Verification** - Verify payments settled (critical security pattern)
- **Lightning Address Zapping** - Send to Lightning Addresses (`user@domain.com`)
- **Payment History** - Track all Lightning transactions
- **Balance Checking** - Query wallet balance
- **DID Integration** - Publish Lightning endpoint to DID document
- **Invoice Decoding** - Inspect BOLT11 invoice details

## Prerequisites

- Node.js installed (for `npx @didcid/keymaster`)
- Archon identity configured (`~/.archon.env` with `ARCHON_WALLET_PATH`, `ARCHON_PASSPHRASE`)
- `jq` recommended for JSON parsing

All created by `archon-keymaster` setup. If you don't have Archon configured yet, see the `archon-keymaster` skill first.

## Security Notes

This skill handles Lightning Network payments:

1. **Non-custodial**: You control your Lightning node and private keys
2. **Payment verification is built-in**: `lightning-pay.sh` automatically verifies payments; if using keymaster directly, you must verify manually with `lightning-check` (see Payment Verification Pattern below)
3. **Environment access**: Scripts source `~/.archon.env` for wallet access
4. **Network connectivity**: Connects to Lightning Network via Archon gatekeeper

## Quick Start

### Create Lightning Wallet

```bash
./scripts/lightning/add-lightning.sh [id]
```

Creates a Lightning wallet for your current DID (or specified DID alias).

Examples:
```bash
./scripts/lightning/add-lightning.sh          # Current DID
./scripts/lightning/add-lightning.sh work     # Specific DID alias
```

### Check Balance

```bash
./scripts/lightning/lightning-balance.sh [id]
```

Returns current balance in satoshis.

Example output:
```
2257 sats
```

## Receiving Payments

### Create Invoice

```bash
./scripts/lightning/lightning-invoice.sh <amount> <memo> [id]
```

Creates a BOLT11 invoice to receive payment.

**Arguments:**
- `amount` - Amount in satoshis (1000 = 0.00001 BTC)
- `memo` - Description/memo for the invoice
- `id` - (optional) DID alias, defaults to current identity

**Example:**
```bash
./scripts/lightning/lightning-invoice.sh 1000 "Coffee payment"
```

**Output:**
```json
{
  "paymentRequest": "lnbc10u1p...",
  "paymentHash": "a3f7b8c9..."
}
```

Share this invoice with the payer. They can:
- Scan as QR code
- Paste into any Lightning wallet
- Pay via Lightning-enabled app

## Sending Payments

### Pay Invoice (Basic)

```bash
./scripts/lightning/lightning-pay.sh <bolt11> [id]
```

Pay a BOLT11 invoice with automatic payment verification.

**Arguments:**
- `bolt11` - BOLT11 invoice string
- `id` - (optional) DID alias to pay from

**Output:** Success or failure message with exit code

**Example:**
```bash
./scripts/lightning/lightning-pay.sh lnbc10u1p...
# ✅ Payment confirmed
# (exits 0 on success, 1 on failure)
```

The script automatically verifies the payment settled before outputting success.

### ⚠️ Payment Verification Pattern (CRITICAL)

**The payment hash is NOT proof of payment!** Lightning payments can fail, time out, or remain pending.

**Our `lightning-pay.sh` script handles verification automatically:**

```bash
./scripts/lightning/lightning-pay.sh lnbc10u1p...
# ✅ Payment confirmed
# (or "❌ Payment failed or pending" + exit 1)
```

The script verifies the payment settled and outputs a clear success/failure message. No manual checking needed.

**Why verification matters:**
- Payment hash ≠ success (can fail after returning hash)
- Prevents false confirmation (thinking you paid when you didn't)

### Verify Payment Status

```bash
./scripts/lightning/lightning-check.sh <paymentHash> [id]
```

Check whether a payment settled.

**Arguments:**
- `paymentHash` - Payment hash from `lightning-pay`
- `id` - (optional) DID alias

**Returns:**
```json
{
  "paid": true,
  "preimage": "...",
  "amount": 1000
}
```

- `"paid": true` — Payment settled successfully
- `"paid": false` — Payment failed or still pending

### Lightning Address Zapping

```bash
./scripts/lightning/lightning-zap.sh <recipient> <amount> [memo] [id]
```

Send sats to a Lightning Address, DID, or alias.

**Arguments:**
- `recipient` - Lightning Address (`user@domain.com`), DID, or alias
- `amount` - Amount in satoshis
- `memo` - (optional) Message/memo
- `id` - (optional) DID alias to send from

**Examples:**
```bash
# Zap to Lightning Address
./scripts/lightning/lightning-zap.sh user@getalby.com 1000 "Great post!"

# Zap to DID
./scripts/lightning/lightning-zap.sh did:cid:bagaaiera... 5000

# Zap to alias
./scripts/lightning/lightning-zap.sh alice 2000 "Coffee"
```

**Output:** Success or failure message with exit code

**Example:**
```bash
./scripts/lightning/lightning-zap.sh user@getalby.com 1000 "Great post!"
# ✅ Payment confirmed
# (exits 0 on success, 1 on failure)
```

The script automatically verifies the payment settled before outputting success.

**What it does:**
1. Resolves Lightning Address to LNURL endpoint
2. Requests invoice for specified amount
3. Pays invoice
4. Returns payment hash (you still need to verify!)

## Payment History

### List Payments

```bash
./scripts/lightning/lightning-payments.sh [id]
```

Show all Lightning payments (sent and received).

**Example output:**
```
2026/03/05 11:17:38  -100 sats "Payment memo"
2026/03/04 17:08:14  +20 sats "Received payment"
2026/03/03 17:16:31  +25 sats "Test invoice"
```

Format: `YYYY/MM/DD HH:MM:SS  [+/-]amount sats ["memo"]`
- Negative amounts = payments sent
- Positive amounts = payments received
- Memo is optional

## DID Integration

### Publish Lightning Endpoint

```bash
./scripts/lightning/publish-lightning.sh [id]
```

Add your Lightning endpoint to your DID document.

**What it does:**
- Updates your DID document with Lightning service info
- Makes your Lightning endpoint publicly discoverable
- Others can look up your DID and pay you

**Example:**
```bash
./scripts/lightning/publish-lightning.sh

# Your DID document now includes:
# {
#   "didDocument": {
#     "id": "did:cid:bagaaiera...",
#     "service": [{
#       "id": "did:cid:bagaaiera...#lightning",
#       "type": "Lightning",
#       "serviceEndpoint": "http://...onion:4222/invoice/bagaaiera..."
#     }]
#   }
# }
```

### Unpublish Lightning Endpoint

```bash
./scripts/lightning/unpublish-lightning.sh [id]
```

Remove Lightning endpoint from your DID document.

## Utilities

### Decode Invoice

```bash
./scripts/lightning/lightning-decode.sh <bolt11>
```

Inspect BOLT11 invoice details before paying.

**Example output:**
```json
{
  "amount": 1000,
  "description": "Coffee payment",
  "paymentHash": "a3f7b8c9...",
  "timestamp": 1709635800,
  "expiry": 3600,
  "destination": "03..."
}
```

**Use cases:**
- Verify amount before paying
- Check invoice hasn't expired
- Confirm recipient/description
- Extract payment hash for tracking

## Complete Workflow Examples

### Example 1: Simple Payment

```bash
# Alice creates invoice
INVOICE=$(./scripts/lightning/lightning-invoice.sh 1000 "Coffee")
echo "Invoice: $INVOICE"

# Bob pays invoice
RESULT=$(./scripts/lightning/lightning-pay.sh "$INVOICE")
HASH=$(echo "$RESULT" | jq -r .paymentHash)

# Bob verifies payment
STATUS=$(./scripts/lightning/lightning-check.sh "$HASH" | jq -r .paid)
if [ "$STATUS" = "true" ]; then
  echo "✅ Payment confirmed!"
fi

# Alice checks balance
./scripts/lightning/lightning-balance.sh
```

### Example 2: Lightning Address Zap

```bash
# Zap creator via Lightning Address
./scripts/lightning/lightning-zap.sh creator@getalby.com 5000 "Love your content!"
# ✅ Payment confirmed

# Payment verification is automatic - no manual checking needed
```

### Example 3: Invoice Verification

```bash
# Receive a BOLT11 invoice from someone
INVOICE="lnbc10u1p..."

# Decode to verify amount and recipient
./scripts/lightning/lightning-decode.sh "$INVOICE"
# Check amount, description, expiry

# If looks good, pay it
RESULT=$(./scripts/lightning/lightning-pay.sh "$INVOICE")
HASH=$(echo "$RESULT" | jq -r .paymentHash)

# CRITICAL: Verify payment settled
./scripts/lightning/lightning-check.sh "$HASH"
```

### Example 4: Multi-DID Wallet Management

```bash
# Create wallets for different personas
./scripts/lightning/add-lightning.sh personal
./scripts/lightning/add-lightning.sh work
./scripts/lightning/add-lightning.sh project

# Check balances
./scripts/lightning/lightning-balance.sh personal
./scripts/lightning/lightning-balance.sh work
./scripts/lightning/lightning-balance.sh project

# Pay from specific wallet
./scripts/lightning/lightning-pay.sh lnbc10u1p... work
```

### Example 5: Publishing Lightning to DID

```bash
# Create Lightning wallet
./scripts/lightning/add-lightning.sh

# Publish to DID document
./scripts/lightning/publish-lightning.sh

# Others can now discover your Lightning endpoint
# They look up your DID and see your Lightning service

# Later, if you want to unpublish:
./scripts/lightning/unpublish-lightning.sh
```

### Example 6: Sending Invoice via Dmail

```bash
# Alice creates an invoice for 5000 sats
INVOICE_JSON=$(npx @didcid/keymaster lightning-invoice 5000 "Consulting fee")
INVOICE=$(echo "$INVOICE_JSON" | jq -r .paymentRequest)

# Alice sends the invoice to Bob via dmail
npx @didcid/keymaster send-dmail \
  "did:cid:bob..." \
  "Invoice for consulting work" \
  "Please pay this invoice: $INVOICE"

# Bob receives the dmail, extracts the invoice, and pays
npx @didcid/keymaster lightning-pay "$INVOICE"
# ✅ Payment confirmed

# Alice checks her payment history
npx @didcid/keymaster lightning-payments
# Shows the received payment
```

**Why this matters:** Agents can request payment without needing email, phone numbers, or centralized messaging platforms. Just DIDs + Lightning + dmail.

## Environment Setup

All scripts require:

```bash
source ~/.archon.env   # Load wallet path and passphrase
```

This is automatically sourced by the wrapper scripts. `npx` is used to run keymaster, so no nvm sourcing is needed.

**Environment variables (`~/.archon.env`):**
- `ARCHON_WALLET_PATH` - Path to your wallet file
- `ARCHON_PASSPHRASE` - Wallet encryption passphrase
- `ARCHON_GATEKEEPER_URL` - (optional) Gatekeeper endpoint

## Advanced Usage

### Lightning Node Details

Archon Lightning wallets are:
- **Non-custodial** - You control the keys
- **Self-hosted** - Runs via Archon gatekeeper
- **DID-integrated** - Same identity across protocols

The wallet is managed by `@didcid/keymaster` which interfaces with Lightning infrastructure.

### Payment Amounts

Lightning amounts are in **satoshis**:
- 1 satoshi = 0.00000001 BTC
- 1000 sats = 0.00001 BTC (~$0.01 at $100k BTC)
- 100,000 sats = 0.001 BTC (~$1 at $100k BTC)

Minimum payment typically 1 sat, maximum depends on channel capacity.

### Invoice Expiry

BOLT11 invoices typically expire after 1 hour. Check expiry with:

```bash
./scripts/lightning/lightning-decode.sh lnbc10u1p... | jq .expiry
```

### Lightning Address Resolution

Lightning Addresses resolve via LNURL:

```
user@domain.com
→ Query: https://domain.com/.well-known/lnurlp/user
→ Get invoice endpoint
→ Request invoice for amount
→ Pay invoice
```

The `lightning-zap.sh` script handles this automatically.

## Error Handling

### Common Issues

**"No route found":**
- Lightning Network couldn't find path to recipient
- Try smaller amount or wait for better routing

**"Insufficient balance":**
- Check balance: `./scripts/lightning/lightning-balance.sh`
- Add funds to your wallet

**"Invoice expired":**
- Request new invoice from recipient
- Check expiry: `./scripts/lightning/lightning-decode.sh`

**"Payment failed":**
- Always verify with `lightning-check`
- Payment hash ≠ success
- May need to retry with new invoice

### Verification Workflow

```bash
# 1. Attempt payment
RESULT=$(./scripts/lightning/lightning-pay.sh "$INVOICE" 2>&1)

# 2. Check for errors
if ! echo "$RESULT" | jq -e .paymentHash > /dev/null 2>&1; then
  echo "Payment failed: $RESULT"
  exit 1
fi

# 3. Extract payment hash
HASH=$(echo "$RESULT" | jq -r .paymentHash)

# 4. Verify payment settled
for i in {1..5}; do
  STATUS=$(./scripts/lightning/lightning-check.sh "$HASH" | jq -r .paid)
  if [ "$STATUS" = "true" ]; then
    echo "✅ Payment confirmed"
    exit 0
  fi
  sleep 2
done

echo "⏳ Payment still pending or failed"
exit 1
```

## Security Best Practices

### Payment Verification

**Always verify payments settled:**
```bash
# ❌ WRONG
./scripts/lightning/lightning-pay.sh lnbc10u1p...
echo "Paid!" # NO!

# ✅ CORRECT
HASH=$(./scripts/lightning/lightning-pay.sh lnbc10u1p... | jq -r .paymentHash)
./scripts/lightning/lightning-check.sh "$HASH" | jq -r .paid
```

### Invoice Validation

**Before paying, verify:**
- Amount is correct
- Recipient is expected
- Invoice hasn't expired
- Description matches expectation

```bash
./scripts/lightning/lightning-decode.sh lnbc10u1p...
# Check output before paying
```

### Key Security

- Lightning private keys derived from DID seed
- Keep `ARCHON_PASSPHRASE` secure
- Backup your 12-word mnemonic (see `archon-vault` skill)
- Use separate DIDs for different risk profiles

### Amount Limits

- Start with small amounts for testing
- Lightning is for micropayments (< $100 typical)
- Large amounts should use on-chain Bitcoin
- Check balance before sending

## Troubleshooting

### "Command not found: npx"

Ensure Node.js is installed and in your PATH:

```bash
node --version  # Should show v16 or newer
npx --version   # Should show npm version
```

If not installed, install Node.js via your package manager or from https://nodejs.org

### "Cannot read wallet"

```bash
source ~/.archon.env
ls -la "$ARCHON_WALLET_PATH"
# Ensure wallet file exists and is readable
```

### "Payment hash not found"

Payment may still be pending or failed. Wait 5-10 seconds and try `lightning-check` again.

### "Lightning wallet not found"

```bash
./scripts/lightning/add-lightning.sh
# Creates wallet for current DID
```

### Network Issues

If Archon gatekeeper is unreachable:
```bash
echo $ARCHON_GATEKEEPER_URL
# Verify URL is correct

# Try default gatekeeper
unset ARCHON_GATEKEEPER_URL
./scripts/lightning/lightning-balance.sh
```

## Data Storage

Lightning payment data is stored:
- **Locally:** Wallet state in `~/.archon.wallet.json`
- **Network:** Channel state on Lightning Network
- **DID document:** Public endpoint (if published)

No payment history or balances are exposed publicly unless you explicitly publish them.

## Use Cases

**Agent-to-Agent Payments:**
- Pay for API access
- Skill marketplace transactions
- Service subscriptions
- Bounty payments

**Content Monetization:**
- Paywalled articles
- Per-use API access
- Streaming sats for media
- Microtips for social posts

**Real-Time Payments:**
- Pay-per-compute
- Storage payments
- Data feed subscriptions
- Time-based access

**Value-4-Value:**
- Podcast boosts
- Creator support
- Open source tips
- P2P payments

## References

- Archon documentation: https://github.com/archetech/archon
- Keymaster reference: https://github.com/archetech/archon/tree/main/keymaster
- Lightning Network: https://lightning.network
- BOLT specifications: https://github.com/lightning/bolts
- Lightning Address: https://lightningaddress.com

## Related Skills

- **archon-keymaster** — Core DID management and credentials
- **archon-vault** — Encrypted backups and disaster recovery
- **archon-cashu** — Ecash tokens with DID locking

---

**⚡ Powered by Lightning. Secured by Archon. Built for agents.**
