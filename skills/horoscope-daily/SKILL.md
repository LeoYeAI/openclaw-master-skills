---
name: horoscope-daily
clawhub-slug: horoscope-daily
clawhub-owner: eamanc-lab
homepage: https://github.com/eamanc-lab/fortune-telling-skills
description: |
  Generates personalized horoscope readings for all twelve zodiac signs based on Western astrology.
  Supports any date (today, tomorrow, a specific date) and any time period (daily/weekly/monthly),
  covering five dimensions — Overall, Love, Career, Finance, and Health — with a Lucky Guide and Daily Tip.
  Can deliver personalized readings based on the user's birthday. Pure LLM generation, no external API required.
  Trigger words: horoscope, daily horoscope, zodiac forecast, what's my horoscope today,
  weekly horoscope, monthly horoscope, star sign reading, astrology forecast, what's my sign today.
  Not intended for: Ba Zi (Four Pillars), Zi Wei Dou Shu, Tarot, Numerology, or Feng Shui —
  use fortune-hub to find the right skill for those domains.
license: MIT
compatibility:
  platforms:
    - claude-code
    - claude-ai
    - api
metadata:
  author: eamanc
  version: "2.0.0"
  tags: ["horoscope", "zodiac", "astrology", "daily horoscope", "star sign"]
---

# Daily Horoscope Generator

Draws from a rich knowledge base of zodiac sign traits to deliver personalized horoscope readings for any date and any time period.

## Quick Start

Just say your sign (or birthday) and get your reading:

```
"Aries horoscope today"
"Scorpio reading for March 25th"
"I was born June 15, 1995 — what's my horoscope today?"
"Generate today's horoscope for all 12 signs"
"Gemini weekly horoscope"
"Sagittarius horoscope for March"
```

**Full Example**:

Input: `Gemini horoscope for tomorrow`

Output:
> # ♊ Gemini Horoscope — Tomorrow (2026-03-19, Thursday)
>
> ## Overall ⭐⭐⭐⭐ (4/5)
> Mercury's lively energy sharpens your mind and quickens your wit — perfect for anything that calls for communication and coordination. An unexpected message may arrive in the afternoon; stay open to it and you might be pleasantly surprised.
>
> ## Love ⭐⭐⭐ (3/5)
> Conversation flows easily today, but things could stay a little surface-level. Try putting the phone down and having a real, unhurried talk with your partner. If you're single, a social gathering could bring a genuinely interesting connection.
>
> ## Career ⭐⭐⭐⭐⭐ (5/5)
> Thursday's forward-moving energy pairs beautifully with your natural talent for multitasking — push several projects ahead at once. In team settings, your ideas are the spark that gets everyone excited.
>
> ## Finance ⭐⭐⭐ (3/5)
> Income stays steady, but a "too good to pass up" purchase may be tempting. Add it to your cart and sit on it for a day before you commit.
>
> ## Health ⭐⭐⭐⭐ (4/5)
> Your energy is high, but watch out for eye strain. Step away from the screen for five minutes every hour. Spring's temperature swings mean you'll want to layer up in the morning and evening.
>
> ## Lucky Guide
> - 🎨 Lucky Color: Mint Green
> - 🔢 Lucky Numbers: 5, 14
> - ⏰ Lucky Hours: 2:00 PM – 4:00 PM
> - 💑 Best Match Today: Libra
>
> ## Daily Tip
> > Reach out to a friend you haven't spoken to in a while this afternoon — a light, easy conversation could spark an idea you weren't expecting.

## User Context

This Skill can deliver more personalized readings when it knows your birthday.

**Reading**: Before generating, check in this order:
1. This directory's `MEMORY.md` — use first
2. `fortune-hub/MEMORY.md` (if it exists) — fill in any missing profile fields

If data is available, use it directly without asking again.

**Writing**: If the user shares their birthday, write it to **this directory's** `MEMORY.md`:

```markdown
# User Profile

## Basic Info
- Birthday (Gregorian): YYYY-MM-DD
- Sun Sign: [Sign Name]
- Sign Period: Early / Middle / Late
```

| Field | Required | Notes |
|-------|----------|-------|
| Birthday (Gregorian) | No (sign can be specified directly) | Enables personalized readings |

**Updating**: Update `MEMORY.md` when the user asks to change their info.

## Workflow

### Step 1: Parse the User's Intent

Extract the following parameters from the user's input:

| Parameter | Parsing Rule | Default |
|-----------|-------------|---------|
| **Sign** | Stated directly, or inferred from birthday | Required (ask if unclear) |
| **Date** | "today/tomorrow/the day after" or a specific date like "March 25th" | Today |
| **Period** | Daily / Weekly / Monthly | Daily |
| **Dimension** | Is the user asking about just one area (e.g., "love life")? | All dimensions |
| **Mode** | Single sign or all 12 signs | Single sign |

