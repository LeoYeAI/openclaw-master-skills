import type { Project } from '../../types/project.js';
import type {
  ValuationMethod,
  ValuationResult,
  ComprehensiveValuation,
  FinancialProjection,
  DealStructure,
} from '../../types/models.js';

/**
 * 估值引擎
 * 使用多种方法对创业公司进行估值
 */
export class ValuationEngine {
  /**
   * 综合估值分析
   */
  async comprehensiveValuation(project: Project): Promise<ComprehensiveValuation> {
    const valuationMethods: ValuationResult[] = [];

    // 应用不同估值方法
    valuationMethods.push(await this.scorecardMethod(project));
    valuationMethods.push(await this.berkusMethod(project));
    valuationMethods.push(await this.riskFactorMethod(project));

    if (project.financials.revenue && project.financials.revenue.current > 0) {
      valuationMethods.push(await this.comparableMethod(project));
    }

    // 计算推荐估值（加权平均）
    const recommendedValuation = this.calculateWeightedValuation(valuationMethods, project);

    // 获取基准数据
    const benchmarkData = this.getBenchmarkData(project);

    // 生成交易条款建议
    const dealTerms = this.suggestDealTerms(project, recommendedValuation.preMoney);

    return {
      recommendedValuation,
      valuationByMethod: valuationMethods,
      benchmarkData,
      dealTerms,
      analysis: this.generateAnalysis(project, recommendedValuation, valuationMethods),
      risks: this.identifyValuationRisks(project, valuationMethods),
    };
  }

  /**
   * 记分卡法 (Scorecard Method)
   * 适用于早期创业公司
   */
  private async scorecardMethod(project: Project): Promise<ValuationResult> {
    // 基准估值（根据地区和行业）
    const baselineValuation = this.getBaselineValuation(project);

    // 评分因素及权重
    const factors = {
      team: { weight: 0.30, score: 0 },
      market: { weight: 0.25, score: 0 },
      product: { weight: 0.15, score: 0 },
      competition: { weight: 0.10, score: 0 },
      marketing: { weight: 0.10, score: 0 },
      funding: { weight: 0.05, score: 0 },
      other: { weight: 0.05, score: 0 },
    };

    // 团队评分 (0-150%)
    const founderCount = project.team.founders.length;
    const hasExperience = project.team.founders.some(f =>
      f.background.toLowerCase().includes('experience') ||
      f.background.toLowerCase().includes('founder')
    );

    if (founderCount >= 2 && founderCount <= 3 && hasExperience) {
      factors.team.score = 130;
    } else if (founderCount >= 2) {
      factors.team.score = 110;
    } else {
      factors.team.score = 80;
    }

    // 市场评分 (0-150%)
    if (project.market.tam && project.market.tam >= 10_000_000_000) {
      factors.market.score = 140;
    } else if (project.market.tam && project.market.tam >= 1_000_000_000) {
      factors.market.score = 120;
    } else {
      factors.market.score = 90;
    }

    // 产品评分 (0-150%)
    const productStageScores = {
      'idea': 70,
      'prototype': 90,
      'mvp': 110,
      'launched': 130,
      'scaling': 150,
    };
    factors.product.score = productStageScores[project.product.stage] || 100;

    // 竞争评分 (0-150%)
    const competitorCount = project.market.competitors.length;
    if (competitorCount <= 3) {
      factors.competition.score = 130;
    } else if (competitorCount <= 7) {
      factors.competition.score = 100;
    } else {
      factors.competition.score = 80;
    }

    // 市场营销/牵引力评分 (0-150%)
    if (project.traction) {
      if (project.traction.customers && project.traction.customers >= 100) {
        factors.marketing.score = 140;
      } else if (project.traction.customers && project.traction.customers >= 10) {
        factors.marketing.score = 120;
      } else if (project.traction.users && project.traction.users >= 1000) {
        factors.marketing.score = 110;
      } else {
        factors.marketing.score = 90;
      }
    } else {
      factors.marketing.score = 80;
    }

    // 融资需求评分 (0-150%)
    factors.funding.score = 100;

    // 其他因素 (0-150%)
    factors.other.score = 100;

    // 计算加权调整系数
    let adjustmentFactor = 0;
    for (const [key, factor] of Object.entries(factors)) {
      adjustmentFactor += (factor.score / 100) * factor.weight;
    }

    const valuation = Math.round(baselineValuation * adjustmentFactor);

    return {
      method: 'scorecard' as ValuationMethod,
      valuation,
      range: {
        low: Math.round(valuation * 0.7),
        mid: valuation,
        high: Math.round(valuation * 1.3),
      },
      assumptions: [
        {
          key: '基准估值',
          value: baselineValuation,
          rationale: `基于${project.location}地区${project.industry}行业的${project.fundraising.currentStage}阶段基准`,
        },
        {
          key: '团队因素',
          value: `${factors.team.score}%`,
          rationale: `${founderCount}位创始人，${hasExperience ? '具备' : '缺乏'}相关经验`,
        },
        {
          key: '市场因素',
          value: `${factors.market.score}%`,
          rationale: `TAM ${project.market.tam ? '$' + this.formatNumber(project.market.tam) : '未知'}`,
        },
        {
          key: '产品因素',
          value: `${factors.product.score}%`,
          rationale: `产品处于${project.product.stage}阶段`,
        },
        {
          key: '综合调整系数',
          value: adjustmentFactor.toFixed(2),
          rationale: '各因素加权平均',
        },
      ],
    };
  }

