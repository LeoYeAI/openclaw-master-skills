import type { Project } from '../../types/project.js';
import type { Investor, InvestorMatch } from '../../types/investor.js';

/**
 * 投资人匹配引擎
 * 基于项目特征匹配合适的投资机构
 */
export class InvestorMatcher {
  private investors: Investor[] = [];

  constructor(investors: Investor[]) {
    this.investors = investors;
  }

  /**
   * 为项目匹配投资人
   */
  async matchInvestors(project: Project, topN: number = 20): Promise<InvestorMatch[]> {
    const matches: InvestorMatch[] = [];

    for (const investor of this.investors) {
      const matchResult = this.calculateMatch(project, investor);

      if (matchResult.matchScore > 0) {
        matches.push(matchResult);
      }
    }

    // 按匹配分数排序
    matches.sort((a, b) => b.matchScore - a.matchScore);

    // 返回前N个
    return matches.slice(0, topN);
  }

  /**
   * 计算项目与投资人的匹配度
   */
  private calculateMatch(project: Project, investor: Investor): InvestorMatch {
    let score = 0;
    const maxScore = 100;
    const matchReasons: string[] = [];
    const concerns: string[] = [];

    // 1. 融资阶段匹配 (0-25分)
    if (investor.strategy.stages.includes(project.fundraising.currentStage)) {
      score += 25;
      matchReasons.push(`投资阶段完全匹配（${project.fundraising.currentStage}）`);
    } else {
      // 检查相邻阶段
      const stageOrder = ['pre-seed', 'seed', 'series-a', 'series-b', 'series-c', 'series-d-plus'];
      const projectStageIndex = stageOrder.indexOf(project.fundraising.currentStage);
      const hasAdjacentStage = investor.strategy.stages.some(s => {
        const investorStageIndex = stageOrder.indexOf(s);
        return Math.abs(investorStageIndex - projectStageIndex) === 1;
      });

      if (hasAdjacentStage) {
        score += 15;
        matchReasons.push(`投资阶段接近（可考虑）`);
      } else {
        concerns.push(`投资阶段不匹配（机构关注：${investor.strategy.stages.join(', ')}）`);
      }
    }

    // 2. 行业匹配 (0-25分)
    if (investor.strategy.industries.includes(project.industry)) {
      score += 25;
      matchReasons.push(`行业完全匹配（${project.industry}）`);

      // 检查细分行业
      if (investor.strategy.subIndustries && project.subIndustry) {
        if (investor.strategy.subIndustries.includes(project.subIndustry)) {
          score += 5; // 额外加分
          matchReasons.push(`细分领域也匹配（${project.subIndustry}）`);
        }
      }
    } else {
      concerns.push(`行业不在机构主要投资范围（机构关注：${investor.strategy.industries.join(', ')}）`);
    }

    // 3. 投资金额匹配 (0-20分)
    const targetAmount = project.fundraising.targetAmount;
    const { min, max, typical } = investor.strategy.investmentRange;

    if (targetAmount >= min && targetAmount <= max) {
      // 在范围内
      const closenessToTypical = 1 - Math.abs(targetAmount - typical) / typical;
      score += Math.round(20 * Math.max(0.5, closenessToTypical));
      matchReasons.push(`投资金额在范围内（$${this.formatNumber(min)}-${this.formatNumber(max)}）`);
    } else if (targetAmount < min) {
      score += 5;
      concerns.push(`融资金额低于机构通常投资额（最低$${this.formatNumber(min)}）`);
    } else {
      concerns.push(`融资金额超过机构通常投资额（最高$${this.formatNumber(max)}）`);
    }

    // 4. 地域匹配 (0-15分)
    const projectRegion = this.getRegion(project.location);
    if (investor.strategy.geographicFocus.includes(projectRegion) ||
        investor.strategy.geographicFocus.includes('global')) {
      score += 15;
      matchReasons.push(`地域匹配（${projectRegion}）`);
    } else {
      score += 5; // 部分分数，因为很多机构会考虑非重点地区的优质项目
      concerns.push(`地域不是机构主要关注区域（机构关注：${investor.strategy.geographicFocus.join(', ')}）`);
    }

    // 5. 商业模式匹配 (0-10分)
    if (investor.strategy.businessModels &&
        investor.strategy.businessModels.includes(project.businessModel)) {
      score += 10;
      matchReasons.push(`商业模式匹配（${project.businessModel}）`);
    }

    // 6. 特殊关注领域匹配 (0-5分 bonus)
    if (investor.strategy.specialFocus) {
      const projectKeywords = [
        project.name.toLowerCase(),
        project.description.toLowerCase(),
        project.product.description.toLowerCase(),
      ].join(' ');

      const hasSpecialMatch = investor.strategy.specialFocus.some(focus =>
        projectKeywords.includes(focus.toLowerCase())
      );

      if (hasSpecialMatch) {
        score += 5;
        matchReasons.push('项目符合机构特殊关注主题');
      }
    }

    // 7. 投资风格匹配分析（不计分，仅用于策略建议）
    let approachStrategy = '';
    if (investor.investmentStyle) {
      const { leadInvestor, followOn, handsOn } = investor.investmentStyle;

      if (leadInvestor) {
        approachStrategy += '该机构偏好领投，适合作为主要投资方。';
      } else if (followOn) {
        approachStrategy += '该机构主要做跟投，需要先找到领投方。';
      }

      if (handsOn === 'very-hands-on' || handsOn === 'hands-on') {
        approachStrategy += '该机构会深度参与公司运营，可提供丰富资源支持。';
      }

      // 附加价值
      if (investor.investmentStyle.valueAdd && investor.investmentStyle.valueAdd.length > 0) {
        approachStrategy += `\n附加价值：${investor.investmentStyle.valueAdd.join('、')}。`;
      }
    }

    // 决策流程信息
    if (investor.decisionProcess?.averageTimeToDecision) {
      approachStrategy += `\n平均决策周期：${investor.decisionProcess.averageTimeToDecision}天。`;
    }

    // 联系方式建议
    if (investor.contact?.preferredContact) {
      const contactPreference = investor.contact.preferredContact;
      if (contactPreference === 'warm-intro') {
        approachStrategy += '\n最佳接触方式：通过共同人脉warm intro。';
      } else if (contactPreference === 'submission-form') {
        approachStrategy += '\n可通过官网提交BP。';
      }
    }

    // 确定优先级
    let priority: 'high' | 'medium' | 'low';
    if (score >= 80) {
      priority = 'high';
    } else if (score >= 60) {
      priority = 'medium';
    } else {
      priority = 'low';
    }

    return {
      investor,
      matchScore: Math.min(score, maxScore),
      matchReasons,
      concerns,
      approachStrategy: approachStrategy || '建议研究该机构的投资组合和投资论点，定制化接触策略。',
      priority,
    };
  }

