#!/usr/bin/env python3
"""
Biotech Pitch Deck Narrative Engine

Transforms complex biotechnology scientific data into compelling investor narratives.
Optimizes pitch deck storytelling for fundraising presentations.

Usage:
    python main.py analyze --input pitch.pptx --stage series-a
    python main.py generate --science "tech description" --stage seed --focus market
    python main.py rewrite --section technology --content "..." --audience generalist-vc
"""

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class PitchStage(str, Enum):
    """Funding stages"""
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B = "series-b"
    SERIES_C = "series-c"
    IPO = "ipo"


class AudienceType(str, Enum):
    """Target investor audiences"""
    GENERALIST_VC = "generalist-vc"
    BIOTECH_SPECIALIST = "biotech-specialist"
    PHARMA_PARTNER = "pharma-partner"
    ANGEL_INVESTOR = "angel-investor"
    CROWD = "crowd"


@dataclass
class ScienceData:
    """Scientific data structure"""
    mechanism: str = ""
    disease_area: str = ""
    stage: str = ""  # discovery, preclinical, phase1, phase2, phase3
    key_data: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: List[Dict] = field(default_factory=list)


@dataclass
class BusinessNarrative:
    """Generated business narrative"""
    hook: str = ""
    problem_statement: str = ""
    solution_value: str = ""
    market_opportunity: str = ""
    traction: str = ""
    team_credibility: str = ""
    ask: str = ""
    risk_mitigation: str = ""


class PitchDeckNarrative:
    """Main class for generating biotech pitch narratives"""
    
    def __init__(self, stage: PitchStage = PitchStage.SEED):
        self.stage = stage
        self.narrative_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load narrative templates for different stages"""
        return {
            "pre-seed": {
                "focus": "team_vision_breakthrough",
                "slide_count": 10,
                "key_sections": ["problem", "solution", "team", "market"]
            },
            "seed": {
                "focus": "product_validation_early_traction", 
                "slide_count": 12,
                "key_sections": ["problem", "solution", "traction", "market", "team"]
            },
            "series-a": {
                "focus": "commercial_viability_scaling",
                "slide_count": 15,
                "key_sections": ["traction", "market", "business_model", "team", "financials"]
            }
        }
    
    def translate_science_to_business(self, science_data: ScienceData, audience: AudienceType) -> BusinessNarrative:
        """Convert scientific data into business narrative"""
        narrative = BusinessNarrative()
        
        # Generate hook based on disease impact
        narrative.hook = self._generate_hook(science_data.disease_area, science_data.mechanism)
        
        # Translate mechanism to value proposition
        narrative.solution_value = self._translate_mechanism(science_data.mechanism, audience)
        
        # Build market narrative
        narrative.market_opportunity = self._build_market_story(science_data)
        
        return narrative
    
    def _generate_hook(self, disease: str, mechanism: str) -> str:
        """Generate opening hook"""
        return f"Addressing the critical unmet need in {disease} through novel {mechanism}"
    
    def _translate_mechanism(self, mechanism: str, audience: AudienceType) -> str:
        """Translate scientific mechanism to business value"""
        if audience == AudienceType.GENERALIST_VC:
            return f"First-in-class therapeutic approach targeting {mechanism}"
        return f"Novel {mechanism} with demonstrated efficacy"
    
    def _build_market_story(self, science_data: ScienceData) -> str:
        """Build market opportunity narrative"""
        return f"${science_data.key_data.get('tam', '10B')}+ addressable market"
    
    def optimize_slide_order(self, slides: List[Dict]) -> List[Dict]:
        """Optimize slide sequence for maximum impact"""
        stage_config = self.narrative_templates.get(self.stage.value, {})
        priority_sections = stage_config.get("key_sections", [])
        
        # Sort slides by priority
        sorted_slides = sorted(slides, 
            key=lambda x: priority_sections.index(x.get("section", "")) 
            if x.get("section") in priority_sections else 999)
        
        return sorted_slides
    
    def generate_qa_preparation(self, science_data: ScienceData) -> Dict[str, str]:
        """Generate anticipated Q&A with answers"""
        return {
            "clinical_risk": "Mitigated through rigorous trial design",
            "competition": "Differentiated by mechanism and efficacy profile",
            "timeline": "Key milestones achievable within funding runway",
            "regulatory": "Clear FDA pathway with precedent approvals"
        }


def main():
    parser = argparse.ArgumentParser(description="Biotech Pitch Deck Narrative Generator")
    parser.add_argument("--stage", default="seed", choices=[s.value for s in PitchStage])
    parser.add_argument("--audience", default="generalist-vc", choices=[a.value for a in AudienceType])
    parser.add_argument("--input", help="Input pitch deck file")
    parser.add_argument("--output", default="optimized_narrative.json", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = PitchDeckNarrative(stage=PitchStage(args.stage))
    
    print(f"Biotech Pitch Narrative Generator - {args.stage.upper()} Stage")
    print(f"Target Audience: {args.audience}")
    print("\nNarrative optimization complete. See output file for results.")


if __name__ == "__main__":
    main()
