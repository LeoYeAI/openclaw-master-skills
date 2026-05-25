---
name: "data-source-audit"
description: "Comprehensive audit of all construction data sources and systems. Map data flows, identify silos, assess quality, and create integration roadmap."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔗", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Source Audit for Construction

## Overview

Perform comprehensive audits of construction data sources to identify silos, map data flows, assess quality, and plan integration strategies. Essential for digital transformation and data-driven construction initiatives.

## Business Case

Construction organizations typically have 10-50+ data sources:
- Project management systems
- Estimating software
- Scheduling tools
- Accounting/ERP systems
- BIM platforms
- Document management systems
- Field apps
- Spreadsheets

> **Note:** This skill is vendor-agnostic and works with any data source. Product names mentioned elsewhere in examples are trademarks of their respective owners.

This skill helps:
- Discover all data sources
- Map data flows and dependencies
- Identify integration opportunities
- Prioritize data improvement efforts

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime
import pandas as pd
import json

class DataSourceType(Enum):
    DATABASE = "database"
    API = "api"
    FILE_SHARE = "file_share"
    CLOUD_APP = "cloud_app"
    SPREADSHEET = "spreadsheet"
    LEGACY_SYSTEM = "legacy_system"
    IOT_SENSOR = "iot_sensor"
    MANUAL_ENTRY = "manual_entry"

class DataDomain(Enum):
    COST = "cost"
    SCHEDULE = "schedule"
    BIM = "bim"
    DOCUMENT = "document"
    FIELD = "field"
    SAFETY = "safety"
    QUALITY = "quality"
    HR = "hr"
    ACCOUNTING = "accounting"
    PROCUREMENT = "procurement"

@dataclass
class DataSource:
    name: str
    source_type: DataSourceType
    domains: List[DataDomain]
    owner: str
    department: str
    description: str
    # Technical details
    technology: str
    location: str  # cloud, on-prem, hybrid
    access_method: str  # API, ODBC, file export, manual
    # Data characteristics
    update_frequency: str  # real-time, daily, weekly, monthly, ad-hoc
    data_volume: str  # small, medium, large
    retention_period: str
    # Quality metrics
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    timeliness_score: float = 0.0
    # Integration status
    integrations: List[str] = field(default_factory=list)
    is_master: bool = False  # Is this the master source for any entity?
    master_for: List[str] = field(default_factory=list)
    # Issues
    known_issues: List[str] = field(default_factory=list)
    # Metadata
    last_audit_date: Optional[datetime] = None
    audit_notes: str = ""

@dataclass
class DataFlow:
    source: str
    target: str
    flow_type: str  # push, pull, bidirectional, manual
    frequency: str
    entities: List[str]  # What data entities flow
    transformation: str  # none, simple, complex
    status: str  # active, planned, deprecated

@dataclass
class DataSilo:
    name: str
    sources: List[str]
    impact: str  # high, medium, low
    description: str
    resolution_options: List[str]

