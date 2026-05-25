/**
 * Basic usage examples for FA Advisor skill
 */

import FAAdvisor from '../src/index.js';
import type { Project } from '../src/types/project.js';
import type { Investor } from '../src/types/investor.js';
import sampleInvestors from '../src/data/investors/sample-investors.json' assert { type: 'json' };

// Example startup project
const sampleProject: Project = {
  name: 'CloudFlow AI',
  tagline: '企业级AI工作流自动化平台',
  description: 'CloudFlow AI是一个面向企业的AI驱动的工作流自动化平台，帮助企业通过自然语言快速构建、部署和管理复杂的业务流程自动化。',
  foundedDate: '2023-06',
  location: '上海, 中国',
  website: 'https://cloudflow-ai.example.com',

  industry: 'enterprise-software',
  subIndustry: 'workflow-automation',
  businessModel: 'b2b-saas',
  targetMarket: '中大型企业的IT和运营团队',

  product: {
    description: '一站式AI工作流平台，通过自然语言交互，让非技术人员也能轻松构建自动化流程',
    stage: 'launched',
    keyFeatures: [
      '自然语言流程构建',
      'AI驱动的流程优化建议',
      '支持100+企业应用集成',
      '可视化流程编辑器',
      '实时监控和分析'
    ],
    uniqueValueProposition: '相比传统RPA工具降低90%实施成本，提升10倍开发效率',
    customerPainPoints: [
      '传统RPA工具实施成本高、周期长',
      '需要专业技术人员才能配置',
      '系统集成复杂，维护困难'
    ],
  },

  market: {
    tam: 50_000_000_000, // $50B
    sam: 10_000_000_000, // $10B
    som: 500_000_000,    // $500M
    marketGrowthRate: 0.35, // 35% CAGR
    competitors: [
      {
        name: 'UiPath',
        description: '全球领先的RPA平台',
        differentiation: '我们专注于AI原生设计，更易用且成本更低'
      },
      {
        name: 'Automation Anywhere',
        description: '企业RPA解决方案',
        differentiation: '我们提供无代码体验，降低使用门槛'
      },
      {
        name: 'Zapier',
        description: '面向中小企业的自动化工具',
        differentiation: '我们专注企业级需求，提供更强的安全性和可扩展性'
      }
    ],
  },

  team: {
    founders: [
      {
        name: '张明',
        title: 'CEO & Co-founder',
        background: '前阿里巴巴高级技术专家，10年企业软件经验，曾负责钉钉工作流引擎',
        linkedin: 'https://linkedin.com/in/example'
      },
      {
        name: '李华',
        title: 'CTO & Co-founder',
        background: '前华为AI实验室负责人，AI领域专家，发表过多篇顶会论文',
        linkedin: 'https://linkedin.com/in/example2'
      }
    ],
    teamSize: 25,
    keyHires: ['VP of Sales', 'Head of Customer Success']
  },

  financials: {
    revenue: {
      current: 1_200_000, // $1.2M ARR
      projected: [
        { year: 2024, amount: 3_000_000 },
        { year: 2025, amount: 8_000_000 },
        { year: 2026, amount: 20_000_000 }
      ]
    },
    expenses: {
      monthly: 150_000,
      runway: 18
    },
    metrics: {
      arr: 1_200_000,
      mrr: 100_000,
      grossMargin: 0.85,
      customerAcquisitionCost: 8_000,
      lifetimeValue: 36_000,
      churnRate: 0.03
    }
  },

  fundraising: {
    currentStage: 'series-a',
    targetAmount: 10_000_000,
    minimumAmount: 8_000_000,
    currentValuation: 40_000_000,
    previousRounds: [
      {
        stage: 'seed',
        amount: 2_000_000,
        date: '2023-08',
        investors: ['经纬中国', '真格基金'],
        valuation: 10_000_000
      }
    ],
    useOfFunds: [
      {
        category: '产品研发',
        percentage: 40,
        description: '扩充工程团队，加强AI能力和企业集成'
      },
      {
        category: '市场销售',
        percentage: 35,
        description: '建立销售团队，拓展企业客户'
      },
      {
        category: '运营支出',
        percentage: 15,
        description: '日常运营和管理'
      },
      {
        category: '储备金',
        percentage: 10,
        description: '应急储备'
      }
    ]
  },

  traction: {
    customers: 45,
    users: 2_500,
    growth: '月环比增长 40%',
    partnerships: ['钉钉', '企业微信', '飞书'],
    awards: ['36氪WISE 2023最具潜力企业', 'TechCrunch Disrupt入围'],
    press: ['36氪', 'TechCrunch', '雷锋网']
  }
};

