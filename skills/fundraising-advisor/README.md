# OpenClaw FA Advisor Skill

> 🎉 **Python版本已完全实现并测试通过！** (2026-03-05)
> **快速开始：** `pip install -e . && python3 test_complete.py`
> **文档：** [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md) | [PYTHON_ARCHITECTURE.md](./PYTHON_ARCHITECTURE.md)

🚀 A comprehensive Financial Advisor (FA) skill for OpenClaw that replaces traditional primary market investment advisory services.

---

## 🐍 Python版本 - Production Ready ✅

**Python版本核心优势：强大的PDF处理能力**（财务报表解析、OCR识别、专业报告生成）

### ⚡ 快速开始

```bash
# 1. 安装Python包
pip install -e .

# 2. 安装系统依赖（PDF处理）
# macOS: brew install tesseract ghostscript poppler
# Linux: sudo apt-get install tesseract-ocr poppler-utils ghostscript

# 3. 运行测试
python3 test_complete.py  # 完整测试所有6个模块
python3 example_python.py  # 简单示例
```

### ✅ 已实现的模块（100%）

- ✅ **ProjectAssessor** - 5维度项目评估（Team, Market, Product, Traction, Financials）
- ✅ **ValuationEngine** - 4种估值方法（Scorecard, Berkus, Risk Factor, Comparable）
- ✅ **PitchDeckGenerator** - 12页Pitch Deck + 完整商业计划书
- ✅ **InvestorMatcher** - 5因素投资人匹配 + 接触策略
- ✅ **InvestmentAnalyzer** - 投资备忘录 + 27项DD清单
- ✅ **PDF处理** - 解析、OCR、财务提取、报告生成（**Python独有**）

### 📊 测试结果

```
✅ 测试 1/6: 项目评估 - PASSED (89/100, HIGHLY-READY)
✅ 测试 2/6: 估值分析 - PASSED ($17.6M Pre-Money, 3种方法)
✅ 测试 3/6: Pitch Deck生成 - PASSED (12页)
✅ 测试 4/6: 商业计划书生成 - PASSED (4.4KB)
✅ 测试 5/6: 投资人匹配 - PASSED (Top匹配91.5分)
✅ 测试 6/6: 投资分析 - PASSED (STRONG-YES + 27项DD)

🎊 所有测试通过！
```

### 💻 Python API示例

```python
import asyncio
from fa_advisor import FAAdvisor, Project, FundingStage, Industry, BusinessModel

async def main():
    advisor = FAAdvisor()

    # 项目评估
    assessment = await advisor.quick_assessment(project)
    print(f"Score: {assessment.scores.overall}/100")

    # 估值分析
    valuation = await advisor.valuate(project)
    print(f"Pre-Money: ${valuation.recommended_valuation.pre_money:,.0f}")

    # 生成Pitch Deck
    pitch_deck = await advisor.generate_pitch_deck(project)

    # 投资人匹配
    matches = await advisor.match_investors(project, top_n=10)

    # PDF处理（Python独有功能）
    financial_data = await advisor.parse_financial_pdf("财报.pdf")
    ocr_result = await advisor.ocr_pdf("扫描件.pdf", language='chi_sim+eng')

asyncio.run(main())
```

**详细文档：**
- [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md) - 实现完成报告
- [PYTHON_ARCHITECTURE.md](./PYTHON_ARCHITECTURE.md) - 完整架构设计
- [QUICKSTART_PYTHON.md](./QUICKSTART_PYTHON.md) - 5分钟快速开始

---

## 📖 用户指南（通用）

## Overview

This skill provides professional investment advisory services for both startups seeking funding and investment institutions looking for quality projects. It handles the complete lifecycle of fundraising from initial assessment to deal closing.

## Core Capabilities

