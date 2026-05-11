# Crypto/Web3 Founder Guide

Specific considerations for crypto founders, with focus on Solana ecosystem (November 2025).

## Market Context (November 2025)

### Crypto Adoption (a16z State of Crypto 2025)

**Market Size** ([a16z State of Crypto 2025](https://a16zcrypto.com/posts/article/state-of-crypto-report-2025/))
- **Total market cap**: Crossed $4 trillion (first time)
- **Crypto owners globally**: 716 million (+16% YoY)
- **Active onchain users**: 40-70 million
- **Mobile wallet users**: All-time highs (+20% YoY)
- **Only 5.6-9.8% of owners** actively transact onchain—massive builder opportunity

**Infrastructure Readiness**
- **3,400+ TPS** aggregate across major networks (100x growth in 5 years)
- **L2 fees dropped**: ~$24 (2021) → <$0.01 (2025)
- **Blockspace**: Now "cheap and abundant" per a16z

### Current Conditions

**Market State**
- Correction phase: BTC from $111K peak to sub-$100K
- "Extreme Fear" on sentiment indicators
- $340B market cap wipeout
- $19B in liquidations

**The Opportunity**
- Historic precedent: Extreme fear precedes major recoveries
- Companies building through volatility dominate next cycle
- Hiring strategy should be tied to execution milestones, not prices
- Your strategy should not change based on daily price action

### Funding Reality

**Q1-Q3 2025: $22.8B Total** (Sources: [Galaxy Digital Q3 2025](https://www.galaxy.com/insights/research/crypto-blockchain-venture-capital-q3), [CryptoRank Q3 2025](https://cryptorank.io/insights/reports/crypto-fundraising-report-Q3-25))
- **Q1 2025:** $4.8B (incl. $2B Binance/MGX—largest crypto VC deal ever)
- **Q2 2025:** $10B+—first quarter exceeding $10B in 3 years
- **Q3 2025:** $4.65B across 415 deals (7 deals = 50% of capital)
- **Median deal size:** $4.5M (all-time high) ([Galaxy Q3 2025](https://www.galaxy.com/insights/research/crypto-blockchain-venture-capital-q3))
- **US dominance:** 40-47% of all deals and capital
- **IPOs replacing tokens:** Circle IPO (5x return), Strategy $2.47B IPO, Bullish $1.11B IPO
- **GENIUS Act passed (Jul 2025)**—first federal stablecoin framework
- **Seed→Series A graduation:** Only 17% of seed-funded crypto companies reach Series A ([funding.decentralised.co](https://funding.decentralised.co/))

**Priority Sectors by VC Evidence** (Sources: [Galaxy Digital](https://www.galaxy.com/insights/research/crypto-blockchain-venture-capital-q3), [a16z State of Crypto 2025](https://a16zcrypto.com/posts/article/state-of-crypto-report-2025/), [CryptoRank](https://cryptorank.io/insights/reports/crypto-fundraising-report-Q3-25))
| Sector | Signal |
|--------|--------|
| Stablecoins/Payments | $46T transaction volume (106% YoY); $300B+ supply; #17 US Treasury holder – a16z |
| CeFi + Infrastructure | >60% of Q3 2025 funding; IPO exits proving business models – CryptoRank |
| DeFi (Solana-focused) | ~20% of spot trading on DEXs; Hyperliquid $1B+ annualized revenue – a16z |
| Crypto-AI Integration | $30T agent economy by 2030 (Gartner via a16z); top thesis for Pantera |
| DePIN | $3.5T projected by 2028 (WEF); Helium 1.4M daily users, 111K hotspots |
| RWAs/Tokenization | $30B tokenized on-chain; 4x growth in 2 years – a16z |

**What's Declining**: Security tooling, generic interoperability, NFT speculation, enterprise blockchain.

**What VCs Want**
- Revenue-generating models over speculation
- Regulatory compliance as competitive advantage
- Sustainable unit economics
- Infrastructure plays > consumer apps

**Rob Hadick** (Dragonfly): "Don't see funding levels reaching 2021-2022 highs for a very long time." Established companies (founded ~2018) getting majority of capital; newer companies get deal count but smaller checks.

### Global Developer Landscape (Electric Capital 2024)

**Geographic Shift** ([Electric Capital Developer Report 2024](https://developerreport.com/developer-report))
- **Asia overtook North America** as #1 region for crypto developers (32% vs 24%)
- **India**: Rose from 10th to 2nd globally, contributing 17% of new developers
- **US share dropped**: From 38% (2015) to 19% (2024)—81% of crypto devs now outside US
- **34% of developers** now work on multiple chains (up from <10% in 2015)

**Developer Quality vs. Quantity**
- Total monthly active devs: 23,613 (-7% YoY)
- BUT established developers (2+ years): **+27% YoY** (all-time high)
- 70% of all code commits from 2+ year developers
- 80% of developer losses from part-time/one-time contributors

**Ecosystem Rankings**
| Ecosystem | Monthly Active Devs | New Devs (2024) | YoY Growth |
|-----------|---------------------|-----------------|------------|
| Ethereum (+ L2s) | 31,869 | 16,181 | - |
| Solana | 17,708 | 7,625 | +83% |
| Bitcoin | ~1,200 | 7,400+ | Stable |

## Solana Ecosystem

### Network Performance (Q3 2025)

Source: [Messari State of Solana Q3 2025](https://messari.io/report/state-of-solana-q3-2025)

- **Avg Daily Non-Vote Txs**: 95.9M — real user activity (excludes validator votes)
- **Avg Daily Fee Payers**: 2.8M unique addresses
- **Avg Tx Fee**: $0.012 (0.000061 SOL)
- **Median Tx Fee**: $0.0012 (0.000006 SOL) — local fee markets keep costs low even during spikes
- **Active Validators**: 963 across 38 countries, 208 data centers
- **Nakamoto Coefficient**: 20 — above median of other networks
- **Uptime**: 16+ months continuous (longest since launch)
- **Peak TPS**: Briefly hit 100,000 TPS under stress test

### Economic Strength (Q3 2025)

Source: [Messari State of Solana Q3 2025](https://messari.io/report/state-of-solana-q3-2025)

- **DeFi TVL**: $11.5B (+32.7% QoQ) — #2 among all networks after surpassing TRON
- **Stablecoin Market Cap**: $14.1B (+36.5% QoQ, ATH) — USDC $10B (71%), USDT $2.4B (17%)
- **Chain GDP (App Revenue)**: $584.3M — PumpFun $118M, Jupiter $93M, Axiom $85M
- **App Revenue Capture Ratio**: 262.8% — apps earn $2.63 for every $1 in tx fees
- **Q3 REV**: $222.3M — highest of all blockchains (base fees + priority fees + MEV tips)
- **Avg Daily DEX Volume**: $4B spot (+17% QoQ), $1.6B perps (+93% QoQ)
- **RWA Value**: $682.2M (+41.9% QoQ) — USDY, BUIDL, ONyc leading
- **Developer Growth**: #1 for new developers globally with 7,625 new devs in 2024 (+83% YoY); 17,708 active total ([Electric Capital 2024](https://developerreport.com/developer-report))
- **Only country where Solana is #1**: India (27% of new Indian devs chose Solana)

### Institutional Adoption

Source: [Messari State of Solana Q3 2025](https://messari.io/report/state-of-solana-q3-2025)

- **Rex Osprey Solana Staking ETF (SSK)**: First US staking crypto ETF, launched July 2, 2025 — $330.2M flows since inception
- **9 additional SOL ETF filings** pending approval (VanEck, Invesco, Galaxy, others)
- **Digital Asset Treasury Companies (DATs)**: 20 companies hold 18.9M SOL ($3.9B)
  - Forward Industries: 6.8M SOL (largest) — $1.65B raise led by Galaxy, Jump, Multicoin
  - Solana Company: 2.2M SOL (backed by Pantera, Summer Capital)
- **Total Staked**: 409.6M SOL ($85.5B) — 67.1% of circulating supply

### Why Solana Wins for Payments/Infrastructure

- Sub-200ms payments match x402 speed requirements
- Sub-penny fees enable true micropayments
- Proven scale (162M+ daily transactions)
- Existing payment infrastructure (USDC, Jupiter, Drift)
- Institutional validation (Franklin Templeton, BlackRock, Pantera)

## Grants & Funding Sources

### Solana Foundation Grants

**Program Overview**
- Total deployed: $100M+ across 500+ projects
- Grant types: Milestone-based, convertible, RFPs

**How to Apply**
1. Fill application at Solana Foundation portal
2. Project overview + public good justification
3. Structured budget + milestones
4. ~1 week review process

**Recent RFPs**
- $400K for Solana Actions/Blinks open-source dev
- $275K for open-source data tooling
- Solana Mobile Builder Grants

### Superteam Grants

**Fast Track for Emerging Markets**
- Funding: $200 - $10,000 (equity-free)
- Application: <15 minutes
- Decision: 48 hours
- Contact: grants@superteam.fun

**What Gets Funded**
- Public goods for Solana community
- Decentralization/censorship resistance tools
- Technical contributions + dApps
- Content creation/community initiatives

**What Doesn't Get Funded**
- Projects unrelated to Solana
- Purely commercial without community benefit
- No clear implementation plan

### Colosseum Accelerator

**Program Details**
- Investment: $250K pre-seed per team
- Acceptance rate: ~0.68% (highly competitive)
- Major hackathons: Renaissance, Radar, Breakout (2x/year)
- Eternal Challenge: Perpetual 4-week sprints (submit anytime)
- Eternal Award: $25K USDC semi-annually

**What They Look For**
- Technical excellence
- Clear problem/solution fit
- Strong team execution
- Ecosystem integration potential

### Other Funding Sources

**Ecosystem VCs**
- RockawayX: $125M Fund II (Solana focus)
- Solana Ventures: Active ecosystem support
- Multicoin Capital: Internet Capital Markets thesis
- Galaxy Digital: Deep Solana research

**Regional Programs**
- Solana x Cal Grants: Up to $10K USDC (USA)
- Superteam country chapters

## Regulatory Environment

### Project Crypto (SEC, November 2025)

**Major Shift**
- Chair Paul Atkins: Comprehensive regulatory modernization
- Token Taxonomy: Clear Howey analysis framework coming
- Multi-Function Platforms: Enabling crypto "super-apps"
- Goal: Position U.S. as global leader in digital finance

**What This Means**
- End of "regulation by enforcement"
- Clear rules for custody, trading, exchanges
- Path for crypto businesses to return to U.S.
- Compliance = competitive advantage

### Solana ETFs

**Breaking Development (June 2025)**
- SEC requested updated filings for Solana ETFs
- Approval expected within 4 months
- Will unlock institutional capital similar to BTC/ETH ETFs

### Practical Implications

- Budget for legal from day one ($25K-50K)
- Engage crypto-specialized lawyers
- Consider jurisdiction strategy
- Document compliance efforts
- Join industry groups (Blockchain Association)

## Go-to-Market for Crypto

### Building in Public vs. Stealth

**Community-First (Recommended for Most)**
- Build community BEFORE product launch
- Attract 100 "true fans" as foundation
- Authenticity >> marketing budget
- High-quality content + ecosystem participation

**When to Go Stealth**
- Highly competitive market with copycat risk
- Novel technology requiring IP protection
- Need quiet cycles to fix unit economics

**Hybrid (Popular)**
- Stealth dev + selective community building
- Share progress with early believers
- Launch to existing community

### Distribution Channels

**Developer Relations (Critical for Infrastructure)**
- Build tools that make developers successful
- Documentation >>> marketing
- Hackathons, workshops, tutorials
- DevRel = your growth engine

**X (Twitter) as Primary Channel**
- Founder-led narrative building
- Technical deep dives + progress updates
- Engage in ecosystem discussions
- Founder faces beat brand pages

**Progressive Disclosure**
- Don't announce until you have something to show
- Ship features, then market them
- Let users discover and evangelize

### Community as Product

**Core Principle**: Your community IS the product, not a marketing channel.

**Pre-Launch**
- Build small, dedicated group (100 true fans)
- Shared mission, not speculation
- Active ecosystem participation

**Launch**
- Reward true believers (not farmers)
- Design launch FOR your community
- Community becomes distribution

**Post-Launch**
- Turn users into owners
- Governance participation
- Co-creation of roadmap

## Revenue Models That Work

### DeFi Infrastructure

- **Transaction fees**: % of volume (DEXs, lending)
- **Spread/slippage**: Market making revenue
- **Staking fees**: 5-10% of staking rewards
- **MEV capture**: Via Jito or similar

### Payments Infrastructure

- **x402 Protocol**: Agent-to-agent payments
- **Payment rails**: Crypto-native settlement
- **B2B payments**: Stablecoin invoicing
- **Subscription models**: Recurring crypto payments

### Platform/Network Effects

- Marketplaces (take rate on transactions)
- Aggregators (fee per API call)
- Infrastructure-as-a-Service (RPC, indexing)
- Data/Analytics (subscription + API)

### What to Avoid

- Token-only value capture (no cash flow)
- Mercenary liquidity mining
- Ponzi-nomics (unsustainable yields)
- Grant-dependent (no path to sustainability)

**Key Principle**: Show path to real revenue within 12 months.

## Security & Audits

### Why Audits Are Non-Negotiable

**Historical Context**
- 2021: ~$2B lost to DeFi vulnerabilities
- 2022: Ronin ($600M), Euler ($197M)
- One exploit destroys project overnight

**What One Hack Costs**
- User funds (and trust) destroyed
- Project death
- Legal liability
- Blacklisted from future funding

### Audit Cost Breakdown

| Project Type | Cost Range | Timeline |
|-------------|-----------|----------|
| Simple Token | $8K - $15K | 1-2 weeks |
| DEX/AMM (Basic) | $25K - $50K | 2-4 weeks |
| Lending Protocol | $50K - $100K | 4-6 weeks |
| Complex DeFi | $100K - $150K+ | 6-8 weeks |

**Cost Factors**
- Code complexity (LOC, architecture)
- Novel mechanisms vs. battle-tested
- Firm reputation (Tier 1 = premium)
- Documentation quality
- Timeline (rush = 20-50% more)

### Top Audit Firms (Solana)

**Tier 1 ($$$)**
- Trail of Bits
- OpenZeppelin
- Halborn

**Tier 2 ($$)**
- OtterSec (Solana-native)
- Neodyme (Solana-focused)
- Sec3
- Zellic

### Cost-Saving Strategies

1. **Clean code first**: Internal review reduces scope
2. **Clear documentation**: Saves auditor time
3. **Battle-tested libraries**: Anchor, SPL standards
4. **Start small**: Audit MVP, iterate
5. **Multiple audits**: 2 smaller audits vs. 1 expensive

### Pre-Audit Checklist

- [ ] Comprehensive test suite (>80% coverage)
- [ ] Internal security review
- [ ] Clear architecture documentation
- [ ] Threat model documented
- [ ] Known issues/assumptions listed
- [ ] Testnet deployment + stress testing

**Budget Rule**: 5-10% of development budget for audits.

## Crypto-Specific Death Patterns

### Pattern 1: Building Tech Without a Problem (~30% of failures)

"Cool tech but without ever thinking if it's solving a real problem."

**Death signal**: Can't answer "Why does this need to be on-chain?" simply
**Coaching question**: "If blockchain didn't exist, how would you solve this problem?"

### Pattern 2: Token Before Product

Large premines, no economic flywheel, speculation-driven.

**Death signal**: TGE announcement before product traction metrics
**Coaching question**: "What would your product look like if you never launched a token?"

### Pattern 3: Regulatory Naïveté

No legal counsel, no token classification analysis.

**Death signal**: Launching in jurisdiction you don't understand
**Coaching question**: "Have you had a securities lawyer review your token structure?"

### Pattern 4: Ecosystem Protocol Dependency

Building on experimental chains without escape plan.

**Death signal**: Core infrastructure depends on unproven L2/protocol
**Coaching question**: "What happens if [dependency] fails or pivots? What's your exit plan?"

### Pattern 5: VC Capital Without PMF

VCs now "laser-focused on fundamentals"—funding without product-market fit is increasingly rare.

**Death signal**: Spending VC money on growth before retention metrics work
**Coaching question**: "If you couldn't raise more money, how would you get to profitability?"

### Pattern 6: The 53% Failure Rate

1.8M tokens failed in Q1 2025 alone; 52.7% of all cryptos since 2021 are "dead" ([CoinGecko Research, April 2025](https://www.coingecko.com/research/publications/how-many-cryptos-failed)).

**Death signal**: No differentiation from existing solutions
**Coaching question**: "What's different about your approach that would make you survive when half of projects fail?"

### Pattern 7: Ignoring Sybil-Proofing

zkSync, Starknet heavily criticized for airdrop farmer capture.

**Death signal**: Airdrop strategy without anti-sybil measures
**Coaching question**: "How do you ensure your token distribution rewards real users, not farmers?"

### Pattern 8: Hype > Delivery

Marketing roadmap commitments you can't ship.

**Death signal**: Public promises with no technical execution plan
**Coaching question**: "Can you ship what you've promised in the next 90 days? What's blocking you?"

*Note: The following percentages are estimates based on industry post-mortems and VC analysis, not a single comprehensive study.*

### Weak Security (~25% of failures)
- Rushed smart contracts
- Skipped audits
- Result: Hacks, drained treasuries

### Overhyped Fundraising (~20% of failures)
- Raise millions without sustainable product
- Burn > runway before PMF

### Poor Community Trust (~15% of failures)
- Broken promises
- Anonymous teams that rug
- Ignored feedback

### Ignoring Compliance (~10% of failures)
- "Move fast and break things" doesn't work
- Regulatory enforcement kills projects

### Pre-Revenue Specific

- Burning cash on marketing too early
- Wrong team composition (too much biz/ops before PMF)
- Chasing hype cycles (pivoting to whatever's hot)
- Neglecting audits

## Successful Project Patterns

### Jupiter (DEX Aggregator)
- Technical excellence first
- Best execution for traders
- Clean UX rivaling CEXs
- Built reputation before token
- Community-first governance

### Drift Protocol (Perpetuals)
- First-mover advantage
- Strong technical documentation
- Active community
- Continuous iteration

### Jito (Liquid Staking + MEV)
- Solved real problem (MEV redistribution)
- Built infrastructure others depend on
- Technical credibility first
- Open-source + transparent

### Common Patterns

1. **Technical Excellence First**: Product works reliably at scale
2. **Solve Real Problem**: "Must have" not "nice to have"
3. **Community-Driven**: Users become evangelists
4. **Transparent Operations**: Regular updates, public roadmap
5. **Ecosystem Integration**: Composability with other protocols
6. **Sustainable Economics**: Real revenue, not speculation

## Treasury Management

### The Challenge
- Token-based treasuries lose value in downturns
- Fundraising dries up in bear markets
- User acquisition costs rise

### Recommended Allocation

- **50%+ Stables (USDC)**: Operational runway
- **30% Blue Chips (SOL, BTC, ETH)**: Moderate exposure
- **20% Native Token**: If applicable

### Runway Discipline

- 24-month minimum runway at all times
- Burn rate tied to milestones, not price
- Monthly financial reviews
- Scenario planning (bull/bear cases)

### Hiring Strategy

- Hire for execution milestones, not market conditions
- Pay market rates (don't "time" with low salaries)
- Equity/tokens + stables (not just tokens)

## 18-Month Path to Seed

### Phase 1: Grants (Month 1-6)
- Apply: Solana Foundation, Superteam
- Target: $10K-50K initial capital
- Build MVP + core community (100 people)

### Phase 2: Accelerator (Month 4-9)
- Colosseum Eternal (anytime submission)
- Major hackathon participation
- Target: $250K pre-seed

### Phase 3: Launch + Traction (Month 6-12)
- Mainnet launch with audits
- Ecosystem partnerships
- First $10K revenue month
- Revenue model validation

### Phase 4: Seed Round (Month 12-18)
- Show revenue + community traction
- Target Solana-focused VCs
- Target: $1M-3M seed

### Budget Framework

**Capital Sources**
- Grants: $50K-100K
- Accelerator: $250K
- Early Revenue: $25K-100K
- Seed: $1M-3M

**Burn Rate**
- Pre-Accelerator: $15K-25K/month
- Post-Accelerator: $40K-60K/month
- Post-Seed: $100K-150K/month

**Key Milestones**
- Month 3: First grant received
- Month 6: Accelerator acceptance
- Month 9: MVP on mainnet
- Month 12: First $10K revenue month
- Month 18: Seed round closed

## Resources

### Communities
- Solana Discord
- Superteam (regional chapters)
- Colosseum Discord
- Helius Dev Community

### Tools
- RPC: Helius, Triton, QuickNode
- Analytics: Dune, Flipside
- Testing: Bankrun, Devnet

### Content & Research (Free)
- [Galaxy Digital Research](https://www.galaxy.com/insights/research/) - Quarterly VC reports, institutional grade
- [a16z State of Crypto](https://a16zcrypto.com/posts/article/state-of-crypto-report-2025/) - Annual comprehensive report
- [Electric Capital Developer Report](https://developerreport.com/developer-report) - Developer ecosystem data
- [CryptoRank Reports](https://cryptorank.io/insights/reports/) - Quarterly funding analysis
- [funding.decentralised.co](https://funding.decentralised.co/) - 15K+ funding rounds database (free)
- Helius Blog - Solana ecosystem reports
- Messari - Some free reports, enterprise paywalled

### Events
- Breakpoint (annual conference)
- Solana Hacker House (global)
- Colosseum Hackathons
