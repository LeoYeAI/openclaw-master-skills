---
name: Crab Catch
description: |
  Crab Catch is a Web3 research skill that automatically collects and
  organizes project data and potential risks from social media, websites,
  code, and on-chain data, and produces a complete and objective
  research report.
metadata:
  author: NotevenDe
  version: 2.1.0
---

# Crab Catch — Research Skill Orchestration

## Prerequisites

CLAWBOT **must run** these commands at session start (not just read them):

```bash
which agent-browser || npm install -g agent-browser
agent-browser install
```

## Data Sources

CLAWBOT is the research driver — responsible for analysis, judgment, iteration,
and report generation. The APIs, scripts, and tools below are **data-fetching
methods only**.

**API Base URL**: `https://crab-skill.opsat.io`

### Signature Authentication

All API requests except `/api/health` require Crab signature headers.

1. Run `node skills/scripts/crab-sign.js` **once** at session start to get headers JSON.
   (First run auto-generates credentials; cached signature reused if still valid within 24h.)
2. Store the output and attach these four headers to **all** subsequent API requests:
   `X-Crab-Timestamp`, `X-Crab-Signature`, `X-Crab-Key`, `X-Crab-Address`.
3. Only re-run with `--refresh` if API returns `auth_expired`.

### Twitter & Social Data (see `twitter-analysis/SKILL.md` for full params)

| Category | Key endpoints | Purpose |
|----------|---------------|---------|
| Profile | `/api/twitter/user`, `tweets`, `replies` | Basic info, content, interactions |
| Risk signals | `/api/twitter/deleted-tweets`, `follower-events` | Removed content, follow/unfollow patterns |
| Reply threads | `/api/readx/tweet-detail-conversation-v2` | Primary comment source (fast, raw data) |
| Quote tweets | `/api/readx/tweet-quotes` | KOL commentary, community opinions with context |
| Engagement data | `/api/readx/tweet-detail-v2` | Views/source — detect bot-inflation |
| Deleted content | `/api/readx/tweet-results-by-ids` | Batch fetch deleted tweet snapshots |
| Long-form | `/api/readx/tweet-article` | Technical analyses, roadmaps published as articles |
| Relationships | `/api/readx/following-light`, `friendships-show` | Inner circle, team relationship verification |
| Credibility | `/api/twitter/kol-followers`, `/api/readx/user-verified-followers` | Who credible follows them (`verified-followers` needs `user_id` not username) |
| Search | `/api/twitter/search`, `/api/readx/search2` | Risk signals, disputes, community discussions |

### GitHub Code (see `github-analysis/SKILL.md`)

Local script `skills/scripts/github_analyze.js` — no external API.
`convertToMarkdown(url, options)` or `analyzeRepository(url, options)`.

### On-chain Data (see `onchain-audit/SKILL.md`)

**Binance API** — `address` + `chainName` (uppercase: `BSC`/`ETHEREUM`/`BASE`/`SOLANA`):

| Endpoint | Description |
|----------|-------------|
| `/api/onchain/audit` | Contract audit (dual-source) |
| `/api/onchain/token-info` | Token metadata and market dynamics |
| `/api/onchain/wallet` | Wallet positions (BSC/BASE/SOLANA only) |
| `/api/onchain/token-search` | Token search (requires `keyword`) |

**Bitget API** — `chain` + `contract` (lowercase: `bnb`/`eth`/`base`/`sol`):

| Endpoint | Description |
|----------|-------------|
| `/api/onchain-2/token-info` | Token details |
| `/api/onchain-2/token-price` | Token price |
| `/api/onchain-2/tx-info` | Transaction statistics |
| `/api/onchain-2/liquidity` | Liquidity pool info |
| `/api/onchain-2/security-audit` | Security audit |

**Onchain Explorer API** — `chain` + `address` (see `API_EXPLORER.md` for full params):

| Endpoint | Chain | Description |
|----------|-------|-------------|
| `/api/explorer/contract` | ETH, BSC | Contract ABI, source code, compiler info, proxy detection |
| `/api/explorer/token-history` | ETH, BSC, SOL | Token transfer history with pagination |
| `/api/explorer/sol-address` | SOL | SOL/SPL balances + recent transfer records |

### Website Content (see `agent-browser/SKILL.md`)

CLAWBOT uses `agent-browser` CLI to open and inspect websites.

## Language Preference

Output language **matches the user's input language**; default **Chinese (zh-CN)**.
Raw API data (usernames, tickers, addresses, code) stays in original form.

## Orchestration Flow

**Callback-driven**: each module's output triggers queries in other modules.
Modules keep feeding each other until no new high-value leads remain.

