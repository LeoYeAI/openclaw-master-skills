import type { Project } from '../../types/project.js';
import type { InvestmentMemo } from '../../types/investor.js';

/**
 * 投资分析引擎
 * 为投资机构生成投资分析报告和投资备忘录
 */
export class InvestmentAnalyzer {
  /**
   * 生成投资备忘录
   */
  async generateInvestmentMemo(project: Project): Promise<InvestmentMemo> {
    return {
      project: {
        name: project.name,
        industry: project.industry,
        stage: project.fundraising.currentStage,
      },
      executiveSummary: this.generateExecutiveSummary(project),
      investmentHighlights: this.identifyInvestmentHighlights(project),
      marketOpportunity: this.analyzeMarketOpportunity(project),
      competitivePosition: this.analyzeCompetitivePosition(project),
      teamAssessment: this.assessTeam(project),
      financialAnalysis: this.analyzeFinancials(project),
      risks: this.identifyInvestmentRisks(project),
      recommendation: this.generateRecommendation(project),
    };
  }

  /**
   * 生成完整的投资备忘录文档
   */
  async generateMemoDocument(project: Project): Promise<string> {
    const memo = await this.generateInvestmentMemo(project);
    const sections: string[] = [];

    sections.push(`# 投资备忘录: ${memo.project.name}\n`);
    sections.push(`**行业**: ${memo.project.industry}`);
    sections.push(`**阶段**: ${memo.project.stage}`);
    sections.push(`**日期**: ${new Date().toISOString().split('T')[0]}\n`);

    // 执行摘要
    sections.push(`## 执行摘要\n`);
    sections.push(memo.executiveSummary + '\n');

    // 投资亮点
    sections.push(`## 投资亮点\n`);
    memo.investmentHighlights.forEach((h, i) => {
      sections.push(`${i + 1}. ${h}`);
    });
    sections.push('');

    // 市场机会
    sections.push(`## 市场机会\n`);
    sections.push(`**市场规模**: ${memo.marketOpportunity.size}`);
    sections.push(`**市场增长**: ${memo.marketOpportunity.growth}`);
    sections.push(`**市场动态**: ${memo.marketOpportunity.dynamics}\n`);

    // 竞争地位
    sections.push(`## 竞争地位与差异化\n`);
    sections.push(`**核心优势**:`);
    memo.competitivePosition.strengths.forEach(s => sections.push(`- ${s}`));
    sections.push(`\n**需要关注的劣势**:`);
    memo.competitivePosition.weaknesses.forEach(w => sections.push(`- ${w}`));
    sections.push(`\n**差异化策略**: ${memo.competitivePosition.differentiation}\n`);

    // 团队评估
    sections.push(`## 团队评估\n`);
    sections.push(memo.teamAssessment.overview + '\n');
    sections.push(`**团队优势**:`);
    memo.teamAssessment.strengths.forEach(s => sections.push(`- ${s}`));
    if (memo.teamAssessment.gaps.length > 0) {
      sections.push(`\n**团队缺口**:`);
      memo.teamAssessment.gaps.forEach(g => sections.push(`- ${g}`));
    }
    sections.push('');

    // 财务分析
    sections.push(`## 财务分析\n`);
    sections.push(`**当前关键指标**:`);
    for (const [key, value] of Object.entries(memo.financialAnalysis.currentMetrics)) {
      sections.push(`- ${key}: ${value}`);
    }
    sections.push(`\n**财务预测**: ${memo.financialAnalysis.projections}`);
    sections.push(`**估值分析**: ${memo.financialAnalysis.valuation}\n`);

    // 风险分析
    sections.push(`## 风险因素\n`);
    memo.risks.forEach(risk => {
      const severity = risk.severity === 'high' ? '🔴' : risk.severity === 'medium' ? '🟡' : '🟢';
      sections.push(`### ${severity} ${risk.category}\n`);
      sections.push(`**描述**: ${risk.description}`);
      sections.push(`**缓解措施**: ${risk.mitigation}\n`);
    });

    // 投资建议
    sections.push(`## 投资建议\n`);
    const decisionEmoji = {
      'pass': '❌',
      'maybe': '🤔',
      'proceed': '✅',
      'strong-yes': '🌟',
    };
    sections.push(`**决策**: ${decisionEmoji[memo.recommendation.decision]} ${memo.recommendation.decision.toUpperCase()}\n`);
    sections.push(`**理由**: ${memo.recommendation.reasoning}\n`);
    sections.push(`**下一步行动**:`);
    memo.recommendation.nextSteps.forEach(step => sections.push(`- ${step}`));

    return sections.join('\n');
  }

