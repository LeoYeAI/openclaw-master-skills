# Strategy Playbook — Apple Search Ads

Complete strategic guide for planning, launching, and scaling ASA campaigns.

## Campaign Planning

### Before You Start

**Prerequisites checklist:**
- [ ] App Store listing optimized (screenshots, description, keywords)
- [ ] Conversion tracking implemented (AdServices or MMP)
- [ ] LTV model estimated (even rough)
- [ ] Budget allocated ($500+ monthly recommended to start)
- [ ] Competitor research done

### Know Your Numbers

| Metric | How to Calculate | Why It Matters |
|--------|------------------|----------------|
| **LTV** | Revenue per user over lifetime | Sets max CPA |
| **Target CPA** | LTV / 3 to LTV / 5 | Profitable acquisition |
| **Breakeven CPA** | LTV - margins | Maximum spend |
| **TTR benchmark** | 5-10% | Ad relevance |
| **CVR benchmark** | 30-60% | Landing page quality |

## Campaign Architecture

### The 4-Campaign Structure

```
1. BRAND (Defend)
   └── Your app name, brand terms
   └── Goal: 100% impression share, lowest CPA
   └── Budget: 10-20% of total
   
2. CATEGORY (Capture)
   └── Generic category terms
   └── Goal: Volume with target CPA
   └── Budget: 40-50% of total
   
3. COMPETITOR (Steal)
   └── Competitor app names
   └── Goal: Profitable poaching
   └── Budget: 15-25% of total
   
4. DISCOVERY (Learn)
   └── Search Match enabled
   └── Goal: Find new keywords
   └── Budget: 10-15% of total
```

### Ad Group Structure

For each campaign, create ad groups by:

**Option A: By Match Type**
```
Campaign: MyApp - US - Category
├── Ad Group: Category - Exact
│   └── meditation app, mindfulness, daily meditation
├── Ad Group: Category - Broad
│   └── meditation, mindfulness
└── Ad Group: Category - Discovery
    └── Search Match ON
```

**Option B: By Theme**
```
Campaign: MyApp - US - Category
├── Ad Group: Meditation
│   └── meditation app, best meditation, guided meditation
├── Ad Group: Sleep
│   └── sleep app, sleep sounds, better sleep
└── Ad Group: Stress
    └── stress relief, anxiety app, calm app
```

## Keyword Strategy

### Keyword Research Process

1. **Start with App Store Connect**
   - Download search terms from your organic sources
   - These are proven to have intent for your app

2. **Competitor Analysis**
   - What keywords do competitors rank for?
   - Use tools: Sensor Tower, App Annie, Mobile Action

3. **Apple Search Ads Suggestions**
   - Use the keyword suggestions in ASA dashboard
   - Add with broad match first to test

4. **Search Term Mining**
   - Review Search Term reports weekly
   - Graduate high performers to exact match

### Keyword Tiers

| Tier | Description | Bid Strategy |
|------|-------------|--------------|
| **Tier 1** | Brand terms | Bid high (2-3x avg) |
| **Tier 2** | Category leaders | Bid at target CPA |
| **Tier 3** | Long-tail specific | Bid below avg, test |
| **Tier 4** | Competitor names | Start low, test carefully |
| **Tier 5** | Discovery/Broad | Lowest bids, mine data |

### Negative Keywords

