import type { Project, ProjectAssessment } from '../../types/project.js';

/**
 * 项目评估引擎
 * 全面评估创业项目的投资价值
 */
export class ProjectAssessor {
  /**
   * 评估项目
   */
  async assess(project: Project): Promise<ProjectAssessment> {
    const scores = {
      team: this.assessTeam(project),
      market: this.assessMarket(project),
      product: this.assessProduct(project),
      traction: this.assessTraction(project),
      financials: this.assessFinancials(project),
      overall: 0,
    };

    // 加权计算总分
    scores.overall = this.calculateOverallScore(scores);

    const strengths = this.identifyStrengths(project, scores);
    const weaknesses = this.identifyWeaknesses(project, scores);
    const risks = this.assessRisks(project);
    const recommendations = this.generateRecommendations(project, scores, weaknesses);
    const investmentReadiness = this.determineInvestmentReadiness(scores, risks);

    return {
      project,
      scores,
      strengths,
      weaknesses,
      risks,
      recommendations,
      investmentReadiness,
    };
  }

  /**
   * 评估团队 (0-100)
   */
  private assessTeam(project: Project): number {
    let score = 0;
    const { team } = project;

    // 创始人数量 (0-20)
    const founderCount = team.founders.length;
    if (founderCount >= 2 && founderCount <= 4) {
      score += 20;
    } else if (founderCount === 1) {
      score += 10;
    } else {
      score += 5;
    }

    // 创始人背景 (0-30)
    const hasRelevantBackground = team.founders.some(
      f => f.background.toLowerCase().includes('experience') ||
           f.background.toLowerCase().includes('expertise')
    );
    if (hasRelevantBackground) {
      score += 30;
    } else {
      score += 15;
    }

    // 团队规模 (0-20)
    if (team.teamSize >= 5 && team.teamSize <= 50) {
      score += 20;
    } else if (team.teamSize >= 2 && team.teamSize < 5) {
      score += 15;
    } else if (team.teamSize > 50) {
      score += 10;
    } else {
      score += 5;
    }

    // 关键岗位 (0-30)
    const hasKeyHires = team.keyHires && team.keyHires.length > 0;
    if (hasKeyHires) {
      score += 30;
    } else {
      score += 10;
    }

    return Math.min(score, 100);
  }

  /**
   * 评估市场 (0-100)
   */
  private assessMarket(project: Project): number {
    let score = 0;
    const { market } = project;

    // 市场规模 (0-40)
    if (market.tam !== undefined) {
      if (market.tam >= 10_000_000_000) { // $10B+
        score += 40;
      } else if (market.tam >= 1_000_000_000) { // $1B+
        score += 30;
      } else if (market.tam >= 100_000_000) { // $100M+
        score += 20;
      } else {
        score += 10;
      }
    }

    // 市场增长率 (0-30)
    if (market.marketGrowthRate !== undefined) {
      if (market.marketGrowthRate >= 0.3) { // 30%+
        score += 30;
      } else if (market.marketGrowthRate >= 0.15) { // 15%+
        score += 20;
      } else if (market.marketGrowthRate >= 0.05) { // 5%+
        score += 10;
      } else {
        score += 5;
      }
    }

    // 竞争格局 (0-30)
    const competitorCount = market.competitors.length;
    const hasDifferentiation = market.competitors.some(c => c.differentiation);

    if (competitorCount <= 3 && hasDifferentiation) {
      score += 30;
    } else if (competitorCount <= 5) {
      score += 20;
    } else if (competitorCount <= 10) {
      score += 10;
    } else {
      score += 5;
    }

    return Math.min(score, 100);
  }

