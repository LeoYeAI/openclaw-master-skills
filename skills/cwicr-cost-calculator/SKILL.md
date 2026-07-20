---
name: "cwicr-cost-calculator"
description: "Calculate construction costs using DDC CWICR resource-based methodology. Break down costs into labor, materials, equipment with transparent pricing."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw":{"emoji":"💰","os":["darwin","linux","win32"],"homepage":"https://datadrivenconstruction.io","requires":{"bins":["python3"]}}}
---

# CWICR Cost Calculator

## Business Case

### Problem Statement
Traditional cost estimation often produces "black box" estimates with hidden markups. Stakeholders need:
- Transparent cost breakdowns
- Traceable pricing logic
- Auditable calculations
- Resource-level detail

### Solution
Resource-based cost calculation using CWICR methodology that separates physical norms (labor hours, material quantities) from volatile prices, enabling transparent and auditable estimates.

### Business Value
- **Full transparency** - Every cost component visible
- **Auditable** - Traceable calculation logic
- **Flexible** - Update prices without changing norms
- **Accurate** - Based on 55,000+ validated work items

## Technical Implementation

### Prerequisites
```bash
pip install pandas numpy
```

### Python Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class CostComponent(Enum):
    """Cost breakdown components."""
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    OVERHEAD = "overhead"
    PROFIT = "profit"
    TOTAL = "total"


