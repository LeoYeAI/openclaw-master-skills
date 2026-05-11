---
name: revenue-recognition-agent
description: >
  ASC 606 / IFRS 15 revenue recognition analysis and compliance for SaaS, services,
  and multi-element arrangements. Guides the 5-step recognition model, identifies
  performance obligations, determines transaction prices, allocates revenue across
  obligations, and tracks deferred/contract revenue. Produces journal entries,
  deferred revenue schedules, and disclosure checklists for audit-ready financials.
  Use when: recognizing revenue for contracts with customers, reviewing SaaS subscription
  treatment, analyzing multi-element bundles, booking deferred revenue, or preparing
  ASC 606 footnote disclosures. NOT for: tax revenue recognition (different rules),
  government contracts under ASC 808, or lease accounting (use ASC 842 guidance).
version: 1.0.0
author: PrecisionLedger
tags:
  - accounting
  - revenue
  - asc606
  - ifrs15
  - saas
  - compliance
  - deferred-revenue
  - gaap
---

# Revenue Recognition Agent

ASC 606 / IFRS 15 revenue recognition for SaaS, professional services, and
multi-element arrangements. Covers the full 5-step model, deferred revenue
scheduling, journal entries, and audit disclosure checklists.

---

## When to Use This Skill

**Trigger phrases:**
- "How do we recognize this SaaS contract?"
- "Is this deferred revenue or revenue?"
- "Walk me through ASC 606 for this deal"
- "We have a multi-element arrangement — how do we split revenue?"
- "Customer paid upfront for 12 months — when do we book it?"
- "What are our performance obligations?"
- "Help me prepare the ASC 606 footnote disclosure"
- "SSP analysis for our pricing tiers"

**NOT for:**
- Tax revenue recognition — tax timing rules differ significantly from GAAP
- Government contracts under collaborative arrangements (ASC 808)
- Lease revenue — use ASC 842 / IFRS 16
- Insurance contract revenue — use ASC 944 / IFRS 17
- Financial instrument income (interest, dividends) — use ASC 320/ASC 835
- Crypto/token revenue — highly fact-specific, escalate to Irfan

---

## The 5-Step Model (ASC 606 / IFRS 15)

All revenue recognition flows through these five steps:

```
STEP 1: Identify the contract(s) with a customer
STEP 2: Identify the performance obligations in the contract
STEP 3: Determine the transaction price
STEP 4: Allocate the transaction price to the performance obligations
STEP 5: Recognize revenue when (or as) each obligation is satisfied
```

---

## Step-by-Step Guidance

### Step 1: Identify the Contract

A contract exists when ALL of these are met:

```
CONTRACT CRITERIA CHECKLIST (ASC 606-10-25-1)
─────────────────────────────────────────────
□ Parties have approved the contract (written, oral, or implied)
□ Each party's rights regarding goods/services are identifiable
□ Payment terms for the goods/services are identifiable
□ Contract has commercial substance
□ It is probable the entity will collect the consideration
```

**Collection probability assessment:**
- Review customer credit history, payment terms, and industry
- If collection is NOT probable → no revenue until collected
- Variable consideration subject to constraint (Step 3)

**Contract modifications:**
- Distinct new goods/services + standalone selling price → new contract
- Not distinct or not at SSP → modify original contract (prospective or cumulative catch-up)

---

### Step 2: Identify Performance Obligations

A performance obligation is a **promise to transfer a distinct good or service**.

**Distinct test (both criteria must be met):**
```
1. CAPABLE OF BEING DISTINCT: Customer can benefit from 
   the good/service on its own or with readily available resources.

2. DISTINCT WITHIN THE CONTRACT: Promise is separately 
   identifiable from other promises in the contract.
```

**Common SaaS / services obligations:**

| Arrangement Element | Typically Distinct? | Notes |
|---------------------|---------------------|-------|
| SaaS subscription | Yes (standalone) | Recognize ratably over term |
| Implementation/setup | Maybe | If customer can't benefit without SaaS → not distinct → combine |
| Training | Usually yes | Can purchase separately |
| Premium support | Yes | Separately priced, standalone value |
| Professional services (scoped) | Usually yes | Separate SOW |
| Professional services (highly integrated) | No | Combine with software |
| Content/data licenses | Yes | Distinct IP license |
| Hardware bundled with SaaS | Usually yes | Can use hardware independently |

