"""
Investment Analyzer - 投资分析模块（投资人视角）
"""

import logging
from typing import List

from fa_advisor.types.project import Project
from fa_advisor.types.models import (
    InvestmentMemo,
    InvestmentRecommendation,
    InvestmentDecision,
    Risk,
    RiskSeverity,
    DueDiligenceItem
)

logger = logging.getLogger(__name__)


class InvestmentAnalyzer:
    """
    投资分析器 - 从投资人视角分析项目
    
    生成：
    - 投资备忘录
    - 尽职调查清单
    - 风险评估
    - 投资建议
    """

    async def generate_investment_memo(self, project: Project) -> InvestmentMemo:
        """
        生成投资备忘录
        
        Args:
            project: 项目信息
            
        Returns:
            完整的投资备忘录
        """
        logger.info(f"Generating investment memo for {project.name}")

        # 1. Executive Summary
        executive_summary = self._generate_executive_summary(project)

        # 2. Investment Highlights
        highlights = self._identify_investment_highlights(project)

        # 3. Market Analysis
        market_analysis = self._analyze_market(project)

        # 4. Product Assessment
        product_assessment = self._assess_product(project)

        # 5. Team Evaluation
        team_evaluation = self._evaluate_team(project)

        # 6. Financial Analysis
        financial_analysis = self._analyze_financials(project)

        # 7. Competitive Position
        competitive_position = self._analyze_competition(project)

        # 8. Risk Assessment
        risks = self._identify_risks(project)

        # 9. Valuation Assessment
        valuation_assessment = self._assess_valuation(project)

        # 10. Investment Recommendation
        recommendation = self._generate_recommendation(
            project, highlights, risks, financial_analysis
        )

        return InvestmentMemo(
            executive_summary=executive_summary,
            investment_highlights=highlights,
            market_analysis=market_analysis,
            product_assessment=product_assessment,
            team_evaluation=team_evaluation,
            financial_analysis=financial_analysis,
            competitive_position=competitive_position,
            risks=risks,
            valuation_assessment=valuation_assessment,
            recommendation=recommendation
        )

    def _generate_executive_summary(self, project: Project) -> str:
        """生成执行摘要"""
        revenue = project.financials.revenue.current
        stage = project.fundraising.current_stage.value

        summary = (
            f"{project.name} is a {stage}-stage {project.industry.value} company "
            f"operating a {project.business_model.value} model. "
        )

        if revenue > 0:
            summary += f"The company has achieved ${revenue:,.0f} in ARR "
        else:
            summary += "The company is pre-revenue "

        if project.traction and project.traction.customers:
            summary += f"with {project.traction.customers} customers. "

        summary += (
            f"They are raising ${project.fundraising.target_amount:,.0f} "
            f"to {project.fundraising.use_of_funds[0].description.lower() if project.fundraising.use_of_funds else 'grow the business'}."
        )

        return summary

    def _identify_investment_highlights(self, project: Project) -> List[str]:
        """识别投资亮点"""
        highlights = []

        # 团队亮点
        if len(project.team.founders) >= 2:
            backgrounds = ", ".join([f.name for f in project.team.founders[:2]])
            highlights.append(
                f"Strong founding team: {backgrounds} with relevant experience"
            )

        # 市场亮点
        tam = project.market.tam
        if tam >= 10_000_000_000:
            highlights.append(
                f"Large addressable market: ${tam / 1_000_000_000:.1f}B TAM growing "
                f"at {project.market.market_growth_rate * 100:.0f}% CAGR"
            )

        # 产品亮点
        if project.product.stage.value in ['launched', 'scaling']:
            highlights.append(
                f"Proven product: {project.product.stage.value} with "
                f"{len(project.product.key_features)} key features"
            )

        # 牵引力亮点
        revenue = project.financials.revenue.current
        if revenue > 1_000_000:
            highlights.append(f"Strong traction: ${revenue:,.0f} ARR")
        elif revenue > 0:
            if len(project.financials.revenue.projected) > 0:
                growth = (project.financials.revenue.projected[0].amount - revenue) / revenue
                if growth > 1.0:
                    highlights.append(
                        f"High growth trajectory: {growth * 100:.0f}% projected YoY growth"
                    )

        # 财务效率
        if project.financials.metrics:
            metrics = project.financials.metrics
            if metrics.gross_margin and metrics.gross_margin > 0.7:
                highlights.append(
                    f"Strong unit economics: {metrics.gross_margin * 100:.0f}% gross margin"
                )
            
            if metrics.lifetime_value and metrics.customer_acquisition_cost:
                ltv_cac = metrics.lifetime_value / metrics.customer_acquisition_cost
                if ltv_cac >= 3:
                    highlights.append(
                        f"Efficient customer acquisition: {ltv_cac:.1f}x LTV/CAC ratio"
                    )

        # 合作伙伴
        if project.traction and project.traction.partnerships:
            highlights.append(
                f"Strategic partnerships: {', '.join(project.traction.partnerships[:3])}"
            )

        # 如果亮点不足，添加通用亮点
        if len(highlights) < 3:
            highlights.append(
                f"Clear value proposition: {project.product.unique_value_proposition}"
            )

        return highlights[:7]  # 最多7个亮点

    def _analyze_market(self, project: Project) -> str:
        """市场分析"""
        market = project.market
        
        analysis = f"""
**Market Size:**
- TAM: ${market.tam / 1_000_000_000:.2f}B
"""
        if market.sam:
            analysis += f"- SAM: ${market.sam / 1_000_000_000:.2f}B\n"
        
        analysis += f"""
- Growth Rate: {market.market_growth_rate * 100:.1f}% CAGR

**Market Dynamics:**

The {project.industry.value} market is experiencing {"rapid" if market.market_growth_rate > 0.2 else "steady"} growth, driven by increasing demand for {project.business_model.value} solutions.

**Target Customer:**

{project.target_market}

**Market Timing:**

{"Excellent" if market.market_growth_rate > 0.25 else "Good"} timing to enter the market given current growth trajectory and customer adoption trends.
"""

        return analysis

    def _assess_product(self, project: Project) -> str:
        """产品评估"""
        product = project.product
        
        assessment = f"""
**Product Stage:** {product.stage.value.title()}

**Description:**

{product.description}

**Key Features:**
"""
        for feature in product.key_features:
            assessment += f"- {feature}\n"

        assessment += f"""

**Value Proposition:**

{product.unique_value_proposition}

**Customer Pain Points Addressed:**
"""
        for pain in product.customer_pain_points:
            assessment += f"- {pain}\n"

        assessment += f"""

**Product Maturity:**

{"High - Product is proven and scaling" if product.stage.value == 'scaling' else "Medium - Product is launched and being validated" if product.stage.value == 'launched' else "Early - Product is in development"}
"""

        return assessment

    def _evaluate_team(self, project: Project) -> str:
        """团队评估"""
        team = project.team
        
        evaluation = f"""
**Founders ({len(team.founders)}):**
"""

        for founder in team.founders:
            evaluation += f"""
- **{founder.name}** - {founder.title}
  {founder.background}
"""

        evaluation += f"""

**Team Size:** {team.team_size} people

**Team Composition:**

{"Strong and well-balanced team" if team.team_size >= 10 else "Small but focused team"}

"""

        if team.key_hires:
            evaluation += f"**Key Hires Planned:** {', '.join(team.key_hires)}\n\n"

        evaluation += f"""
**Assessment:**

{"Excellent" if len(team.founders) >= 2 and team.team_size >= 20 else "Strong" if len(team.founders) >= 2 else "Adequate"} team with {"complementary" if len(team.founders) >= 2 else "focused"} skill sets. {"Founders have relevant domain experience." if any('founder' in f.background.lower() or 'ceo' in f.background.lower() for f in team.founders) else "Team is building relevant expertise."}
"""

        return evaluation

    def _analyze_financials(self, project: Project) -> str:
        """财务分析"""
        financials = project.financials
        revenue = financials.revenue.current
        
        analysis = f"""
**Current Financials:**

- Revenue (ARR): ${revenue:,.0f}
- Monthly Burn: ${financials.expenses.monthly:,.0f}
- Runway: {financials.expenses.runway} months
"""

        if financials.metrics:
            metrics = financials.metrics
            analysis += "\n**Key Metrics:**\n\n"
            
            if metrics.arr:
                analysis += f"- ARR: ${metrics.arr:,.0f}\n"
            if metrics.mrr:
                analysis += f"- MRR: ${metrics.mrr:,.0f}\n"
            if metrics.gross_margin:
                analysis += f"- Gross Margin: {metrics.gross_margin * 100:.1f}%\n"
            if metrics.customer_acquisition_cost:
                analysis += f"- CAC: ${metrics.customer_acquisition_cost:,.0f}\n"
            if metrics.lifetime_value:
                analysis += f"- LTV: ${metrics.lifetime_value:,.0f}\n"
                if metrics.customer_acquisition_cost:
                    ratio = metrics.lifetime_value / metrics.customer_acquisition_cost
                    analysis += f"- LTV/CAC: {ratio:.1f}x\n"
            if metrics.churn_rate:
                analysis += f"- Churn Rate: {metrics.churn_rate * 100:.2f}%\n"

        analysis += "\n**Revenue Projections:**\n\n"
        for proj in financials.revenue.projected:
            analysis += f"- {proj.year}: ${proj.amount:,.0f}\n"

        # 财务健康度评估
        if revenue > 1_000_000 and financials.expenses.runway >= 12:
            health = "Strong"
        elif revenue > 0 and financials.expenses.runway >= 6:
            health = "Moderate"
        else:
            health = "Needs Improvement"

        analysis += f"\n**Financial Health:** {health}\n"

        return analysis

    def _analyze_competition(self, project: Project) -> str:
        """竞争分析"""
        competitors = project.market.competitors
        
        if not competitors:
            return """
**Competitive Landscape:**

Early market with limited direct competition. This presents both an opportunity (blue ocean) and a risk (market validation needed).

**Competitive Advantage:**

First-mover advantage with unique value proposition.
"""

        analysis = "**Key Competitors:**\n\n"
        
        for comp in competitors[:5]:
            analysis += f"- **{comp.name}:** {comp.description}\n"
            if comp.differentiation:
                analysis += f"  - *Differentiation:* {comp.differentiation}\n"

        analysis += f"""

**Competitive Position:**

{"Strong" if len(competitors) <= 3 else "Moderate" if len(competitors) <= 5 else "Highly competitive"} market with {"clear" if len(competitors) <= 3 else "some"} differentiation.

**Moat:**

{project.product.unique_value_proposition}
"""

        return analysis

    def _identify_risks(self, project: Project) -> List[Risk]:
        """识别风险"""
        risks = []

        # 1. 执行风险
        if project.team.team_size < 10:
            risks.append(Risk(
                category="Execution",
                description="Small team size may limit execution capacity",
                severity=RiskSeverity.MEDIUM,
                mitigation="Plan to hire key positions with funding"
            ))

        # 2. 市场风险
        if len(project.market.competitors) > 5:
            risks.append(Risk(
                category="Competition",
                description="Highly competitive market with multiple established players",
                severity=RiskSeverity.HIGH,
                mitigation="Strong product differentiation and aggressive go-to-market"
            ))

        # 3. 财务风险
        if project.financials.expenses.runway < 6:
            risks.append(Risk(
                category="Financial",
                description=f"Limited runway of {project.financials.expenses.runway} months",
                severity=RiskSeverity.HIGH,
                mitigation="Immediate focus on extending runway through this raise"
            ))
        elif project.financials.expenses.runway < 12:
            risks.append(Risk(
                category="Financial",
                description="Moderate runway requiring efficient capital deployment",
                severity=RiskSeverity.MEDIUM,
                mitigation="Clear milestones to achieve before next raise"
            ))

        # 4. 产品风险
        if project.product.stage.value in ['idea', 'mvp']:
            risks.append(Risk(
                category="Product",
                description="Early product stage with unproven market fit",
                severity=RiskSeverity.HIGH,
                mitigation="Focus on customer validation and iterative development"
            ))

        # 5. 收入风险
        if project.financials.revenue.current == 0:
            risks.append(Risk(
                category="Revenue",
                description="Pre-revenue with unproven business model",
                severity=RiskSeverity.MEDIUM,
                mitigation="Clear path to first revenue and unit economics validation"
            ))

        # 6. 市场规模风险
        if project.market.tam < 1_000_000_000:
            risks.append(Risk(
                category="Market Size",
                description="Limited TAM may constrain growth potential",
                severity=RiskSeverity.MEDIUM,
                mitigation="Focus on market expansion or adjacent opportunities"
            ))

        # 7. 客户集中风险
        if project.traction and project.traction.customers and project.traction.customers < 10:
            risks.append(Risk(
                category="Customer Concentration",
                description="Limited customer base creates concentration risk",
                severity=RiskSeverity.MEDIUM,
                mitigation="Diversify customer base and reduce reliance on key accounts"
            ))

        # 确保至少有3个风险
        if len(risks) < 3:
            risks.append(Risk(
                category="Market Timing",
                description="Market adoption pace uncertainty",
                severity=RiskSeverity.LOW,
                mitigation="Monitor market signals and adjust strategy accordingly"
            ))

        return risks[:7]  # 最多7个主要风险

    def _assess_valuation(self, project: Project) -> str:
        """估值评估"""
        target_valuation = project.fundraising.current_valuation
        revenue = project.financials.revenue.current
        
        assessment = ""
        
        if target_valuation:
            assessment += f"**Company's Ask:** ${target_valuation:,.0f} pre-money\n\n"

        if revenue > 0:
            multiple = target_valuation / revenue if target_valuation else 0
            assessment += f"**Revenue Multiple:** {multiple:.1f}x ARR\n\n"

        assessment += f"""
**Valuation Assessment:**

{"Premium valuation justified by strong traction and growth" if revenue > 1_000_000 else "Early-stage valuation based primarily on team and market opportunity" if revenue == 0 else "Fair valuation for current stage and metrics"}

**Comparable Analysis:**

{"Above market" if target_valuation and revenue > 0 and (target_valuation / revenue) > 15 else "In line with market" if target_valuation else "To be determined"} based on {project.industry.value} benchmarks.

**Recommendation:**

{"Accept proposed valuation" if not target_valuation or revenue > 500_000 else "Negotiate 10-20% lower valuation" if revenue == 0 else "Valuation is reasonable"}
"""

        return assessment

    def _generate_recommendation(
        self,
        project: Project,
        highlights: List[str],
        risks: List[Risk],
        financial_analysis: str
    ) -> InvestmentRecommendation:
        """生成投资建议"""
        
        # 计算决策分数
        score = 0
        
        # 正面因素
        score += len(highlights) * 10  # 每个亮点+10分
        
        if project.financials.revenue.current > 1_000_000:
            score += 20
        elif project.financials.revenue.current > 0:
            score += 10
            
        if project.market.tam >= 10_000_000_000:
            score += 15
            
        if len(project.team.founders) >= 2:
            score += 10
            
        if project.product.stage.value in ['launched', 'scaling']:
            score += 10

        # 负面因素
        critical_risks = [r for r in risks if r.severity == RiskSeverity.CRITICAL]
        high_risks = [r for r in risks if r.severity == RiskSeverity.HIGH]
        
        score -= len(critical_risks) * 20
        score -= len(high_risks) * 10

        # 确定决策
        if score >= 70:
            decision = InvestmentDecision.STRONG_YES
            confidence = "high"
            reasoning = "Exceptional opportunity with strong team, market, and traction"
        elif score >= 50:
            decision = InvestmentDecision.PROCEED
            confidence = "high"
            reasoning = "Solid opportunity with clear path to value creation"
        elif score >= 30:
            decision = InvestmentDecision.MAYBE
            confidence = "medium"
            reasoning = "Promising but requires more validation and de-risking"
        else:
            decision = InvestmentDecision.PASS
            confidence = "high"
            reasoning = "Significant concerns outweigh potential upside"

        # 生成下一步行动
        next_steps = self._generate_next_steps(decision, project, risks)

        return InvestmentRecommendation(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            next_steps=next_steps
        )

    def _generate_next_steps(
        self,
        decision: InvestmentDecision,
        project: Project,
        risks: List[Risk]
    ) -> List[str]:
        """生成下一步行动"""
        steps = []

        if decision in [InvestmentDecision.STRONG_YES, InvestmentDecision.PROCEED]:
            steps.extend([
                "Schedule partner meeting for final decision",
                "Conduct customer reference calls",
                "Review financial model and projections in detail",
                "Perform technical due diligence",
                "Check founder references"
            ])
            
            if project.financials.revenue.current > 0:
                steps.append("Validate revenue metrics and customer retention")
            
            steps.append("Issue term sheet if all checks pass")

        elif decision == InvestmentDecision.MAYBE:
            steps.extend([
                "Request additional information on key concerns",
                "Schedule follow-up meeting with founders",
                "Monitor progress over next 1-2 quarters"
            ])
            
            # 针对特定风险的行动
            for risk in risks:
                if risk.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]:
                    steps.append(f"Address {risk.category.lower()} risk: {risk.mitigation}")

        else:  # PASS
            steps.extend([
                "Provide constructive feedback to founders",
                "Stay in touch for future rounds if situation improves"
            ])

        return steps[:7]  # 最多7个步骤

    def generate_due_diligence_checklist(self, project: Project) -> List[DueDiligenceItem]:
        """
        生成尽职调查清单
        
        Returns:
            按类别组织的DD清单
        """
        logger.info(f"Generating DD checklist for {project.name}")

        checklist = []

        # 1. Legal (高优先级)
        checklist.extend([
            DueDiligenceItem(
                category="Legal",
                item="Incorporation documents and cap table review",
                priority="high"
            ),
            DueDiligenceItem(
                category="Legal",
                item="Founder vesting schedules and agreements",
                priority="high"
            ),
            DueDiligenceItem(
                category="Legal",
                item="IP assignment and ownership verification",
                priority="high"
            ),
            DueDiligenceItem(
                category="Legal",
                item="Material contracts and customer agreements",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Legal",
                item="Employment agreements and stock option plans",
                priority="medium"
            ),
        ])

        # 2. Financial (高优先级)
        checklist.extend([
            DueDiligenceItem(
                category="Financial",
                item="Historical financial statements (P&L, balance sheet, cash flow)",
                priority="high"
            ),
            DueDiligenceItem(
                category="Financial",
                item="Revenue recognition policies and procedures",
                priority="high"
            ),
            DueDiligenceItem(
                category="Financial",
                item="Customer cohort analysis and retention metrics",
                priority="high"
            ),
            DueDiligenceItem(
                category="Financial",
                item="Unit economics breakdown (CAC, LTV, payback period)",
                priority="high"
            ),
            DueDiligenceItem(
                category="Financial",
                item="Budget vs. actual variance analysis",
                priority="medium"
            ),
        ])

        # 3. Product/Technical
        checklist.extend([
            DueDiligenceItem(
                category="Technical",
                item="Product demo and technical architecture review",
                priority="high" if project.product.stage.value in ['mvp', 'launched', 'scaling'] else "medium"
            ),
            DueDiligenceItem(
                category="Technical",
                item="Code repository access and quality assessment",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Technical",
                item="Security and data privacy compliance review",
                priority="high"
            ),
            DueDiligenceItem(
                category="Technical",
                item="Technology stack and scalability assessment",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Technical",
                item="Product roadmap and development timeline",
                priority="medium"
            ),
        ])

        # 4. Commercial
        checklist.extend([
            DueDiligenceItem(
                category="Commercial",
                item="Customer reference calls (3-5 customers)",
                priority="high" if project.traction and project.traction.customers and project.traction.customers > 5 else "medium"
            ),
            DueDiligenceItem(
                category="Commercial",
                item="Sales pipeline and conversion metrics review",
                priority="high" if project.financials.revenue.current > 0 else "medium"
            ),
            DueDiligenceItem(
                category="Commercial",
                item="Marketing and customer acquisition strategy assessment",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Commercial",
                item="Competitive positioning and market research",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Commercial",
                item="Partnership agreements and strategic relationships",
                priority="low"
            ),
        ])

        # 5. Team/HR
        checklist.extend([
            DueDiligenceItem(
                category="Team",
                item="Founder background checks and reference calls",
                priority="high"
            ),
            DueDiligenceItem(
                category="Team",
                item="Key employee retention and compensation review",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Team",
                item="Organization chart and hiring plan",
                priority="medium"
            ),
            DueDiligenceItem(
                category="Team",
                item="Company culture and employee satisfaction assessment",
                priority="low"
            ),
        ])

        # 6. Market
        checklist.extend([
            DueDiligenceItem(
                category="Market",
                item="Market size validation and growth projections",
                priority="high"
            ),
            DueDiligenceItem(
                category="Market",
                item="Regulatory and compliance landscape review",
                priority="medium" if project.industry.value in ['fintech', 'healthcare'] else "low"
            ),
            DueDiligenceItem(
                category="Market",
                item="Industry expert consultations",
                priority="medium"
            ),
        ])

        return checklist