/**
 * Example 1: Complete startup package
 */
async function example1_StartupPackage() {
  console.log('='.repeat(70));
  console.log('Example 1: Complete Startup Fundraising Package');
  console.log('='.repeat(70));

  const advisor = new FAAdvisor(sampleInvestors as Investor[]);
  const result = await advisor.startupPackage(sampleProject);

  console.log('\n📊 Assessment Summary:');
  console.log(`Overall Score: ${result.assessment.scores.overall}/100`);
  console.log(`Investment Readiness: ${result.assessment.investmentReadiness}`);

  console.log('\n💰 Valuation:');
  console.log(`Pre-money: $${formatNumber(result.valuation.recommendedValuation.preMoney)}`);
  console.log(`Post-money: $${formatNumber(result.valuation.recommendedValuation.postMoney)}`);

  console.log('\n🎯 Top 5 Matched Investors:');
  result.investorMatches.slice(0, 5).forEach((match, i) => {
    console.log(`${i + 1}. ${match.investor.name} - Match Score: ${match.matchScore}/100`);
  });

  console.log('\n📝 Pitch Deck:');
  console.log(`Generated ${result.pitchDeck.slides.length} slides`);
  result.pitchDeck.slides.slice(0, 3).forEach(slide => {
    console.log(`  - Slide ${slide.number}: ${slide.title}`);
  });

  // Save results (in real app)
  // await fs.writeFile('pitch-deck-outline.json', JSON.stringify(result.pitchDeck, null, 2));
  // await fs.writeFile('business-plan.md', result.businessPlan);
  // await fs.writeFile('investor-outreach.md', result.outreachStrategy);
}

/**
 * Example 2: Quick assessment only
 */
async function example2_QuickAssessment() {
  console.log('\n' + '='.repeat(70));
  console.log('Example 2: Quick Assessment');
  console.log('='.repeat(70));

  const advisor = new FAAdvisor();
  await advisor.quickAssessment(sampleProject);
}

/**
 * Example 3: Investor analysis package
 */
async function example3_InvestorPackage() {
  console.log('\n' + '='.repeat(70));
  console.log('Example 3: Investor Analysis Package');
  console.log('='.repeat(70));

  const advisor = new FAAdvisor();
  const result = await advisor.investorPackage(sampleProject);

  console.log('\n📝 Investment Memo:');
  console.log(`Decision: ${result.memo.recommendation.decision.toUpperCase()}`);
  console.log(`\nHighlights:`);
  result.memo.investmentHighlights.slice(0, 3).forEach(h => {
    console.log(`  - ${h}`);
  });

  console.log(`\nKey Risks:`);
  result.memo.risks.slice(0, 3).forEach(r => {
    console.log(`  - [${r.severity.toUpperCase()}] ${r.category}: ${r.description}`);
  });

  console.log('\n✅ Due Diligence Checklist:');
  console.log(`${result.ddChecklist.length} items`);

  // Save full memo
  // await fs.writeFile('investment-memo.md', result.memoDocument);
}

/**
 * Example 4: Individual operations
 */
async function example4_IndividualOperations() {
  console.log('\n' + '='.repeat(70));
  console.log('Example 4: Individual Operations');
  console.log('='.repeat(70));

  const advisor = new FAAdvisor(sampleInvestors as Investor[]);

  // Just valuation
  console.log('\n💰 Valuation Only:');
  const valuation = await advisor.valuate(sampleProject);
  console.log(`Recommended valuation: $${formatNumber(valuation.recommendedValuation.preMoney)}`);
  console.log(`Methods used: ${valuation.valuationByMethod.map(v => v.method).join(', ')}`);

  // Just investor matching
  console.log('\n🎯 Investor Matching Only:');
  const matches = await advisor.matchInvestors(sampleProject, 10);
  console.log(`Found ${matches.length} matches`);
  console.log(`Top match: ${matches[0].investor.name} (${matches[0].matchScore}/100)`);

  // Just pitch deck
  console.log('\n📑 Pitch Deck Only:');
  const deck = await advisor.generatePitchDeck(sampleProject);
  console.log(`Generated ${deck.slides.length}-slide deck`);
}

// Helper function
function formatNumber(num: number): string {
  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(1)}B`;
  } else if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  } else if (num >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return num.toString();
}

// Run examples
async function main() {
  await example1_StartupPackage();
  await example2_QuickAssessment();
  await example3_InvestorPackage();
  await example4_IndividualOperations();

  console.log('\n' + '='.repeat(70));
  console.log('✅ All examples completed!');
  console.log('='.repeat(70));
}

// Execute if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { sampleProject };
