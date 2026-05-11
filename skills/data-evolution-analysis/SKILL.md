---
name: "data-evolution-analysis"
description: "Analyze data evolution patterns in construction organizations. Assess digital maturity and data strategy for construction companies"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📚", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Evolution Analysis

## Overview

Based on DDC methodology (Chapter 1.1), this skill analyzes data evolution patterns in construction organizations, assessing digital maturity levels from paper-based workflows to fully data-driven operations.

**Book Reference:** "Эволюция использования данных в строительной отрасли" / "Evolution of Data Usage in Construction"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import json

class MaturityLevel(Enum):
    """Digital maturity levels based on DDC methodology"""
    LEVEL_0_PAPER = 0      # Paper-based, no digital tools
    LEVEL_1_BASIC = 1      # Basic digital (spreadsheets, email)
    LEVEL_2_STRUCTURED = 2  # Structured databases, some integration
    LEVEL_3_INTEGRATED = 3  # ERP/BIM integration, workflows
    LEVEL_4_AUTOMATED = 4   # Automated processes, ML/AI
    LEVEL_5_PREDICTIVE = 5  # Predictive analytics, digital twins

class DataCategory(Enum):
    """Categories of construction data"""
    DESIGN = "design"
    COST = "cost"
    SCHEDULE = "schedule"
    QUALITY = "quality"
    SAFETY = "safety"
    PROCUREMENT = "procurement"
    DOCUMENT = "document"
    COMMUNICATION = "communication"

@dataclass
class DataFlowAssessment:
    """Assessment of data flow in an organization"""
    category: DataCategory
    source_systems: List[str]
    storage_format: str
    integration_level: float  # 0-1
    automation_level: float   # 0-1
    data_quality_score: float # 0-1
    issues: List[str] = field(default_factory=list)

@dataclass
class MaturityAssessment:
    """Complete digital maturity assessment"""
    organization_name: str
    assessment_date: datetime
    overall_level: MaturityLevel
    category_scores: Dict[DataCategory, float]
    data_flows: List[DataFlowAssessment]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    roadmap: Dict[str, List[str]]