**Series of distinct services:**
- SaaS subscriptions = series of distinct services (each day/month of access)
- Treated as single performance obligation
- Revenue recognized ratably (straight-line) over subscription period

---

### Step 3: Determine the Transaction Price

Transaction price = consideration the entity expects to be entitled to.

**Components to analyze:**

```
Transaction Price Components
─────────────────────────────────────────────
1. FIXED CONSIDERATION
   → Contract price net of discounts

2. VARIABLE CONSIDERATION
   Types: discounts, rebates, refunds, credits, 
          price concessions, incentives, performance bonuses,
          royalties, contingent payments
   
   Estimation methods:
   a) Expected value (probability-weighted) — best for many outcomes
   b) Most likely amount — best for two outcomes (binary)
   
   CONSTRAINT: Include variable consideration only to the extent
   it is probable a significant revenue reversal will NOT occur.

3. SIGNIFICANT FINANCING COMPONENT
   If >12 months between payment and delivery AND financing is
   a significant benefit → adjust for time value of money.
   
   Practical expedient: If contract < 1 year, ignore financing.

4. NON-CASH CONSIDERATION
   Measure at fair value of non-cash consideration received.

5. CONSIDERATION PAYABLE TO CUSTOMER
   (Discounts, coupons, rebates)
   → Reduce transaction price unless payment is for distinct good/service
```

---

### Step 4: Allocate Transaction Price

Allocate based on **Standalone Selling Price (SSP)** of each performance obligation.

**SSP determination methods (in order of preference):**

```
1. OBSERVABLE PRICE
   → Actual price when entity sells the good/service separately.
   → Best evidence. Use when available.

2. ADJUSTED MARKET ASSESSMENT APPROACH
   → Price the market would pay for the good/service.
   → Research competitor pricing, customer willingness to pay.

3. EXPECTED COST PLUS MARGIN APPROACH
   → Forecast costs to satisfy the obligation + appropriate margin.

4. RESIDUAL APPROACH (limited use)
   → SSP = Transaction price - sum of SSPs of other obligations.
   → Only permitted if SSP is highly variable or uncertain.
```

**Allocation example:**

```
Contract: $12,000 annual SaaS deal
Includes: SaaS license + Implementation + Training

Element           SSP       Allocation %   Allocated Price
─────────────────────────────────────────────────────────
SaaS License      $10,000      71.4%          $8,571
Implementation    $2,500       17.9%          $2,143
Training          $1,500       10.7%          $1,286
─────────────────────────────────────────────
Total SSP         $14,000      100%           $12,000

Note: Contract price ($12k) is less than total SSP ($14k) —
the $2,000 discount is allocated proportionally across all obligations.
```

---

### Step 5: Recognize Revenue

**Over time** (straight-line or input/output method) when ANY criterion is met:
```
□ Customer simultaneously receives and consumes the benefits
  (→ SaaS subscriptions, most services)
□ Entity's performance creates or enhances an asset the 
  customer controls (→ customized software for customer)
□ Entity's performance creates no alternative use AND entity
  has right to payment for work completed to date (→ custom dev)
```

**At a point in time** (when control transfers) for all other obligations:
```
Indicators of control transfer:
□ Entity has right to payment
□ Customer has legal title
□ Entity has transferred physical possession
□ Customer has significant risks and rewards
□ Customer has accepted the asset
```

**Common patterns:**

| Obligation Type | Recognition Pattern | Measure |
|----------------|---------------------|---------|
| SaaS subscription | Over time | Straight-line over term |
| Professional services (T&M) | Over time | Hours incurred / total estimated |
| Fixed-fee project | Over time | % complete (input method) |
| Software license (functional IP) | Point in time | License delivery date |
| Software license (symbolic IP) | Over time | Ratably |
| Training (one-time) | Point in time | Date training is delivered |
| Hardware sale | Point in time | Delivery / acceptance |

---

## Deferred Revenue Scheduling

### SaaS Subscription Schedule

For a $12,000 annual contract starting March 1, 2026 (fiscal year = calendar):

