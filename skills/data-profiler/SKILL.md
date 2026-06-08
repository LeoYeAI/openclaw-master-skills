---
name: "data-profiler"
description: "Profile construction data to understand characteristics, distributions, quality metrics, and patterns. Essential for data quality assessment and ETL planning."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🏷️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Profiler for Construction

## Overview

Analyze construction data to understand its characteristics, distributions, quality, and patterns. Essential for data quality assessment, ETL planning, and identifying data issues before they impact projects.

## Business Case

Before using any construction data, you need to understand:
- What data types are present
- Distribution of values
- Missing data patterns
- Anomalies and outliers
- Referential integrity issues

This skill profiles data to answer these questions and provides actionable insights.

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import json

@dataclass
class ColumnProfile:
    name: str
    data_type: str
    inferred_type: str  # More specific: project_id, cost, date, csi_code, etc.
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    uniqueness_ratio: float
    # For numeric columns
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_dev: Optional[float] = None
    # For string columns
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    # Top values
    top_values: List[Tuple[Any, int]] = field(default_factory=list)
    # Patterns
    common_patterns: List[str] = field(default_factory=list)
    # Quality flags
    quality_issues: List[str] = field(default_factory=list)

@dataclass
class DataProfile:
    source_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    duplicate_rows: int
    memory_usage: str
    profiled_at: datetime
    quality_score: float
    recommendations: List[str]

