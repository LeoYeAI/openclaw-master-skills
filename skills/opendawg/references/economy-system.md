# Bot Arcade — Economy & Progression System

A comprehensive guide to the virtual economy, progression mechanics,
and behavioral psychology powering the Arcade's engagement engine.

---

## VIRTUAL CURRENCY: ARCADE COINS 🪙

### Design Philosophy
Arcade Coins are the universal currency. They are:
- **Abundant enough** to feel rewarding (players should earn steadily)
- **Scarce enough** to feel valuable (big purchases require effort)
- **Transparent** in earning and spending (no hidden mechanics)

### Inflation Control
To prevent currency inflation over time:
1. **Coin sinks** — Cosmetics, tournament entries, and premium features
   remove coins from circulation
2. **Scaling costs** — Higher-level cosmetics cost exponentially more
3. **Daily caps** — Maximum 500 coins earnable per day from free games
4. **Decay prevention** — Coins don't expire (anti-frustration measure)

### Exchange Rates (for operators enabling real-currency features)
| Platform Currency | Arcade Coins |
|------------------|-------------|
| 1 Telegram Star | 50 🪙 |
| $1 USD | 500 🪙 |
| Free daily login | 10 🪙 |

---

## XP & LEVELING SYSTEM

### XP Sources
| Action | XP Earned |
|--------|----------|
| Play any game | 10 XP |
| Win any game | 25 XP |
| Complete daily challenge | 50 XP |
| Win a tournament match | 75 XP |
| Defeat a boss | 100 XP |
| Win a tournament | 200 XP |
| Achieve a new achievement | 50 XP |
| Daily login | 5 XP |
| Help another player (gift, teach) | 15 XP |

### Level Curve
Exponential curve with soft plateaus to maintain progression feel:

```
Level  XP Required   Cumulative    Unlock
─────  ──────────   ──────────    ──────
  1        0              0       Slots, Trivia, Fortune
  2       50             50       —
  3      100            150       —
  4      175            325       —
  5      250            575       Word Wars, Riddle Rush
  6      350            925       —
  7      500          1,425       —
  8      650          2,075       —
  9      850          2,925       —
 10    1,000          3,925       Dice Royale, Scratch & Win
 11    1,200          5,125       —
 12    1,500          6,625       —
 13    1,800          8,425       —
 14    2,200         10,625       —
 15    2,500         13,125       Boss Raids
 16    3,000         16,125       —
 17    3,500         19,625       —
 18    4,000         23,625       —
 19    4,500         28,125       —
 20    5,000         33,125       Tournament Creation
 21    5,500         38,625       —
 22    6,000         44,625       —
 23    6,500         51,125       —
 24    7,000         58,125       —
 25    8,000         66,125       Prediction Arena
 30   10,000        116,125       Custom Game Creation
 40   15,000        266,125       —
 50   20,000        466,125       Legendary Status
```

### Level Display
```
Level 17 ⭐
[████████████████░░░░] 3,200 / 3,500 XP
```

### Prestige System (Level 50+)
After reaching Level 50, players can "Prestige":
- Reset to Level 1
- Keep all cosmetics and achievements
- Gain a prestige star (⭐→⭐⭐→⭐⭐⭐)
- Unlock prestige-exclusive cosmetics
- All XP earnings get a permanent 10% bonus per prestige

---

## ACHIEVEMENT SYSTEM

### Achievement Design Principles
1. **Progressive** — Most achievements have multiple tiers (Bronze/Silver/Gold)
2. **Discoverable** — Some achievements are hidden until unlocked (surprise!)
3. **Varied** — Mix of skill, luck, social, and dedication achievements
4. **Rewarding** — Every achievement gives tangible rewards (coins, XP, titles)

### Complete Achievement List

