---
name: afrexai-invoice-engine
description: Generate, manage, and track professional invoices with payment terms, recurring billing, overdue automation, and financial reporting. Use when creating invoices, tracking payments, managing clients, or reviewing revenue.
---

# Invoice Engine — Complete Invoicing & Accounts Receivable

A zero-dependency agent skill for end-to-end invoicing — from quote to payment to reporting.

## Quick Start

When the user says "create an invoice" or "bill [client]":

1. Check if client exists in memory (see Client Registry below)
2. If new client → run Client Onboarding
3. Generate invoice using the Invoice Builder
4. Present for review → finalize
5. Track in the Invoice Ledger

---

## 1. Client Registry

Maintain a YAML client database in your workspace:

```yaml
# clients.yaml
clients:
  - id: "CLI-001"
    name: "Acme Corp"
    contact: "Jane Smith"
    email: "jane@acme.com"
    address:
      line1: "123 Business Ave"
      line2: "Suite 400"
      city: "New York"
      state: "NY"
      zip: "10001"
      country: "US"
    tax_id: "US-EIN-12-3456789"
    payment_terms: "net-30"       # net-15, net-30, net-45, net-60, due-on-receipt, custom
    preferred_currency: "USD"
    default_tax_rate: 0           # 0 for B2B cross-border, local rate for domestic
    notes: "PO required for invoices > $5,000"
    created: "2026-01-15"
    lifetime_revenue: 12500.00
    invoices_sent: 3
    invoices_paid: 2
    avg_days_to_pay: 22
```

### Client Onboarding Checklist
When adding a new client, collect:
- [ ] Legal entity name (exactly as on their records)
- [ ] Billing contact name + email
- [ ] Billing address (full, with country)
- [ ] Tax ID / VAT number (if applicable)
- [ ] Preferred payment terms
- [ ] Currency preference
- [ ] Any PO or approval requirements
- [ ] Tax-exempt? (if so, get certificate reference)

---

## 2. Invoice Builder

### Invoice Number Format
```
[PREFIX]-[YEAR].[MONTH].[SEQUENCE]
Example: INV-2026.02.001
```

Configurable prefix per business line:
- `INV` = standard invoice
- `PRO` = proforma / quote
- `REC` = recurring invoice
- `CN` = credit note

### Invoice Template

When generating an invoice, structure it as:

```
╔══════════════════════════════════════════════════════════╗
║  [YOUR COMPANY NAME]                                     ║
║  [Address Line 1]                                        ║
║  [City, State ZIP]                                       ║
║  [Country]                                               ║
║  Tax ID: [YOUR TAX ID]                                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  INVOICE [NUMBER]                  Date: [ISSUE DATE]    ║
║                                    Due:  [DUE DATE]      ║
║                                                          ║
║  Bill To:                          Payment Terms:        ║
║  [CLIENT NAME]                     [Net-30 / etc.]       ║
║  [Client Address]                                        ║
║  [City, State ZIP]                 PO Number:            ║
║  Tax ID: [CLIENT TAX ID]          [If applicable]        ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  #  │ Description          │ Qty │ Rate    │ Amount     ║
╠═════╪══════════════════════╪═════╪═════════╪════════════╣
║  1  │ [Service/Product]    │  1  │ $X,XXX  │ $X,XXX.XX ║
║  2  │ [Service/Product]    │  3  │ $XXX    │ $X,XXX.XX ║
║  3  │ [Expense passthrough]│  1  │ $XXX    │ $XXX.XX   ║
╠═════╧══════════════════════╧═════╧═════════╧════════════╣
║                              Subtotal:    $XX,XXX.XX     ║
║                              Discount:    -$X,XXX.XX     ║
║                              Tax (X%):    $X,XXX.XX      ║
║                              ─────────────────────────   ║
║                              TOTAL DUE:   $XX,XXX.XX     ║
╠══════════════════════════════════════════════════════════╣
║  Payment Methods:                                        ║
║  • Bank Transfer: [Bank] | Acct: [XXXX] | Routing: [XX] ║
║  • PayPal: [email]                                       ║
║  • Stripe: [payment link]                                ║
║  • Bitcoin: [address] / Lightning: [LNURL]               ║
║                                                          ║
║  Notes: [Custom message / thank you / late fee notice]   ║
╚══════════════════════════════════════════════════════════╝
```

