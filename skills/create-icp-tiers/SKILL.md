---
name: create-icp-tiers
description: "Classify companies into Ideal Customer Profile (ICP) tiers based on firmographic data (industry + employee count). Creates a custom property via API and 4 classification workflows in HubSpot UI."
license: MIT
metadata:
  author: tomgranot
  version: "1.0"
  category: segmentation-scoring
---

# Create ICP Tier Property and Classification Workflows

Classify every company in the CRM into an Ideal Customer Profile tier based on firmographic data. Creates a custom dropdown property and 4 automated workflows that continuously classify companies as they enter or change.

## Why This Matters

Without ICP classification, every inbound lead looks the same regardless of whether they come from a large enterprise in a target vertical or a tiny company in an irrelevant industry. Sales and marketing have no systematic way to prioritize outreach, allocate resources, or differentiate campaigns by company fit. ICP Tier is also a major input to the lead scoring model.

## Prerequisites

- Super Admin permissions in HubSpot
- Access to Automation > Workflows (Marketing Hub Professional or higher)
- Data enrichment processes completed (company name, industry, geo values) so company data is as complete as possible
- Company properties **Number of Employees** and **Industry** should be well-populated. Check coverage:
  - Industry: aim for 80%+ populated
  - Employee count: aim for 80%+ populated
  - Companies missing these fields will fall to "Not ICP" (conservative, intentional)

## Interview: Gather Requirements

Before executing, collect the following information from the user:

**Q1: What industries define your ideal customer?**
- Examples: Manufacturing, Professional Services, Logistics, Retail, Education, Media & Entertainment, Hospitality, Real Estate, Agriculture
- Default: No default -- this is highly business-specific and must be provided by the user

**Q2: What employee count ranges define your tiers?**
- Examples: Tier 1: 1,000+, Tier 2: 200-999, Tier 3: 50-199, Not ICP: under 50
- Default: Tier 1: 1,000+, Tier 2: 200-999, Tier 3: 50-199

**Q3: Are there any other firmographic criteria?**
- Examples: Annual revenue thresholds, geographic restrictions (US-only, EMEA, etc.), specific technologies used, funding stage
- Default: None -- industry and employee count are the primary classification axes

## Plan

1. Define your ICP tier criteria (industry verticals + employee count thresholds)
2. Create the ICP Tier custom property via API or UI
3. Build 4 classification workflows (Tier 1, Tier 2, Tier 3, Not ICP)
4. Activate workflows in staggered sequence
5. Verify classification results (after state)

## Before State

### Define Your ICP Tiers

Before building anything, define your criteria framework:

| Tier | Label | Industry Verticals | Employee Threshold |
|------|-------|-------------------|-------------------|
| Tier 1 | Primary ICP | [Your primary verticals, e.g., Manufacturing, Professional Services, Logistics] | [e.g., 1,000+] |
| Tier 2 | Secondary ICP | [Your secondary verticals, e.g., Retail, Education, Media & Entertainment] | [e.g., 200+] |
| Tier 3 | Tertiary ICP | [Your tertiary verticals, e.g., Hospitality, Real Estate, Agriculture] | [e.g., 200+] |
| Not ICP | Not ICP | Everything else | Any |

**Size-based demotion pattern:** Companies in a higher-tier industry but below that tier's employee threshold should be demoted to the next tier down, not classified as "Not ICP". For example:
- A company in a Tier 1 industry with fewer than 1,000 but more than 200 employees -> Tier 2
- A company in a Tier 2 industry with fewer than 200 but more than 50 employees -> Tier 3
- Only companies below 50 employees in any ICP industry, or in non-ICP industries entirely, should be "Not ICP"

This ensures ICP-relevant companies are never lost due to size alone.

### Audit Current State