  /**
   * Berkus法
   * 适用于Pre-Revenue早期公司
   */
  private async berkusMethod(project: Project): Promise<ValuationResult> {
    // Berkus法：5个关键要素，每个最高500K
    const maxPerFactor = 500_000;
    let valuation = 0;

    const factors: Array<{ key: string; value: number; rationale: string }> = [];

    // 1. 好的创意/基本价值 (0-500K)
    const ideaValue = project.product.uniqueValueProposition.length > 50 ? maxPerFactor : maxPerFactor * 0.6;
    valuation += ideaValue;
    factors.push({
      key: '创意价值',
      value: ideaValue,
      rationale: '独特价值主张的清晰度和吸引力',
    });

    // 2. 原型/技术风险降低 (0-500K)
    const prototypeScores = {
      'idea': 0,
      'prototype': maxPerFactor * 0.4,
      'mvp': maxPerFactor * 0.7,
      'launched': maxPerFactor,
      'scaling': maxPerFactor,
    };
    const prototypeValue = prototypeScores[project.product.stage] || 0;
    valuation += prototypeValue;
    factors.push({
      key: '产品/技术',
      value: prototypeValue,
      rationale: `产品${project.product.stage}阶段的技术风险评估`,
    });

    // 3. 优质管理团队 (0-500K)
    const teamQuality = project.team.founders.length >= 2 ? maxPerFactor * 0.8 : maxPerFactor * 0.5;
    valuation += teamQuality;
    factors.push({
      key: '管理团队',
      value: teamQuality,
      rationale: `${project.team.founders.length}位创始人，团队${project.team.teamSize}人`,
    });

    // 4. 战略关系/市场风险降低 (0-500K)
    const hasPartnerships = project.traction?.partnerships && project.traction.partnerships.length > 0;
    const relationshipValue = hasPartnerships ? maxPerFactor * 0.7 : maxPerFactor * 0.3;
    valuation += relationshipValue;
    factors.push({
      key: '战略关系',
      value: relationshipValue,
      rationale: hasPartnerships ? `已建立${project.traction!.partnerships!.length}个战略合作` : '战略关系待建立',
    });

    // 5. 产品推出/销售风险降低 (0-500K)
    let salesValue = 0;
    if (project.traction?.customers && project.traction.customers >= 10) {
      salesValue = maxPerFactor;
    } else if (project.traction?.customers && project.traction.customers > 0) {
      salesValue = maxPerFactor * 0.6;
    } else if (project.product.stage === 'launched') {
      salesValue = maxPerFactor * 0.3;
    }
    valuation += salesValue;
    factors.push({
      key: '产品推出/销售',
      value: salesValue,
      rationale: project.traction?.customers
        ? `${project.traction.customers}个付费客户`
        : '销售尚未验证',
    });

    valuation = Math.round(valuation);

    return {
      method: 'berkus' as ValuationMethod,
      valuation,
      range: {
        low: Math.round(valuation * 0.8),
        mid: valuation,
        high: Math.round(valuation * 1.2),
      },
      assumptions: factors,
    };
  }

