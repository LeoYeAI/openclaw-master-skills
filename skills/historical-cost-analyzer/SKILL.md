---
name: "historical-cost-analyzer"
description: "Analyze historical construction costs for benchmarking, trend analysis, and estimating calibration. Compare projects, track escalation, identify patterns."
---

# Historical Cost Analyzer for Construction

## Overview

Analyze historical construction cost data for benchmarking, escalation tracking, and estimating calibration. Compare similar projects, identify cost drivers, and improve future estimates.

## Business Case

Historical cost analysis enables:
- **Benchmarking**: Compare current estimates to past projects
- **Calibration**: Improve estimating accuracy using actual data
- **Trends**: Track cost escalation and market changes
- **Risk Assessment**: Identify cost drivers and overrun patterns

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

@dataclass
class CostBenchmark:
    metric_name: str
    value: float
    unit: str
    percentile_25: float
    percentile_50: float
    percentile_75: float
    sample_size: int
    project_types: List[str]

@dataclass
class EscalationAnalysis:
    from_year: int
    to_year: int
    annual_rate: float
    total_change: float
    category: str
    confidence: float

@dataclass
class CostDriver:
    factor: str
    impact_percentage: float
    correlation: float
    description: str

class HistoricalCostAnalyzer:
    """Analyze historical construction costs."""

    # RSMeans City Cost Indexes (sample - would be loaded from database)
    LOCATION_FACTORS = {
        'New York': 1.32, 'San Francisco': 1.28, 'Los Angeles': 1.15,
        'Chicago': 1.12, 'Houston': 0.92, 'Dallas': 0.89,
        'Phoenix': 0.93, 'Atlanta': 0.91, 'Denver': 1.02,
        'Seattle': 1.08, 'National Average': 1.00
    }

    # Historical cost indices by year
    COST_INDICES = {
        2015: 100.0, 2016: 102.1, 2017: 105.3, 2018: 109.2,
        2019: 112.5, 2020: 114.8, 2021: 121.4, 2022: 135.6,
        2023: 142.3, 2024: 148.7, 2025: 154.2, 2026: 160.0
    }

    def __init__(self, historical_data: pd.DataFrame = None):
        self.data = historical_data
        self.benchmarks: Dict[str, CostBenchmark] = {}

    def load_data(self, data: pd.DataFrame):
        """Load historical project data."""
        self.data = data.copy()

        # Normalize data
        if 'completion_year' not in self.data.columns and 'completion_date' in self.data.columns:
            self.data['completion_year'] = pd.to_datetime(self.data['completion_date']).dt.year

        # Calculate key metrics
        if 'gross_area' in self.data.columns and 'final_cost' in self.data.columns:
            self.data['cost_per_sf'] = self.data['final_cost'] / self.data['gross_area']

        if 'original_estimate' in self.data.columns and 'final_cost' in self.data.columns:
            self.data['overrun_pct'] = ((self.data['final_cost'] - self.data['original_estimate'])
                                         / self.data['original_estimate'] * 100)

    def normalize_to_year(self, costs: pd.Series, from_years: pd.Series,
                          to_year: int = 2026) -> pd.Series:
        """Normalize costs to a common year using cost indices."""
        normalized = costs.copy()

        for i, (cost, year) in enumerate(zip(costs, from_years)):
            if pd.notna(cost) and pd.notna(year):
                year = int(year)
                if year in self.COST_INDICES and to_year in self.COST_INDICES:
                    factor = self.COST_INDICES[to_year] / self.COST_INDICES[year]
                    normalized.iloc[i] = cost * factor

        return normalized

    def normalize_to_location(self, costs: pd.Series, locations: pd.Series,
                               to_location: str = 'National Average') -> pd.Series:
        """Normalize costs to a common location."""
        normalized = costs.copy()
        to_factor = self.LOCATION_FACTORS.get(to_location, 1.0)

        for i, (cost, loc) in enumerate(zip(costs, locations)):
            if pd.notna(cost) and loc in self.LOCATION_FACTORS:
                from_factor = self.LOCATION_FACTORS[loc]
                normalized.iloc[i] = cost * (to_factor / from_factor)

        return normalized

    def calculate_benchmarks(self, project_type: str = None,
                              year_range: Tuple[int, int] = None) -> Dict[str, CostBenchmark]:
        """Calculate cost benchmarks from historical data."""
        df = self.data.copy()

        # Filter by project type
        if project_type and 'project_type' in df.columns:
            df = df[df['project_type'] == project_type]

        # Filter by year range
        if year_range and 'completion_year' in df.columns:
            df = df[(df['completion_year'] >= year_range[0]) &
                    (df['completion_year'] <= year_range[1])]

        benchmarks = {}

        # Cost per SF
        if 'cost_per_sf' in df.columns:
            values = df['cost_per_sf'].dropna()
            if len(values) > 0:
                benchmarks['cost_per_sf'] = CostBenchmark(
                    metric_name='Cost per SF',
                    value=values.median(),
                    unit='$/SF',
                    percentile_25=values.quantile(0.25),
                    percentile_50=values.quantile(0.50),
                    percentile_75=values.quantile(0.75),
                    sample_size=len(values),
                    project_types=[project_type] if project_type else df['project_type'].unique().tolist()
                )

        # Overrun percentage
        if 'overrun_pct' in df.columns:
            values = df['overrun_pct'].dropna()
            if len(values) > 0:
                benchmarks['overrun_pct'] = CostBenchmark(
                    metric_name='Cost Overrun',
                    value=values.median(),
                    unit='%',
                    percentile_25=values.quantile(0.25),
                    percentile_50=values.quantile(0.50),
                    percentile_75=values.quantile(0.75),
                    sample_size=len(values),
                    project_types=[project_type] if project_type else df['project_type'].unique().tolist()
                )

        self.benchmarks.update(benchmarks)
        return benchmarks

    def calculate_escalation(self, category: str = 'overall',
                              from_year: int = 2020,
                              to_year: int = 2026) -> EscalationAnalysis:
        """Calculate cost escalation between years."""
        if from_year in self.COST_INDICES and to_year in self.COST_INDICES:
            from_index = self.COST_INDICES[from_year]
            to_index = self.COST_INDICES[to_year]

            total_change = (to_index - from_index) / from_index
            years = to_year - from_year
            annual_rate = (to_index / from_index) ** (1 / years) - 1 if years > 0 else 0

            return EscalationAnalysis(
                from_year=from_year,
                to_year=to_year,
                annual_rate=annual_rate,
                total_change=total_change,
                category=category,
                confidence=0.95
            )

        return None

    def identify_cost_drivers(self, target_col: str = 'cost_per_sf') -> List[CostDriver]:
        """Identify factors that drive costs."""
        if self.data is None or target_col not in self.data.columns:
            return []

        drivers = []
        target = self.data[target_col].dropna()

        # Analyze numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        exclude = [target_col, 'final_cost', 'original_estimate']

        for col in numeric_cols:
            if col not in exclude:
                valid_mask = self.data[col].notna() & self.data[target_col].notna()
                if valid_mask.sum() > 10:
                    corr, p_value = stats.pearsonr(
                        self.data.loc[valid_mask, col],
                        self.data.loc[valid_mask, target_col]
                    )

                    if abs(corr) > 0.3 and p_value < 0.05:
                        impact = corr * self.data[col].std() / target.std() * 100

                        drivers.append(CostDriver(
                            factor=col,
                            impact_percentage=abs(impact),
                            correlation=corr,
                            description=f"{'Positive' if corr > 0 else 'Negative'} correlation with {target_col}"
                        ))

        # Analyze categorical columns
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns

        for col in categorical_cols:
            if col not in ['project_id', 'project_name']:
                groups = self.data.groupby(col)[target_col].mean()
                if len(groups) > 1:
                    variance = groups.var()
                    overall_var = target.var()

                    if variance / overall_var > 0.1:
                        drivers.append(CostDriver(
                            factor=col,
                            impact_percentage=variance / overall_var * 100,
                            correlation=0,
                            description=f"Categorical factor with significant cost variation"
                        ))

        return sorted(drivers, key=lambda x: -x.impact_percentage)

    def compare_to_benchmark(self, estimate: Dict, project_type: str = None) -> Dict:
        """Compare an estimate to historical benchmarks."""
        if project_type:
            self.calculate_benchmarks(project_type)

        comparison = {}

        # Cost per SF comparison
        if 'cost_per_sf' in estimate and 'cost_per_sf' in self.benchmarks:
            benchmark = self.benchmarks['cost_per_sf']
            value = estimate['cost_per_sf']

            percentile = stats.percentileofscore(
                self.data['cost_per_sf'].dropna(), value
            )

            comparison['cost_per_sf'] = {
                'estimate': value,
                'benchmark_median': benchmark.value,
                'benchmark_range': (benchmark.percentile_25, benchmark.percentile_75),
                'percentile': percentile,
                'status': 'within_range' if benchmark.percentile_25 <= value <= benchmark.percentile_75 else 'outside_range'
            }

        return comparison

    def find_similar_projects(self, criteria: Dict, n: int = 10) -> pd.DataFrame:
        """Find similar historical projects."""
        df = self.data.copy()

        # Filter by criteria
        if 'project_type' in criteria:
            df = df[df['project_type'] == criteria['project_type']]

        if 'gross_area' in criteria:
            target = criteria['gross_area']
            tolerance = criteria.get('area_tolerance', 0.3)
            df = df[(df['gross_area'] >= target * (1 - tolerance)) &
                    (df['gross_area'] <= target * (1 + tolerance))]

        if 'location' in criteria and 'location' in df.columns:
            df = df[df['location'] == criteria['location']]

        if 'year_range' in criteria:
            df = df[(df['completion_year'] >= criteria['year_range'][0]) &
                    (df['completion_year'] <= criteria['year_range'][1])]

        # Sort by similarity (simple: by area difference)
        if 'gross_area' in criteria and 'gross_area' in df.columns:
            df['similarity'] = 1 - abs(df['gross_area'] - criteria['gross_area']) / criteria['gross_area']
            df = df.sort_values('similarity', ascending=False)

        return df.head(n)

    def analyze_overrun_patterns(self) -> Dict:
        """Analyze patterns in cost overruns."""
        if 'overrun_pct' not in self.data.columns:
            return {}

        analysis = {}

        # Overall statistics
        overruns = self.data['overrun_pct'].dropna()
        analysis['overall'] = {
            'mean': overruns.mean(),
            'median': overruns.median(),
            'std': overruns.std(),
            'projects_over_budget': (overruns > 0).sum(),
            'projects_under_budget': (overruns < 0).sum(),
            'pct_over_budget': (overruns > 0).mean() * 100
        }

        # By project type
        if 'project_type' in self.data.columns:
            by_type = self.data.groupby('project_type')['overrun_pct'].agg(['mean', 'std', 'count'])
            analysis['by_type'] = by_type.to_dict('index')

        # By size category
        if 'gross_area' in self.data.columns:
            self.data['size_category'] = pd.cut(
                self.data['gross_area'],
                bins=[0, 10000, 50000, 100000, np.inf],
                labels=['Small (<10k SF)', 'Medium (10-50k SF)', 'Large (50-100k SF)', 'Very Large (>100k SF)']
            )
            by_size = self.data.groupby('size_category')['overrun_pct'].agg(['mean', 'std', 'count'])
            analysis['by_size'] = by_size.to_dict('index')

        return analysis

    def generate_report(self, project_type: str = None) -> str:
        """Generate comprehensive cost analysis report."""
        lines = ["# Historical Cost Analysis Report", ""]
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"**Projects Analyzed:** {len(self.data):,}")
        if project_type:
            lines.append(f"**Project Type:** {project_type}")
        lines.append("")

        # Benchmarks
        benchmarks = self.calculate_benchmarks(project_type)
        if benchmarks:
            lines.append("## Cost Benchmarks")
            for name, bm in benchmarks.items():
                lines.append(f"\n### {bm.metric_name}")
                lines.append(f"- **Median:** {bm.value:.2f} {bm.unit}")
                lines.append(f"- **25th Percentile:** {bm.percentile_25:.2f} {bm.unit}")
                lines.append(f"- **75th Percentile:** {bm.percentile_75:.2f} {bm.unit}")
                lines.append(f"- **Sample Size:** {bm.sample_size}")

        # Escalation
        lines.append("\n## Cost Escalation")
        esc = self.calculate_escalation(from_year=2020, to_year=2026)
        if esc:
            lines.append(f"- **Period:** {esc.from_year} to {esc.to_year}")
            lines.append(f"- **Annual Rate:** {esc.annual_rate:.1%}")
            lines.append(f"- **Total Change:** {esc.total_change:.1%}")

        # Cost Drivers
        drivers = self.identify_cost_drivers()
        if drivers:
            lines.append("\n## Key Cost Drivers")
            for driver in drivers[:5]:
                lines.append(f"- **{driver.factor}:** {driver.impact_percentage:.1f}% impact (r={driver.correlation:.2f})")

        # Overrun Analysis
        overrun_analysis = self.analyze_overrun_patterns()
        if 'overall' in overrun_analysis:
            lines.append("\n## Overrun Analysis")
            overall = overrun_analysis['overall']
            lines.append(f"- **Average Overrun:** {overall['mean']:.1f}%")
            lines.append(f"- **Projects Over Budget:** {overall['pct_over_budget']:.1f}%")

        return "\n".join(lines)
```

## Quick Start

```python
import pandas as pd

# Load historical data
historical = pd.read_excel("historical_projects.xlsx")

# Initialize analyzer
analyzer = HistoricalCostAnalyzer()
analyzer.load_data(historical)

# Calculate benchmarks for office buildings
benchmarks = analyzer.calculate_benchmarks(project_type='Office')
print(f"Office median cost: ${benchmarks['cost_per_sf'].value:.2f}/SF")

# Calculate escalation
escalation = analyzer.calculate_escalation(from_year=2020, to_year=2026)
print(f"Annual escalation: {escalation.annual_rate:.1%}")

# Find similar projects
similar = analyzer.find_similar_projects({
    'project_type': 'Office',
    'gross_area': 50000,
    'year_range': (2020, 2025)
})
print(f"Found {len(similar)} similar projects")

# Compare estimate to benchmark
comparison = analyzer.compare_to_benchmark({'cost_per_sf': 250}, 'Office')
print(f"Estimate percentile: {comparison['cost_per_sf']['percentile']:.0f}th")

# Generate report
report = analyzer.generate_report('Office')
print(report)
```

## Dependencies

```bash
pip install pandas numpy scipy
```
