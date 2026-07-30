# Filter Reference

All filters are passed inside the `--filters` JSON argument of `fetch` and `statistics` commands.

## Filter JSON Structure

Every filter uses this shape:
```json
{
  "filter_name": {
    "values": ["value1", "value2"],
    "negate": false
  }
}
```
Set `"negate": true` to **exclude** entities matching those values.

---

## Filters Requiring Autocomplete (MANDATORY)

These fields MUST be resolved via the `autocomplete` command before use.
Never pass raw user text directly — always use the standardized values returned.

| Filter Field | `--field` Arg | Example Query |
|---|---|---|
| `linkedin_category` | `linkedin_category` | `"software development"`, `"financial services"` |
| `naics_category` | `naics_category` | `"software"`, `"healthcare"` |
| `job_title` | `job_title` | `"Chief Technology Officer"`, `"Account Executive"` |
| `business_intent_topics` | `business_intent_topics` | `"CRM software"`, `"cloud migration"` |
| `company_tech_stack_tech` | `company_tech_stack_tech` | `"Salesforce"`, `"React"`, `"Kubernetes"` |
| `city_region` | `city_region` | `"San Francisco"`, `"New York"` (US cities only) |

**Mutual exclusion**: Never use both `linkedin_category` AND `naics_category` in the same query.

---

## Enum Filters (Use Values Directly — No Autocomplete)

### `company_size` (number of employees)
```
"1-10"  "11-50"  "51-200"  "201-500"  "501-1000"
"1001-5000"  "5001-10000"  "10001+"
```

### `company_revenue` (annual revenue)
```
"0-500K"  "500K-1M"  "1M-5M"  "5M-10M"  "10M-25M"  "25M-75M"
"75M-200M"  "200M-500M"  "500M-1B"  "1B-10B"  "10B-100B"  "100B-1T"
"1T-10T"  "10T+"
```

### `company_age` (years since founding)
```
"0-3"  "3-6"  "6-10"  "10-20"  "20+"
```

### `number_of_locations`
```
"0-1"  "2-5"  "6-20"  "21-50"  "51-100"  "101-1000"  "1001+"
```

### `company_tech_stack_category`
```
"Technology"  "Marketing"  "E-commerce"  "Devops And Development"
"Programming Languages And Frameworks"  "Testing And Qa"
"Platform And Storage"  "Health Tech"  "Business Intelligence And Analytics"
"Operations Management"  "Customer Management"  "Hr"
"Industrial Engineering And Manufacturing"  "Product And Design"
"Sales"  "It Security"  "It Management"  "Finance And Accounting"
"Computer Networks"  "Collaboration"  "Communications"
"Productivity And Operations"  "Healthcare And Life Science"  "Other"
```

### `job_level` (prospects only)
```
"c-suite"  "manager"  "owner"  "senior non-managerial"  "partner"
"freelancer"  "junior"  "director"  "board member"  "founder"
"president"  "senior manager"  "advisor"  "non-managerial"  "vice president"
```

### `job_department` (prospects only)
```
"administration"  "healthcare"  "partnerships"  "c-suite"  "design"
"human resources"  "engineering"  "education"  "strategy"  "product"
"sales"  "r&d"  "retail"  "customer success"  "security"  "public service"
"creative"  "it"  "support"  "marketing"  "trade"  "legal"  "operations"
"real estate"  "procurement"  "data"  "manufacturing"  "logistics"  "finance"
```

---

## Location Filters

### Country codes (ISO Alpha-2)
Use with `company_country_code` or `prospect_country_code`:
```
"US"  "GB"  "DE"  "FR"  "IL"  "CA"  "AU"  "SG"  "IN"  "NL"  ...
```

### Region/State codes (ISO 3166-2)
Use with `company_region_country_code` or `prospect_region_country_code`:
```
"US-CA"  "US-NY"  "US-TX"  "US-FL"  "US-WA"  "IL-TA"  "GB-ENG"  ...
```

**Mutual exclusion**: Never combine `company_country_code` AND `company_region_country_code` (same applies to prospect variants). Use one or the other.

**US cities**: Use `city_region` filter (requires autocomplete) instead of `region_country_code` for city-level targeting.

---

## Boolean / Presence Filters

| Filter | Valid Values | Notes |
|---|---|---|
| `has_website` | `true`, `false`, `null` | null = no filter |
| `is_public_company` | `true`, `false`, `null` | true = NYSE/NASDAQ listed |
| `has_email` | `true`, `null` | prospects only; use `true` when contact emails needed |
| `has_phone_number` | `true`, `null` | prospects only |

---

## Range Filters (Prospects Only)

### `total_experience_months`
```json
{ "total_experience_months": { "gte": 24, "lte": 120 } }
```

### `current_role_months`
```json
{ "current_role_months": { "gte": 6, "lte": 36 } }
```

---

## Event Filter (use within `fetch`)

Filter businesses that have a specific event within a lookback window:
```json
{
  "events": {
    "values": ["new_funding_round", "new_partnership"],
    "last_occurrence": 60,
    "negate": false
  }
}
```
`last_occurrence`: number of days (30–90 only, **cannot exceed 90**).

---

## Title vs. Department/Level

- For **specific titles**: use `job_title` (requires autocomplete)
- For **broad roles**: use `job_level` + `job_department` (no autocomplete)
- **Never** combine `job_title` WITH `job_level` or `job_department` in the same query

---

## Example Filter Objects

### US SaaS companies, 51–500 employees
```json
{
  "linkedin_category": { "values": ["Software Development"] },
  "company_country_code": { "values": ["US"] },
  "company_size": { "values": ["51-200", "201-500"] }
}
```

### CTOs at companies using Salesforce (prospects)
```json
{
  "job_title": { "values": ["Chief Technology Officer"] },
  "company_tech_stack_tech": { "values": ["Salesforce"] }
}
```

### Companies with recent funding in fintech
```json
{
  "linkedin_category": { "values": ["Financial Services"] },
  "events": { "values": ["new_funding_round"], "last_occurrence": 60 }
}
```

### Exclude companies under 10 employees
```json
{
  "company_size": { "values": ["1-10"], "negate": true }
}
```