  /**
   * 风险因素总和法 (Risk Factor Summation Method)
   */
  private async riskFactorMethod(project: Project): Promise<ValuationResult> {
    // 基准估值
    const baseValuation = this.getBaselineValuation(project);

    // 12个风险因素，每个从-2到+2
    const risks = {
      management: 0, // 管理风险
      stage: 0, // 阶段风险
      legislation: 0, // 政策/法律风险
      manufacturing: 0, // 生产风险
      sales: 0, // 销售/市场风险
      funding: 0, // 资金风险
      competition: 0, // 竞争风险
      technology: 0, // 技术风险
      litigation: 0, // 诉讼风险
      international: 0, // 国际风险
      reputation: 0, // 声誉风险
      exit: 0, // 退出风险
    };

    // 评估各项风险
    // 管理风险
    if (project.team.founders.length >= 2 && project.team.founders.length <= 3) {
      risks.management = 1;
    } else if (project.team.founders.length === 1) {
      risks.management = -1;
    }

    // 阶段风险
    const stageRisks: Record<string, number> = {
      'idea': -2,
      'prototype': -1,
      'mvp': 0,
      'launched': 1,
      'scaling': 2,
    };
    risks.stage = stageRisks[project.product.stage] || 0;

    // 销售/市场风险
    if (project.traction?.customers && project.traction.customers >= 100) {
      risks.sales = 2;
    } else if (project.traction?.customers && project.traction.customers >= 10) {
      risks.sales = 1;
    } else if (!project.traction?.customers) {
      risks.sales = -2;
    }

    // 资金风险
    if (project.financials.expenses && project.financials.expenses.runway >= 12) {
      risks.funding = 1;
    } else if (project.financials.expenses && project.financials.expenses.runway < 6) {
      risks.funding = -2;
    }

    // 竞争风险
    if (project.market.competitors.length <= 3) {
      risks.competition = 1;
    } else if (project.market.competitors.length >= 10) {
      risks.competition = -1;
    }

    // 技术风险
    if (project.product.stage === 'launched' || project.product.stage === 'scaling') {
      risks.technology = 1;
    } else if (project.product.stage === 'idea') {
      risks.technology = -1;
    }

    // 计算总风险调整
    const totalRiskAdjustment = Object.values(risks).reduce((sum, r) => sum + r, 0);
    const adjustmentPerFactor = baseValuation * 0.025; // 每个风险因素±2.5%
    const valuation = Math.round(baseValuation + (totalRiskAdjustment * adjustmentPerFactor));

    return {
      method: 'risk-factor' as ValuationMethod,
      valuation,
      range: {
        low: Math.round(valuation * 0.75),
        mid: valuation,
        high: Math.round(valuation * 1.25),
      },
      assumptions: [
        {
          key: '基准估值',
          value: baseValuation,
          rationale: '行业和阶段基准',
        },
        {
          key: '风险调整总分',
          value: totalRiskAdjustment,
          rationale: '12个风险因素的综合评分（-24到+24）',
        },
        {
          key: '管理风险',
          value: risks.management,
          rationale: `${project.team.founders.length}位创始人`,
        },
        {
          key: '阶段风险',
          value: risks.stage,
          rationale: project.product.stage,
        },
        {
          key: '销售风险',
          value: risks.sales,
          rationale: project.traction?.customers ? `${project.traction.customers}个客户` : '无客户',
        },
        {
          key: '竞争风险',
          value: risks.competition,
          rationale: `${project.market.competitors.length}个竞争对手`,
        },
      ],
    };
  }

  /**
   * 可比公司法 (Comparable Company Method)
   * 适用于有收入的公司
   */
  private async comparableMethod(project: Project): Promise<ValuationResult> {
    if (!project.financials.revenue || project.financials.revenue.current === 0) {
      throw new Error('可比公司法需要有收入数据');
    }

    // 获取行业倍数（这里使用估算值，实际应该从数据库获取）
    const industryMultiples = this.getIndustryMultiples(project.industry, project.fundraising.currentStage);

    const revenue = project.financials.revenue.current;
    const arr = project.financials.metrics?.arr || revenue;

    // 使用收入倍数计算估值
    const valuation = Math.round(arr * industryMultiples.revenueMultiple);

    return {
      method: 'comparable' as ValuationMethod,
      valuation,
      range: {
        low: Math.round(arr * industryMultiples.revenueMultiple * 0.7),
        mid: valuation,
        high: Math.round(arr * industryMultiples.revenueMultiple * 1.3),
      },
      assumptions: [
        {
          key: 'ARR',
          value: arr,
          rationale: '年度经常性收入',
        },
        {
          key: '收入倍数',
          value: industryMultiples.revenueMultiple,
          rationale: `${project.industry}行业${project.fundraising.currentStage}阶段的中位数倍数`,
        },
      ],
      multiples: {
        revenueMultiple: industryMultiples.revenueMultiple,
        ebitdaMultiple: industryMultiples.ebitdaMultiple,
      },
    };
  }