**Zodiac Signs Reference Table**:

| Symbol | Sign | Date Range | Symbol | Sign | Date Range |
|--------|------|-----------|--------|------|-----------|
| ♈ | Aries | 3/21-4/19 | ♎ | Libra | 9/23-10/22 |
| ♉ | Taurus | 4/20-5/20 | ♏ | Scorpio | 10/23-11/21 |
| ♊ | Gemini | 5/21-6/20 | ♐ | Sagittarius | 11/22-12/21 |
| ♋ | Cancer | 6/21-7/22 | ♑ | Capricorn | 12/22-1/19 |
| ♌ | Leo | 7/23-8/22 | ♒ | Aquarius | 1/20-2/18 |
| ♍ | Virgo | 8/23-9/22 | ♓ | Pisces | 2/19-3/20 |

### Step 2: Load Sign Knowledge

Load **only the relevant sign's** trait file (do not load all 12):

| Sign | File Path |
|------|-----------|
| Aries | [references/signs/aries.md](references/signs/aries.md) |
| Taurus | [references/signs/taurus.md](references/signs/taurus.md) |
| Gemini | [references/signs/gemini.md](references/signs/gemini.md) |
| Cancer | [references/signs/cancer.md](references/signs/cancer.md) |
| Leo | [references/signs/leo.md](references/signs/leo.md) |
| Virgo | [references/signs/virgo.md](references/signs/virgo.md) |
| Libra | [references/signs/libra.md](references/signs/libra.md) |
| Scorpio | [references/signs/scorpio.md](references/signs/scorpio.md) |
| Sagittarius | [references/signs/sagittarius.md](references/signs/sagittarius.md) |
| Capricorn | [references/signs/capricorn.md](references/signs/capricorn.md) |
| Aquarius | [references/signs/aquarius.md](references/signs/aquarius.md) |
| Pisces | [references/signs/pisces.md](references/signs/pisces.md) |

The element and modality quick-reference table is in [references/zodiac-index.md](references/zodiac-index.md) — load it only when cross-sign comparisons or batch generation is needed.

### Step 3: Generate the Reading

Use the sign's traits combined with the date context to generate the horoscope, following the rules below.

#### Output Format (Daily)

```markdown
# {Symbol} {Sign} Daily Horoscope ({YYYY-MM-DD}, {Day of Week})

## Overall {Stars} ({N}/5)
[2-3 sentences of overall energy, weaving in the sign's core traits and the day's energy]

## Love {Stars} ({N}/5)
[1-2 sentences, offering perspective for both partnered and single readers]

## Career {Stars} ({N}/5)
[1-2 sentences, connecting to the day-of-week energy]

## Finance {Stars} ({N}/5)
[1-2 sentences, tuned to the rhythm of the month]

## Health {Stars} ({N}/5)
[1-2 sentences, grounded in the current season]

## Lucky Guide
- 🎨 Lucky Color: [specific color name]
- 🔢 Lucky Numbers: [2 numbers]
- ⏰ Lucky Hours: [HH:MM – HH:MM]
- 💑 Best Match Today: [sign name]

## Daily Tip
> [One specific, actionable piece of guidance]
```

#### Output Format (Weekly)

```markdown
# {Symbol} {Sign} Weekly Horoscope ({Start Date} – {End Date})

## This Week's Theme: [3 keywords]

## Overview
[3-4 sentences covering the week's overall arc]

## Dimension Breakdown

### Love {Stars} ({N}/5)
[2-3 sentences, with a highlight for key days this week]

### Career {Stars} ({N}/5)
[2-3 sentences, with specific action guidance]

### Finance {Stars} ({N}/5)
[2-3 sentences, with income/spending reminders]

### Health {Stars} ({N}/5)
[1-2 sentences]

## Power Days This Week
- {Day}: [special note for this day]
- {Day}: [special note for this day]

## Weekly Tip
> [One actionable suggestion for the week]
```

#### Output Format (Monthly)

```markdown
# {Symbol} {Sign} Horoscope — {Month} {YYYY}

## This Month's Theme: [3 keywords]
## Monthly Overall Rating: {Stars} ({N}/5)

## Big Picture
[4-5 sentences covering the month's arc, including early/mid/late month pacing]

## Dimension Breakdown

### Love {Stars} ({N}/5)
[3-4 sentences, noting monthly turning points]

### Career {Stars} ({N}/5)
[3-4 sentences, highlighting key windows of opportunity]

### Finance {Stars} ({N}/5)
[2-3 sentences, with money management advice]

### Health {Stars} ({N}/5)
[2-3 sentences, with seasonal reminders]

## Key Dates
- {M}/{D}: [note]
- {M}/{D}: [note]
- {M}/{D}: [note]

## Monthly Tip
> [One actionable suggestion for the month]
```

