---
name: FA Advisor
description: Professional Financial Advisor (FA) skill for primary market financing - replaces traditional investment advisory services with AI-powered project assessment, pitch deck generation, valuation analysis, and investor matching
version: 0.1.0
metadata:
  clawdbot:
    emoji: 💼
    homepage: https://github.com/your-org/openclaw-fa-advisor
    tags:
      - finance
      - investment
      - fundraising
      - valuation
      - pitch-deck
      - venture-capital
      - startup
      - fa
      - advisor
    requires:
      env: []
      bins: []
      config: []
    install: []
    os: [darwin, linux, win32]
---

# FA Advisor - AI Investment Advisory Skill

**FA Advisor** is a comprehensive financial advisory skill that replaces traditional primary market investment advisors (FA). It provides professional services for both startups seeking funding and investors evaluating opportunities.

## When to Use This Skill

Use FA Advisor when you need to:

- **For Startups:**
  - Assess your project's investment readiness
  - Generate professional pitch decks and business plans
  - Get company valuation analysis
  - Find and match with suitable investors
  - Design fundraising strategy

- **For Investors:**
  - Analyze startup investment opportunities
  - Generate investment memos
  - Conduct preliminary due diligence
  - Assess deal valuation and terms

## Core Capabilities

### 1. Project Assessment
Comprehensive evaluation across 5 dimensions:
- Team quality (founders, size, experience)
- Market opportunity (TAM, growth rate, competition)
- Product maturity (stage, features, differentiation)
- Market traction (customers, revenue, growth)
- Financial health (metrics, runway, unit economics)

**Output:** 0-100 score, investment readiness level, strengths/weaknesses, recommendations

### 2. Pitch Deck & Business Plan Generation
Automatically creates professional fundraising materials:
- 12-slide standard pitch deck outline
- Detailed business plan document
- Cover, Problem, Solution, Market, Product, Business Model, Traction, Competition, Team, Financials, Ask, Vision

**Output:** Structured pitch deck outline, full markdown business plan

### 3. Valuation Analysis
Multi-method valuation engine:
- **Scorecard Method** - Factor-based adjustment (team, market, product, etc.)
- **Berkus Method** - Pre-revenue qualitative valuation (5 key factors)
- **Risk Factor Summation** - 12 risk factors assessment
- **Comparable Company Method** - Industry multiples (for revenue-stage companies)

**Output:** Recommended valuation range, methodology breakdown, deal terms suggestion

### 4. Investor Matching
Smart matching algorithm considering:
- Funding stage alignment
- Industry focus
- Investment amount range
- Geographic preference
- Business model fit

**Output:** Top 20 matched investors, match score (0-100), approach strategy, priority ranking

### 5. Investment Analysis
Generate professional investment memos:
- Executive summary
- Investment highlights
- Market opportunity analysis
- Competitive position assessment
- Team evaluation
- Financial analysis
- Risk identification
- Investment recommendation (Pass/Maybe/Proceed/Strong-Yes)

**Output:** Complete investment memo, due diligence checklist

## How to Use

### Quick Commands

```
"Assess my startup project"
"Generate a pitch deck for my SaaS company"
"What's a reasonable valuation for my Series A?"
"Match me with suitable VCs"
"Analyze this startup as an investor"
"Create an investment memo"
```

### Detailed Usage

**Step 1: Prepare Project Information**

Provide your project details including:
- Company name, description, industry
- Product stage and features
- Market size (TAM/SAM/SOM) and growth rate
- Team information (founders, size)
- Financial metrics (revenue, burn rate, runway)
- Traction (customers, users, partnerships)
- Fundraising goals (stage, target amount)

**Step 2: Choose Your Service**

**For Startups - Complete Package:**
```
"I need help preparing for Series A fundraising. My company is [name],
we do [description], currently have [metrics], and seeking $[amount]
for [use of funds]."
```

The skill will generate:
- ✅ Project assessment with scores
- ✅ Professional pitch deck (12 slides)
- ✅ Detailed business plan
- ✅ Valuation analysis ($X pre-money)
- ✅ Top 20 matched investors with outreach strategy

**For Investors - Analysis Package:**
```
"Analyze this startup opportunity: [company description and metrics]"
```

The skill will generate:
- ✅ Investment memo with recommendation
- ✅ Due diligence checklist
- ✅ Risk assessment
- ✅ Valuation analysis

**For Quick Assessment:**
```
"Quick assessment: evaluate my project readiness for fundraising"
```

**For Specific Needs:**
- "Generate pitch deck only"
- "Do a valuation analysis"
- "Find matching investors"
- "Create business plan"

## Example Scenarios

### Scenario 1: Early-Stage Startup Preparing for Seed Round

**User Input:**
```
"I'm preparing for seed fundraising. My company CloudFlow AI is an
enterprise AI workflow automation platform. We have 45 customers,
$1.2M ARR, 85% gross margin, and seeking $3M seed funding."
```

**FA Advisor Output:**
1. **Assessment**: Overall score 78/100 - "Ready for fundraising"
2. **Valuation**: $8-12M pre-money (using Scorecard + Berkus methods)
3. **Pitch Deck**: 12-slide outline customized for your business
4. **Matched Investors**: 15 seed-stage VCs with 80+ match scores
   - Y Combinator (90/100) - Stage & industry perfect match
   - Sequoia China (85/100) - Geographic + industry fit
   - Matrix Partners (82/100) - Enterprise software focus
