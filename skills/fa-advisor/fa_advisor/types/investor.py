"""
Investor data types and schemas
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class InvestorType(str, Enum):
    """Type of investor"""
    VC = "vc"
    PE = "pe"
    ANGEL = "angel"
    CVC = "cvc"  # Corporate VC
    FAMILY_OFFICE = "family-office"
    ACCELERATOR = "accelerator"


class InvestmentStyle(str, Enum):
    """Investment style"""
    LEAD = "lead"
    FOLLOW = "follow"
    SYNDICATE = "syndicate"


# Sub-models

class InvestmentStrategy(BaseModel):
    """Investment strategy and focus"""
    stages: List[str]
    industries: List[str]
    investment_range_min: float = Field(gt=0)
    investment_range_max: float = Field(gt=0)
    geographic_focus: List[str]
    business_models: Optional[List[str]] = None


class InvestmentStyle(BaseModel):
    """Investment style and approach"""
    lead_investor: bool
    hands_on: bool
    value_add: List[str] = Field(default_factory=list)


class PortfolioCompany(BaseModel):
    """Portfolio company information"""
    name: str
    industry: str
    stage: str
    status: Optional[str] = None  # active, exited, failed


class TeamMember(BaseModel):
    """Investor team member"""
    name: str
    title: str
    background: Optional[str] = None
    linkedin: Optional[HttpUrl] = None


class Contact(BaseModel):
    """Contact information"""
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[str] = None


# Main Investor model

class Investor(BaseModel):
    """
    Investor/VC firm information

    Complete information about an investment firm including
    strategy, portfolio, team, and contact details.
    """
    # Basic Information
    name: str = Field(min_length=1)
    type: InvestorType
    description: str
    headquarters: str
    founded: Optional[int] = Field(None, ge=1900, le=2100)

    # Investment Strategy
    strategy: InvestmentStrategy
    investment_style: InvestmentStyle

    # Portfolio & Track Record
    portfolio: Optional[List[PortfolioCompany]] = None
    total_aum: Optional[float] = Field(None, gt=0, description="Assets Under Management")
    fund_size: Optional[float] = Field(None, gt=0, description="Current fund size")

    # Team
    team: Optional[List[TeamMember]] = None

    # Contact
    contact: Optional[Contact] = None

    # Metadata
    notable_exits: Optional[List[str]] = None
    investment_thesis: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sequoia Capital China",
                "type": "vc",
                "description": "Leading venture capital firm",
                "headquarters": "Beijing, China",
                "founded": 2005,
                "strategy": {
                    "stages": ["seed", "series-a", "series-b"],
                    "industries": ["enterprise-software", "fintech", "ai-ml"],
                    "investment_range_min": 1000000,
                    "investment_range_max": 50000000,
                    "geographic_focus": ["China", "Southeast Asia"]
                },
                "investment_style": {
                    "lead_investor": True,
                    "hands_on": True,
                    "value_add": ["Strategic guidance", "Network access"]
                }
            }
        }