  /**
   * 生成尽职调查清单
   */
  generateDueDiligenceChecklist(project: Project): string[] {
    const checklist: string[] = [];

    // 法律与合规
    checklist.push('## 法律与合规');
    checklist.push('- [ ] 公司注册文件和章程');
    checklist.push('- [ ] 股权结构和cap table');
    checklist.push('- [ ] 所有重大合同（客户、供应商、合作伙伴）');
    checklist.push('- [ ] 知识产权（专利、商标、版权）');
    checklist.push('- [ ] 劳动合同和期权协议');
    checklist.push('- [ ] 合规性文件（许可证、资质）');
    checklist.push('- [ ] 诉讼和纠纷历史');

    // 财务
    checklist.push('\n## 财务');
    checklist.push('- [ ] 过去3年财务报表');
    checklist.push('- [ ] 银行对账单和现金流报表');
    checklist.push('- [ ] 税务申报记录');
    checklist.push('- [ ] 应收账款和应付账款明细');
    checklist.push('- [ ] 收入确认政策');
    checklist.push('- [ ] 财务预测模型和假设');
    checklist.push('- [ ] 之前融资轮次的所有文件');

    // 业务
    checklist.push('\n## 业务');
    checklist.push('- [ ] 商业计划书和pitch deck');
    checklist.push('- [ ] 产品演示和技术文档');
    checklist.push('- [ ] 客户列表和案例研究');
    checklist.push('- [ ] 销售pipeline和CRM数据');
    checklist.push('- [ ] 营销材料和增长策略');
    checklist.push('- [ ] 竞争分析报告');
    checklist.push('- [ ] 市场研究和用户调研');

    // 技术
    checklist.push('\n## 技术');
    checklist.push('- [ ] 技术架构文档');
    checklist.push('- [ ] 代码库审查（code review）');
    checklist.push('- [ ] 技术债务评估');
    checklist.push('- [ ] 安全审计和数据保护');
    checklist.push('- [ ] 第三方依赖和API集成');
    checklist.push('- [ ] 技术路线图');
    checklist.push('- [ ] 基础设施和运维文档');

    // 团队
    checklist.push('\n## 团队与人力资源');
    checklist.push('- [ ] 创始人背景调查（reference check）');
    checklist.push('- [ ] 完整的团队名单和组织架构');
    checklist.push('- [ ] 薪酬和福利体系');
    checklist.push('- [ ] 员工流失率和留存情况');
    checklist.push('- [ ] 招聘计划');
    checklist.push('- [ ] 企业文化和价值观');

    // 客户与市场
    checklist.push('\n## 客户与市场');
    checklist.push('- [ ] 前10大客户访谈');
    checklist.push('- [ ] 客户满意度调查');
    checklist.push('- [ ] 用户留存和流失数据');
    checklist.push('- [ ] NPS（净推荐值）');
    checklist.push('- [ ] 市场定位和品牌认知');

    return checklist;
  }

  // ===== 私有方法 =====

