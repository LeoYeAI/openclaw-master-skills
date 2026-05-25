"""
Valuation Engine - 多方法估值分析

支持的估值方法：
1. Scorecard Method - 评分卡法
2. Berkus Method - Berkus 估值法
3. Risk Factor Summation - 风险因子求和法
4. Comparable Company Method - 可比公司法
"""

import logging
from typing import List

from fa_advisor.types.project import Project, FundingStage
from fa_advisor.types.models import (
    ValuationResult,
    ValuationMethod,
    RecommendedValuation,
    DealTerms
)

logger = logging.getLogger(__name__)


class ValuationEngine:
    """估值引擎 - 使用多种方法进行创业公司估值"""

    # 基准估值（按阶段）
    BASE_VALUATIONS = {
        FundingStage.PRE_SEED: 2_000_000,
        FundingStage.SEED: 5_000_000,
        FundingStage.SERIES_A: 15_000_000,
        FundingStage.SERIES_B: 40_000_000,
        FundingStage.SERIES_C: 100_000_000,
        FundingStage.SERIES_D_PLUS: 250_000_000,
        FundingStage.PRE_IPO: 500_000_000,
    }

    # 行业倍数（Revenue Multiple）
    INDUSTRY_MULTIPLES = {
        'enterprise-software': {'min': 8, 'max': 15, 'median': 10},
        'consumer-internet': {'min': 3, 'max': 8, 'median': 5},
        'fintech': {'min': 6, 'max': 12, 'median': 8},
        'healthcare': {'min': 5, 'max': 10, 'median': 7},
        'ai-ml': {'min': 10, 'max': 20, 'median': 12},
        'ecommerce': {'min': 2, 'max': 5, 'median': 3},
        'default': {'min': 5, 'max': 10, 'median': 7},
    }

    async def comprehensive_valuation(self, project: Project) -> ValuationResult:
        """综合估值分析 - 使用多种方法"""
        logger.info(f"Performing comprehensive valuation for {project.name}")

        valuations = []

        # 1. Scorecard Method（适用于所有阶段）
        scorecard = self._scorecard_method(project)
        valuations.append(scorecard)

        # 2. Berkus Method（适用于早期阶段）
        if project.fundraising.current_stage in [FundingStage.PRE_SEED, FundingStage.SEED]:
            berkus = self._berkus_method(project)
            valuations.append(berkus)

        # 3. Risk Factor Summation（适用于早期到中期）
        if project.fundraising.current_stage in [
            FundingStage.PRE_SEED, FundingStage.SEED,
            FundingStage.SERIES_A, FundingStage.SERIES_B
        ]:
            risk_factor = self._risk_factor_summation(project)
            valuations.append(risk_factor)

        # 4. Comparable Company Method（适用于有营收的公司）
        if project.financials.revenue.current > 0:
            comparable = self._comparable_company_method(project)
            valuations.append(comparable)

        # 计算推荐估值
        recommended = self._calculate_recommended_valuation(project, valuations)

        # 生成交易条款
        deal_terms = self._generate_deal_terms(project, recommended)

        # 生成假设和警告
        assumptions = self._generate_assumptions(project, valuations)
        caveats = self._generate_caveats(project)

        return ValuationResult(
            valuation_by_method=valuations,
            recommended_valuation=recommended,
            deal_terms=deal_terms,
            assumptions=assumptions,
            caveats=caveats
        )

    def _scorecard_method(self, project: Project) -> ValuationMethod:
        """评分卡估值法"""
        base_valuation = self.BASE_VALUATIONS.get(
            project.fundraising.current_stage, 5_000_000
        )

        team_factor = self._evaluate_team_factor(project)
        product_factor = self._evaluate_product_factor(project)
        market_factor = self._evaluate_market_factor(project)
        competition_factor = self._evaluate_competition_factor(project)
        sales_factor = self._evaluate_sales_factor(project)
        other_factor = self._evaluate_other_factors(project)

        total_adjustment = (
            team_factor * 0.30 + product_factor * 0.25 + market_factor * 0.25 +
            competition_factor * 0.10 + sales_factor * 0.10 + other_factor * 0.10
        )

        final_valuation = base_valuation * (1 + total_adjustment)
        confidence = "high" if abs(total_adjustment) < 0.3 else "medium"

        return ValuationMethod(
            method="Scorecard Method",
            valuation=final_valuation,
            confidence=confidence,
            notes=f"Base: ${base_valuation:,.0f}, Adjustment: {total_adjustment:+.0%}"
        )

    def _evaluate_team_factor(self, project: Project) -> float:
        """评估团队因素 (-0.25 to +0.25)"""
        score = 0.0
        if len(project.team.founders) >= 2:
            score += 0.05
        if project.team.team_size >= 20:
            score += 0.08
        elif project.team.team_size >= 10:
            score += 0.05
        if project.team.key_hires:
            score += 0.04
        return min(max(score - 0.05, -0.25), 0.25)

    def _evaluate_product_factor(self, project: Project) -> float:
        """评估产品因素"""
        score = {'idea': -0.10, 'mvp': 0.0, 'launched': 0.10, 'scaling': 0.15}.get(
            project.product.stage.value, 0.0
        )
        if len(project.product.key_features) >= 5:
            score += 0.05
        return min(max(score, -0.25), 0.25)

    def _evaluate_market_factor(self, project: Project) -> float:
        """评估市场因素"""
        score = 0.0
        tam = project.market.tam
        if tam >= 50_000_000_000:
            score += 0.15
        elif tam >= 10_000_000_000:
            score += 0.10
        if project.market.market_growth_rate >= 0.3:
            score += 0.10
        return min(max(score, -0.25), 0.25)

    def _evaluate_competition_factor(self, project: Project) -> float:
        """评估竞争因素"""
        num = len(project.market.competitors)
        if num == 0:
            return 0.05
        elif num <= 3:
            return 0.10
        elif num > 5:
            return -0.10
        return 0.0

    def _evaluate_sales_factor(self, project: Project) -> float:
        """评估销售因素"""
        revenue = project.financials.revenue.current
        if revenue > 1_000_000:
            return 0.10
        elif revenue > 100_000:
            return 0.05
        return -0.05 if revenue == 0 else 0.0

    def _evaluate_other_factors(self, project: Project) -> float:
        """评估其他因素"""
        score = 0.0
        if project.traction and project.traction.partnerships:
            score += 0.03 * min(len(project.traction.partnerships), 3)
        return min(max(score, -0.10), 0.10)

    def _berkus_method(self, project: Project) -> ValuationMethod:
        """Berkus 估值法（适用于早期阶段）"""
        valuation = 0.0

        # 1. 商业模式 ($0-500K)
        valuation += 400_000 if project.business_model.value in ['b2b-saas', 'marketplace'] else 250_000

        # 2. 产品/技术
        product_value = {'idea': 100_000, 'mvp': 300_000, 'launched': 450_000, 'scaling': 500_000}
        valuation += product_value.get(project.product.stage.value, 200_000)

        # 3. 管理团队
        team_value = 200_000 if len(project.team.founders) >= 2 else 100_000
        if project.team.team_size >= 5:
            team_value += 150_000
        valuation += min(team_value, 500_000)

        # 4. 战略关系
        if project.traction and project.traction.partnerships:
            valuation += min(len(project.traction.partnerships) * 150_000, 500_000)

        # 5. 产品推出/销售
        revenue = project.financials.revenue.current
        if revenue > 500_000:
            valuation += 500_000
        elif revenue > 100_000:
            valuation += 400_000
        elif revenue > 0:
            valuation += 300_000
        else:
            valuation += 100_000

        return ValuationMethod(
            method="Berkus Method",
            valuation=valuation,
            confidence="medium",
            notes="Early-stage valuation using Berkus Method"
        )

    def _risk_factor_summation(self, project: Project) -> ValuationMethod:
        """风险因子求和法"""
        base_valuation = self.BASE_VALUATIONS.get(
            project.fundraising.current_stage, 5_000_000
        )

        risks = {
            'management': 1 if len(project.team.founders) >= 2 else -1,
            'stage': {'idea': -2, 'mvp': -1, 'launched': 1, 'scaling': 2}.get(
                project.product.stage.value, 0
            ),
            'sales_marketing': 2 if project.financials.revenue.current > 1_000_000 else -1,
            'funding': 2 if project.financials.expenses.runway >= 18 else 0,
            'competition': 1 if len(project.market.competitors) <= 3 else -1,
            'technology': 1 if project.product.stage.value in ['launched', 'scaling'] else 0,
        }

        total_risk = sum(risks.values())
        adjustment = total_risk * 0.05
        final_valuation = base_valuation * (1 + adjustment)

        return ValuationMethod(
            method="Risk Factor Summation",
            valuation=final_valuation,
            confidence="medium",
            notes=f"Risk adjustment: {adjustment:+.0%}"
        )

    def _comparable_company_method(self, project: Project) -> ValuationMethod:
        """可比公司估值法"""
        revenue = project.financials.revenue.current
        multiples = self.INDUSTRY_MULTIPLES.get(
            project.industry.value, self.INDUSTRY_MULTIPLES['default']
        )

        # 根据增长率调整倍数
        growth_adjustment = 0.0
        if len(project.financials.revenue.projected) >= 1:
            next_year = project.financials.revenue.projected[0].amount
            if revenue > 0:
                growth_rate = (next_year - revenue) / revenue
                if growth_rate > 1.0:
                    growth_adjustment = 0.3
                elif growth_rate > 0.5:
                    growth_adjustment = 0.2

        adjusted_multiple = multiples['median'] * (1 + growth_adjustment)
        valuation = revenue * adjusted_multiple

        return ValuationMethod(
            method="Comparable Company",
            valuation=valuation,
            confidence="high" if revenue > 1_000_000 else "medium",
            notes=f"Revenue: ${revenue:,.0f}, Multiple: {adjusted_multiple:.1f}x"
        )

    def _calculate_recommended_valuation(
        self, project: Project, valuations: List[ValuationMethod]
    ) -> RecommendedValuation:
        """计算推荐估值（加权平均）"""
        weights = {'high': 1.5, 'medium': 1.0, 'low': 0.5}

        weighted_sum = sum(v.valuation * weights.get(v.confidence, 1.0) for v in valuations)
        total_weight = sum(weights.get(v.confidence, 1.0) for v in valuations)

        pre_money = weighted_sum / total_weight if total_weight > 0 else 5_000_000
        post_money = pre_money + project.fundraising.target_amount

        methods_used = [v.method for v in valuations]
        reasoning = f"Weighted average of {len(valuations)} methods: {', '.join(methods_used)}"

        return RecommendedValuation(
            pre_money=pre_money,
            post_money=post_money,
            reasoning=reasoning
        )

    def _generate_deal_terms(
        self, project: Project, valuation: RecommendedValuation
    ) -> DealTerms:
        """生成交易条款建议"""
        raise_amount = project.fundraising.target_amount
        equity_dilution = raise_amount / valuation.post_money
        stage = project.fundraising.current_stage.value

        return DealTerms(
            raise_amount=raise_amount,
            equity_dilution=equity_dilution,
            investor_type=f"{stage.title()} stage VCs",
            round_structure="Lead investor + syndicate" if raise_amount > 3_000_000 else "Solo"
        )

    def _generate_assumptions(
        self, project: Project, valuations: List[ValuationMethod]
    ) -> List[str]:
        """生成估值假设"""
        return [
            f"Stage: {project.fundraising.current_stage.value.title()}",
            f"Industry: {project.industry.value}",
            f"Used {len(valuations)} valuation methods",
            "Current ARR: ${:,.0f}".format(project.financials.revenue.current) if project.financials.revenue.current > 0 else "Pre-revenue"
        ]

    def _generate_caveats(self, project: Project) -> List[str]:
        """生成估值警告"""
        caveats = [
            "Valuation is an estimate based on available information",
            "Actual valuation depends on market conditions",
            "Multiple methods used to triangulate fair value"
        ]
        if project.financials.revenue.current == 0:
            caveats.append("Pre-revenue valuations have higher uncertainty")
        return caveats