```python
import os
from hubspot import HubSpot
from dotenv import load_dotenv

load_dotenv()
api_client = HubSpot(access_token=os.getenv("HUBSPOT_API_TOKEN"))

# Check if ICP Tier property already exists
# Use your chosen property name (e.g., "company_segment", "buyer_tier", "icp_tier")
PROPERTY_NAME = "company_segment"
try:
    prop = api_client.crm.properties.core_api.get_by_name(
        object_type="companies", property_name=PROPERTY_NAME
    )
    print(f"ICP Tier property exists: {prop.label}")
except Exception:
    print(f"ICP Tier property '{PROPERTY_NAME}' does not exist yet")

# Check data coverage for classification
for prop_name in ["industry", "numberofemployees"]:
    result = api_client.crm.companies.search_api.do_search(
        public_object_search_request={
            "filterGroups": [{
                "filters": [{
                    "propertyName": prop_name,
                    "operator": "NOT_HAS_PROPERTY"
                }]
            }],
            "limit": 0
        }
    )
    print(f"Companies missing {prop_name}: {result.total}")
```

## Execute

### Step 1: Create the ICP Tier Property

Choose a property name that fits your CRM conventions (e.g., `company_segment`, `buyer_tier`, or `icp_tier`). The name is configurable -- just be consistent across workflows and lists.

**Via API (recommended):**

```python
from hubspot.crm.properties import ModelProperty, PropertyCreate

# Configure your property name here
PROPERTY_NAME = "company_segment"

api_client.crm.properties.core_api.create(
    object_type="companies",
    property_create=PropertyCreate(
        name=PROPERTY_NAME,
        label="ICP Tier",
        type="enumeration",
        field_type="select",
        group_name="companyinformation",
        description="Automated ICP classification based on industry and employee count. Set by workflow - do not edit manually.",
        options=[
            {"label": "Tier 1 - Primary ICP", "value": "tier_1_primary", "displayOrder": 0},
            {"label": "Tier 2 - Secondary ICP", "value": "tier_2_secondary", "displayOrder": 1},
            {"label": "Tier 3 - Tertiary ICP", "value": "tier_3_tertiary", "displayOrder": 2},
            {"label": "Not ICP", "value": "not_icp", "displayOrder": 3},
        ]
    )
)
```

**Via UI:** Settings > Properties > Company properties > Create property > Dropdown select with the four tier options.

### Step 2: Build Classification Workflows

Build 4 company-based workflows in the HubSpot UI. Workflows must use **filter-based triggers** ("When filter criteria is met") with AND logic.

#### Building the Classification Workflows: Three Options

**Option 1: Manual UI Build.** Follow the per-workflow specifications below. This is the most reliable method and gives you full control over every trigger and action.

**Option 2: HubSpot Breeze AI.** Navigate to **Automation > Workflows > Create workflow > "Describe what you want"** and paste the following prompt (repeat for each tier, adjusting the tier name, industries, and thresholds):

```
Create a company-based workflow that triggers when filter criteria is met:
- Number of Employees is greater than or equal to [THRESHOLD]
- AND Industry is any of [LIST YOUR INDUSTRIES]
- AND the custom property "ICP Tier" is unknown

The workflow should set the custom property "ICP Tier" to "[TIER VALUE]".
Enable re-enrollment for all trigger properties.
```

For the Not ICP catch-all workflow, use:
```
Create a company-based workflow that triggers when filter criteria is met:
- Custom property "ICP Tier" is unknown

The workflow should wait a delay (30-90 minutes) to let tiered workflows process first, then set the custom property "ICP Tier" to "Not ICP".
Enable re-enrollment.
```

**CRITICAL WARNING: Breeze trigger limitations.** Breeze creates **event-based triggers (OR logic)** instead of **filter-based triggers (AND logic)**. This is especially dangerous for ICP classification because event-based triggers fire when any single property changes, regardless of other conditions, leading to incorrect tier assignments. After Breeze creates each workflow, you MUST manually verify and rebuild the triggers to use filter-based enrollment with AND logic. Breeze is best used for creating the workflow skeleton (actions, delays) -- the trigger conditions almost always need manual correction.