### 1. 📊 Project Assessment
Comprehensive evaluation across 5 dimensions:
- **Team Quality** - Founders' background, team size, experience
- **Market Opportunity** - TAM/SAM/SOM, growth rate, competition
- **Product Maturity** - Development stage, features, differentiation
- **Market Traction** - Customers, revenue, growth metrics
- **Financial Health** - Unit economics, runway, key metrics

**Output:** 0-100 score, investment readiness level, strengths/weaknesses, actionable recommendations

### 2. 📑 Pitch Deck & Business Plan Generation
Automatically creates professional fundraising materials:
- **12-slide standard pitch deck** outline covering: Cover, Problem, Solution, Market, Product, Business Model, Traction, Competition, Team, Financials, Ask, Vision
- **Detailed business plan** document (10-15 pages)
- Customized to your industry, stage, and target investors

**Output:** Structured pitch deck outline, full markdown business plan ready for customization

### 3. 💰 Valuation Analysis
Multi-method valuation engine supporting:
- **Scorecard Method** - Factor-based adjustment (team, market, product, competition, etc.)
- **Berkus Method** - Pre-revenue qualitative valuation (5 key factors)
- **Risk Factor Summation** - 12 risk factors assessment with adjustments
- **Comparable Company Method** - Industry multiples analysis (for revenue-stage companies)

**Output:** Recommended pre-money valuation range, methodology breakdown, deal terms suggestions

### 4. 🎯 Investor Matching
Smart matching algorithm considering:
- Funding stage alignment
- Industry focus and expertise
- Investment amount range
- Geographic preferences
- Business model fit
- Historical portfolio

**Output:** Top 20 matched investors with scores (0-100), detailed reasoning, outreach strategy, priority ranking

### 5. 🔍 Investment Analysis (For Investors)
Generate professional investment decision-making materials:
- Executive summary with clear recommendation
- Investment highlights and key value drivers
- Market opportunity and TAM analysis
- Competitive positioning assessment
- Team evaluation and capability review
- Financial analysis and unit economics
- Risk identification with severity ratings
- Due diligence checklist (50+ items)

**Output:** Complete investment memo, recommendation (Pass/Maybe/Proceed/Strong-Yes), DD checklist

## Usage

### Quick Start with OpenClaw

```bash
# Talk to the FA advisor through any connected channel
openclaw agent --message "I'm raising a Series A for my SaaS startup, need help with pitch deck"

# Or through specific channels (WhatsApp, Telegram, Slack, etc.)
# Just send a message like: "Help me prepare for fundraising"
```

### Common Use Cases

**For Startups:**
```
"Assess my startup's investment readiness"
"Generate a pitch deck for my [industry] startup"
"What's a reasonable valuation for my Series A?"
"Which VCs should I target?"
"Create a complete fundraising package"
"Help me prepare for due diligence"
```

**For Investors:**
```
"Analyze this Series A opportunity"
"What are the key risks in this deal?"
"Generate an investment memo"
"Is the valuation fair?"
"Create a due diligence checklist"
```

## Example Scenarios

### Scenario 1: Early-Stage Startup Preparing for Seed Round

**Input:**
```
"I'm preparing for seed fundraising. My company CloudFlow AI is an enterprise
AI workflow automation platform. We have 45 customers, $1.2M ARR, 85% gross
margin, and seeking $3M seed funding."
```

**FA Advisor Output:**
1. **Assessment**: Overall score 78/100 - "Ready for fundraising"
2. **Valuation**: $8-12M pre-money (Scorecard + Berkus methods)
3. **Pitch Deck**: 12-slide outline customized for your business
4. **Matched Investors**: 15 seed-stage VCs with 80+ match scores
   - Y Combinator (90/100) - Perfect stage & industry match
   - Sequoia China (85/100) - Geographic + industry fit
   - Matrix Partners (82/100) - Enterprise software focus
5. **Strategy**: Prioritize warm intros, target 5-10 firms in parallel

### Scenario 2: VC Evaluating Series A Deal

**Input:**
```
"Analyze this Series A opportunity: FinTech startup, $5M revenue,
200% YoY growth, asking for $15M at $60M pre."
```