```
CONTRACT REVENUE SCHEDULE
─────────────────────────────────────────────────────────────
Contract:    Acme Corp — Annual SaaS License
Period:      March 1, 2026 – February 28, 2027
ARR:         $12,000 | MRR: $1,000
─────────────────────────────────────────────────────────────
Month        Days    Recognized     Cumulative    Deferred
─────────────────────────────────────────────────────────────
Mar 2026     31      $1,000         $1,000        $11,000
Apr 2026     30      $1,000         $2,000        $10,000
May 2026     31      $1,000         $3,000         $9,000
Jun 2026     30      $1,000         $4,000         $8,000
Jul 2026     31      $1,000         $5,000         $7,000
Aug 2026     31      $1,000         $6,000         $6,000
Sep 2026     30      $1,000         $7,000         $5,000
Oct 2026     31      $1,000         $8,000         $4,000
Nov 2026     30      $1,000         $9,000         $3,000
Dec 2026     31      $1,000        $10,000         $2,000
Jan 2027     31      $1,000        $11,000         $1,000
Feb 2027     28      $1,000        $12,000             $0
─────────────────────────────────────────────────────────────
TOTAL                $12,000
```

**Balance sheet classification:**
- Deferred revenue due within 12 months → Current Liability
- Deferred revenue beyond 12 months → Non-Current Liability

### Multi-Element Arrangement Schedule

```python
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional
import math

@dataclass
class PerformanceObligation:
    name: str
    allocated_price: float
    recognition_pattern: str  # "point_in_time" | "over_time_straight_line" | "over_time_pct_complete"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    completion_date: Optional[date] = None  # for point in time
    pct_complete: float = 0.0  # for % complete method (0.0-1.0)

def calculate_recognized_revenue(
    obligation: PerformanceObligation,
    as_of_date: date
) -> float:
    """
    Calculate cumulative revenue recognized for an obligation as of a date.
    
    Examples:
        # SaaS subscription (over time, straight-line)
        sub = PerformanceObligation(
            name="SaaS License",
            allocated_price=8571,
            recognition_pattern="over_time_straight_line",
            start_date=date(2026, 3, 1),
            end_date=date(2027, 2, 28)
        )
        recognized = calculate_recognized_revenue(sub, date(2026, 6, 30))
        # → $2,857 (4 months of 12)
        
        # Training (point in time)
        training = PerformanceObligation(
            name="Training",
            allocated_price=1286,
            recognition_pattern="point_in_time",
            completion_date=date(2026, 3, 15)
        )
        recognized = calculate_recognized_revenue(training, date(2026, 4, 1))
        # → $1,286 (training already delivered)
    """
    if obligation.recognition_pattern == "point_in_time":
        if obligation.completion_date and as_of_date >= obligation.completion_date:
            return obligation.allocated_price
        return 0.0
    
    elif obligation.recognition_pattern == "over_time_straight_line":
        if not obligation.start_date or not obligation.end_date:
            raise ValueError("start_date and end_date required for straight-line")
        
        total_days = (obligation.end_date - obligation.start_date).days
        elapsed_days = min(
            (as_of_date - obligation.start_date).days,
            total_days
        )
        elapsed_days = max(0, elapsed_days)
        return obligation.allocated_price * (elapsed_days / total_days)
    
    elif obligation.recognition_pattern == "over_time_pct_complete":
        return obligation.allocated_price * min(obligation.pct_complete, 1.0)
    
    return 0.0


def deferred_revenue_balance(
    obligations: List[PerformanceObligation],
    invoiced_amount: float,
    as_of_date: date
) -> dict:
    """
    Calculate deferred revenue and recognized revenue balances.
    
    Returns:
        total_recognized, total_deferred, per_obligation breakdown
    """
    results = []
    total_recognized = 0.0
    
    for ob in obligations:
        recognized = calculate_recognized_revenue(ob, as_of_date)
        deferred = ob.allocated_price - recognized
        total_recognized += recognized
        results.append({
            "obligation": ob.name,
            "allocated_price": ob.allocated_price,
            "recognized": round(recognized, 2),
            "deferred": round(deferred, 2),
        })
    
    return {
        "as_of_date": as_of_date.isoformat(),
        "invoiced": invoiced_amount,
        "total_recognized": round(total_recognized, 2),
        "total_deferred": round(invoiced_amount - total_recognized, 2),
        "obligations": results,
    }
```

