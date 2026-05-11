---
name: "erp-integration-analysis"
description: "Analyze ERP system integration for construction data flows. Map and optimize data flows between ERP modules"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔗", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# ERP Integration Analysis

## Overview

Based on DDC methodology (Chapter 1.2), this skill analyzes ERP system integration patterns in construction organizations, mapping data flows between modules and identifying optimization opportunities.

**Book Reference:** "Технологии и системы управления в современном строительстве" / "Technologies and Management Systems in Modern Construction"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
import json

class ERPModule(Enum):
    """Common ERP modules in construction"""
    FINANCE = "finance"
    PROJECT_MANAGEMENT = "project_management"
    PROCUREMENT = "procurement"
    INVENTORY = "inventory"
    HR = "human_resources"
    PAYROLL = "payroll"
    EQUIPMENT = "equipment"
    SUBCONTRACTS = "subcontracts"
    BILLING = "billing"
    COST_CONTROL = "cost_control"
    DOCUMENT_MANAGEMENT = "document_management"
    REPORTING = "reporting"

class IntegrationMethod(Enum):
    """Types of integration methods"""
    API = "api"
    DATABASE = "database"
    FILE_EXPORT = "file_export"
    MANUAL = "manual"
    WEBHOOK = "webhook"
    MESSAGE_QUEUE = "message_queue"
    ETL = "etl"

