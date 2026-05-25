"""
Investor Matcher - 智能匹配投资人
"""

import logging
from typing import List

from fa_advisor.types.project import Project
from fa_advisor.types.investor import Investor
from fa_advisor.types.models import InvestorMatch

logger = logging.getLogger(__name__)


class InvestorMatcher:
    """
    投资人匹配器
    
    基于多个维度匹配合适的投资人：
    - 投资阶段匹配
    - 行业focus匹配
    - 投资金额范围匹配
    - 地理位置匹配
    - 商业模式匹配
    """

    def __init__(self, investors: List[Investor]):
        """
        初始化投资人匹配器
        
        Args:
            investors: 投资人列表
        """
        self.investors = investors
        logger.info(f"Initialized InvestorMatcher with {len(investors)} investors")

    async def match_investors(
        self,
        project: Project,
        top_n: int = 20
    ) -> List[InvestorMatch]:
        """
        匹配投资人
        
        Args:
            project: 项目信息
            top_n: 返回top N个匹配结果
            
        Returns:
            排序后的投资人匹配列表
        """
        logger.info(f"Matching investors for {project.name}")

        if not self.investors:
            logger.warning("No investors in database")
            return []

        matches = []

        for investor in self.investors:
            # 计算匹配分数
            stage_score, stage_fit = self._match_stage(project, investor)
            industry_score, industry_fit = self._match_industry(project, investor)
            amount_score, amount_fit = self._match_amount(project, investor)
            geo_score, geo_fit = self._match_geography(project, investor)
            model_score = self._match_business_model(project, investor)

            # 总分计算（加权）
            total_score = (
                stage_score * 0.35 +      # 阶段最重要
                industry_score * 0.30 +    # 行业其次
                amount_score * 0.20 +      # 金额
                geo_score * 0.10 +         # 地理
                model_score * 0.05         # 商业模式
            )

            # 生成匹配理由
            reasoning = self._generate_reasoning(
                project, investor, stage_fit, industry_fit, amount_fit, geo_fit
            )

            # 确定优先级
            priority = self._determine_priority(total_score)

            matches.append(InvestorMatch(
                investor_name=investor.name,
                match_score=total_score,
                reasoning=reasoning,
                stage_fit=stage_fit,
                industry_fit=industry_fit,
                check_size_fit=amount_fit,
                geo_fit=geo_fit,
                priority=priority
            ))

        # 按分数排序
        matches.sort(key=lambda x: x.match_score, reverse=True)

        return matches[:top_n]

    def _match_stage(self, project: Project, investor: Investor) -> tuple[float, bool]:
        """
        匹配投资阶段
        
        Returns:
            (score, is_match) - score: 0-100, is_match: True/False
        """
        project_stage = project.fundraising.current_stage.value
        investor_stages = investor.strategy.stages

        # 精确匹配
        if project_stage in investor_stages:
            return 100.0, True

        # 相邻阶段匹配
        stage_order = ['pre-seed', 'seed', 'series-a', 'series-b', 'series-c']

        if project_stage in stage_order:
            project_idx = stage_order.index(project_stage)

            # 检查相邻阶段
            for stage in investor_stages:
                if stage in stage_order:
                    investor_idx = stage_order.index(stage)
                    diff = abs(project_idx - investor_idx)

                    if diff == 1:
                        return 70.0, True  # 相邻阶段
                    elif diff == 2:
                        return 40.0, False  # 差2个阶段

        return 20.0, False

    def _match_industry(self, project: Project, investor: Investor) -> tuple[float, bool]:
        """
        匹配行业focus
        
        Returns:
            (score, is_match)
        """
        project_industry = project.industry.value
        investor_industries = investor.strategy.industries

        # 精确匹配
        if project_industry in investor_industries:
            return 100.0, True

        # 部分匹配（例如 "enterprise-software" 和 "software"）
        for inv_industry in investor_industries:
            if inv_industry in project_industry or project_industry in inv_industry:
                return 80.0, True

        # 泛投资人（投很多行业）
        if len(investor_industries) > 5:
            return 50.0, False

        return 30.0, False

    def _match_amount(self, project: Project, investor: Investor) -> tuple[float, bool]:
        """
        匹配投资金额范围
        
        Returns:
            (score, is_match)
        """
        target_amount = project.fundraising.target_amount
        min_check = investor.strategy.investment_range_min
        max_check = investor.strategy.investment_range_max

        # 在范围内
        if min_check <= target_amount <= max_check:
            # 在中间范围得分更高
            range_center = (min_check + max_check) / 2
            distance_from_center = abs(target_amount - range_center) / (max_check - min_check)

            if distance_from_center < 0.25:  # 在中心附近25%范围
                return 100.0, True
            else:
                return 85.0, True

        # 略低于最小投资额
        if min_check * 0.7 <= target_amount < min_check:
            return 60.0, True  # 可能接受较小的票

        # 略高于最大投资额
        if max_check < target_amount <= max_check * 1.3:
            return 60.0, True  # 可能领投或联合投资

        return 20.0, False

    def _match_geography(self, project: Project, investor: Investor) -> tuple[float, bool]:
        """
        匹配地理位置
        
        Returns:
            (score, is_match)
        """
        project_location = project.location.lower()
        geo_focus = [g.lower() for g in investor.strategy.geographic_focus]

        # 精确匹配城市或国家
        for geo in geo_focus:
            if geo in project_location or project_location in geo:
                return 100.0, True

        # 全球投资人
        if 'global' in geo_focus or 'worldwide' in geo_focus:
            return 80.0, True

        # 同地区（粗略判断）
        asia = ['china', 'beijing', 'shanghai', 'singapore', 'hongkong', 'tokyo', 'seoul']
        us = ['usa', 'us', 'silicon valley', 'new york', 'boston', 'san francisco']
        europe = ['uk', 'london', 'berlin', 'paris', 'amsterdam']

        project_region = None
        investor_region = None

        if any(loc in project_location for loc in asia):
            project_region = 'asia'
        elif any(loc in project_location for loc in us):
            project_region = 'us'
        elif any(loc in project_location for loc in europe):
            project_region = 'europe'

        for geo in geo_focus:
            if any(loc in geo for loc in asia):
                investor_region = 'asia'
            elif any(loc in geo for loc in us):
                investor_region = 'us'
            elif any(loc in geo for loc in europe):
                investor_region = 'europe'

        if project_region and project_region == investor_region:
            return 70.0, True

        return 40.0, False

    def _match_business_model(self, project: Project, investor: Investor) -> float:
        """
        匹配商业模式
        
        Returns:
            score: 0-100
        """
        if not investor.strategy.business_models:
            return 50.0  # 无特定偏好

        project_model = project.business_model.value

        if project_model in investor.strategy.business_models:
            return 100.0

        # 相似模式
        similar = {
            'b2b-saas': ['subscription', 'enterprise', 'platform'],
            'marketplace': ['platform', 'transaction'],
            'subscription': ['b2b-saas', 'b2c', 'freemium']
        }

        if project_model in similar:
            for inv_model in investor.strategy.business_models:
                if inv_model in similar[project_model]:
                    return 70.0

        return 40.0

    def _generate_reasoning(
        self,
        project: Project,
        investor: Investor,
        stage_fit: bool,
        industry_fit: bool,
        amount_fit: bool,
        geo_fit: bool
    ) -> str:
        """生成匹配理由"""
        reasons = []

        if stage_fit:
            reasons.append(f"Invests in {project.fundraising.current_stage.value}")

        if industry_fit:
            reasons.append(f"Focus on {project.industry.value}")

        if amount_fit:
            reasons.append(
                f"Check size ${investor.strategy.investment_range_min / 1_000_000:.0f}M-"
                f"${investor.strategy.investment_range_max / 1_000_000:.0f}M fits ${project.fundraising.target_amount / 1_000_000:.0f}M target"
            )

        if geo_fit:
            reasons.append(f"Geographic focus includes {project.location}")

        if investor.investment_style.lead_investor:
            reasons.append("Can lead rounds")

        if investor.investment_style.hands_on:
            reasons.append("Hands-on investor")

        if not reasons:
            reasons.append("General fit based on portfolio strategy")

        return "; ".join(reasons)

    def _determine_priority(self, score: float) -> str:
        """确定优先级"""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

    def generate_outreach_strategy(self, matches: List[InvestorMatch]) -> str:
        """
        生成投资人接触策略
        
        Args:
            matches: 匹配结果列表
            
        Returns:
            Markdown 格式的接触策略
        """
        if not matches:
            return "No investor matches found. Please expand search criteria."

        high_priority = [m for m in matches if m.priority == "high"]
        medium_priority = [m for m in matches if m.priority == "medium"]
        low_priority = [m for m in matches if m.priority == "low"]

        strategy = f"""# Investor Outreach Strategy

## Summary

- **Total Matches:** {len(matches)}
- **High Priority:** {len(high_priority)}
- **Medium Priority:** {len(medium_priority)}
- **Low Priority:** {len(low_priority)}

## Priority Tier 1: High Priority ({len(high_priority)} investors)

**Target Timeline:** Weeks 1-2

**Investors:**
"""

        for match in high_priority[:10]:
            strategy += f"- **{match.investor_name}** (Match: {match.match_score:.0f}/100)\n"
            strategy += f"  - {match.reasoning}\n"

        strategy += """

**Approach:**
1. Seek warm introductions through your network
2. Leverage mutual connections or portfolio companies
3. Attend events where these investors are present
4. Personalize each outreach highlighting specific fit

## Priority Tier 2: Medium Priority

**Target Timeline:** Weeks 3-4

**Focus:** {len(medium_priority)} investors with good fit but may require more effort

**Approach:**
1. Cold email with strong value proposition
2. Engage on social media and thought leadership content
3. Request informational meetings
4. Follow up persistently but respectfully

## Priority Tier 3: Low Priority

**Target Timeline:** Weeks 5-6 (if needed)

**Focus:** Backup options if Tier 1 and 2 don't yield results

## Outreach Best Practices

### Email Template (First Contact)

```
Subject: [Company Name] - [One-line Value Prop] - Raising ${matches[0].investor_name if matches else 'X'}M

Hi [Investor Name],

I'm [Your Name], founder of [Company]. We're [one-sentence description].

We're [traction metric] and raising $[amount] to [key use of funds].

I believe [Investor Firm] would be a great fit because:
1. [Specific reason related to their portfolio/thesis]
2. [Another specific reason]

Would you be open to a 15-minute call next week?

Best,
[Your Name]
```

### Meeting Preparation

1. **Research the investor:**
   - Recent portfolio companies
   - Investment thesis
   - Decision-making process

2. **Prepare materials:**
   - 12-slide pitch deck
   - Financial model
   - Demo (if applicable)

3. **Know your metrics:**
   - Revenue, growth rate, customer count
   - Unit economics (CAC, LTV, churn)
   - Competitive differentiation

### Follow-up Cadence

- **Day 0:** Initial outreach
- **Day 3:** Polite follow-up if no response
- **Day 7:** Final follow-up with additional data/update
- **Day 14:** Move to next tier if no engagement

## Parallel Processing

**Recommended Approach:** Contact 5-10 investors simultaneously

- **Tier 1:** 5 investors per week
- **Tier 2:** 3-5 investors per week
- **Target:** 2-3 serious conversations leading to term sheets

## Key Metrics to Track

- **Response Rate:** Aim for >30%
- **Meeting Conversion:** Aim for >50% of responses
- **Partner Meeting:** Aim for >30% of first meetings
- **Term Sheet:** Aim for 2-3 from 20 conversations

## Timeline

**Week 1-2:** Tier 1 outreach
**Week 3-4:** Tier 2 outreach + Tier 1 follow-ups
**Week 5-6:** Tier 3 outreach + Partner meetings
**Week 7-8:** Due diligence + term sheet negotiations
**Week 9-10:** Final negotiations + close

**Total Estimated Timeline:** 8-12 weeks from outreach to close

---

*Note: Update this strategy weekly based on feedback and market conditions*
"""

        return strategy
