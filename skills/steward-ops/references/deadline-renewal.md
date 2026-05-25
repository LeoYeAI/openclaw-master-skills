# Deadline & Renewal Tracking

## Purpose
Deadlines and renewals are the silent killers of small operations. A missed renewal can mean a lost domain,
an expired session can mean lost access to a revenue-generating platform, and a forgotten deadline can mean
legal or financial consequences. Steward maintains an always-current map of every time-sensitive item across
the entire operation — business and personal.

---

## The Deadline Registry

Every deadline and renewal in the system lives in a structured registry. This is the single source of truth.

### Registry Entry Format
```
ID: [unique identifier]
Category: [session | subscription | license | domain | certificate | insurance | tax | legal | contract | custom]
Item: [what this deadline is for]
Platform/Provider: [where this lives]
Account: [which account/email it's associated with]
Current Status: [active | expiring-soon | expired | renewed | cancelled]
Expiration Date: [exact date]
Lead Time Required: [how many days before expiration should we start acting]
Alert Schedule: [when to send reminders — e.g., "30 days, 14 days, 7 days, 3 days, 1 day"]
Renewal Method: [auto-renew | manual-login | manual-payment | requires-approval | requires-reauthorization]
Renewal Cost: [amount, if known]
Renewal URL: [direct link to renewal page]
Last Renewed: [date of last renewal]
Renewal Cycle: [monthly | quarterly | annual | custom-days]
Grace Period: [how many days after expiration before real consequences]
Consequence of Missing: [what happens if this expires — be specific]
Owner: [who is responsible for this renewal]
Notes: [any special instructions or context]
```

---

## Deadline Categories & Tracking Logic

### Platform Session Expirations
These are authentication sessions that expire and require re-authorization. They are particularly dangerous
because they silently disable functionality.

**Tracking requirements:**
- Log the exact authorization date
- Calculate expiration based on known platform limits
- Set alerts starting at 7 days before expiration
- Include re-authorization instructions in every alert

**Common session types and their windows:**
| Platform | Session Type | Typical Duration | Renewal Method |
|----------|-------------|-----------------|----------------|
| KDP (Amazon) | AgentReach auth | ~29 days | Re-authorize via login |
| Reddit | API/OAuth token | ~29 days | Re-authorize via login |
| Etsy | API connection | Varies | Re-authorize + check restrictions |
| Google APIs | OAuth refresh | 7 days (inactive) / 6 months (active) | Auto-refresh if active |
| Stripe | Dashboard session | 30 days | Re-login |
| Social media APIs | OAuth tokens | Platform-specific | Re-authorize |

**Alert cadence for sessions:**
- 7 days before: "KDP session expires in 7 days. Plan re-authorization."
- 3 days before: "KDP session expires in 3 days. Re-authorize today to maintain buffer."
- 1 day before: "⚠️ KDP session expires TOMORROW. Re-authorize now."
- Day of: "🔴 KDP session expires TODAY. Immediate re-authorization required."
- Expired: "🚨 KDP session has EXPIRED. Functionality is disabled until re-authorized."

### Subscription & SaaS Renewals
Track every paid subscription, whether business or personal.

**Tracking requirements:**
- Track billing cycle (monthly/annual)
- Note whether auto-renew is enabled
- Track the payment method on file (last 4 digits, expiration of card)
- Flag subscriptions approaching their card expiration
- Track annual spend per subscription for audit purposes

