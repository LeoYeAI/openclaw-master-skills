"""
PDF Generator - Create PDF reports and documents
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from fa_advisor.types.models import (
    ProjectAssessment,
    ValuationResult,
    InvestmentMemo,
    PitchDeckOutline
)

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    PDF generation service using ReportLab

    Capabilities:
    - Assessment reports
    - Valuation analysis reports
    - Investment memos
    - Pitch deck documents
    """

    def __init__(self, page_size=letter):
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Score style (for large numbers)
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#2e7d32'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))

    async def generate_assessment_report(
        self,
        assessment: ProjectAssessment,
        company_name: str,
        output_path: str | Path
    ) -> Path:
        """
        Generate assessment report PDF

        Args:
            assessment: ProjectAssessment object
            company_name: Name of the company
            output_path: Output PDF path

        Returns:
            Path to generated PDF
        """
        output_path = Path(output_path)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build document content
        story = []

        # Title
        story.append(Paragraph(
            f"Investment Readiness Assessment",
            self.styles['CustomTitle']
        ))
        story.append(Paragraph(
            company_name,
            self.styles['CustomSubtitle']
        ))
        story.append(Paragraph(
            datetime.now().strftime("%B %d, %Y"),
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Overall Score
        story.append(Paragraph(
            "Overall Score",
            self.styles['Heading2']
        ))
        story.append(Paragraph(
            f"{assessment.scores.overall:.0f}/100",
            self.styles['ScoreStyle']
        ))
        story.append(Paragraph(
            f"<b>Investment Readiness:</b> {assessment.investment_readiness.value.title()}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Detailed Scores Table
        story.append(Paragraph(
            "Detailed Scores",
            self.styles['Heading2']
        ))

        scores_data = [
            ['Dimension', 'Score'],
            ['Team', f"{assessment.scores.team:.0f}/100"],
            ['Market', f"{assessment.scores.market:.0f}/100"],
            ['Product', f"{assessment.scores.product:.0f}/100"],
            ['Traction', f"{assessment.scores.traction:.0f}/100"],
            ['Financials', f"{assessment.scores.financials:.0f}/100"],
        ]

        scores_table = Table(scores_data, colWidths=[3 * inch, 2 * inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        story.append(scores_table)
        story.append(Spacer(1, 0.3 * inch))

        # Strengths
        story.append(Paragraph(
            "✓ Key Strengths",
            self.styles['Heading2']
        ))
        for strength in assessment.strengths:
            story.append(Paragraph(
                f"• {strength}",
                self.styles['Normal']
            ))
        story.append(Spacer(1, 0.2 * inch))

        # Weaknesses
        story.append(Paragraph(
            "⚠ Areas for Improvement",
            self.styles['Heading2']
        ))
        for weakness in assessment.weaknesses:
            story.append(Paragraph(
                f"• {weakness}",
                self.styles['Normal']
            ))
        story.append(Spacer(1, 0.2 * inch))

        # Recommendations
        story.append(Paragraph(
            "💡 Recommendations",
            self.styles['Heading2']
        ))
        for i, rec in enumerate(assessment.recommendations, 1):
            story.append(Paragraph(
                f"{i}. {rec}",
                self.styles['Normal']
            ))

        # Build PDF
        doc.build(story)

        logger.info(f"Assessment report generated: {output_path}")
        return output_path

    async def generate_valuation_report(
        self,
        valuation: ValuationResult,
        company_name: str,
        output_path: str | Path
    ) -> Path:
        """Generate valuation analysis report PDF"""
        output_path = Path(output_path)
        doc = SimpleDocTemplate(str(output_path), pagesize=self.page_size)

        story = []

        # Title
        story.append(Paragraph(
            "Valuation Analysis Report",
            self.styles['CustomTitle']
        ))
        story.append(Paragraph(company_name, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.5 * inch))

        # Recommended Valuation
        story.append(Paragraph("Recommended Valuation", self.styles['Heading2']))
        story.append(Paragraph(
            f"<b>Pre-Money:</b> ${valuation.recommended_valuation.pre_money:,.0f}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Post-Money:</b> ${valuation.recommended_valuation.post_money:,.0f}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(
            f"<b>Reasoning:</b> {valuation.recommended_valuation.reasoning}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Valuation Methods
        story.append(Paragraph("Valuation by Method", self.styles['Heading2']))
        methods_data = [['Method', 'Valuation', 'Confidence']]
        for method in valuation.valuation_by_method:
            methods_data.append([
                method.method,
                f"${method.valuation:,.0f}",
                method.confidence.title()
            ])

        methods_table = Table(methods_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
        methods_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(methods_table)
        story.append(Spacer(1, 0.3 * inch))

        # Deal Terms
        story.append(Paragraph("Suggested Deal Terms", self.styles['Heading2']))
        story.append(Paragraph(
            f"<b>Raise Amount:</b> ${valuation.deal_terms.raise_amount:,.0f}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Equity Dilution:</b> {valuation.deal_terms.equity_dilution * 100:.1f}%",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Investor Type:</b> {valuation.deal_terms.investor_type}",
            self.styles['Normal']
        ))

        doc.build(story)
        logger.info(f"Valuation report generated: {output_path}")
        return output_path

    async def generate_investment_memo(
        self,
        memo: InvestmentMemo,
        company_name: str,
        output_path: str | Path
    ) -> Path:
        """Generate investment memo PDF"""
        output_path = Path(output_path)
        doc = SimpleDocTemplate(str(output_path), pagesize=self.page_size)

        story = []

        # Title
        story.append(Paragraph("Investment Memo", self.styles['CustomTitle']))
        story.append(Paragraph(company_name, self.styles['CustomSubtitle']))
        story.append(Paragraph(
            datetime.now().strftime("%B %d, %Y"),
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['Heading2']))
        story.append(Paragraph(memo.executive_summary, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Recommendation
        story.append(Paragraph("Recommendation", self.styles['Heading2']))
        decision_color = {
            'pass': '#d32f2f',
            'maybe': '#f57c00',
            'proceed': '#388e3c',
            'strong-yes': '#1976d2'
        }.get(memo.recommendation.decision.value, '#000000')

        story.append(Paragraph(
            f'<font color="{decision_color}"><b>{memo.recommendation.decision.value.upper()}</b></font>',
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Confidence:</b> {memo.recommendation.confidence.title()}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))

        # Investment Highlights
        story.append(Paragraph("Investment Highlights", self.styles['Heading2']))
        for highlight in memo.investment_highlights:
            story.append(Paragraph(f"• {highlight}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Risks
        story.append(Paragraph("Key Risks", self.styles['Heading2']))
        for risk in memo.risks[:5]:  # Top 5 risks
            severity_color = {
                'low': '#4caf50',
                'medium': '#ff9800',
                'high': '#f44336',
                'critical': '#b71c1c'
            }.get(risk.severity.value, '#000000')

            story.append(Paragraph(
                f'<font color="{severity_color}">■</font> <b>{risk.category}</b>: {risk.description}',
                self.styles['Normal']
            ))
        story.append(Spacer(1, 0.2 * inch))

        # Next Steps
        story.append(Paragraph("Next Steps", self.styles['Heading2']))
        for i, step in enumerate(memo.recommendation.next_steps, 1):
            story.append(Paragraph(f"{i}. {step}", self.styles['Normal']))

        doc.build(story)
        logger.info(f"Investment memo generated: {output_path}")
        return output_path

    def format_currency(self, amount: float) -> str:
        """Format currency for display"""
        if amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"${amount / 1_000:.1f}K"
        return f"${amount:.0f}"
