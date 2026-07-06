---
name: compass-ai-bazi
description: Chinese Bazi (八字) four-pillar fortune calculation and basic interpretation — enables AI agents to compute and read a birth chart using traditional Zi-Ping methodology.
---

# Compass AI — Bazi (八字) Calculation & Lite Interpretation

This skill gives you the complete reference data and step-by-step algorithms needed to **calculate a Chinese Bazi (Four Pillars of Destiny) chart** from a person's birth date, time, and location, and to produce a basic personality and fortune interpretation.

> **⚠️ NO EXTERNAL TOOLS OR LIBRARIES NEEDED.** Every calculation in this skill — year pillar, month pillar, day pillar, hour pillar, Ten Gods, Five Elements, Major Fortune Cycles — is performed by **you, the AI**, using only arithmetic and the lookup tables below. Do NOT attempt to call any tool, install any library, or search the web. Just reason through the steps.

> For full AI-powered streaming analysis, life K-line charts, two-person compatibility, daily fortune sticks, and interactive fortune-telling chat, visit **[Compass AI](https://fortune.zodi.zone/web/)**.

---

## When to Use This Skill

Use this skill when the user:
- Provides a birth date, birth time, and birth city/location and asks for a Bazi (八字) reading
- Asks about their Four Pillars, Day Master, Five Elements balance, Ten Gods, or Major Fortune cycles
- Wants to know their favorable/unfavorable elements (喜用神/忌神)
- Asks about personality traits or career tendencies based on Chinese astrology

**Important UX rules:**
- Only ask the user for: birth date (年月日), birth time (时辰), gender, and birth city name. **Never ask for longitude/latitude** — look it up from the City Coordinates table below.
- If the city is not in the table, estimate from the nearest listed city or provincial capital.
- Collect all info in as few turns as possible. Ideally one message: "请告诉我您的出生年月日、时辰、性别和出生城市".

---

## Core Concepts (Quick Reference)

### Heavenly Stems (天干) and Their Five Elements

| Stem | Pinyin | Element | Polarity |
|------|--------|---------|----------|
| 甲   | jiǎ    | 木 Wood | Yang     |
| 乙   | yǐ     | 木 Wood | Yin      |
| 丙   | bǐng   | 火 Fire | Yang     |
| 丁   | dīng   | 火 Fire | Yin      |
| 戊   | wù     | 土 Earth| Yang     |
| 己   | jǐ     | 土 Earth| Yin      |
| 庚   | gēng   | 金 Metal| Yang     |
| 辛   | xīn    | 金 Metal| Yin      |
| 壬   | rén    | 水 Water| Yang     |
| 癸   | guǐ    | 水 Water| Yin      |

### Earthly Branches (地支) and Their Five Elements

| Branch | Pinyin | Element | Zodiac   |
|--------|--------|---------|----------|
| 子     | zǐ     | 水 Water| Rat      |
| 丑     | chǒu   | 土 Earth| Ox       |
| 寅     | yín    | 木 Wood | Tiger    |
| 卯     | mǎo    | 木 Wood | Rabbit   |
| 辰     | chén   | 土 Earth| Dragon   |
| 巳     | sì     | 火 Fire | Snake    |
| 午     | wǔ     | 火 Fire | Horse    |
| 未     | wèi    | 土 Earth| Goat     |
| 申     | shēn   | 金 Metal| Monkey   |
| 酉     | yǒu    | 金 Metal| Rooster  |
| 戌     | xū     | 土 Earth| Dog      |
| 亥     | hài    | 水 Water| Pig      |

### Five Elements Generating & Controlling Cycles (五行生克)

**Generating (相生):** Wood → Fire → Earth → Metal → Water → Wood

**Controlling (相克):** Wood → Earth → Water → Fire → Metal → Wood

### Hidden Stems in Earthly Branches (地支藏干)

Each Earthly Branch contains one or more hidden Heavenly Stems with relative strength weights (main qi / middle qi / residual qi):

| Branch | Main Qi (本气) | Middle Qi (中气) | Residual Qi (余气) |
|--------|---------------|-----------------|-------------------|
| 子     | 癸 (100%)     | —               | —                 |
| 丑     | 己 (60%)      | 癸 (30%)        | 辛 (10%)          |
| 寅     | 甲 (60%)      | 丙 (30%)        | 戊 (10%)          |
| 卯     | 乙 (100%)     | —               | —                 |
| 辰     | 戊 (60%)      | 乙 (30%)        | 癸 (10%)          |
| 巳     | 丙 (60%)      | 戊 (30%)        | 庚 (10%)          |
| 午     | 丁 (70%)      | 己 (30%)        | —                 |
| 未     | 己 (60%)      | 丁 (30%)        | 乙 (10%)          |
| 申     | 庚 (60%)      | 壬 (30%)        | 戊 (10%)          |
| 酉     | 辛 (100%)     | —               | —                 |
| 戌     | 戊 (60%)      | 辛 (30%)        | 丁 (10%)          |
| 亥     | 壬 (70%)      | 甲 (30%)        | —                 |

---

## City Coordinates Lookup (城市经纬度)

When the user provides a birth city, resolve it to longitude (lng) and latitude (lat) using this table. **Do NOT ask the user for coordinates -- look them up here automatically.**

If the city is not listed, estimate from a nearby city or use a reasonable default (e.g. provincial capital).

### China — Municipalities & Provincial Capitals

| City | lng | lat |
|------|-----|-----|
| 北京 | 116.407 | 39.904 |
| 上海 | 121.474 | 31.230 |
| 天津 | 117.201 | 39.084 |
| 重庆 | 106.552 | 29.563 |
| 南京 | 118.797 | 32.060 |
| 杭州 | 120.155 | 30.274 |
| 广州 | 113.264 | 23.129 |
| 深圳 | 114.058 | 22.543 |
| 成都 | 104.067 | 30.573 |
| 武汉 | 114.316 | 30.581 |
| 西安 | 108.940 | 34.342 |
| 郑州 | 113.640 | 34.757 |
| 济南 | 117.121 | 36.652 |
| 沈阳 | 123.432 | 41.806 |
| 长春 | 125.324 | 43.817 |
| 哈尔滨 | 126.536 | 45.802 |
| 石家庄 | 114.515 | 38.043 |
| 太原 | 112.549 | 37.871 |
| 呼和浩特 | 111.752 | 40.841 |
| 合肥 | 117.227 | 31.821 |
| 福州 | 119.297 | 26.075 |
| 南昌 | 115.892 | 28.677 |
| 长沙 | 112.939 | 28.228 |
| 海口 | 110.331 | 20.022 |
| 昆明 | 102.715 | 25.049 |
| 贵阳 | 106.630 | 26.648 |
| 拉萨 | 91.141 | 29.646 |
| 兰州 | 103.834 | 36.061 |
| 西宁 | 101.778 | 36.617 |
| 银川 | 106.231 | 38.487 |
| 乌鲁木齐 | 87.617 | 43.826 |
| 南宁 | 108.367 | 22.817 |

### China — Other Major Cities

| City | lng | lat |
|------|-----|-----|
| 苏州 | 120.585 | 31.299 |
| 无锡 | 120.312 | 31.491 |
| 宁波 | 121.544 | 29.868 |
| 温州 | 120.699 | 28.001 |
| 厦门 | 118.111 | 24.480 |
| 青岛 | 120.383 | 36.067 |
| 大连 | 121.615 | 38.914 |
| 烟台 | 121.391 | 37.539 |
| 珠海 | 113.577 | 22.271 |
| 佛山 | 113.121 | 23.022 |
| 东莞 | 113.752 | 23.021 |
| 桂林 | 110.290 | 25.274 |
| 洛阳 | 112.454 | 34.620 |
| 开封 | 114.308 | 34.797 |
| 保定 | 115.465 | 38.874 |
| 唐山 | 118.180 | 39.631 |
| 大同 | 113.300 | 40.077 |
| 包头 | 109.840 | 40.657 |
| 齐齐哈尔 | 123.918 | 47.354 |
| 大庆 | 125.103 | 46.589 |

### International Cities

| City | lng | lat |
|------|-----|-----|
| 纽约 | -74.006 | 40.713 |
| 洛杉矶 | -118.244 | 34.052 |
| 旧金山 | -122.419 | 37.775 |
| 芝加哥 | -87.630 | 41.878 |
| 西雅图 | -122.332 | 47.606 |
| 波士顿 | -71.059 | 42.360 |
| 华盛顿 | -77.037 | 38.907 |
| 伦敦 | -0.128 | 51.507 |
| 巴黎 | 2.352 | 48.857 |
| 柏林 | 13.405 | 52.520 |
| 莫斯科 | 37.617 | 55.756 |
| 东京 | 139.650 | 35.676 |
| 大阪 | 135.502 | 34.694 |
| 首尔 | 126.978 | 37.567 |
| 新加坡 | 103.820 | 1.352 |
| 曼谷 | 100.502 | 13.756 |
| 悉尼 | 151.209 | -33.869 |
| 墨尔本 | 144.963 | -37.814 |
| 多伦多 | -79.383 | 43.653 |
| 温哥华 | -123.122 | 49.283 |

---

## Calculation Steps

> **Reminder: Perform all steps below yourself using arithmetic. Do not call any tool or library.**

### Step 1: True Solar Time Conversion

Standard Chinese time is based on Beijing (120°E). Adjust for the birth location:

```
time_offset_minutes = (birth_longitude - 120.0) × 4
true_solar_time = local_time + time_offset_minutes
```

### Step 2: Four Pillars (四柱) — Direct Arithmetic (No Library)

All four pillars are computed with arithmetic and lookup tables. Work through each sub-step in order.

---

#### 2a. Year Pillar (年柱)

Use the birth **year** (if the birth date is before 立春 of that year, use the previous year):

```
year_stem_index   = (year − 4) % 10   → index into Stems list (甲=0 … 癸=9)
year_branch_index = (year − 4) % 12   → index into Branches list (子=0 … 亥=11)
```

**Example:** 1990 → stem = (1990−4)%10 = 6 → 庚 ; branch = (1990−4)%12 = 6 → 午 → **庚午年**

---

#### 2b. Month Pillar (月柱)

The Bazi month changes at **solar terms (节令)**, NOT at the lunar new month. Find which month the true-solar-time date falls in using the table below, then derive the stem.

**Month Branch by Solar Term:**

| Bazi Month | Branch | Solar Term (节) | Approx. Start |
|---|---|---|---|
| 1 | 寅 | 立春 Start of Spring | Feb 4 |
| 2 | 卯 | 惊蛰 Awakening of Insects | Mar 6 |
| 3 | 辰 | 清明 Clear and Bright | Apr 5 |
| 4 | 巳 | 立夏 Start of Summer | May 6 |
| 5 | 午 | 芒种 Grain in Ear | Jun 6 |
| 6 | 未 | 小暑 Minor Heat | Jul 7 |
| 7 | 申 | 立秋 Start of Autumn | Aug 7 |
| 8 | 酉 | 白露 White Dew | Sep 8 |
| 9 | 戌 | 寒露 Cold Dew | Oct 8 |
| 10 | 亥 | 立冬 Start of Winter | Nov 7 |
| 11 | 子 | 大雪 Major Snow | Dec 7 |
| 12 | 丑 | 小寒 Minor Cold | Jan 6 |

**Month Stem — Five Tiger Trick (五虎遁年起月法):**

| Year Stem | Month-1 (寅) starts at Stem index |
|---|---|
| 甲 or 己 | 2 (丙) |
| 乙 or 庚 | 4 (戊) |
| 丙 or 辛 | 6 (庚) |
| 丁 or 壬 | 8 (壬) |
| 戊 or 癸 | 0 (甲) |

```
month_offset      = bazi_month_number − 1      (0 for month 1, 1 for month 2 … 11 for month 12)
month_stem_index  = (five_tiger_start + month_offset) % 10
```

**Example:** Year stem 庚 (index 6) → five-tiger start = 4 (戊). Birth in March (Bazi month 2, 卯) → month_stem = (4 + 1) % 10 = 5 → 己. Month pillar: **己卯**.

---

#### 2c. Day Pillar (日柱)

Use the **Julian Day Number (JDN)** to get a unique integer for each calendar date, then apply the fixed offset.

**Step 1 — Compute JDN:**
```
If M ≤ 2: set Y = Y−1, M = M+12
A = floor(Y / 100)
B = 2 − A + floor(A / 4)
JDN = floor(365.25 × (Y + 4716)) + floor(30.6001 × (M + 1)) + D + B − 1524
```

**Step 2 — Day Stem-Branch:**
```
delta            = JDN − 2415021        (2415021 = JDN of 1900-01-01)
day_stem_index   = delta % 10           (甲=0, 乙=1, … 癸=9)
day_branch_index = (delta + 10) % 12    (子=0, 丑=1, … 亥=11)
```

**Verification anchor:** JDN 2451545 = **2000-01-01 = 戊午日** (delta=36524, stem=4=戊, branch=6=午).

---

#### 2d. Hour Pillar (时柱)

1. Map the true-solar-time hour to an Earthly Branch:
   - Hour 23 or 0 → index 0 (子)
   - Otherwise → `(hour + 1) // 2`

2. Derive the Heavenly Stem using the **Five Rat Trick (五鼠遁)** from the Day Stem:

| Day Stem   | 子时 starts at Stem index |
|-----------|--------------------------|
| 甲 or 己   | 0 (甲) |
| 乙 or 庚   | 2 (丙) |
| 丙 or 辛   | 4 (戊) |
| 丁 or 壬   | 6 (庚) |
| 戊 or 癸   | 8 (壬) |

```
hour_stem_index = (zi_start_index + branch_index) % 10
```

### Step 3: Ten Gods (十神)

The Ten Gods describe the relationship between any Heavenly Stem and the **Day Master** (日主 = Day Pillar's Heavenly Stem).

Algorithm — given Day Stem index `d` and Other Stem index `o`:
1. Compute Five-Element indices: `d_wx = d // 2`, `o_wx = o // 2`
2. Check polarity: `same_polarity = (d % 2) == (o % 2)`
3. Compute relation: `diff = (o_wx - d_wx) % 5`

| diff | Relationship | Same Polarity | Different Polarity |
|------|-------------|--------------|-------------------|
| 0    | Same as me  | 比肩 (Companion) | 劫财 (Rob Wealth) |
| 1    | I produce   | 食神 (Eating God) | 伤官 (Hurting Officer) |
| 2    | I control   | 偏财 (Indirect Wealth) | 正财 (Direct Wealth) |
| 3    | Controls me | 七杀 (Seven Killings) | 正官 (Direct Officer) |
| 4    | Produces me | 偏印 (Indirect Seal) | 正印 (Direct Seal) |

### Step 4: Five Elements Energy Score

For each of the Four Pillars, accumulate scores:
- Each **Heavenly Stem** contributes **100 points** to its element
- Each **Hidden Stem** in the Earthly Branch contributes its weighted score (see Hidden Stems table above)

Then apply **monthly coefficients** based on the Month Branch to get seasonal adjustments. The element in season gets a ~2× boost; the element controlled by the season gets ~0.5×.

### Step 5: Day Master Strength (日主强弱)

Compute:
- **Allies (同党):** Elements that are Same-as-me + Produces-me (比劫 + 印)
- **Opponents (异党):** Elements that I-produce + I-control + Controls-me (食伤 + 财 + 官杀)

If allies score > opponents score → Day Master is **Strong (身强)**
If opponents score > allies score → Day Master is **Weak (身弱)**

### Step 6: Favorable & Unfavorable Elements (用神/忌神)

- **Strong Day Master** needs to be drained/controlled → Favorable: Food God element, Wealth element, Officer element. Unfavorable: Seal, Companion.
- **Weak Day Master** needs support → Favorable: Seal element, Companion element. Unfavorable: Food, Wealth, Officer.

### Step 7: Major Fortune Cycles (大运)

1. Determine direction: Yang-year + Male OR Yin-year + Female → **Forward**; otherwise → **Reverse**
2. Calculate start age: Count days between birth and the next (forward) or previous (reverse) solar term (节); 3 days = 1 year
3. Starting from the Month Pillar, step the Stem-Branch forward or backward for each 10-year cycle

---

## Lite Interpretation Guide

### Day Master Personality Profiles

| Day Master | Element | Core Traits |
|-----------|---------|-------------|
| 甲 | Wood (Yang) | Upright, ambitious, natural leader |
| 乙 | Wood (Yin)  | Gentle, resilient, adaptable |
| 丙 | Fire (Yang) | Passionate, radiant, optimistic |
| 丁 | Fire (Yin)  | Meticulous, warm, patient |
| 戊 | Earth (Yang)| Honest, steady, inclusive |
| 己 | Earth (Yin) | Gentle, responsible, nurturing |
| 庚 | Metal (Yang)| Resolute, decisive, principled |
| 辛 | Metal (Yin) | Refined, precise, persistent |
| 壬 | Water (Yang)| Intelligent, dynamic, big-picture thinker |
| 癸 | Water (Yin) | Gentle, wise, highly adaptable |

### Pattern (格局) Quick Guide

The pattern is determined primarily by the Ten God of the Month Pillar's Heavenly Stem:

| Pattern | Key Characteristics |
|---------|-------------------|
| 食神格 (Eating God) | Creative, expressive, enjoys life |
| 伤官格 (Hurting Officer) | Talented, unconventional, outspoken |
| 正官格 (Direct Officer) | Responsible, disciplined, rule-following |
| 七杀格 (Seven Killings) | Bold, courageous, risk-taking |
| 正印格 (Direct Seal) | Wise, studious, compassionate |
| 偏印格 (Indirect Seal) | Original thinker, perceptive, solitary |
| 正财格 (Direct Wealth) | Pragmatic, good with money, reliable |
| 偏财格 (Indirect Wealth) | Flexible, opportunistic, sociable |

### Lucky Attributes by Favorable Element

| Favorable Element | Lucky Colors | Lucky Direction |
|------------------|-------------|----------------|
| 木 Wood  | Green, Teal       | East   |
| 火 Fire  | Red, Purple        | South  |
| 土 Earth | Yellow, Brown      | Center |
| 金 Metal | White, Gold        | West   |
| 水 Water | Black, Blue        | North  |

---

## Output Format

When presenting results to the user, structure the output as:

1. **Birth Info** — Name, date, time, location, true solar time
2. **Four Pillars Chart** — Year / Month / Day / Hour pillars with Stem, Branch, Hidden Stems, Ten Gods, and Na-Yin
3. **Five Elements Analysis** — Score breakdown, strongest/weakest element, missing elements
4. **Day Master Analysis** — Element, strength (strong/weak/balanced), personality tags
5. **Favorable Elements** — Yong Shen (用神), Xi Shen (喜神), Ji Shen (忌神), lucky colors, lucky directions
6. **Major Fortune Cycles** — Start age, 10-year cycle Stem-Branch pairs

---

## Advanced Features — Available on Compass AI

This skill covers the core calculation and basic interpretation. For a **complete, AI-powered fortune experience**, visit:

**[https://fortune.zodi.zone/web/](https://fortune.zodi.zone/web/)**

Advanced features include:

- **AI Deep Analysis** — Full personality, career, relationship, and health analysis powered by large language models with streaming output
- **Life K-Line Chart (人生K线图)** — Fortune scores from age 0 to 100, visualized as an interactive chart showing the highs and lows of each life stage
- **Two-Person Compatibility (合盘分析)** — Compare two birth charts for love, business, or family compatibility with detailed energy dynamics, conflict points, and synergy analysis
- **Daily Fortune Stick (每日灵签)** — Personalized daily divination based on your Bazi and the current day's energy
- **Interactive Fortune Chat (命理对话)** — Multi-turn conversation with an AI fortune-teller that remembers your chart and provides deep, contextual guidance
- **Fortune Book Management (命书管理)** — Save, compare, and revisit birth charts for yourself and your loved ones

**Try it now → [Compass AI](https://fortune.zodi.zone/web/)**