class CostStatus(Enum):
    """Cost calculation status."""
    CALCULATED = "calculated"
    ESTIMATED = "estimated"
    MISSING_DATA = "missing_data"
    ERROR = "error"


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a work item."""
    work_item_code: str
    description: str
    unit: str
    quantity: float

    labor_cost: float = 0.0
    material_cost: float = 0.0
    equipment_cost: float = 0.0
    overhead_cost: float = 0.0
    profit_cost: float = 0.0

    unit_price: float = 0.0
    total_cost: float = 0.0

    labor_hours: float = 0.0
    labor_rate: float = 0.0

    resources: List[Dict[str, Any]] = field(default_factory=list)
    status: CostStatus = CostStatus.CALCULATED

    def to_dict(self) -> Dict[str, Any]:
        return {
            'work_item_code': self.work_item_code,
            'description': self.description,
            'unit': self.unit,
            'quantity': self.quantity,
            'labor_cost': self.labor_cost,
            'material_cost': self.material_cost,
            'equipment_cost': self.equipment_cost,
            'overhead_cost': self.overhead_cost,
            'profit_cost': self.profit_cost,
            'total_cost': self.total_cost,
            'status': self.status.value
        }


@dataclass
class CostSummary:
    """Summary of cost estimate."""
    total_cost: float
    labor_total: float
    material_total: float
    equipment_total: float
    overhead_total: float
    profit_total: float

    item_count: int
    currency: str
    calculated_at: datetime

    breakdown_by_category: Dict[str, float] = field(default_factory=dict)


class CWICRCostCalculator:
    """Resource-based cost calculator using CWICR methodology."""

    DEFAULT_OVERHEAD_RATE = 0.15  # 15% overhead
    DEFAULT_PROFIT_RATE = 0.10   # 10% profit

    def __init__(self, cwicr_data: pd.DataFrame,
                 overhead_rate: float = None,
                 profit_rate: float = None,
                 currency: str = "USD"):
        """Initialize calculator with CWICR data."""
        self.data = cwicr_data
        self.overhead_rate = overhead_rate or self.DEFAULT_OVERHEAD_RATE
        self.profit_rate = profit_rate or self.DEFAULT_PROFIT_RATE
        self.currency = currency

        # Index data for fast lookup
        self._index_data()

    def _index_data(self):
        """Create index for fast work item lookup."""
        if 'work_item_code' in self.data.columns:
            self._code_index = self.data.set_index('work_item_code')
        else:
            self._code_index = None

    def calculate_item_cost(self, work_item_code: str,
                            quantity: float,
                            price_overrides: Dict[str, float] = None) -> CostBreakdown:
        """Calculate cost for single work item."""

        # Find work item in database
        if self._code_index is not None and work_item_code in self._code_index.index:
            item = self._code_index.loc[work_item_code]
        else:
            # Try partial match
            matches = self.data[
                self.data['work_item_code'].str.contains(work_item_code, case=False, na=False)
            ]
            if matches.empty:
                return CostBreakdown(
                    work_item_code=work_item_code,
                    description="NOT FOUND",
                    unit="",
                    quantity=quantity,
                    status=CostStatus.MISSING_DATA
                )
            item = matches.iloc[0]

        # Get base costs
        labor_unit = float(item.get('labor_cost', 0) or 0)
        material_unit = float(item.get('material_cost', 0) or 0)
        equipment_unit = float(item.get('equipment_cost', 0) or 0)

        # Apply price overrides if provided
        if price_overrides:
            if 'labor_rate' in price_overrides:
                labor_norm = float(item.get('labor_norm', 0) or 0)
                labor_unit = labor_norm * price_overrides['labor_rate']
            if 'material_factor' in price_overrides:
                material_unit *= price_overrides['material_factor']
            if 'equipment_factor' in price_overrides:
                equipment_unit *= price_overrides['equipment_factor']

        # Calculate component costs
        labor_cost = labor_unit * quantity
        material_cost = material_unit * quantity
        equipment_cost = equipment_unit * quantity

        # Direct costs
        direct_cost = labor_cost + material_cost + equipment_cost

        # Overhead and profit
        overhead_cost = direct_cost * self.overhead_rate
        profit_cost = (direct_cost + overhead_cost) * self.profit_rate

        # Total
        total_cost = direct_cost + overhead_cost + profit_cost

        # Unit price
        unit_price = total_cost / quantity if quantity > 0 else 0

        return CostBreakdown(
            work_item_code=work_item_code,
            description=str(item.get('description', '')),
            unit=str(item.get('unit', '')),
            quantity=quantity,
            labor_cost=labor_cost,
            material_cost=material_cost,
            equipment_cost=equipment_cost,
            overhead_cost=overhead_cost,
            profit_cost=profit_cost,
            unit_price=unit_price,
            total_cost=total_cost,
            labor_hours=float(item.get('labor_norm', 0) or 0) * quantity,
            labor_rate=float(item.get('labor_rate', 0) or 0),
            status=CostStatus.CALCULATED
        )

    def calculate_estimate(self, items: List[Dict[str, Any]],
                          group_by_category: bool = True) -> CostSummary:
        """Calculate cost estimate for multiple items."""

        breakdowns = []
        for item in items:
            code = item.get('work_item_code') or item.get('code')
            qty = item.get('quantity', 0)
            overrides = item.get('price_overrides')

            breakdown = self.calculate_item_cost(code, qty, overrides)
            breakdowns.append(breakdown)

        # Aggregate totals
        labor_total = sum(b.labor_cost for b in breakdowns)
        material_total = sum(b.material_cost for b in breakdowns)
        equipment_total = sum(b.equipment_cost for b in breakdowns)
        overhead_total = sum(b.overhead_cost for b in breakdowns)
        profit_total = sum(b.profit_cost for b in breakdowns)
        total_cost = sum(b.total_cost for b in breakdowns)

        # Group by category if requested
        breakdown_by_category = {}
        if group_by_category:
            for b in breakdowns:
                # Extract category from work item code prefix
                category = b.work_item_code.split('-')[0] if '-' in b.work_item_code else 'Other'
                if category not in breakdown_by_category:
                    breakdown_by_category[category] = 0
                breakdown_by_category[category] += b.total_cost

        return CostSummary(
            total_cost=total_cost,
            labor_total=labor_total,
            material_total=material_total,
            equipment_total=equipment_total,
            overhead_total=overhead_total,
            profit_total=profit_total,
            item_count=len(breakdowns),
            currency=self.currency,
            calculated_at=datetime.now(),
            breakdown_by_category=breakdown_by_category
        )

    def calculate_from_qto(self, qto_df: pd.DataFrame,
                          code_column: str = 'work_item_code',
                          quantity_column: str = 'quantity') -> pd.DataFrame:
        """Calculate costs from Quantity Takeoff DataFrame."""

        results = []
        for _, row in qto_df.iterrows():
            code = row[code_column]
            qty = row[quantity_column]

            breakdown = self.calculate_item_cost(code, qty)
            result = breakdown.to_dict()

            # Add original QTO columns
            for col in qto_df.columns:
                if col not in result:
                    result[f'qto_{col}'] = row[col]

            results.append(result)

        return pd.DataFrame(results)

    def apply_regional_factors(self, base_costs: pd.DataFrame,
                               region_factors: Dict[str, float]) -> pd.DataFrame:
        """Apply regional adjustment factors."""
        adjusted = base_costs.copy()

        if 'labor_cost' in adjusted.columns and 'labor' in region_factors:
            adjusted['labor_cost'] *= region_factors['labor']

        if 'material_cost' in adjusted.columns and 'material' in region_factors:
            adjusted['material_cost'] *= region_factors['material']

        if 'equipment_cost' in adjusted.columns and 'equipment' in region_factors:
            adjusted['equipment_cost'] *= region_factors['equipment']

        # Recalculate totals
        adjusted['direct_cost'] = (
            adjusted.get('labor_cost', 0) +
            adjusted.get('material_cost', 0) +
            adjusted.get('equipment_cost', 0)
        )
        adjusted['total_cost'] = adjusted['direct_cost'] * (1 + self.overhead_rate) * (1 + self.profit_rate)

        return adjusted

    def compare_estimates(self, estimate1: CostSummary,
                         estimate2: CostSummary) -> Dict[str, Any]:
        """Compare two cost estimates."""
        return {
            'total_difference': estimate2.total_cost - estimate1.total_cost,
            'total_percent_change': (
                (estimate2.total_cost - estimate1.total_cost) /
                estimate1.total_cost * 100 if estimate1.total_cost > 0 else 0
            ),
            'labor_difference': estimate2.labor_total - estimate1.labor_total,
            'material_difference': estimate2.material_total - estimate1.material_total,
            'equipment_difference': estimate2.equipment_total - estimate1.equipment_total,
            'item_count_difference': estimate2.item_count - estimate1.item_count
        }


class CostReportGenerator:
    """Generate cost reports from calculations."""

    def __init__(self, calculator: CWICRCostCalculator):
        self.calculator = calculator

    def generate_summary_report(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary cost report."""
        summary = self.calculator.calculate_estimate(items)

        return {
            'report_date': datetime.now().isoformat(),
            'currency': summary.currency,
            'total_cost': round(summary.total_cost, 2),
            'breakdown': {
                'labor': round(summary.labor_total, 2),
                'material': round(summary.material_total, 2),
                'equipment': round(summary.equipment_total, 2),
                'overhead': round(summary.overhead_total, 2),
                'profit': round(summary.profit_total, 2)
            },
            'percentages': {
                'labor': round(summary.labor_total / summary.total_cost * 100, 1) if summary.total_cost > 0 else 0,
                'material': round(summary.material_total / summary.total_cost * 100, 1) if summary.total_cost > 0 else 0,
                'equipment': round(summary.equipment_total / summary.total_cost * 100, 1) if summary.total_cost > 0 else 0,
            },
            'item_count': summary.item_count,
            'by_category': summary.breakdown_by_category
        }

    def generate_detailed_report(self, items: List[Dict[str, Any]]) -> pd.DataFrame:
        """Generate detailed line-item report."""
        results = []

        for item in items:
            code = item.get('work_item_code') or item.get('code')
            qty = item.get('quantity', 0)

            breakdown = self.calculator.calculate_item_cost(code, qty)
            results.append(breakdown.to_dict())

        df = pd.DataFrame(results)

        # Add totals row
        totals = df[['labor_cost', 'material_cost', 'equipment_cost',
                     'overhead_cost', 'profit_cost', 'total_cost']].sum()
        totals['description'] = 'TOTAL'
        totals['work_item_code'] = ''

        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

        return df


