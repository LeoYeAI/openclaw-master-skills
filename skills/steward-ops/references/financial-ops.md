# Financial Ops & Bill Management

## Purpose
Money touches everything. Bills, subscriptions, invoices, refunds, payments, taxes — they all have deadlines,
and missing any of them has real consequences: late fees, service interruptions, compliance violations, or
damaged vendor relationships. Steward maintains complete financial operational awareness so the principal
never has to think about whether a bill was paid or a subscription is still needed.

---

## Financial Tracking Registry

### The Bill & Payment Tracker
Every recurring financial obligation lives in a structured registry:

```
ID: [unique identifier]
Type: [subscription | utility | insurance | tax | loan | vendor-invoice | one-time]
Payee: [who gets paid]
Amount: [$X.XX] [or "variable" with typical range]
Frequency: [monthly | quarterly | annually | one-time | variable]
Due Date: [day of month, or specific date for non-recurring]
Payment Method: [card ending XXXX | bank account | PayPal | manual check | auto-pay]
Auto-Pay: [yes | no]
Account: [which business/personal account is charged]
Category: [SaaS/tools | hosting/infrastructure | marketing | insurance | tax | utilities | personal | other]
Tax Deductible: [yes | no | partial — business %]
Contract Term: [month-to-month | annual | multi-year | N/A]
Cancellation Notice: [X days required | cancel anytime | N/A]
Last Payment: [date and amount]
Next Payment: [date and expected amount]
Annual Cost: [$X.XX calculated]
Status: [active | paused | pending-cancellation | cancelled | disputed]
Notes: [any special context]
```

### Revenue Tracking
In addition to expenses, track incoming revenue:
```
Source: [Stripe | PayPal | platform payouts | direct deposit | other]
Product/Service: [what generates this revenue]
Expected Amount: [typical or contracted amount]
Frequency: [per sale | monthly recurring | project-based]
Payout Schedule: [when funds arrive after sale/event]
Tax Implications: [sales tax, income tax, platform fees]
```

---

## Subscription Audit Framework

### Monthly Subscription Review
Every month, Steward should produce a subscription health report:

```markdown
## Subscription Audit — [Month Year]

### Active Subscriptions: [count] | Total Monthly Cost: $[X.XX] | Annual: $[X.XX]

### By Category:
| Category | Count | Monthly | Annual |
|----------|-------|---------|--------|
| SaaS/Tools | [X] | $[X] | $[X] |
| Hosting/Infrastructure | [X] | $[X] | $[X] |
| Marketing | [X] | $[X] | $[X] |
| Personal | [X] | $[X] | $[X] |

### Usage Assessment:
✅ High Use (keep): [list with cost]
🟡 Medium Use (review): [list with cost and last used date]
🔴 Low/No Use (cancel candidate): [list with cost and last used date]
❓ Unknown Usage (investigate): [list with cost]

### Cost Changes:
- [Subscription] increased from $[X] to $[Y] effective [date]
- [Subscription] promotional rate ends [date], will increase to $[Y]

### Upcoming Renewals:
- [Subscription] — renews [date] — $[amount] — [decision needed: yes/no]

### Savings Opportunities:
- Cancel [X]: Save $[Y]/month ($[Z]/year)
- Downgrade [X]: Save $[Y]/month
- Switch from monthly to annual billing on [X]: Save $[Y]/year
- Bundle [X] and [Y]: Save $[Z]/month
```

### The Value Assessment
For each subscription, periodically evaluate:
1. **Usage frequency**: When was this last used? How often?
2. **Revenue contribution**: Does this directly contribute to revenue?
3. **Operational necessity**: Would the business stop functioning without this?
4. **Alternative availability**: Is there a free or cheaper alternative?
5. **Feature utilization**: Are we using the full plan, or could we downgrade?

---

## Payment Processing & Monitoring

### Payment Failure Detection
When a payment fails (detected via email, dashboard, or API):
1. Immediately check the payment method — is the card expired? Insufficient funds?
2. Assess the impact — will service be interrupted?
3. Determine the grace period — how long before the failure causes a problem?
4. Escalate with full context and resolution steps

**Payment failure escalation format:**
```
🔴 PAYMENT FAILURE

Service: [what failed]
Amount: $[X.XX]
Error: [reason — card expired, insufficient funds, processing error]
Impact: [what happens if not resolved — service suspended, late fee, etc.]
Grace Period: [X days before consequences]
Fix: [specific steps to resolve — update card, retry payment, contact support]
Link: [where to go to fix it]
```

### Payment Method Health
Track all payment methods and their expiration dates:
```
CARD: [type] ending [last 4]
Expires: [month/year]
Subscriptions Using: [count] — [list]
Alert: [X days before expiration, flag all subscriptions that need updating]
```

When a card approaches expiration:
- 60 days: "Card ending [XXXX] expires in 60 days. [X] subscriptions use this card."
- 30 days: "Card ending [XXXX] expires in 30 days. Update these subscriptions: [list]"
- 14 days: "⚠️ Card ending [XXXX] expires in 14 days. [X] subscriptions will fail."

---

## Invoice Management

### Incoming Invoices
When an invoice is received (via email or platform):
1. Extract: vendor, amount, due date, payment terms, invoice number
2. Check against expected expenses — is this a known vendor and expected amount?
3. Flag anomalies — unexpected vendor, unusual amount, early/late invoice
4. Add to the payment calendar
5. Surface in the daily briefing if action is needed