---

## Journal Entries

### Standard SaaS Subscription

**On invoice / cash receipt (upfront annual):**
```
DR  Cash / Accounts Receivable          $12,000
    CR  Deferred Revenue                    $12,000
(Record contract liability at contract start)
```

**Monthly revenue recognition:**
```
DR  Deferred Revenue                    $1,000
    CR  Revenue — SaaS Subscriptions        $1,000
(Recognize ratably each month over 12-month term)
```

### Multi-Element Arrangement

**Contract signed, invoice sent — $12,000:**
```
DR  Accounts Receivable                 $12,000
    CR  Deferred Revenue — SaaS             $8,571
    CR  Deferred Revenue — Implementation   $2,143
    CR  Deferred Revenue — Training         $1,286
(Allocate to performance obligation buckets at contract inception)
```

**Training delivered (March 15):**
```
DR  Deferred Revenue — Training         $1,286
    CR  Revenue — Professional Services     $1,286
(Recognize at point in time — training delivered)
```

**Implementation complete (March 31):**
```
DR  Deferred Revenue — Implementation   $2,143
    CR  Revenue — Professional Services     $2,143
(Recognize at point in time — implementation accepted)
```

**Monthly SaaS recognition:**
```
DR  Deferred Revenue — SaaS             $714.25
    CR  Revenue — SaaS Subscriptions        $714.25
($8,571 ÷ 12 months = $714.25/month)
```

### Refund Reserve (Variable Consideration)

When variable consideration is constrained:
```
DR  Revenue                             $500
    CR  Refund Liability                    $500
(Constrain estimated refunds — reverse when constraint resolved)
```

---

## Common SaaS Scenarios

### Scenario A: Annual Upfront, No Implementation

**Facts:** $24,000/year, January 1 start, pure SaaS, no other elements.

**Treatment:**
- Single performance obligation: SaaS subscription (series)
- Recognize $2,000/month straight-line
- Deferred revenue = $24,000 at inception, releases monthly

### Scenario B: Multi-Year Deal with Escalating Pricing

**Facts:** 3-year deal, Year 1: $10k, Year 2: $12k, Year 3: $14k. Total: $36k.

**Treatment options:**
1. If pricing reflects SSP each year → recognize at stated amounts per year
2. If pricing includes significant financing → adjust for time value
3. If escalation is NOT commensurate with standalone pricing → level-load:
   - Annual recognized = $36k ÷ 3 = $12k/year (straight-line)

**Apply judgment test:**
- Does Year 1 price reflect discount (material right)? → New performance obligation
- Is price increase > CPI/market rate? → Consider if reflecting SSP

### Scenario C: Free Trial Converts to Paid

**Facts:** 30-day free trial, then $500/month subscription.

**Treatment:**
- Free trial = no consideration exchanged → no revenue during trial
- On conversion: new contract created
- Recognize $500/month from conversion date forward
- No catch-up for trial period

### Scenario D: Customer Success Bonus

**Facts:** $100k implementation contract + $20k bonus if customer hits adoption KPI.

**Treatment:**
- Fixed: $100k
- Variable: $20k bonus (constrain if reversal probable)
- If unlikely to be reversed: include $20k in transaction price from day 1
- If uncertain: exclude until adoption KPI confirmed
- Recognize over implementation timeline using % complete

### Scenario E: Contract Modification (Upgrade)

**Facts:** Original: $1,000/month. Month 6, customer upgrades to $1,500/month for remainder (6 months left) at standalone pricing.

**Treatment (new contract method):**
- Additional services are distinct and at SSP → treat as new contract
- Original contract continues at $1,000/month through month 12
- New contract: $1,500/month starting month 7

**Treatment (prospective modification):**
- If additional services NOT at SSP → prospective adjustment
- Remaining consideration: original deferred + upgrade amount
- Recognize over remaining term

---

## Disclosure Checklist (ASC 606)

Required footnote disclosures for annual financial statements:

