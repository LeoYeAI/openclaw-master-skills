---
name: "data-silo-detection"
description: "Detect and map data silos in construction organizations. Identify disconnected data sources and integration opportunities"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔗", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Silo Detection

## Overview

Based on DDC methodology (Chapter 1.2), this skill detects and maps data silos in construction organizations, identifying disconnected data sources, duplicate data, and integration opportunities.

**Book Reference:** "Технологии и системы управления в современном строительстве" / "Technologies and Management Systems in Modern Construction"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
import json
from collections import defaultdict

class DataDomain(Enum):
    """Construction data domains"""
    DESIGN = "design"
    COST = "cost"
    SCHEDULE = "schedule"
    QUALITY = "quality"
    SAFETY = "safety"
    PROCUREMENT = "procurement"
    SITE = "site"
    DOCUMENT = "document"
    FINANCIAL = "financial"
    HR = "hr"

class SiloSeverity(Enum):
    """Severity level of data silo"""
    CRITICAL = "critical"      # Major business impact
    HIGH = "high"              # Significant inefficiency
    MEDIUM = "medium"          # Noticeable issues
    LOW = "low"                # Minor inconvenience

class DataSourceType(Enum):
    """Types of data sources"""
    DATABASE = "database"
    SPREADSHEET = "spreadsheet"
    FILE_SHARE = "file_share"
    CLOUD_APP = "cloud_app"
    DESKTOP_APP = "desktop_app"
    PAPER = "paper"
    EMAIL = "email"
    PERSONAL = "personal"

@dataclass
class DataSource:
    """Represents a data source in the organization"""
    id: str
    name: str
    type: DataSourceType
    domain: DataDomain
    owner: str
    department: str
    users: List[str]
    data_entities: List[str]
    connections: List[str] = field(default_factory=list)
    update_frequency: str = "unknown"
    access_level: str = "department"  # personal, department, organization
    has_api: bool = False
    last_modified: Optional[datetime] = None

@dataclass
class DataSilo:
    """Detected data silo"""
    id: str
    sources: List[DataSource]
    domain: DataDomain
    severity: SiloSeverity
    issue_type: str
    description: str
    impact: str
    affected_users: int
    affected_processes: List[str]
    recommendations: List[str]
    estimated_cost: Optional[float] = None

@dataclass
class DuplicateData:
    """Detected duplicate data across sources"""
    entity_name: str
    sources: List[str]
    discrepancy_rate: float  # 0-1
    master_source: Optional[str] = None
    issues: List[str] = field(default_factory=list)

@dataclass
class SiloAnalysis:
    """Complete silo analysis results"""
    organization: str
    analysis_date: datetime
    total_sources: int
    silos_detected: List[DataSilo]
    duplicates: List[DuplicateData]
    connectivity_score: float
    data_flow_gaps: List[Dict]
    priority_actions: List[str]
    integration_roadmap: Dict