class DataSourceAuditor:
    """Audit and analyze construction data sources."""

    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.flows: List[DataFlow] = []
        self.silos: List[DataSilo] = []

    def add_source(self, source: DataSource):
        """Register a data source."""
        self.sources[source.name] = source

    def add_flow(self, flow: DataFlow):
        """Register a data flow between sources."""
        self.flows.append(flow)

    def discover_sources_from_survey(self, survey_responses: List[Dict]) -> List[DataSource]:
        """Create data sources from survey responses."""
        sources = []

        for response in survey_responses:
            source = DataSource(
                name=response['system_name'],
                source_type=DataSourceType(response['type']),
                domains=[DataDomain(d) for d in response['domains']],
                owner=response['owner'],
                department=response['department'],
                description=response['description'],
                technology=response['technology'],
                location=response['location'],
                access_method=response['access_method'],
                update_frequency=response['update_frequency'],
                data_volume=response['data_volume'],
                retention_period=response['retention_period'],
            )
            sources.append(source)
            self.add_source(source)

        return sources

    def identify_silos(self) -> List[DataSilo]:
        """Identify data silos based on integration analysis."""
        silos = []

        # Find sources with no integrations
        isolated_sources = [
            name for name, source in self.sources.items()
            if not source.integrations and source.source_type != DataSourceType.MANUAL_ENTRY
        ]

        if isolated_sources:
            silos.append(DataSilo(
                name="Isolated Systems",
                sources=isolated_sources,
                impact="high",
                description="Systems with no integrations, requiring manual data transfer",
                resolution_options=[
                    "Implement API integration",
                    "Set up automated file exports",
                    "Migrate to integrated platform"
                ]
            ))

        # Find duplicate data domains without master
        domain_sources: Dict[DataDomain, List[str]] = {}
        for name, source in self.sources.items():
            for domain in source.domains:
                if domain not in domain_sources:
                    domain_sources[domain] = []
                domain_sources[domain].append(name)

        for domain, sources in domain_sources.items():
            if len(sources) > 1:
                # Check if any is designated master
                masters = [s for s in sources if self.sources[s].is_master]
                if not masters:
                    silos.append(DataSilo(
                        name=f"No Master for {domain.value}",
                        sources=sources,
                        impact="medium",
                        description=f"Multiple sources for {domain.value} data without designated master",
                        resolution_options=[
                            "Designate master data source",
                            "Implement MDM solution",
                            "Create data reconciliation process"
                        ]
                    ))

        # Find one-way flows that should be bidirectional
        flow_pairs = {}
        for flow in self.flows:
            key = tuple(sorted([flow.source, flow.target]))
            if key not in flow_pairs:
                flow_pairs[key] = []
            flow_pairs[key].append(flow)

        for (s1, s2), flows in flow_pairs.items():
            if len(flows) == 1 and flows[0].flow_type != 'bidirectional':
                # Check if bidirectional would make sense
                s1_domains = set(self.sources[s1].domains)
                s2_domains = set(self.sources[s2].domains)
                if s1_domains & s2_domains:  # Overlapping domains
                    silos.append(DataSilo(
                        name=f"One-way flow: {s1} -> {s2}",
                        sources=[s1, s2],
                        impact="low",
                        description="Data flows one direction only between systems with overlapping domains",
                        resolution_options=[
                            "Evaluate need for bidirectional sync",
                            "Implement change data capture"
                        ]
                    ))

        self.silos = silos
        return silos

    def assess_source_quality(self, source_name: str, sample_data: pd.DataFrame) -> Dict[str, float]:
        """Assess data quality for a source based on sample data."""
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")

        scores = {}

        # Completeness: % of non-null values
        completeness = 1 - (sample_data.isnull().sum().sum() / sample_data.size)
        scores['completeness'] = completeness

        # Uniqueness: % of unique rows (for key columns)
        if len(sample_data) > 0:
            uniqueness = len(sample_data.drop_duplicates()) / len(sample_data)
        else:
            uniqueness = 1.0
        scores['uniqueness'] = uniqueness

        # Validity: Basic format checks (simplified)
        validity_checks = 0
        total_checks = 0

        for col in sample_data.columns:
            if 'date' in col.lower():
                total_checks += 1
                try:
                    pd.to_datetime(sample_data[col], errors='raise')
                    validity_checks += 1
                except:
                    pass
            if 'email' in col.lower():
                total_checks += 1
                valid_emails = sample_data[col].str.contains(r'@.*\.', na=False).sum()
                if valid_emails / len(sample_data) > 0.9:
                    validity_checks += 1

        scores['validity'] = validity_checks / total_checks if total_checks > 0 else 1.0

        # Update source with scores
        self.sources[source_name].completeness_score = scores['completeness']
        self.sources[source_name].accuracy_score = scores['validity']

        return scores

    def create_data_catalog(self) -> pd.DataFrame:
        """Create a data catalog from all sources."""
        catalog_entries = []

        for name, source in self.sources.items():
            entry = {
                'Source Name': name,
                'Type': source.source_type.value,
                'Domains': ', '.join(d.value for d in source.domains),
                'Owner': source.owner,
                'Department': source.department,
                'Technology': source.technology,
                'Location': source.location,
                'Access Method': source.access_method,
                'Update Frequency': source.update_frequency,
                'Data Volume': source.data_volume,
                'Integrations': len(source.integrations),
                'Is Master': 'Yes' if source.is_master else 'No',
                'Quality Score': (source.completeness_score + source.accuracy_score) / 2,
                'Known Issues': len(source.known_issues),
            }
            catalog_entries.append(entry)

        return pd.DataFrame(catalog_entries)

    def generate_integration_matrix(self) -> pd.DataFrame:
        """Generate integration matrix showing connections between sources."""
        source_names = list(self.sources.keys())
        matrix = pd.DataFrame(
            index=source_names,
            columns=source_names,
            data=''
        )

        for flow in self.flows:
            if flow.source in source_names and flow.target in source_names:
                current = matrix.loc[flow.source, flow.target]
                symbol = '→' if flow.flow_type == 'push' else '←' if flow.flow_type == 'pull' else '↔'
                matrix.loc[flow.source, flow.target] = f"{current}{symbol}" if current else symbol

        return matrix

    def calculate_integration_score(self) -> Dict[str, float]:
        """Calculate overall integration score and breakdown."""
        if not self.sources:
            return {'overall': 0.0}

        scores = {}

        # Coverage: % of sources with at least one integration
        integrated = sum(1 for s in self.sources.values() if s.integrations)
        scores['coverage'] = integrated / len(self.sources)

        # Master data: % of domains with designated master
        domains_with_master = set()
        for source in self.sources.values():
            if source.is_master:
                domains_with_master.update(source.master_for)

        all_domains = set()
        for source in self.sources.values():
            all_domains.update(d.value for d in source.domains)

        scores['master_data'] = len(domains_with_master) / len(all_domains) if all_domains else 1.0

        # Data quality average
        quality_scores = [
            (s.completeness_score + s.accuracy_score) / 2
            for s in self.sources.values()
            if s.completeness_score > 0 or s.accuracy_score > 0
        ]
        scores['quality'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        # Silo impact
        high_impact_silos = sum(1 for s in self.silos if s.impact == 'high')
        scores['silo_risk'] = 1 - (high_impact_silos * 0.2)  # Each high-impact silo reduces score

        # Overall
        scores['overall'] = (
            scores['coverage'] * 0.3 +
            scores['master_data'] * 0.25 +
            scores['quality'] * 0.25 +
            scores['silo_risk'] * 0.2
        )

        return scores

    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        report = ["# Data Source Audit Report", ""]
        report.append(f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report.append(f"**Total Sources:** {len(self.sources)}")
        report.append(f"**Total Data Flows:** {len(self.flows)}")
        report.append("")

        # Integration Score
        scores = self.calculate_integration_score()
        report.append("## Integration Maturity Score")
        report.append(f"**Overall Score:** {scores['overall']:.1%}")
        report.append(f"- Coverage: {scores['coverage']:.1%}")
        report.append(f"- Master Data: {scores['master_data']:.1%}")
        report.append(f"- Data Quality: {scores['quality']:.1%}")
        report.append(f"- Silo Risk: {scores['silo_risk']:.1%}")
        report.append("")

        # Sources by Type
        report.append("## Sources by Type")
        by_type = {}
        for source in self.sources.values():
            t = source.source_type.value
            by_type[t] = by_type.get(t, 0) + 1
        for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
            report.append(f"- {t}: {count}")
        report.append("")

        # Data Silos
        report.append("## Identified Data Silos")
        if self.silos:
            for silo in self.silos:
                report.append(f"\n### {silo.name}")
                report.append(f"**Impact:** {silo.impact}")
                report.append(f"**Sources:** {', '.join(silo.sources)}")
                report.append(f"**Description:** {silo.description}")
                report.append("**Resolution Options:**")
                for opt in silo.resolution_options:
                    report.append(f"- {opt}")
        else:
            report.append("No significant data silos identified.")
        report.append("")

        # Recommendations
        report.append("## Recommendations")
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")

        return "\n".join(report)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on audit findings."""
        recommendations = []

        scores = self.calculate_integration_score()

        if scores['coverage'] < 0.7:
            recommendations.append(
                "Increase integration coverage - over 30% of systems are isolated. "
                "Prioritize connecting high-value data sources."
            )

        if scores['master_data'] < 0.5:
            recommendations.append(
                "Implement Master Data Management - designate authoritative sources "
                "for key entities (projects, vendors, employees, cost codes)."
            )

        if scores['quality'] < 0.7:
            recommendations.append(
                "Improve data quality - implement validation rules at data entry points "
                "and automated quality monitoring."
            )

        # Check for spreadsheet dependency
        spreadsheets = [s for s in self.sources.values()
                       if s.source_type == DataSourceType.SPREADSHEET]
        if len(spreadsheets) > 3:
            recommendations.append(
                f"Reduce spreadsheet dependency - {len(spreadsheets)} spreadsheet-based "
                "data sources identified. Migrate critical data to proper databases."
            )

        # Check for legacy systems
        legacy = [s for s in self.sources.values()
                 if s.source_type == DataSourceType.LEGACY_SYSTEM]
        if legacy:
            recommendations.append(
                f"Plan legacy system migration - {len(legacy)} legacy systems identified. "
                "Create modernization roadmap."
            )

        return recommendations
```

## Quick Start

```python
# Initialize auditor
auditor = DataSourceAuditor()

# Add known sources
auditor.add_source(DataSource(
    name="Procore",
    source_type=DataSourceType.CLOUD_APP,
    domains=[DataDomain.DOCUMENT, DataDomain.FIELD, DataDomain.SCHEDULE],
    owner="Project Controls",
    department="Operations",
    description="Primary project management platform",
    technology="SaaS",
    location="cloud",
    access_method="API",
    update_frequency="real-time",
    data_volume="large",
    retention_period="7 years",
    integrations=["Sage 300", "Primavera P6"],
    is_master=True,
    master_for=["projects", "documents"]
))

auditor.add_source(DataSource(
    name="Sage 300",
    source_type=DataSourceType.DATABASE,
    domains=[DataDomain.COST, DataDomain.ACCOUNTING],
    owner="Finance",
    department="Accounting",
    description="ERP and job costing system",
    technology="SQL Server",
    location="on-prem",
    access_method="ODBC",
    update_frequency="daily",
    data_volume="medium",
    retention_period="10 years",
    is_master=True,
    master_for=["costs", "vendors", "invoices"]
))

# Add data flows
auditor.add_flow(DataFlow(
    source="Procore",
    target="Sage 300",
    flow_type="push",
    frequency="daily",
    entities=["change_orders", "budget_changes"],
    transformation="simple",
    status="active"
))

# Identify silos
silos = auditor.identify_silos()

# Generate report
report = auditor.generate_audit_report()
print(report)

# Create data catalog
catalog = auditor.create_data_catalog()
catalog.to_excel("data_catalog.xlsx", index=False)
```

## Survey Template

Use this survey to discover data sources across the organization:

```yaml
System Survey:
  - system_name: "What is the name of this system?"
  - type: "What type of system is it?"
    options: [database, api, file_share, cloud_app, spreadsheet, legacy_system]
  - domains: "What types of data does it contain?"
    options: [cost, schedule, bim, document, field, safety, quality, hr, accounting]
  - owner: "Who is the system owner?"
  - department: "Which department uses this system?"
  - technology: "What technology/platform is it built on?"
  - location: "Where is the system hosted?"
    options: [cloud, on-prem, hybrid]
  - access_method: "How can data be accessed?"
    options: [api, odbc, file_export, manual]
  - update_frequency: "How often is data updated?"
    options: [real-time, daily, weekly, monthly, ad-hoc]
  - integrations: "What other systems does it connect to?"
```

## Resources

- **DAMA DMBOK**: Data Management Body of Knowledge
- **Data Governance Frameworks**: DCAM, EDM Council
- **Integration Patterns**: Enterprise Integration Patterns book