**FA Advisor Output:**
1. **Investment Memo**: "Proceed" recommendation
2. **Highlights**: Strong traction, exceptional growth, large TAM
3. **Risks**: High competition, regulatory uncertainty, customer concentration
4. **Valuation**: Fair range $50-70M (12x revenue multiple)
5. **Next Steps**: Customer calls, financial deep-dive, regulatory review

### Scenario 3: Valuation Question

**Input:**
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

## Programmatic Usage (Advanced)

For developers who want to use the skill programmatically:

```typescript
import FAAdvisor from '@openclaw/skill-fa-advisor';
import type { Project } from '@openclaw/skill-fa-advisor';

// Initialize advisor
const advisor = new FAAdvisor();

// Quick assessment
const assessment = await advisor.quickAssessment(yourProject);
console.log(`Score: ${assessment.scores.overall}/100`);

// Full startup package
const result = await advisor.startupPackage(yourProject);
// Returns: assessment, pitchDeck, businessPlan, valuation, investorMatches

// Investor analysis
const memo = await advisor.investorPackage(yourProject);
// Returns: investment memo, DD checklist, recommendation

// Individual services
const pitchDeck = await advisor.generatePitchDeck(yourProject);
const valuation = await advisor.valuate(yourProject);
const investors = await advisor.matchInvestors(yourProject, 20);
```

See [examples/](./examples/) directory for complete code samples.

## Data Structure

### Project Schema

```typescript
{
  // Basic info
  name: string;
  description: string;
  industry: 'enterprise-software' | 'fintech' | 'healthcare' | ...;
  businessModel: 'b2b-saas' | 'b2c' | 'marketplace' | ...;
  location: string;
  targetMarket: string;

  // Product
  product: {
    description: string;
    stage: 'idea' | 'mvp' | 'launched' | 'scaling';
    keyFeatures: string[];
    uniqueValueProposition: string;
    customerPainPoints: string[];
  };

  // Market
  market: {
    tam: number;  // Total Addressable Market in USD
    sam?: number; // Serviceable Addressable Market
    som?: number; // Serviceable Obtainable Market
    marketGrowthRate: number; // CAGR (e.g., 0.35 for 35%)
    competitors: Array<{
      name: string;
      description: string;
      differentiation?: string;
    }>;
  };

  // Team
  team: {
    founders: Array<{
      name: string;
      title: string;
      background: string;
      linkedin?: string;
    }>;
    teamSize: number;
    keyHires?: string[];
  };

  // Financials
  financials: {
    revenue: {
      current: number; // Current ARR
      projected: Array<{ year: number; amount: number }>;
    };
    expenses: {
      monthly: number;
      runway: number; // months
    };
    metrics?: {
      arr?: number;
      mrr?: number;
      grossMargin?: number;
      customerAcquisitionCost?: number;
      lifetimeValue?: number;
      churnRate?: number;
    };
  };

  // Fundraising
  fundraising: {
    currentStage: 'pre-seed' | 'seed' | 'series-a' | 'series-b' | ...;
    targetAmount: number;
    minimumAmount?: number;
    currentValuation?: number;
    previousRounds?: Array<{
      stage: string;
      amount: number;
      date: string;
      investors: string[];
      valuation: number;
    }>;
    useOfFunds: Array<{
      category: string;
      percentage: number;
      description: string;
    }>;
  };

  // Traction (optional)
  traction?: {
    customers?: number;
    users?: number;
    growth?: string;
    partnerships?: string[];
    awards?: string[];
    press?: string[];
  };
}
```

## Outputs & Deliverables

The skill generates structured markdown documents:

1. **assessment-report.md** - Project evaluation with scores and recommendations
2. **pitch-deck-outline.md** - 12-slide deck structure with key points per slide
3. **business-plan.md** - Complete business plan (10-15 pages)
4. **valuation-analysis.md** - Multi-method valuation with assumptions and reasoning
5. **investor-matches.md** - Ranked list of investors with match scores and strategy
6. **investment-memo.md** - Professional investment memo for decision-making
7. **dd-checklist.md** - Due diligence checklist (50+ items across categories)

