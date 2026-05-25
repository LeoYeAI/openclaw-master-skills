"""
Result models and data structures for analysis outputs
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class InvestmentReadiness(str, Enum):
    """Investment readiness levels"""
    NOT_READY = "not-ready"
    NEEDS_IMPROVEMENT = "needs-improvement"
    READY = "ready"
    HIGHLY_READY = "highly-ready"


class InvestmentDecision(str, Enum):
    """Investment decision recommendations"""
    PASS = "pass"
    MAYBE = "maybe"
    PROCEED = "proceed"
    STRONG_YES = "strong-yes"


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Assessment Models

class AssessmentScores(BaseModel):
    """Detailed assessment scores"""
    team: float = Field(ge=0, le=100)
    market: float = Field(ge=0, le=100)
    product: float = Field(ge=0, le=100)
    traction: float = Field(ge=0, le=100)
    financials: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class ProjectAssessment(BaseModel):
    """Complete project assessment results"""
    scores: AssessmentScores
    investment_readiness: InvestmentReadiness
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    summary: str


# Valuation Models

class ValuationMethod(BaseModel):
    """Valuation result from a specific method"""
    method: str
    valuation: float = Field(gt=0)
    confidence: str  # low, medium, high
    notes: Optional[str] = None


class RecommendedValuation(BaseModel):
    """Recommended valuation range"""
    pre_money: float = Field(gt=0)
    post_money: float = Field(gt=0)
    reasoning: str


class DealTerms(BaseModel):
    """Suggested deal terms"""
    raise_amount: float = Field(gt=0)
    equity_dilution: float = Field(ge=0, le=1)
    investor_type: str
    round_structure: Optional[str] = None


class ValuationResult(BaseModel):
    """Complete valuation analysis results"""
    valuation_by_method: List[ValuationMethod]
    recommended_valuation: RecommendedValuation
    deal_terms: DealTerms
    assumptions: List[str]
    caveats: List[str]


# Pitch Deck Models

class PitchSlide(BaseModel):
    """Individual pitch deck slide"""
    number: int = Field(ge=1)
    title: str
    key_points: List[str]
    notes: Optional[str] = None


class PitchDeckOutline(BaseModel):
    """Complete pitch deck outline"""
    slides: List[PitchSlide]
    total_slides: int
    target_audience: str
    estimated_duration: Optional[str] = None  # e.g., "15-20 minutes"


# Investor Matching Models

class InvestorMatch(BaseModel):
    """Investor match result"""
    investor_name: str
    match_score: float = Field(ge=0, le=100)
    reasoning: str
    stage_fit: bool
    industry_fit: bool
    check_size_fit: bool
    geo_fit: bool
    warm_intro_available: Optional[bool] = None
    priority: str  # high, medium, low


class OutreachStrategy(BaseModel):
    """Investor outreach strategy"""
    priority_tier_1: List[str]
    priority_tier_2: List[str]
    priority_tier_3: List[str]
    timeline: str
    approach_notes: str


# Investment Analysis Models

class Risk(BaseModel):
    """Investment risk"""
    category: str
    description: str
    severity: RiskSeverity
    mitigation: Optional[str] = None


class InvestmentRecommendation(BaseModel):
    """Investment recommendation"""
    decision: InvestmentDecision
    confidence: str  # low, medium, high
    reasoning: str
    next_steps: List[str]


class InvestmentMemo(BaseModel):
    """Complete investment memo"""
    executive_summary: str
    investment_highlights: List[str]
    market_analysis: str
    product_assessment: str
    team_evaluation: str
    financial_analysis: str
    competitive_position: str
    risks: List[Risk]
    valuation_assessment: str
    recommendation: InvestmentRecommendation


class DueDiligenceItem(BaseModel):
    """Due diligence checklist item"""
    category: str
    item: str
    priority: str  # high, medium, low
    completed: bool = False
    notes: Optional[str] = None


# PDF Processing Models

class FinancialStatementData(BaseModel):
    """Extracted financial statement data from PDF"""
    revenue: Optional[float] = None
    expenses: Optional[float] = None
    profit: Optional[float] = None
    assets: Optional[float] = None
    liabilities: Optional[float] = None
    equity: Optional[float] = None
    period: Optional[str] = None
    raw_tables: Optional[List[List[str]]] = None


class PDFExtractionResult(BaseModel):
    """PDF extraction result"""
    success: bool
    text: Optional[str] = None
    tables: Optional[List[List[str]]] = None
    financial_data: Optional[FinancialStatementData] = None
    error: Optional[str] = None