  private generateExecutiveSummary(project: Project): string {
    const parts: string[] = [];

    parts.push(
      `${project.name}是一家${project.industry}领域的${project.fundraising.currentStage}阶段创业公司，` +
      `主要提供${project.product.uniqueValueProposition}。`
    );

    if (project.market.tam) {
      parts.push(
        `公司瞄准的是一个TAM达${this.formatNumber(project.market.tam)}美元的大市场` +
        (project.market.marketGrowthRate
          ? `，年增长率${(project.market.marketGrowthRate * 100).toFixed(0)}%。`
          : '。')
      );
    }

    if (project.team.founders.length > 0) {
      const founderNames = project.team.founders.map(f => f.name).join('、');
      parts.push(`公司由${founderNames}等${project.team.founders.length}位创始人于${project.foundedDate || '近期'}创立。`);
    }

    if (project.traction) {
      if (project.traction.customers && project.traction.customers > 0) {
        parts.push(`目前已服务${project.traction.customers}+付费客户`);
      }
      if (project.traction.users && project.traction.users > 0) {
        parts.push(`，拥有${project.traction.users}+用户`);
      }
    }

    if (project.financials.revenue && project.financials.revenue.current > 0) {
      parts.push(
        `，年收入${this.formatNumber(project.financials.revenue.current)}美元` +
        (project.financials.metrics?.grossMargin
          ? `，毛利率${(project.financials.metrics.grossMargin * 100).toFixed(0)}%。`
          : '。')
      );
    } else {
      parts.push('。');
    }

    parts.push(
      `\n公司正在寻求${this.formatNumber(project.fundraising.targetAmount)}美元的${project.fundraising.currentStage}融资，` +
      `资金主要用于${project.fundraising.useOfFunds.map(u => u.category).slice(0, 3).join('、')}等方面。`
    );

    return parts.join('');
  }

  private identifyInvestmentHighlights(project: Project): string[] {
    const highlights: string[] = [];

    // 市场机会
    if (project.market.tam && project.market.tam >= 10_000_000_000) {
      highlights.push(`巨大的市场机会：TAM超过${this.formatNumber(project.market.tam)}美元`);
    }

    if (project.market.marketGrowthRate && project.market.marketGrowthRate >= 0.2) {
      highlights.push(`高增长市场：年增长率${(project.market.marketGrowthRate * 100).toFixed(0)}%`);
    }

    // 产品与技术
    if (project.product.stage === 'launched' || project.product.stage === 'scaling') {
      highlights.push('产品已推向市场，技术风险较低');
    }

    if (project.product.keyFeatures.length >= 5) {
      highlights.push('产品功能丰富，具备明显的差异化优势');
    }

    // 牵引力
    if (project.traction) {
      if (project.traction.customers && project.traction.customers >= 100) {
        highlights.push(`强劲的市场牵引力：${project.traction.customers}+付费客户`);
      }

      if (project.traction.partnerships && project.traction.partnerships.length >= 3) {
        highlights.push(`建立了多个战略合作伙伴关系，包括${project.traction.partnerships.slice(0, 2).join('、')}等`);
      }
    }

    // 财务
    if (project.financials.revenue && project.financials.revenue.current >= 1_000_000) {
      highlights.push(`年收入${this.formatNumber(project.financials.revenue.current)}美元，商业模式已验证`);
    }

    if (project.financials.metrics) {
      if (project.financials.metrics.grossMargin && project.financials.metrics.grossMargin >= 0.7) {
        highlights.push(`优秀的毛利率：${(project.financials.metrics.grossMargin * 100).toFixed(0)}%`);
      }

      if (project.financials.metrics.lifetimeValue && project.financials.metrics.customerAcquisitionCost) {
        const ratio = project.financials.metrics.lifetimeValue / project.financials.metrics.customerAcquisitionCost;
        if (ratio >= 3) {
          highlights.push(`健康的单位经济模型：LTV/CAC = ${ratio.toFixed(1)}`);
        }
      }
    }

    // 团队
    if (project.team.founders.length >= 2 && project.team.founders.length <= 3) {
      highlights.push('理想的创始团队配置，具备互补技能');
    }

    // 竞争
    if (project.market.competitors.length <= 3) {
      highlights.push('竞争较少，有机会建立市场领导地位');
    }

    // 如果亮点少于3个，添加一些通用亮点
    if (highlights.length < 3) {
      highlights.push(`清晰的价值主张：${project.product.uniqueValueProposition.substring(0, 80)}`);
      highlights.push(`瞄准${project.targetMarket}这一具有增长潜力的市场`);
    }

    return highlights.slice(0, 5); // 最多5个亮点
  }

