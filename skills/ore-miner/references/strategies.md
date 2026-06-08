# ORE Mining Strategies

## Overview

Each round, you decide:
1. **How much SOL** to deploy (0.001 - 1.0 per round)
2. **How many tiles** to cover (1-25)
3. **Which tiles** to pick (optimal AI, random, specific patterns)

The interplay of these three decisions defines your strategy.

## Strategy Profiles

### Optimal (Recommended Default)
- **Tiles:** AI-selected based on historical data
- **Risk:** Medium
- **Tile Selection:** `optimal`
- **How it works:** refinORE's AI analyzes recent round data and picks tiles with the best expected value. Considers hot/cold tile patterns, competition density, and historical win rates.
- **Best for:** Set-and-forget autonomous mining
- **Expected win rate:** ~52-55% over large samples

### Degen
- **Tiles:** 25 (all tiles)
- **Risk:** High
- **Tile Selection:** `random` or `optimal`
- **How it works:** Cover every single tile. You're guaranteed to be on the winning tile, but you also pay for all 25 tiles. Profit comes from having proportionally more SOL on the winning tile than competitors.
- **Best for:** Maximizing motherlode catch probability
- **Expected win rate:** 100% (you always win, but net P&L varies)
- **Warning:** High cost per round. Only profitable when you have outsized stake on winning tile or ML hits.

### Conservative
- **Tiles:** 5-10
- **Risk:** Low
- **Tile Selection:** `optimal`
- **SOL Amount:** Lower end (0.005-0.01)
- **How it works:** Cover fewer tiles to reduce cost per round. Only deploy when EV is positive. Skip rounds with negative EV.
- **Best for:** Preservation of capital, grinding small profits
- **Expected win rate:** ~20-40% (fewer tiles = lower hit rate, but lower cost)

### Skip-Last-Winner
- **Tiles:** 24
- **Risk:** Medium
- **Tile Selection:** Custom (avoid last winning tile)
- **How it works:** The tile that won the previous round is excluded. Based on the (statistical fallacy) intuition that lightning doesn't strike twice. In reality, each round is independent, but this costs slightly less than 25 tiles while covering 24.
- **Best for:** Superstitious miners who want near-full coverage at lower cost

### Hot Tiles (Momentum)
- **Tiles:** 5-15 (tiles that won recently)
- **Risk:** Medium
- **Tile Selection:** Custom (target high-frequency winners)
- **How it works:** Track which tiles have won most often in the last 100 rounds. Target those tiles, betting on momentum continuing.
- **Note:** ORE uses a random number generator — there is no actual momentum. This strategy is for entertainment, not edge.
- **Best for:** Miners who believe in streaks

### Cold Tiles (Mean Reversion)
- **Tiles:** 5-15 (tiles that haven't won recently)
- **Risk:** Medium
- **Tile Selection:** Custom (target low-frequency tiles)
- **How it works:** Target tiles that haven't won in a long time, betting they're "due." Again, each round is independent, but psychologically satisfying.
- **Note:** Same caveat as hot tiles — RNG is memoryless.
- **Best for:** Miners who believe in mean reversion

## Strategy Comparison Matrix

| Strategy | Tiles | Cost/Round | Win Rate | Variance | ML Catch | Best When |
|----------|-------|-----------|----------|----------|----------|-----------|
| Optimal | AI | Medium | ~53% | Medium | Good | Always (default) |
| Degen | 25 | Highest | 100% | Highest | Maximum | Fat ML, low competition |
| Conservative | 5-10 | Lowest | ~25% | Low | Low | Negative EV periods |
| Skip-last | 24 | High | ~96% | High | Very good | Want near-full coverage |
| Hot tiles | 5-15 | Medium | Varies | Medium | Medium | Streak patterns visible |
| Cold tiles | 5-15 | Medium | Varies | Medium | Medium | Tiles overdue |

## Dynamic Strategy Adjustments

A smart agent adjusts strategy based on conditions:

### When to Go Degen (25 tiles)
- Motherlode > 200 ORE (fat ML, worth catching)
- Very few miners in round (low competition = high EV)
- You're on a winning streak and want to ride it

### When to Go Conservative (5-10 tiles)
- EV is negative or barely positive
- SOL balance is getting low
- On a losing streak (reduce exposure)
- Many miners in round (high competition)

### When to Skip a Round
- EV < -5%
- SOL balance < 0.05 (need gas reserves)
- API errors or unusual conditions
- Just had a big win and want to lock in profit

### When to Increase Deployment
- EV > +10% (strong positive)
- Few competitors in the round
- Red market day (historically profitable)
- Just restarted after ML hit (ML is small, competition drops)

### When to Decrease Deployment
- Losing streak > 5 rounds
- Net P&L going negative
- SOL balance dropping toward minimum
- Lots of competition suddenly appeared

## SOL Amount Guidelines

| Balance | Suggested Per Round | Reasoning |
|---------|-------------------|-----------|
| < 0.1 SOL | 0.001-0.003 | Survival mode, minimize burn |
| 0.1-0.5 SOL | 0.005-0.01 | Standard small miner |
| 0.5-2 SOL | 0.01-0.05 | Standard miner |
| 2-10 SOL | 0.05-0.1 | Comfortable, can be aggressive |
| 10+ SOL | 0.1+ | Whale territory |

**Rule of thumb:** Never deploy more than 2-5% of your balance per round. This ensures you can survive long losing streaks (which will happen — variance is real).