```
User provides URL / Ticker / contract address + research intent
  │
  ▼
Step 1 — Parse input, initialize entity queue
  Extract: Twitter links, GitHub repos, contract addresses, tickers, chain
  Aggregator URLs → extract entities from path (see rules below)

  Initialize:
    entity_queue  = [{ entity, type, depth: 0 }]
    processed     = set()
    claims        = []    # official claims to verify later
    fund_trace    = []    # addresses to trace fund flow
    team_members  = []    # { handle, role, source }
    MAX_DEPTH     = 2
  │
  ▼
Step 2 — Multi-module collection

  While entity_queue is not empty:
    pop → skip if processed or depth > MAX_DEPTH → route by type:
      URL      → 2a Website
      Twitter  → 2b Social
      GitHub   → 2c Code
      Contract → 2d Chain
      Ticker   → 2d token-search first
    After each module: extract new entities → queue at depth+1
    (see Cross-module Callback Summary below for full routing)

  ── 2a. Website exploration ──────────────────────────────────

  **Use `agent-browser` CLI** (see agent-browser/SKILL.md for commands).
  agent-browser renders JS, captures interactive elements, and allows
  clicking through pages — essential for DApp testing and dynamic sites.
  Fallback to WebFetch only when agent-browser fails (e.g. install issue).

  Visit pages in order:
    Landing → Docs/Whitepaper → Team/About → DApp → Tokenomics → Footer

  Extract from each page:
    - Official claims → append to claims[] ("audited by X", "100M supply",
      "decentralized", "LP locked", partnerships, etc.)
    - Team names + social links → team_members[] + queue 2b
    - Contract addresses → queue 2d
    - GitHub repos → queue 2c

  DApp proactive testing (key investigation step):
    - Open DApp via agent-browser, wait for load
    - Does the UI render real data or just a mock shell?
    - Are core functions visible and interactive?
    - Check network requests: broken APIs? Suspicious external calls?
    - If DApp shows on-chain values → cross-check against 2d data
    - Screenshot as evidence

  Security check: SSL, domain age, redirects, suspicious popups.
  Fallback: blank/Cloudflare → retry with `--headed`. No website → flag as risk.

  ── 2b. Social data collection (Twitter) ─────────────────────

  Purpose: collect project claims, discover team, find community disputes.
  NOT the investigation core — feeds into 2a/2c/2d for verification.

  For project official account:
    1. /api/twitter/user + tweets + replies + deleted-tweets (parallel)
    2. Pick 1-2 high-value tweets → conversation-v2 + quotes
    3. /api/readx/following-light → identify team members from following list
       (mutual follows, bio mentions project, new account only posts about project)
       → add to team_members[], queue 2b at depth+1
    4. Risk search: search2 "{project} scam OR rug OR hack OR exploit"

  For team member accounts (depth 1+):
    1. /api/twitter/user + tweets (parallel)
    2. Only retain project-related tweets → append to claims[]
       (team member statements carry same weight as official claims)
    3. friendships-show with other known team members
       (all isolated = fake team red flag)

  ── 2c. Code analysis (GitHub) ───────────────────────────────

  github-analysis → analyzeRepository / convertToMarkdown

  Focus: claim verification + security scan
    - "Open source" → repo public? Code complete or stub?
    - "Audited" → audit report in repo? Code matches?
    - Hardcoded addresses (admin, treasury) → queue 2d + fund_trace[]
    - Suspicious patterns: obfuscation, eval(), wallet-draining code,
      backdoors, malicious dependencies, clipboard hijacking
    - Contributor identities → try resolve to Twitter → team_members[]
    - Freshness: last commit, bus factor, fork-of-fork detection

  ── 2d. On-chain analysis (investigation core) ───────────────

  Phase 1 — Token & contract basics (parallel):
    Binance: audit, token-info, wallet
    Bitget:  token-info, token-price, tx-info, liquidity, security-audit
    Cross-verify between sources.

  Phase 2 — Contract deep inspection (ETH/BSC):
    /api/explorer/contract → ABI + source code
    - Read ABI: identify owner-only functions (pause, mint, blacklist,
      upgrade, setFee, transferOwnership)
    - If proxy contract: queue implementation address (recursive 2d)
    - If source verified: scan for backdoor patterns in code
    - If NOT verified: flag as risk (cannot audit)

  Phase 3 — Fund flow tracing:
    Triggered by: fund_trace[], deployer discovery, large holder detection
    /api/explorer/token-history → trace address transaction history

    Tracing logic (recursive within depth limit):
      1. Fetch token-history for the address
      2. Identify significant transfers:
         - Large outflows to unknown wallets → trace recipient
         - Inflows from deployer → insider?
         - Flows to/from known exchanges → cash-out pattern?
         - Circular flows (A→B→C→A) → wash trading?
      3. For each significant counterparty:
         - New address → add to fund_trace[] at depth+1
         - Known exchange → note cash-out
         - Mixer/bridge → flag as risk signal
      4. Stop when: depth limit / no significant new flows

    SOL specific:
    - /api/explorer/sol-address → balance snapshot + SPL tokens
    - /api/explorer/token-history (SOL) → filter by type/source
      SWAP on Jupiter/Raydium = trading; TRANSFER = fund movement

  │
  ▼
Step 3 — Verify claims & resolve contradictions
  Goal: every official claim gets a verdict. Contradictions are the story.
  If verification needs data not yet collected → callback to Step 2.

  Process claims[] collected during Step 2:

    | Claim | Verify with | How |
    |-------|-------------|-----|
    | "Decentralized" | Explorer ABI + on-chain | pause/mint/blacklist? EOA or multisig? |
    | "Audited by X" | Website + GitHub + firm | Link valid? Code matches audited version? |
    | "Max supply N" | Explorer source code | Uncapped mint()? Owner can mint? |
    | "Locked liquidity" | On-chain LP lock | Lock verified? Duration? Amount? |
    | "Open source" | GitHub + Explorer | Public? Verified? ABI matches? |
    | "Partnerships" | Partner channels (browser) | Partner acknowledges? One-sided? |

    Priority: verify claims affecting user funds first.
    Mark each: ✅ Verified / ⚠️ Unverified / ❌ Contradicted

  For each ❌ or anomaly → dispute analysis:
    1. Project claim vs actual data (on-chain, code) → cite both
    2. Community analysis → search2 + conversation threads
    3. On-chain evidence → tx hashes, fund flow from fund_trace[]
    4. Synthesize: claim → reality → community → verdict
       🔴 → full analysis / 🟡 → summary only
  │
  ▼
Step 4 — Hypothesis-driven deep dig
  Follow high-value leads from Steps 2-3. May callback to any module.

  Key hypotheses:
    - Contract upgradable → who holds proxy admin?
    - Large holder → tokens from deployer? Insider?
    - Deleted tweets → timing vs on-chain events?
    - Deployer has other contracts → same pattern? Previous rugs?

  Team verification:
    - Identity: Twitter vs website claims vs GitHub commits
    - History: search2 "{name} founder OR CEO", wallet history
    - Red flags: account age = project age? No pre-project history?

  Any new lead → callback to Step 2 (respecting MAX_DEPTH).
  Stop when: no new leads or sufficient for judgment.

  ─── END OF DATA COLLECTION ───
  │
  ▼
Step 5 — Distill (no fetching)
  Rank by impact. Discard noise. Connect dots. Reconstruct timeline.
  │
  ▼
Step 6 — Produce report (see REPORT_TEMPLATE.md)
  Curated intelligence, NOT a data dump. Focus on:
    1. Contradictions & anomalies
    2. Claim verification results
    3. Fund flow analysis
    4. Proactive test results (DApp, website)
    5. Security findings
  Omit routine confirmations. [[N]](url) citations required.
  Language follows user input; default zh-CN.
```