  private analyzeMarketOpportunity(project: Project): InvestmentMemo['marketOpportunity'] {
    const { market } = project;

    let sizeDescription = '';
    if (market.tam) {
      sizeDescription = `TAM（总体市场规模）约为${this.formatNumber(market.tam)}美元`;
      if (market.sam) {
        sizeDescription += `，SAM（可服务市场）约为${this.formatNumber(market.sam)}美元`;
      }
      if (market.som) {
        sizeDescription += `，SOM（可获得市场）约为${this.formatNumber(market.som)}美元`;
      }
      sizeDescription += '。';
    } else {
      sizeDescription = '市场规模有待进一步量化分析。';
    }

    let growthDescription = '';
    if (market.marketGrowthRate) {
      const rate = (market.marketGrowthRate * 100).toFixed(1);
      if (market.marketGrowthRate >= 0.2) {
        growthDescription = `市场正以年均${rate}%的高速增长，属于快速增长期。`;
      } else if (market.marketGrowthRate >= 0.1) {
        growthDescription = `市场年增长率约${rate}%，保持稳健增长。`;
      } else {
        growthDescription = `市场增长率约${rate}%，相对成熟。`;
      }
    } else {
      growthDescription = '市场增长趋势有待进一步调研。';
    }

    const dynamics = `${project.targetMarket}市场当前有${market.competitors.length}个主要竞争者。` +
      (market.competitors.length <= 3
        ? '市场相对蓝海，有较大发展空间。'
        : market.competitors.length <= 7
        ? '市场竞争适中，需要明确差异化定位。'
        : '市场竞争激烈，需要强大的执行力和资源投入。');

    return {
      size: sizeDescription,
      growth: growthDescription,
      dynamics,
    };
  }

  private analyzeCompetitivePosition(project: Project): InvestmentMemo['competitivePosition'] {
    const strengths: string[] = [];
    const weaknesses: string[] = [];

    // 分析优势
    if (project.product.stage === 'launched' || project.product.stage === 'scaling') {
      strengths.push('产品已推向市场，先发优势明显');
    }

    if (project.traction?.customers && project.traction.customers >= 50) {
      strengths.push('已建立客户基础，形成网络效应');
    }

    if (project.financials.metrics?.grossMargin && project.financials.metrics.grossMargin >= 0.6) {
      strengths.push('高毛利率带来定价能力和盈利空间');
    }

    project.product.keyFeatures.slice(0, 2).forEach(feature => {
      strengths.push(`产品特性：${feature}`);
    });

    // 分析劣势
    if (project.market.competitors.length > 10) {
      weaknesses.push('市场竞争者众多，面临激烈竞争');
    }

    if (!project.traction || (project.traction.customers || 0) < 10) {
      weaknesses.push('市场牵引力有限，需要加速客户获取');
    }

    if (project.team.teamSize < 10) {
      weaknesses.push('团队规模较小，执行能力有待加强');
    }

    const differentiation = project.product.uniqueValueProposition +
      (project.market.competitors.length > 0 && project.market.competitors[0].differentiation
        ? `相比主要竞争对手，${project.market.competitors[0].differentiation}`
        : '');

    return {
      strengths,
      weaknesses,
      differentiation,
    };
  }

