---
name: "data-anomaly-detector"
description: "Detect anomalies and outliers in construction data: unusual costs, schedule variances, productivity spikes. Statistical and ML-based detection methods."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "✔️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Anomaly Detector for Construction

## Overview

Detect unusual patterns, outliers, and anomalies in construction data. Identify cost overruns, schedule delays, productivity issues, and data quality problems before they impact projects.

## Business Case

Construction data often contains anomalies that indicate:
- Cost estimate errors or fraud
- Schedule logic issues
- Productivity problems
- Data entry mistakes
- Equipment or material issues

Early detection prevents costly corrections and project delays.

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

class AnomalyType(Enum):
    OUTLIER = "outlier"
    PATTERN_BREAK = "pattern_break"
    MISSING_SEQUENCE = "missing_sequence"
    DUPLICATE = "duplicate"
    IMPOSSIBLE_VALUE = "impossible_value"
    TREND_DEVIATION = "trend_deviation"

class AnomalySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Anomaly:
    id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    field: str
    value: Any
    expected_range: Optional[Tuple[float, float]] = None
    description: str = ""
    row_index: Optional[int] = None
    detection_method: str = ""
    confidence: float = 0.0
    suggested_action: str = ""

@dataclass
class AnomalyReport:
    source: str
    detected_at: datetime
    total_records: int
    anomalies: List[Anomaly]
    summary: Dict[str, int]