**Alert cadence for subscriptions:**
- Annual subscriptions: 60 days, 30 days, 14 days, 7 days, 1 day
- Monthly subscriptions: 7 days, 1 day (only if there's a reason to cancel/change)
- Auto-renewing: Alert only if decision needed (cancel? downgrade? upgrade?)
- Manual-pay: Full alert cadence with payment instructions

### Domain, SSL & DNS Renewals
These are critical infrastructure items. Losing a domain can be catastrophic.

**Tracking requirements:**
- Domain registrar and login credentials location
- DNS hosting provider (if different from registrar)
- SSL certificate provider and type (Let's Encrypt auto-renew vs manual)
- Domain expiration date (from WHOIS, not memory)
- Auto-renew status
- Associated email accounts and services

**Alert cadence for domains:**
- 90 days: "Domain [x] renews in 90 days. Verify auto-renew is active."
- 30 days: "Domain [x] renews in 30 days. Confirm payment method is current."
- 14 days: "Domain [x] renews in 14 days."
- 7 days: "⚠️ Domain [x] renews in 7 days. Verify renewal will succeed."
- Day of: "Domain [x] renewal processes today."
- If NOT auto-renewing: Double the alert frequency and start at 120 days.

### Contract & Agreement Deadlines
Track all contracts with external parties.

**Tracking requirements:**
- Contract start and end dates
- Auto-renewal clauses and notice periods
- Cancellation windows (many contracts require 30-60 day notice to cancel)
- Rate change dates
- Performance review dates
- Deliverable deadlines (both ours and theirs)

**Critical contract intelligence:**
- Calculate the "last possible cancellation date" = renewal date minus notice period
- Alert BEFORE the cancellation window closes, not just before renewal
- Track whether the contract has an auto-escalation clause (price increases)

### Tax & Regulatory Deadlines
Non-negotiable deadlines with legal consequences.

**Tracking requirements:**
- Federal, state, and local tax filing dates
- Estimated tax payment dates
- Sales tax filing dates (if applicable)
- Business license renewal dates
- Annual report filing dates
- Industry-specific regulatory deadlines

**Alert cadence for tax/regulatory:**
- 60 days: "Quarterly estimated tax due in 60 days. Begin preparation."
- 30 days: "Quarterly estimated tax due in 30 days. Gather documentation."
- 14 days: "⚠️ Quarterly estimated tax due in 14 days."
- 7 days: "⚠️ Quarterly estimated tax due in 7 days. File this week."
- 3 days: "🔴 Quarterly estimated tax due in 3 days."
- Day of: "🚨 Quarterly estimated tax due TODAY."

### Insurance Renewals
Both business and personal insurance.

**Tracking requirements:**
- Policy type, provider, and policy number
- Premium amount and payment schedule
- Coverage period start and end
- Renewal date and rate change notifications
- Claims history that might affect renewal
- Competing quotes obtained

### License & Permit Tracking
Business licenses, software licenses, professional certifications.

**Tracking requirements:**
- License type and issuing authority
- Expiration date and renewal process
- Continuing education requirements (if professional license)
- Software license keys and seat counts
- License transfer restrictions

---

## The Deadline Dashboard

### Visual Format (for React/HTML dashboards)
Organize deadlines into time horizons:

```
OVERDUE (Red)
[Items past their deadline — immediate attention required]

THIS WEEK (Orange)
[Items due in the next 7 days]

THIS MONTH (Yellow)
[Items due in the next 30 days]

THIS QUARTER (Blue)
[Items due in the next 90 days]

TRACKING (Gray)
[Items monitored but not yet approaching — for awareness only]
```

### Text Format (for briefings)
```markdown
## Deadline Status — [Date]

### 🚨 OVERDUE
- [Item] — was due [date] ([X] days ago) — [consequence] — [action needed]

### 🔴 Due This Week
- [Item] — due [date] ([X] days) — [renewal method] — [cost if applicable]

### 🟡 Due This Month
- [Item] — due [date] — [auto-renew status] — [decision needed: Y/N]

### 🔵 Upcoming (30-90 days)
- [Item] — due [date] — [status]

### ✅ Recently Renewed
- [Item] — renewed [date] — next due [date]
```

---

## Renewal Decision Intelligence

Steward doesn't just track — it helps make renewal decisions:

### Pre-Renewal Audit
Before any significant renewal, Steward should assess:
1. **Usage check**: Is this subscription/service still being used? When was it last accessed?
2. **Value check**: Is this generating value proportional to its cost?
3. **Alternative check**: Are there better/cheaper alternatives available?
4. **Bundle check**: Can this be consolidated with another service?
5. **Timing check**: Is this the best time to renew, or should we time it differently?

### Renewal Recommendation Format
```
RENEWAL DECISION: [Item Name]
Due: [date]
Cost: [amount] / [cycle]
Last 90 Days Usage: [high/medium/low/none]
Annual Cost: [calculated]
Recommendation: [Renew | Cancel | Downgrade | Investigate alternatives | Negotiate]
Reason: [1-2 sentences]
Action Required By: [date — accounting for notice periods]
```

---

## Cross-System Deadline Correlation

Steward connects related deadlines across systems:

- **Payment method expiration → subscription failures**: If a credit card expires next month, flag ALL
  subscriptions that use that card
- **Domain expiration → email disruption**: If a domain expires, flag all email accounts on that domain
- **Platform session → product availability**: If a KDP session expires, flag all KDP-published products
  that won't be manageable
- **Insurance lapse → compliance violation**: If business insurance lapses, flag any contracts that
  require proof of insurance
- **License expiration → feature loss**: If a software license expires, flag workflows that depend on
  that software

---

## Deadline Maintenance Protocols

### Daily Deadline Scan
Every morning, before the daily briefing:
1. Check all items with deadlines in the next 14 days
2. Verify status hasn't changed (auto-renewal might have processed, etc.)
3. Check for new deadlines that appeared overnight (new invoices, new emails)
4. Update the registry with any changes
5. Feed the results into the daily briefing

### Weekly Deadline Audit
Once per week:
1. Review the full registry for accuracy
2. Check for items that might have been missed
3. Verify auto-renewal statuses haven't changed
4. Look for new subscriptions or commitments that need tracking
5. Clean up completed/cancelled items

### Monthly Deadline Review
Once per month:
1. Full audit of all tracked items
2. Cost analysis of all subscriptions and renewals
3. Identify consolidation opportunities
4. Review the alert cadence — is it too aggressive? Too passive?
5. Update any changed renewal processes or URLs

---

## Emergency Deadline Protocols

When a deadline is missed or about to be missed:

### Immediate Actions
1. Assess the actual consequence (not the assumed consequence)
2. Determine if there's a grace period
3. Identify the fastest path to resolution
4. Prepare a clear action plan for the principal
5. Escalate to P0 with all context and recommended actions

### Post-Incident Review
After any missed deadline:
1. Why was it missed? (Alert not sent? Alert ignored? Process failure?)
2. What was the actual impact?
3. How do we prevent recurrence?
4. Does the alert cadence need adjustment?
5. Update the registry with lessons learned