```
ASC 606 DISCLOSURE CHECKLIST
─────────────────────────────────────────────
DISAGGREGATION OF REVENUE (ASC 606-10-50-5)
□ Revenue by product/service line
□ Revenue by geography (if material)
□ Revenue by customer type (enterprise vs. SMB)
□ Revenue by recognition timing (point in time vs. over time)

CONTRACT BALANCES (ASC 606-10-50-8)
□ Opening and closing balances of:
  - Receivables
  - Contract assets (unbilled revenue)
  - Contract liabilities (deferred revenue)
□ Revenue recognized from prior-period contract liabilities
□ Revenue recognized from contract assets

PERFORMANCE OBLIGATIONS (ASC 606-10-50-12)
□ Description of promises and when satisfied
□ Significant payment terms
□ Nature of goods/services transferred
□ Obligations for returns, refunds, warranties

TRANSACTION PRICE ALLOCATION (ASC 606-10-50-17)
□ Aggregate amount allocated to remaining unsatisfied obligations
□ When entity expects to recognize this amount (quantitative or qualitative)
□ Practical expedients applied (if any):
  - Portfolio approach
  - Practical expedient for contracts ≤1 year
  - Sales-based/usage-based royalty exemption

SIGNIFICANT JUDGMENTS (ASC 606-10-50-17)
□ Methods used to recognize revenue over time
□ Methods to determine SSP
□ Variable consideration estimation approach
□ Significant constraints applied
```

---

## Common Mistakes & Red Flags

```
RED FLAG: Booking gross vs. net incorrectly
─────────────────────────────────────────────
Agent vs. Principal analysis:
- Principal: Controls good/service before transfer → GROSS revenue
- Agent: Arranges for another entity → NET (commission only)
Key question: Who bears inventory/credit risk?

RED FLAG: Revenue pulled forward on renewal
─────────────────────────────────────────────
Auto-renewals are new contracts, not continuations.
Do not accelerate deferred revenue into earlier periods.

RED FLAG: Implementation fees recognized at go-live
─────────────────────────────────────────────────────
If implementation is NOT distinct (bundled with SaaS):
→ Allocate to SaaS obligation, recognize over service term.
→ NOT at the go-live date.

RED FLAG: Gross-up for non-refundable activation fees
──────────────────────────────────────────────────────
One-time upfront fees (activation, setup) with no stand-alone value:
→ Defer and recognize over expected customer relationship.
→ NOT as immediate revenue at contract start.

RED FLAG: Variable consideration not constrained
─────────────────────────────────────────────────
If usage-based or contingent fees are included:
→ Only include if highly probable no significant reversal.
→ Reassess each reporting period.
```

---

## Quick Reference: Recognition Cheat Sheet

```
WHAT IS IT?                         HOW TO RECOGNIZE
────────────────────────────────────────────────────────────
Monthly SaaS subscription           Ratably over term (monthly)
Annual SaaS (upfront)               Ratably monthly; defer upfront
Multi-year SaaS (flat pricing)      Ratably over total term
Multi-year SaaS (escalating)        At stated amounts if = SSP
Implementation (not distinct)       Ratably over SaaS term
Implementation (distinct)           % complete (input method)
Training                            At delivery (point in time)
Software license (functional IP)    At delivery (point in time)
Software license (symbolic IP)      Ratably over license term
T&M professional services           As hours/costs incurred
Fixed-fee project                   % complete
Usage/consumption fees              As used/consumed
Minimum guarantees + overages       Guarantee ratably; overage as earned
Refundable deposits                 Liability until non-refundable
Non-refundable setup fees           Defer over customer relationship
```

---

## Integration Points

- **`startup-financial-model`** — Feed recognized revenue into P&L projections and MRR models
- **`qbo-automation`** — Sync deferred revenue schedules with QuickBooks chart of accounts
- **`kpi-alert-system`** — Alert when deferred revenue balance drops unexpectedly
- **`crypto-tax-agent`** — For token/crypto revenue requiring separate tax treatment
- **`cap-table-manager`** — Coordinate when equity-linked consideration is part of a contract

---

## References

- ASC 606: Revenue from Contracts with Customers (FASB)
- IFRS 15: Revenue from Contracts with Customers (IASB)
- AICPA Software Revenue Recognition Guide (ASC 606 for SaaS)
- Big 4 industry guides: Deloitte "Revenue from Contracts with Customers," PwC "Revenue"