### Line Item Types
- **Time-based**: Hours × hourly rate (log hours, auto-calculate)
- **Fixed fee**: Project milestones, retainers
- **Quantity-based**: Units × unit price
- **Expense passthrough**: At-cost or with markup %
- **Discount line**: Negative amount (early payment, volume, loyalty)
- **Recurring**: Auto-populated from recurring schedule

### Tax Handling Decision Tree
```
Is client in same country as you?
├── YES → Apply local tax rate
│   ├── Client tax-exempt? → Add exemption reference, 0% tax
│   └── Client NOT exempt → Apply standard rate
└── NO → Usually 0% (reverse charge / export)
    ├── Both in EU? → Reverse charge mechanism (0%, note on invoice)
    ├── US interstate? → Check nexus rules
    └── International → 0% with export reference
```

### Discount & Pricing Framework
- **Early payment**: 2/10 Net 30 (2% discount if paid within 10 days)
- **Volume**: Tiered pricing (1-10 units = $X, 11-50 = $Y, 51+ = $Z)
- **Loyalty**: After 6+ invoices, offer 5% ongoing discount
- **Bundled**: Package multiple services, discount 10-15% vs à la carte
- **Seasonal**: Q4 premium (+10%), Q1 discount (-5%) if applicable

---

## 3. Invoice Lifecycle & Status Tracking

### Status Flow
```
DRAFT → SENT → VIEWED → PARTIALLY_PAID → PAID → CLOSED
                  ↓
              OVERDUE → ESCALATED → WRITTEN_OFF
                  ↓
            DISPUTED → RESOLVED → PAID
```

### Invoice Ledger (YAML)

```yaml
# invoices.yaml
invoices:
  - number: "INV-2026.02.001"
    client_id: "CLI-001"
    status: "sent"
    issue_date: "2026-02-13"
    due_date: "2026-03-15"
    currency: "USD"
    subtotal: 5000.00
    discount: 0
    tax: 0
    total: 5000.00
    amount_paid: 0
    balance_due: 5000.00
    payment_terms: "net-30"
    line_items:
      - description: "AI Integration Consulting — February"
        qty: 20
        rate: 250.00
        amount: 5000.00
    payments: []
    notes: ""
    sent_date: "2026-02-13"
    reminders_sent: 0
    created: "2026-02-13T10:30:00Z"
```

### Payment Recording
When a payment comes in:
```yaml
payments:
  - date: "2026-03-10"
    amount: 5000.00
    method: "bank_transfer"    # bank_transfer, stripe, paypal, btc, cash, check
    reference: "TXN-ABC123"
    notes: "Paid in full"
```

Update: `amount_paid`, `balance_due`, `status` (→ paid if balance = 0, → partially_paid if balance > 0)

---

## 4. Recurring Invoices

### Schedule Configuration
```yaml
recurring:
  - id: "REC-001"
    client_id: "CLI-001"
    description: "Monthly Retainer — AI Ops Support"
    frequency: "monthly"          # weekly, biweekly, monthly, quarterly, annually
    day_of_month: 1               # 1-28 (avoid 29-31 for safety)
    line_items:
      - description: "AI Operations Retainer"
        qty: 1
        rate: 3500.00
    auto_send: true               # false = create as draft
    start_date: "2026-01-01"
    end_date: null                # null = indefinite
    next_invoice: "2026-03-01"
    invoices_generated: 2
    active: true
```

### Recurring Invoice Routine (run on schedule)
1. Check `recurring` entries where `next_invoice <= today` and `active = true`
2. For each: generate invoice from template, assign next number
3. If `auto_send = true` → mark as sent, notify client
4. If `auto_send = false` → save as draft, notify user for review
5. Update `next_invoice` to next occurrence
6. Log in daily memory

---

## 5. Overdue Management & Collections

### Reminder Schedule
| Days After Due | Action | Tone |
|---|---|---|
| +1 day | Friendly reminder email | "Just a gentle reminder..." |
| +7 days | Follow-up with invoice attached | "Following up on..." |
| +14 days | Firm reminder, mention late fee | "This invoice is now 14 days past due..." |
| +30 days | Final notice before escalation | "Final notice — please remit payment..." |
| +45 days | Escalate to human (Kalin/Christina) | Flag for personal outreach |
| +60 days | Consider write-off or collections | Business decision |

