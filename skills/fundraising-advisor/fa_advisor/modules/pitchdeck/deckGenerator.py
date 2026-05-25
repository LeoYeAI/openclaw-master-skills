"""
Pitch Deck Generator - 生成专业的 Pitch Deck 和商业计划书
"""

import logging
from typing import List

from fa_advisor.types.project import Project
from fa_advisor.types.models import PitchDeckOutline, PitchSlide

logger = logging.getLogger(__name__)


class PitchDeckGenerator:
    """
    Pitch Deck 生成器
    
    生成标准的 12-slide pitch deck 和详细的商业计划书
    """

    async def generate_outline(self, project: Project) -> PitchDeckOutline:
        """
        生成 Pitch Deck 大纲
        
        标准的 12 页结构：
        1. Cover
        2. Problem
        3. Solution
        4. Market Opportunity
        5. Product
        6. Business Model
        7. Traction
        8. Competition
        9. Team
        10. Financials
        11. Ask
        12. Vision
        """
        logger.info(f"Generating pitch deck outline for {project.name}")

        slides = []

        # Slide 1: Cover
        slides.append(PitchSlide(
            number=1,
            title="Cover",
            key_points=[
                project.name,
                project.tagline or project.description[:100],
                f"Fundraising: {project.fundraising.current_stage.value.title()}",
                f"Target: ${project.fundraising.target_amount:,.0f}"
            ],
            notes="Company logo, tagline, and contact information"
        ))

        # Slide 2: Problem
        slides.append(PitchSlide(
            number=2,
            title="Problem",
            key_points=project.product.customer_pain_points[:5],
            notes="Clearly articulate the customer pain points you're solving"
        ))

        # Slide 3: Solution
        slides.append(PitchSlide(
            number=3,
            title="Solution",
            key_points=[
                project.product.unique_value_proposition,
                *project.product.key_features[:4]
            ],
            notes="Explain how your product solves the problem"
        ))

        # Slide 4: Market Opportunity
        market_points = [
            f"TAM: ${project.market.tam / 1_000_000_000:.1f}B"
        ]
        if project.market.sam:
            market_points.append(f"SAM: ${project.market.sam / 1_000_000_000:.1f}B")
        if project.market.som:
            market_points.append(f"SOM: ${project.market.som / 1_000_000:.0f}M")
        market_points.append(f"Market Growth: {project.market.market_growth_rate * 100:.0f}% CAGR")

        slides.append(PitchSlide(
            number=4,
            title="Market Opportunity",
            key_points=market_points,
            notes="Show the size and growth of your target market"
        ))

        # Slide 5: Product
        slides.append(PitchSlide(
            number=5,
            title="Product",
            key_points=[
                f"Stage: {project.product.stage.value.title()}",
                project.product.description,
                *[f"• {feature}" for feature in project.product.key_features]
            ],
            notes="Demo or screenshots of your product"
        ))

        # Slide 6: Business Model
        slides.append(PitchSlide(
            number=6,
            title="Business Model",
            key_points=[
                f"Model: {project.business_model.value.upper()}",
                f"Target Market: {project.target_market}",
                self._generate_revenue_stream(project)
            ],
            notes="Explain how you make money"
        ))

        # Slide 7: Traction
        traction_points = []
        if project.financials.revenue.current > 0:
            traction_points.append(f"ARR: ${project.financials.revenue.current:,.0f}")
        
        if project.traction:
            if project.traction.customers:
                traction_points.append(f"Customers: {project.traction.customers:,}")
            if project.traction.users:
                traction_points.append(f"Users: {project.traction.users:,}")
            if project.traction.growth:
                traction_points.append(f"Growth: {project.traction.growth}")
            if project.traction.partnerships:
                traction_points.append(f"Partners: {', '.join(project.traction.partnerships[:3])}")

        if not traction_points:
            traction_points = ["Early stage - building traction"]

        slides.append(PitchSlide(
            number=7,
            title="Traction",
            key_points=traction_points,
            notes="Show your growth metrics and momentum"
        ))

        # Slide 8: Competition
        comp_points = []
        if project.market.competitors:
            for comp in project.market.competitors[:3]:
                comp_points.append(f"{comp.name}: {comp.differentiation or comp.description}")
        else:
            comp_points = ["First mover in this space"]

        comp_points.append(f"Our Advantage: {project.product.unique_value_proposition}")

        slides.append(PitchSlide(
            number=8,
            title="Competition",
            key_points=comp_points,
            notes="Competitive landscape and your differentiation"
        ))

        # Slide 9: Team
        team_points = [
            f"{founder.name} - {founder.title}: {founder.background[:100]}"
            for founder in project.team.founders
        ]
        team_points.append(f"Team Size: {project.team.team_size} people")
        
        if project.team.key_hires:
            team_points.append(f"Key Hires: {', '.join(project.team.key_hires)}")

        slides.append(PitchSlide(
            number=9,
            title="Team",
            key_points=team_points,
            notes="Highlight founders' expertise and team composition"
        ))

        # Slide 10: Financials
        financial_points = [
            f"Current ARR: ${project.financials.revenue.current:,.0f}",
            f"Monthly Burn: ${project.financials.expenses.monthly:,.0f}",
            f"Runway: {project.financials.expenses.runway} months"
        ]

        if project.financials.revenue.projected:
            proj = project.financials.revenue.projected
            financial_points.append(
                f"Projected ARR (3Y): " +
                " → ".join([f"${p.amount / 1_000_000:.1f}M" for p in proj[:3]])
            )

        if project.financials.metrics:
            metrics = project.financials.metrics
            if metrics.gross_margin:
                financial_points.append(f"Gross Margin: {metrics.gross_margin * 100:.0f}%")

        slides.append(PitchSlide(
            number=10,
            title="Financials",
            key_points=financial_points,
            notes="Revenue, projections, and key metrics"
        ))

        # Slide 11: Ask (The Ask)
        ask_points = [
            f"Raising: ${project.fundraising.target_amount:,.0f}",
            f"Stage: {project.fundraising.current_stage.value.title()}",
            "",
            "Use of Funds:"
        ]

        for uof in project.fundraising.use_of_funds:
            ask_points.append(f"• {uof.category} ({uof.percentage}%): {uof.description}")

        slides.append(PitchSlide(
            number=11,
            title="The Ask",
            key_points=ask_points,
            notes="Funding amount and use of funds"
        ))

        # Slide 12: Vision
        slides.append(PitchSlide(
            number=12,
            title="Vision",
            key_points=[
                f"Mission: Transform {project.industry.value} with {project.product.description[:100]}",
                f"5-Year Goal: Become the leading {project.business_model.value} platform in {project.industry.value}",
                f"Exit Potential: ${project.market.tam / 100:,.0f} (1% of TAM)"
            ],
            notes="Long-term vision and impact"
        ))

        return PitchDeckOutline(
            slides=slides,
            total_slides=len(slides),
            target_audience="Seed/Series A investors",
            estimated_duration="15-20 minutes"
        )

    async def generate_business_plan(self, project: Project) -> str:
        """
        生成详细的商业计划书（Markdown 格式）
        """
        logger.info(f"Generating business plan for {project.name}")

        bp = f"""# Business Plan: {project.name}

{project.tagline or project.description}

**Location:** {project.location}
**Industry:** {project.industry.value}
**Business Model:** {project.business_model.value}

---

## Executive Summary

{project.name} is a {project.fundraising.current_stage.value}-stage {project.industry.value} company that {project.description}

We are currently raising ${project.fundraising.target_amount:,.0f} to {', '.join([uof.description for uof in project.fundraising.use_of_funds[:2]])}.

**Key Highlights:**
- **Market:** ${project.market.tam / 1_000_000_000:.1f}B TAM growing at {project.market.market_growth_rate * 100:.0f}% CAGR
- **Traction:** ${project.financials.revenue.current:,.0f} ARR{'with ' + str(project.traction.customers) + ' customers' if project.traction and project.traction.customers else ''}
- **Team:** {len(project.team.founders)} experienced founders, {project.team.team_size} team members

---

## 1. Problem

The {project.target_market} face several critical challenges:

"""

        for i, pain in enumerate(project.product.customer_pain_points, 1):
            bp += f"{i}. {pain}\n"

        bp += f"""

These problems result in significant inefficiencies, costs, and missed opportunities for our target customers.

---

## 2. Solution

{project.name} solves these problems through:

**Value Proposition:** {project.product.unique_value_proposition}

**Product Description:** {project.product.description}

**Key Features:**
"""

        for feature in project.product.key_features:
            bp += f"- {feature}\n"

        bp += f"""

**Product Stage:** {project.product.stage.value.title()}

---

## 3. Market Analysis

### Total Addressable Market (TAM)

- **TAM:** ${project.market.tam / 1_000_000_000:.2f}B
"""

        if project.market.sam:
            bp += f"- **SAM:** ${project.market.sam / 1_000_000_000:.2f}B\n"
        if project.market.som:
            bp += f"- **SOM:** ${project.market.som / 1_000_000:.0f}M\n"

        bp += f"""
- **Growth Rate:** {project.market.market_growth_rate * 100:.1f}% CAGR

### Target Market

{project.target_market}

### Market Dynamics

The {project.industry.value} market is experiencing rapid growth driven by increasing demand for {project.business_model.value} solutions.

---

## 4. Competition

"""

        if project.market.competitors:
            for comp in project.market.competitors:
                bp += f"""
### {comp.name}

**Description:** {comp.description}

**Our Differentiation:** {comp.differentiation or 'Not specified'}

"""
        else:
            bp += "We are pioneering a new category with limited direct competition.\n"

        bp += f"""

**Competitive Advantage:** {project.product.unique_value_proposition}

---

## 5. Business Model

**Model Type:** {project.business_model.value.upper()}

{self._generate_detailed_business_model(project)}

---

## 6. Go-to-Market Strategy

**Target Customers:** {project.target_market}

**Sales Strategy:** {"Enterprise sales with focus on mid to large companies" if 'enterprise' in project.target_market.lower() else "Product-led growth with self-service model"}

**Marketing Channels:**
- Content marketing and SEO
- Strategic partnerships
- Industry events and conferences
- Digital advertising

---

## 7. Traction & Metrics

"""

        if project.financials.revenue.current > 0:
            bp += f"**Current ARR:** ${project.financials.revenue.current:,.0f}\n"

        if project.traction:
            if project.traction.customers:
                bp += f"**Customers:** {project.traction.customers:,}\n"
            if project.traction.users:
                bp += f"**Users:** {project.traction.users:,}\n"
            if project.traction.growth:
                bp += f"**Growth:** {project.traction.growth}\n"
            if project.traction.partnerships:
                bp += f"**Partnerships:** {', '.join(project.traction.partnerships)}\n"
            if project.traction.awards:
                bp += f"**Awards:** {', '.join(project.traction.awards)}\n"

        if project.financials.metrics:
            metrics = project.financials.metrics
            bp += "\n**Key Metrics:**\n"
            if metrics.gross_margin:
                bp += f"- Gross Margin: {metrics.gross_margin * 100:.1f}%\n"
            if metrics.customer_acquisition_cost:
                bp += f"- CAC: ${metrics.customer_acquisition_cost:,.0f}\n"
            if metrics.lifetime_value:
                bp += f"- LTV: ${metrics.lifetime_value:,.0f}\n"
            if metrics.churn_rate:
                bp += f"- Churn Rate: {metrics.churn_rate * 100:.1f}%\n"

        bp += f"""

---

## 8. Team

"""

        for founder in project.team.founders:
            bp += f"""
### {founder.name} - {founder.title}

{founder.background}

"""

        bp += f"""
**Team Size:** {project.team.team_size} people

"""

        if project.team.key_hires:
            bp += f"**Key Hires Needed:** {', '.join(project.team.key_hires)}\n"

        bp += f"""

---

## 9. Financial Projections

### Current Financials

- **Revenue:** ${project.financials.revenue.current:,.0f} ARR
- **Monthly Burn:** ${project.financials.expenses.monthly:,.0f}
- **Runway:** {project.financials.expenses.runway} months

### Revenue Projections

"""

        for proj in project.financials.revenue.projected:
            bp += f"- **{proj.year}:** ${proj.amount:,.0f}\n"

        minimum_amount = project.fundraising.minimum_amount if project.fundraising.minimum_amount else project.fundraising.target_amount
        bp += f"""

---

## 10. Fundraising

### Current Round

- **Stage:** {project.fundraising.current_stage.value.title()}
- **Target Amount:** ${project.fundraising.target_amount:,.0f}
- **Minimum Amount:** ${minimum_amount:,.0f}

### Use of Funds

"""

        for uof in project.fundraising.use_of_funds:
            bp += f"- **{uof.category}** ({uof.percentage}%): {uof.description}\n"

        if project.fundraising.previous_rounds:
            bp += "\n### Previous Rounds\n\n"
            for round in project.fundraising.previous_rounds:
                bp += f"- **{round.stage.title()}** ({round.date}): ${round.amount:,.0f} at ${round.valuation:,.0f} valuation from {', '.join(round.investors)}\n"

        bp += f"""

---

## 11. Milestones & Roadmap

**Short-term (6 months):**
- Achieve ${(project.financials.revenue.current * 1.5):,.0f} ARR
- Grow team to {project.team.team_size + 10} people
- Launch 2-3 major features

**Medium-term (12 months):**
- Reach ${(project.financials.revenue.current * 3):,.0f} ARR
- Expand to new market segments
- Achieve profitability or raise Series B

**Long-term (3 years):**
- Become market leader in {project.industry.value}
- ${project.financials.revenue.projected[-1].amount if project.financials.revenue.projected else 20_000_000:,.0f} ARR
- Strategic exit or IPO

---

## 12. Exit Strategy

Potential exit opportunities include:
- Acquisition by larger {project.industry.value} companies
- IPO after achieving ${50_000_000:,.0f}+ ARR
- Strategic merger

**Comparable Exits:** [Industry examples]

---

## Appendix

### Key Risks

1. **Market Risk:** Competition from established players
2. **Execution Risk:** Scaling team and operations
3. **Technology Risk:** Maintaining product leadership

### Mitigation Strategies

- Strong IP and technology moat
- Experienced team with proven track record
- Strategic partnerships for distribution

---

*Document generated on {self._get_current_date()}*
*For more information: {project.website or 'Contact founders'}*
"""

        return bp

    def _generate_revenue_stream(self, project: Project) -> str:
        """生成收入流描述"""
        model = project.business_model.value

        if model == 'b2b-saas':
            return "Subscription-based SaaS model with monthly/annual contracts"
        elif model == 'marketplace':
            return "Transaction fees from both buyers and sellers"
        elif model == 'platform':
            return "Platform fees and premium features"
        elif model == 'subscription':
            return "Recurring subscription revenue"
        else:
            return f"{model} with multiple revenue streams"

    def _generate_detailed_business_model(self, project: Project) -> str:
        """生成详细的商业模式描述"""
        model = project.business_model.value

        descriptions = {
            'b2b-saas': """
We operate a B2B SaaS model with:
- **Pricing:** Tiered subscription plans based on usage/seats
- **Sales:** Combination of self-service and enterprise sales
- **Contract Length:** Monthly for SMBs, annual for enterprises
- **Revenue Recognition:** Recognized monthly over contract period
""",
            'marketplace': """
We operate a two-sided marketplace with:
- **Revenue Model:** Transaction fees (% of GMV)
- **Take Rate:** 10-20% depending on transaction size
- **Additional Revenue:** Premium features and advertising
""",
            'b2c': """
We serve consumers directly with:
- **Pricing:** Freemium model with premium upgrades
- **Monetization:** In-app purchases and subscriptions
- **Customer Acquisition:** Digital marketing and viral growth
"""
        }

        return descriptions.get(model, f"We operate a {model} business model.")

    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