  /**
   * 生成投资人接触策略
   */
  generateOutreachStrategy(matches: InvestorMatch[]): string {
    const lines: string[] = [];

    lines.push('# 投资人接触策略\n');

    // 高优先级
    const highPriority = matches.filter(m => m.priority === 'high');
    if (highPriority.length > 0) {
      lines.push('## 🎯 高优先级目标机构\n');
      lines.push('这些机构与您的项目高度匹配，应优先接触：\n');

      highPriority.forEach((match, index) => {
        lines.push(`### ${index + 1}. ${match.investor.name}`);
        lines.push(`**匹配度**: ${match.matchScore}分`);
        lines.push(`**匹配原因**:`);
        match.matchReasons.forEach(r => lines.push(`- ${r}`));
        if (match.concerns.length > 0) {
          lines.push(`**需要注意**:`);
          match.concerns.forEach(c => lines.push(`- ${c}`));
        }
        lines.push(`**接触策略**: ${match.approachStrategy}`);
        if (match.investor.contact?.email) {
          lines.push(`**联系邮箱**: ${match.investor.contact.email}`);
        }
        if (match.investor.contact?.submissionUrl) {
          lines.push(`**提交链接**: ${match.investor.contact.submissionUrl}`);
        }
        lines.push('');
      });
    }

    // 中优先级
    const mediumPriority = matches.filter(m => m.priority === 'medium');
    if (mediumPriority.length > 0) {
      lines.push('## 📋 中优先级备选机构\n');
      lines.push('这些机构也值得考虑，可作为第二梯队：\n');

      mediumPriority.slice(0, 10).forEach((match, index) => {
        lines.push(`**${index + 1}. ${match.investor.name}** (匹配度: ${match.matchScore}分)`);
        lines.push(`   - ${match.matchReasons[0] || '部分匹配'}`);
        if (match.concerns.length > 0) {
          lines.push(`   - ⚠️ ${match.concerns[0]}`);
        }
        lines.push('');
      });
    }

    // 总体建议
    lines.push('## 💡 总体建议\n');
    lines.push('1. **优先warm intro**: 通过共同联系人介绍，成功率更高');
    lines.push('2. **定制化BP**: 根据每个机构的投资论点定制pitch deck');
    lines.push('3. **同时接触**: 同时联系5-10家机构，不要串行');
    lines.push('4. **快速迭代**: 收集反馈，持续改进pitch');
    lines.push('5. **保持节奏**: 控制整个融资周期在2-3个月内完成');

    return lines.join('\n');
  }

