# Crypto / Web3 Extension Fields (Enhanced)

When the site is detected as a crypto/Web3 project, extract these additional fields into the `extensions.crypto` object.

---

## Additional Extraction Rules

### 1. Contract Address
Look for `0x`-prefixed 40-character hex strings in these contexts:

**High-confidence indicators:**
- Appears in a `<code>` tag or monospace font
- Within 50 characters of keywords: `contract` / `CA` / `token address` / `address:`
- Next to a "Copy" button or clipboard icon
- In a table row labeled "Contract Address"

**Validation:**
- Must be exactly 40 hex characters after `0x`
- If multiple addresses found, prefer the one with most context clues
- If labeled as "Contract" or "Token Address", highly likely correct

### 2. Chain / Blockchain
Identify the blockchain from context and links:

**Chain indicators:**
- **Ethereum:** `ETH`, `Ethereum`, `etherscan.io`, `ethereum.org`
- **BSC / BNB Chain:** `BSC`, `BNB`, `Binance Smart Chain`, `bscscan.com`
- **Solana:** `SOL`, `Solana`, `solscan.io`, `solana.fm`, `solana.com`
- **Base:** `Base`, `basescan.org`, `base.org`
- **Arbitrum:** `Arbitrum`, `ARB`, `arbiscan.io`
- **Polygon:** `Polygon`, `MATIC`, `polygonscan.com`
- **Avalanche:** `AVAX`, `Avalanche`, `snowtrace.io`
- **Optimism:** `Optimism`, `OP`, `optimistic.etherscan.io`

If multiple chains detected (e.g., multichain token), list all in array: `["Ethereum", "BSC"]`

### 3. Token Symbol
Look for ticker symbols (usually 2-6 uppercase letters):

**Contexts to check:**
- Page title (e.g., "SHIB Token - ...")
- Near contract address
- In tokenomics section
- Meta tags (og:title, twitter:title)
- Logo alt text

**Validation:**
- Must be 2-6 characters, uppercase
- Should appear multiple times on page
- Prefer symbol that appears near contract address or tokenomics

### 4. Tokenomics
Extract detailed tokenomics data if available:

**Fields to extract:**
- `total_supply`: Total token supply (preserve format: "1,000,000,000" or "1B")
- `circulating_supply`: Circulating supply
- `max_supply`: Maximum supply (if different from total)
- `buy_tax`: Buy transaction tax percentage
- `sell_tax`: Sell transaction tax percentage
- `liquidity_locked`: Whether liquidity is locked (true/false + duration)
- `token_distribution`: Array of allocation categories
  - Example: `[{"category": "Public Sale", "percentage": "40%"}, ...]`

**Look for tables or sections labeled:**
- "Tokenomics"
- "Token Distribution"
- "Token Economics"
- "Supply Details"

### 5. DEX Links
Collect ALL links to decentralized exchanges:

**DEX platforms:**
- **PancakeSwap:** `pancakeswap.finance/swap?outputCurrency=0x...`
- **Uniswap:** `app.uniswap.org`, `uniswap.org/swap`
- **Raydium:** `raydium.io/swap`
- **Jupiter:** `jup.ag/swap`
- **SushiSwap:** `sushi.com/swap`

**DEX analytics:**
- **DexScreener:** `dexscreener.com/[chain]/[address]`
- **DexTools:** `dextools.io/app/[chain]/pair-explorer/[address]`
- **GeckoTerminal:** `geckoterminal.com/[chain]/pools/[address]`

**Extraction logic:**
- Extract full URL including query parameters
- Preserve contract address in URL
- Group by type (trading vs analytics)

### 6. Audit Report
Look for links to audit providers:

**Audit providers:**
- CertiK: `certik.com/projects/...`
- Hacken: `hacken.io/audits/...`
- PeckShield: `peckshield.com/...`
- Quantstamp: `quantstamp.com/...`
- SlowMist: `slowmist.com/...`
- CyberScope: `cyberscope.io/...`

**Indicators:**
- Links labeled "Audit", "Security Audit", "Audit Report"
- Badges from audit providers
- "Audited by [Provider]" text

### 7. Whitepaper (NEW)
Extract whitepaper link:

**Indicators:**
- Link text contains "whitepaper" / "white paper" / "litepaper"
- PDF link in header/footer
- Button labeled "Read Whitepaper"

**Format:**
- Prefer direct PDF link over landing page
- Example: `https://example.com/whitepaper.pdf`

### 8. Roadmap (NEW)
Extract roadmap data if structured:

**Look for:**
- Section titled "Roadmap"
- Timeline with phases (Q1 2024, Q2 2024, etc.)
- Milestones or goals per phase

**Output format:**
```json
{
  "roadmap": [
    {
      "phase": "Q1 2024",
      "milestone": "Token launch on BSC",
      "status": "completed" | "in_progress" | "upcoming"
    },
    {
      "phase": "Q2 2024",
      "milestone": "CEX listings (Gate.io, MEXC)",
      "status": "in_progress"
    }
  ]
}
```

