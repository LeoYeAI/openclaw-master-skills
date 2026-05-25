---
name: "data-quality-check"
description: "Assess construction data quality using completeness, accuracy, consistency, timeliness, and validity metrics. Automated validation with regex patterns, thresholds, and reporting."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "✔️", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Quality Check for Construction

## Overview

Based on DDC methodology (Chapter 2.6), this skill provides comprehensive data quality assessment for construction projects. Poor data quality leads to poor decisions - validate early, validate often.

**Book Reference:** "Требования к качеству данных и его обеспечение" / "Data Quality Requirements"

> "Качество данных определяется пятью ключевыми метриками: полнота, точность, согласованность, своевременность и достоверность."
> — DDC Book, Chapter 2.6

## Quick Start

```python
import pandas as pd

# Load construction data
df = pd.read_excel("bim_export.xlsx")

# Quick quality check
quality_score = {
    'completeness': (1 - df.isnull().sum().sum() / df.size) * 100,
    'unique_ids': df['ElementId'].nunique() == len(df),
    'valid_volumes': (df['Volume_m3'] >= 0).all()
}

print(f"Completeness: {quality_score['completeness']:.1f}%")
print(f"Unique IDs: {quality_score['unique_ids']}")
print(f"Valid volumes: {quality_score['valid_volumes']}")
```

## Data Quality Dimensions

### The 5 Quality Metrics