  private assessTeam(project: Project): InvestmentMemo['teamAssessment'] {
    const overview = `团队由${project.team.founders.length}位创始人组成，当前团队规模${project.team.teamSize}人。` +
      project.team.founders.map(f => `${f.name}（${f.title}）${f.background.substring(0, 50)}...`).join('；');

    const strengths: string[] = [];
    const gaps: string[] = [];

    // 团队优势
    if (project.team.founders.length >= 2 && project.team.founders.length <= 3) {
      strengths.push('创始团队规模合理，便于决策和执行');
    }

    if (project.team.founders.some(f =>
      f.background.toLowerCase().includes('experience') ||
      f.background.toLowerCase().includes('founder')
    )) {
      strengths.push('创始人具备相关行业经验或创业经验');
    }

    if (project.team.teamSize >= 10) {
      strengths.push('团队已具备一定规模，组织能力初步形成');
    }

    // 团队缺口
    if (project.team.founders.length === 1) {
      gaps.push('单一创始人，建议引入联合创始人分担风险');
    }

    if (project.team.teamSize < 5) {
      gaps.push('团队规模较小，需要快速扩充核心岗位');
    }

    if (!project.team.keyHires || project.team.keyHires.length === 0) {
      gaps.push('缺少关键岗位招聘计划说明');
    }

    return {
      overview,
      strengths,
      gaps,
    };
  }

  private analyzeFinancials(project: Project): InvestmentMemo['financialAnalysis'] {
    const currentMetrics: Record<string, any> = {};

    if (project.financials.revenue) {
      currentMetrics['当前收入'] = `$${this.formatNumber(project.financials.revenue.current)}`;
    } else {
      currentMetrics['当前收入'] = 'Pre-revenue';
    }

    if (project.financials.metrics) {
      const m = project.financials.metrics;
      if (m.arr) currentMetrics['ARR'] = `$${this.formatNumber(m.arr)}`;
      if (m.mrr) currentMetrics['MRR'] = `$${this.formatNumber(m.mrr)}`;
      if (m.grossMargin) currentMetrics['毛利率'] = `${(m.grossMargin * 100).toFixed(0)}%`;
      if (m.customerAcquisitionCost) currentMetrics['CAC'] = `$${this.formatNumber(m.customerAcquisitionCost)}`;
      if (m.lifetimeValue) currentMetrics['LTV'] = `$${this.formatNumber(m.lifetimeValue)}`;
      if (m.churnRate) currentMetrics['月流失率'] = `${(m.churnRate * 100).toFixed(1)}%`;
    }

    if (project.financials.expenses) {
      currentMetrics['月消耗'] = `$${this.formatNumber(project.financials.expenses.monthly)}`;
      currentMetrics['跑道'] = `${project.financials.expenses.runway}个月`;
    }

    let projections = '财务预测';
    if (project.financials.revenue?.projected && project.financials.revenue.projected.length > 0) {
      projections = '未来收入预测：' +
        project.financials.revenue.projected
          .slice(0, 3)
          .map(p => `${p.year}年$${this.formatNumber(p.amount)}`)
          .join(', ');
    } else {
      projections = '需要提供详细的财务预测模型';
    }

    let valuation = '估值';
    if (project.fundraising.currentValuation) {
      valuation = `当前融资估值：$${this.formatNumber(project.fundraising.currentValuation)}`;
    } else {
      valuation = '估值待协商，建议使用多种估值方法综合确定';
    }

    return {
      currentMetrics,
      projections,
      valuation,
    };
  }

