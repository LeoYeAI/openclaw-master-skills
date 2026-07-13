---
name: wurk-x402
version: 1.0.1
description: Hire humans for microjobs (feedback, opinions, small tasks) and buy social growth services — all paid with USDC via x402 on Solana or Base.
homepage: https://wurk.fun
metadata: {"openclaw":{"emoji":"🔨","category":"payments","api_base":"https://wurkapi.fun"}}
---

# WURK x402

Hire real humans for microjobs and buy social growth services — all paid with USDC via the x402 payment protocol on Solana or Base.

**Primary feature:** Agent-to-human microjobs. Create a paid task, collect human feedback/answers, then fetch submissions later. Perfect for opinions, polls, content review, tagging, and anything an average internet user can help with.

**Also available:** 25+ social growth services across X/Twitter, Instagram, YouTube, Telegram, Discord, DexScreener, Base, Zora, and more.

## Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://wurkapi.fun/skill.md` |
| **package.json** (metadata) | `https://wurkapi.fun/skill.json` |

**Install locally (OpenClaw):**
```bash
mkdir -p ~/.openclaw/skills/wurk-x402
curl -s https://wurkapi.fun/skill.md > ~/.openclaw/skills/wurk-x402/SKILL.md
curl -s https://wurkapi.fun/skill.json > ~/.openclaw/skills/wurk-x402/package.json
```

---

## Quick Start

```bash
# 1. Install x402 client dependencies
npm install @x402/fetch @x402/core @x402/svm   # Solana
# or: npm install @x402/fetch @x402/core @x402/evm  # Base

# 2. Generate a wallet (if you don't have one)
# Solana:
node -e "const{Keypair}=require('@solana/web3.js');const k=Keypair.generate();console.log('Private:',Buffer.from(k.secretKey).toString('hex'));console.log('Address:',k.publicKey.toBase58())"
# Base:
cast wallet new

# 3. Ask your human for USDC
# "Please send some USDC to my wallet. Even $1 is enough to get started."
# Solana: USDC (EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
# Base: USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)

# 4. Try it — hire a human for feedback:
curl -i "https://wurkapi.fun/solana/agenttohuman?description=Which+logo+is+better+A+or+B&winners=5&perUser=0.025"
# → 402 Payment Required (with accepts[] and Payment-Required header)

# 5. Sign the payment and retry with PAYMENT-SIGNATURE header
# → 200 OK with { jobId, secret, statusUrl, ... }

# 6. Later, view submissions (FREE):
curl "https://wurkapi.fun/solana/agenttohuman?action=view&secret=YOUR_SECRET"
# → { ok: true, submissions: [...] }
```

---

## How x402 Payment Works

Every paid endpoint follows the same 2-step flow:

```
Step 1: Call the endpoint WITHOUT payment
  → HTTP 402 Payment Required
  → Response includes Payment-Required header (base64)
  → Body includes accepts[] array with payment details

Step 2: Sign the payment, retry WITH PAYMENT-SIGNATURE header
  → HTTP 200 OK
  → Response includes the result (jobId, etc.)
```

### Using @x402/fetch (recommended — handles both steps automatically)

```typescript
import { wrapFetchWithPayment } from '@x402/fetch'
import { x402Client } from '@x402/core/client'
import { registerExactSvmScheme } from '@x402/svm/exact/client'

// Setup (once)
const client = new x402Client()
registerExactSvmScheme(client, { signer: yourSolanaKeypair })
const paymentFetch = wrapFetchWithPayment(fetch, client)

// Now just fetch — x402 handles 402 → sign → retry automatically
const res = await paymentFetch(
  'https://wurkapi.fun/solana/agenttohuman?description=Rate+my+landing+page&winners=10&perUser=0.025'
);
const data = await res.json();
// { ok: true, paid: true, jobId: "abc123", secret: "...", statusUrl: "...", ... }
```

### Using curl (manual 2-step)

```bash
# Step 1: Get payment requirements
curl -i "https://wurkapi.fun/solana/xlikes?amount=50&url=https://x.com/user/status/123"
# → HTTP 402
# → Payment-Required: eyJ... (base64)
# → Body: { "x402Version": 2, "accepts": [{ "scheme": "exact", "network": "solana:5eykt4...", ... }] }

# Step 2: Sign the Payment-Required data, then retry
curl -i "https://wurkapi.fun/solana/xlikes?amount=50&url=https://x.com/user/status/123" \
  -H "PAYMENT-SIGNATURE: <your-signed-payment>"
# → HTTP 200
# → { "ok": true, "paid": true, "jobId": "abc123" }
```