```python
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

class DataQualityChecker:
    """Comprehensive data quality assessment for construction data"""

    def __init__(self, df):
        self.df = df.copy()
        self.results = {}
        self.issues = []

    def check_completeness(self, required_columns=None):
        """Check for missing values (Полнота)"""
        if required_columns is None:
            required_columns = self.df.columns.tolist()

        completeness = {}
        for col in required_columns:
            if col in self.df.columns:
                non_null = self.df[col].notna().sum()
                total = len(self.df)
                completeness[col] = (non_null / total) * 100
            else:
                completeness[col] = 0
                self.issues.append(f"Missing required column: {col}")

        overall = np.mean(list(completeness.values()))

        self.results['completeness'] = {
            'by_column': completeness,
            'overall': overall,
            'threshold': 95,
            'passed': overall >= 95
        }

        return self.results['completeness']

    def check_accuracy(self, rules=None):
        """Check data accuracy against rules (Точность)"""
        if rules is None:
            # Default construction data rules
            rules = {
                'Volume_m3': {'min': 0, 'max': 10000},
                'Area_m2': {'min': 0, 'max': 100000},
                'Weight_kg': {'min': 0, 'max': 1000000},
                'Cost': {'min': 0, 'max': 100000000}
            }

        accuracy = {}
        for col, bounds in rules.items():
            if col in self.df.columns:
                valid = self.df[col].between(
                    bounds.get('min', -np.inf),
                    bounds.get('max', np.inf)
                ).sum()
                total = self.df[col].notna().sum()
                accuracy[col] = (valid / total * 100) if total > 0 else 100

                # Log invalid values
                invalid_count = total - valid
                if invalid_count > 0:
                    self.issues.append(
                        f"{col}: {invalid_count} values outside range [{bounds.get('min')}, {bounds.get('max')}]"
                    )

        overall = np.mean(list(accuracy.values())) if accuracy else 100

        self.results['accuracy'] = {
            'by_column': accuracy,
            'overall': overall,
            'threshold': 98,
            'passed': overall >= 98
        }

        return self.results['accuracy']

    def check_consistency(self, unique_cols=None, relationship_rules=None):
        """Check data consistency (Согласованность)"""
        consistency = {}

        # Check unique columns
        if unique_cols is None:
            unique_cols = ['ElementId']

        for col in unique_cols:
            if col in self.df.columns:
                is_unique = self.df[col].nunique() == len(self.df)
                consistency[f'{col}_unique'] = 100 if is_unique else \
                    (self.df[col].nunique() / len(self.df) * 100)

                if not is_unique:
                    duplicates = self.df[self.df[col].duplicated()][col].unique()
                    self.issues.append(f"Duplicate {col}: {len(duplicates)} duplicates found")

        # Check cross-field relationships
        if relationship_rules is None:
            relationship_rules = [
                ('End_Date', '>=', 'Start_Date'),
                ('Gross_Volume', '>=', 'Net_Volume')
            ]

        for col1, op, col2 in relationship_rules:
            if col1 in self.df.columns and col2 in self.df.columns:
                if op == '>=':
                    valid = (self.df[col1] >= self.df[col2]).sum()
                elif op == '>':
                    valid = (self.df[col1] > self.df[col2]).sum()
                elif op == '==':
                    valid = (self.df[col1] == self.df[col2]).sum()

                total = self.df[[col1, col2]].notna().all(axis=1).sum()
                consistency[f'{col1}_{op}_{col2}'] = (valid / total * 100) if total > 0 else 100

        overall = np.mean(list(consistency.values())) if consistency else 100

        self.results['consistency'] = {
            'checks': consistency,
            'overall': overall,
            'threshold': 99,
            'passed': overall >= 99
        }

        return self.results['consistency']

    def check_timeliness(self, date_col='Modified_Date', max_age_days=30):
        """Check data timeliness (Своевременность)"""
        if date_col not in self.df.columns:
            self.results['timeliness'] = {
                'overall': None,
                'message': f'Column {date_col} not found'
            }
            return self.results['timeliness']

        dates = pd.to_datetime(self.df[date_col], errors='coerce')
        cutoff = datetime.now() - timedelta(days=max_age_days)

        recent = (dates >= cutoff).sum()
        total = dates.notna().sum()
        timeliness_pct = (recent / total * 100) if total > 0 else 0

        oldest = dates.min()
        newest = dates.max()
        avg_age = (datetime.now() - dates.mean()).days if dates.notna().any() else None

        self.results['timeliness'] = {
            'recent_percentage': timeliness_pct,
            'oldest_record': oldest,
            'newest_record': newest,
            'average_age_days': avg_age,
            'threshold': 80,
            'passed': timeliness_pct >= 80
        }

        return self.results['timeliness']

    def check_validity(self, patterns=None):
        """Check data validity with regex patterns (Достоверность)"""
        if patterns is None:
            patterns = {
                'ElementId': r'^[A-Z]{1,3}\d{3,6}$',  # e.g., W001, FL12345
                'Level': r'^Level\s*\d+$|^L\d+$|^Уровень\s*\d+$',
                'Email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
                'Phone': r'^\+?\d{10,15}$'
            }

        validity = {}
        for col, pattern in patterns.items():
            if col in self.df.columns:
                non_null = self.df[col].dropna()
                if len(non_null) > 0:
                    matches = non_null.astype(str).str.match(pattern).sum()
                    validity[col] = (matches / len(non_null) * 100)

                    invalid = len(non_null) - matches
                    if invalid > 0:
                        self.issues.append(f"{col}: {invalid} values don't match pattern")
                else:
                    validity[col] = 100

        overall = np.mean(list(validity.values())) if validity else 100

        self.results['validity'] = {
            'by_column': validity,
            'overall': overall,
            'threshold': 95,
            'passed': overall >= 95
        }

        return self.results['validity']

    def run_full_check(self):
        """Run all quality checks"""
        self.check_completeness()
        self.check_accuracy()
        self.check_consistency()
        self.check_timeliness()
        self.check_validity()

        # Calculate overall score
        scores = []
        for metric in ['completeness', 'accuracy', 'consistency', 'validity']:
            if metric in self.results and self.results[metric].get('overall'):
                scores.append(self.results[metric]['overall'])

        self.results['overall_score'] = np.mean(scores) if scores else 0
        self.results['grade'] = self._calculate_grade(self.results['overall_score'])
        self.results['issues'] = self.issues

        return self.results

    def _calculate_grade(self, score):
        """Calculate quality grade"""
        if score >= 98:
            return 'A+'
        elif score >= 95:
            return 'A'
        elif score >= 90:
            return 'B'
        elif score >= 80:
            return 'C'
        elif score >= 70:
            return 'D'
        else:
            return 'F'

    def generate_report(self):
        """Generate quality report"""
        if not self.results:
            self.run_full_check()

        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY REPORT")
        report.append("=" * 60)
        report.append(f"Records analyzed: {len(self.df)}")
        report.append(f"Columns: {len(self.df.columns)}")
        report.append("")
        report.append(f"OVERALL SCORE: {self.results['overall_score']:.1f}% (Grade: {self.results['grade']})")
        report.append("")
        report.append("-" * 60)

        # Detail by dimension
        for metric in ['completeness', 'accuracy', 'consistency', 'validity', 'timeliness']:
            if metric in self.results:
                r = self.results[metric]
                passed = '✓' if r.get('passed', False) else '✗'
                overall = r.get('overall', r.get('recent_percentage', 'N/A'))
                if isinstance(overall, (int, float)):
                    report.append(f"{metric.upper():15s}: {overall:>6.1f}% {passed}")
                else:
                    report.append(f"{metric.upper():15s}: {overall}")

        report.append("-" * 60)

        if self.issues:
            report.append("")
            report.append("ISSUES FOUND:")
            for issue in self.issues[:10]:  # Show first 10
                report.append(f"  • {issue}")
            if len(self.issues) > 10:
                report.append(f"  ... and {len(self.issues) - 10} more issues")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
```

