"""
FA Advisor - Main class

Provides comprehensive financial advisory services for startups and investors
"""

import logging
from typing import List, Optional, Dict
from pathlib import Path

from fa_advisor.types.project import Project
from fa_advisor.types.investor import Investor
from fa_advisor.types.models import (
    ProjectAssessment,
    ValuationResult,
    PitchDeckOutline,
    InvestmentMemo,
    InvestorMatch,
)

from fa_advisor.modules.assessment import ProjectAssessor
from fa_advisor.modules.pitchdeck import PitchDeckGenerator
from fa_advisor.modules.valuation import ValuationEngine
from fa_advisor.modules.matching import InvestorMatcher
from fa_advisor.modules.analysis import InvestmentAnalyzer
from fa_advisor.pdf import (
    PDFParser,
    FinancialStatementParser,
    PDFGenerator,
    OCRService
)

logger = logging.getLogger(__name__)


class FAAdvisor:
    """
    FA Advisor - Main class

    Provides comprehensive financial advisory services for:
    - Startups seeking funding
    - Investors evaluating opportunities
    """

    def __init__(self, investors: Optional[List[Investor]] = None):
        """
        Initialize FA Advisor

        Args:
            investors: Optional list of investors for matching
        """
        # Core modules
        self.project_assessor = ProjectAssessor()
        self.pitch_deck_generator = PitchDeckGenerator()
        self.valuation_engine = ValuationEngine()
        self.investor_matcher = InvestorMatcher(investors or [])
        self.investment_analyzer = InvestmentAnalyzer()

        # PDF modules
        self.pdf_parser = PDFParser()
        self.financial_parser = FinancialStatementParser()
        self.pdf_generator = PDFGenerator()
        self.ocr_service = OCRService()

        logger.info("FA Advisor initialized")

    async def startup_package(
        self,
        project: Project,
        financial_pdf: Optional[str | Path] = None,
        generate_pdf: bool = True
    ) -> Dict:
        """
        Complete startup package: assessment + deck + valuation + investor matching

        Args:
            project: Project information
            financial_pdf: Optional PDF path for financial statement parsing
            generate_pdf: Whether to generate PDF reports

        Returns:
            Dict containing assessment, pitch_deck, business_plan, valuation,
            investor_matches, and outreach_strategy
        """
        print("\n🚀 Generating complete startup fundraising package...\n")

        # 1. Parse financial PDF if provided
        if financial_pdf:
            print(f"📄 Parsing financial PDF: {financial_pdf}")
            financial_result = await self.financial_parser.parse_financial_pdf(financial_pdf)
            if financial_result.success and financial_result.financial_data:
                # Update project financials with PDF data
                if financial_result.financial_data.revenue:
                    project.financials.revenue.current = financial_result.financial_data.revenue
                print("✅ Financial data extracted from PDF\n")

        # 2. Project Assessment
        print("📊 Step 1/4: Assessing project...")
        assessment = await self.project_assessor.assess(project)
        print(f"✅ Overall score: {assessment.scores.overall:.0f}/100 - {assessment.investment_readiness.value}\n")

        # 3. Pitch Deck & Business Plan
        print("📑 Step 2/4: Generating pitch deck and business plan...")
        pitch_deck = await self.pitch_deck_generator.generate_outline(project)
        business_plan = await self.pitch_deck_generator.generate_business_plan(project)
        print(f"✅ Generated {pitch_deck.total_slides}-slide pitch deck\n")

        # 4. Valuation Analysis
        print("💰 Step 3/4: Performing valuation analysis...")
        valuation = await self.valuation_engine.comprehensive_valuation(project)
        print(f"✅ Recommended pre-money valuation: {self._format_number(valuation.recommended_valuation.pre_money)}\n")

        # 5. Investor Matching
        print("🎯 Step 4/4: Matching with investors...")
        investor_matches = await self.investor_matcher.match_investors(project, top_n=20)
        outreach_strategy = self.investor_matcher.generate_outreach_strategy(investor_matches)
        print(f"✅ Found {len(investor_matches)} matching investors\n")

        result = {
            'assessment': assessment,
            'pitch_deck': pitch_deck,
            'business_plan': business_plan,
            'valuation': valuation,
            'investor_matches': investor_matches,
            'outreach_strategy': outreach_strategy,
        }

        # 6. Generate PDF reports if requested
        if generate_pdf:
            print("📝 Generating PDF reports...")
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            result['pdf_reports'] = {
                'assessment': await self.pdf_generator.generate_assessment_report(
                    assessment,
                    project.name,
                    output_dir / f"{project.name}_assessment.pdf"
                ),
                'valuation': await self.pdf_generator.generate_valuation_report(
                    valuation,
                    project.name,
                    output_dir / f"{project.name}_valuation.pdf"
                )
            }
            print("✅ PDF reports generated in 'output' directory\n")

        return result

    async def investor_package(
        self,
        project: Project,
        generate_pdf: bool = True
    ) -> Dict:
        """
        Investor package: analyze a deal from investor perspective

        Args:
            project: Project to analyze
            generate_pdf: Whether to generate PDF memo

        Returns:
            Dict containing memo, dd_checklist, and valuation
        """
        print("\n🔍 Generating investment analysis package...\n")

        # 1. Investment Memo
        print("📝 Step 1/3: Generating investment memo...")
        memo = await self.investment_analyzer.generate_investment_memo(project)
        print(f"✅ Investment recommendation: {memo.recommendation.decision.value.upper()}\n")

        # 2. Due Diligence Checklist
        print("✅ Step 2/3: Generating due diligence checklist...")
        dd_checklist = self.investment_analyzer.generate_due_diligence_checklist(project)
        print(f"✅ Generated {len(dd_checklist)}-item DD checklist\n")

        # 3. Valuation Analysis
        print("💰 Step 3/3: Performing valuation analysis...")
        valuation = await self.valuation_engine.comprehensive_valuation(project)
        print(f"✅ Fair valuation range: {self._format_number(valuation.recommended_valuation.pre_money)}\n")

        result = {
            'memo': memo,
            'dd_checklist': dd_checklist,
            'valuation': valuation,
        }

        # Generate PDF memo if requested
        if generate_pdf:
            print("📝 Generating PDF investment memo...")
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            result['pdf_memo'] = await self.pdf_generator.generate_investment_memo(
                memo,
                project.name,
                output_dir / f"{project.name}_investment_memo.pdf"
            )
            print("✅ PDF memo generated\n")

        return result

    async def quick_assessment(self, project: Project) -> ProjectAssessment:
        """Quick assessment - fast check of investment readiness"""
        assessment = await self.project_assessor.assess(project)

        print(f"\n📊 Quick Assessment: {project.name}")
        print("=" * 50)
        print(f"Overall Score: {assessment.scores.overall:.0f}/100")
        print(f"Investment Readiness: {assessment.investment_readiness.value.upper()}")
        print(f"\n🎯 Scores:")
        print(f"  Team:       {assessment.scores.team:.0f}/100")
        print(f"  Market:     {assessment.scores.market:.0f}/100")
        print(f"  Product:    {assessment.scores.product:.0f}/100")
        print(f"  Traction:   {assessment.scores.traction:.0f}/100")
        print(f"  Financials: {assessment.scores.financials:.0f}/100")

        print(f"\n✅ Strengths:")
        for s in assessment.strengths:
            print(f"  - {s}")

        print(f"\n⚠️  Weaknesses:")
        for w in assessment.weaknesses:
            print(f"  - {w}")

        print(f"\n💡 Recommendations:")
        for r in assessment.recommendations:
            print(f"  - {r}")

        return assessment

    # Individual service methods

    async def generate_pitch_deck(self, project: Project) -> PitchDeckOutline:
        """Generate pitch deck only"""
        return await self.pitch_deck_generator.generate_outline(project)

    async def generate_business_plan(self, project: Project) -> str:
        """Generate business plan only"""
        return await self.pitch_deck_generator.generate_business_plan(project)

    async def valuate(self, project: Project) -> ValuationResult:
        """Valuation analysis only"""
        return await self.valuation_engine.comprehensive_valuation(project)

    async def match_investors(
        self,
        project: Project,
        top_n: int = 20
    ) -> List[InvestorMatch]:
        """Match investors only"""
        return await self.investor_matcher.match_investors(project, top_n)

    async def analyze_for_investor(self, project: Project) -> InvestmentMemo:
        """Generate investment memo only"""
        return await self.investment_analyzer.generate_investment_memo(project)

    # PDF processing methods

    async def parse_pdf(self, pdf_path: str | Path):
        """Parse a PDF file (text + tables)"""
        return await self.pdf_parser.parse_pdf(pdf_path)

    async def parse_financial_pdf(self, pdf_path: str | Path):
        """Parse a financial statement PDF"""
        return await self.financial_parser.parse_financial_pdf(pdf_path)

    async def ocr_pdf(self, pdf_path: str | Path):
        """Perform OCR on a scanned PDF"""
        return await self.ocr_service.ocr_pdf(pdf_path)

    # Helper methods

    def _format_number(self, num: float) -> str:
        """Format large numbers"""
        if num >= 1_000_000_000:
            return f"${num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"${num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.1f}K"
        return f"${num:.0f}"