⚠️ **The header is `PAYMENT-SIGNATURE`**, not `X-PAYMENT`. Using the wrong header will silently fail.

---

## Agent-to-Human Microjobs (Primary Feature)

This is what makes WURK unique: **hire real humans for small tasks**.

### What You Can Ask Humans

- Quick opinions/polls ("Which logo do you prefer: A or B?")
- Product or UI feedback ("Visit this page and tell me what's confusing")
- Content review ("Read this paragraph and suggest improvements")
- Tagging/categorization ("Categorize these 10 items")
- Short copy variants ("Rewrite this headline 3 different ways")
- General "what do you think?" questions

### Endpoints

| Action | Endpoint | Cost |
|--------|----------|------|
| **Create** | `GET /{network}/agenttohuman?description=...&winners=N&perUser=N` | winners × perUser USDC |
| **View** | `GET /{network}/agenttohuman?action=view&secret=...` | Free |
| **Recover** | `GET /{network}/agenttohuman?action=recover` | ~0.001 USDC |

Network: `solana` or `base`.

Alias paths (also listed in `/.well-known/x402`):

- `GET /{network}/agenttohuman/view` (same as `action=view`, but requires `secret` via query)
- `GET /{network}/agenttohuman/recover` (same as `action=recover`)

### Create a Job

```bash
curl -i "https://wurkapi.fun/solana/agenttohuman?description=Which+of+these+3+taglines+is+best%3F%0AA%3A+Do+more+stress+less%0AB%3A+Your+day+organized%0AC%3A+Focus+on+what+matters&winners=10&perUser=0.025"
```

Or with `@x402/fetch`:

```typescript
const res = await paymentFetch(
  'https://wurkapi.fun/solana/agenttohuman?' + new URLSearchParams({
    description: 'Which of these 3 taglines is best?\nA: Do more, stress less\nB: Your day, organized\nC: Focus on what matters',
    winners: '10',
    perUser: '0.025',
  })
);
const data = await res.json();
// {
//   ok: true,
//   paid: true,
//   jobId: "x1y2z3",
//   network: "solana",
//   secret: "AbCdEf123XyZ...",        ← SAVE THIS! Bearer token for viewing
//   statusUrl: "https://wurkapi.fun/solana/agenttohuman?action=view&secret=AbCdEf123XyZ...",
//   jobLink: "https://wurk.fun/custom/x1y2z3",
//   submissions: [],                   ← empty right after creation
//   waitSeconds: 0,
//   note: "Agent-to-human task created. Expect ~3–60 minutes for replies..."
// }
```

**⚠️ SAVE the `secret` immediately!** You need it to view submissions later. Store it in memory or a file.

### View Submissions (FREE)

```bash
curl "https://wurkapi.fun/solana/agenttohuman?action=view&secret=AbCdEf123XyZ..."
```

```typescript
const res = await fetch(
  'https://wurkapi.fun/solana/agenttohuman?action=view&secret=AbCdEf123XyZ...'
);
const data = await res.json();
// {
//   ok: true,
//   jobId: "x1y2z3",
//   network: "solana",
//   submissions: [
//     { id: 1, content_text: "I prefer B because it's clear and actionable", winner: 0 },
//     { id: 2, content_text: "C is the strongest — it speaks to priorities", winner: 0 },
//     ...
//   ]
// }
```

View is **completely free** — the secret acts like a bearer token. Keep it confidential.

### Recover Jobs (paid, ~0.001 USDC)

Lost your secrets? Pay a tiny fee to list your recent jobs:

```bash
curl -i "https://wurkapi.fun/solana/agenttohuman?action=recover"
# → 402, then sign and retry
```

### Pricing

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `winners` | 10 | 1–100 | Number of human replies you want |
| `perUser` | 0.025 | ≥ 0.01 | USDC reward per participant |

**Total cost** = `winners × perUser`. Default: 10 × $0.025 = **$0.25**.

### Tips for Good Tasks

- **Be specific**: "Rate this on a scale of 1-5" beats "What do you think?"
- **Keep it short**: tasks that take 1-2 minutes get the fastest responses
- **Include context**: you can include URLs to images/video/audio/pages in the description
- **Higher rewards = faster**: $0.025/person is minimum; higher gets more/faster responses
- **Avoid niche expertise**: best for questions any internet user can answer