class DataSiloDetector:
    """
    Detect and analyze data silos in construction organizations.
    Based on DDC methodology Chapter 1.2.
    """

    def __init__(self):
        self.domain_relationships = self._define_domain_relationships()
        self.critical_entities = self._define_critical_entities()

    def _define_domain_relationships(self) -> Dict[DataDomain, List[DataDomain]]:
        """Define expected relationships between domains"""
        return {
            DataDomain.DESIGN: [
                DataDomain.COST, DataDomain.SCHEDULE,
                DataDomain.PROCUREMENT, DataDomain.QUALITY
            ],
            DataDomain.COST: [
                DataDomain.DESIGN, DataDomain.SCHEDULE,
                DataDomain.FINANCIAL, DataDomain.PROCUREMENT
            ],
            DataDomain.SCHEDULE: [
                DataDomain.DESIGN, DataDomain.COST,
                DataDomain.SITE, DataDomain.HR
            ],
            DataDomain.PROCUREMENT: [
                DataDomain.COST, DataDomain.DESIGN,
                DataDomain.SITE, DataDomain.FINANCIAL
            ],
            DataDomain.SITE: [
                DataDomain.SCHEDULE, DataDomain.SAFETY,
                DataDomain.QUALITY, DataDomain.HR
            ],
            DataDomain.QUALITY: [
                DataDomain.DESIGN, DataDomain.SITE,
                DataDomain.DOCUMENT
            ],
            DataDomain.SAFETY: [
                DataDomain.SITE, DataDomain.HR,
                DataDomain.DOCUMENT
            ],
            DataDomain.FINANCIAL: [
                DataDomain.COST, DataDomain.PROCUREMENT,
                DataDomain.HR
            ]
        }

    def _define_critical_entities(self) -> Dict[str, List[DataDomain]]:
        """Define entities that should be shared across domains"""
        return {
            "project": [DataDomain.DESIGN, DataDomain.COST, DataDomain.SCHEDULE],
            "budget": [DataDomain.COST, DataDomain.FINANCIAL, DataDomain.PROCUREMENT],
            "schedule": [DataDomain.SCHEDULE, DataDomain.SITE, DataDomain.PROCUREMENT],
            "material": [DataDomain.DESIGN, DataDomain.COST, DataDomain.PROCUREMENT],
            "labor": [DataDomain.HR, DataDomain.COST, DataDomain.SCHEDULE],
            "subcontractor": [DataDomain.PROCUREMENT, DataDomain.COST, DataDomain.SCHEDULE],
            "rfi": [DataDomain.DESIGN, DataDomain.DOCUMENT, DataDomain.SITE],
            "change_order": [DataDomain.COST, DataDomain.DESIGN, DataDomain.SCHEDULE]
        }

    def detect_silos(
        self,
        organization: str,
        data_sources: List[DataSource],
        process_flows: Optional[List[Dict]] = None
    ) -> SiloAnalysis:
        """
        Detect data silos in the organization.

        Args:
            organization: Organization name
            data_sources: List of data sources to analyze
            process_flows: Optional business process flows

        Returns:
            Complete silo analysis
        """
        # Build connectivity graph
        connectivity = self._build_connectivity_graph(data_sources)

        # Detect isolated sources
        isolated_silos = self._detect_isolated_sources(
            data_sources, connectivity
        )

        # Detect domain silos
        domain_silos = self._detect_domain_silos(data_sources)

        # Detect duplicate data
        duplicates = self._detect_duplicates(data_sources)

        # Detect data flow gaps
        flow_gaps = self._detect_flow_gaps(
            data_sources, process_flows
        )

        # Calculate connectivity score
        connectivity_score = self._calculate_connectivity_score(
            data_sources, connectivity
        )

        # Combine all silos
        all_silos = isolated_silos + domain_silos

        # Prioritize silos
        prioritized_silos = self._prioritize_silos(all_silos)

        # Generate priority actions
        priority_actions = self._generate_priority_actions(
            prioritized_silos, duplicates
        )

        # Create integration roadmap
        roadmap = self._create_integration_roadmap(
            prioritized_silos, flow_gaps
        )

        return SiloAnalysis(
            organization=organization,
            analysis_date=datetime.now(),
            total_sources=len(data_sources),
            silos_detected=prioritized_silos,
            duplicates=duplicates,
            connectivity_score=connectivity_score,
            data_flow_gaps=flow_gaps,
            priority_actions=priority_actions,
            integration_roadmap=roadmap
        )

    def _build_connectivity_graph(
        self,
        sources: List[DataSource]
    ) -> Dict[str, Set[str]]:
        """Build graph of source connections"""
        graph = defaultdict(set)

        for source in sources:
            for connection in source.connections:
                graph[source.id].add(connection)
                graph[connection].add(source.id)

        return graph

    def _detect_isolated_sources(
        self,
        sources: List[DataSource],
        connectivity: Dict[str, Set[str]]
    ) -> List[DataSilo]:
        """Detect sources with no connections"""
        silos = []

        for source in sources:
            connections = len(connectivity.get(source.id, set()))

            if connections == 0:
                severity = SiloSeverity.CRITICAL if source.domain in [
                    DataDomain.COST, DataDomain.SCHEDULE
                ] else SiloSeverity.HIGH

                silos.append(DataSilo(
                    id=f"isolated_{source.id}",
                    sources=[source],
                    domain=source.domain,
                    severity=severity,
                    issue_type="isolated_source",
                    description=f"{source.name} has no connections to other systems",
                    impact="Data must be manually transferred, risking errors and delays",
                    affected_users=len(source.users),
                    affected_processes=self._get_affected_processes(source.domain),
                    recommendations=[
                        f"Connect {source.name} via API or ETL to related systems",
                        "Establish data synchronization schedule",
                        "Define master data source for shared entities"
                    ]
                ))
            elif connections == 1 and source.access_level == "personal":
                silos.append(DataSilo(
                    id=f"personal_{source.id}",
                    sources=[source],
                    domain=source.domain,
                    severity=SiloSeverity.MEDIUM,
                    issue_type="personal_silo",
                    description=f"{source.name} is a personal data store with limited access",
                    impact="Data not accessible to team, knowledge loss risk",
                    affected_users=1,
                    affected_processes=self._get_affected_processes(source.domain),
                    recommendations=[
                        "Move data to shared organizational repository",
                        "Implement access controls instead of isolation",
                        "Document data structure and usage"
                    ]
                ))

        return silos

    def _detect_domain_silos(
        self,
        sources: List[DataSource]
    ) -> List[DataSilo]:
        """Detect silos between domains that should be connected"""
        silos = []

        # Group sources by domain
        domain_sources = defaultdict(list)
        for source in sources:
            domain_sources[source.domain].append(source)

        # Check for missing domain connections
        for domain, related_domains in self.domain_relationships.items():
            domain_srcs = domain_sources.get(domain, [])

            for related in related_domains:
                related_srcs = domain_sources.get(related, [])

                if domain_srcs and related_srcs:
                    # Check if any connections exist between domains
                    has_connection = False
                    for src in domain_srcs:
                        for rel_src in related_srcs:
                            if rel_src.id in src.connections:
                                has_connection = True
                                break

                    if not has_connection:
                        silos.append(DataSilo(
                            id=f"domain_gap_{domain.value}_{related.value}",
                            sources=domain_srcs + related_srcs,
                            domain=domain,
                            severity=SiloSeverity.HIGH,
                            issue_type="domain_disconnect",
                            description=f"No data flow between {domain.value} and {related.value}",
                            impact="Related information not synchronized, decision delays",
                            affected_users=sum(len(s.users) for s in domain_srcs + related_srcs),
                            affected_processes=self._get_affected_processes(domain) +
                                              self._get_affected_processes(related),
                            recommendations=[
                                f"Establish integration between {domain.value} and {related.value} systems",
                                "Define shared data entities and master sources",
                                "Implement automated data synchronization"
                            ]
                        ))

        return silos

    def _detect_duplicates(
        self,
        sources: List[DataSource]
    ) -> List[DuplicateData]:
        """Detect duplicate data across sources"""
        duplicates = []

        # Map entities to sources
        entity_sources = defaultdict(list)
        for source in sources:
            for entity in source.data_entities:
                entity_sources[entity].append(source.id)

        # Find duplicates
        for entity, source_ids in entity_sources.items():
            if len(source_ids) > 1:
                # Check if it's a critical entity
                is_critical = entity.lower() in self.critical_entities

                duplicate = DuplicateData(
                    entity_name=entity,
                    sources=source_ids,
                    discrepancy_rate=0.0,  # Would need actual data to calculate
                    issues=[]
                )

                if is_critical and len(source_ids) > 2:
                    duplicate.issues.append(
                        "Critical entity duplicated in multiple systems"
                    )

                if not any(s for s in sources if s.id in source_ids and "master" in s.name.lower()):
                    duplicate.issues.append("No clear master source defined")

                duplicates.append(duplicate)

        return duplicates

    def _detect_flow_gaps(
        self,
        sources: List[DataSource],
        process_flows: Optional[List[Dict]]
    ) -> List[Dict]:
        """Detect gaps in expected data flows"""
        gaps = []

        # Check critical entity coverage
        for entity, required_domains in self.critical_entities.items():
            entity_domains = set()
            for source in sources:
                if entity in [e.lower() for e in source.data_entities]:
                    entity_domains.add(source.domain)

            missing = set(required_domains) - entity_domains
            if missing:
                gaps.append({
                    "entity": entity,
                    "missing_domains": [d.value for d in missing],
                    "impact": f"{entity} data not available in {len(missing)} domains"
                })

        return gaps

    def _calculate_connectivity_score(
        self,
        sources: List[DataSource],
        connectivity: Dict[str, Set[str]]
    ) -> float:
        """Calculate overall connectivity score"""
        if not sources:
            return 0.0

        # Calculate average connections per source
        total_connections = sum(len(conns) for conns in connectivity.values())
        avg_connections = total_connections / len(sources)

        # Ideal connections per source
        ideal_connections = 3

        # Score based on average connections
        connection_score = min(1.0, avg_connections / ideal_connections)

        # Penalize for isolated sources
        isolated = sum(1 for s in sources if s.id not in connectivity or not connectivity[s.id])
        isolation_penalty = isolated / len(sources)

        # API availability bonus
        api_count = sum(1 for s in sources if s.has_api)
        api_bonus = (api_count / len(sources)) * 0.2

        return max(0, min(1.0, connection_score - isolation_penalty + api_bonus))

    def _get_affected_processes(self, domain: DataDomain) -> List[str]:
        """Get business processes affected by domain"""
        process_map = {
            DataDomain.DESIGN: ["Design Review", "RFI Processing", "Drawing Distribution"],
            DataDomain.COST: ["Budgeting", "Cost Tracking", "Invoice Processing"],
            DataDomain.SCHEDULE: ["Planning", "Progress Tracking", "Resource Allocation"],
            DataDomain.PROCUREMENT: ["Vendor Selection", "Purchase Orders", "Material Tracking"],
            DataDomain.SITE: ["Daily Reports", "Progress Photos", "Issue Management"],
            DataDomain.QUALITY: ["Inspections", "Defect Tracking", "Compliance"],
            DataDomain.SAFETY: ["Incident Reporting", "Safety Inspections", "Training"],
            DataDomain.FINANCIAL: ["Billing", "Payments", "Financial Reporting"],
            DataDomain.HR: ["Timekeeping", "Resource Management", "Certifications"]
        }
        return process_map.get(domain, [])

    def _prioritize_silos(
        self,
        silos: List[DataSilo]
    ) -> List[DataSilo]:
        """Prioritize silos by severity and impact"""
        severity_order = {
            SiloSeverity.CRITICAL: 0,
            SiloSeverity.HIGH: 1,
            SiloSeverity.MEDIUM: 2,
            SiloSeverity.LOW: 3
        }

        return sorted(
            silos,
            key=lambda s: (severity_order[s.severity], -s.affected_users)
        )

    def _generate_priority_actions(
        self,
        silos: List[DataSilo],
        duplicates: List[DuplicateData]
    ) -> List[str]:
        """Generate prioritized action items"""
        actions = []

        # Critical silos first
        critical_silos = [s for s in silos if s.severity == SiloSeverity.CRITICAL]
        for silo in critical_silos[:3]:
            actions.append(f"URGENT: {silo.recommendations[0]}")

        # Duplicate data issues
        critical_dups = [d for d in duplicates if d.issues]
        for dup in critical_dups[:2]:
            actions.append(
                f"Define master source for '{dup.entity_name}' "
                f"(currently in {len(dup.sources)} sources)"
            )

        # High priority silos
        high_silos = [s for s in silos if s.severity == SiloSeverity.HIGH]
        for silo in high_silos[:3]:
            if silo.recommendations:
                actions.append(silo.recommendations[0])

        return actions[:10]

    def _create_integration_roadmap(
        self,
        silos: List[DataSilo],
        gaps: List[Dict]
    ) -> Dict:
        """Create phased integration roadmap"""
        roadmap = {
            "Phase 1 - Quick Wins (0-3 months)": [],
            "Phase 2 - Core Integration (3-6 months)": [],
            "Phase 3 - Advanced Integration (6-12 months)": [],
            "Phase 4 - Optimization (12+ months)": []
        }

        # Phase 1: Address personal silos and easy integrations
        for silo in silos:
            if silo.issue_type == "personal_silo":
                roadmap["Phase 1 - Quick Wins (0-3 months)"].append(
                    f"Migrate {silo.sources[0].name} to shared repository"
                )

        # Phase 2: Core domain integrations
        domain_gaps = [s for s in silos if s.issue_type == "domain_disconnect"]
        for silo in domain_gaps[:3]:
            roadmap["Phase 2 - Core Integration (3-6 months)"].append(
                silo.recommendations[0] if silo.recommendations else silo.description
            )

        # Phase 3: Critical entity master data
        roadmap["Phase 3 - Advanced Integration (6-12 months)"].extend([
            "Implement master data management for shared entities",
            "Deploy integration middleware/ESB",
            "Establish data governance policies"
        ])

        # Phase 4: Optimization
        roadmap["Phase 4 - Optimization (12+ months)"].extend([
            "Implement real-time data synchronization",
            "Deploy integration monitoring and alerting",
            "Continuous improvement based on metrics"
        ])

        return roadmap

    def generate_report(self, analysis: SiloAnalysis) -> str:
        """Generate silo analysis report"""
        report = f"""
# Data Silo Analysis Report
## {analysis.organization}

**Analysis Date:** {analysis.analysis_date.strftime('%Y-%m-%d')}
**Data Sources Analyzed:** {analysis.total_sources}
**Connectivity Score:** {analysis.connectivity_score:.0%}

## Executive Summary

Detected **{len(analysis.silos_detected)}** data silos and **{len(analysis.duplicates)}** duplicate data issues.

### Silos by Severity
"""
        severity_counts = defaultdict(int)
        for silo in analysis.silos_detected:
            severity_counts[silo.severity.value] += 1

        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                report += f"- **{severity.title()}**: {count}\n"

        report += "\n## Priority Actions\n\n"
        for i, action in enumerate(analysis.priority_actions, 1):
            report += f"{i}. {action}\n"

        report += "\n## Detected Silos\n\n"
        for silo in analysis.silos_detected[:5]:
            report += f"""
### {silo.id}
- **Type:** {silo.issue_type}
- **Severity:** {silo.severity.value}
- **Impact:** {silo.impact}
- **Affected Users:** {silo.affected_users}
"""

        report += "\n## Integration Roadmap\n"
        for phase, items in analysis.integration_roadmap.items():
            report += f"\n### {phase}\n"
            for item in items:
                report += f"- {item}\n"

        return report