  /**
   * 评估产品 (0-100)
   */
  private assessProduct(project: Project): number {
    let score = 0;
    const { product } = project;

    // 产品阶段 (0-40)
    const stageScores: Record<typeof product.stage, number> = {
      'idea': 5,
      'prototype': 15,
      'mvp': 25,
      'launched': 35,
      'scaling': 40,
    };
    score += stageScores[product.stage];

    // 独特价值主张 (0-30)
    const uvpLength = product.uniqueValueProposition.length;
    if (uvpLength >= 50) {
      score += 30;
    } else if (uvpLength >= 20) {
      score += 20;
    } else {
      score += 10;
    }

    // 核心功能 (0-15)
    const featureCount = product.keyFeatures.length;
    if (featureCount >= 5) {
      score += 15;
    } else if (featureCount >= 3) {
      score += 10;
    } else {
      score += 5;
    }

    // 痛点识别 (0-15)
    const painPointCount = product.customerPainPoints.length;
    if (painPointCount >= 3) {
      score += 15;
    } else if (painPointCount >= 2) {
      score += 10;
    } else {
      score += 5;
    }

    return Math.min(score, 100);
  }

  /**
   * 评估牵引力 (0-100)
   */
  private assessTraction(project: Project): number {
    if (!project.traction) {
      return 0;
    }

    let score = 0;
    const { traction } = project;

    // 客户数量 (0-30)
    if (traction.customers !== undefined) {
      if (traction.customers >= 1000) {
        score += 30;
      } else if (traction.customers >= 100) {
        score += 20;
      } else if (traction.customers >= 10) {
        score += 10;
      } else if (traction.customers > 0) {
        score += 5;
      }
    }

    // 用户数量 (0-25)
    if (traction.users !== undefined) {
      if (traction.users >= 100_000) {
        score += 25;
      } else if (traction.users >= 10_000) {
        score += 20;
      } else if (traction.users >= 1_000) {
        score += 15;
      } else if (traction.users > 0) {
        score += 10;
      }
    }

    // 合作伙伴 (0-20)
    if (traction.partnerships && traction.partnerships.length > 0) {
      score += Math.min(traction.partnerships.length * 5, 20);
    }

    // 奖项和媒体 (0-15)
    const hasAwards = traction.awards && traction.awards.length > 0;
    const hasPress = traction.press && traction.press.length > 0;
    if (hasAwards && hasPress) {
      score += 15;
    } else if (hasAwards || hasPress) {
      score += 10;
    }

    // 增长趋势 (0-10)
    if (traction.growth) {
      score += 10;
    }

    return Math.min(score, 100);
  }

  /**
   * 评估财务 (0-100)
   */
  private assessFinancials(project: Project): number {
    let score = 0;
    const { financials } = project;

    // 收入 (0-30)
    if (financials.revenue) {
      if (financials.revenue.current >= 10_000_000) { // $10M+
        score += 30;
      } else if (financials.revenue.current >= 1_000_000) { // $1M+
        score += 25;
      } else if (financials.revenue.current >= 100_000) { // $100K+
        score += 15;
      } else if (financials.revenue.current > 0) {
        score += 10;
      }
    }

    // 关键指标 (0-40)
    if (financials.metrics) {
      const { metrics } = financials;

      // 毛利率
      if (metrics.grossMargin !== undefined) {
        if (metrics.grossMargin >= 0.7) {
          score += 15;
        } else if (metrics.grossMargin >= 0.5) {
          score += 10;
        } else if (metrics.grossMargin >= 0.3) {
          score += 5;
        }
      }

      // LTV/CAC比率
      if (metrics.lifetimeValue && metrics.customerAcquisitionCost) {
        const ratio = metrics.lifetimeValue / metrics.customerAcquisitionCost;
        if (ratio >= 3) {
          score += 15;
        } else if (ratio >= 2) {
          score += 10;
        } else if (ratio >= 1) {
          score += 5;
        }
      }

      // 流失率
      if (metrics.churnRate !== undefined) {
        if (metrics.churnRate <= 0.05) { // 5%以下
          score += 10;
        } else if (metrics.churnRate <= 0.1) { // 10%以下
          score += 5;
        }
      }
    }

    // 跑道 (0-30)
    if (financials.expenses) {
      const { runway } = financials.expenses;
      if (runway >= 18) {
        score += 30;
      } else if (runway >= 12) {
        score += 20;
      } else if (runway >= 6) {
        score += 10;
      } else {
        score += 5;
      }
    }

    return Math.min(score, 100);
  }