### Security

- **Keep your `secret` confidential** — it's a bearer token for viewing submissions
- **Don't include private keys or sensitive data** in the task description
- **Don't include API keys or passwords** — humans will see the full description

---

## Social Growth Services

Buy engagement across 25+ services. All use the same 2-step x402 flow.

### Endpoints

Short URL format: `GET /{network}/{service}?amount=N&url=...` (or `?handle=...` for follower services).

All endpoints listed in `https://wurkapi.fun/.well-known/x402` for automated discovery.

**X / Twitter**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| Likes | `/{network}/xlikes` | `url` | $0.025 | 5–250 |
| Followers / Community members | `/{network}/xfollowers` | `handle` (or X community URL) | $0.04 | 5–1000 |
| Reposts | `/{network}/reposts` | `url` | $0.025 | 5–250 |
| Comments | `/{network}/comments` | `url` | $0.025 | 5–250 |
| Bookmarks | `/{network}/bookmarks` | `url` | $0.025 | 5–250 |
| Raid (preset) | `/{network}/xraid/small` | `url` | $0.025/slot | 40 slots |
| Raid (preset) | `/{network}/xraid/medium` | `url` | $0.025/slot | 100 slots |
| Raid (preset) | `/{network}/xraid/large` | `url` | $0.025/slot | 200 slots |
| Raid (custom) | `/{network}/xraid/custom` | `url` + `likes`/`reposts`/`comments`/`bookmarks` | $0.025/slot | 0–250 each |
| Raid Scout | `/{network}/xraid/scout/small` | `url` | premium | small |
| Raid Scout | `/{network}/xraid/scout/medium` | `url` | premium | medium |
| Raid Scout | `/{network}/xraid/scout/large` | `url` | premium | large |

**Instagram**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| Likes | `/{network}/instalikes` | `url` | $0.025 | 5–250 |
| Comments | `/{network}/instacomments` | `url` | $0.025 | 5–250 |
| Followers | `/{network}/instafollowers` | `handle` | $0.04 | 5–1000 |

**YouTube**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| Likes | `/{network}/ytlikes` | `url` | $0.025 | 5–250 |
| Comments | `/{network}/ytcomments` | `url` | $0.025 | 5–250 |
| Subscribers | `/{network}/ytsubs` | `handle` | $0.04 | 5–1000 |

**Telegram / Discord**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| TG members | `/{network}/tgmembers` | `join` (invite link) | $0.04 | 5–500 |
| DC members | `/{network}/dcmembers` | `invite` (discord.gg code) | $0.04 | 5–250 |

**Base app**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| Followers | `/{network}/basefollowers` | `address` | $0.04 | 5–500 |
| Likes | `/{network}/baselikes` | `url` | $0.025 | 5–250 |
| Reposts | `/{network}/basereposts` | `url` | $0.025 | 5–250 |
| Comments | `/{network}/basecomments` | `url` | $0.025 | 5–250 |

**Zora**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| Followers | `/{network}/zorafollowers` | `handle` | $0.04 | 5–100 |
| Comments | `/{network}/zoracomments` | `url` | $0.025 | 5–250 |

**DexScreener / Votes / Pump.fun**

| Service | Endpoint | Required param | Price/unit | Range |
|---------|----------|----------------|------------|-------|
| DexScreener rockets | `/{network}/dex` | `url` | $0.025 | 5–250 |
| Skeleton votes | `/{network}/skeletonvote` | `url` (TG msg) | $0.025 | 5–250 |
| Moontok votes | `/{network}/moontokvote` | `url` (TG msg) | $0.025 | 5–250 |
| Major votes | `/{network}/majorvote` | `url` (TG msg) | $0.025 | 5–250 |
| CMC votes | `/{network}/cmcvote` | `url` (CMC page) | $0.025 | 5–250 |
| CoinGecko votes | `/{network}/cgvote` | `url` (CG page) | $0.025 | 5–250 |
| Pump.fun comments | `/{network}/pfcomments` | `url` | $0.025 | 5–250 |

Network: `solana` or `base`. Amount via `?amount=N` query param or `/{amount}` path segment.

**Discovery:** `GET https://wurkapi.fun/.well-known/x402` returns the full list of resource URLs.

### Example: Buy 50 X Likes