**Add negatives immediately for:**
- "free" (if you're paid)
- Competitor names (in brand campaign)
- Unrelated categories
- Misspellings that waste budget

**Negative keyword structure:**
```
Campaign-level negatives:
└── Broad terms you NEVER want

Ad Group-level negatives:
└── Terms that belong in OTHER ad groups
```

## Bidding Strategy

### Starting Bids

| Campaign Type | Starting Bid | Adjust After |
|---------------|--------------|--------------|
| Brand | $2-3 | 7 days |
| Category | $1-2 | 7 days |
| Competitor | $0.50-1 | 14 days |
| Discovery | $0.30-0.50 | 7 days |

### Optimization Cadence

**Daily (5 min):**
- Check spend vs budget
- Pause anything wildly over CPA

**Weekly (30 min):**
- Review search terms
- Add negatives
- Graduate keywords
- Adjust bids ±20%

**Monthly (2 hours):**
- Full performance review
- Budget reallocation
- Test new keywords
- Analyze competitor trends

### Bid Adjustment Rules

```
If CPA < Target by 20%+ AND volume is good:
  → Increase bid 20%

If CPA > Target by 20%+:
  → Decrease bid 20%
  → Or pause if no improvement after 2 weeks

If Impressions low BUT CPA is good:
  → Increase bid gradually to get more volume

If TTR < 3%:
  → Ad isn't relevant, lower bid or pause
```

## Scaling Strategy

### Phase 1: Validation ($500-2K/month)

Goals:
- Prove attribution works
- Find CPA benchmarks
- Identify winning keywords

Structure:
- 1-2 campaigns (Brand + Category)
- 3-5 ad groups
- 20-50 keywords
- US only

### Phase 2: Optimization ($2K-10K/month)

Goals:
- Optimize to target CPA
- Build keyword portfolio
- Test competitors

Structure:
- 4 campaigns (full structure)
- 10-15 ad groups
- 100-200 keywords
- Add UK, Canada, Australia

### Phase 3: Scale ($10K+/month)

Goals:
- Maximize volume at CPA
- International expansion
- Custom Product Pages

Structure:
- Multiple campaigns per country
- Dedicated teams for optimization
- Advanced automation
- All major markets

### Budget Scaling Rules

**Don't scale too fast.** Increase budget by max 20-30% at a time.

```
Week 1: $50/day
Week 2: If CPA good → $65/day
Week 3: If CPA good → $85/day
Week 4: If CPA good → $110/day
...
```

If CPA spikes after increase, pull back immediately.

## Multi-Country Expansion

### Expansion Order (English-first)

1. **Tier 1:** US (highest volume, test here first)
2. **Tier 2:** UK, Canada, Australia (English, easy)
3. **Tier 3:** Germany, France (high value, need localization)
4. **Tier 4:** Japan, South Korea (high LTV, need localization)
5. **Tier 5:** Brazil, Mexico, India (volume play, lower CPT)

### Localization Checklist

For each new country:
- [ ] App Store listing translated
- [ ] Screenshots localized
- [ ] Keywords researched in local language
- [ ] Custom Product Page created
- [ ] Separate campaign created
- [ ] Local currency budget set

### Country-Specific Considerations

| Country | Notes |
|---------|-------|
| US | Highest competition, highest CPT, but most volume |
| UK | Similar to US but smaller, good for testing |
| Germany | High LTV, privacy-conscious, need localization |
| Japan | Very high LTV for games, unique keywords |
| Brazil | High volume, low CPT, Portuguese required |

## Custom Product Pages

### Strategy

Create CPPs for:
1. **Different audiences** — Feature focus (workout vs meditation)
2. **Different intents** — Problem vs aspiration
3. **Seasonal** — Holidays, New Year, summer

### A/B Testing

```
Campaign: MyApp - US - Category
├── Ad Group: Meditation - Control
│   └── Default Product Page
│   └── 50% traffic
└── Ad Group: Meditation - Test
    └── CPP: Sleep-focused
    └── 50% traffic
```

Run for 2 weeks minimum, then compare CVR.

## Advanced Tactics

### Dayparting

Test performance by hour of day:
1. Run 2 weeks with all hours
2. Analyze by hour in reports
3. Turn off worst-performing hours
4. Reallocate budget to best hours

### Audience Exclusions

Exclude users who already have your app:
```json
"targetingDimensions": {
  "appDownloaders": {
    "excluded": [YOUR_ADAM_ID]
  }
}
```

### Search Tab Campaigns

Lower intent but cheaper clicks:
- Good for brand awareness
- Use different creative messaging
- Expect lower CVR but lower CPT
- Separate budget from Search Results

### Today Tab Campaigns

Premium placement, brand awareness:
- Higher minimum budget
- Best for app launches
- Seasonal promotions
- Brand building

## Reporting & Analysis

### Key Reports to Run

| Report | Frequency | Purpose |
|--------|-----------|---------|
| Campaign performance | Daily | Monitor spend/CPA |
| Search terms | Weekly | Keyword mining |
| Ad group performance | Weekly | Bid optimization |
| Impression share | Monthly | Competitive view |
| Geo performance | Monthly | Country decisions |

### Funnel Analysis

Track the full funnel:
```
Impressions → Taps → Installs → Activations → Revenue
     ↓          ↓         ↓            ↓           ↓
   TTR        CVR     Retention    Conversion    ROAS
```

### Attribution Windows

Default: 30-day click-through attribution

Consider:
- Short window (7 days) for quick decisions
- Long window (30 days) for accurate LTV

## Common Mistakes

1. **Starting with broad match only** → No control, wasted spend
2. **Ignoring Search Terms** → Missing optimization gold
3. **Same bid everywhere** → Different keywords have different values
4. **Scaling too fast** → CPA spikes, budget burned
5. **No negatives** → Paying for irrelevant searches
6. **Mixing countries** → Can't optimize properly
7. **Not defending brand** → Competitors steal your users
8. **Ignoring CVR** → Problem might be App Store, not ads
9. **No attribution** → Optimizing blind
10. **Copying competitors** → Their strategy isn't yours