### Invoice Verification Checklist
Before flagging an invoice for payment:
- [ ] Vendor is recognized and authorized
- [ ] Amount matches expected range or contract terms
- [ ] Services/products were actually received
- [ ] Terms match the agreement (net 30, net 60, etc.)
- [ ] No duplicate invoice (check invoice number against recent payments)
- [ ] Tax calculations are correct

### Outgoing Invoices
If the principal invoices clients:
- Track invoice sent date, amount, and due date
- Monitor for payment receipt
- Flag overdue invoices based on terms
- Suggest follow-up cadence for unpaid invoices:
  - Day after due: Friendly reminder
  - 7 days overdue: Direct follow-up
  - 14 days overdue: Escalation with firmer language
  - 30 days overdue: Final notice with consequences

---

## Tax Operations

### Quarterly Estimated Tax
Track and remind for estimated tax payments:
- Q1: Due April 15
- Q2: Due June 15
- Q3: Due September 15
- Q4: Due January 15

**Prep timeline for each payment:**
- 45 days before: "Quarterly estimated tax due in 45 days. Start gathering income data."
- 30 days before: "Quarterly estimated tax due in 30 days. Calculate estimated amount."
- 14 days before: "Quarterly estimated tax due in 14 days. Prepare payment."
- 7 days before: "⚠️ Quarterly estimated tax due in 7 days."
- Day of: "🔴 Quarterly estimated tax due TODAY."

### Sales Tax (if applicable)
- Track which states/jurisdictions require sales tax collection
- Monitor thresholds for nexus (economic nexus thresholds vary by state)
- Track filing deadlines by jurisdiction
- Flag when approaching thresholds in new jurisdictions

### Year-End Tax Preparation
Starting November:
- Organize receipts and expense records
- Verify 1099 information for contractors
- Review deductible expenses
- Compile revenue by source
- Gather investment/financial documentation
- Flag items needing accountant attention

---

## Receipt & Expense Management

### Receipt Capture Protocol
When receipts arrive (email, digital, or captured):
1. Extract: vendor, amount, date, category, payment method
2. Categorize: business expense, personal, split (with business %)
3. File in the appropriate organizational structure
4. Flag for tax deduction if applicable
5. Match against expected expenses

### Expense Categorization
Standard categories (customize per principal):
- Software & SaaS Tools
- Hosting & Infrastructure
- Marketing & Advertising
- Professional Services (legal, accounting, consulting)
- Office Supplies & Equipment
- Travel & Transportation
- Meals & Entertainment (business)
- Insurance
- Taxes & Licenses
- Education & Training
- Subscriptions & Memberships
- Utilities
- Rent/Workspace
- Miscellaneous Business
- Personal (non-deductible)

### Monthly Expense Summary
```markdown
## Expense Summary — [Month Year]

Total Expenses: $[X,XXX.XX]
vs Last Month: [+/- $X.XX] ([X]%)
vs Budget: [over/under by $X.XX]

### Top Categories:
1. [Category]: $[X.XX] ([X]% of total)
2. [Category]: $[X.XX] ([X]% of total)
3. [Category]: $[X.XX] ([X]% of total)

### Notable Items:
- [Unusual expense or large purchase]
- [Price increase detected]
- [New recurring expense started]

### Tax-Deductible Total: $[X,XXX.XX]
```

---

## Financial Alert Thresholds

Configure alerts for financial anomalies:

| Condition | Alert Level | Action |
|-----------|------------|--------|
| Unexpected charge > $100 | P1 | Immediate verification |
| Subscription price increase | P2 | Review in daily briefing |
| Revenue drop > 20% week-over-week | P1 | Investigate causes |
| Recurring charge missed (auto-pay failed) | P1 | Verify payment method |
| New recurring charge detected | P2 | Verify authorization |
| Account balance below threshold | P1 | Review upcoming payments |
| Refund/chargeback received | P2 | Review details |
| Invoice overdue by 7+ days | P2 | Follow-up needed |
| Tax deadline within 30 days | P2 | Begin preparation |
| Annual subscription renewal within 60 days | P3 | Review for value |

---

## Vendor Payment Intelligence

### Payment Timing Strategy
Optimize when payments are made:
- **Early payment discounts**: Track vendors offering 2/10 net 30 (2% off if paid in 10 days)
- **Cash flow management**: Spread large payments across billing cycles when possible
- **Late fee avoidance**: Always pay before the late fee threshold, never on the due date (buffer for processing)
- **Credit card rewards optimization**: Route payments through the card that maximizes rewards
  (if applicable and within Steward's awareness)

### Vendor Spend Analysis (Quarterly)
```markdown
## Vendor Spend Analysis — [Quarter Year]

### Top 10 Vendors by Spend:
| Vendor | Quarterly Spend | Annual Run Rate | Category | Contract Status |
|--------|----------------|-----------------|----------|----------------|
| [Vendor] | $[X] | $[X] | [cat] | [month-to-month / annual / expiring] |

### Consolidation Opportunities:
- [Vendor A] and [Vendor B] provide similar services. Consolidating could save $[X]/month.

### Price Increases Detected:
- [Vendor]: Increased from $[X] to $[Y] ([Z]% increase)

### Upcoming Contract Renewals:
- [Vendor] — renews [date] — current rate: $[X] — negotiate? [yes/no]
```