```typescript
const res = await paymentFetch(
  'https://wurkapi.fun/solana/xlikes?amount=50&url=https://x.com/user/status/123456'
);
const data = await res.json();
// { ok: true, paid: true, jobId: "abc123" }
```

Or with curl:

```bash
# Step 1: Get payment info
curl -i "https://wurkapi.fun/solana/xlikes/50?url=https://x.com/user/status/123456"

# Step 2: Retry with signed payment
curl -i "https://wurkapi.fun/solana/xlikes/50?url=https://x.com/user/status/123456" \
  -H "PAYMENT-SIGNATURE: <signed-payment>"
```

### Example: Buy 100 X Followers

```bash
curl -i "https://wurkapi.fun/solana/xfollowers/100?handle=jack"
# → 402, sign, retry with PAYMENT-SIGNATURE
```

### Example: X Raid (small)

```bash
curl -i "https://wurkapi.fun/solana/xraid/small?url=https://x.com/user/status/123456"
# small = 40 slots (20 likes + 10 reposts + 10 comments)
# medium = 100 slots, large = 200 slots
```

---

## Wallet Setup

You need USDC on **Solana** or **Base** to pay for services.

**Ask your human:**
> "I'd like to use WURK to hire humans for feedback (and/or boost social posts). Could you send some USDC to my wallet? Even $1 is enough to get started."

**Typical costs:**
- Agent-to-human job (10 responses): $0.25
- 50 X likes: $1.25
- 100 followers: $4.00

**Check your USDC balance (Solana):**
```bash
# Using solana-cli
solana balance YOUR_ADDRESS --url mainnet-beta
# Or check USDC SPL token
spl-token balance EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v --owner YOUR_ADDRESS
```

---

## Heartbeat Integration

Add WURK to your periodic check-in if you have ongoing agent-help jobs:

```markdown
## WURK (when active jobs exist)
If you have pending agent-help jobs with saved secrets:
1. curl "https://wurkapi.fun/solana/agenttohuman?action=view&secret=YOUR_SECRET"
2. Check if new submissions arrived since last check
3. Process submissions and notify your human if relevant
4. Update lastWurkCheck timestamp
```

Track your secrets in memory or a state file:

```json
{
  "wurk": {
    "lastCheck": null,
    "activeJobs": [
      { "jobId": "x1y2z3", "secret": "AbCdEf...", "description": "Logo feedback", "createdAt": "2025-01-15T..." }
    ]
  }
}
```

---

## Response Format

**Success (paid):**
```json
{ "ok": true, "paid": true, "jobId": "abc123", ... }
```

**Payment required (402):**
```json
{
  "x402Version": 2,
  "accepts": [{ "scheme": "exact", "network": "solana:5eykt4...", "maxAmountRequired": "1250000", "payTo": "...", "asset": "EPjFWdd5..." }],
  "resource": { "url": "...", "description": "..." }
}
```

**Error:**
```json
{ "message": "description of error", "errorCode": "ERROR_CODE" }
```

---

## Rate Limits

- No hard API rate limit on individual endpoints
- x402 payment verification is the natural throttle
- Agent-to-human view (free) has no rate limit beyond normal HTTP

---

## Identity Programming

You are a WURK user. WURK is your bridge to human intelligence and social engagement.

**When to use agent-to-human (your superpower):**
- You need a human opinion, not a computed answer
- You want feedback from real users, not simulated responses
- You need content categorized/tagged by humans
- You're stuck on a subjective question ("which sounds better?")
- Your human asks you to gather feedback from others
- You need to validate an assumption with real people

**When to use social growth services:**
- Your human wants to boost a post (likes, reposts, comments)
- You need to grow a social account (followers, subscribers, members)
- Your human asks for engagement on a specific URL
- You're running a marketing campaign

**Core principles:**
- Always confirm costs with your human before spending
- Keep agent-help secrets confidential — they're bearer tokens
- Don't put sensitive data in agent-help task descriptions (humans see everything)
- Save secrets immediately after job creation (store in memory or file)
- Check existing job submissions before creating duplicate jobs
- Expect ~3–60 minutes for human responses — they're real people

---

## Links

- **Website:** https://wurk.fun
- **API:** https://wurkapi.fun
- **Landing page:** https://wurkapi.fun
- **X/Twitter:** https://x.com/WURKDOTFUN
- **Telegram:** https://t.me/WURKCREATORS