  /**
   * 生成交易结构建议
   */
  generateDealStructure(
    project: Project,
    preMoney: number,
    investmentAmount?: number
  ): DealStructure {
    const investment = investmentAmount || project.fundraising.targetAmount;
    const postMoney = preMoney + investment;
    const newInvestorOwnership = investment / postMoney;

    // 计算股权稀释
    const existingOwnership = project.fundraising.previousRounds
      ? project.fundraising.previousRounds.reduce((sum, round) => {
          const roundPostMoney = (round.valuation || 0) + round.amount;
          return sum * (1 - round.amount / roundPostMoney);
        }, 1)
      : 1;

    const founderOwnership = existingOwnership * (1 - newInvestorOwnership) * 0.85; // 假设15%期权池
    const optionPool = 0.15 * (1 - newInvestorOwnership);
    const existingInvestorOwnership = 1 - newInvestorOwnership - founderOwnership - optionPool;

    return {
      investment: {
        amount: investment,
        currency: 'USD',
      },
      valuation: {
        preMoney,
        postMoney,
        method: 'Comprehensive valuation analysis',
      },
      equity: {
        newInvestorOwnership: Math.round(newInvestorOwnership * 10000) / 100,
        founderOwnership: Math.round(founderOwnership * 10000) / 100,
        existingInvestorOwnership: Math.round(existingInvestorOwnership * 10000) / 100,
        optionPool: Math.round(optionPool * 10000) / 100,
      },
      terms: {
        liquidationPreference: {
          multiple: 1,
          participating: false,
        },
        antiDilution: 'weighted-average',
        boardSeats: {
          founders: 2,
          investors: 1,
          independent: 1,
        },
        protectiveProvisions: [
          '增发新股',
          '出售公司',
          '修改公司章程',
          '分配股利',
          '增加债务超过一定金额',
        ],
        dragAlong: true,
        tagAlong: true,
        rightOfFirstRefusal: true,
      },
    };
  }

  // ===== 辅助方法 =====

  private getBaselineValuation(project: Project): number {
    // 根据地区、行业和阶段返回基准估值
    const stageBaselines: Record<string, number> = {
      'pre-seed': 2_000_000,
      'seed': 5_000_000,
      'series-a': 15_000_000,
      'series-b': 40_000_000,
      'series-c': 100_000_000,
      'series-d-plus': 250_000_000,
      'pre-ipo': 500_000_000,
    };

    let baseline = stageBaselines[project.fundraising.currentStage] || 5_000_000;

    // 根据行业调整（热门行业溢价）
    const hotIndustries = ['ai-ml', 'fintech', 'biotech'];
    if (hotIndustries.includes(project.industry)) {
      baseline *= 1.3;
    }

    return baseline;
  }

  private getIndustryMultiples(industry: string, stage: string): {
    revenueMultiple: number;
    ebitdaMultiple: number;
  } {
    // 简化版本，实际应该从数据库获取最新的行业数据
    const multiplesByIndustry: Record<string, { revenueMultiple: number; ebitdaMultiple: number }> = {
      'enterprise-software': { revenueMultiple: 10, ebitdaMultiple: 20 },
      'ai-ml': { revenueMultiple: 15, ebitdaMultiple: 25 },
      'fintech': { revenueMultiple: 8, ebitdaMultiple: 15 },
      'healthcare': { revenueMultiple: 7, ebitdaMultiple: 12 },
      'ecommerce': { revenueMultiple: 3, ebitdaMultiple: 8 },
      'b2b-saas': { revenueMultiple: 12, ebitdaMultiple: 22 },
    };

    return multiplesByIndustry[industry] || { revenueMultiple: 5, ebitdaMultiple: 10 };
  }