  /**
   * 计算综合得分
   */
  private calculateOverallScore(scores: Omit<ProjectAssessment['scores'], 'overall'>): number {
    const weights = {
      team: 0.30,
      market: 0.25,
      product: 0.20,
      traction: 0.15,
      financials: 0.10,
    };

    return Math.round(
      scores.team * weights.team +
      scores.market * weights.market +
      scores.product * weights.product +
      scores.traction * weights.traction +
      scores.financials * weights.financials
    );
  }

  /**
   * 识别优势
   */
  private identifyStrengths(project: Project, scores: ProjectAssessment['scores']): string[] {
    const strengths: string[] = [];

    if (scores.team >= 80) {
      strengths.push('优秀的创始团队，具备深厚的行业背景和执行能力');
    }

    if (scores.market >= 80) {
      strengths.push('巨大的市场机会，市场规模可观且增长迅速');
    }

    if (scores.product >= 80) {
      strengths.push('产品已经较为成熟，具备清晰的价值主张和差异化优势');
    }

    if (scores.traction >= 70) {
      strengths.push('已获得显著的市场牵引力，有明确的增长趋势');
    }

    if (scores.financials >= 70) {
      strengths.push('财务指标健康，收入模式已得到验证');
    }

    // 具体特征分析
    if (project.market.tam && project.market.tam >= 10_000_000_000) {
      strengths.push(`TAM超过100亿美元，市场空间巨大`);
    }

    if (project.financials.metrics?.grossMargin && project.financials.metrics.grossMargin >= 0.7) {
      strengths.push(`毛利率${Math.round(project.financials.metrics.grossMargin * 100)}%，盈利能力强`);
    }

    if (project.traction?.customers && project.traction.customers >= 100) {
      strengths.push(`已获得${project.traction.customers}+付费客户，商业模式得到验证`);
    }

    return strengths;
  }

  /**
   * 识别劣势
   */
  private identifyWeaknesses(project: Project, scores: ProjectAssessment['scores']): string[] {
    const weaknesses: string[] = [];

    if (scores.team < 60) {
      weaknesses.push('团队需要加强，建议补充行业经验丰富的核心成员');
    }

    if (scores.market < 60) {
      weaknesses.push('市场机会有限或竞争过于激烈，需要重新评估目标市场');
    }

    if (scores.product < 60) {
      weaknesses.push('产品成熟度不足，需要加快产品迭代和功能完善');
    }

    if (scores.traction < 40) {
      weaknesses.push('缺乏市场验证，需要尽快获取早期客户并证明产品价值');
    }

    if (scores.financials < 40) {
      weaknesses.push('财务指标较弱，需要改善单位经济模型和现金流管理');
    }

    // 具体问题
    if (project.team.founders.length === 1) {
      weaknesses.push('单一创始人风险较高，建议引入联合创始人');
    }

    if (project.financials.expenses && project.financials.expenses.runway < 6) {
      weaknesses.push(`跑道仅剩${project.financials.expenses.runway}个月，需要尽快完成融资`);
    }

    if (project.market.competitors.length > 10) {
      weaknesses.push('竞争过于激烈，需要强化差异化优势');
    }

    if (project.product.stage === 'idea' || project.product.stage === 'prototype') {
      weaknesses.push('产品尚未推向市场，需要加快MVP开发和市场验证');
    }

    return weaknesses;
  }

