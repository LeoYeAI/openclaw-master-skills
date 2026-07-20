# archon-lightning

> Lightning Network payments powered by Archon DIDs

Send and receive Bitcoin over Lightning. No custody. No permission. Just your DID and the Lightning Network.

## What is this?

`archon-lightning` integrates the Lightning Network with [Archon](https://github.com/archetech/archon) decentralized identities (DIDs). Your DID becomes your Lightning identity - no separate wallet app, no custodian, no KYC.

- ⚡ **Lightning wallets for DIDs** - Each DID can have its own Lightning wallet
- 💸 **Send/receive sats** - Pay BOLT11 invoices or create invoices to receive payments
- ⚡ **Lightning Address zaps** - Send to `user@domain.com` Lightning Addresses, DIDs, or aliases
- ✅ **Payment verification** - Cryptographic proof that payments settled
- 📊 **Payment history** - Track all Lightning transactions
- 🔗 **DID integration** - Publish your Lightning endpoint to your DID document

All powered by your Archon DID - same cryptographic identity across protocols.

## Why does this matter?

**The problem:** AI agents need to pay for services (APIs, compute, data). Traditional payment rails require:
- Bank accounts (agents can't open them)
- Credit cards (same problem)
- Custodial services (trust someone else with your funds)
- Complex integrations (OAuth, API keys, rate limits)

**The solution:** Lightning Network provides:
- Instant payments (sub-second settlement)
- Micropayments (pay per API call, not monthly subscriptions)
- Global reach (no borders, no intermediaries)
- Privacy (no personal information required)
- Non-custodial (your keys, your coins)

Archon DIDs + Lightning = **financial autonomy for AI agents**.

## Quick Examples

### Create a Lightning Wallet

```bash
./scripts/lightning/add-lightning.sh
```

Your DID now has a Lightning wallet. That's it.

### Check Balance

```bash
./scripts/lightning/lightning-balance.sh
```

### Receive Sats (Create Invoice)

```bash
./scripts/lightning/lightning-invoice.sh 1000 "Coffee payment"
# Returns: {"paymentRequest": "lnbc10u1...", "paymentHash": "..."}
```

Extract the `paymentRequest` value and share it. When paid, sats arrive in your wallet instantly.

### Pay an Invoice

```bash
./scripts/lightning/lightning-pay.sh lnbc10u1...
# ✅ Payment confirmed
# (or "❌ Payment failed or pending" if payment didn't settle)
```

Payment verification is built-in - the script automatically verifies before outputting success.

### Zap via Lightning Address

```bash
./scripts/lightning/lightning-zap.sh user@getalby.com 1000 "Great post!"
# ✅ Payment confirmed
```

Send to Lightning Addresses, DIDs, or aliases - all in one command. Payment verification is automatic.

### Payment History

```bash
./scripts/lightning/lightning-payments.sh
```

## What Can You Build?

**AI-to-AI Payments:**
- Agent pays another agent for API access
- Skill marketplace with Lightning payments
- Bounties paid in sats for completed tasks
- Subscription services charged per-use

**Content Monetization:**
- Pay-per-article (unlock with Lightning payment)
- Streaming sats for video/audio
- Microtips for social media posts
- Paywalled APIs

**Decentralized Services:**
- Pay for compute/storage in real-time
- Lightning-gated access control
- Atomic payments for data feeds
- Cross-agent value transfer

**Value-4-Value:**
- Podcast boosts/streaming sats
- Creator tips via Lightning Address
- P2P payments without intermediaries

## How It Works

### Lightning Wallet Creation

When you run `add-lightning`, your DID creates a Lightning wallet using your DID's cryptographic identity:

```
DID private key → Lightning node seed → Lightning wallet
```

The wallet is non-custodial - you control the keys, you control the funds.

### Payment Flow

**Receiving:**
1. Create invoice (`lightning-invoice`) → BOLT11 string
2. Share invoice (QR code, copy/paste, etc.)
3. Payer pays → sats arrive in your wallet
4. Check invoice status (`lightning-check`)

**Sending:**
1. Get BOLT11 invoice (from recipient)
2. Decode (optional: `lightning-decode` to verify amount/recipient)
3. Pay (`lightning-pay`) → returns payment hash
4. **Verify payment settled** (`lightning-check`)

### Payment Verification Pattern

**⚠️ Critical Security Pattern:**

A payment hash does NOT mean the payment succeeded. Lightning payments can:
- Be pending (not yet routed)
- Fail (no route, insufficient balance)
- Time out (invoice expired)

**Our `lightning-pay.sh` script handles this automatically:**

```bash
./scripts/lightning/lightning-pay.sh lnbc10u1...
# ✅ Payment confirmed
# (or exits with error if payment failed)
```

The script verifies the payment settled and outputs a clear success/failure message. No manual checking needed.

### Lightning Address

Lightning Addresses (`user@domain.com`) are human-readable payment endpoints. They resolve to BOLT11 invoices via LNURL.

```bash
./scripts/lightning/lightning-zap.sh user@getalby.com 1000
```

Behind the scenes:
1. Query `https://domain.com/.well-known/lnurlp/user`
2. Get invoice endpoint
3. Request invoice for amount
4. Pay BOLT11 invoice
5. Verify payment

### DID Integration

Publish your Lightning endpoint to your DID document so others can pay you:

```bash
./scripts/lightning/publish-lightning.sh
```

Your DID document now includes a Lightning service entry:
```json
{
  "didDocument": {
    "id": "did:cid:bagaaiera...",
    "service": [
      {
        "id": "did:cid:bagaaiera...#lightning",
        "type": "Lightning",
        "serviceEndpoint": "http://...onion:4222/invoice/bagaaiera..."
      }
    ]
  }
}
```

Anyone can look up your DID and pay you via Lightning.

## Installation

```bash
# Clone the agent-skills repo
git clone https://github.com/archetech/agent-skills
cd agent-skills/archon-lightning

# Prerequisites: Archon identity configured
# (If not, see archon-keymaster first)

# Create Lightning wallet
./scripts/lightning/add-lightning.sh

# Verify it worked
./scripts/lightning/lightning-balance.sh
# {"balance": 0}
```

See [SKILL.md](./SKILL.md) for complete documentation.

## Architecture

```
archon-lightning/
├── scripts/
│   └── lightning/
│       ├── add-lightning.sh           # Create wallet
│       ├── lightning-balance.sh       # Check balance
│       ├── lightning-invoice.sh       # Create invoice
│       ├── lightning-pay.sh           # Pay invoice
│       ├── lightning-check.sh         # Verify payment
│       ├── lightning-zap.sh           # Lightning Address payment
│       ├── lightning-payments.sh      # Payment history
│       ├── publish-lightning.sh       # Publish to DID
│       ├── unpublish-lightning.sh     # Remove from DID
│       └── lightning-decode.sh        # Decode invoice
├── README.md                          # This file
└── SKILL.md                          # Complete technical docs
```

All scripts wrap the [@didcid/keymaster](https://github.com/archetech/archon/tree/main/keymaster) CLI with environment setup and error handling.

## Real-World Usage

**Morningstar (AI agent):**
- DID: `did:cid:bagaaieranxnl4gmwyw2nv4imoo5fuwvsa4ihba4clp5l22twztuwevjrevha`
- Lightning wallet for paid API access
- Receives tips via Lightning Address
- Pays for compute resources in real-time

**Use cases already working:**
- Agent-to-agent service payments
- Micropayments for API calls
- Value-4-value content tipping
- Lightning-gated access control

## Security Model

**What you trust:**
- Your hardware (runs the Lightning node)
- Lightning Network (routing and settlement)
- Mathematics (cryptographic proofs)
- Open source code (audit everything)

**What you DON'T trust:**
- Central servers (Lightning is peer-to-peer)
- Custodians (you control your keys)
- Banks (no traditional finance involved)
- Payment processors (direct payments)

## Roadmap

**Current capabilities:**
- ✅ Wallet creation and management
- ✅ Invoice generation and payment
- ✅ Lightning Address zapping
- ✅ Payment verification
- ✅ Balance checking and history
- ✅ DID document integration

## Contributing

Found a bug? Want a feature? Have a use case?

- **Issues:** https://github.com/archetech/agent-skills/issues
- **Discussions:** https://github.com/archetech/archon/discussions
- **Archon core:** https://github.com/archetech/archon

## License

Same as parent repo: [agent-skills license](https://github.com/archetech/agent-skills)

## Learn More

- **Lightning Network:** https://lightning.network
- **BOLT specs:** https://github.com/lightning/bolts
- **Lightning Address:** https://lightningaddress.com
- **Archon documentation:** https://github.com/archetech/archon
- **Complete skill documentation:** [SKILL.md](./SKILL.md)

---

**⚡ Powered by Lightning. Secured by Archon. Built for agents.**
