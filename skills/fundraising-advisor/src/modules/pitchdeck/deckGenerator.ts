import type { Project, PitchDeckOutline } from '../../types/project.js';

/**
 * Pitch Deck 生成器
 * 根据项目信息生成专业的 Pitch Deck 大纲和内容
 */
export class PitchDeckGenerator {
  /**
   * 生成 Pitch Deck 大纲
   */
  async generateOutline(project: Project): Promise<PitchDeckOutline> {
    const slides: PitchDeckOutline['slides'] = [];

    // 1. 封面页
    slides.push({
      number: 1,
      title: project.name,
      type: 'cover',
      keyPoints: [
        project.tagline || project.description.substring(0, 100),
        `${project.fundraising.currentStage} · ${project.industry}`,
        project.location,
      ],
      notes: '简洁有力的封面，包含公司名称、一句话描述、融资阶段',
    });

    // 2. 问题页
    slides.push({
      number: 2,
      title: '问题 / Problem',
      type: 'problem',
      keyPoints: project.product.customerPainPoints.map(p => `• ${p}`),
      notes: '清晰阐述目标客户面临的核心痛点，用数据或故事增强说服力',
    });

    // 3. 解决方案页
    slides.push({
      number: 3,
      title: '解决方案 / Solution',
      type: 'solution',
      keyPoints: [
        `核心方案：${project.product.uniqueValueProposition}`,
        ...project.product.keyFeatures.slice(0, 3).map(f => `• ${f}`),
      ],
      notes: '展示产品如何解决上述问题，强调独特价值主张',
    });

    // 4. 市场机会页
    slides.push({
      number: 4,
      title: '市场机会 / Market Opportunity',
      type: 'market',
      keyPoints: [
        project.market.tam ? `TAM: $${this.formatNumber(project.market.tam)}` : 'TAM: 市场规模待定',
        project.market.sam ? `SAM: $${this.formatNumber(project.market.sam)}` : 'SAM: 可服务市场待定',
        project.market.som ? `SOM: $${this.formatNumber(project.market.som)}` : 'SOM: 可获得市场待定',
        project.market.marketGrowthRate
          ? `市场年增长率: ${(project.market.marketGrowthRate * 100).toFixed(1)}%`
          : '市场增长迅速',
      ],
      notes: '使用TAM-SAM-SOM模型展示市场规模，配合增长趋势数据',
    });

    // 5. 产品展示页
    slides.push({
      number: 5,
      title: '产品 / Product',
      type: 'product',
      keyPoints: [
        `产品阶段：${this.translateProductStage(project.product.stage)}`,
        ...project.product.keyFeatures.map(f => `• ${f}`),
      ],
      notes: '产品截图或演示，突出核心功能和用户体验',
    });

    // 6. 商业模式页
    slides.push({
      number: 6,
      title: '商业模式 / Business Model',
      type: 'business-model',
      keyPoints: [
        `模式：${this.translateBusinessModel(project.businessModel)}`,
        `目标客户：${project.targetMarket}`,
        project.financials.revenue
          ? `当前收入：$${this.formatNumber(project.financials.revenue.current)}`
          : '收入模式验证中',
        project.financials.metrics?.grossMargin
          ? `毛利率：${(project.financials.metrics.grossMargin * 100).toFixed(1)}%`
          : '',
      ].filter(Boolean),
      notes: '清晰说明如何赚钱，客户获取和定价策略',
    });

    // 7. 牵引力/成就页
    if (project.traction) {
      slides.push({
        number: 7,
        title: '牵引力 / Traction',
        type: 'traction',
        keyPoints: [
          project.traction.customers ? `${this.formatNumber(project.traction.customers)}+ 付费客户` : '',
          project.traction.users ? `${this.formatNumber(project.traction.users)}+ 用户` : '',
          project.traction.growth ? `增长：${project.traction.growth}` : '',
          ...(project.traction.partnerships || []).slice(0, 3).map(p => `合作伙伴：${p}`),
          ...(project.traction.awards || []).slice(0, 2).map(a => `获奖：${a}`),
        ].filter(Boolean),
        notes: '用图表展示增长曲线，突出关键里程碑',
      });
    }

    // 8. 竞争格局页
    slides.push({
      number: slides.length + 1,
      title: '竞争格局 / Competition',
      type: 'competition',
      keyPoints: [
        '主要竞争对手：',
        ...project.market.competitors.slice(0, 4).map(c =>
          `• ${c.name}${c.differentiation ? ` - 我们的优势: ${c.differentiation}` : ''}`
        ),
      ],
      notes: '使用竞争矩阵或对比表格，清晰展示差异化优势',
    });

    // 9. 团队页
    slides.push({
      number: slides.length + 1,
      title: '团队 / Team',
      type: 'team',
      keyPoints: [
        ...project.team.founders.map(f =>
          `${f.name} - ${f.title}: ${f.background.substring(0, 80)}`
        ),
        `团队规模：${project.team.teamSize}人`,
        ...(project.team.keyHires || []).slice(0, 2).map(h => `关键岗位：${h}`),
      ],
      notes: '创始人照片 + 核心背景，强调行业经验和互补性',
    });

    // 10. 财务预测页
    if (project.financials.revenue?.projected) {
      slides.push({
        number: slides.length + 1,
        title: '财务预测 / Financials',
        type: 'financials',
        keyPoints: [
          '收入预测：',
          ...project.financials.revenue.projected.slice(0, 3).map(p =>
            `${p.year}年: $${this.formatNumber(p.amount)}`
          ),
          project.financials.metrics?.arr ? `ARR: $${this.formatNumber(project.financials.metrics.arr)}` : '',
          project.financials.metrics?.mrr ? `MRR: $${this.formatNumber(project.financials.metrics.mrr)}` : '',
        ].filter(Boolean),
        notes: '使用柱状图或折线图展示收入增长预测，附关键假设',
      });
    }

    // 11. 融资需求页
    slides.push({
      number: slides.length + 1,
      title: '融资需求 / The Ask',
      type: 'ask',
      keyPoints: [
        `融资阶段：${this.translateFundingStage(project.fundraising.currentStage)}`,
        `融资金额：$${this.formatNumber(project.fundraising.targetAmount)}`,
        project.fundraising.currentValuation
          ? `估值：$${this.formatNumber(project.fundraising.currentValuation)}`
          : '',
        '资金用途：',
        ...project.fundraising.useOfFunds.map(u =>
          `• ${u.category} (${u.percentage}%): ${u.description}`
        ),
      ].filter(Boolean),
      notes: '清晰说明融资金额、估值和具体用途，配合时间线',
    });

    // 12. 愿景页
    slides.push({
      number: slides.length + 1,
      title: '愿景 / Vision',
      type: 'vision',
      keyPoints: [
        '我们的愿景是...',
        '未来3-5年发展规划',
        '潜在退出路径（IPO / M&A）',
      ],
      notes: '描绘公司的长远愿景和对行业的影响',
    });

    return { slides };
  }