### Cross-module Callback Summary

Each module feeds discoveries into other modules:

```
  ┌──────────┐     handles, claims      ┌──────────┐
  │  Website  │ ──────────────────────→  │  Twitter  │
  │   (2a)    │ ◀────────────────────── │   (2b)    │
  └─────┬─────┘   URLs from tweets      └─────┬─────┘
        │ contracts, repos                     │ addresses, accusations
        ▼                                      ▼
  ┌──────────┐     hardcoded addrs      ┌──────────┐
  │  GitHub   │ ──────────────────────→  │ On-chain  │
  │   (2c)    │ ◀── code vs claims ──── │   (2d)    │
  └──────────┘                          └─────┬─────┘
                                               │ recursive
                                               ▼
                                          (2d again)
```

| Source | Discovers | Triggers |
|--------|-----------|----------|
| Website | Twitter handles, claims, contracts, repos | → team_members[]/claims[]/2b/2c/2d |
| Twitter | URLs, addresses, accusations, team members, statements | → 2a/2d/fund_trace[]/claims[]/team_members[] |
| GitHub | Contributors, hardcoded addrs, code contradictions, trojans | → team_members[]/2d/fund_trace[]/claims[] |
| On-chain | Proxy impl, deployer contracts, large holders, data contradictions | → 2d recursive/fund_trace[]/claims[] |

**Depth control:** 0 = user input → 1 = discovered → 2 = max, high-value only → beyond: note only

## Failure Handling