## Architecture

```
src/
├── index.ts                 # Main skill entry point & FAAdvisor class
├── types/                   # TypeScript type definitions
│   ├── project.ts          # Project data structures & enums
│   ├── investor.ts         # Investor database types
│   └── models.ts           # Valuation models & result types
├── modules/
│   ├── assessment/         # Project assessment engine
│   │   └── projectAssessor.ts
│   ├── pitchdeck/          # BP & Pitch deck generation
│   │   └── deckGenerator.ts
│   ├── valuation/          # Financial modeling & valuation
│   │   └── valuationEngine.ts
│   ├── matching/           # Investor-project matching
│   │   └── investorMatcher.ts
│   └── analysis/           # Investment analysis
│       └── investmentAnalyzer.ts
├── data/
│   ├── investors/          # Investor database (JSON)
│   │   └── sample-investors.json
│   ├── templates/          # Document templates
│   └── market/             # Market data & benchmarks
└── utils/                  # Shared utilities
```

## Configuration

The skill can be configured through OpenClaw's workspace settings:

```yaml
# In your OpenClaw workspace config
skills:
  fa-advisor:
    enabled: true
    config:
      # Investor database source
      investorDbPath: "./data/investors"

      # Market data sources (optional)
      marketDataSources:
        - crunchbase
        - pitchbook
        - custom

      # Output preferences
      pitchDeckTemplate: "modern"  # modern, classic, minimal
      language: "zh-CN"            # zh-CN, en-US

      # Advanced features
      enableDeepResearch: true
      enableValuationModel: true
```

## Data Sources

This skill integrates with:

- **Built-in Investor Database**: Sample VC/PE firms with investment preferences
- **Market Data**: Industry reports, market size estimates, competitive intelligence (optional external APIs)
- **Financial Benchmarks**: Public company data, valuation multiples, industry standards

**Note:** Core functionality works without external APIs. Optional integrations with Crunchbase/PitchBook can enhance investor matching accuracy.

## Best Practices

### For Accurate Results

1. **Provide Complete Information**: The more detailed your input, the better the analysis
2. **Be Realistic**: Use actual numbers, not aspirational goals
3. **Update Regularly**: Refresh your data as your company evolves
4. **Compare Multiple Methods**: Valuation uses multiple approaches for balanced view
5. **Iterate**: Use assessment recommendations to improve before pitching

### For Startups

- Use **Quick Assessment** first to identify weaknesses before generating materials
- Generate **Pitch Deck** early to organize your story
- Get **Valuation Analysis** to set realistic expectations
- Use **Investor Matching** to build targeted outreach list
- Prepare for questions the AI identifies in the analysis

### For Investors

- Generate **Investment Memo** to document your thinking
- Use **DD Checklist** to ensure thorough evaluation
- Compare **Valuation** across multiple methods
- Review **Risk Assessment** before proceeding

## Customization

The skill adapts to:

- **Industries**: Enterprise SaaS, Consumer Internet, FinTech, HealthTech, AI/ML, E-commerce, Hardware, and more
- **Stages**: Pre-seed, Seed, Series A/B/C, Growth, Pre-IPO
- **Regions**: North America, Europe, China, Southeast Asia, Global
- **Languages**: English, 中文 (Chinese)

## Limitations & Disclaimers

⚠️ **Important:**

- **Valuation models are estimations** based on market benchmarks and methodologies, not absolute truth
- **Investor data may not be current** - always verify with latest information
- **Not a substitute for professional advice** - consult lawyers, accountants, and advisors for specific situations
- **Results depend on input quality** - garbage in, garbage out
- **Market dynamics matter** - timing, sentiment, and macro conditions affect real outcomes
- **Warm introductions are crucial** - cold outreach success rate is typically low