#### Games Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| G01 | First Blood | Win your first game | 25🪙 |
| G02 | Ten Down | Win 10 games | 50🪙 + badge |
| G03 | Centurion | Win 100 games | 200🪙 + title |
| G04 | Thousand Wins | Win 1,000 games | 1000🪙 + border |
| G05 | Jack of All Trades | Win at least 1 of every game type | 300🪙 + badge |
| G06 | Perfectionist | Score 100% on a 10-question trivia round | 150🪙 |
| G07 | Speed Demon | Answer trivia correctly in under 3 seconds | 75🪙 |
| G08 | Linguist | Win 50 word games | 200🪙 |
| G09 | Riddler | Solve 25 riddles without hints | 250🪙 |
| G10 | Lucky Seven | Hit 7️⃣7️⃣7️⃣ on slots | 500🪙 + title |

#### Slots Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| S01 | First Spin | Play your first slot game | 10🪙 |
| S02 | Hot Streak | Win 3 slot games in a row | 50🪙 |
| S03 | Diamond Hunter | Hit 3x💎 | 200🪙 |
| S04 | Slot Veteran | Play 500 slot games | 300🪙 |
| S05 | Against All Odds | Hit the progressive jackpot | 1000🪙 + title |

#### Social Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| X01 | Social Butterfly | Play with 10 different players | 100🪙 |
| X02 | Party Animal | Play with 25 different players | 250🪙 |
| X03 | Philanthropist | Gift 1,000 total coins | 100🪙 + badge |
| X04 | Rival | Challenge the same player 10 times | 75🪙 |
| X05 | Crowd Favorite | Be gifted coins by 5 players | 150🪙 |
| X06 | Recruiter | Refer 5 new players | 500🪙 |
| X07 | Mentor | Help 3 new players reach Level 5 | 200🪙 |

#### Streak Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| K01 | Consistent | 3-day login streak | 25🪙 |
| K02 | Dedicated | 7-day login streak | 100🪙 + badge |
| K03 | Devoted | 14-day login streak | 250🪙 |
| K04 | Obsessed | 30-day login streak | 500🪙 + title |
| K05 | Immortal | 100-day login streak | 2000🪙 + border |
| K06 | Fire Starter | 5-game win streak (any game) | 75🪙 |
| K07 | Inferno | 10-game win streak | 200🪙 |
| K08 | Supernova | 25-game win streak | 500🪙 + title |

#### Collection Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| C01 | Fortune Seeker | Collect 10 fortunes | 50🪙 |
| C02 | Rainbow Collector | Find all 5 fortune rarities | 150🪙 + badge |
| C03 | Oracle | Collect 3 Legendary fortunes | 500🪙 + title |
| C04 | Badge Collector | Unlock 10 badges | 100🪙 |
| C05 | Completionist | Unlock 25 badges | 500🪙 |
| C06 | Title Baron | Earn 5 different titles | 200🪙 |
| C07 | Fashion Icon | Own 10 cosmetic items | 150🪙 |

#### Combat Category
| ID | Achievement | Requirement | Reward |
|----|------------|-------------|--------|
| B01 | Dragon Slayer | Defeat your first boss | 100🪙 |
| B02 | Raid Leader | Lead 5 successful raids | 200🪙 |
| B03 | Boss Killer | Defeat 10 different bosses | 400🪙 + title |
| B04 | Flawless Victory | Defeat a boss without anyone dying | 300🪙 |
| B05 | Last Stand | Win a raid with only 1 HP remaining | 200🪙 |

#### Hidden Achievements (don't show until unlocked)
| ID | Achievement | Trigger | Reward |
|----|------------|---------|--------|
| H01 | Night Owl | Play between 2-5 AM local time | 50🪙 |
| H02 | Early Bird | Play between 5-7 AM local time | 50🪙 |
| H03 | Marathon | Play for 2+ hours straight | 100🪙 |
| H04 | Comeback King | Win after being down 0-2 in a best-of-5 | 150🪙 |
| H05 | The Floor Is Lava | Win 5 games without losing any | 200🪙 |
| H06 | Easter Egg | Type a secret phrase | 100🪙 |
| H07 | Generous Soul | Gift away more coins than you keep | 250🪙 |

---

## STREAK MECHANICS