#### Generation Rules

**Content Quality**:
1. Keep scores balanced — the sum of all five dimension scores should land between 14 and 19 (average 2.8–3.8 per dimension). Avoid all-high or all-low spreads.
2. Every reading must echo the sign's core traits (Aries = drive and initiative, Taurus = groundedness, Gemini = communication, etc.).
3. Each sign's reading on the same day must be clearly distinct — no copy-paste-and-swap-the-name content.
4. Be specific and vivid — ❌ "Things look good today" ✅ "An impromptu afternoon meeting could be your moment to shine as an organizer"

**Writing Style**:

Default to the **warm mentor** voice (think Susan Miller meets Cafe Astrology):

- Lead with the cosmic weather, then bring it down to earth with a natural metaphor
- Good news first; wrap any challenging energy in constructive, forward-looking guidance
- Land each dimension with a concrete, actionable takeaway
- Sound like a knowledgeable, friendly astrologer having a conversation — not a fortune-teller issuing decrees

**Banned Phrases**:

| Don't Use | Use Instead |
|-----------|-------------|
| ❌ "You are destined to..." | ✅ "Your chart suggests a tendency toward..." |
| ❌ "Disaster / catastrophe / danger" | ✅ "This period calls for extra care in [area]" |
| ❌ "You will never..." | ✅ "This area may need more patience and a fresh approach" |
| ❌ "You must remedy this or else..." | ✅ "Here are some directions worth exploring" |
| ❌ Unconditional praise with no nuance | ✅ Mostly positive, but honestly flag challenging areas |
| ❌ "Will definitely," "fated," "will certainly happen" | ✅ "The energy points toward," "may," "your chart indicates" |

Absolutely off-limits: disease diagnosis, death references, disaster predictions, or any fear-based language.

**Astrological Depth**:

Weave the following elements naturally into readings — don't just list them mechanically:

- **Element (Fire / Earth / Air / Water)**: Sets the tone of the reading
  - Fire signs (Aries, Leo, Sagittarius): Focus on drive, passion, creative momentum
  - Earth signs (Taurus, Virgo, Capricorn): Focus on stability, pragmatism, long-term building
  - Air signs (Gemini, Libra, Aquarius): Focus on communication, social life, mental agility
  - Water signs (Cancer, Scorpio, Pisces): Focus on intuition, emotional depth, inner insight

- **Modality (Cardinal / Fixed / Mutable)**: Shapes the rhythm of the reading
  - Cardinal (Aries, Cancer, Libra, Capricorn): Emphasize initiating and launching new things
  - Fixed (Taurus, Leo, Scorpio, Aquarius): Emphasize commitment and deepening what's already in motion
  - Mutable (Gemini, Virgo, Sagittarius, Pisces): Emphasize adapting and transitioning

- **Ruling Planet Energy**: Weave in the symbolic qualities of the ruling planet (Mercury = communication, Venus = love and beauty, Mars = action, Jupiter = expansion, Saturn = responsibility, etc.)

- **Season Resonance**: When the current season aligns with the sign's element (e.g., summer and a Fire sign), note this resonance in the Health and Overall sections. When they clash (e.g., winter and a Fire sign), offer practical tips for balancing the elemental energy.

**Date-Based Differentiation**:

| Date Feature | Dimension Affected | Score Shift & Content Direction |
|-------------|-------------------|--------------------------------|
| Monday | Career | +1 lean; focus on new plans and setting the week's intentions |
| Tuesday–Thursday | Career | Baseline; focus on execution and momentum |
| Friday | Love / Social | +1 lean; focus on social plans and relationship nurturing |
| Saturday | Health | +1 lean; focus on rest, relaxation, and outdoor activity |
| Sunday | Overall | Lean toward reflection, recharging, and preparing for the week ahead |
| Early month (1st–5th) | Finance | Focus on budgeting and planning |
| Mid-month (13th–17th) | Career | Focus on mid-point check-ins and course corrections |
| Late month (25th–31st) | Finance | Focus on reviewing, wrapping up, and celebrating wins |
| Spring (Mar–May) | Health | Watch for allergies, temperature swings, and sleep schedule shifts |
| Summer (Jun–Aug) | Health | Watch for heat, hydration, diet, and exercise balance |
| Fall (Sep–Nov) | Health | Watch for dryness, respiratory health, and seasonal mood dips |
| Winter (Dec–Feb) | Health | Watch for staying warm, immunity, and indoor movement |

