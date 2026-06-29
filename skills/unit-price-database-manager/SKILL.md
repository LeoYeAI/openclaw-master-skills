---
name: "unit-price-database-manager"
description: "Manage construction unit price databases: update prices, track vendors, apply location factors, maintain historical records. Essential for accurate estimating."
---

# Unit Price Database Manager for Construction

## Overview

Manage and maintain construction unit price databases. Update prices from vendors, apply location and time adjustments, track price history, and ensure estimating accuracy.

## Business Case

Accurate unit prices are critical for:
- **Competitive Bids**: Win work with accurate pricing
- **Cost Control**: Avoid budget surprises
- **Vendor Management**: Track supplier pricing
- **Historical Analysis**: Understand price trends

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
import json

@dataclass
class UnitPrice:
    code: str
    description: str
    unit: str
    base_price: Decimal
    labor_cost: Decimal
    material_cost: Decimal
    equipment_cost: Decimal
    effective_date: date
    expiration_date: Optional[date] = None
    source: str = ""
    vendor: str = ""
    location: str = "National Average"
    notes: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class PriceUpdate:
    code: str
    old_price: Decimal
    new_price: Decimal
    change_pct: float
    updated_at: datetime
    updated_by: str
    reason: str

@dataclass
class VendorQuote:
    vendor_name: str
    item_code: str
    quoted_price: Decimal
    quote_date: date
    valid_until: date
    quantity_break: Optional[int] = None
    notes: str = ""

