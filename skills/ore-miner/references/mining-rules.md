# ORE V2 Mining Rules & Mechanics

## How ORE V2 Works

ORE is a mineable token on Solana with a hard cap of 5 million tokens (like Bitcoin's scarcity). V2 uses a grid-based wagering model.

### Round Mechanics
- **5x5 grid** of 25 tiles per round
- **Rounds last ~1 minute**
- Miners deploy SOL on tiles they choose (1-25 tiles)
- At round end, a **random number generator picks 1 winning tile**
- SOL from the **24 losing tiles is redistributed to winners** (proportional to their stake on the winning tile)
- ~50% of the time, one participant on the winning tile earns **+1 ORE bonus**

### Fee Structure
- **10% refining fee** on claimed ORE rewards — redistributed to unclaimed holders (rewards patience)
- **10% of deposited SOL** goes to protocol treasury — auto-buys ORE on market — 90% burned, 10% to stakers

### Emission Rate
- **Base rate: 1 ORE per minute** distributed across all miners
- **Deflationary mechanism**: buyback-and-burn can make net emissions negative
- **No pre-mine, no VC allocation** — 100% mined by community

## Motherlode (ML)

The motherlode is an accumulating jackpot that makes ORE mining uniquely exciting.

### How It Works
- Every round adds **0.2 ORE** to the motherlode pool
- Motherlode triggers with a **1 in 625 chance** per round (~0.16%)
- If NOT triggered, the pool **keeps growing**
- When triggered, the **entire accumulated pool** goes to winners on that tile
- Growth rate: **0.2 ORE/min = 12 ORE/hour = 288 ORE/day**

### Size Categories
| Size | ORE Amount | Value (at ~$78/ORE) | Significance |
|------|-----------|---------------------|--------------|
| Small | < 20 | < $1,560 | Just reset. Not noteworthy. |
| Building | 20-50 | $1,560-$3,900 | Getting interesting. |
| Decent | 50-100 | $3,900-$7,800 | Starting to get attention. |
| Big | 100-200 | $7,800-$15,600 | People get excited. |
| Very Big | 200-400 | $15,600-$31,200 | Community buzzing. |
| MASSIVE | 400-700+ | $31,200-$54,600+ | Everyone watching. Huge jackpot. |

### Strategy Implications
- When ML is large (>100 ORE), more miners tend to participate, increasing competition
- Consider the ML value when calculating your EV
- A fat ML makes even marginally negative EV rounds potentially worth playing (lottery ticket value)

## Expected Value (EV)

EV tells you whether mining a round is expected to be profitable.

### Calculation Factors
- Total SOL deployed by all miners in the round
- Your deployment amount and number of tiles
- Current ORE price and bonus probability
- Motherlode value and trigger probability
- Number of competing miners on each tile

### EV Guidelines
| EV Range | Action |
|----------|--------|
| > +10% | Strong positive — deploy full amount |
| +5% to +10% | Good — deploy normal amount |
| 0% to +5% | Marginal — deploy minimum or normal |
| -5% to 0% | Slightly negative — consider reducing or skipping |
| < -5% | Negative — reduce to minimum or skip round |

### When EV Is Better
- **Red market days**: Fewer miners deploy SOL, reducing competition = higher EV
- **Late night/early morning (UTC)**: Fewer active miners
- **After big ML hits**: People tend to temporarily stop mining, reducing competition

## Tokenomics

| Token | Purpose | Notes |
|-------|---------|-------|
| **ORE** | Mined token | Hard cap 5M. Emission 1/min. Deflationary. |
| **stORE** | Staked ORE | Earns ~22% APR from refining fees |
| **SOL** | Mining currency | Deploy to mine. Also gas for transactions. |
| **SKR** | Seeker token | Also mineable on refinORE |

## Key Terms Glossary

| Term | Meaning |
|------|---------|
| ML | Motherlode — the accumulating jackpot |
| Deploy | Putting SOL on tiles to mine |
| Refining | The 10% fee mechanism on ORE claims |
| Refined ORE | ORE earned from refining fee redistribution |
| Unrefined ORE | ORE earned from mining (not yet claimed) |
| Session signer | Privy-managed key that auto-mines for you |
| Hot tile | Tile that won recently (marked with fire emoji) |
| Cold tile | Tile that hasn't won in a while (marked with snowflake) |
| EV | Expected Value — predicted profitability of a round |

## History

| Date | Event |
|------|-------|
| Apr 2024 | V1 launch — pure proof-of-work (DrillX hash), crashed Solana network |
| Oct 2024 | V2 launch — grid-based wagering model, sustainable |
| Nov 2025 | Peak price: ~$500/ORE (from ~$10 six weeks prior) |
| Jan 2026 | Current: ~$78/ORE |

- Creator: **HardhatChad** (pseudonymous)
- ~20K wallet holders
- 2,100+ refinORE users