| Failure type | Action |
|-------------|--------|
| Timeout / 502-504 | Retry once after 3s |
| 429 (rate limit) | Retry once after `Retry-After` or 10s |
| 401 / 403 / 400 | Do not retry; skip |
| Other errors | Do not retry; skip |

On failure: skip source, continue. Include **Data Coverage** note in report.
Omit sections with no data; never halt for a single failure.

## Entity Extraction Rules

| Entity Type | Identification |
|----------|---------|
| Twitter profile | `x.com/{username}` or `twitter.com/{username}` |
| Twitter post | `x.com/{username}/status/{id}` |
| GitHub repo | `github.com/{owner}/{repo}` |
| EVM contract | `0x` + 40 hex chars |
| Solana address | base58 32–44 chars + contextual keywords (below) |
| Ticker | `$XXX` or `ticker/symbol/token: XXX` |
| Chain | URL domain / path keywords / page text |

**Solana keywords** (at least one must be present):
`solana`, `sol`, `raydium`, `jupiter`, `orca`, `meteora`, `pump.fun`,
`moonshot`, `birdeye`, `solscan`, `solana.fm`, `spl token`, `program id`
No keyword → flag as "unresolved address".

## Aggregator URL Parsing

| Platform | Path | Parsed result |
|------|---------|---------|
| clawhub.ai | `/owner/repo` | → GitHub repo (use `github-analysis`, skip browser) |
| dexscreener.com | `/chain/address` | → contract + chain |
| dextools.io | `/app/chain/pair/address` | → contract + chain |
| pump.fun | `/address` | → Solana contract |
| gmgn.ai | `/chain/address` | → contract + chain |
| birdeye.so | `/token/address` | → contract |
| defined.fi | `/chain/address` | → contract + chain |

## Data Display Rules

- Skip any metric that returned an error or timed out — leave it out entirely.
- Do not display API latency unless it was actually measured successfully.

## Local Memory & Report Storage

1. Save report as PDF to `~/.crab-catch/reports/{project_name}_{YYYY-MM-DD}.pdf`
2. Maintain index `~/.crab-catch/reports/index.json`:
   `{ "project": "name", "date": "YYYY-MM-DD", "file": "filename.pdf", "entry": "original input" }`

## Report Output

Use `REPORT_TEMPLATE.md` as the report structure.

### Report philosophy: curated intelligence, not data dump

The report should be **concise and decision-oriented**. The reader wants to know:
is this project trustworthy? What are the risks? Where do the claims fall apart?

**Five pillars of the report** (in order of importance):

1. **Contradictions & anomalies** — where different sources tell different stories.
   This is the most valuable content. Twitter says X, website says Y, on-chain shows Z.
2. **Claim verification** — systematic test of every official statement.
   What the project claims vs what the code/chain actually shows.
3. **Fund flow analysis** — where the money goes.
   Deployer → holders → exchanges. Insider patterns, circular flows, cash-outs.
4. **Proactive testing** — DApp functionality, website integrity, code security.
   Does the product work? Is the website legit? Are there backdoors in the code?
5. **Security findings** — contract risks, code trojans, permission hazards.
   ABI dangerous functions, proxy patterns, obfuscated code.

**What to omit:** routine data that confirms nothing special. If a metric is normal,
don't list it. If a claim checks out cleanly, a single ✅ row is enough — no paragraph.
Only expand on findings that change the reader's decision.

### Section constraints

**Must keep** — always present, fixed order:
- Header (project name + timestamp)
- 📌 Basic Information (flexible rows — agent adds/removes based on data, no fixed schema)
- 🧠 Core Findings (with Executive Summary)
- 📝 Conclusion & Verdict
- 📂 References

**Default keep** — user can request to skip:
- 🛡️ Verification & Cross-Reference (Claim / Contradictions / Disputes / Gaps)
- ⚠️ Risk Warning

**Data-dependent** — skip if no data:
- 📊 Deep Dive
  - 👤 Team & Key Figures
  - 💻 GitHub Analysis
  - ⛓️ On-chain Security
  - 📈 Social Signals
  - 📅 Project Timeline

### Formatting rules

**Citation system (mandatory, like academic papers):**
- Every factual claim MUST have `[[N]](url)` citation
- No source = mark as ⚠️ Unverified, NOT stated as fact
- Sequential numbering, first appearance order
- Bidirectional: every `[[N]]` ↔ References entry

**Other:**
- Numbers: K / M / B; prices: `$` prefix
- Highlight high-risk signals (honeypot, high tax, upgradable contracts)
- **Data Coverage** note when sources unavailable
- DYOR disclaimer
- **Output language matches user input; default zh-CN**