  private identifyInvestmentRisks(project: Project): InvestmentMemo['risks'] {
    const risks: InvestmentMemo['risks'] = [];

    // 市场风险
    if (project.market.competitors.length > 10) {
      risks.push({
        category: '市场竞争风险',
        description: '市场竞争激烈，存在多个成熟竞争对手',
        severity: 'high',
        mitigation: '聚焦细分市场，建立差异化优势和护城河',
      });
    }

    // 执行风险
    if (project.team.founders.length === 1) {
      risks.push({
        category: '团队风险',
        description: '单一创始人，关键人物依赖度高',
        severity: 'high',
        mitigation: '引入联合创始人，建立继任计划',
      });
    }

    // 财务风险
    if (!project.financials.revenue || project.financials.revenue.current === 0) {
      risks.push({
        category: '收入风险',
        description: '尚未产生收入，商业模式未经验证',
        severity: 'medium',
        mitigation: '尽快获取付费客户，证明产品市场契合度',
      });
    }

    if (project.financials.expenses && project.financials.expenses.runway < 6) {
      risks.push({
        category: '现金流风险',
        description: `现金跑道不足6个月（剩余${project.financials.expenses.runway}个月）`,
        severity: 'high',
        mitigation: '立即启动融资，同时控制开支延长跑道',
      });
    }

    // 产品风险
    if (project.product.stage === 'idea' || project.product.stage === 'prototype') {
      risks.push({
        category: '产品风险',
        description: '产品尚在早期阶段，技术和市场验证不足',
        severity: 'high',
        mitigation: '加快产品开发，尽早推向市场获取反馈',
      });
    }

    // 规模化风险
    if (!project.traction || (project.traction.customers || 0) < 10) {
      risks.push({
        category: '规模化风险',
        description: '缺乏足够的市场牵引力，规模化路径不明确',
        severity: 'medium',
        mitigation: '优化用户获取策略，建立可持续的增长引擎',
      });
    }

    return risks;
  }

  private generateRecommendation(project: Project): InvestmentMemo['recommendation'] {
    // 简单的评分逻辑
    let score = 0;

    // 市场 (0-30)
    if (project.market.tam && project.market.tam >= 10_000_000_000) score += 30;
    else if (project.market.tam && project.market.tam >= 1_000_000_000) score += 20;
    else score += 10;

    // 团队 (0-25)
    if (project.team.founders.length >= 2 && project.team.founders.length <= 3) score += 25;
    else if (project.team.founders.length >= 2) score += 15;
    else score += 5;

    // 产品 (0-20)
    const productScores: Record<string, number> = {
      'idea': 5,
      'prototype': 10,
      'mvp': 15,
      'launched': 18,
      'scaling': 20,
    };
    score += productScores[project.product.stage] || 10;

    // 牵引力 (0-15)
    if (project.traction?.customers && project.traction.customers >= 100) score += 15;
    else if (project.traction?.customers && project.traction.customers >= 10) score += 10;
    else score += 2;

    // 财务 (0-10)
    if (project.financials.revenue && project.financials.revenue.current >= 1_000_000) score += 10;
    else if (project.financials.revenue && project.financials.revenue.current > 0) score += 5;

    // 决策
    let decision: InvestmentMemo['recommendation']['decision'];
    let reasoning: string;
    let nextSteps: string[];

    if (score >= 80) {
      decision = 'strong-yes';
      reasoning = '项目在市场、团队、产品和牵引力等多个维度表现优秀，具有很高的投资价值。建议快速推进到下一阶段。';
      nextSteps = [
        '安排与创始团队的深度访谈',
        '进行客户访谈和市场调研',
        '启动法律和财务尽职调查',
        '准备投资条款清单（Term Sheet）',
      ];
    } else if (score >= 65) {
      decision = 'proceed';
      reasoning = '项目整体质量良好，值得进一步尽职调查。需要重点关注某些领域的风险。';
      nextSteps = [
        '深入了解团队背景和执行能力',
        '验证市场规模和增长假设',
        '评估竞争格局和差异化优势',
        '审查财务模型和关键假设',
      ];
    } else if (score >= 45) {
      decision = 'maybe';
      reasoning = '项目有一定潜力，但存在明显的风险点和不确定性。可以继续观察，但不建议立即投资。';
      nextSteps = [
        '要求创业团队提供更详细的信息',
        '等待项目在关键指标上取得进展',
        '评估是否符合我们的风险偏好',
        '考虑小额跟投或可转债等灵活结构',
      ];
    } else {
      decision = 'pass';
      reasoning = '项目当前阶段风险较高，不符合我们的投资标准。建议暂时放弃，未来可以继续关注。';
      nextSteps = [
        '礼貌回复创业团队说明原因',
        '建议团队在特定方面改进后再联系',
        '将项目加入观察名单定期review',
      ];
    }

    return {
      decision,
      reasoning,
      nextSteps,
    };
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
    return num.toFixed(0);
  }
}