Additional Breeze limitations:
- Breeze **cannot** create "is unknown" filter conditions reliably -- verify that the "ICP Tier is unknown" guard is correctly configured
- Breeze **cannot** configure re-enrollment rules
- Breeze **cannot** create multiple filter groups with OR between groups and AND within groups (needed for Tier 2 and Tier 3 demotion logic)

**Option 3: Claude Anthropic Chrome Extension.** The Claude Chrome extension lets Claude see and interact with the HubSpot workflow builder UI directly. You can describe each workflow's logic in natural language and Claude will click through the UI to build it. This is often more accurate than Breeze for the ICP workflows because of their complex multi-group filter logic and the critical requirement for AND-based triggers. Build the four workflows one at a time, activating in the staggered sequence described in Step 3.

> **Note on Fast Mode**: If you're using Claude Code's Fast Mode to speed up workflow creation,
> be aware of the billing model: Haiku usage is included in your subscription, but Opus in
> Fast Mode consumes extra credits. For workflow building tasks (which are UI-heavy and may
> require many interactions), consider whether the speed tradeoff is worth the credit cost.

#### Workflow Specifications

#### Workflow 1: Tier 1 (Primary ICP)

- Name: `ICP TIER: Assign Tier 1 - Primary ICP`
- Trigger: When filter criteria is met
  - Number of Employees >= [your threshold, e.g., 1,000]
  - AND Industry is any of [your primary verticals and their variants]
- Re-enrollment: ON (for all trigger properties)
- Action: Set ICP Tier = "Tier 1 - Primary ICP"

**Industry variant tip:** HubSpot has multiple labels for the same vertical. For example, "Manufacturing" might appear as "Manufacturing", "Industrial Automation", "Machinery", "Electrical/Electronic Manufacturing". Include ALL relevant variants in the "is any of" filter. Check what values actually exist in your data.

#### Workflow 2: Tier 2 (Secondary ICP)

- Name: `ICP TIER: Assign Tier 2 - Secondary ICP`
- Trigger: When filter criteria is met

**Filter Group 1 — Secondary industries at threshold:**
- Number of Employees >= [e.g., 200]
- AND Industry is any of [your secondary verticals and variants]
- AND ICP Tier is unknown (prevents overwriting Tier 1)

**Filter Group 2 — Primary industries demoted by size:**
- Number of Employees >= [e.g., 200]
- AND Number of Employees <= [e.g., 999]
- AND Industry is any of [your primary verticals and variants]
- AND ICP Tier is unknown

- Re-enrollment: ON
- Action: Set ICP Tier = "Tier 2 - Secondary ICP"

#### Workflow 3: Tier 3 (Tertiary ICP)

- Name: `ICP TIER: Assign Tier 3 - Tertiary ICP`
- Trigger: When filter criteria is met
- Multiple filter groups for:
  - Tertiary industries at threshold
  - Primary industries demoted by size (below Tier 2 threshold)
  - Secondary industries demoted by size (below Tier 2 threshold)
  - Each group includes AND ICP Tier is unknown
- Re-enrollment: ON
- Action: Set ICP Tier = "Tier 3 - Tertiary ICP"

#### Workflow 4: Not ICP (Catch-All)

- Name: `ICP TIER: Assign Not ICP`
- Trigger: When filter criteria is met
  - ICP Tier is unknown
- Re-enrollment: ON
- Action 1: **Delay (30-90 minutes)** to let tiered workflows process first
- Action 2: Set ICP Tier = "Not ICP"

### Step 3: Activation Sequence

**Activate workflows in staggered sequence to prevent race conditions:**

1. Activate Tier 1 workflow -> enroll existing companies
2. Wait a few minutes (3-10 minutes)
3. Activate Tier 2 workflow -> enroll existing companies
4. Wait a few minutes (3-10 minutes)
5. Activate Tier 3 workflow -> enroll existing companies
6. Wait a few minutes (3-10 minutes)
7. Activate Not ICP workflow -> enroll existing companies