  /**
   * 生成详细内容（用于BP文档）
   */
  async generateBusinessPlan(project: Project): Promise<string> {
    const sections: string[] = [];

    // 执行摘要
    sections.push(`# ${project.name} - 商业计划书`);
    sections.push(`\n## 执行摘要\n`);
    sections.push(project.description);
    sections.push(`\n**行业**: ${project.industry}`);
    sections.push(`**商业模式**: ${this.translateBusinessModel(project.businessModel)}`);
    sections.push(`**融资阶段**: ${this.translateFundingStage(project.fundraising.currentStage)}`);
    sections.push(`**融资金额**: $${this.formatNumber(project.fundraising.targetAmount)}`);

    // 问题与解决方案
    sections.push(`\n## 问题与解决方案\n`);
    sections.push(`### 客户痛点\n`);
    project.product.customerPainPoints.forEach(p => {
      sections.push(`- ${p}`);
    });
    sections.push(`\n### 我们的解决方案\n`);
    sections.push(project.product.description);
    sections.push(`\n**独特价值主张**: ${project.product.uniqueValueProposition}\n`);

    // 市场分析
    sections.push(`\n## 市场分析\n`);
    sections.push(`**目标市场**: ${project.targetMarket}\n`);
    if (project.market.tam) {
      sections.push(`- **TAM** (Total Addressable Market): $${this.formatNumber(project.market.tam)}`);
    }
    if (project.market.sam) {
      sections.push(`- **SAM** (Serviceable Addressable Market): $${this.formatNumber(project.market.sam)}`);
    }
    if (project.market.som) {
      sections.push(`- **SOM** (Serviceable Obtainable Market): $${this.formatNumber(project.market.som)}`);
    }
    if (project.market.marketGrowthRate) {
      sections.push(`- **市场增长率**: ${(project.market.marketGrowthRate * 100).toFixed(1)}% CAGR`);
    }

    // 竞争分析
    sections.push(`\n### 竞争格局\n`);
    project.market.competitors.forEach(c => {
      sections.push(`**${c.name}**`);
      if (c.description) sections.push(`  - ${c.description}`);
      if (c.differentiation) sections.push(`  - 我们的差异化: ${c.differentiation}`);
    });

    // 产品
    sections.push(`\n## 产品\n`);
    sections.push(`**当前阶段**: ${this.translateProductStage(project.product.stage)}\n`);
    sections.push(`### 核心功能\n`);
    project.product.keyFeatures.forEach(f => {
      sections.push(`- ${f}`);
    });

    // 商业模式
    sections.push(`\n## 商业模式\n`);
    sections.push(`**模式类型**: ${this.translateBusinessModel(project.businessModel)}`);
    sections.push(`**目标客户**: ${project.targetMarket}`);

    // 团队
    sections.push(`\n## 团队\n`);
    sections.push(`**团队规模**: ${project.team.teamSize}人\n`);
    sections.push(`### 创始团队\n`);
    project.team.founders.forEach(f => {
      sections.push(`**${f.name}** - ${f.title}`);
      sections.push(`${f.background}`);
      if (f.linkedin) sections.push(`[LinkedIn](${f.linkedin})`);
      sections.push('');
    });

    // 财务
    if (project.financials.revenue) {
      sections.push(`\n## 财务状况\n`);
      sections.push(`**当前收入**: $${this.formatNumber(project.financials.revenue.current)}`);

      if (project.financials.revenue.projected.length > 0) {
        sections.push(`\n### 收入预测\n`);
        project.financials.revenue.projected.forEach(p => {
          sections.push(`- ${p.year}年: $${this.formatNumber(p.amount)}`);
        });
      }

      if (project.financials.metrics) {
        sections.push(`\n### 关键指标\n`);
        const m = project.financials.metrics;
        if (m.arr) sections.push(`- ARR: $${this.formatNumber(m.arr)}`);
        if (m.mrr) sections.push(`- MRR: $${this.formatNumber(m.mrr)}`);
        if (m.grossMargin) sections.push(`- 毛利率: ${(m.grossMargin * 100).toFixed(1)}%`);
        if (m.customerAcquisitionCost) sections.push(`- CAC: $${this.formatNumber(m.customerAcquisitionCost)}`);
        if (m.lifetimeValue) sections.push(`- LTV: $${this.formatNumber(m.lifetimeValue)}`);
        if (m.churnRate) sections.push(`- 流失率: ${(m.churnRate * 100).toFixed(1)}%`);
      }
    }

    // 牵引力
    if (project.traction) {
      sections.push(`\n## 市场牵引力\n`);
      const t = project.traction;
      if (t.customers) sections.push(`- **付费客户**: ${this.formatNumber(t.customers)}`);
      if (t.users) sections.push(`- **总用户数**: ${this.formatNumber(t.users)}`);
      if (t.growth) sections.push(`- **增长情况**: ${t.growth}`);

      if (t.partnerships && t.partnerships.length > 0) {
        sections.push(`\n### 战略合作伙伴\n`);
        t.partnerships.forEach(p => sections.push(`- ${p}`));
      }
    }

    // 融资需求
    sections.push(`\n## 融资需求\n`);
    sections.push(`**融资阶段**: ${this.translateFundingStage(project.fundraising.currentStage)}`);
    sections.push(`**融资金额**: $${this.formatNumber(project.fundraising.targetAmount)}`);
    if (project.fundraising.minimumAmount) {
      sections.push(`**最低金额**: $${this.formatNumber(project.fundraising.minimumAmount)}`);
    }
    if (project.fundraising.currentValuation) {
      sections.push(`**当前估值**: $${this.formatNumber(project.fundraising.currentValuation)}`);
    }

    sections.push(`\n### 资金用途\n`);
    project.fundraising.useOfFunds.forEach(u => {
      sections.push(`- **${u.category}** (${u.percentage}%): ${u.description}`);
    });

    // 历史融资
    if (project.fundraising.previousRounds && project.fundraising.previousRounds.length > 0) {
      sections.push(`\n### 历史融资\n`);
      project.fundraising.previousRounds.forEach(r => {
        sections.push(`- **${this.translateFundingStage(r.stage)}** (${r.date}): $${this.formatNumber(r.amount)}`);
        if (r.investors.length > 0) {
          sections.push(`  投资方: ${r.investors.join(', ')}`);
        }
      });
    }

    return sections.join('\n');
  }

