---
name: "data-lineage-tracker"
description: "Track data origin, transformations, and flow through construction systems. Essential for audit trails, compliance, and debugging data issues."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "✔️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Lineage Tracker for Construction

## Overview

Track the origin, transformations, and flow of construction data through systems. Provides audit trails for compliance, helps debug data issues, and ensures data governance.

## Business Case

Construction projects require data accountability:
- **Audit Compliance**: Know where every number came from
- **Issue Resolution**: Trace data problems to their source
- **Change Impact**: Understand what downstream systems are affected
- **Regulatory Requirements**: Maintain data provenance for legal/insurance

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid

class TransformationType(Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    AGGREGATE = "aggregate"
    JOIN = "join"
    FILTER = "filter"
    CALCULATE = "calculate"
    MANUAL_EDIT = "manual_edit"
    IMPORT = "import"
    EXPORT = "export"

@dataclass
class DataSource:
    id: str
    name: str
    system: str
    location: str
    owner: str
    created_at: datetime

@dataclass
class TransformationStep:
    id: str
    transformation_type: TransformationType
    description: str
    input_entities: List[str]
    output_entities: List[str]
    logic: str  # SQL, Python, or description
    performed_by: str  # user or system
    performed_at: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataEntity:
    id: str
    name: str
    source_id: str
    entity_type: str  # table, file, field, record
    created_at: datetime
    version: int = 1
    checksum: Optional[str] = None
    parent_entities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LineageRecord:
    id: str
    entity_id: str
    transformation_id: str
    upstream_entities: List[str]
    downstream_entities: List[str]
    recorded_at: datetime

class ConstructionDataLineageTracker:
    """Track data lineage for construction data flows."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.sources: Dict[str, DataSource] = {}
        self.entities: Dict[str, DataEntity] = {}
        self.transformations: Dict[str, TransformationStep] = {}
        self.lineage_records: List[LineageRecord] = []

    def register_source(self, name: str, system: str, location: str, owner: str) -> DataSource:
        """Register a new data source."""
        source = DataSource(
            id=f"SRC-{uuid.uuid4().hex[:8]}",
            name=name,
            system=system,
            location=location,
            owner=owner,
            created_at=datetime.now()
        )
        self.sources[source.id] = source
        return source

    def register_entity(self, name: str, source_id: str, entity_type: str,
                       parent_entities: List[str] = None,
                       metadata: Dict = None) -> DataEntity:
        """Register a data entity (table, file, field)."""
        entity = DataEntity(
            id=f"ENT-{uuid.uuid4().hex[:8]}",
            name=name,
            source_id=source_id,
            entity_type=entity_type,
            created_at=datetime.now(),
            parent_entities=parent_entities or [],
            metadata=metadata or {}
        )
        self.entities[entity.id] = entity
        return entity

    def calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data verification."""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_transformation(self,
                             transformation_type: TransformationType,
                             description: str,
                             input_entities: List[str],
                             output_entities: List[str],
                             logic: str,
                             performed_by: str,
                             parameters: Dict = None) -> TransformationStep:
        """Record a data transformation."""
        transformation = TransformationStep(
            id=f"TRF-{uuid.uuid4().hex[:8]}",
            transformation_type=transformation_type,
            description=description,
            input_entities=input_entities,
            output_entities=output_entities,
            logic=logic,
            performed_by=performed_by,
            performed_at=datetime.now(),
            parameters=parameters or {}
        )
        self.transformations[transformation.id] = transformation

        # Create lineage records
        for output_id in output_entities:
            record = LineageRecord(
                id=f"LIN-{uuid.uuid4().hex[:8]}",
                entity_id=output_id,
                transformation_id=transformation.id,
                upstream_entities=input_entities,
                downstream_entities=[],
                recorded_at=datetime.now()
            )
            self.lineage_records.append(record)

            # Update downstream references for input entities
            for input_id in input_entities:
                for existing_record in self.lineage_records:
                    if existing_record.entity_id == input_id:
                        existing_record.downstream_entities.append(output_id)

        return transformation

    def trace_upstream(self, entity_id: str, depth: int = None) -> List[Dict]:
        """Trace all upstream sources of an entity."""
        visited = set()
        lineage = []

        def trace(eid: str, current_depth: int):
            if eid in visited:
                return
            if depth is not None and current_depth > depth:
                return

            visited.add(eid)

            entity = self.entities.get(eid)
            if not entity:
                return

            # Find transformations that produced this entity
            for record in self.lineage_records:
                if record.entity_id == eid:
                    transformation = self.transformations.get(record.transformation_id)
                    if transformation:
                        lineage.append({
                            'entity': entity.name,
                            'entity_id': eid,
                            'depth': current_depth,
                            'transformation': transformation.description,
                            'transformation_type': transformation.transformation_type.value,
                            'performed_at': transformation.performed_at.isoformat(),
                            'performed_by': transformation.performed_by,
                            'upstream': record.upstream_entities
                        })

                        for upstream_id in record.upstream_entities:
                            trace(upstream_id, current_depth + 1)

        trace(entity_id, 0)
        return sorted(lineage, key=lambda x: x['depth'])

    def trace_downstream(self, entity_id: str, depth: int = None) -> List[Dict]:
        """Trace all downstream dependencies of an entity."""
        visited = set()
        dependencies = []

        def trace(eid: str, current_depth: int):
            if eid in visited:
                return
            if depth is not None and current_depth > depth:
                return

            visited.add(eid)

            entity = self.entities.get(eid)
            if not entity:
                return

            # Find entities that use this entity
            for record in self.lineage_records:
                if eid in record.upstream_entities:
                    transformation = self.transformations.get(record.transformation_id)
                    if transformation:
                        dependencies.append({
                            'entity': self.entities[record.entity_id].name if record.entity_id in self.entities else record.entity_id,
                            'entity_id': record.entity_id,
                            'depth': current_depth,
                            'transformation': transformation.description,
                            'transformation_type': transformation.transformation_type.value
                        })

                        trace(record.entity_id, current_depth + 1)

        trace(entity_id, 0)
        return sorted(dependencies, key=lambda x: x['depth'])

    def get_entity_history(self, entity_id: str) -> List[Dict]:
        """Get complete history of changes to an entity."""
        history = []

        for record in self.lineage_records:
            if record.entity_id == entity_id:
                transformation = self.transformations.get(record.transformation_id)
                if transformation:
                    history.append({
                        'timestamp': transformation.performed_at.isoformat(),
                        'action': transformation.transformation_type.value,
                        'description': transformation.description,
                        'performed_by': transformation.performed_by,
                        'inputs': [
                            self.entities[eid].name if eid in self.entities else eid
                            for eid in record.upstream_entities
                        ]
                    })

        return sorted(history, key=lambda x: x['timestamp'])

    def impact_analysis(self, entity_id: str) -> Dict:
        """Analyze impact of changes to an entity."""
        downstream = self.trace_downstream(entity_id)

        impact = {
            'entity': self.entities[entity_id].name if entity_id in self.entities else entity_id,
            'total_affected': len(downstream),
            'affected_by_depth': {},
            'affected_entities': downstream
        }

        for dep in downstream:
            depth = dep['depth']
            impact['affected_by_depth'][depth] = impact['affected_by_depth'].get(depth, 0) + 1

        return impact

    def validate_lineage(self) -> List[str]:
        """Validate lineage for completeness and consistency."""
        issues = []

        # Check for orphan entities (no source or transformation)
        for eid, entity in self.entities.items():
            has_lineage = any(r.entity_id == eid for r in self.lineage_records)
            if not has_lineage and entity.entity_type != 'source':
                issues.append(f"Entity '{entity.name}' has no lineage record")

        # Check for broken references
        all_entity_ids = set(self.entities.keys())
        for record in self.lineage_records:
            for upstream_id in record.upstream_entities:
                if upstream_id not in all_entity_ids:
                    issues.append(f"Lineage references unknown entity: {upstream_id}")

        # Check for circular dependencies
        for eid in self.entities:
            upstream = set()
            to_check = [eid]
            while to_check:
                current = to_check.pop()
                if current in upstream:
                    issues.append(f"Circular dependency detected involving entity: {self.entities[eid].name}")
                    break
                upstream.add(current)
                for record in self.lineage_records:
                    if record.entity_id == current:
                        to_check.extend(record.upstream_entities)

        return issues

    def generate_lineage_graph(self, entity_id: str) -> str:
        """Generate Mermaid diagram of lineage."""
        lines = ["```mermaid", "graph LR"]

        upstream = self.trace_upstream(entity_id, depth=5)
        downstream = self.trace_downstream(entity_id, depth=5)

        # Add nodes
        added_nodes = set()
        for item in upstream + downstream:
            node_id = item['entity_id'].replace('-', '_')
            if node_id not in added_nodes:
                entity = self.entities.get(item['entity_id'])
                name = entity.name if entity else item['entity_id']
                lines.append(f"    {node_id}[{name}]")
                added_nodes.add(node_id)

        # Add target node
        target_node = entity_id.replace('-', '_')
        if target_node not in added_nodes:
            entity = self.entities.get(entity_id)
            name = entity.name if entity else entity_id
            lines.append(f"    {target_node}[{name}]:::target")

        # Add edges
        for item in upstream:
            for upstream_id in item.get('upstream', []):
                from_node = upstream_id.replace('-', '_')
                to_node = item['entity_id'].replace('-', '_')
                lines.append(f"    {from_node} --> {to_node}")

        for item in downstream:
            from_node = entity_id.replace('-', '_')
            to_node = item['entity_id'].replace('-', '_')
            if to_node != from_node:
                lines.append(f"    {from_node} --> {to_node}")

        lines.append("    classDef target fill:#f96")
        lines.append("```")

        return "\n".join(lines)

    def export_lineage(self) -> Dict:
        """Export complete lineage data."""
        return {
            'project_id': self.project_id,
            'exported_at': datetime.now().isoformat(),
            'sources': {k: {
                'id': v.id,
                'name': v.name,
                'system': v.system,
                'location': v.location,
                'owner': v.owner
            } for k, v in self.sources.items()},
            'entities': {k: {
                'id': v.id,
                'name': v.name,
                'source_id': v.source_id,
                'entity_type': v.entity_type,
                'parent_entities': v.parent_entities
            } for k, v in self.entities.items()},
            'transformations': {k: {
                'id': v.id,
                'type': v.transformation_type.value,
                'description': v.description,
                'input_entities': v.input_entities,
                'output_entities': v.output_entities,
                'performed_by': v.performed_by,
                'performed_at': v.performed_at.isoformat()
            } for k, v in self.transformations.items()},
            'lineage_records': [{
                'id': r.id,
                'entity_id': r.entity_id,
                'transformation_id': r.transformation_id,
                'upstream_entities': r.upstream_entities
            } for r in self.lineage_records]
        }

    def generate_report(self) -> str:
        """Generate lineage report."""
        lines = [f"# Data Lineage Report: {self.project_id}", ""]
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Sources:** {len(self.sources)}")
        lines.append(f"**Entities:** {len(self.entities)}")
        lines.append(f"**Transformations:** {len(self.transformations)}")
        lines.append("")

        # Sources
        lines.append("## Data Sources")
        for source in self.sources.values():
            lines.append(f"- **{source.name}** ({source.system})")
            lines.append(f"  - Location: {source.location}")
            lines.append(f"  - Owner: {source.owner}")
        lines.append("")

        # Validation
        issues = self.validate_lineage()
        if issues:
            lines.append("## Lineage Issues")
            for issue in issues:
                lines.append(f"- ⚠️ {issue}")
            lines.append("")

        # Transformation summary
        lines.append("## Transformation Summary")
        type_counts = {}
        for t in self.transformations.values():
            type_counts[t.transformation_type.value] = type_counts.get(t.transformation_type.value, 0) + 1
        for t_type, count in sorted(type_counts.items()):
            lines.append(f"- {t_type}: {count}")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize tracker
tracker = ConstructionDataLineageTracker("PROJECT-001")

# Register sources
procore = tracker.register_source("Procore", "SaaS", "cloud", "PM Team")
sage = tracker.register_source("Sage 300", "Database", "on-prem", "Finance")

# Register entities
budget = tracker.register_entity("Project Budget", procore.id, "table")
costs = tracker.register_entity("Job Costs", sage.id, "table")
report = tracker.register_entity("Cost Variance Report", procore.id, "file")

# Record transformation
tracker.record_transformation(
    transformation_type=TransformationType.JOIN,
    description="Join budget and actual costs for variance calculation",
    input_entities=[budget.id, costs.id],
    output_entities=[report.id],
    logic="SELECT b.*, c.actual, (b.budget - c.actual) as variance FROM budget b JOIN costs c ON b.cost_code = c.cost_code",
    performed_by="ETL Pipeline"
)

# Trace lineage
upstream = tracker.trace_upstream(report.id)
print("Upstream lineage:", upstream)

# Generate graph
print(tracker.generate_lineage_graph(report.id))

# Export for audit
lineage_data = tracker.export_lineage()
```

## Resources

- **Data Governance**: DAMA DMBOK lineage guidelines
- **Audit Requirements**: SOX, ISO compliance