## Validation Rules Builder

### Custom Validation Rules

```python
class ValidationRulesBuilder:
    """Build custom validation rules for construction data"""

    def __init__(self):
        self.rules = []

    def add_not_null(self, column):
        """Column must not have null values"""
        self.rules.append({
            'type': 'not_null',
            'column': column,
            'check': lambda df, col=column: df[col].notna().all()
        })
        return self

    def add_unique(self, column):
        """Column must have unique values"""
        self.rules.append({
            'type': 'unique',
            'column': column,
            'check': lambda df, col=column: df[col].nunique() == len(df)
        })
        return self

    def add_range(self, column, min_val=None, max_val=None):
        """Column values must be within range"""
        self.rules.append({
            'type': 'range',
            'column': column,
            'min': min_val,
            'max': max_val,
            'check': lambda df, col=column, mn=min_val, mx=max_val:
                df[col].between(mn or -np.inf, mx or np.inf).all()
        })
        return self

    def add_regex(self, column, pattern):
        """Column values must match regex pattern"""
        self.rules.append({
            'type': 'regex',
            'column': column,
            'pattern': pattern,
            'check': lambda df, col=column, p=pattern:
                df[col].astype(str).str.match(p).all()
        })
        return self

    def add_in_list(self, column, valid_values):
        """Column values must be in list"""
        self.rules.append({
            'type': 'in_list',
            'column': column,
            'valid_values': valid_values,
            'check': lambda df, col=column, vals=valid_values:
                df[col].isin(vals).all()
        })
        return self

    def add_custom(self, name, check_func):
        """Add custom validation function"""
        self.rules.append({
            'type': 'custom',
            'name': name,
            'check': check_func
        })
        return self

    def validate(self, df):
        """Run all validation rules"""
        results = []

        for rule in self.rules:
            try:
                passed = rule['check'](df)
                results.append({
                    'rule': rule.get('name', f"{rule['type']}:{rule.get('column', 'custom')}"),
                    'passed': passed,
                    'type': rule['type']
                })
            except Exception as e:
                results.append({
                    'rule': rule.get('name', f"{rule['type']}:{rule.get('column', 'custom')}"),
                    'passed': False,
                    'error': str(e)
                })

        return results

# Usage example
rules = (ValidationRulesBuilder()
    .add_not_null('ElementId')
    .add_unique('ElementId')
    .add_range('Volume_m3', min_val=0)
    .add_range('Cost', min_val=0)
    .add_in_list('Category', ['Wall', 'Floor', 'Column', 'Beam', 'Slab'])
    .add_regex('Level', r'^Level\s*\d+$')
)

results = rules.validate(df)
for r in results:
    status = '✓' if r['passed'] else '✗'
    print(f"{status} {r['rule']}")
```

## Automated Quality Pipeline