  // 辅助方法
  private formatNumber(num: number): string {
    if (num >= 1_000_000_000) {
      return `${(num / 1_000_000_000).toFixed(1)}B`;
    } else if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(1)}M`;
    } else if (num >= 1_000) {
      return `${(num / 1_000).toFixed(1)}K`;
    }
    return num.toString();
  }

  private translateProductStage(stage: string): string {
    const map: Record<string, string> = {
      'idea': '创意阶段',
      'prototype': '原型阶段',
      'mvp': 'MVP阶段',
      'launched': '已上线',
      'scaling': '规模化增长',
    };
    return map[stage] || stage;
  }

  private translateBusinessModel(model: string): string {
    const map: Record<string, string> = {
      'b2b-saas': 'B2B SaaS',
      'b2c': 'B2C',
      'marketplace': '市场平台',
      'platform': '平台型',
      'transaction': '交易型',
      'subscription': '订阅制',
      'freemium': '免费增值',
      'enterprise': '企业服务',
      'hybrid': '混合模式',
    };
    return map[model] || model;
  }

  private translateFundingStage(stage: string): string {
    const map: Record<string, string> = {
      'pre-seed': '天使轮',
      'seed': '种子轮',
      'series-a': 'A轮',
      'series-b': 'B轮',
      'series-c': 'C轮',
      'series-d-plus': 'D轮+',
      'pre-ipo': 'Pre-IPO',
    };
    return map[stage] || stage;
  }
}
