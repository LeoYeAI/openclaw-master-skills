"""
OpenClaw FA Advisor Skill

A comprehensive Financial Advisor skill for primary market financing
"""

from fa_advisor.advisor import FAAdvisor
from fa_advisor.types.project import Project, FundingStage, Industry, BusinessModel
from fa_advisor.types.investor import Investor, InvestorType
from fa_advisor.types.models import (
    ProjectAssessment,
    ValuationResult,
    InvestmentMemo,
    PitchDeckOutline,
)

# Version
__version__ = "0.1.0"

# Exports
__all__ = [
    "FAAdvisor",
    "Project",
    "Investor",
    "FundingStage",
    "Industry",
    "BusinessModel",
    "InvestorType",
    "ProjectAssessment",
    "ValuationResult",
    "InvestmentMemo",
    "PitchDeckOutline",
]
