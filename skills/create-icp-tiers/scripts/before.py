# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
#   "python-dotenv>=1.0",
# ]
# ///
"""
Create ICP Tiers — Before State
Check readiness for ICP Tier classification:
  - How many companies have the required properties (industry, employee count)
  - Whether the ICP Tier property already exists
  - Employee size distribution
  - Industry breakdown for tier planning

Uses generic industry examples: Manufacturing, Professional Services, Logistics,
Retail, Education, Media, etc.

Outputs:
  1. Company property fill rates
  2. Industry + employee count distribution
  3. Whether the ICP tier property exists
  4. CSV audit trail: before_create_icp_tiers.csv
"""

import csv
import os

import requests
from dotenv import load_dotenv

# ── Configuration ────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TOKEN = os.environ["HUBSPOT_ACCESS_TOKEN"]
BASE = "https://api.hubapi.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

SEARCH_URL = f"{BASE}/crm/v3/objects/companies/search"
CSV_FILE = os.path.join(os.path.dirname(__file__), "before_create_icp_tiers.csv")

# Configurable property name — match whatever you chose in execute.py
PROPERTY_NAME = "company_segment"

# ── Helpers ──────────────────────────────────────────────────────

def search_count(filters):
    resp = requests.post(SEARCH_URL, headers=HEADERS, json={
        "filterGroups": [{"filters": filters}],
        "limit": 1,
    })
    resp.raise_for_status()
    return resp.json().get("total", 0)


# ── Main ─────────────────────────────────────────────────────────

print("=" * 60)
print("BEFORE STATE: ICP Tier Property Readiness")
print("=" * 60)
print()

audit_rows = []

# Total companies
has_domain = search_count([
    {"propertyName": "domain", "operator": "HAS_PROPERTY"},
])
no_domain = search_count([
    {"propertyName": "domain", "operator": "NOT_HAS_PROPERTY"},
])
total = has_domain + no_domain
print(f"Total companies: {total} (has domain: {has_domain}, no domain: {no_domain})")
print()

# ── Industry ─────────────────────────────────────────────────────
print("INDUSTRY PROPERTY")
print("-" * 40)

has_industry = search_count([
    {"propertyName": "industry", "operator": "HAS_PROPERTY"},
])
missing_industry = search_count([
    {"propertyName": "industry", "operator": "NOT_HAS_PROPERTY"},
])
print(f"  Has industry:     {has_industry:>6} ({has_industry / total * 100:.1f}%)" if total else "")
print(f"  Missing industry: {missing_industry:>6} ({missing_industry / total * 100:.1f}%)" if total else "")
print()

# Example ICP industry tiers (generic, not company-specific)
print("  Example ICP-relevant industry breakdown:")
icp_industries = {
    "Tier 1 (Primary)": [
        "Manufacturing", "Industrial Automation",
        "Professional Services", "Logistics",
    ],
    "Tier 2 (Secondary)": [
        "Retail", "Education", "Higher Education",
        "Media & Entertainment", "Broadcasting",
    ],
    "Tier 3 (Tertiary)": [
        "Hospitality", "Real Estate", "Agriculture",
        "Construction", "Food & Beverages",
    ],
}

for tier, industries in icp_industries.items():
    print(f"  {tier}:")
    for ind in industries:
        count = search_count([
            {"propertyName": "industry", "operator": "EQ", "value": ind},
        ])
        print(f"    {ind!r}: {count}")
        audit_rows.append({
            "metric": f"industry_{ind}", "value": count, "tier": tier,
        })
print()

# ── Number of Employees ──────────────────────────────────────────
print("NUMBER OF EMPLOYEES PROPERTY")
print("-" * 40)

has_employees = search_count([
    {"propertyName": "numberofemployees", "operator": "HAS_PROPERTY"},
])
missing_employees = search_count([
    {"propertyName": "numberofemployees", "operator": "NOT_HAS_PROPERTY"},
])
print(f"  Has employee count:     {has_employees:>6} ({has_employees / total * 100:.1f}%)" if total else "")
print(f"  Missing employee count: {missing_employees:>6} ({missing_employees / total * 100:.1f}%)" if total else "")
print()