The stagger ensures higher-priority tiers process first. The "ICP Tier is unknown" filter on Tiers 2-4 prevents overwriting, and the delay on Not ICP provides additional buffer.

## After State

Wait 2-4 hours for all workflows to process, then verify.

```python
# Use the same property name you chose in Step 1
PROPERTY_NAME = "company_segment"

# Check coverage
result = api_client.crm.companies.search_api.do_search(
    public_object_search_request={
        "filterGroups": [{
            "filters": [{
                "propertyName": PROPERTY_NAME,
                "operator": "NOT_HAS_PROPERTY"
            }]
        }],
        "limit": 0
    }
)
print(f"Companies without ICP Tier: {result.total} (should be 0)")

# Check distribution
for tier_value in ["tier_1_primary", "tier_2_secondary", "tier_3_tertiary", "not_icp"]:
    result = api_client.crm.companies.search_api.do_search(
        public_object_search_request={
            "filterGroups": [{
                "filters": [{
                    "propertyName": PROPERTY_NAME,
                    "operator": "EQ",
                    "value": tier_value
                }]
            }],
            "limit": 0
        }
    )
    print(f"  {tier_value}: {result.total}")
```

**Verification checklist:**

1. **Total coverage:** 0 companies with ICP Tier unknown
2. **Distribution sanity:** Tier 1 should be the smallest group, Not ICP the largest. If Tier 1 is huge, the employee threshold may be too low or industry list too broad.
3. **Spot-check Tier 1:** Open 5-10 Tier 1 companies. Confirm each has the correct employee count and industry.
4. **Spot-check demotions:** Find Tier 2 companies in primary ICP industries. Confirm they have employee counts below the Tier 1 threshold but above the Tier 2 threshold.
5. **Spot-check Not ICP:** Open 5-10 Not ICP companies. Confirm each has at least one disqualifying factor (low employee count, non-ICP industry, or missing data).
6. **Check workflow errors:** Review each workflow's history for failures.

## Key Technical Learnings

- **CRITICAL: Breeze AI creates wrong trigger types.** Breeze generates event-based triggers (OR logic between groups) instead of filter-based triggers (AND logic within groups). Event-based triggers mean any single property change enrolls the company regardless of other conditions. Always verify triggers manually or build them from scratch.
- **Activation sequence prevents race conditions.** Stagger activation (Tier 1 first, then 2, then 3, then Not ICP) so higher-priority tiers claim companies before lower tiers. The "ICP Tier is unknown" filter provides additional protection.
- **The delay on Not ICP is critical.** Without it, the catch-all workflow would classify companies as Not ICP before tiered workflows have a chance to process them. A delay of 30-90 minutes is typical.
- **Size-based demotion is the key design pattern.** Never classify a company in an ICP industry as "Not ICP" just because it is smaller than the primary threshold. Demote to the next tier instead. This preserves ICP-adjacent companies for secondary targeting.
- **Companies with missing data fall to Not ICP.** This is intentional and conservative. If you later enrich company data (via data provider, manual entry, or Breeze Intelligence), the re-enrollment triggers automatically reclassify those companies.
- **Do not manually edit ICP Tier values.** The workflows manage this property. If you need exceptions, create a separate "ICP Tier Override" property and adjust workflows to respect it.
- **Include industry label variants.** HubSpot has multiple labels for the same vertical (e.g., "Manufacturing" vs "Industrial Automation" vs "Machinery" vs "Electrical/Electronic Manufacturing"). Check what values actually exist in your data and include all relevant variants in your workflow filters.
- **Validate with a script after Breeze creates workflows.** If your HubSpot API token has the `automation-access` scope, you can read workflow definitions via the Workflows API and programmatically verify that triggers match your spec.