### Reminder Templates

**Day +1 (Friendly)**
```
Subject: Friendly reminder — Invoice [NUMBER] due [DATE]

Hi [CONTACT],

Hope all is well! Just a quick reminder that invoice [NUMBER] for [AMOUNT] was due on [DATE].

If you've already sent payment, please disregard this note.

Payment details are on the attached invoice. Let me know if you need anything.

Best,
[YOUR NAME]
```

**Day +14 (Firm)**
```
Subject: Invoice [NUMBER] — 14 days overdue ([AMOUNT])

Hi [CONTACT],

Invoice [NUMBER] for [AMOUNT] is now 14 days past the due date of [DATE].

Per our agreement, a late fee of [X]% may apply to balances outstanding beyond [Y] days.

Could you confirm when we can expect payment? Happy to discuss if there's an issue.

Thanks,
[YOUR NAME]
```

**Day +30 (Final)**
```
Subject: Final notice — Invoice [NUMBER] overdue ([AMOUNT])

Hi [CONTACT],

This is a final reminder that invoice [NUMBER] for [AMOUNT] remains unpaid, now 30 days past the due date.

Please arrange payment within the next 7 business days to avoid further action.

If there's a dispute or issue with this invoice, please let me know immediately so we can resolve it.

Regards,
[YOUR NAME]
```

### Late Fee Calculation
```
Standard: 1.5% per month on overdue balance (18% APR)
Grace period: 5 business days after due date
Compound: Simple interest (not compound)
Cap: 25% of invoice total (or local legal maximum)

Formula: late_fee = balance_due × (monthly_rate / 30) × days_overdue
Example: $5,000 × (0.015 / 30) × 14 = $35.00
```

---

## 6. Financial Reporting

### Revenue Dashboard (generate weekly/monthly)

```
═══ REVENUE SUMMARY — [MONTH YEAR] ═══

Invoiced This Month:      $XX,XXX.XX  ([N] invoices)
Collected This Month:     $XX,XXX.XX  ([N] payments)
Outstanding (not overdue): $XX,XXX.XX  ([N] invoices)
Overdue:                  $XX,XXX.XX  ([N] invoices, avg [X] days late)
Written Off (YTD):        $XX,XXX.XX

Collection Rate:          XX.X%  (collected / invoiced, trailing 90 days)
Avg Days to Pay:          XX days (trailing 90 days)
Avg Invoice Size:         $X,XXX.XX

═══ TOP CLIENTS (by revenue, YTD) ═══
1. [Client] — $XX,XXX  ([N] invoices, avg [X] days to pay)
2. [Client] — $XX,XXX  ([N] invoices, avg [X] days to pay)
3. [Client] — $XX,XXX  ([N] invoices, avg [X] days to pay)

═══ AGING REPORT ═══
Current (not yet due):     $XX,XXX  ([N] invoices)
1-15 days overdue:         $XX,XXX  ([N] invoices)
16-30 days overdue:        $XX,XXX  ([N] invoices)
31-60 days overdue:        $XX,XXX  ([N] invoices)
60+ days overdue:          $XX,XXX  ([N] invoices) ⚠️

═══ MONTHLY TREND ═══
Jan: $XX,XXX ████████████
Feb: $XX,XXX ████████████████
Mar: $XX,XXX ██████████
...

═══ ACTIONS NEEDED ═══
• [N] invoices need reminder emails
• [N] recurring invoices due for generation
• [Client] has disputed INV-XXXX — needs resolution
```

### Key Metrics to Track
- **Collection Rate**: % of invoiced amount actually collected (target: >95%)
- **DSO (Days Sales Outstanding)**: avg days from invoice to payment (target: <30)
- **Overdue Ratio**: overdue balance / total outstanding (target: <10%)
- **Revenue Concentration**: % from top client (flag if >40% — dependency risk)
- **MRR from Recurring**: recurring invoice total / month

---

## 7. Credit Notes & Adjustments

When a refund or correction is needed:

```yaml
credit_note:
  number: "CN-2026.02.001"
  original_invoice: "INV-2026.01.003"
  client_id: "CLI-001"
  reason: "Partial refund — service hours overcharged"
  line_items:
    - description: "Correction: 5 hours overcharged"
      qty: -5
      rate: 250.00
      amount: -1250.00
  total: -1250.00
  issued: "2026-02-13"
```