```python
class DataQualityPipeline:
    """Automated data quality pipeline"""

    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.history = []

    def _default_config(self):
        return {
            'required_columns': ['ElementId', 'Category', 'Volume_m3'],
            'unique_columns': ['ElementId'],
            'numeric_ranges': {
                'Volume_m3': (0, 10000),
                'Area_m2': (0, 100000),
                'Cost': (0, 100000000)
            },
            'valid_categories': ['Wall', 'Floor', 'Column', 'Beam', 'Slab',
                                 'Foundation', 'Roof', 'Stair', 'Door', 'Window'],
            'min_quality_score': 90
        }

    def run(self, df, source_name='unknown'):
        """Run quality pipeline"""
        checker = DataQualityChecker(df)

        # Configure checks based on config
        checker.check_completeness(self.config['required_columns'])
        checker.check_accuracy({
            col: {'min': r[0], 'max': r[1]}
            for col, r in self.config['numeric_ranges'].items()
        })
        checker.check_consistency(self.config['unique_columns'])
        checker.check_validity()

        results = checker.run_full_check()

        # Store in history
        self.history.append({
            'timestamp': datetime.now(),
            'source': source_name,
            'records': len(df),
            'score': results['overall_score'],
            'grade': results['grade'],
            'issues_count': len(results['issues'])
        })

        # Check threshold
        passed = results['overall_score'] >= self.config['min_quality_score']

        return {
            'passed': passed,
            'score': results['overall_score'],
            'grade': results['grade'],
            'details': results,
            'report': checker.generate_report()
        }

    def get_history_summary(self):
        """Get quality history summary"""
        if not self.history:
            return "No quality checks performed yet."

        df_history = pd.DataFrame(self.history)
        return {
            'total_checks': len(self.history),
            'avg_score': df_history['score'].mean(),
            'min_score': df_history['score'].min(),
            'max_score': df_history['score'].max(),
            'latest': self.history[-1]
        }
```

## Quality Reporting

### Export Quality Report

```python
def export_quality_report(df, output_path, include_details=True):
    """Export comprehensive quality report to Excel"""
    checker = DataQualityChecker(df)
    results = checker.run_full_check()

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary = pd.DataFrame({
            'Metric': ['Overall Score', 'Grade', 'Records', 'Columns', 'Issues'],
            'Value': [
                f"{results['overall_score']:.1f}%",
                results['grade'],
                len(df),
                len(df.columns),
                len(results['issues'])
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)

        # Completeness details
        if 'completeness' in results:
            comp_df = pd.DataFrame.from_dict(
                results['completeness']['by_column'],
                orient='index',
                columns=['Completeness_%']
            )
            comp_df.to_excel(writer, sheet_name='Completeness')

        # Issues list
        if results['issues']:
            issues_df = pd.DataFrame({'Issue': results['issues']})
            issues_df.to_excel(writer, sheet_name='Issues', index=False)

        # Missing values analysis
        if include_details:
            missing = df.isnull().sum()
            missing_df = pd.DataFrame({
                'Column': missing.index,
                'Missing_Count': missing.values,
                'Missing_%': (missing.values / len(df) * 100).round(2)
            })
            missing_df.to_excel(writer, sheet_name='Missing_Values', index=False)

    return output_path
```

## Quick Reference

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Completeness | % non-null values | ≥ 95% |
| Accuracy | Values within valid range | ≥ 98% |
| Consistency | Unique IDs, valid relationships | ≥ 99% |
| Validity | Match expected patterns | ≥ 95% |
| Timeliness | Records updated recently | ≥ 80% |

## Common Validation Patterns

```python
# Construction-specific regex patterns
PATTERNS = {
    'element_id': r'^[A-Z]{1,3}\d{3,8}$',
    'revit_id': r'^\d{5,8}$',
    'ifc_guid': r'^[A-Za-z0-9_$]{22}$',
    'level': r'^(Level|L|Уровень)\s*[-]?\d+$',
    'grid': r'^[A-Z]{1,2}[-/]?\d{0,3}$',
    'date_iso': r'^\d{4}-\d{2}-\d{2}$',
    'cost_code': r'^\d{2,3}[.-]\d{2,4}[.-]?\d{0,4}$'
}
```

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.6
- **Website**: https://datadrivenconstruction.io
- **Great Expectations**: https://greatexpectations.io

## Next Steps

- See `bim-validation-pipeline` for BIM-specific validation
- See `etl-pipeline` for data processing pipelines
- See `data-visualization` for quality dashboards