5. **Strategy**: "Prioritize warm intros, target 5-10 firms in parallel, 2-3 month timeline"

### Scenario 2: VC Evaluating Series A Deal

**User Input:**
```
"Analyze this Series A opportunity: FinTech startup, $5M revenue,
200% YoY growth, asking for $15M at $60M pre."
```

**FA Advisor Output:**
1. **Investment Memo**: "Proceed" recommendation
2. **Highlights**:
   - Strong revenue traction ($5M ARR)
   - Exceptional growth (200% YoY)
   - Large market opportunity (FinTech)
3. **Risks**:
   - High competition in FinTech space
   - Regulatory uncertainty
   - Customer concentration risk
4. **Valuation**: Fair range $50-70M pre-money (12x revenue multiple)
5. **Next Steps**: Customer calls, financial deep-dive, regulatory review

### Scenario 3: Valuation for Growth-Stage Company

**User Input:**
```
"My B2B SaaS company has $10M ARR, 120% net revenue retention,
40 enterprise customers. What's a fair Series B valuation?"
```

**FA Advisor Output:**
- **Comparable Method**: $100-120M (10-12x ARR for enterprise SaaS)
- **VC Method**: $90M (targeting 10x return)
- **Recommended**: $100M pre-money
- **Deal Structure**: 20% dilution for $25M investment
- **Rationale**: Strong NRR and enterprise focus justify premium multiple

## Data Structure

The skill uses TypeScript with Zod schemas for type safety:

### Project Schema
```typescript
{
  name, description, industry, businessModel, location,
  product: { stage, features, valueProposition, painPoints },
  market: { tam, sam, som, growthRate, competitors },
  team: { founders, teamSize, keyHires },
  financials: { revenue, expenses, metrics },
  fundraising: { stage, targetAmount, useOfFunds },
  traction: { customers, users, growth, partnerships }
}
```

### Investor Schema
```typescript
{
  name, type, description, headquarters,
  strategy: { stages, industries, investmentRange, geographicFocus },
  investmentStyle: { leadInvestor, handsOn, valueAdd },
  portfolio, team, contact
}
```

## Outputs & Deliverables

All outputs are generated as structured markdown documents:

1. **assessment-report.md** - Project evaluation with scores and recommendations
2. **pitch-deck-outline.md** - 12-slide deck structure with key points
3. **business-plan.md** - Complete BP (10-15 pages)
4. **valuation-analysis.md** - Multi-method valuation with assumptions
5. **investor-matches.md** - Ranked list with match reasoning and strategy
6. **investment-memo.md** - Professional memo for investor decision-making
7. **dd-checklist.md** - Due diligence checklist (50+ items)

## Customization

The skill can be customized for:
- **Industries**: Enterprise software, consumer internet, FinTech, HealthTech, AI/ML, etc.
- **Stages**: Pre-seed, Seed, Series A/B/C, Growth
- **Regions**: North America, Europe, China, Southeast Asia, Global
- **Languages**: English, 中文 (Chinese)

## Technical Details

**Built with:**
- TypeScript for type safety
- Zod for schema validation
- Modular architecture (assessment, pitchdeck, valuation, matching, analysis)
- Extensible design for custom valuation methods

**Requirements:**
- No external API keys required for basic functionality
- Optional: Crunchbase API, PitchBook data for enhanced investor matching
- Node.js 18+ environment

## Best Practices

1. **For Accurate Results**: Provide complete and accurate project information
2. **Valuation**: Consider as guidance, not absolute truth - market dynamics matter
3. **Investor Matching**: Use as starting point, warm introductions always better
4. **Pitch Deck**: Customize the generated outline with your unique story
5. **Multiple Iterations**: Refine inputs based on initial assessment recommendations

## Limitations

- Valuation models are estimations based on market benchmarks
- Investor data may not be 100% current (update regularly)
- No substitute for professional legal/financial advice
- Results depend heavily on input quality and completeness

## Privacy & Security

- All processing is done locally
- No data is sent to external services (unless optional APIs enabled)
- Your financial data and pitch materials remain private
- Suitable for confidential pre-announcement fundraising

## Support & Contributions

- GitHub: [Repository Link]
- Issues: Report bugs or request features
- Contributions: See CONTRIBUTING.md
- Examples: Check `/examples` directory for full code samples

## License

MIT License - Free for commercial and personal use

---

## Quick Start Example

```typescript
import FAAdvisor from '@openclaw/skill-fa-advisor';

const advisor = new FAAdvisor();

// Quick assessment
await advisor.quickAssessment(yourProject);

// Full startup package
const result = await advisor.startupPackage(yourProject);
// → Assessment, Pitch Deck, BP, Valuation, Investor Matches

// Investor analysis
const memo = await advisor.investorPackage(yourProject);
// → Investment Memo, DD Checklist, Risks, Recommendation
```

---

**Version**: 0.1.0
**Updated**: 2024-01-04
**Compatibility**: OpenClaw 2025+