class UnitPriceDatabaseManager:
    """Manage construction unit price databases."""

    # Location adjustment factors
    LOCATION_FACTORS = {
        'New York': 1.32, 'San Francisco': 1.28, 'Los Angeles': 1.15,
        'Chicago': 1.12, 'Boston': 1.18, 'Seattle': 1.08,
        'Denver': 1.02, 'National Average': 1.00,
        'Houston': 0.92, 'Dallas': 0.89, 'Phoenix': 0.93,
        'Atlanta': 0.91, 'Miami': 0.95
    }

    def __init__(self, db_path: str = None):
        self.prices: Dict[str, UnitPrice] = {}
        self.price_history: Dict[str, List[UnitPrice]] = {}
        self.vendor_quotes: Dict[str, List[VendorQuote]] = {}
        self.updates: List[PriceUpdate] = []
        self.db_path = db_path

    def add_price(self, price: UnitPrice) -> str:
        """Add or update a unit price."""
        code = price.code

        # Track history
        if code in self.prices:
            if code not in self.price_history:
                self.price_history[code] = []
            self.price_history[code].append(self.prices[code])

            # Record update
            old_price = self.prices[code].base_price
            if old_price != price.base_price:
                change_pct = float((price.base_price - old_price) / old_price * 100)
                self.updates.append(PriceUpdate(
                    code=code,
                    old_price=old_price,
                    new_price=price.base_price,
                    change_pct=change_pct,
                    updated_at=datetime.now(),
                    updated_by="system",
                    reason="Price update"
                ))

        self.prices[code] = price
        return code

    def get_price(self, code: str, location: str = None,
                  as_of_date: date = None) -> Optional[UnitPrice]:
        """Get unit price with optional location adjustment."""
        if code not in self.prices:
            return None

        price = self.prices[code]

        # Check date validity
        if as_of_date:
            if price.effective_date > as_of_date:
                # Look in history
                if code in self.price_history:
                    for hist_price in reversed(self.price_history[code]):
                        if hist_price.effective_date <= as_of_date:
                            if hist_price.expiration_date is None or hist_price.expiration_date >= as_of_date:
                                price = hist_price
                                break

            if price.expiration_date and price.expiration_date < as_of_date:
                return None

        # Apply location factor
        if location and location != price.location:
            adjusted = UnitPrice(
                code=price.code,
                description=price.description,
                unit=price.unit,
                base_price=self._apply_location_factor(price.base_price, price.location, location),
                labor_cost=self._apply_location_factor(price.labor_cost, price.location, location),
                material_cost=price.material_cost,  # Materials less location-sensitive
                equipment_cost=self._apply_location_factor(price.equipment_cost, price.location, location),
                effective_date=price.effective_date,
                expiration_date=price.expiration_date,
                source=price.source,
                vendor=price.vendor,
                location=location,
                notes=f"Adjusted from {price.location}",
                tags=price.tags
            )
            return adjusted

        return price

    def _apply_location_factor(self, amount: Decimal, from_loc: str, to_loc: str) -> Decimal:
        """Apply location adjustment factor."""
        from_factor = self.LOCATION_FACTORS.get(from_loc, 1.0)
        to_factor = self.LOCATION_FACTORS.get(to_loc, 1.0)
        return Decimal(str(float(amount) * to_factor / from_factor))

    def apply_escalation(self, percentage: float, categories: List[str] = None,
                         effective_date: date = None) -> int:
        """Apply escalation to prices."""
        if effective_date is None:
            effective_date = date.today()

        count = 0
        factor = Decimal(str(1 + percentage / 100))

        for code, price in self.prices.items():
            if categories and not any(tag in price.tags for tag in categories):
                continue

            old_price = price.base_price
            new_price = UnitPrice(
                code=price.code,
                description=price.description,
                unit=price.unit,
                base_price=price.base_price * factor,
                labor_cost=price.labor_cost * factor,
                material_cost=price.material_cost * factor,
                equipment_cost=price.equipment_cost * factor,
                effective_date=effective_date,
                source=f"Escalated {percentage}% from {price.source}",
                vendor=price.vendor,
                location=price.location,
                tags=price.tags
            )

            self.add_price(new_price)
            count += 1

        return count

    def add_vendor_quote(self, quote: VendorQuote):
        """Add a vendor quote."""
        code = quote.item_code
        if code not in self.vendor_quotes:
            self.vendor_quotes[code] = []
        self.vendor_quotes[code].append(quote)

    def get_best_price(self, code: str, quantity: int = 1) -> Optional[Dict]:
        """Get best available price from vendors."""
        if code not in self.vendor_quotes:
            return None

        valid_quotes = []
        today = date.today()

        for quote in self.vendor_quotes[code]:
            if quote.valid_until >= today:
                if quote.quantity_break is None or quantity >= quote.quantity_break:
                    valid_quotes.append(quote)

        if not valid_quotes:
            return None

        best = min(valid_quotes, key=lambda q: q.quoted_price)

        return {
            'vendor': best.vendor_name,
            'price': best.quoted_price,
            'valid_until': best.valid_until,
            'all_quotes': [
                {'vendor': q.vendor_name, 'price': q.quoted_price}
                for q in sorted(valid_quotes, key=lambda x: x.quoted_price)
            ]
        }

    def search_prices(self, query: str = None, category: str = None,
                       min_price: float = None, max_price: float = None) -> List[UnitPrice]:
        """Search prices by various criteria."""
        results = []

        for code, price in self.prices.items():
            # Text search
            if query:
                query_lower = query.lower()
                if (query_lower not in code.lower() and
                    query_lower not in price.description.lower()):
                    continue

            # Category filter
            if category and category not in price.tags:
                continue

            # Price range
            if min_price and float(price.base_price) < min_price:
                continue
            if max_price and float(price.base_price) > max_price:
                continue

            results.append(price)

        return results

    def get_price_history(self, code: str) -> List[Dict]:
        """Get price history for an item."""
        history = []

        if code in self.price_history:
            for price in self.price_history[code]:
                history.append({
                    'date': price.effective_date,
                    'price': float(price.base_price),
                    'source': price.source
                })

        if code in self.prices:
            history.append({
                'date': self.prices[code].effective_date,
                'price': float(self.prices[code].base_price),
                'source': self.prices[code].source
            })

        return sorted(history, key=lambda x: x['date'])

    def analyze_price_trends(self, code: str) -> Dict:
        """Analyze price trends for an item."""
        history = self.get_price_history(code)

        if len(history) < 2:
            return {'trend': 'insufficient_data'}

        prices = [h['price'] for h in history]
        dates = [h['date'] for h in history]

        # Calculate changes
        first_price = prices[0]
        last_price = prices[-1]
        total_change = (last_price - first_price) / first_price * 100

        # Calculate annualized rate
        days = (dates[-1] - dates[0]).days
        years = days / 365.25
        if years > 0:
            annual_rate = ((last_price / first_price) ** (1 / years) - 1) * 100
        else:
            annual_rate = 0

        return {
            'code': code,
            'first_price': first_price,
            'last_price': last_price,
            'total_change_pct': total_change,
            'annual_rate_pct': annual_rate,
            'data_points': len(history),
            'period_years': years,
            'trend': 'increasing' if total_change > 5 else 'decreasing' if total_change < -5 else 'stable'
        }

    def import_from_csv(self, file_path: str) -> int:
        """Import prices from CSV file."""
        df = pd.read_csv(file_path)
        count = 0

        for _, row in df.iterrows():
            price = UnitPrice(
                code=row['code'],
                description=row['description'],
                unit=row['unit'],
                base_price=Decimal(str(row['base_price'])),
                labor_cost=Decimal(str(row.get('labor_cost', 0))),
                material_cost=Decimal(str(row.get('material_cost', 0))),
                equipment_cost=Decimal(str(row.get('equipment_cost', 0))),
                effective_date=date.today() if 'effective_date' not in row else pd.to_datetime(row['effective_date']).date(),
                source=row.get('source', 'CSV Import'),
                tags=row.get('tags', '').split(',') if 'tags' in row else []
            )
            self.add_price(price)
            count += 1

        return count

    def export_to_csv(self, file_path: str, location: str = None) -> int:
        """Export prices to CSV file."""
        data = []

        for code, price in self.prices.items():
            if location:
                price = self.get_price(code, location)

            data.append({
                'code': price.code,
                'description': price.description,
                'unit': price.unit,
                'base_price': float(price.base_price),
                'labor_cost': float(price.labor_cost),
                'material_cost': float(price.material_cost),
                'equipment_cost': float(price.equipment_cost),
                'location': price.location,
                'effective_date': price.effective_date.isoformat(),
                'source': price.source,
                'tags': ','.join(price.tags)
            })

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return len(data)

    def validate_prices(self) -> List[Dict]:
        """Validate prices for issues."""
        issues = []

        for code, price in self.prices.items():
            # Check for expired prices
            if price.expiration_date and price.expiration_date < date.today():
                issues.append({
                    'code': code,
                    'issue': 'expired',
                    'message': f"Price expired on {price.expiration_date}"
                })

            # Check for old prices
            age_days = (date.today() - price.effective_date).days
            if age_days > 365:
                issues.append({
                    'code': code,
                    'issue': 'stale',
                    'message': f"Price is {age_days} days old"
                })

            # Check for zero prices
            if price.base_price <= 0:
                issues.append({
                    'code': code,
                    'issue': 'invalid',
                    'message': "Zero or negative price"
                })

            # Check component breakdown
            total_components = price.labor_cost + price.material_cost + price.equipment_cost
            if total_components > 0 and abs(float(price.base_price - total_components)) > 0.01:
                issues.append({
                    'code': code,
                    'issue': 'mismatch',
                    'message': f"Component costs don't match total: {total_components} vs {price.base_price}"
                })

        return issues

    def generate_report(self) -> str:
        """Generate database status report."""
        lines = ["# Unit Price Database Report", ""]
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Total Items:** {len(self.prices):,}")
        lines.append("")

        # Category breakdown
        categories = {}
        for price in self.prices.values():
            for tag in price.tags:
                categories[tag] = categories.get(tag, 0) + 1

        if categories:
            lines.append("## Items by Category")
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                lines.append(f"- {cat}: {count}")
            lines.append("")

        # Recent updates
        recent_updates = sorted(self.updates, key=lambda x: x.updated_at, reverse=True)[:10]
        if recent_updates:
            lines.append("## Recent Updates")
            for update in recent_updates:
                lines.append(f"- {update.code}: {update.change_pct:+.1f}% on {update.updated_at.strftime('%Y-%m-%d')}")
            lines.append("")

        # Validation issues
        issues = self.validate_prices()
        if issues:
            lines.append("## Validation Issues")
            lines.append(f"Total issues: {len(issues)}")
            for issue in issues[:10]:
                lines.append(f"- {issue['code']}: {issue['message']}")

        return "\n".join(lines)
