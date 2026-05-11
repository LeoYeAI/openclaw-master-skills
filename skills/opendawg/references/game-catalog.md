# Bot Arcade — Game Catalog & Detailed Mechanics

This reference document contains the deep game design rules, edge cases,
balancing notes, and advanced mechanics for every game in the Arcade.

---

## EMOJI SLOTS — Deep Mechanics

### Random Number Generation
Each reel is independently randomized. Use the following weighted distribution
to create satisfying near-miss rates while maintaining fair odds:

**Symbol Weights (per reel):**
| Symbol | Weight | Probability |
|--------|--------|------------|
| 🍒 Cherry | 20 | 20% |
| 🍋 Lemon | 18 | 18% |
| 🔔 Bell | 16 | 16% |
| ⭐ Star | 15 | 15% |
| 🍀 Clover | 13 | 13% |
| 💎 Diamond | 10 | 10% |
| 7️⃣ Seven | 5 | 5% |
| 🎰 Jackpot | 3 | 3% |

**Expected Outcomes:**
- Three of a kind (any): ~2.8% per spin
- Three 💎: ~0.1% (1 in 1000)
- Three 7️⃣: ~0.0125% (1 in 8000)
- Two matching: ~28% per spin
- No match: ~69% per spin

**House Edge:** Designed for ~30% return on virtual currency — generous
enough to feel rewarding, tight enough to drive engagement.

### Special Events
- **Lucky Hour:** Random 1-hour windows where all payouts double
- **Theme Reel Events:** Holiday-themed reels (Halloween, Christmas, etc.)
- **Progressive Jackpot:** 1% of every spin's cost goes to a shared jackpot
  pool. Jackpot triggers on 🎰🎰🎰 (0.0027% chance)

### Anti-Frustration Design
- After 10 consecutive losses, guarantee a 2-match on next spin
- Show "biggest win today" to set aspirational anchors
- Celebrate even small wins with energy to maintain positive association

---

## TRIVIA BLITZ — Question Generation

### Quality Guidelines
When generating trivia questions:
1. **Verify accuracy** — Only ask questions with definitively correct answers
2. **Avoid ambiguity** — Each question should have exactly ONE correct answer
3. **Balanced distractors** — Wrong answers should be plausible but clearly wrong
4. **No trick questions** — Questions should test knowledge, not reading comprehension
5. **Cultural sensitivity** — Avoid region-specific knowledge unless category is geography
6. **Timeliness** — For pop culture, keep references within last 10 years

### Difficulty Calibration
**Easy questions** should be answerable by most adults:
- "What planet is known as the Red Planet?" (Mars)
- "How many sides does a hexagon have?" (6)

**Medium questions** require specific knowledge:
- "What year did the Berlin Wall fall?" (1989)
- "What is the chemical symbol for tungsten?" (W)

**Hard questions** are expert-level:
- "What is the only country whose flag is not rectangular?" (Nepal)
- "In what year was the first email sent?" (1971)

### Group Trivia Variants
- **Speed Round:** Questions appear for only 10 seconds
- **Wager Round:** Players bet coins before seeing the question
- **All-In:** One question, everyone answers, highest wager wins
- **Category Auction:** Players bid to choose the next category
- **Sudden Death:** One wrong answer and you're eliminated

### Anti-Cheat Measures
- Vary question phrasing to prevent copy-paste searching
- Use time-pressure (fastest correct answer wins in group mode)
- Rotate between question styles (multiple choice, fill-in, true/false)

---

## WORD WARS — Advanced Modes

### Scramble Difficulty Scaling
| Difficulty | Word Length | Hints | Time | Points |
|-----------|------------|-------|------|--------|
| Easy | 4-5 letters | 2 | 60s | 10 |
| Medium | 6-7 letters | 1 | 45s | 25 |
| Hard | 8-9 letters | 1 | 30s | 50 |
| Expert | 10+ letters | 0 | 20s | 100 |

### Word Chain Rules
1. New word must start with the last letter of previous word
2. Minimum 3 letters per word
3. No proper nouns (unless category is "Places")
4. No repeating words within a game
5. 10-second time limit per turn
6. Category variants: Animals, Foods, Countries, Movies, anything

### Hangman Word Selection
Choose words that are:
- Common enough to be guessable
- Long enough to be challenging (6+ letters)
- Not obscure jargon
- Thematically appropriate for the audience

### Rhyme Battle Scoring
| Achievement | Points |
|------------|--------|
| Valid rhyme | 10 |
| Perfect rhyme | 15 |
| Multi-syllable rhyme | 25 |
| Rhyme + clever meaning | 30 |
| Stumped (no answer in 15s) | Elimination |

### Definition Bluff
1. Present a genuinely obscure English word
2. Each player writes a fake definition
3. Mix in the real definition
4. Players vote on which they think is real
5. Score: 10 pts for guessing correctly, 15 pts for each player fooled by your fake

---

## RIDDLE RUSH — Riddle Design

### Riddle Categories
- **Classic:** Traditional "What am I?" riddles
- **Lateral:** Situation-based puzzles requiring creative thinking
- **Math:** Number puzzles and logic problems
- **Visual:** ASCII art or emoji-based puzzles
- **Meta:** Riddles about words, language, or the chat itself

### Difficulty Progression
Start with Level 1 (easy) and progress. Each correct answer advances the
level. Each wrong answer drops back 1 level (minimum 1).