  /**
   * 分析为什么某个知名机构不匹配
   */
  analyzeNonMatch(project: Project, investorName: string): string {
    const investor = this.investors.find(i =>
      i.name.toLowerCase().includes(investorName.toLowerCase())
    );

    if (!investor) {
      return `未找到名为 "${investorName}" 的投资机构信息。`;
    }

    const match = this.calculateMatch(project, investor);

    const lines: string[] = [];
    lines.push(`# ${investor.name} 匹配分析\n`);
    lines.push(`**匹配得分**: ${match.matchScore}/100\n`);

    if (match.matchScore >= 70) {
      lines.push('✅ 该机构与您的项目匹配度较高，建议接触。\n');
    } else if (match.matchScore >= 50) {
      lines.push('⚠️ 该机构与项目有一定匹配度，可以尝试，但需要注意以下问题。\n');
    } else {
      lines.push('❌ 该机构与项目匹配度较低，可能不是最佳选择。\n');
    }

    if (match.matchReasons.length > 0) {
      lines.push('**匹配点**:');
      match.matchReasons.forEach(r => lines.push(`- ${r}`));
      lines.push('');
    }

    if (match.concerns.length > 0) {
      lines.push('**不匹配原因**:');
      match.concerns.forEach(c => lines.push(`- ${c}`));
      lines.push('');
    }

    lines.push(`**机构投资策略**:`);
    lines.push(`- 关注阶段: ${investor.strategy.stages.join(', ')}`);
    lines.push(`- 关注行业: ${investor.strategy.industries.join(', ')}`);
    lines.push(`- 投资金额: $${this.formatNumber(investor.strategy.investmentRange.min)} - $${this.formatNumber(investor.strategy.investmentRange.max)}`);
    lines.push(`- 地域关注: ${investor.strategy.geographicFocus.join(', ')}`);

    if (investor.strategy.thesis) {
      lines.push(`\n**投资论点**: ${investor.strategy.thesis}`);
    }

    return lines.join('\n');
  }

  // 辅助方法
  private getRegion(location: string): any {
    const loc = location.toLowerCase();

    if (loc.includes('china') || loc.includes('beijing') || loc.includes('shanghai') ||
        loc.includes('shenzhen') || loc.includes('hangzhou') || loc.includes('中国') ||
        loc.includes('北京') || loc.includes('上海') || loc.includes('深圳')) {
      return 'china';
    }

    if (loc.includes('us') || loc.includes('usa') || loc.includes('san francisco') ||
        loc.includes('new york') || loc.includes('silicon valley') || loc.includes('america')) {
      return 'north-america';
    }

    if (loc.includes('europe') || loc.includes('uk') || loc.includes('london') ||
        loc.includes('berlin') || loc.includes('paris')) {
      return 'europe';
    }

    if (loc.includes('singapore') || loc.includes('thailand') || loc.includes('vietnam') ||
        loc.includes('indonesia') || loc.includes('malaysia')) {
      return 'southeast-asia';
    }

    if (loc.includes('japan') || loc.includes('korea') || loc.includes('taiwan') ||
        loc.includes('hong kong')) {
      return 'asia';
    }

    return 'global';
  }

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
}