# Convenience functions
def calculate_cost(cwicr_data: pd.DataFrame,
                   work_item_code: str,
                   quantity: float) -> float:
    """Quick cost calculation."""
    calc = CWICRCostCalculator(cwicr_data)
    breakdown = calc.calculate_item_cost(work_item_code, quantity)
    return breakdown.total_cost


def estimate_project_cost(cwicr_data: pd.DataFrame,
                         items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Quick project cost estimate."""
    calc = CWICRCostCalculator(cwicr_data)
    report = CostReportGenerator(calc)
    return report.generate_summary_report(items)
```

## Quick Start

```python
import pandas as pd
from cwicr_data_loader import CWICRDataLoader

# Load CWICR data
loader = CWICRDataLoader()
cwicr = loader.load("ddc_cwicr_en.parquet")

# Initialize calculator
calc = CWICRCostCalculator(cwicr)

# Calculate single item
breakdown = calc.calculate_item_cost("CONC-001", quantity=150)
print(f"Total: ${breakdown.total_cost:,.2f}")
print(f"  Labor: ${breakdown.labor_cost:,.2f}")
print(f"  Material: ${breakdown.material_cost:,.2f}")
print(f"  Equipment: ${breakdown.equipment_cost:,.2f}")
```

## Common Use Cases

### 1. Project Estimate
```python
items = [
    {'work_item_code': 'CONC-001', 'quantity': 150},
    {'work_item_code': 'EXCV-002', 'quantity': 200},
    {'work_item_code': 'REBAR-003', 'quantity': 15000}  # kg
]

summary = calc.calculate_estimate(items)
print(f"Project Total: ${summary.total_cost:,.2f}")
```

### 2. QTO Integration
```python
# Load BIM quantities
qto = pd.read_excel("quantities.xlsx")

# Calculate costs
costs = calc.calculate_from_qto(qto,
    code_column='work_item',
    quantity_column='quantity'
)
print(costs[['description', 'quantity', 'total_cost']])
```

### 3. Regional Adjustment
```python
# Apply Berlin pricing
berlin_factors = {
    'labor': 1.15,      # 15% higher labor
    'material': 0.95,   # 5% lower materials
    'equipment': 1.0
}

adjusted = calc.apply_regional_factors(costs, berlin_factors)
```

## Resources

- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Construction Cost Estimation