class DataEvolutionAnalyzer:
    """
    Analyze data evolution and digital maturity in construction organizations.
    Based on DDC methodology Chapter 1.1.
    """

    def __init__(self):
        self.assessment_criteria = self._load_criteria()
        self.evolution_stages = self._define_evolution_stages()

    def _load_criteria(self) -> Dict[DataCategory, Dict]:
        """Load assessment criteria for each category"""
        return {
            DataCategory.DESIGN: {
                "tools": ["CAD", "BIM", "Collaboration Platform"],
                "metrics": ["model_usage", "clash_detection", "design_reviews"],
                "weight": 0.20
            },
            DataCategory.COST: {
                "tools": ["Spreadsheets", "Estimating Software", "ERP"],
                "metrics": ["automation_level", "historical_data", "benchmarking"],
                "weight": 0.15
            },
            DataCategory.SCHEDULE: {
                "tools": ["Gantt Charts", "CPM Software", "4D BIM"],
                "metrics": ["resource_loading", "progress_tracking", "forecasting"],
                "weight": 0.15
            },
            DataCategory.QUALITY: {
                "tools": ["Checklists", "QC Software", "Defect Tracking"],
                "metrics": ["inspection_digitization", "defect_analytics", "compliance"],
                "weight": 0.12
            },
            DataCategory.SAFETY: {
                "tools": ["Incident Reports", "Safety Software", "IoT Sensors"],
                "metrics": ["incident_tracking", "predictive_safety", "training"],
                "weight": 0.12
            },
            DataCategory.PROCUREMENT: {
                "tools": ["RFQ Manual", "e-Procurement", "Supply Chain"],
                "metrics": ["vendor_management", "material_tracking", "integration"],
                "weight": 0.10
            },
            DataCategory.DOCUMENT: {
                "tools": ["File Shares", "DMS", "CDE"],
                "metrics": ["version_control", "access_control", "searchability"],
                "weight": 0.08
            },
            DataCategory.COMMUNICATION: {
                "tools": ["Email", "Collaboration", "Unified Platform"],
                "metrics": ["response_time", "transparency", "audit_trail"],
                "weight": 0.08
            }
        }

    def _define_evolution_stages(self) -> Dict[MaturityLevel, Dict]:
        """Define characteristics of each evolution stage"""
        return {
            MaturityLevel.LEVEL_0_PAPER: {
                "name": "Paper-Based",
                "description": "Manual, paper-based processes",
                "characteristics": [
                    "Physical document storage",
                    "Manual data entry",
                    "Limited data sharing",
                    "No real-time visibility"
                ],
                "typical_tools": ["Paper forms", "Physical filing"]
            },
            MaturityLevel.LEVEL_1_BASIC: {
                "name": "Basic Digital",
                "description": "Basic digitization with standalone tools",
                "characteristics": [
                    "Spreadsheets for calculations",
                    "Email for communication",
                    "File shares for storage",
                    "Manual data transfer between systems"
                ],
                "typical_tools": ["Excel", "Word", "Email", "File shares"]
            },
            MaturityLevel.LEVEL_2_STRUCTURED: {
                "name": "Structured Data",
                "description": "Structured databases and specialized software",
                "characteristics": [
                    "Department-specific software",
                    "Structured databases",
                    "Basic reporting",
                    "Some standardization"
                ],
                "typical_tools": ["CAD", "Estimating software", "Project software"]
            },
            MaturityLevel.LEVEL_3_INTEGRATED: {
                "name": "Integrated Systems",
                "description": "Connected systems with data flow",
                "characteristics": [
                    "ERP integration",
                    "BIM adoption",
                    "Automated workflows",
                    "Cross-department data sharing"
                ],
                "typical_tools": ["BIM", "ERP", "CDE", "BI dashboards"]
            },
            MaturityLevel.LEVEL_4_AUTOMATED: {
                "name": "Automated & Analytics",
                "description": "Automation and advanced analytics",
                "characteristics": [
                    "Automated data collection",
                    "Machine learning models",
                    "Predictive analytics",
                    "Real-time dashboards"
                ],
                "typical_tools": ["ML platforms", "IoT", "Advanced analytics"]
            },
            MaturityLevel.LEVEL_5_PREDICTIVE: {
                "name": "Predictive & Autonomous",
                "description": "AI-driven, predictive operations",
                "characteristics": [
                    "Digital twins",
                    "Autonomous decision support",
                    "Continuous optimization",
                    "Predictive maintenance"
                ],
                "typical_tools": ["Digital twins", "AI/ML", "Autonomous systems"]
            }
        }

    def assess_organization(
        self,
        organization_name: str,
        survey_responses: Dict[str, any],
        system_inventory: List[Dict],
        process_documentation: Optional[Dict] = None
    ) -> MaturityAssessment:
        """
        Perform comprehensive digital maturity assessment.

        Args:
            organization_name: Name of the organization
            survey_responses: Responses from maturity survey
            system_inventory: List of systems/tools in use
            process_documentation: Optional process documentation

        Returns:
            Complete maturity assessment
        """
        # Analyze data flows
        data_flows = self._analyze_data_flows(system_inventory, survey_responses)

        # Calculate category scores
        category_scores = self._calculate_category_scores(
            data_flows, survey_responses
        )

        # Determine overall maturity level
        overall_score = sum(
            score * self.assessment_criteria[cat]["weight"]
            for cat, score in category_scores.items()
        )
        overall_level = self._score_to_level(overall_score)

        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_gaps(category_scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_level, weaknesses, data_flows
        )

        # Create roadmap
        roadmap = self._create_roadmap(overall_level, recommendations)

        return MaturityAssessment(
            organization_name=organization_name,
            assessment_date=datetime.now(),
            overall_level=overall_level,
            category_scores=category_scores,
            data_flows=data_flows,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            roadmap=roadmap
        )

    def _analyze_data_flows(
        self,
        system_inventory: List[Dict],
        survey_responses: Dict
    ) -> List[DataFlowAssessment]:
        """Analyze data flows between systems"""
        flows = []

        for category in DataCategory:
            # Find systems for this category
            category_systems = [
                s for s in system_inventory
                if s.get("category") == category.value
            ]

            if not category_systems:
                flows.append(DataFlowAssessment(
                    category=category,
                    source_systems=[],
                    storage_format="none",
                    integration_level=0.0,
                    automation_level=0.0,
                    data_quality_score=0.0,
                    issues=["No systems identified for this category"]
                ))
                continue

            # Analyze integration and automation
            integration = self._calculate_integration_score(category_systems)
            automation = self._calculate_automation_score(
                category_systems, survey_responses
            )
            quality = survey_responses.get(
                f"{category.value}_data_quality", 0.5
            )

            # Identify issues
            issues = self._identify_flow_issues(
                category_systems, integration, automation
            )

            flows.append(DataFlowAssessment(
                category=category,
                source_systems=[s["name"] for s in category_systems],
                storage_format=category_systems[0].get("format", "unknown"),
                integration_level=integration,
                automation_level=automation,
                data_quality_score=quality,
                issues=issues
            ))

        return flows

    def _calculate_integration_score(
        self, systems: List[Dict]
    ) -> float:
        """Calculate integration score for systems"""
        if not systems:
            return 0.0

        total_integrations = sum(
            len(s.get("integrations", [])) for s in systems
        )
        max_integrations = len(systems) * 3  # Assume max 3 integrations per system

        return min(1.0, total_integrations / max_integrations)

    def _calculate_automation_score(
        self,
        systems: List[Dict],
        survey: Dict
    ) -> float:
        """Calculate automation score"""
        scores = []

        for system in systems:
            system_score = 0.0
            if system.get("has_api"):
                system_score += 0.3
            if system.get("automated_imports"):
                system_score += 0.3
            if system.get("automated_exports"):
                system_score += 0.2
            if system.get("workflow_automation"):
                system_score += 0.2
            scores.append(system_score)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_category_scores(
        self,
        data_flows: List[DataFlowAssessment],
        survey: Dict
    ) -> Dict[DataCategory, float]:
        """Calculate maturity score for each category"""
        scores = {}

        for flow in data_flows:
            # Combine different aspects
            tool_score = survey.get(f"{flow.category.value}_tool_maturity", 0.5)
            process_score = survey.get(f"{flow.category.value}_process_maturity", 0.5)

            category_score = (
                tool_score * 0.3 +
                process_score * 0.2 +
                flow.integration_level * 0.2 +
                flow.automation_level * 0.2 +
                flow.data_quality_score * 0.1
            )

            scores[flow.category] = category_score

        return scores

    def _score_to_level(self, score: float) -> MaturityLevel:
        """Convert numeric score to maturity level"""
        if score < 0.1:
            return MaturityLevel.LEVEL_0_PAPER
        elif score < 0.25:
            return MaturityLevel.LEVEL_1_BASIC
        elif score < 0.45:
            return MaturityLevel.LEVEL_2_STRUCTURED
        elif score < 0.65:
            return MaturityLevel.LEVEL_3_INTEGRATED
        elif score < 0.85:
            return MaturityLevel.LEVEL_4_AUTOMATED
        else:
            return MaturityLevel.LEVEL_5_PREDICTIVE

    def _identify_gaps(
        self,
        scores: Dict[DataCategory, float]
    ) -> tuple[List[str], List[str]]:
        """Identify strengths and weaknesses"""
        avg_score = sum(scores.values()) / len(scores)

        strengths = [
            f"{cat.value}: {score:.0%}"
            for cat, score in scores.items()
            if score > avg_score + 0.1
        ]

        weaknesses = [
            f"{cat.value}: {score:.0%}"
            for cat, score in scores.items()
            if score < avg_score - 0.1
        ]

        return strengths, weaknesses

    def _identify_flow_issues(
        self,
        systems: List[Dict],
        integration: float,
        automation: float
    ) -> List[str]:
        """Identify issues in data flow"""
        issues = []

        if integration < 0.3:
            issues.append("Low system integration - data silos likely")
        if automation < 0.3:
            issues.append("Manual data transfer required")
        if len(systems) > 3:
            issues.append("Multiple overlapping systems")

        return issues

    def _generate_recommendations(
        self,
        level: MaturityLevel,
        weaknesses: List[str],
        flows: List[DataFlowAssessment]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Level-specific recommendations
        level_recs = {
            MaturityLevel.LEVEL_0_PAPER: [
                "Implement basic digital tools (spreadsheets, file sharing)",
                "Digitize critical paper-based processes",
                "Train staff on basic digital skills"
            ],
            MaturityLevel.LEVEL_1_BASIC: [
                "Adopt specialized construction software",
                "Implement structured data storage",
                "Standardize data formats and naming conventions"
            ],
            MaturityLevel.LEVEL_2_STRUCTURED: [
                "Integrate key systems (ERP, PM, BIM)",
                "Implement Common Data Environment (CDE)",
                "Develop automated workflows"
            ],
            MaturityLevel.LEVEL_3_INTEGRATED: [
                "Implement advanced analytics and dashboards",
                "Explore IoT for automated data collection",
                "Develop machine learning models for prediction"
            ],
            MaturityLevel.LEVEL_4_AUTOMATED: [
                "Implement digital twin technology",
                "Deploy AI-driven decision support",
                "Enable predictive maintenance and operations"
            ],
            MaturityLevel.LEVEL_5_PREDICTIVE: [
                "Continuous optimization of AI models",
                "Expand autonomous decision-making",
                "Industry leadership and knowledge sharing"
            ]
        }

        recommendations.extend(level_recs.get(level, []))

        # Address specific weaknesses
        for flow in flows:
            if flow.integration_level < 0.3:
                recommendations.append(
                    f"Improve {flow.category.value} system integrations"
                )
            if flow.data_quality_score < 0.5:
                recommendations.append(
                    f"Implement data quality controls for {flow.category.value}"
                )

        return recommendations[:10]  # Top 10 recommendations

    def _create_roadmap(
        self,
        current_level: MaturityLevel,
        recommendations: List[str]
    ) -> Dict[str, List[str]]:
        """Create phased improvement roadmap"""
        return {
            "Phase 1 (0-6 months)": recommendations[:3],
            "Phase 2 (6-12 months)": recommendations[3:6],
            "Phase 3 (12-24 months)": recommendations[6:],
            "Target Level": [
                f"Move from {current_level.name} to "
                f"{MaturityLevel(min(current_level.value + 1, 5)).name}"
            ]
        }

    def compare_assessments(
        self,
        assessments: List[MaturityAssessment]
    ) -> Dict:
        """Compare multiple assessments over time or across organizations"""
        comparison = {
            "assessments": len(assessments),
            "levels": [a.overall_level.name for a in assessments],
            "trends": {},
            "best_practices": []
        }

        # Track category trends
        for category in DataCategory:
            scores = [a.category_scores[category] for a in assessments]
            comparison["trends"][category.value] = {
                "scores": scores,
                "improvement": scores[-1] - scores[0] if len(scores) > 1 else 0
            }

        return comparison

    def generate_report(
        self,
        assessment: MaturityAssessment
    ) -> str:
        """Generate executive summary report"""
        stage_info = self.evolution_stages[assessment.overall_level]

        report = f"""
# Digital Maturity Assessment Report
## {assessment.organization_name}

**Assessment Date:** {assessment.assessment_date.strftime('%Y-%m-%d')}
**Overall Maturity Level:** {assessment.overall_level.name} - {stage_info['name']}

### Executive Summary
{stage_info['description']}

### Category Scores
"""
        for cat, score in assessment.category_scores.items():
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            report += f"- {cat.value.title()}: {bar} {score:.0%}\n"

        report += "\n### Strengths\n"
        for strength in assessment.strengths:
            report += f"- {strength}\n"

        report += "\n### Areas for Improvement\n"
        for weakness in assessment.weaknesses:
            report += f"- {weakness}\n"

        report += "\n### Recommendations\n"
        for i, rec in enumerate(assessment.recommendations, 1):
            report += f"{i}. {rec}\n"

        report += "\n### Roadmap\n"
        for phase, items in assessment.roadmap.items():
            report += f"\n**{phase}**\n"
            for item in items:
                report += f"- {item}\n"

        return report


class DataEvolutionTracker:
    """Track data evolution over time"""

    def __init__(self, organization_name: str):
        self.organization = organization_name
        self.history: List[MaturityAssessment] = []
        self.milestones: List[Dict] = []

    def add_assessment(self, assessment: MaturityAssessment):
        """Add new assessment to history"""
        self.history.append(assessment)
        self._check_milestones(assessment)

    def _check_milestones(self, assessment: MaturityAssessment):
        """Check if any milestones were reached"""
        if len(self.history) > 1:
            prev = self.history[-2]

            # Level improvement
            if assessment.overall_level.value > prev.overall_level.value:
                self.milestones.append({
                    "date": assessment.assessment_date,
                    "type": "level_up",
                    "description": f"Advanced from {prev.overall_level.name} "
                                   f"to {assessment.overall_level.name}"
                })

            # Category improvements
            for cat in DataCategory:
                if assessment.category_scores[cat] - prev.category_scores[cat] > 0.2:
                    self.milestones.append({
                        "date": assessment.assessment_date,
                        "type": "category_improvement",
                        "description": f"Significant improvement in {cat.value}"
                    })

    def get_evolution_summary(self) -> Dict:
        """Get summary of evolution over time"""
        if not self.history:
            return {"error": "No assessments recorded"}

        return {
            "organization": self.organization,
            "first_assessment": self.history[0].assessment_date,
            "latest_assessment": self.history[-1].assessment_date,
            "starting_level": self.history[0].overall_level.name,
            "current_level": self.history[-1].overall_level.name,
            "total_assessments": len(self.history),
            "milestones": self.milestones,
            "level_progression": [a.overall_level.value for a in self.history]
        }
```

## Common Use Cases

### Assess Current Digital Maturity

```python
analyzer = DataEvolutionAnalyzer()

# Define systems in use
systems = [
    {"name": "AutoCAD", "category": "design", "has_api": False},
    {"name": "Revit", "category": "design", "has_api": True, "integrations": ["Navisworks"]},
    {"name": "Excel", "category": "cost", "has_api": False},
    {"name": "MS Project", "category": "schedule", "has_api": False},
    {"name": "Email", "category": "communication", "has_api": False}
]

# Survey responses (from questionnaire)
survey = {
    "design_tool_maturity": 0.6,
    "design_process_maturity": 0.5,
    "design_data_quality": 0.7,
    "cost_tool_maturity": 0.3,
    "cost_process_maturity": 0.4,
    "cost_data_quality": 0.5,
    "schedule_tool_maturity": 0.4,
    "schedule_process_maturity": 0.3,
    "schedule_data_quality": 0.4
}

assessment = analyzer.assess_organization(
    organization_name="Construction Co",
    survey_responses=survey,
    system_inventory=systems
)

print(f"Maturity Level: {assessment.overall_level.name}")
print(f"Recommendations: {assessment.recommendations[:3]}")
```

### Track Evolution Over Time

```python
tracker = DataEvolutionTracker("Construction Co")

# Add quarterly assessments
tracker.add_assessment(q1_assessment)
tracker.add_assessment(q2_assessment)
tracker.add_assessment(q3_assessment)

summary = tracker.get_evolution_summary()
print(f"Progress: {summary['starting_level']} → {summary['current_level']}")
print(f"Milestones: {len(summary['milestones'])}")
```

### Generate Executive Report

```python
report = analyzer.generate_report(assessment)
print(report)

# Save to file
with open("maturity_report.md", "w") as f:
    f.write(report)
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DataEvolutionAnalyzer` | Main assessment engine |
| `MaturityLevel` | 6 levels from paper to predictive |
| `DataCategory` | 8 categories (design, cost, schedule, etc.) |
| `DataFlowAssessment` | Analyze data flows per category |
| `MaturityAssessment` | Complete assessment results |
| `DataEvolutionTracker` | Track progress over time |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 1.1
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [data-silo-detection](../../Chapter-1.2/data-silo-detection/SKILL.md) to identify integration gaps
- Use [erp-integration-analysis](../../Chapter-1.2/erp-integration-analysis/SKILL.md) for system integration
- Use [digital-maturity-assessment](../../Chapter-5.1/digital-maturity-assessment/SKILL.md) for detailed assessments
