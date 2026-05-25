# 快速开始指南

## 5分钟上手FA Advisor

### 1. 安装

```bash
npm install @openclaw/skill-fa-advisor
# 或
pnpm add @openclaw/skill-fa-advisor
```

### 2. 基础使用

```typescript
import FAAdvisor from '@openclaw/skill-fa-advisor';
import type { Project } from '@openclaw/skill-fa-advisor';

// 创建advisor实例
const advisor = new FAAdvisor();

// 定义你的项目
const myProject: Project = {
  name: '你的公司名称',
  description: '公司简介',
  industry: 'enterprise-software',
  businessModel: 'b2b-saas',
  location: '北京, 中国',
  targetMarket: '中大型企业',

  product: {
    description: '产品描述',
    stage: 'launched',
    keyFeatures: ['功能1', '功能2', '功能3'],
    uniqueValueProposition: '独特价值主张',
    customerPainPoints: ['痛点1', '痛点2'],
  },

  market: {
    tam: 10_000_000_000, // $10B
    marketGrowthRate: 0.3, // 30%
    competitors: [
      { name: '竞品A', description: '描述' }
    ],
  },

  team: {
    founders: [
      {
        name: '创始人姓名',
        title: 'CEO',
        background: '背景介绍'
      }
    ],
    teamSize: 10,
  },

  financials: {
    revenue: {
      current: 500_000,
      projected: [
        { year: 2024, amount: 2_000_000 }
      ]
    },
    expenses: {
      monthly: 50_000,
      runway: 12
    },
  },

  fundraising: {
    currentStage: 'seed',
    targetAmount: 3_000_000,
    useOfFunds: [
      { category: '产品开发', percentage: 50, description: '招聘工程师' },
      { category: '市场推广', percentage: 30, description: '品牌建设' },
      { category: '运营', percentage: 20, description: '日常开支' }
    ]
  }
};

// 快速评估
const assessment = await advisor.quickAssessment(myProject);

// 生成pitch deck
const pitchDeck = await advisor.generatePitchDeck(myProject);

// 估值分析
const valuation = await advisor.valuate(myProject);
console.log(`估值: $${valuation.recommendedValuation.preMoney}`);
```

### 3. 创业公司完整服务

```typescript
// 一次性获取所有融资材料
const fullPackage = await advisor.startupPackage(myProject);

console.log('评估得分:', fullPackage.assessment.scores.overall);
console.log('推荐估值:', fullPackage.valuation.recommendedValuation.preMoney);
console.log('匹配投资人:', fullPackage.investorMatches.length);
console.log('Pitch Deck:', fullPackage.pitchDeck.slides.length, '页');

// 保存结果
import fs from 'fs/promises';
await fs.writeFile('business-plan.md', fullPackage.businessPlan);
await fs.writeFile('investor-outreach.md', fullPackage.outreachStrategy);
```

### 4. 投资人分析

```typescript
// 从投资人角度分析项目
const investorView = await advisor.investorPackage(myProject);

console.log('投资建议:', investorView.memo.recommendation.decision);
console.log('投资亮点:', investorView.memo.investmentHighlights);
console.log('风险:', investorView.memo.risks);

// 保存投资备忘录
await fs.writeFile('investment-memo.md', investorView.memoDocument);
```

### 5. 在OpenClaw中使用

如果你在OpenClaw环境中：

```bash
# 通过对话使用
"评估我的项目投资价值"
"生成一份pitch deck"
"推荐适合的投资机构"
"做一个估值分析"
```

## 常见场景

### 场景1: 准备融资材料

```typescript
const advisor = new FAAdvisor();

// 1. 先做评估，了解项目状态
const assessment = await advisor.quickAssessment(myProject);

if (assessment.investmentReadiness === 'ready' ||
    assessment.investmentReadiness === 'highly-ready') {

  // 2. 生成pitch deck
  const deck = await advisor.generatePitchDeck(myProject);

  // 3. 生成BP
  const bp = await advisor.generateBusinessPlan(myProject);

  // 4. 估值分析
  const valuation = await advisor.valuate(myProject);

  // 5. 匹配投资人
  const matches = await advisor.matchInvestors(myProject);

  console.log('✅ 融资材料准备完毕！');
} else {
  console.log('⚠️ 建议先改进以下方面:');
  assessment.recommendations.forEach(r => console.log(`- ${r}`));
}
```

### 场景2: 投资机构评估项目

```typescript
const advisor = new FAAdvisor();

// 生成投资备忘录
const memo = await advisor.analyzeForInvestor(myProject);

// 决策
switch(memo.recommendation.decision) {
  case 'strong-yes':
    console.log('🌟 强烈推荐投资');
    break;
  case 'proceed':
    console.log('✅ 可以推进DD');
    break;
  case 'maybe':
    console.log('🤔 需要更多信息');
    break;
  case 'pass':
    console.log('❌ 建议pass');
    break;
}

console.log('\n下一步行动:');
memo.recommendation.nextSteps.forEach(step => {
  console.log(`- ${step}`);
});
```

### 场景3: 只需要估值

```typescript
const advisor = new FAAdvisor();
const valuation = await advisor.valuate(myProject);

console.log('估值分析结果:');
console.log(`推荐估值: $${formatNumber(valuation.recommendedValuation.preMoney)}`);

console.log('\n各方法估值:');
valuation.valuationByMethod.forEach(method => {
  console.log(`${method.method}: $${formatNumber(method.valuation)}`);
});
```

## 下一步

- 查看 [完整文档](./README.md)
- 浏览 [使用示例](./examples/)
- 了解 [API参考](./README.md#api)
- 参与 [贡献](./CONTRIBUTING.md)

## 获取帮助

- GitHub Issues: 报告bug或请求功能
- Discussions: 提问和讨论
- Examples: 查看更多示例代码

祝融资顺利！🚀