print("  Employee count distribution:")
size_ranges = [
    ("1-99", 1, 99),
    ("100-499", 100, 499),
    ("500-1999", 500, 1999),
    ("2000-9999", 2000, 9999),
    ("10000+", 10000, 999999999),
]
for label, low, high in size_ranges:
    count = search_count([
        {"propertyName": "numberofemployees", "operator": "GTE", "value": str(low)},
        {"propertyName": "numberofemployees", "operator": "LTE", "value": str(high)},
    ])
    print(f"    {label:>10}: {count}")
    audit_rows.append({"metric": f"employees_{label}", "value": count, "tier": ""})
print()

# ── Combined readiness ───────────────────────────────────────────
print("COMBINED READINESS")
print("-" * 40)

has_both = search_count([
    {"propertyName": "industry", "operator": "HAS_PROPERTY"},
    {"propertyName": "numberofemployees", "operator": "HAS_PROPERTY"},
])
missing_both = search_count([
    {"propertyName": "industry", "operator": "NOT_HAS_PROPERTY"},
    {"propertyName": "numberofemployees", "operator": "NOT_HAS_PROPERTY"},
])
has_industry_only = search_count([
    {"propertyName": "industry", "operator": "HAS_PROPERTY"},
    {"propertyName": "numberofemployees", "operator": "NOT_HAS_PROPERTY"},
])
has_employees_only = search_count([
    {"propertyName": "numberofemployees", "operator": "HAS_PROPERTY"},
    {"propertyName": "industry", "operator": "NOT_HAS_PROPERTY"},
])

if total > 0:
    print(f"  Has BOTH industry + employees:    {has_both:>6} ({has_both / total * 100:.1f}%) "
          f"<-- classifiable")
    print(f"  Has industry only (no employees): {has_industry_only:>6} "
          f"({has_industry_only / total * 100:.1f}%)")
    print(f"  Has employees only (no industry): {has_employees_only:>6} "
          f"({has_employees_only / total * 100:.1f}%)")
    print(f"  Missing BOTH:                     {missing_both:>6} "
          f"({missing_both / total * 100:.1f}%)")
print()

# ── ICP Tier property status ─────────────────────────────────────
print("ICP TIER PROPERTY STATUS")
print("-" * 40)

prop_resp = requests.get(
    f"{BASE}/crm/v3/properties/companies/{PROPERTY_NAME}", headers=HEADERS,
)
if prop_resp.status_code == 200:
    prop = prop_resp.json()
    print(f"  ICP Tier property EXISTS: {prop.get('label')} (name: {PROPERTY_NAME})")
    print(f"  Type: {prop.get('type')}, Field type: {prop.get('fieldType')}")
    options = prop.get("options", [])
    if options:
        print(f"  Options: {[o['label'] for o in options]}")
    has_tier = search_count([
        {"propertyName": PROPERTY_NAME, "operator": "HAS_PROPERTY"},
    ])
    print(f"  Already classified: {has_tier}")
else:
    print(f"  ICP Tier property '{PROPERTY_NAME}' does NOT exist yet (this script will create it)")
print()

# ── CSV audit trail ──────────────────────────────────────────────
summary_rows = [
    {"metric": "total_companies", "value": total, "tier": ""},
    {"metric": "has_industry", "value": has_industry, "tier": ""},
    {"metric": "missing_industry", "value": missing_industry, "tier": ""},
    {"metric": "has_employees", "value": has_employees, "tier": ""},
    {"metric": "missing_employees", "value": missing_employees, "tier": ""},
    {"metric": "has_both", "value": has_both, "tier": ""},
    {"metric": "missing_both", "value": missing_both, "tier": ""},
]
all_rows = summary_rows + audit_rows

with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["metric", "value", "tier"])
    writer.writeheader()
    writer.writerows(all_rows)
print(f"Audit trail written to {CSV_FILE}")

# ── Summary ──────────────────────────────────────────────────────
print()
print("=" * 60)
print("BEFORE STATE SUMMARY")
print("=" * 60)
print(f"  Total companies: {total}")
if total > 0:
    print(f"  Ready for ICP classification (has both): {has_both} "
          f"({has_both / total * 100:.1f}%)")
    not_classifiable = has_industry_only + has_employees_only + missing_both
    print(f"  Not classifiable: {not_classifiable} ({not_classifiable / total * 100:.1f}%)")
print()
print("  Enrichment options for missing data:")
print("    1. HubSpot Company Insights (built-in, auto-fills from domain)")
print("    2. Third-party enrichment (ZoomInfo, Apollo, Clearbit)")
print("    3. Manual review for high-value companies")
print("    4. Accept as-is — missing-data companies default to 'Not ICP'")
print("=" * 60)