class ConstructionAnomalyDetector:
    """Detect anomalies in construction data."""

    # Construction-specific thresholds
    COST_THRESHOLDS = {
        'concrete_per_cy': (200, 800),
        'steel_per_ton': (1500, 4000),
        'labor_per_hour': (25, 150),
        'overhead_percentage': (5, 25),
        'contingency_percentage': (3, 20),
    }

    SCHEDULE_THRESHOLDS = {
        'max_activity_duration': 365,  # days
        'max_lag': 30,  # days
        'min_productivity': 0.1,
        'max_productivity': 10.0,
    }

    def __init__(self):
        self.anomalies: List[Anomaly] = []
        self.detection_history: List[AnomalyReport] = []

    def detect_cost_anomalies(self, df: pd.DataFrame, cost_column: str,
                              group_by: str = None) -> List[Anomaly]:
        """Detect anomalies in cost data."""
        anomalies = []

        # Statistical outlier detection (IQR method)
        Q1 = df[cost_column].quantile(0.25)
        Q3 = df[cost_column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[cost_column] < lower_bound) | (df[cost_column] > upper_bound)]

        for idx, row in outliers.iterrows():
            value = row[cost_column]
            severity = AnomalySeverity.HIGH if abs(value - df[cost_column].median()) > 3 * IQR else AnomalySeverity.MEDIUM

            anomalies.append(Anomaly(
                id=f"COST-{idx}",
                anomaly_type=AnomalyType.OUTLIER,
                severity=severity,
                field=cost_column,
                value=value,
                expected_range=(lower_bound, upper_bound),
                description=f"Cost value {value:,.2f} outside expected range",
                row_index=idx,
                detection_method="IQR",
                confidence=0.95,
                suggested_action="Review cost estimate for errors"
            ))

        # Negative cost check
        negatives = df[df[cost_column] < 0]
        for idx, row in negatives.iterrows():
            anomalies.append(Anomaly(
                id=f"COST-NEG-{idx}",
                anomaly_type=AnomalyType.IMPOSSIBLE_VALUE,
                severity=AnomalySeverity.CRITICAL,
                field=cost_column,
                value=row[cost_column],
                expected_range=(0, None),
                description="Negative cost value detected",
                row_index=idx,
                detection_method="Business Rule",
                confidence=1.0,
                suggested_action="Correct data entry error or investigate credit"
            ))

        # Group-based anomalies (if grouped)
        if group_by and group_by in df.columns:
            group_stats = df.groupby(group_by)[cost_column].agg(['mean', 'std'])

            for group_name, stats in group_stats.iterrows():
                group_data = df[df[group_by] == group_name]
                z_scores = np.abs((group_data[cost_column] - stats['mean']) / stats['std'])

                for idx, z in z_scores.items():
                    if z > 3:
                        anomalies.append(Anomaly(
                            id=f"COST-GROUP-{idx}",
                            anomaly_type=AnomalyType.OUTLIER,
                            severity=AnomalySeverity.MEDIUM,
                            field=cost_column,
                            value=df.loc[idx, cost_column],
                            description=f"Unusual cost for group {group_name} (z-score: {z:.2f})",
                            row_index=idx,
                            detection_method="Z-Score by Group",
                            confidence=min(z / 5, 1.0)
                        ))

        return anomalies

    def detect_schedule_anomalies(self, df: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies in schedule data."""
        anomalies = []

        # Check for required columns
        required = ['start_date', 'end_date']
        if not all(col in df.columns for col in required):
            return anomalies

        # Convert dates
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])

        # Calculate duration
        df['duration'] = (df['end_date'] - df['start_date']).dt.days

        # Negative duration (end before start)
        negative_duration = df[df['duration'] < 0]
        for idx, row in negative_duration.iterrows():
            anomalies.append(Anomaly(
                id=f"SCHED-NEG-{idx}",
                anomaly_type=AnomalyType.IMPOSSIBLE_VALUE,
                severity=AnomalySeverity.CRITICAL,
                field="duration",
                value=row['duration'],
                description="End date before start date",
                row_index=idx,
                detection_method="Business Rule",
                confidence=1.0,
                suggested_action="Correct dates"
            ))

        # Extremely long durations
        long_tasks = df[df['duration'] > self.SCHEDULE_THRESHOLDS['max_activity_duration']]
        for idx, row in long_tasks.iterrows():
            anomalies.append(Anomaly(
                id=f"SCHED-LONG-{idx}",
                anomaly_type=AnomalyType.OUTLIER,
                severity=AnomalySeverity.MEDIUM,
                field="duration",
                value=row['duration'],
                expected_range=(0, self.SCHEDULE_THRESHOLDS['max_activity_duration']),
                description=f"Task duration {row['duration']} days exceeds threshold",
                row_index=idx,
                detection_method="Threshold",
                confidence=0.9,
                suggested_action="Review if task should be broken down"
            ))

        # Zero duration non-milestones
        if 'is_milestone' in df.columns:
            zero_duration = df[(df['duration'] == 0) & (~df['is_milestone'])]
            for idx, row in zero_duration.iterrows():
                anomalies.append(Anomaly(
                    id=f"SCHED-ZERO-{idx}",
                    anomaly_type=AnomalyType.IMPOSSIBLE_VALUE,
                    severity=AnomalySeverity.HIGH,
                    field="duration",
                    value=0,
                    description="Zero duration task that is not a milestone",
                    row_index=idx,
                    detection_method="Business Rule",
                    confidence=1.0,
                    suggested_action="Add duration or mark as milestone"
                ))

        return anomalies

    def detect_productivity_anomalies(self, df: pd.DataFrame,
                                      quantity_col: str,
                                      hours_col: str) -> List[Anomaly]:
        """Detect productivity anomalies."""
        anomalies = []

        # Calculate productivity
        df['productivity'] = df[quantity_col] / df[hours_col].replace(0, np.nan)

        # Use Modified Z-Score (more robust for skewed data)
        median = df['productivity'].median()
        mad = np.abs(df['productivity'] - median).median()
        modified_z = 0.6745 * (df['productivity'] - median) / mad

        outliers = df[np.abs(modified_z) > 3.5]

        for idx, row in outliers.iterrows():
            prod = row['productivity']
            z = modified_z.loc[idx]

            severity = AnomalySeverity.HIGH if abs(z) > 5 else AnomalySeverity.MEDIUM
            direction = "high" if z > 0 else "low"

            anomalies.append(Anomaly(
                id=f"PROD-{idx}",
                anomaly_type=AnomalyType.OUTLIER,
                severity=severity,
                field="productivity",
                value=prod,
                description=f"Unusually {direction} productivity: {prod:.2f} units/hour",
                row_index=idx,
                detection_method="Modified Z-Score",
                confidence=min(abs(z) / 7, 1.0),
                suggested_action=f"Investigate {direction} productivity cause"
            ))

        return anomalies

    def detect_time_series_anomalies(self, df: pd.DataFrame,
                                      date_col: str,
                                      value_col: str,
                                      window: int = 7) -> List[Anomaly]:
        """Detect anomalies in time series data (e.g., daily costs, progress)."""
        anomalies = []

        df = df.sort_values(date_col).copy()
        df['rolling_mean'] = df[value_col].rolling(window=window, center=True).mean()
        df['rolling_std'] = df[value_col].rolling(window=window, center=True).std()

        # Points outside 2 standard deviations from rolling mean
        df['z_score'] = (df[value_col] - df['rolling_mean']) / df['rolling_std']

        outliers = df[np.abs(df['z_score']) > 2].dropna()

        for idx, row in outliers.iterrows():
            anomalies.append(Anomaly(
                id=f"TS-{idx}",
                anomaly_type=AnomalyType.TREND_DEVIATION,
                severity=AnomalySeverity.MEDIUM if abs(row['z_score']) < 3 else AnomalySeverity.HIGH,
                field=value_col,
                value=row[value_col],
                expected_range=(
                    row['rolling_mean'] - 2 * row['rolling_std'],
                    row['rolling_mean'] + 2 * row['rolling_std']
                ),
                description=f"Value deviates from {window}-day trend",
                row_index=idx,
                detection_method="Rolling Z-Score",
                confidence=min(abs(row['z_score']) / 4, 1.0)
            ))

        return anomalies

    def detect_duplicate_anomalies(self, df: pd.DataFrame,
                                   key_columns: List[str]) -> List[Anomaly]:
        """Detect duplicate records."""
        anomalies = []

        duplicates = df[df.duplicated(subset=key_columns, keep=False)]

        if len(duplicates) > 0:
            dup_groups = duplicates.groupby(key_columns).size()
            for keys, count in dup_groups.items():
                anomalies.append(Anomaly(
                    id=f"DUP-{hash(str(keys)) % 10000}",
                    anomaly_type=AnomalyType.DUPLICATE,
                    severity=AnomalySeverity.HIGH,
                    field=str(key_columns),
                    value=keys,
                    description=f"Found {count} duplicate records for {keys}",
                    detection_method="Exact Match",
                    confidence=1.0,
                    suggested_action="Review and remove duplicates"
                ))

        return anomalies

    def detect_sequence_gaps(self, df: pd.DataFrame, sequence_col: str) -> List[Anomaly]:
        """Detect gaps in sequential data (invoice numbers, PO numbers, etc.)."""
        anomalies = []

        # Extract numeric part if mixed format
        df['seq_num'] = pd.to_numeric(
            df[sequence_col].astype(str).str.extract(r'(\d+)')[0],
            errors='coerce'
        )

        sorted_seq = df['seq_num'].dropna().sort_values()
        expected = range(int(sorted_seq.min()), int(sorted_seq.max()) + 1)
        actual = set(sorted_seq.astype(int))
        missing = set(expected) - actual

        if missing:
            # Group consecutive missing numbers
            missing_ranges = []
            sorted_missing = sorted(missing)
            start = sorted_missing[0]
            end = start

            for num in sorted_missing[1:]:
                if num == end + 1:
                    end = num
                else:
                    missing_ranges.append((start, end))
                    start = num
                    end = num
            missing_ranges.append((start, end))

            for start, end in missing_ranges:
                range_str = str(start) if start == end else f"{start}-{end}"
                anomalies.append(Anomaly(
                    id=f"SEQ-{start}",
                    anomaly_type=AnomalyType.MISSING_SEQUENCE,
                    severity=AnomalySeverity.MEDIUM,
                    field=sequence_col,
                    value=range_str,
                    description=f"Missing sequence number(s): {range_str}",
                    detection_method="Sequence Analysis",
                    confidence=1.0,
                    suggested_action="Investigate missing numbers"
                ))

        return anomalies

    def run_full_detection(self, df: pd.DataFrame, config: Dict) -> AnomalyReport:
        """Run all applicable anomaly detection methods."""
        all_anomalies = []

        # Cost anomalies
        if 'cost_columns' in config:
            for col in config['cost_columns']:
                if col in df.columns:
                    all_anomalies.extend(
                        self.detect_cost_anomalies(df, col, config.get('group_by'))
                    )

        # Schedule anomalies
        if 'start_date' in df.columns and 'end_date' in df.columns:
            all_anomalies.extend(self.detect_schedule_anomalies(df))

        # Productivity
        if 'quantity_col' in config and 'hours_col' in config:
            all_anomalies.extend(
                self.detect_productivity_anomalies(
                    df, config['quantity_col'], config['hours_col']
                )
            )

        # Duplicates
        if 'key_columns' in config:
            all_anomalies.extend(
                self.detect_duplicate_anomalies(df, config['key_columns'])
            )

        # Sequence gaps
        if 'sequence_column' in config:
            all_anomalies.extend(
                self.detect_sequence_gaps(df, config['sequence_column'])
            )

        # Create summary
        summary = {}
        for a in all_anomalies:
            key = f"{a.anomaly_type.value}_{a.severity.value}"
            summary[key] = summary.get(key, 0) + 1

        report = AnomalyReport(
            source=config.get('source_name', 'Unknown'),
            detected_at=datetime.now(),
            total_records=len(df),
            anomalies=all_anomalies,
            summary=summary
        )

        self.detection_history.append(report)
        return report

    def generate_report(self, report: AnomalyReport) -> str:
        """Generate markdown anomaly report."""
        lines = [f"# Anomaly Detection Report", ""]
        lines.append(f"**Source:** {report.source}")
        lines.append(f"**Detected At:** {report.detected_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Total Records:** {report.total_records:,}")
        lines.append(f"**Anomalies Found:** {len(report.anomalies)}")
        lines.append("")

        # Summary by severity
        lines.append("## Summary by Severity")
        for severity in AnomalySeverity:
            count = sum(1 for a in report.anomalies if a.severity == severity)
            if count > 0:
                lines.append(f"- **{severity.value.upper()}:** {count}")
        lines.append("")

        # Critical anomalies first
        critical = [a for a in report.anomalies if a.severity == AnomalySeverity.CRITICAL]
        if critical:
            lines.append("## Critical Anomalies")
            for a in critical:
                lines.append(f"\n### {a.id}")
                lines.append(f"- **Type:** {a.anomaly_type.value}")
                lines.append(f"- **Field:** {a.field}")
                lines.append(f"- **Value:** {a.value}")
                lines.append(f"- **Description:** {a.description}")
                lines.append(f"- **Action:** {a.suggested_action}")

        # All anomalies table
        lines.append("\n## All Anomalies")
        lines.append("| ID | Type | Severity | Field | Description |")
        lines.append("|-----|------|----------|-------|-------------|")
        for a in report.anomalies[:50]:
            lines.append(f"| {a.id} | {a.anomaly_type.value} | {a.severity.value} | {a.field} | {a.description[:50]} |")

        if len(report.anomalies) > 50:
            lines.append(f"\n*... and {len(report.anomalies) - 50} more anomalies*")

        return "\n".join(lines)
```

## Quick Start

```python
import pandas as pd

# Load data
df = pd.read_excel("project_costs.xlsx")

# Initialize detector
detector = ConstructionAnomalyDetector()

# Run detection
config = {
    'source_name': 'Project Costs Q1 2026',
    'cost_columns': ['total_cost', 'labor_cost', 'material_cost'],
    'group_by': 'cost_code',
    'key_columns': ['project_id', 'cost_code', 'date'],
    'sequence_column': 'invoice_number'
}

report = detector.run_full_detection(df, config)

# Generate report
print(detector.generate_report(report))

# Get critical anomalies for immediate action
critical = [a for a in report.anomalies if a.severity == AnomalySeverity.CRITICAL]
print(f"\n{len(critical)} critical anomalies require immediate attention")
```

## Dependencies

```bash
pip install pandas numpy scipy
```

## Resources

- **Statistical Methods**: IQR, Z-Score, Modified Z-Score
- **Construction Benchmarks**: RSMeans, ENR indices
