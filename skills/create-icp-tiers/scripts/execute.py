# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
#   "python-dotenv>=1.0",
# ]
# ///
"""
Create ICP Tiers — Execute
Create the ICP Tier company property in HubSpot.

This creates an enumeration (dropdown) property with four tiers:
  - Tier 1 - Primary ICP
  - Tier 2 - Secondary ICP
  - Tier 3 - Tertiary ICP
  - Not ICP

The property is created via API. The classification WORKFLOWS must be
built manually in HubSpot UI because the Workflows API (v4) is
beta/unstable. See the skill instructions for workflow setup guidance.

Generic industry tier examples:
  Tier 1: Manufacturing, Professional Services, Logistics
  Tier 2: Retail, Education, Media & Entertainment
  Tier 3: Hospitality, Real Estate, Agriculture
"""

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

PROPERTY_NAME = "company_segment"
PROPERTY_URL = f"{BASE}/crm/v3/properties/companies/{PROPERTY_NAME}"
CREATE_URL = f"{BASE}/crm/v3/properties/companies"

PROPERTY_PAYLOAD = {
    "name": PROPERTY_NAME,
    "label": "ICP Tier",
    "type": "enumeration",
    "fieldType": "select",
    "groupName": "companyinformation",
    "description": (
        "Automated ICP classification based on industry vertical and "
        "employee count. Tiers are set by workflow — do not edit manually."
    ),
    "options": [
        {
            "label": "Tier 1 - Primary ICP",
            "value": "tier_1_primary_icp",
            "displayOrder": 0,
        },
        {
            "label": "Tier 2 - Secondary ICP",
            "value": "tier_2_secondary_icp",
            "displayOrder": 1,
        },
        {
            "label": "Tier 3 - Tertiary ICP",
            "value": "tier_3_tertiary_icp",
            "displayOrder": 2,
        },
        {
            "label": "Not ICP",
            "value": "not_icp",
            "displayOrder": 3,
        },
    ],
}

# ── Main ─────────────────────────────────────────────────────────

print("=" * 60)
print("EXECUTE: Create ICP Tier Company Property")
print("=" * 60)
print()

# Step 1: Check if property already exists
print(f"Step 1: Checking if '{PROPERTY_NAME}' property already exists...")
resp = requests.get(PROPERTY_URL, headers=HEADERS)

if resp.status_code == 200:
    existing = resp.json()
    print(f"  Property already exists!")
    print(f"    Label:       {existing.get('label')}")
    print(f"    Type:        {existing.get('type')}")
    print(f"    Field type:  {existing.get('fieldType')}")
    print(f"    Group:       {existing.get('groupName')}")
    options = existing.get("options", [])
    print(f"    Options:     {len(options)}")
    for opt in options:
        print(f"      - {opt.get('label')} ({opt.get('value')})")
    print()
    print("Skipping creation — property already exists.")
    print("=" * 60)
else:
    print("  Property does not exist. Proceeding with creation.")
    print()

    # Step 2: Create the property
    print(f"Step 2: Creating '{PROPERTY_NAME}' property...")
    resp = requests.post(CREATE_URL, headers=HEADERS, json=PROPERTY_PAYLOAD)

    if resp.status_code in (200, 201):
        print("  Property created successfully!")
        print()

        # Step 3: Verify
        print("Step 3: Verifying property by reading it back...")
        verify_resp = requests.get(PROPERTY_URL, headers=HEADERS)

        if verify_resp.status_code == 200:
            verified = verify_resp.json()
            print("  Verification successful!")
            print(f"    Name:        {verified.get('name')}")
            print(f"    Label:       {verified.get('label')}")
            print(f"    Type:        {verified.get('type')}")
            print(f"    Field type:  {verified.get('fieldType')}")
            print(f"    Group:       {verified.get('groupName')}")
            print(f"    Description: {verified.get('description')}")
            options = verified.get("options", [])
            print(f"    Options:     {len(options)}")
            for opt in sorted(options, key=lambda o: o.get("displayOrder", 0)):
                print(f"      [{opt.get('displayOrder')}] "
                      f"{opt.get('label')} ({opt.get('value')})")
        else:
            print(f"  WARNING: Verification GET failed ({verify_resp.status_code})")
            print(f"    {verify_resp.text[:300]}")
    else:
        print(f"  FAILED to create property ({resp.status_code})")
        print(f"    {resp.text[:500]}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if resp.status_code in (200, 201):
        print("  ICP Tier property created and verified.")
        print()
        print("  NEXT STEPS — Build classification workflows in HubSpot UI:")
        print()
        print("  The workflows should classify companies into tiers based on")
        print("  industry and employee count. Example tier criteria:")
        print()
        print("  Tier 1 (Primary ICP):")
        print("    Industry: Manufacturing, Professional Services, Logistics")
        print("    Employee count: 1,000+")
        print()
        print("  Tier 2 (Secondary ICP):")
        print("    Industry: Retail, Education, Media & Entertainment")
        print("    Employee count: 200-999 (or Tier 1 industries w/ 200-999)")
        print()
        print("  Tier 3 (Tertiary ICP):")
        print("    Industry: Hospitality, Real Estate, Agriculture")
        print("    Employee count: 50-199 (or higher-tier industries w/ 50-199)")
        print()
        print("  Not ICP:")
        print("    Everything else (non-target industry, <50 employees, or missing data)")
        print()
        print("  Customize these tiers to match YOUR actual ICP definition.")
    else:
        print("  Property creation failed. Check error above.")
    print("=" * 60)