**Personalization Rules** (when a full birthday is provided):
- Birthday falls in the first 1/3 of the sign's date range → weave in transitional qualities from the previous sign
- Birthday falls in the final 1/3 → weave in anticipatory qualities from the next sign
- Reading date is within 3 days of the user's birthday → mention "birthday energy boost"; Overall score gets +1

### Step 4: Output and Saving

**Single sign query**: Output directly in the conversation.

**All 12 signs (batch)**:
1. Generate in order (♈ Aries → ♓ Pisces)
2. Keep each daily reading to 150–200 words
3. Save as a Markdown file in the current working directory
4. File naming — daily: `{YYYY-MM-DD}-daily-horoscope.md`
5. Weekly: `{YYYY-MM-DD}-weekly-horoscope.md`
6. Monthly: `{YYYY-MM}-monthly-horoscope.md`

## Error Handling

| Scenario | Response |
|----------|----------|
| Sign not specified | Ask: "What's your sign? Or share your birthday and I'll figure it out for you 🌟" |
| Invalid date given | Prompt: "I couldn't quite parse that date — try something like: 'tomorrow,' 'next Monday,' 'March 25th,' or '2026-03-25'" |
| Birthday on a cusp (e.g., Jan 19 or 20) | Explain both possible signs and ask the user to confirm |
| User asks about Ba Zi, Tarot, or other non-zodiac topics | Redirect: "For that, I'd suggest using fortune-hub to find the right skill — there are dedicated modules for Ba Zi and Tarot" |
| User questions whether astrology is scientific | Respond warmly: "Horoscopes are a rich cultural tradition — think of them as a fun lens for reflection. For big life decisions, I'd always recommend grounding things in rational thinking and professional advice 😊" |

## Not Intended For

Please **do not** invoke this Skill for:
- **Ba Zi / Four Pillars / Zi Wei Dou Shu / Feng Shui / Qi Men Dun Jia** → Use fortune-hub to find the right skill
- **Tarot** → Use fortune-hub to find the right skill
- **Vedic Astrology** → Use fortune-hub to find the right skill
- **Precise astronomical chart calculation** → Requires an astronomical engine like Kerykeion; this skill does not perform astronomical computation
- **Psychological counseling / medical advice** → This skill is for entertainment only and does not replace professional services

## Automated Daily Delivery (Advanced)

Pair this skill with a scheduled task to get your horoscope delivered automatically every day:

1. **Save your info**: On first use, store your sign (or birthday) in memory so future runs don't need to ask again
2. **Create a scheduled task**: Use Claude Code's cron capability to set a daily trigger (e.g., every morning at 8:00 AM)
3. **Auto-generate + deliver**: When the task fires, it reads your sign from memory → runs this skill → sends the reading via your chosen channel (Feishu, DingTalk, etc.)

**Example scheduled task setup**:

```
Every morning at 8:00 AM, read my sign from memory, generate today's horoscope, and send it to my Feishu group
```

**Prerequisites**:
- Your sign or birthday has been saved in memory
- A message delivery channel has been configured (e.g., a feishu-lark skill webhook)

> Tip: On a user's first visit, you might say — "Want me to remember your sign? I can set it up to send you a daily horoscope automatically."

## Language & Localization

Always detect and respond in the user's language.

**English:**
- Warm mentor tone, like Susan Miller meets Cafe Astrology
- Personify planets: "Mercury's active energy sharpens your thinking"
- Nature metaphors: seeds, bloom, tides, seasons
- Structure: celestial event → personal impact → actionable advice
- Hedging: "The stars suggest..." "You may find..." "This is a good time to..."

**中文:**
- 温暖导师型语气，亲切但专业
- 守护星能量融入描述："水星的活跃能量让你思维格外敏捷"
- 自然隐喻：种子、绽放、潮汐
- 结构：天象描述 → 对你的影响 → 具体建议
- 柔化措辞："星盘显示..." "你可能会..." "适合..."
- 禁用："命中注定""大凶""克夫""血光之灾"

## Atomic Design

This Skill handles one thing: **Western zodiac horoscope generation**. It does not include Ba Zi, Tarot, Numerology, Zi Wei Dou Shu, or any other fortune-telling system. For other domains, combine the relevant Skills from this repository or route through fortune-hub.

## Disclaimer

Horoscope readings are rooted in cultural and symbolic tradition and are intended for entertainment and reflection only. They do not constitute medical, legal, financial, or any other form of professional advice. For important life decisions, please rely on sound reasoning and qualified professional guidance.