  /**
   * 风险评估
   */
  private assessRisks(project: Project): ProjectAssessment['risks'] {
    const risks: ProjectAssessment['risks'] = [];

    // 市场风险
    if (project.market.competitors.length > 10) {
      risks.push({
        category: '市场风险',
        description: '市场竞争激烈，面临众多竞争对手',
        severity: 'high',
        mitigation: '建立清晰的差异化定位，聚焦特定细分市场',
      });
    }

    // 执行风险
    if (project.team.founders.length === 1) {
      risks.push({
        category: '执行风险',
        description: '单一创始人，关键人物风险较高',
        severity: 'medium',
        mitigation: '引入联合创始人或关键高管，建立备份机制',
      });
    }

    // 财务风险
    if (project.financials.expenses && project.financials.expenses.runway < 6) {
      risks.push({
        category: '财务风险',
        description: '现金流跑道不足6个月，面临资金压力',
        severity: 'high',
        mitigation: '立即启动融资流程，同时控制成本延长跑道',
      });
    }

    // 产品风险
    if (project.product.stage === 'idea' || project.product.stage === 'prototype') {
      risks.push({
        category: '产品风险',
        description: '产品尚未推向市场，市场接受度未知',
        severity: 'high',
        mitigation: '尽快完成MVP开发，获取早期用户反馈',
      });
    }

    // 牵引力风险
    if (!project.traction || (project.traction.customers || 0) < 10) {
      risks.push({
        category: '市场验证风险',
        description: '缺乏足够的市场验证和客户牵引力',
        severity: 'medium',
        mitigation: '聚焦获取早期付费客户，建立案例研究',
      });
    }

    return risks;
  }

  /**
   * 生成建议
   */
  private generateRecommendations(
    project: Project,
    scores: ProjectAssessment['scores'],
    weaknesses: string[]
  ): string[] {
    const recommendations: string[] = [];

    // 基于得分的建议
    if (scores.overall >= 80) {
      recommendations.push('项目整体质量优秀，建议立即启动融资流程');
      recommendations.push('可以瞄准顶级VC，争取更好的融资条件');
    } else if (scores.overall >= 60) {
      recommendations.push('项目具备融资基础，建议在改进关键弱项后启动融资');
      recommendations.push('针对性补强团队和产品，提升项目竞争力');
    } else {
      recommendations.push('项目尚不具备融资条件，建议先进行内部优化');
      recommendations.push('聚焦产品开发和早期市场验证，积累更多牵引力');
    }

    // 针对性建议
    if (scores.traction < 50) {
      recommendations.push('优先任务：获取早期客户，证明产品市场契合度');
    }

    if (scores.team < 70) {
      recommendations.push('考虑引入行业专家或经验丰富的联合创始人');
    }

    if (scores.financials < 50 && project.financials.revenue) {
      recommendations.push('改善单位经济模型，关注关键财务指标如LTV/CAC比率');
    }

    // 融资策略建议
    if (project.fundraising.currentStage === 'seed' || project.fundraising.currentStage === 'pre-seed') {
      recommendations.push('对于早期阶段，重点展示团队能力和市场机会');
      recommendations.push('寻找愿意承担早期风险的天使投资人或种子基金');
    } else {
      recommendations.push('对于成长阶段，需要展示清晰的收入增长和单位经济模型');
      recommendations.push('目标机构应该在你的行业有专业认知和资源网络');
    }

    return recommendations;
  }

  /**
   * 判断融资准备度
   */
  private determineInvestmentReadiness(
    scores: ProjectAssessment['scores'],
    risks: ProjectAssessment['risks']
  ): ProjectAssessment['investmentReadiness'] {
    const highRisks = risks.filter(r => r.severity === 'high').length;

    if (scores.overall >= 80 && highRisks === 0) {
      return 'highly-ready';
    } else if (scores.overall >= 65 && highRisks <= 1) {
      return 'ready';
    } else if (scores.overall >= 50) {
      return 'needs-work';
    } else {
      return 'not-ready';
    }
  }
}
