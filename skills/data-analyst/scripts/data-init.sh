#!/bin/bash
# data-init.sh - Initialize data analysis workspace
# Usage: ./data-init.sh

DATA_DIR="${HOME}/.openclaw/workspace/data-analysis"

echo "🚀 Initializing Data Analysis Workspace"
echo "======================================="

# Create directory structure
mkdir -p "$DATA_DIR"/{data,queries,reports,notebooks,scripts}

# Create queries directory with common patterns
cat > "$DATA_DIR/queries/README.md" << 'EOF'
# SQL Queries

Store reusable SQL queries here.

## Naming Convention
- `daily-<name>.sql` - Daily reports
- `weekly-<name>.sql` - Weekly reports
- `adhoc-<name>.sql` - One-off queries
- `template-<name>.sql` - Reusable templates
EOF

cat > "$DATA_DIR/queries/template-exploration.sql" << 'EOF'
-- Data Exploration Template
-- Replace TABLE_NAME with your table

-- Row count
SELECT COUNT(*) as total_rows FROM TABLE_NAME;

-- Sample data
SELECT * FROM TABLE_NAME LIMIT 10;

-- Column overview (PostgreSQL)
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'TABLE_NAME';

-- Null analysis
-- SELECT 
--     COUNT(*) as total,
--     SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) as nulls,
--     ROUND(SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as null_pct
-- FROM TABLE_NAME;
EOF

# Create report templates
cat > "$DATA_DIR/reports/README.md" << 'EOF'
# Reports Directory

Generated reports go here.

## Report Types
- `weekly-YYYY-MM-DD.md` - Weekly analytics
- `monthly-YYYY-MM.md` - Monthly summaries
- `adhoc-<name>.md` - One-off analyses
EOF

cat > "$DATA_DIR/reports/template-analysis.md" << 'EOF'
# Analysis Report: [Title]

**Date:** [Date]
**Author:** [Name]
**Status:** Draft

## Executive Summary
[2-3 sentences with key findings]

## Question
[What are we trying to answer?]

## Data Sources
- [Source 1]: [Description]
- [Source 2]: [Description]

## Methodology
[How we approached the analysis]

## Findings

### Key Metrics
| Metric | Value | Change | Notes |
|--------|-------|--------|-------|
| | | | |

### Insights
1. **[Insight]**: [Supporting evidence]
2. **[Insight]**: [Supporting evidence]

## Visualizations
[Insert charts/graphs]

## Recommendations
1. [Action to take]
2. [Action to take]

## Appendix
[Supporting data tables, SQL queries used]
EOF

# Create Python analysis template
cat > "$DATA_DIR/scripts/analyze_template.py" << 'EOF'
#!/usr/bin/env python3
"""
Data Analysis Template
Usage: python analyze_template.py --input <file.csv>
"""

import pandas as pd
import argparse
from datetime import datetime

def load_data(filepath):
    """Load data from CSV or Excel."""
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")

def explore_data(df):
    """Basic data exploration."""
    print("\n=== DATA OVERVIEW ===")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"\nColumn Types:\n{df.dtypes}")
    print(f"\nMissing Values:\n{df.isnull().sum()}")
    print(f"\nBasic Statistics:\n{df.describe()}")
    return df

def clean_data(df):
    """Basic data cleaning."""
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # Report on nulls
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        print(f"Columns with nulls: {null_cols}")
    
    return df

def analyze(df):
    """Main analysis logic - customize this."""
    print("\n=== ANALYSIS ===")
    # Add your analysis here
    # Example:
    # - Aggregations
    # - Groupby operations
    # - Statistical tests
    return df

def main():
    parser = argparse.ArgumentParser(description='Data Analysis Script')
    parser.add_argument('--input', '-i', required=True, help='Input file path')
    parser.add_argument('--output', '-o', help='Output file path')
    args = parser.parse_args()
    
    print(f"Loading data from: {args.input}")
    df = load_data(args.input)
    
    df = explore_data(df)
    df = clean_data(df)
    df = analyze(df)
    
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nResults saved to: {args.output}")
    
    print("\n✅ Analysis complete!")

if __name__ == '__main__':
    main()
EOF
chmod +x "$DATA_DIR/scripts/analyze_template.py"

# Create data quality checklist
cat > "$DATA_DIR/data-quality-checklist.md" << 'EOF'
# Data Quality Checklist

Use this for every new dataset.

## Dataset: [Name]
**Source:** [Where it came from]
**Date:** [When received/pulled]
**Rows:** [Count]
**Columns:** [Count]

## Completeness
- [ ] Row count matches expected
- [ ] No unexpected nulls
- [ ] All required columns present

## Accuracy
- [ ] Values in expected ranges
- [ ] Dates are valid
- [ ] IDs/keys are valid

## Consistency
- [ ] No duplicate primary keys
- [ ] Consistent formatting (dates, text case)
- [ ] Referential integrity (foreign keys valid)

## Timeliness
- [ ] Data is current enough for analysis
- [ ] Timestamp columns are recent

## Issues Found
| Issue | Severity | Resolution |
|-------|----------|------------|
| | | |

## Cleaning Actions Taken
1. 
2. 
3. 
EOF

echo "✅ Created: $DATA_DIR/data/"
echo "✅ Created: $DATA_DIR/queries/"
echo "✅ Created: $DATA_DIR/reports/"
echo "✅ Created: $DATA_DIR/scripts/"
echo "✅ Created: $DATA_DIR/data-quality-checklist.md"
echo ""
echo "🎉 Data analysis workspace ready!"
echo ""
echo "Quick start:"
echo "  1. Put data files in data/"
echo "  2. Store SQL queries in queries/"
echo "  3. Use scripts/analyze_template.py as starting point"
echo "  4. Generate reports in reports/"