class DataFlowDirection(Enum):
    """Direction of data flow"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class DataFlow:
    """Represents a data flow between systems/modules"""
    source_module: str
    target_module: str
    data_type: str
    frequency: str  # real-time, hourly, daily, weekly, manual
    method: IntegrationMethod
    direction: DataFlowDirection
    volume: str  # low, medium, high
    critical: bool = False
    issues: List[str] = field(default_factory=list)

@dataclass
class ERPSystem:
    """ERP system definition"""
    name: str
    vendor: str
    version: str
    modules: List[ERPModule]
    database: str
    has_api: bool
    api_type: Optional[str] = None  # REST, SOAP, GraphQL
    custom_modules: List[str] = field(default_factory=list)

@dataclass
class IntegrationPoint:
    """Integration point between systems"""
    id: str
    source_system: str
    target_system: str
    method: IntegrationMethod
    endpoint: Optional[str] = None
    authentication: Optional[str] = None
    data_format: str = "json"
    status: str = "active"
    reliability_score: float = 1.0
    last_sync: Optional[datetime] = None

@dataclass
class IntegrationAnalysis:
    """Complete integration analysis results"""
    erp_system: ERPSystem
    external_systems: List[str]
    data_flows: List[DataFlow]
    integration_points: List[IntegrationPoint]
    integration_score: float
    bottlenecks: List[str]
    recommendations: List[str]
    data_flow_diagram: Dict


class ERPIntegrationAnalyzer:
    """
    Analyze ERP system integration for construction data flows.
    Based on DDC methodology Chapter 1.2.
    """

    def __init__(self):
        self.module_dependencies = self._define_module_dependencies()
        self.critical_flows = self._define_critical_flows()

    def _define_module_dependencies(self) -> Dict[ERPModule, List[ERPModule]]:
        """Define typical module dependencies"""
        return {
            ERPModule.PROJECT_MANAGEMENT: [
                ERPModule.COST_CONTROL,
                ERPModule.PROCUREMENT,
                ERPModule.HR,
                ERPModule.DOCUMENT_MANAGEMENT
            ],
            ERPModule.COST_CONTROL: [
                ERPModule.FINANCE,
                ERPModule.PROJECT_MANAGEMENT,
                ERPModule.BILLING
            ],
            ERPModule.PROCUREMENT: [
                ERPModule.INVENTORY,
                ERPModule.FINANCE,
                ERPModule.SUBCONTRACTS
            ],
            ERPModule.BILLING: [
                ERPModule.FINANCE,
                ERPModule.PROJECT_MANAGEMENT,
                ERPModule.COST_CONTROL
            ],
            ERPModule.PAYROLL: [
                ERPModule.HR,
                ERPModule.FINANCE,
                ERPModule.PROJECT_MANAGEMENT
            ],
            ERPModule.INVENTORY: [
                ERPModule.PROCUREMENT,
                ERPModule.PROJECT_MANAGEMENT,
                ERPModule.FINANCE
            ],
            ERPModule.EQUIPMENT: [
                ERPModule.PROJECT_MANAGEMENT,
                ERPModule.FINANCE,
                ERPModule.INVENTORY
            ],
            ERPModule.SUBCONTRACTS: [
                ERPModule.PROCUREMENT,
                ERPModule.FINANCE,
                ERPModule.PROJECT_MANAGEMENT
            ]
        }

    def _define_critical_flows(self) -> List[Tuple[str, str]]:
        """Define business-critical data flows"""
        return [
            ("project_management", "cost_control"),
            ("cost_control", "finance"),
            ("procurement", "inventory"),
            ("billing", "finance"),
            ("hr", "payroll"),
            ("project_management", "billing")
        ]

    def analyze_erp_integration(
        self,
        erp_system: ERPSystem,
        external_systems: List[Dict],
        integration_points: List[IntegrationPoint],
        transaction_logs: Optional[List[Dict]] = None
    ) -> IntegrationAnalysis:
        """
        Perform comprehensive ERP integration analysis.

        Args:
            erp_system: The ERP system to analyze
            external_systems: List of external systems
            integration_points: Defined integration points
            transaction_logs: Optional transaction logs for analysis

        Returns:
            Complete integration analysis
        """
        # Map all data flows
        data_flows = self._map_data_flows(
            erp_system, integration_points, transaction_logs
        )

        # Calculate integration score
        integration_score = self._calculate_integration_score(
            erp_system, data_flows, integration_points
        )

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(
            data_flows, integration_points
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            erp_system, data_flows, bottlenecks
        )

        # Create data flow diagram
        diagram = self._create_flow_diagram(
            erp_system, external_systems, data_flows
        )

        return IntegrationAnalysis(
            erp_system=erp_system,
            external_systems=[s["name"] for s in external_systems],
            data_flows=data_flows,
            integration_points=integration_points,
            integration_score=integration_score,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            data_flow_diagram=diagram
        )

    def _map_data_flows(
        self,
        erp: ERPSystem,
        integration_points: List[IntegrationPoint],
        logs: Optional[List[Dict]]
    ) -> List[DataFlow]:
        """Map all data flows in the system"""
        flows = []

        # Internal module flows
        for module in erp.modules:
            dependencies = self.module_dependencies.get(module, [])
            for dep in dependencies:
                if dep in erp.modules:
                    is_critical = (module.value, dep.value) in self.critical_flows
                    flows.append(DataFlow(
                        source_module=module.value,
                        target_module=dep.value,
                        data_type=self._get_data_type(module, dep),
                        frequency="real-time",
                        method=IntegrationMethod.DATABASE,
                        direction=DataFlowDirection.BIDIRECTIONAL,
                        volume="high" if is_critical else "medium",
                        critical=is_critical
                    ))

        # External integration flows
        for point in integration_points:
            if point.source_system == erp.name or point.target_system == erp.name:
                flows.append(DataFlow(
                    source_module=point.source_system,
                    target_module=point.target_system,
                    data_type="mixed",
                    frequency=self._infer_frequency(point),
                    method=point.method,
                    direction=DataFlowDirection.BIDIRECTIONAL,
                    volume="medium",
                    critical=False
                ))

        # Analyze logs if available
        if logs:
            flows = self._enhance_flows_from_logs(flows, logs)

        return flows

    def _get_data_type(
        self, source: ERPModule, target: ERPModule
    ) -> str:
        """Determine data type for module pair"""
        data_types = {
            (ERPModule.PROJECT_MANAGEMENT, ERPModule.COST_CONTROL): "costs_budgets",
            (ERPModule.COST_CONTROL, ERPModule.FINANCE): "financial_transactions",
            (ERPModule.PROCUREMENT, ERPModule.INVENTORY): "purchase_orders",
            (ERPModule.HR, ERPModule.PAYROLL): "employee_time",
            (ERPModule.BILLING, ERPModule.FINANCE): "invoices"
        }
        return data_types.get((source, target), "general_data")

    def _infer_frequency(self, point: IntegrationPoint) -> str:
        """Infer integration frequency from method"""
        if point.method == IntegrationMethod.WEBHOOK:
            return "real-time"
        elif point.method == IntegrationMethod.API:
            return "hourly"
        elif point.method == IntegrationMethod.ETL:
            return "daily"
        elif point.method == IntegrationMethod.FILE_EXPORT:
            return "daily"
        else:
            return "manual"

    def _enhance_flows_from_logs(
        self,
        flows: List[DataFlow],
        logs: List[Dict]
    ) -> List[DataFlow]:
        """Enhance flow information from transaction logs"""
        # Analyze log patterns
        flow_stats = {}
        for log in logs:
            key = (log.get("source"), log.get("target"))
            if key not in flow_stats:
                flow_stats[key] = {"count": 0, "errors": 0}
            flow_stats[key]["count"] += 1
            if log.get("status") == "error":
                flow_stats[key]["errors"] += 1

        # Update flows with statistics
        for flow in flows:
            key = (flow.source_module, flow.target_module)
            if key in flow_stats:
                stats = flow_stats[key]
                error_rate = stats["errors"] / stats["count"] if stats["count"] > 0 else 0
                if error_rate > 0.1:
                    flow.issues.append(f"High error rate: {error_rate:.1%}")
                if stats["count"] < 10:
                    flow.issues.append("Low transaction volume")

        return flows

    def _calculate_integration_score(
        self,
        erp: ERPSystem,
        flows: List[DataFlow],
        points: List[IntegrationPoint]
    ) -> float:
        """Calculate overall integration score (0-1)"""
        scores = []

        # API availability
        if erp.has_api:
            scores.append(1.0)
        else:
            scores.append(0.3)

        # Integration method quality
        method_scores = {
            IntegrationMethod.API: 1.0,
            IntegrationMethod.WEBHOOK: 1.0,
            IntegrationMethod.MESSAGE_QUEUE: 0.9,
            IntegrationMethod.ETL: 0.8,
            IntegrationMethod.DATABASE: 0.7,
            IntegrationMethod.FILE_EXPORT: 0.5,
            IntegrationMethod.MANUAL: 0.2
        }

        if points:
            avg_method_score = sum(
                method_scores.get(p.method, 0.5) for p in points
            ) / len(points)
            scores.append(avg_method_score)

        # Critical flow coverage
        critical_covered = sum(1 for f in flows if f.critical) / len(self.critical_flows)
        scores.append(critical_covered)

        # Flow health (issues)
        flows_with_issues = sum(1 for f in flows if f.issues)
        flow_health = 1 - (flows_with_issues / len(flows)) if flows else 1
        scores.append(flow_health)

        return sum(scores) / len(scores)

    def _identify_bottlenecks(
        self,
        flows: List[DataFlow],
        points: List[IntegrationPoint]
    ) -> List[str]:
        """Identify integration bottlenecks"""
        bottlenecks = []

        # Manual integrations
        manual_flows = [f for f in flows if f.method == IntegrationMethod.MANUAL]
        if manual_flows:
            bottlenecks.append(
                f"{len(manual_flows)} manual data flows requiring automation"
            )

        # File-based integrations
        file_flows = [f for f in flows if f.method == IntegrationMethod.FILE_EXPORT]
        if file_flows:
            bottlenecks.append(
                f"{len(file_flows)} file-based integrations causing delays"
            )

        # Low reliability points
        low_reliability = [p for p in points if p.reliability_score < 0.8]
        if low_reliability:
            bottlenecks.append(
                f"{len(low_reliability)} integration points with low reliability"
            )

        # Flows with issues
        problem_flows = [f for f in flows if f.issues]
        for flow in problem_flows:
            for issue in flow.issues:
                bottlenecks.append(
                    f"{flow.source_module} → {flow.target_module}: {issue}"
                )

        # Missing critical flows
        existing_critical = {
            (f.source_module, f.target_module) for f in flows if f.critical
        }
        for critical in self.critical_flows:
            if critical not in existing_critical:
                bottlenecks.append(
                    f"Missing critical flow: {critical[0]} → {critical[1]}"
                )

        return bottlenecks

    def _generate_recommendations(
        self,
        erp: ERPSystem,
        flows: List[DataFlow],
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate integration improvement recommendations"""
        recommendations = []

        # API recommendations
        if not erp.has_api:
            recommendations.append(
                "Enable API access for the ERP system to improve integration capabilities"
            )

        # Method upgrades
        manual_count = sum(1 for f in flows if f.method == IntegrationMethod.MANUAL)
        if manual_count > 0:
            recommendations.append(
                f"Automate {manual_count} manual data flows using API or ETL"
            )

        file_count = sum(1 for f in flows if f.method == IntegrationMethod.FILE_EXPORT)
        if file_count > 2:
            recommendations.append(
                "Replace file-based integrations with real-time API connections"
            )

        # Real-time integration
        non_realtime = sum(
            1 for f in flows
            if f.critical and f.frequency not in ["real-time", "hourly"]
        )
        if non_realtime > 0:
            recommendations.append(
                f"Upgrade {non_realtime} critical flows to real-time synchronization"
            )

        # Data quality
        if any("error rate" in b.lower() for b in bottlenecks):
            recommendations.append(
                "Implement data validation at integration points to reduce errors"
            )

        # Monitoring
        recommendations.append(
            "Implement integration monitoring dashboard for proactive issue detection"
        )

        return recommendations

    def _create_flow_diagram(
        self,
        erp: ERPSystem,
        external_systems: List[Dict],
        flows: List[DataFlow]
    ) -> Dict:
        """Create data flow diagram structure"""
        nodes = []
        edges = []

        # Add ERP modules as nodes
        for module in erp.modules:
            nodes.append({
                "id": module.value,
                "type": "erp_module",
                "label": module.value.replace("_", " ").title(),
                "system": erp.name
            })

        # Add external systems as nodes
        for system in external_systems:
            nodes.append({
                "id": system["name"],
                "type": "external",
                "label": system["name"],
                "system": "external"
            })

        # Add flows as edges
        for flow in flows:
            edges.append({
                "source": flow.source_module,
                "target": flow.target_module,
                "method": flow.method.value,
                "frequency": flow.frequency,
                "critical": flow.critical,
                "data_type": flow.data_type
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "legend": {
                "node_types": ["erp_module", "external"],
                "edge_methods": [m.value for m in IntegrationMethod]
            }
        }

    def compare_integration_options(
        self,
        options: List[Dict]
    ) -> Dict:
        """Compare different integration approaches"""
        comparison = []

        for option in options:
            score = self._score_integration_option(option)
            comparison.append({
                "name": option["name"],
                "method": option.get("method", "unknown"),
                "cost": option.get("cost", "unknown"),
                "implementation_time": option.get("time", "unknown"),
                "reliability": score["reliability"],
                "scalability": score["scalability"],
                "maintenance": score["maintenance"],
                "total_score": score["total"]
            })

        # Sort by total score
        comparison.sort(key=lambda x: x["total_score"], reverse=True)

        return {
            "options": comparison,
            "recommendation": comparison[0]["name"] if comparison else None
        }

    def _score_integration_option(self, option: Dict) -> Dict:
        """Score an integration option"""
        method = option.get("method", "")

        # Base scores by method
        method_scores = {
            "api": {"reliability": 0.9, "scalability": 0.9, "maintenance": 0.8},
            "etl": {"reliability": 0.8, "scalability": 0.8, "maintenance": 0.7},
            "file": {"reliability": 0.6, "scalability": 0.5, "maintenance": 0.6},
            "manual": {"reliability": 0.4, "scalability": 0.2, "maintenance": 0.3}
        }

        scores = method_scores.get(method, {"reliability": 0.5, "scalability": 0.5, "maintenance": 0.5})
        scores["total"] = sum(scores.values()) / 3

        return scores


class IntegrationHealthMonitor:
    """Monitor ERP integration health"""

    def __init__(self, integration_points: List[IntegrationPoint]):
        self.points = integration_points
        self.history: List[Dict] = []

    def check_health(self) -> Dict:
        """Check current integration health"""
        results = {
            "timestamp": datetime.now(),
            "overall_status": "healthy",
            "points_checked": len(self.points),
            "issues": []
        }

        for point in self.points:
            status = self._check_point(point)
            if status["status"] != "healthy":
                results["issues"].append({
                    "point": point.id,
                    "status": status["status"],
                    "message": status["message"]
                })

        if len(results["issues"]) > 0:
            results["overall_status"] = "degraded"
        if len(results["issues"]) > len(self.points) * 0.5:
            results["overall_status"] = "critical"

        self.history.append(results)
        return results

    def _check_point(self, point: IntegrationPoint) -> Dict:
        """Check individual integration point"""
        if point.status != "active":
            return {"status": "inactive", "message": "Integration point disabled"}

        if point.reliability_score < 0.5:
            return {"status": "degraded", "message": "Low reliability score"}

        if point.last_sync:
            hours_since_sync = (datetime.now() - point.last_sync).total_seconds() / 3600
            if hours_since_sync > 24:
                return {"status": "stale", "message": f"No sync for {hours_since_sync:.0f} hours"}

        return {"status": "healthy", "message": "OK"}

    def get_health_report(self) -> str:
        """Generate health report"""
        current = self.check_health()

        report = f"""
# ERP Integration Health Report
Generated: {current['timestamp'].strftime('%Y-%m-%d %H:%M')}

## Overall Status: {current['overall_status'].upper()}

### Integration Points: {current['points_checked']}
### Active Issues: {len(current['issues'])}
"""
        if current['issues']:
            report += "\n### Issues:\n"
            for issue in current['issues']:
                report += f"- **{issue['point']}**: {issue['status']} - {issue['message']}\n"

        return report
```

## Common Use Cases

### Analyze ERP Integration

```python
analyzer = ERPIntegrationAnalyzer()

# Define ERP system
erp = ERPSystem(
    name="SAP S/4HANA",
    vendor="SAP",
    version="2023",
    modules=[
        ERPModule.FINANCE,
        ERPModule.PROJECT_MANAGEMENT,
        ERPModule.PROCUREMENT,
        ERPModule.COST_CONTROL,
        ERPModule.HR,
        ERPModule.BILLING
    ],
    database="HANA",
    has_api=True,
    api_type="REST"
)

# Define external systems
external = [
    {"name": "Procore", "type": "project_management"},
    {"name": "Revit", "type": "bim"},
    {"name": "Primavera", "type": "scheduling"}
]

# Define integration points
points = [
    IntegrationPoint(
        id="erp-procore",
        source_system="SAP S/4HANA",
        target_system="Procore",
        method=IntegrationMethod.API
    ),
    IntegrationPoint(
        id="erp-primavera",
        source_system="SAP S/4HANA",
        target_system="Primavera",
        method=IntegrationMethod.FILE_EXPORT
    )
]

analysis = analyzer.analyze_erp_integration(
    erp_system=erp,
    external_systems=external,
    integration_points=points
)

print(f"Integration Score: {analysis.integration_score:.0%}")
print(f"Bottlenecks: {len(analysis.bottlenecks)}")
```

### Monitor Integration Health

```python
monitor = IntegrationHealthMonitor(integration_points)

health = monitor.check_health()
print(f"Status: {health['overall_status']}")

if health['issues']:
    for issue in health['issues']:
        print(f"  - {issue['point']}: {issue['message']}")

# Generate report
report = monitor.get_health_report()
print(report)
```

### Compare Integration Options

```python
options = [
    {"name": "REST API Integration", "method": "api", "cost": 50000, "time": "3 months"},
    {"name": "ETL Pipeline", "method": "etl", "cost": 30000, "time": "2 months"},
    {"name": "File-based Export", "method": "file", "cost": 10000, "time": "1 month"}
]

comparison = analyzer.compare_integration_options(options)
print(f"Recommended: {comparison['recommendation']}")
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `ERPIntegrationAnalyzer` | Main analysis engine |
| `ERPSystem` | ERP system definition |
| `ERPModule` | Standard ERP modules |
| `IntegrationPoint` | Integration connection |
| `DataFlow` | Data flow mapping |
| `IntegrationHealthMonitor` | Health monitoring |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 1.2
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [data-silo-detection](../data-silo-detection/SKILL.md) to identify isolated systems
- Use [etl-pipeline](../../Chapter-4.2/etl-pipeline/SKILL.md) for data integration
- Use [interoperability-analyzer](../../Chapter-3.5/interoperability-analyzer/SKILL.md) for standards compliance