  private calculateWeightedValuation(
    results: ValuationResult[],
    project: Project
  ): { preMoney: number; postMoney: number; methodology: string } {
    // 根据项目阶段给不同方法分配权重
    let weights: Record<string, number> = {};

    if (!project.financials.revenue || project.financials.revenue.current === 0) {
      // Pre-revenue: 更依赖定性方法
      weights = {
        scorecard: 0.4,
        berkus: 0.35,
        'risk-factor': 0.25,
      };
    } else {
      // Has revenue: 可比公司法更重要
      weights = {
        scorecard: 0.25,
        berkus: 0.15,
        'risk-factor': 0.2,
        comparable: 0.4,
      };
    }

    let weightedSum = 0;
    let totalWeight = 0;

    for (const result of results) {
      const weight = weights[result.method] || 0;
      weightedSum += result.valuation * weight;
      totalWeight += weight;
    }

    const preMoney = Math.round(weightedSum / totalWeight);
    const postMoney = preMoney + project.fundraising.targetAmount;

    return {
      preMoney,
      postMoney,
      methodology: `加权平均法（${Object.entries(weights).map(([k, v]) => `${k}: ${v * 100}%`).join(', ')}）`,
    };
  }

  private getBenchmarkData(project: Project): ComprehensiveValuation['benchmarkData'] {
    // 这里应该从实际数据库获取，目前使用模拟数据
    const stageMedians: Record<string, number> = {
      'pre-seed': 3_000_000,
      'seed': 8_000_000,
      'series-a': 20_000_000,
      'series-b': 50_000_000,
      'series-c': 120_000_000,
    };

    return {
      industryMedian: stageMedians[project.fundraising.currentStage] || 10_000_000,
      stageMedian: stageMedians[project.fundraising.currentStage] || 10_000_000,
      recentComparables: [
        // 示例数据
      ],
    };
  }

  private suggestDealTerms(
    project: Project,
    preMoney: number
  ): ComprehensiveValuation['dealTerms'] {
    const investment = project.fundraising.targetAmount;
    const postMoney = preMoney + investment;
    const equity = (investment / postMoney) * 100;

    return {
      suggestedInvestment: investment,
      suggestedEquity: Math.round(equity * 100) / 100,
      suggestedValuation: preMoney,
      liquidationPreference: '1x非参与优先清算权',
      antiDilution: '加权平均反稀释条款',
    };
  }

  private generateAnalysis(
    project: Project,
    recommendedValuation: { preMoney: number; postMoney: number },
    methods: ValuationResult[]
  ): string {
    const parts: string[] = [];

    parts.push(`基于对${project.name}的综合分析，我们采用了多种估值方法进行评估。`);

    parts.push(
      `\n推荐的Pre-money估值为$${this.formatNumber(recommendedValuation.preMoney)}，` +
      `投后估值为$${this.formatNumber(recommendedValuation.postMoney)}。`
    );

    // 分析各方法的结果
    const valuations = methods.map(m => m.valuation);
    const min = Math.min(...valuations);
    const max = Math.max(...valuations);
    const range = ((max - min) / min * 100).toFixed(0);

    parts.push(
      `\n各估值方法的结果范围为$${this.formatNumber(min)}至$${this.formatNumber(max)}，` +
      `波动范围${range}%，显示出${range < '30' ? '较高的一致性' : '一定的不确定性'}。`
    );

    // 关键因素分析
    parts.push('\n关键估值驱动因素：');
    if (project.market.tam && project.market.tam >= 10_000_000_000) {
      parts.push(`- 巨大的市场机会（TAM $${this.formatNumber(project.market.tam)}）支撑较高估值`);
    }
    if (project.traction?.customers && project.traction.customers >= 50) {
      parts.push(`- 已验证的市场牵引力（${project.traction.customers}+客户）`);
    }
    if (project.product.stage === 'scaling') {
      parts.push('- 产品已进入规模化阶段，执行风险降低');
    }

    return parts.join('\n');
  }

  private identifyValuationRisks(project: Project, methods: ValuationResult[]): string[] {
    const risks: string[] = [];

    // 估值方法差异过大
    const valuations = methods.map(m => m.valuation);
    const avg = valuations.reduce((a, b) => a + b, 0) / valuations.length;
    const maxDeviation = Math.max(...valuations.map(v => Math.abs(v - avg) / avg));

    if (maxDeviation > 0.4) {
      risks.push('不同估值方法结果差异较大（>40%），估值存在较高不确定性');
    }

    // 缺乏收入数据
    if (!project.financials.revenue || project.financials.revenue.current === 0) {
      risks.push('尚无收入，估值主要基于定性分析，实际价值需市场验证');
    }

    // 产品早期
    if (project.product.stage === 'idea' || project.product.stage === 'prototype') {
      risks.push('产品处于早期阶段，技术和市场风险较高');
    }

    // 竞争激烈
    if (project.market.competitors.length > 10) {
      risks.push('市场竞争激烈，可能影响未来增长和估值');
    }

    return risks;
  }

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