```

## Common Use Cases

### Detect Data Silos

```python
detector = DataSiloDetector()

# Define data sources
sources = [
    DataSource(
        id="revit",
        name="Revit Models",
        type=DataSourceType.DESKTOP_APP,
        domain=DataDomain.DESIGN,
        owner="Design Team",
        department="Engineering",
        users=["architect1", "engineer1", "engineer2"],
        data_entities=["building_model", "drawings", "schedules"],
        connections=["navisworks"],
        has_api=True
    ),
    DataSource(
        id="excel_estimates",
        name="Excel Cost Estimates",
        type=DataSourceType.SPREADSHEET,
        domain=DataDomain.COST,
        owner="Estimator",
        department="Pre-construction",
        users=["estimator1"],
        data_entities=["costs", "quantities", "labor_rates"],
        connections=[],  # No connections - silo!
        access_level="personal"
    ),
    DataSource(
        id="procore",
        name="Procore",
        type=DataSourceType.CLOUD_APP,
        domain=DataDomain.SITE,
        owner="Project Manager",
        department="Operations",
        users=["pm1", "pm2", "super1"],
        data_entities=["daily_reports", "photos", "punch_list"],
        connections=["primavera"],
        has_api=True
    )
]

analysis = detector.detect_silos(
    organization="ABC Construction",
    data_sources=sources
)

print(f"Silos detected: {len(analysis.silos_detected)}")
print(f"Connectivity score: {analysis.connectivity_score:.0%}")
```

### Generate Silo Report

```python
report = detector.generate_report(analysis)
print(report)

# Save to file
with open("silo_report.md", "w") as f:
    f.write(report)
```

### View Priority Actions

```python
print("Priority Actions:")
for i, action in enumerate(analysis.priority_actions, 1):
    print(f"{i}. {action}")

print("\nIntegration Roadmap:")
for phase, items in analysis.integration_roadmap.items():
    print(f"\n{phase}:")
    for item in items:
        print(f"  - {item}")
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DataSiloDetector` | Main detection engine |
| `DataSource` | Data source definition |
| `DataSilo` | Detected silo with details |
| `DuplicateData` | Duplicate data detection |
| `SiloAnalysis` | Complete analysis results |
| `SiloSeverity` | Severity classification |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 1.2
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [erp-integration-analysis](../erp-integration-analysis/SKILL.md) for system integration
- Use [data-evolution-analysis](../../Chapter-1.1/data-evolution-analysis/SKILL.md) for maturity assessment
- Use [etl-pipeline](../../Chapter-4.2/etl-pipeline/SKILL.md) to connect silos