```

## Quick Start

```python
from decimal import Decimal
from datetime import date

# Initialize manager
manager = UnitPriceDatabaseManager()

# Add unit prices
manager.add_price(UnitPrice(
    code="033000.10",
    description="Cast-in-place concrete, 4000 PSI",
    unit="CY",
    base_price=Decimal("450.00"),
    labor_cost=Decimal("150.00"),
    material_cost=Decimal("250.00"),
    equipment_cost=Decimal("50.00"),
    effective_date=date(2026, 1, 1),
    source="RSMeans 2026",
    tags=["concrete", "structural"]
))

# Get price with location adjustment
price = manager.get_price("033000.10", location="New York")
print(f"NYC price: ${price.base_price}/CY")

# Add vendor quote
manager.add_vendor_quote(VendorQuote(
    vendor_name="ABC Concrete",
    item_code="033000.10",
    quoted_price=Decimal("420.00"),
    quote_date=date.today(),
    valid_until=date(2026, 3, 31)
))

# Get best price
best = manager.get_best_price("033000.10")
print(f"Best price: ${best['price']} from {best['vendor']}")

# Apply escalation
count = manager.apply_escalation(3.5, categories=["concrete"])
print(f"Escalated {count} items by 3.5%")

# Generate report
print(manager.generate_report())
```

## Dependencies

```bash
pip install pandas
```
