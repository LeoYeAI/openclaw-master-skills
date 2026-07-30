# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
#   "python-dotenv>=1.0",
# ]
# ///
"""
Create ICP Tiers — After State
Verify ICP Tier classification results after workflows have processed.

Checks:
  1. Total coverage (how many companies have ICP Tier set)
  2. Distribution across tiers
  3. Spot-check Tier 1 companies (industry + employee count)
  4. Spot-check Not ICP companies (disqualifying factors)
  5. Enrichment progress (industry + employee fill rates)
  6. CSV audit trail: after_create_icp_tiers.csv
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
CSV_FILE = os.path.join(os.path.dirname(__file__), "after_create_icp_tiers.csv")

# Configurable property name — match whatever you chose in execute.py
PROPERTY_NAME = "company_segment"

# Load before-state baseline
BEFORE_CSV = os.path.join(os.path.dirname(__file__), "before_create_icp_tiers.csv")
before_data = {}
if os.path.exists(BEFORE_CSV):
    with open(BEFORE_CSV) as f:
        for row in csv.DictReader(f):
            before_data[row["metric"]] = int(row["value"])

# ── Helpers ──────────────────────────────────────────────────────

def search_count(filters):
    resp = requests.post(SEARCH_URL, headers=HEADERS, json={
        "filterGroups": [{"filters": filters}],
        "limit": 1,
    })
    resp.raise_for_status()
    return resp.json().get("total", 0)


def search_sample(filters, properties, limit=10):
    resp = requests.post(SEARCH_URL, headers=HEADERS, json={
        "filterGroups": [{"filters": filters}],
        "properties": properties,
        "limit": limit,
    })
    resp.raise_for_status()
    return resp.json().get("results", [])


# ── Main ─────────────────────────────────────────────────────────

print("=" * 70)
print("AFTER STATE: ICP Tier Classification Verification")
print("=" * 70)
print()

# Total companies
has_domain = search_count([
    {"propertyName": "domain", "operator": "HAS_PROPERTY"},
])
no_domain = search_count([
    {"propertyName": "domain", "operator": "NOT_HAS_PROPERTY"},
])
total = has_domain + no_domain
print(f"Total companies: {total}")
print()

audit_rows = []

# =====================================================
# 1. TOTAL COVERAGE
# =====================================================
print("1. ICP TIER COVERAGE")
print("-" * 50)

has_tier = search_count([
    {"propertyName": PROPERTY_NAME, "operator": "HAS_PROPERTY"},
])
missing_tier = search_count([
    {"propertyName": PROPERTY_NAME, "operator": "NOT_HAS_PROPERTY"},
])

if total > 0:
    print(f"  ICP Tier set:     {has_tier:>6} ({has_tier / total * 100:.1f}%)")
    print(f"  ICP Tier missing: {missing_tier:>6} ({missing_tier / total * 100:.1f}%)")
if missing_tier == 0:
    print("  100% coverage achieved!")
elif missing_tier < 100:
    print("  Nearly complete — remaining companies may still be processing")
else:
    print("  Significant gap — workflows may still be running")
print()

# =====================================================
# 2. DISTRIBUTION ACROSS TIERS
# =====================================================
print("2. TIER DISTRIBUTION")
print("-" * 50)

tier_values = [
    ("Tier 1 - Primary ICP", "tier_1_primary_icp"),
    ("Tier 2 - Secondary ICP", "tier_2_secondary_icp"),
    ("Tier 3 - Tertiary ICP", "tier_3_tertiary_icp"),
    ("Not ICP", "not_icp"),
]

tier_counts = {}
for label, value in tier_values:
    count = search_count([
        {"propertyName": PROPERTY_NAME, "operator": "EQ", "value": value},
    ])
    tier_counts[label] = count
    pct = count / total * 100 if total > 0 else 0
    print(f"  {label:<30} {count:>6} ({pct:>5.1f}%)")
    audit_rows.append({"metric": f"tier_{value}", "value": count})

classified_total = sum(tier_counts.values())
print(f"  {'---':─<45}")
print(f"  {'Classified total':<30} {classified_total:>6}")
print(f"  {'Unclassified':<30} {total - classified_total:>6}")
print()

# =====================================================
# 3. SPOT-CHECK TIER 1
# =====================================================
print("3. SPOT-CHECK: Tier 1 Companies")
print("-" * 50)

tier1_sample = search_sample(
    [{"propertyName": PROPERTY_NAME, "operator": "EQ", "value": "tier_1_primary_icp"}],
    ["name", "industry", "numberofemployees", "domain"],
    limit=10,
)

if tier1_sample:
    for c in tier1_sample:
        p = c.get("properties", {})
        name = p.get("name", "N/A")
        industry = p.get("industry", "N/A")
        employees = p.get("numberofemployees", "N/A")
        print(f"  {name[:35]:<35} | {industry:<30} | {employees:>6} emp")
else:
    print("  No Tier 1 companies found — workflows may still be processing")
print()

# =====================================================
# 4. SPOT-CHECK NOT ICP
# =====================================================
print("4. SPOT-CHECK: Not ICP Companies")
print("-" * 50)

not_icp_sample = search_sample(
    [{"propertyName": PROPERTY_NAME, "operator": "EQ", "value": "not_icp"}],
    ["name", "industry", "numberofemployees", "domain"],
    limit=10,
)

if not_icp_sample:
    for c in not_icp_sample:
        p = c.get("properties", {})
        name = p.get("name", "N/A")
        industry = p.get("industry", "")
        employees = p.get("numberofemployees", "")
        reasons = []
        if not industry:
            reasons.append("no industry")
        if not employees:
            reasons.append("no employee count")
        elif int(employees) < 50:
            reasons.append(f"<50 employees ({employees})")
        if not reasons:
            reasons.append("check workflow criteria")
        print(f"  {name[:35]:<35} | Reason: {', '.join(reasons)}")
else:
    print("  No Not ICP companies found — workflows may still be processing")
print()

# =====================================================
# 5. ENRICHMENT PROGRESS
# =====================================================
print("5. ENRICHMENT PROGRESS (industry + employee fill rates)")
print("-" * 50)

has_industry = search_count([
    {"propertyName": "industry", "operator": "HAS_PROPERTY"},
])
has_employees = search_count([
    {"propertyName": "numberofemployees", "operator": "HAS_PROPERTY"},
])
has_both = search_count([
    {"propertyName": "industry", "operator": "HAS_PROPERTY"},
    {"propertyName": "numberofemployees", "operator": "HAS_PROPERTY"},
])

if total > 0:
    print(f"  Industry fill rate:        {has_industry:>6} / {total} "
          f"({has_industry / total * 100:.1f}%)")
    print(f"  Employee count fill rate:  {has_employees:>6} / {total} "
          f"({has_employees / total * 100:.1f}%)")
    print(f"  Both filled:               {has_both:>6} / {total} "
          f"({has_both / total * 100:.1f}%)")

# Compare to before state
if before_data:
    print()
    print("  Delta from before state:")
    for metric, label in [
        ("has_industry", "Industry"),
        ("has_employees", "Employees"),
        ("has_both", "Both"),
    ]:
        current = {"has_industry": has_industry, "has_employees": has_employees,
                    "has_both": has_both}[metric]
        before_val = before_data.get(metric, 0)
        delta = current - before_val
        print(f"    {label}: {'+' if delta >= 0 else ''}{delta}")
print()

# ── CSV audit trail ──────────────────────────────────────────────
audit_rows.extend([
    {"metric": "total_companies", "value": total},
    {"metric": "has_tier", "value": has_tier},
    {"metric": "missing_tier", "value": missing_tier},
    {"metric": "has_industry", "value": has_industry},
    {"metric": "has_employees", "value": has_employees},
    {"metric": "has_both", "value": has_both},
])

with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["metric", "value"])
    writer.writeheader()
    writer.writerows(audit_rows)
print(f"Audit trail written to {CSV_FILE}")

# ── Summary ──────────────────────────────────────────────────────
print()
print("=" * 70)
print("AFTER STATE SUMMARY")
print("=" * 70)
print(f"  Total companies:          {total}")
if total > 0:
    print(f"  ICP Tier classified:      {has_tier} ({has_tier / total * 100:.1f}%)")
    print(f"  ICP Tier unclassified:    {missing_tier} ({missing_tier / total * 100:.1f}%)")
print()
for label, count in tier_counts.items():
    print(f"  {label:<30} {count:>6}")
print()
if missing_tier == 0:
    print("  COMPLETE — 100% ICP Tier coverage achieved")
elif missing_tier < 100:
    print("  NEARLY COMPLETE — small number still unclassified")
else:
    print("  IN PROGRESS — workflows may still be processing, re-run later")
print()
print("  As enrichment fills in more industry/employee data,")
print("  workflow re-enrollment will auto-reclassify companies.")
print("=" * 70)