### Daily Login Streaks
```
Day 1:  10🪙   ○─
Day 2:  10🪙   ─○─
Day 3:  25🪙   ──●── (milestone!)
Day 4:  25🪙   ───○─
Day 5:  25🪙   ────○─
Day 6:  25🪙   ─────○─
Day 7:  50🪙   ──────●── (milestone!)
Day 14: 100🪙  ──────────────●── (milestone!)
Day 30: 200🪙  ──────────────────────────────●── (MEGA milestone!)
```

### Streak Protection
- **Freeze Token:** Players can earn 1 freeze token per week from daily
  challenges. A freeze token preserves the streak for 1 missed day.
- **Grace Period:** If a player misses by less than 2 hours past midnight,
  extend the window (anti-frustration for timezone issues)

### Win Streaks
Track consecutive wins per game type. Display prominently in profiles
and leaderboards. Reset on a loss.

---

## DAILY CHALLENGES

### Generation Rules
Generate 3 challenges daily, balanced across:
- 1 easy challenge (completable in 1-3 games)
- 1 medium challenge (requires 5-10 games)
- 1 hard challenge (requires skill or luck)

### Challenge Templates
| Template | Example |
|---------|---------|
| Win X games of [type] | Win 3 trivia games |
| Play X rounds of any game | Play 5 rounds of any game |
| Earn X coins in one session | Earn 50 coins in one session |
| Achieve a streak of X | Get a 3-game win streak |
| Get a [rarity] fortune | Get a Rare or better fortune |
| Score X points in [game] | Score 100 points in trivia |
| Play a game with [N] people | Play a game with 3+ people |
| Win without using hints | Win a riddle without hints |

### Completion Bonus
Complete all 3 daily challenges for a mystery bonus:
- 50% chance: 50 bonus coins
- 30% chance: 100 bonus coins
- 15% chance: Random cosmetic item
- 5% chance: Rare achievement unlock

---

## LEADERBOARD SYSTEM

### Leaderboard Types
| Board | Reset | Tracked Metric |
|-------|-------|---------------|
| Daily Top Earners | Every 24h | Coins earned today |
| Weekly Champions | Every 7 days | Total wins this week |
| All-Time Legends | Never | Lifetime coins earned |
| Trivia Masters | Monthly | Trivia score |
| Slot Kings | Monthly | Biggest slot win |
| Boss Slayers | Monthly | Bosses defeated |
| Streak Warriors | Never | Longest login streak |

### Leaderboard Rewards
End-of-period rewards for top performers:

**Daily:**
- #1: 50🪙 + "Daily Champ" tag for next day
- #2-3: 25🪙

**Weekly:**
- #1: 200🪙 + exclusive badge
- #2-3: 100🪙
- #4-10: 50🪙

**Monthly:**
- #1: 1000🪙 + exclusive title + border
- #2-3: 500🪙
- #4-10: 200🪙

---

## BEHAVIORAL PSYCHOLOGY HOOKS

### Variable Ratio Reinforcement
The most addictive reward schedule. Slots and fortune drops use this:
- Players never know WHEN the next reward hits
- Each attempt could be "the one"
- Near-misses amplify the urge to try again

### Loss Aversion (Streaks)
Players fear losing their streak more than they desire the daily bonus.
This drives consistent daily engagement without feeling forced.

### Endowment Effect (Collections)
Once players have 80/100 fortunes collected, they feel compelled to
complete the set. The missing pieces feel more valuable than what they have.

### Social Proof (Leaderboards)
Seeing others win and climb motivates participation. "If they can do it,
I can too." Especially effective when friends are on the leaderboard.

### Sunk Cost (Progression)
A Level 17 player with 23 achievements won't abandon their profile.
The time invested creates loyalty to the platform.

### Peak-End Rule (Session Design)
End every session on a high note:
- Show total earnings for the session
- Preview tomorrow's daily challenge
- Tease upcoming events or unlocks
- "You're only 200 XP from Level 18!"

### IKEA Effect (Boss Raids)
Players value victories they worked hard for. Boss raids take effort,
making the reward feel more meaningful than a slot win.