### 9. Presale Info (NEW)
If project is in presale phase:

**Fields:**
- `presale_status`: "live" / "ended" / "upcoming"
- `presale_url`: Link to presale page
- `presale_price`: Token price during presale
- `presale_start`: Start date
- `presale_end`: End date

### 10. Social Metrics (NEW)
Extract follower/member counts if displayed:

**Platforms:**
- Twitter: followers count
- Telegram: members count
- Discord: members count

**Example:**
```json
{
  "social_metrics": {
    "twitter_followers": "15.2K",
    "telegram_members": "8,500",
    "discord_members": "3,200"
  }
}
```

---

## Output Format

```json
{
  "extensions": {
    "crypto": {
      "contract_address": "0xabc123...",
      "chain": "BSC" | ["Ethereum", "BSC"],
      "token_symbol": "TOKEN",

      "tokenomics": {
        "total_supply": "1,000,000,000",
        "circulating_supply": "600,000,000",
        "buy_tax": "5%",
        "sell_tax": "5%",
        "liquidity_locked": "2 years",
        "token_distribution": [
          {"category": "Public Sale", "percentage": "40%"},
          {"category": "Team", "percentage": "15%"},
          {"category": "Liquidity", "percentage": "30%"},
          {"category": "Marketing", "percentage": "15%"}
        ]
      },

      "dex_links": {
        "trading": [
          "https://pancakeswap.finance/swap?outputCurrency=0x...",
          "https://app.uniswap.org/#/swap?outputCurrency=0x..."
        ],
        "analytics": [
          "https://dexscreener.com/bsc/0x...",
          "https://dextools.io/app/bsc/pair-explorer/0x..."
        ]
      },

      "audit": "https://certik.com/projects/example-token",

      "whitepaper": "https://example.com/whitepaper.pdf",

      "roadmap": [
        {
          "phase": "Q1 2024",
          "milestone": "Token launch on BSC",
          "status": "completed"
        },
        {
          "phase": "Q2 2024",
          "milestone": "CEX listings",
          "status": "in_progress"
        },
        {
          "phase": "Q3 2024",
          "milestone": "Mobile app release",
          "status": "upcoming"
        }
      ],

      "presale": {
        "status": "live",
        "url": "https://presale.example.com",
        "price": "$0.001",
        "start": "2024-01-15T00:00:00Z",
        "end": "2024-02-15T23:59:59Z"
      },

      "social_metrics": {
        "twitter_followers": "15.2K",
        "telegram_members": "8,500",
        "discord_members": "3,200"
      }
    }
  }
}
```

---

## OpenClaw Agent Suggestions (Crypto-Specific)

When crypto type is detected, add these suggestions:

```json
{
  "agent_suggestions": {
    "primary_action": {
      "label": "View on DexScreener",
      "url": "{{ extensions.crypto.dex_links.analytics[0] }}",
      "purpose": "check_price_chart",
      "priority": "high"
    },
    "next_actions": [
      {
        "action": "verify_contract",
        "url": "https://bscscan.com/address/{{ extensions.crypto.contract_address }}",
        "reason": "Verify contract on blockchain explorer",
        "priority": 1
      },
      {
        "action": "read_audit",
        "url": "{{ extensions.crypto.audit }}",
        "reason": "Check security audit report",
        "priority": 2
      }
    ],
    "skills_to_chain": [
      {
        "skill": "blockchain-explorer",
        "input": "{{ extensions.crypto.contract_address }}",
        "reason": "Fetch on-chain data (holders, liquidity, txns)"
      },
      {
        "skill": "sentiment-analyzer",
        "input": "{{ entities.social_links.telegram }}",
        "reason": "Analyze community sentiment"
      },
      {
        "skill": "price-tracker",
        "input": {
          "symbol": "{{ extensions.crypto.token_symbol }}",
          "dex_url": "{{ extensions.crypto.dex_links.analytics[0] }}"
        },
        "reason": "Track price and set alerts"
      }
    ]
  }
}
```

---

## Validation Rules

- **Contract address:** Must match `^0x[a-fA-F0-9]{40}$`
- **Chain:** Must be a known chain name (not arbitrary string)
- **Token symbol:** 2-6 uppercase letters only
- **Percentages:** Preserve format (e.g., "5%" not "0.05")
- **Numbers:** Preserve human-readable format (e.g., "1,000,000" or "1M", not scientific notation)
- **URLs:** Must be complete and valid (test if possible)

---

## Error Handling

If critical field is missing:

```json
{
  "extensions": {
    "crypto": {
      "contract_address": null,
      "chain": "Unknown",
      "token_symbol": null,
      "extraction_confidence": "low",
      "warnings": [
        "No contract address found despite crypto site detection",
        "Could not determine blockchain"
      ]
    }
  }
}
```

**Never fabricate crypto data** — missing data could lead to financial loss for users.