This tool provides **guidance and structure**, not guarantees. Use it as a starting point for your fundraising journey.

## Privacy & Security

- ✅ **Local Processing**: All analysis runs locally, no data sent to external servers (unless optional APIs enabled)
- ✅ **Your Data Stays Private**: Financial information and pitch materials remain confidential
- ✅ **No Cloud Dependencies**: Core functionality works offline
- ✅ **Suitable for Stealth Mode**: Use before public announcement without disclosure concerns

## Installation

### Via ClawHub (Recommended)

```bash
# Search for the skill
clawhub search fa-advisor

# Install
clawhub install fa-advisor

# Verify installation
openclaw skills list
```

### Via NPM

```bash
npm install @openclaw/skill-fa-advisor
# or
pnpm add @openclaw/skill-fa-advisor
```

### From Source

```bash
# Clone repository
git clone https://github.com/your-org/openclaw-fa-advisor.git
cd openclaw-fa-advisor

# Install dependencies
pnpm install

# Build
pnpm build

# Link to your OpenClaw workspace
ln -s $(pwd) ~/openclaw-workspace/skills/fa-advisor
```

## Development

```bash
# Install dependencies
pnpm install

# Build
pnpm build

# Development mode (watch)
pnpm dev

# Run examples
node examples/basic-usage.ts

# Test
pnpm test

# Lint
pnpm lint
```

## Documentation

- [Quick Start Guide](./QUICKSTART.md) - 5-minute getting started
- [SKILL.md](./SKILL.md) - Agent execution instructions (for OpenClaw)
- [Examples](./examples/) - Code samples and use cases
- [Contributing](./CONTRIBUTING.md) - How to contribute
- [Changelog](./CHANGELOG.md) - Version history
- [Publishing Guide](./PUBLISH.md) - How to publish to ClawHub

## Roadmap

**v0.1.0** (Current)
- [x] Core architecture setup
- [x] Project assessment engine
- [x] Pitch deck & business plan generation
- [x] Multi-method valuation engine (Scorecard, Berkus, Risk Factor, Comparables)
- [x] Investor matching algorithm
- [x] Investment analysis & memo generation

**v0.2.0** (Next)
- [ ] DCF (Discounted Cash Flow) valuation method
- [ ] Enhanced financial modeling with scenarios
- [ ] Integration with Crunchbase API
- [ ] Integration with PitchBook data
- [ ] Expanded investor database (1000+ firms)

**v0.3.0** (Future)
- [ ] Full English language support
- [ ] Multi-language pitch decks (CN/EN)
- [ ] Canvas integration for visual pitch deck rendering
- [ ] Voice interaction for pitch practice mode
- [ ] Real-time market data integration
- [ ] Competitive intelligence module

## Support

- **Documentation**: See [docs](./docs/) directory
- **Examples**: Check [examples/](./examples/) for code samples
- **Issues**: Report bugs at [GitHub Issues](https://github.com/your-org/openclaw-fa-advisor/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/your-org/openclaw-fa-advisor/discussions)
- **OpenClaw Community**: [Discord](https://discord.gg/openclaw)

## License

MIT License - Free for commercial and personal use.

See [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Whether it's:

- 🐛 Bug reports and fixes
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🌍 Translations
- 💡 Ideas and suggestions

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting PRs.

## Acknowledgments

Built with:
- [TypeScript](https://www.typescriptlang.org/) - Type-safe development
- [Zod](https://zod.dev/) - Schema validation
- [OpenClaw](https://openclaw.ai/) - AI agent framework

Inspired by:
- Traditional FA (Financial Advisor) services in primary markets
- Y Combinator startup school materials
- VC investment decision-making frameworks
- Startup valuation methodologies (Berkus, Scorecard, etc.)

## Author

Created for the OpenClaw community.

---

**Ready to start fundraising?** 🚀

Install the skill and ask: *"Help me prepare for Series A fundraising"*