| Level | Style | Example Complexity |
|-------|-------|-------------------|
| 1-3 | Classic, single-layer | "I have hands but cannot clap" |
| 4-6 | Multi-layer, abstract | Multiple concepts interwoven |
| 7-9 | Lateral thinking | Requires creative reasoning |
| 10+ | Expert, multi-step | Chain of deductions needed |

### Hint System
- **Hint 1** (after 20s): A categorical clue ("Think about maps...")
- **Hint 2** (after 40s): A structural clue ("It starts with M...")
- **Emergency hint** (after 55s): Very strong clue, minimal points awarded

---

## DICE ROYALE — Detailed Rules

### Yahtzee Rush Scoring
| Combination | Description | Points |
|------------|-------------|--------|
| Ones through Sixes | Sum of specified die | Varies |
| Three of a Kind | 3 same faces | Sum of all dice |
| Four of a Kind | 4 same faces | Sum of all dice |
| Full House | 3+2 of a kind | 25 |
| Small Straight | 4 sequential | 30 |
| Large Straight | 5 sequential | 40 |
| Yahtzee | 5 of a kind | 50 |
| Chance | Any combination | Sum of all dice |

**Rush variant:** Players have only 3 minutes to fill their entire scorecard.
Speed + strategy under pressure.

### Liar's Dice Protocol
1. All players "roll" their dice secretly (AI tracks privately)
2. Starting player makes a bid: "I bet there are at least [N] [face]s total"
3. Next player must either raise the bid or call "Liar!"
4. If called: reveal all dice
   - Caller is right (bid was too high): Bidder loses a die
   - Caller is wrong (bid was accurate or low): Caller loses a die
5. Last player with dice wins

### Craps Flow
```
Come-Out Roll:
  7 or 11 → WIN (Natural)
  2, 3, 12 → LOSE (Craps)
  4,5,6,8,9,10 → This becomes "the Point"

Point Phase:
  Roll the Point again → WIN
  Roll 7 → LOSE (Seven-out)
  Anything else → Roll again
```

---

## BOSS RAIDS — Encounter Design

### Boss Generation Template
Each boss has:
- **Name:** Dramatic, memorable title
- **HP:** Scales with party size (300 per player)
- **ATK/DEF/SPD:** 3 core stats, one is always a weakness
- **Element:** Fire/Ice/Lightning/Shadow/Light
- **3 Phases:** Each phase triggers at HP thresholds (66%, 33%)
- **Special Attacks:** 2-3 unique attacks per phase
- **Loot Table:** Rewards based on contribution and performance

### Player Roles
| Role | Action | Effect |
|------|--------|--------|
| Attacker (⚔️) | Attack | 2d6 + ATK modifier damage |
| Defender (🛡️) | Defend | Reduce incoming damage by 50% for party |
| Mage (🔮) | Magic | 3d6 damage if element matches weakness, else 1d6 |
| Healer (🧪) | Heal | Restore 2d6 HP to lowest-HP party member |

### Combat Resolution
1. Players choose actions simultaneously
2. Dice rolls determine outcomes
3. Boss acts based on phase AI (predictable patterns players can learn)
4. AI narrates the round with dramatic flair
5. Repeat until boss defeated or party wiped

### Boss AI Patterns
**Phase 1 (100-66% HP):** Single target attacks, medium damage
**Phase 2 (66-33% HP):** AoE attacks, buffs self, damage increases
**Phase 3 (33-0% HP):** Enraged — heavy damage, random targets, special moves

### Example Bosses
| Boss | Element | Weakness | Signature Move |
|------|---------|----------|---------------|
| Crystal Serpent | Ice | Fire | Frozen Coil (AoE freeze) |
| Shadow Drake | Shadow | Light | Void Breath (pierces defense) |
| Storm Titan | Lightning | Ice | Thunder Slam (stuns 1 player) |
| Ember Golem | Fire | Ice | Lava Wave (floor damage) |
| Mind Weaver | Light | Shadow | Confusion (swaps 2 players' roles) |

---

## TOURNAMENT MODE — Bracket Design

### Match Resolution
Each tournament match is a best-of-3 in the chosen game type.
If a player doesn't respond within 5 minutes, they forfeit.

### Seeding
Players are seeded by their all-time score in the relevant game.
If no history exists, they are randomly seeded.

### Prize Distribution
| Place | % of Pool |
|-------|----------|
| 1st | 50% |
| 2nd | 25% |
| 3rd-4th | 12.5% each |

### Double Elimination Variant
For 8+ player tournaments, offer double elimination:
- Losers drop to the losers' bracket
- Must lose twice to be eliminated
- Losers' bracket winner faces winners' bracket winner in Grand Finals
- Grand Finals: Winners' bracket player needs to lose once; Losers' bracket
  player needs to win twice

---

## PREDICTION ARENA — Resolution Rules

### Creating Predictions
- Creator defines the question, options (2-4 choices), and resolution time
- Minimum resolution time: 1 hour
- Maximum resolution time: 7 days
- Creator cannot bet on their own prediction (conflict of interest)

### Payout Calculation
Simple pari-mutuel system:
1. Total pool = sum of all wagers
2. Winning pool = sum of wagers on winning outcome
3. Each winner receives: (their wager / winning pool) * total pool
4. House takes 0% cut (to maximize engagement; operator can enable a cut)

### Dispute Resolution
- Creator resolves the prediction with evidence
- If disputed, majority vote among non-betting participants
- Unresolved after 24 hours: all bets refunded
