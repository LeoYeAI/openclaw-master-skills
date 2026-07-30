# Events Reference

Events let you filter for companies/prospects based on recent real-world triggers, or fetch detailed event data for a result set.

## Business Events (`business-events` command)

### Growth & Expansion
| Event Type | Description |
|---|---|
| `new_funding_round` | New investment round (Seed, Series A/B/C/D/E, PE, etc.) |
| `ipo_announcement` | IPO filed or publicly announced |
| `new_investment` | Company made an investment in another company |
| `new_product` | New product or service launched or announced |
| `new_office` | New office location opened |
| `new_partnership` | New strategic partnership or integration announced |
| `company_award` | Award, recognition, or ranking received |

### Hiring & Workforce Growth
| Event Type | Description |
|---|---|
| `increase_in_engineering_department` | Engineering headcount growing |
| `increase_in_sales_department` | Sales headcount growing |
| `increase_in_marketing_department` | Marketing headcount growing |
| `increase_in_operations_department` | Operations headcount growing |
| `increase_in_customer_service_department` | Customer service headcount growing |
| `increase_in_all_departments` | Company-wide headcount growth |
| `hiring_in_engineering_department` | Active engineering job postings |
| `hiring_in_sales_department` | Active sales job postings |
| `hiring_in_marketing_department` | Active marketing job postings |
| `hiring_in_finance_department` | Active finance job postings |
| `hiring_in_legal_department` | Active legal job postings |
| `hiring_in_operations_department` | Active operations job postings |
| `hiring_in_human_resources_department` | Active HR job postings |
| `hiring_in_creative_department` | Active creative job postings |
| `hiring_in_education_department` | Active education job postings |
| `hiring_in_health_department` | Active healthcare job postings |
| `hiring_in_professional_service_department` | Active professional services job postings |
| `hiring_in_support_department` | Active support job postings |
| `hiring_in_trade_department` | Active trade job postings |
| `hiring_in_unknown_department` | Active hiring, department unclear |
| `employee_joined_company` | Notable senior employee joined the company |

### Contraction & Challenges
| Event Type | Description |
|---|---|
| `decrease_in_engineering_department` | Engineering headcount shrinking |
| `decrease_in_sales_department` | Sales headcount shrinking |
| `decrease_in_marketing_department` | Marketing headcount shrinking |
| `decrease_in_operations_department` | Operations headcount shrinking |
| `decrease_in_customer_service_department` | Customer service headcount shrinking |
| `decrease_in_all_departments` | Company-wide headcount contraction / layoffs |
| `closing_office` | Office location closed |
| `cost_cutting` | Cost reduction initiatives announced |
| `merger_and_acquisitions` | M&A activity (being acquired or acquiring) |
| `lawsuits_and_legal_issues` | Legal proceedings, regulatory actions |
| `outages_and_security_breaches` | Technical incidents, security breaches |

---

## Prospect Events (`prospect-events` command)

| Event Type | Description |
|---|---|
| `prospect_changed_role` | Person promoted or changed roles within the same company |
| `prospect_changed_company` | Person moved to a new company |
| `prospect_job_start_anniversary` | Tenure milestone (1-year, 2-year, etc.) |

---

## Using Events as a Fetch Filter

To filter the search result to only include companies that experienced a specific event, add the `events` filter inside the `--filters` JSON of the `fetch` command:

```json
{
  "events": {
    "values": ["new_funding_round", "hiring_in_engineering_department"],
    "last_occurrence": 60,
    "negate": false
  }
}
```

`last_occurrence`: number of days to look back — **30 to 90 only** (hard API limit). Cannot exceed 90.

---

## Fetching Detailed Event Data

After fetching entities, call `business-events` or `prospect-events` to retrieve the actual event details for each company/prospect in the result table.

```bash
RESULT=$(python ~/.agentsource/bin/agentsource.py business-events \
  --session-id "$SESSION_ID" \
  --table-name "$TABLE_NAME" \
  --event-types "new_funding_round,new_partnership" \
  --since "2025-11-01")
cat "$RESULT"
```

**Sample vs. Export**:
- Sample preview (via `--sample-size 3-5`): Shows up to 3 events per entity
- Full export: ALL events per entity, which can be tens to hundreds per company

**Note**: Event data is returned as a new `events_table_name` — use this table name when calling `export`.

---

## Common Event-Driven Workflows

| Sales Trigger | Events to Use |
|---|---|
| Companies that just raised money | `new_funding_round` |
| Companies actively hiring (expansion signal) | `increase_in_all_departments`, `hiring_in_engineering_department` |
| Companies going through change (potential buyer) | `merger_and_acquisitions`, `new_product`, `new_partnership` |
| Distressed companies (cost-cutting tools) | `cost_cutting`, `decrease_in_all_departments`, `closing_office` |
| New executive hire (champion at new company) | `employee_joined_company` |
| Person who just changed jobs (new budget) | `prospect_changed_company`, `prospect_changed_role` |