Apply credit notes against:
1. The original invoice (reduce balance)
2. Future invoices (credit on account)
3. Direct refund (record refund method + reference)

---

## 8. Multi-Currency Support

```yaml
currencies:
  primary: "USD"
  accepted: ["USD", "GBP", "EUR", "BTC"]
  exchange_rates:  # Update weekly or use live rates
    GBP_USD: 1.27
    EUR_USD: 1.08
    BTC_USD: 97500
  conversion_note: "Converted at rate on invoice date. Payment accepted in invoiced currency only."
```

Rules:
- Always invoice in the client's preferred currency
- Record payments in the currency received
- Convert to primary currency for reporting (use rate on payment date)
- Note exchange rate on invoice if cross-currency
- BTC/Lightning: include both sats and fiat equivalent

---

## 9. Quote-to-Invoice Pipeline

### Quote (Proforma) Template
Same as invoice template but:
- Prefix: `PRO-` instead of `INV-`
- Header: "QUOTATION" instead of "INVOICE"
- Add: "Valid until: [DATE]" (typically 30 days)
- Add: "This is not a tax invoice"

### Pipeline Flow
```
QUOTE → ACCEPTED → INVOICE → PAID
  ↓
EXPIRED (auto-expire after validity period)
  ↓
REVISED (new version with changes)
```

When a quote is accepted:
1. Convert to invoice (change prefix, remove validity notice)
2. Assign invoice number
3. Set payment terms based on client profile
4. Send invoice
5. Archive quote as "converted"

---

## 10. Edge Cases & Rules

### Partial Payments
- Record each payment separately with reference
- Update balance_due after each payment
- On final payment → mark PAID
- If partial + overdue → chase remaining balance only

### Disputed Invoices
- Mark status as DISPUTED
- Record dispute reason and date
- Pause reminders during dispute
- Track resolution (adjusted, credit note, or confirmed correct)
- Resume billing after resolution

### Void vs Credit Note
- **Void**: Invoice was sent in error, never should have existed → mark VOIDED, exclude from reports
- **Credit Note**: Services were delivered but need adjustment → issue CN, include in reports

### Tax Invoice Requirements (by region)
- **US**: No strict format, but include EIN if registered
- **UK/EU**: Must include VAT number, VAT amount, "reverse charge" note if applicable
- **Australia**: Must say "Tax Invoice", include ABN, GST amount
- **Canada**: Include GST/HST number, province-specific rules

### Rounding
- Always round line item amounts to 2 decimal places
- Calculate tax on subtotal (not per-line) to avoid penny discrepancies
- Display currency symbol before amount: $1,234.56

### Invoice Numbering
- NEVER reuse or skip numbers (tax audit requirement)
- Sequential within each prefix
- If voided, keep the number, just mark status

---

## 11. Automation Opportunities

Set up cron jobs or heartbeat checks for:
- [ ] Generate recurring invoices on schedule
- [ ] Send overdue reminders per the schedule above
- [ ] Weekly revenue dashboard to owner
- [ ] Monthly aging report
- [ ] Auto-flag clients with >45 days overdue
- [ ] Quarterly review: update exchange rates, review pricing

---

## 12. Export Formats

When the user needs to export:
- **CSV**: For spreadsheet / accounting import
  ```
  invoice_number,client,date,due_date,total,status,amount_paid,balance
  ```
- **JSON**: For API integration or backup
- **Markdown table**: For quick review in chat
- **PDF-ready text**: Formatted text block ready for PDF generation tool

---

## Commands Reference

| Command | Action |
|---|---|
| "Invoice [client] for [amount/description]" | Create new invoice |
| "Quote [client] for [service]" | Create proforma |
| "Show outstanding invoices" | List unpaid invoices |
| "What's overdue?" | Aging report, overdue only |
| "Revenue this month" | Monthly revenue dashboard |
| "Send reminder for [invoice]" | Generate reminder email |
| "Record payment [invoice] [amount]" | Log payment received |
| "Recurring: [client] [amount] [frequency]" | Set up recurring invoice |
| "Credit note for [invoice]" | Issue credit/adjustment |
| "Client report [name]" | Full client payment history |
| "Export invoices [format]" | CSV/JSON/Markdown export |
| "Void [invoice]" | Void an invoice |
| "Update rates" | Refresh exchange rates |
