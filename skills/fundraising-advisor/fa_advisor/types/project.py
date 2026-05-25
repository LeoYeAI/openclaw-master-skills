"""
Project data types and schemas
"""

from enum import Enum
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, HttpUrl, field_validator


class FundingStage(str, Enum):
    """Funding stages"""
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B = "series-b"
    SERIES_C = "series-c"
    SERIES_D_PLUS = "series-d-plus"
    PRE_IPO = "pre-ipo"


class Industry(str, Enum):
    """Industry categories"""
    ENTERPRISE_SOFTWARE = "enterprise-software"
    CONSUMER_INTERNET = "consumer-internet"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    BIOTECH = "biotech"
    AI_ML = "ai-ml"
    ECOMMERCE = "ecommerce"
    HARDWARE = "hardware"
    BLOCKCHAIN = "blockchain"
    EDTECH = "edtech"
    CLEANTECH = "cleantech"
    LOGISTICS = "logistics"
    OTHER = "other"


class BusinessModel(str, Enum):
    """Business models"""
    B2B_SAAS = "b2b-saas"
    B2C = "b2c"
    MARKETPLACE = "marketplace"
    PLATFORM = "platform"
    TRANSACTION = "transaction"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"
    ENTERPRISE = "enterprise"
    HYBRID = "hybrid"


class ProductStage(str, Enum):
    """Product development stages"""
    IDEA = "idea"
    MVP = "mvp"
    LAUNCHED = "launched"
    SCALING = "scaling"


# Sub-models

class Competitor(BaseModel):
    """Competitor information"""
    name: str
    description: str
    differentiation: Optional[str] = None


class Founder(BaseModel):
    """Founder information"""
    name: str
    title: str
    background: str
    linkedin: Optional[HttpUrl] = None


class RevenueProjection(BaseModel):
    """Revenue projection for a specific year"""
    year: int = Field(ge=2020, le=2050)
    amount: float = Field(ge=0)


class UseOfFunds(BaseModel):
    """Use of funds breakdown"""
    category: str
    percentage: float = Field(ge=0, le=100)
    description: str


class PreviousRound(BaseModel):
    """Previous funding round information"""
    stage: str
    amount: float = Field(ge=0)
    date: str
    investors: List[str]
    valuation: float = Field(ge=0)


class Product(BaseModel):
    """Product information"""
    description: str
    stage: ProductStage
    key_features: List[str] = Field(min_length=1)
    unique_value_proposition: str
    customer_pain_points: List[str]


class Market(BaseModel):
    """Market information"""
    tam: float = Field(gt=0, description="Total Addressable Market in USD")
    sam: Optional[float] = Field(None, gt=0, description="Serviceable Addressable Market")
    som: Optional[float] = Field(None, gt=0, description="Serviceable Obtainable Market")
    market_growth_rate: float = Field(ge=0, le=10, description="Market CAGR (e.g., 0.35 for 35%)")
    competitors: List[Competitor] = Field(default_factory=list)


class Team(BaseModel):
    """Team information"""
    founders: List[Founder] = Field(min_length=1)
    team_size: int = Field(ge=1)
    key_hires: Optional[List[str]] = None


class FinancialMetrics(BaseModel):
    """Key financial metrics"""
    arr: Optional[float] = Field(None, ge=0, description="Annual Recurring Revenue")
    mrr: Optional[float] = Field(None, ge=0, description="Monthly Recurring Revenue")
    gross_margin: Optional[float] = Field(None, ge=0, le=1)
    customer_acquisition_cost: Optional[float] = Field(None, ge=0)
    lifetime_value: Optional[float] = Field(None, ge=0)
    churn_rate: Optional[float] = Field(None, ge=0, le=1)


class Revenue(BaseModel):
    """Revenue information"""
    current: float = Field(ge=0)
    projected: List[RevenueProjection]


class Expenses(BaseModel):
    """Expense information"""
    monthly: float = Field(gt=0)
    runway: int = Field(gt=0, description="Runway in months")


class Financials(BaseModel):
    """Financial information"""
    revenue: Revenue
    expenses: Expenses
    metrics: Optional[FinancialMetrics] = None


class Fundraising(BaseModel):
    """Fundraising information"""
    current_stage: FundingStage
    target_amount: float = Field(gt=0)
    minimum_amount: Optional[float] = Field(None, gt=0)
    current_valuation: Optional[float] = Field(None, gt=0)
    previous_rounds: Optional[List[PreviousRound]] = None
    use_of_funds: List[UseOfFunds]

    @field_validator('use_of_funds')
    @classmethod
    def validate_use_of_funds_total(cls, v: List[UseOfFunds]) -> List[UseOfFunds]:
        """Validate that use of funds percentages sum to 100"""
        total = sum(item.percentage for item in v)
        if not (99 <= total <= 101):  # Allow small rounding errors
            raise ValueError(f"Use of funds percentages must sum to 100%, got {total}%")
        return v


class Traction(BaseModel):
    """Traction information"""
    customers: Optional[int] = Field(None, ge=0)
    users: Optional[int] = Field(None, ge=0)
    growth: Optional[str] = None
    partnerships: Optional[List[str]] = None
    awards: Optional[List[str]] = None
    press: Optional[List[str]] = None


# Main Project model

class Project(BaseModel):
    """
    Complete project/startup information

    This is the main data structure for a startup project seeking funding
    or being evaluated by investors.
    """
    # Basic Information
    name: str = Field(min_length=1)
    tagline: Optional[str] = None
    description: str = Field(min_length=10)
    founded_date: Optional[str] = None
    location: str
    website: Optional[HttpUrl] = None

    # Classification
    industry: Industry
    sub_industry: Optional[str] = None
    business_model: BusinessModel
    target_market: str

    # Detailed Information
    product: Product
    market: Market
    team: Team
    financials: Financials
    fundraising: Fundraising
    traction: Optional[Traction] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "CloudFlow AI",
                "tagline": "Enterprise AI Workflow Automation Platform",
                "description": "AI-driven workflow automation for enterprises",
                "location": "Shanghai, China",
                "industry": "enterprise-software",
                "business_model": "b2b-saas",
                "target_market": "Mid to large enterprises",
                "product": {
                    "description": "One-stop AI workflow platform",
                    "stage": "launched",
                    "key_features": ["Natural language workflow builder", "AI optimization"],
                    "unique_value_proposition": "90% lower implementation cost",
                    "customer_pain_points": ["High RPA implementation cost"]
                },
                "market": {
                    "tam": 50000000000,
                    "market_growth_rate": 0.35,
                    "competitors": []
                },
                "team": {
                    "founders": [
                        {
                            "name": "Zhang Ming",
                            "title": "CEO",
                            "background": "Former Alibaba Senior Expert"
                        }
                    ],
                    "team_size": 25
                },
                "financials": {
                    "revenue": {
                        "current": 1200000,
                        "projected": [{"year": 2024, "amount": 3000000}]
                    },
                    "expenses": {
                        "monthly": 150000,
                        "runway": 18
                    }
                },
                "fundraising": {
                    "current_stage": "series-a",
                    "target_amount": 10000000,
                    "use_of_funds": [
                        {
                            "category": "R&D",
                            "percentage": 40,
                            "description": "Product development"
                        },
                        {
                            "category": "Sales",
                            "percentage": 35,
                            "description": "Go to market"
                        },
                        {
                            "category": "Operations",
                            "percentage": 15,
                            "description": "General operations"
                        },
                        {
                            "category": "Reserve",
                            "percentage": 10,
                            "description": "Emergency buffer"
                        }
                    ]
                }
            }
        }