class ConstructionDataProfiler:
    """Profile construction data for quality and characteristics."""

    # Known construction data patterns
    CONSTRUCTION_PATTERNS = {
        'csi_code': r'^\d{2}\s?\d{2}\s?\d{2}$',
        'project_id': r'^[A-Z]{2,4}[-_]?\d{3,6}$',
        'cost_code': r'^\d{2}[-.]?\d{2,4}$',
        'wbs': r'^[\d.]+$',
        'phone': r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
        'email': r'^[\w.-]+@[\w.-]+\.\w+$',
        'date_iso': r'^\d{4}-\d{2}-\d{2}',
        'date_us': r'^\d{1,2}/\d{1,2}/\d{2,4}$',
        'currency': r'^\$?[\d,]+\.?\d{0,2}$',
        'percentage': r'^\d+\.?\d*%?$',
    }

    # Construction-specific column name patterns
    COLUMN_TYPE_HINTS = {
        'project': ['project_id', 'project_name', 'proj', 'job'],
        'cost': ['cost', 'amount', 'price', 'total', 'budget', 'actual'],
        'date': ['date', 'start', 'finish', 'end', 'created', 'modified'],
        'quantity': ['qty', 'quantity', 'count', 'units'],
        'csi': ['csi', 'division', 'masterformat', 'spec'],
        'location': ['location', 'area', 'zone', 'floor', 'level'],
        'person': ['owner', 'manager', 'superintendent', 'foreman', 'contact'],
    }

    def __init__(self):
        self.profiles: Dict[str, DataProfile] = {}

    def profile_dataframe(self, df: pd.DataFrame, source_name: str) -> DataProfile:
        """Profile a pandas DataFrame."""
        columns = []

        for col in df.columns:
            col_profile = self._profile_column(df[col], col)
            columns.append(col_profile)

        # Calculate duplicates
        duplicate_rows = len(df) - len(df.drop_duplicates())

        # Calculate memory usage
        memory_bytes = df.memory_usage(deep=True).sum()
        if memory_bytes < 1024:
            memory_usage = f"{memory_bytes} B"
        elif memory_bytes < 1024**2:
            memory_usage = f"{memory_bytes/1024:.1f} KB"
        else:
            memory_usage = f"{memory_bytes/1024**2:.1f} MB"

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(columns)

        # Generate recommendations
        recommendations = self._generate_recommendations(columns, df)

        profile = DataProfile(
            source_name=source_name,
            row_count=len(df),
            column_count=len(df.columns),
            columns=columns,
            duplicate_rows=duplicate_rows,
            memory_usage=memory_usage,
            profiled_at=datetime.now(),
            quality_score=quality_score,
            recommendations=recommendations
        )

        self.profiles[source_name] = profile
        return profile

    def _profile_column(self, series: pd.Series, name: str) -> ColumnProfile:
        """Profile a single column."""
        total_count = len(series)
        null_count = series.isnull().sum()
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0

        # Get non-null values for analysis
        non_null = series.dropna()
        unique_count = non_null.nunique()
        uniqueness_ratio = unique_count / len(non_null) if len(non_null) > 0 else 0

        profile = ColumnProfile(
            name=name,
            data_type=str(series.dtype),
            inferred_type=self._infer_construction_type(series, name),
            total_count=total_count,
            null_count=null_count,
            null_percentage=round(null_percentage, 2),
            unique_count=unique_count,
            uniqueness_ratio=round(uniqueness_ratio, 4)
        )

        # Numeric analysis
        if pd.api.types.is_numeric_dtype(series):
            profile.min_value = float(non_null.min()) if len(non_null) > 0 else None
            profile.max_value = float(non_null.max()) if len(non_null) > 0 else None
            profile.mean_value = float(non_null.mean()) if len(non_null) > 0 else None
            profile.median_value = float(non_null.median()) if len(non_null) > 0 else None
            profile.std_dev = float(non_null.std()) if len(non_null) > 1 else None

            # Check for outliers
            if len(non_null) > 10 and profile.std_dev:
                outliers = non_null[abs(non_null - profile.mean_value) > 3 * profile.std_dev]
                if len(outliers) > 0:
                    profile.quality_issues.append(f"{len(outliers)} potential outliers detected")

            # Check for negative costs
            if any(hint in name.lower() for hint in ['cost', 'amount', 'price', 'total']):
                negatives = (non_null < 0).sum()
                if negatives > 0:
                    profile.quality_issues.append(f"{negatives} negative values in cost column")

        # String analysis
        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            str_series = non_null.astype(str)
            lengths = str_series.str.len()
            profile.min_length = int(lengths.min()) if len(lengths) > 0 else None
            profile.max_length = int(lengths.max()) if len(lengths) > 0 else None
            profile.avg_length = float(lengths.mean()) if len(lengths) > 0 else None

            # Detect patterns
            profile.common_patterns = self._detect_patterns(str_series)

        # Top values
        if len(non_null) > 0:
            value_counts = non_null.value_counts().head(5)
            profile.top_values = list(zip(value_counts.index.tolist(), value_counts.values.tolist()))

        # Quality checks
        if null_percentage > 50:
            profile.quality_issues.append("High null rate (>50%)")
        if uniqueness_ratio == 1.0 and total_count > 100:
            profile.quality_issues.append("All unique values - possible ID column")
        if uniqueness_ratio < 0.01 and unique_count > 1:
            profile.quality_issues.append("Low cardinality - possible category")

        return profile

    def _infer_construction_type(self, series: pd.Series, name: str) -> str:
        """Infer construction-specific data type."""
        name_lower = name.lower()

        # Check column name hints
        for type_name, hints in self.COLUMN_TYPE_HINTS.items():
            if any(hint in name_lower for hint in hints):
                return type_name

        # Check data patterns
        non_null = series.dropna().astype(str)
        if len(non_null) == 0:
            return "unknown"

        sample = non_null.head(100)

        for pattern_name, pattern in self.CONSTRUCTION_PATTERNS.items():
            matches = sample.str.match(pattern, na=False).sum()
            if matches / len(sample) > 0.8:
                return pattern_name

        # Default to pandas dtype
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        else:
            return "text"

    def _detect_patterns(self, str_series: pd.Series) -> List[str]:
        """Detect common patterns in string data."""
        patterns_found = []

        sample = str_series.head(1000)

        for pattern_name, pattern in self.CONSTRUCTION_PATTERNS.items():
            matches = sample.str.match(pattern, na=False).sum()
            if matches / len(sample) > 0.1:
                patterns_found.append(f"{pattern_name} ({matches/len(sample):.0%})")

        return patterns_found[:3]

    def _calculate_quality_score(self, columns: List[ColumnProfile]) -> float:
        """Calculate overall data quality score (0-100)."""
        if not columns:
            return 0.0

        scores = []

        for col in columns:
            col_score = 100

            # Penalize for nulls
            col_score -= min(col.null_percentage, 50)

            # Penalize for quality issues
            col_score -= len(col.quality_issues) * 10

            scores.append(max(col_score, 0))

        return round(sum(scores) / len(scores), 1)

    def _generate_recommendations(self, columns: List[ColumnProfile], df: pd.DataFrame) -> List[str]:
        """Generate recommendations based on profile."""
        recommendations = []

        # High null columns
        high_null = [c for c in columns if c.null_percentage > 30]
        if high_null:
            recommendations.append(
                f"Review {len(high_null)} columns with >30% null values: "
                f"{', '.join(c.name for c in high_null[:3])}"
            )

        # Potential ID columns without uniqueness
        for col in columns:
            if 'id' in col.name.lower() and col.uniqueness_ratio < 1.0:
                recommendations.append(
                    f"Column '{col.name}' appears to be an ID but has duplicate values"
                )

        # Date columns that should be datetime
        for col in columns:
            if col.inferred_type in ['date_iso', 'date_us'] and col.data_type == 'object':
                recommendations.append(
                    f"Convert '{col.name}' to datetime type for better analysis"
                )

        # Cost columns that are strings
        for col in columns:
            if col.inferred_type == 'currency' and col.data_type == 'object':
                recommendations.append(
                    f"Convert '{col.name}' to numeric type (remove $ and commas)"
                )

        return recommendations

    def profile_to_dict(self, profile: DataProfile) -> Dict:
        """Convert profile to dictionary for JSON export."""
        return {
            'source_name': profile.source_name,
            'row_count': profile.row_count,
            'column_count': profile.column_count,
            'duplicate_rows': profile.duplicate_rows,
            'memory_usage': profile.memory_usage,
            'profiled_at': profile.profiled_at.isoformat(),
            'quality_score': profile.quality_score,
            'recommendations': profile.recommendations,
            'columns': [
                {
                    'name': c.name,
                    'data_type': c.data_type,
                    'inferred_type': c.inferred_type,
                    'null_percentage': c.null_percentage,
                    'unique_count': c.unique_count,
                    'quality_issues': c.quality_issues,
                    'top_values': c.top_values[:3]
                }
                for c in profile.columns
            ]
        }

    def generate_profile_report(self, profile: DataProfile) -> str:
        """Generate markdown profile report."""
        report = [f"# Data Profile: {profile.source_name}", ""]
        report.append(f"**Profiled At:** {profile.profiled_at.strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Quality Score:** {profile.quality_score}/100")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"- **Rows:** {profile.row_count:,}")
        report.append(f"- **Columns:** {profile.column_count}")
        report.append(f"- **Duplicate Rows:** {profile.duplicate_rows:,}")
        report.append(f"- **Memory Usage:** {profile.memory_usage}")
        report.append("")

        # Recommendations
        if profile.recommendations:
            report.append("## Recommendations")
            for rec in profile.recommendations:
                report.append(f"- {rec}")
            report.append("")

        # Column Details
        report.append("## Column Details")
        report.append("")
        report.append("| Column | Type | Inferred | Nulls | Unique | Issues |")
        report.append("|--------|------|----------|-------|--------|--------|")

        for col in profile.columns:
            issues = len(col.quality_issues)
            report.append(
                f"| {col.name} | {col.data_type} | {col.inferred_type} | "
                f"{col.null_percentage:.1f}% | {col.unique_count:,} | {issues} |"
            )

        # Detailed column profiles
        report.append("")
        report.append("## Detailed Column Profiles")

        for col in profile.columns:
            report.append(f"\n### {col.name}")
            report.append(f"- **Type:** {col.data_type} (inferred: {col.inferred_type})")
            report.append(f"- **Nulls:** {col.null_count:,} ({col.null_percentage:.1f}%)")
            report.append(f"- **Unique Values:** {col.unique_count:,} ({col.uniqueness_ratio:.1%})")

            if col.min_value is not None:
                report.append(f"- **Range:** {col.min_value:,.2f} to {col.max_value:,.2f}")
                report.append(f"- **Mean:** {col.mean_value:,.2f}, Median: {col.median_value:,.2f}")

            if col.min_length is not None:
                report.append(f"- **Length:** {col.min_length} to {col.max_length} (avg: {col.avg_length:.1f})")

            if col.top_values:
                report.append(f"- **Top Values:** {col.top_values[:3]}")

            if col.common_patterns:
                report.append(f"- **Patterns:** {', '.join(col.common_patterns)}")

            if col.quality_issues:
                report.append(f"- **Issues:** {', '.join(col.quality_issues)}")

        return "\n".join(report)

    def compare_profiles(self, profile1: DataProfile, profile2: DataProfile) -> Dict:
        """Compare two profiles to detect schema changes or data drift."""
        comparison = {
            'profiles': [profile1.source_name, profile2.source_name],
            'row_count_change': profile2.row_count - profile1.row_count,
            'quality_change': profile2.quality_score - profile1.quality_score,
            'new_columns': [],
            'removed_columns': [],
            'type_changes': [],
            'null_rate_changes': []
        }

        cols1 = {c.name: c for c in profile1.columns}
        cols2 = {c.name: c for c in profile2.columns}

        # Find new/removed columns
        comparison['new_columns'] = [n for n in cols2 if n not in cols1]
        comparison['removed_columns'] = [n for n in cols1 if n not in cols2]

        # Compare common columns
        for name in cols1:
            if name in cols2:
                c1, c2 = cols1[name], cols2[name]

                if c1.data_type != c2.data_type:
                    comparison['type_changes'].append({
                        'column': name,
                        'from': c1.data_type,
                        'to': c2.data_type
                    })

                null_change = c2.null_percentage - c1.null_percentage
                if abs(null_change) > 10:
                    comparison['null_rate_changes'].append({
                        'column': name,
                        'change': null_change
                    })

        return comparison
```

## Quick Start

```python
import pandas as pd

# Load construction data
df = pd.read_excel("project_costs.xlsx")

# Profile the data
profiler = ConstructionDataProfiler()
profile = profiler.profile_dataframe(df, "Project Costs 2025")

# Generate report
report = profiler.generate_profile_report(profile)
print(report)

# Export to JSON
profile_dict = profiler.profile_to_dict(profile)
with open("profile.json", "w") as f:
    json.dump(profile_dict, f, indent=2)

# Compare with previous profile
old_profile = profiler.profile_dataframe(old_df, "Project Costs 2024")
comparison = profiler.compare_profiles(old_profile, profile)
print(f"Quality changed by: {comparison['quality_change']}")
```

## Common Use Cases

1. **Pre-ETL Analysis**: Profile source data before building pipelines
2. **Quality Monitoring**: Track data quality over time
3. **Schema Validation**: Detect unexpected changes in data structure
4. **Anomaly Detection**: Find outliers and data quality issues

## Dependencies

```bash
pip install pandas numpy
```

## Resources

- **Data Profiling Best Practices**: DAMA DMBOK
- **Construction Data Standards**: CSI MasterFormat, UniFormat
