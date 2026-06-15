"""
Project Assessor - Evaluate startup projects for investment readiness
"""

import logging
from typing import List

from fa_advisor.types.project import Project
from fa_advisor.types.models import (
    ProjectAssessment,
    AssessmentScores,
    InvestmentReadiness
)

logger = logging.getLogger(__name__)


class ProjectAssessor:
    """
    Assess startup projects across multiple dimensions

    Scoring dimensions:
    - Team (founders, size, experience)
    - Market (TAM, growth, competition)
    - Product (stage, features, differentiation)
    - Traction (customers, revenue, growth)
    - Financials (metrics, runway, unit economics)
    """

    async def assess(self, project: Project) -> ProjectAssessment:
        """
        Comprehensive project assessment

        Returns:
            ProjectAssessment with scores, readiness, and recommendations
        """
        logger.info(f"Assessing project: {project.name}")

        # Calculate individual dimension scores
        team_score = self._assess_team(project)
        market_score = self._assess_market(project)
        product_score = self._assess_product(project)
        traction_score = self._assess_traction(project)
        financials_score = self._assess_financials(project)

        # Calculate overall score
        overall_score = (
            team_score + market_score + product_score +
            traction_score + financials_score
        ) / 5

        scores = AssessmentScores(
            team=team_score,
            market=market_score,
            product=product_score,
            traction=traction_score,
            financials=financials_score,
            overall=overall_score
        )

        # Determine investment readiness
        readiness = self._determine_readiness(overall_score)

        # Identify strengths and weaknesses
        strengths = self._identify_strengths(project, scores)
        weaknesses = self._identify_weaknesses(project, scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(project, scores, weaknesses)

        # Generate summary
        summary = self._generate_summary(project, scores, readiness)

        return ProjectAssessment(
            scores=scores,
            investment_readiness=readiness,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            summary=summary
        )

    def _assess_team(self, project: Project) -> float:
        """Assess team quality (0-100)"""
        score = 0.0

        # Founder quality (40 points)
        founders = project.team.founders
        if len(founders) >= 2:
            score += 15  # Multiple founders
        elif len(founders) == 1:
            score += 8

        # Check for relevant experience in founder backgrounds
        for founder in founders:
            if any(keyword in founder.background.lower()
                   for keyword in ['founder', 'ceo', 'cto', 'vp', 'director']):
                score += 10
                break

        # LinkedIn presence
        if any(f.linkedin for f in founders):
            score += 5

        # Team size (30 points)
        team_size = project.team.team_size
        if team_size >= 20:
            score += 30
        elif team_size >= 10:
            score += 25
        elif team_size >= 5:
            score += 20
        elif team_size >= 3:
            score += 15
        else:
            score += 10

        # Key hires (15 points)
        if project.team.key_hires and len(project.team.key_hires) > 0:
            score += 15

        # Balance check (15 points)
        if len(founders) >= 2 and team_size >= 5:
            score += 15  # Good founder-team balance

        return min(score, 100)

    def _assess_market(self, project: Project) -> float:
        """Assess market opportunity (0-100)"""
        score = 0.0
        market = project.market

        # TAM size (40 points)
        tam = market.tam
        if tam >= 50_000_000_000:  # $50B+
            score += 40
        elif tam >= 10_000_000_000:  # $10B+
            score += 35
        elif tam >= 1_000_000_000:  # $1B+
            score += 30
        elif tam >= 100_000_000:  # $100M+
            score += 20
        else:
            score += 10

        # Growth rate (30 points)
        growth_rate = market.market_growth_rate
        if growth_rate >= 0.4:  # 40%+
            score += 30
        elif growth_rate >= 0.25:  # 25%+
            score += 25
        elif growth_rate >= 0.15:  # 15%+
            score += 20
        elif growth_rate >= 0.05:  # 5%+
            score += 10
        else:
            score += 5

        # Competition analysis (20 points)
        competitors = market.competitors
        if len(competitors) == 0:
            score += 10  # Blue ocean (but maybe risky)
        elif 1 <= len(competitors) <= 3:
            score += 20  # Good competitive position
        elif len(competitors) <= 5:
            score += 15  # Competitive but manageable
        else:
            score += 5  # Highly competitive

        # SAM/SOM provided (10 points)
        if market.sam and market.som:
            score += 10  # Detailed market analysis

        return min(score, 100)

    def _assess_product(self, project: Project) -> float:
        """Assess product maturity (0-100)"""
        score = 0.0
        product = project.product

        # Product stage (40 points)
        stage_scores = {
            'idea': 10,
            'mvp': 25,
            'launched': 35,
            'scaling': 40
        }
        score += stage_scores.get(product.stage.value, 10)

        # Key features (20 points)
        num_features = len(product.key_features)
        if num_features >= 5:
            score += 20
        elif num_features >= 3:
            score += 15
        elif num_features >= 1:
            score += 10

        # Clear value proposition (20 points)
        uvp_length = len(product.unique_value_proposition)
        if uvp_length >= 50:
            score += 20
        elif uvp_length >= 20:
            score += 15
        else:
            score += 5

        # Pain points identified (20 points)
        pain_points = product.customer_pain_points
        if len(pain_points) >= 3:
            score += 20
        elif len(pain_points) >= 2:
            score += 15
        elif len(pain_points) >= 1:
            score += 10

        return min(score, 100)

    def _assess_traction(self, project: Project) -> float:
        """Assess market traction (0-100)"""
        score = 0.0
        traction = project.traction
        revenue = project.financials.revenue.current

        # Revenue (50 points)
        if revenue >= 5_000_000:  # $5M+
            score += 50
        elif revenue >= 1_000_000:  # $1M+
            score += 45
        elif revenue >= 500_000:  # $500K+
            score += 40
        elif revenue >= 100_000:  # $100K+
            score += 30
        elif revenue > 0:
            score += 20
        else:
            score += 10  # Pre-revenue

        # Customers (20 points)
        if traction and traction.customers:
            customers = traction.customers
            if customers >= 100:
                score += 20
            elif customers >= 50:
                score += 18
            elif customers >= 20:
                score += 15
            elif customers >= 10:
                score += 12
            elif customers >= 1:
                score += 8

        # Partnerships (15 points)
        if traction and traction.partnerships and len(traction.partnerships) > 0:
            score += 15

        # Press/Awards (15 points)
        media_count = 0
        if traction:
            if traction.awards:
                media_count += len(traction.awards)
            if traction.press:
                media_count += len(traction.press)

        if media_count >= 5:
            score += 15
        elif media_count >= 2:
            score += 10
        elif media_count >= 1:
            score += 5

        return min(score, 100)

    def _assess_financials(self, project: Project) -> float:
        """Assess financial health (0-100)"""
        score = 0.0
        financials = project.financials

        # Runway (30 points)
        runway = financials.expenses.runway
        if runway >= 18:
            score += 30
        elif runway >= 12:
            score += 25
        elif runway >= 6:
            score += 15
        elif runway >= 3:
            score += 5

        # Metrics available (30 points)
        metrics = financials.metrics
        if metrics:
            # Gross margin
            if metrics.gross_margin:
                if metrics.gross_margin >= 0.8:
                    score += 10
                elif metrics.gross_margin >= 0.6:
                    score += 8
                elif metrics.gross_margin >= 0.4:
                    score += 5

            # LTV:CAC ratio
            if metrics.lifetime_value and metrics.customer_acquisition_cost:
                ltv_cac = metrics.lifetime_value / metrics.customer_acquisition_cost
                if ltv_cac >= 3:
                    score += 10
                elif ltv_cac >= 2:
                    score += 7
                elif ltv_cac >= 1:
                    score += 3

            # Churn rate
            if metrics.churn_rate is not None:
                if metrics.churn_rate <= 0.03:
                    score += 10
                elif metrics.churn_rate <= 0.05:
                    score += 7
                elif metrics.churn_rate <= 0.10:
                    score += 3

        # Revenue projections (20 points)
        projections = financials.revenue.projected
        if len(projections) >= 3:
            score += 15
            # Check growth rate
            if len(projections) >= 2:
                growth = (projections[1].amount - projections[0].amount) / projections[0].amount
                if growth >= 2.0:  # 200%+ growth
                    score += 5
        elif len(projections) >= 1:
            score += 10

        # Funding efficiency (20 points)
        monthly_burn = financials.expenses.monthly
        revenue_current = financials.revenue.current
        if revenue_current > monthly_burn:
            score += 20  # Default profitability!
        elif monthly_burn > 0:
            burn_multiple = revenue_current / monthly_burn
            if burn_multiple >= 0.8:
                score += 15
            elif burn_multiple >= 0.5:
                score += 10
            elif burn_multiple >= 0.3:
                score += 5

        return min(score, 100)

    def _determine_readiness(self, overall_score: float) -> InvestmentReadiness:
        """Determine investment readiness level"""
        if overall_score >= 80:
            return InvestmentReadiness.HIGHLY_READY
        elif overall_score >= 65:
            return InvestmentReadiness.READY
        elif overall_score >= 50:
            return InvestmentReadiness.NEEDS_IMPROVEMENT
        else:
            return InvestmentReadiness.NOT_READY

    def _identify_strengths(self, project: Project, scores: AssessmentScores) -> List[str]:
        """Identify project strengths"""
        strengths = []

        if scores.team >= 75:
            strengths.append("Strong, experienced founding team")
        if scores.market >= 75:
            strengths.append("Large and rapidly growing market opportunity")
        if scores.product >= 75:
            strengths.append("Mature product with clear differentiation")
        if scores.traction >= 75:
            strengths.append("Solid market traction and customer validation")
        if scores.financials >= 75:
            strengths.append("Healthy financial metrics and runway")

        # Specific strengths
        if project.financials.revenue.current > 1_000_000:
            strengths.append(f"Significant revenue: ${project.financials.revenue.current:,.0f}")
        if project.market.tam >= 10_000_000_000:
            strengths.append(f"Massive TAM: ${project.market.tam / 1_000_000_000:.1f}B")
        if project.team.team_size >= 20:
            strengths.append(f"Substantial team size: {project.team.team_size} people")

        return strengths[:5]  # Top 5 strengths

    def _identify_weaknesses(self, project: Project, scores: AssessmentScores) -> List[str]:
        """Identify project weaknesses"""
        weaknesses = []

        if scores.team < 50:
            weaknesses.append("Team needs strengthening - consider key hires")
        if scores.market < 50:
            weaknesses.append("Market opportunity unclear or too small")
        if scores.product < 50:
            weaknesses.append("Product needs more development and differentiation")
        if scores.traction < 50:
            weaknesses.append("Limited market traction and customer validation")
        if scores.financials < 50:
            weaknesses.append("Financial metrics need improvement")

        # Specific weaknesses
        if project.financials.expenses.runway < 6:
            weaknesses.append(f"Short runway: only {project.financials.expenses.runway} months")
        if project.financials.revenue.current == 0:
            weaknesses.append("Pre-revenue - need customer validation")
        if len(project.market.competitors) > 5:
            weaknesses.append("Highly competitive market")

        return weaknesses[:5]  # Top 5 weaknesses

    def _generate_recommendations(
        self,
        project: Project,
        scores: AssessmentScores,
        weaknesses: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if scores.team < 70:
            recommendations.append("Strengthen team with key executive hires (VP Sales, Head of Product)")
        if scores.market < 70 and project.market.tam < 1_000_000_000:
            recommendations.append("Expand TAM analysis or pivot to larger market opportunity")
        if scores.product < 70:
            recommendations.append("Accelerate product development and gather more customer feedback")
        if scores.traction < 70 and project.financials.revenue.current < 500_000:
            recommendations.append("Focus on customer acquisition and revenue growth")
        if scores.financials < 70:
            if project.financials.expenses.runway < 12:
                recommendations.append("Extend runway through cost optimization or bridge funding")
            if project.financials.metrics and project.financials.metrics.churn_rate:
                if project.financials.metrics.churn_rate > 0.05:
                    recommendations.append("Improve customer retention - churn rate is high")

        # Stage-specific recommendations
        if project.fundraising.current_stage.value in ['pre-seed', 'seed']:
            recommendations.append("Build MVP and achieve product-market fit before scaling")

        return recommendations[:5]  # Top 5 recommendations

    def _generate_summary(
        self,
        project: Project,
        scores: AssessmentScores,
        readiness: InvestmentReadiness
    ) -> str:
        """Generate assessment summary"""
        stage = project.fundraising.current_stage.value.title()
        score = scores.overall

        summary = f"{project.name} is a {stage}-stage {project.industry.value} company "
        summary += f"with an overall assessment score of {score:.0f}/100, "
        summary += f"indicating {readiness.value} for fundraising. "

        # Highlight top dimension
        top_dimension = max(
            [('Team', scores.team), ('Market', scores.market),
             ('Product', scores.product), ('Traction', scores.traction),
             ('Financials', scores.financials)],
            key=lambda x: x[1]
        )
        summary += f"The company's strongest dimension is {top_dimension[0]} ({top_dimension[1]:.0f}/100)."

        return summary
