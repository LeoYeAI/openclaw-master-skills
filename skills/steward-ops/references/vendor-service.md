# Vendor & Service Management

## Purpose
Every external service provider, tool vendor, and contractor is a dependency in the operation.
Steward tracks every vendor relationship — what they provide, what they cost, when contracts renew,
how to contact them, and whether they're still the best option.

---

## Vendor Registry

### Vendor Profile Format
```
VENDOR: [Company/Provider Name]
Service: [What they provide]
Category: [SaaS | Infrastructure | Professional Services | Supplies | Utilities | Other]
Primary Contact: [Name, email, phone]
Support Contact: [Email, phone, ticket URL]
Escalation Contact: [For urgent issues]
Account ID: [Our account/customer number]
Account Email: [Email associated with this vendor]

CONTRACT:
  Type: [Month-to-month | Annual | Multi-year | Pay-as-you-go]
  Start Date: [when the relationship began]
  Current Term: [start — end of current term]
  Renewal Date: [when it auto-renews or must be manually renewed]
  Auto-Renew: [yes | no]
  Notice Period: [days required to cancel or change before renewal]
  Last Cancel Date: [last date to cancel before next renewal — calculated]
  Price: [$X / period]
  Price Lock: [locked until date | subject to increase]
  Payment Method: [card ending XXXX | invoice | bank transfer]

PERFORMANCE:
  SLA: [what they guarantee — uptime, response time, etc.]
  Actual Performance: [how they're actually performing]
  Last Issue: [date and description of last problem]
  Issue History: [count of issues in past 12 months]
  Satisfaction: [high | medium | low]

DEPENDENCIES:
  What Depends On This: [our products, services, or processes that use this vendor]
  Alternatives: [known alternatives if we needed to switch]
  Switch Difficulty: [easy | moderate | hard — how painful would migration be]
  Switch Cost: [estimated time and money to switch]

NOTES: [any special context, history, or relationship notes]
```

---

## Vendor Lifecycle Management

### Vendor Onboarding Checklist
When starting with a new vendor:
- [ ] Contract/terms reviewed and agreed
- [ ] Account created with appropriate email
- [ ] Payment method configured
- [ ] Auto-renewal preferences set
- [ ] Cancellation terms noted in registry
- [ ] Support contact information documented
- [ ] SLA or service level expectations documented
- [ ] Integration with existing systems verified
- [ ] Vendor added to the tracking registry
- [ ] First billing cycle verified correct

### Vendor Review Cadence
- **Monthly**: Check billing for unexpected changes
- **Quarterly**: Review usage vs cost, performance vs SLA
- **Annually**: Full vendor audit — still the best option?

### Vendor Offboarding Checklist
When ending a vendor relationship:
- [ ] Cancellation notice sent within required timeframe
- [ ] Cancellation confirmation received
- [ ] Data exported/migrated (if applicable)
- [ ] Alternative service activated (if needed)
- [ ] Payment method removed
- [ ] Auto-renew confirmed OFF
- [ ] Account access revoked (if shared)
- [ ] Registry updated with cancellation date and reason
- [ ] Verify no remaining charges after cancellation

---

## Vendor Cost Optimization

### Annual Vendor Spend Review
```markdown
## Vendor Spend Review — [Year]

### Total Vendor Spend: $[X,XXX.XX]

### Top Vendors by Spend:
| Vendor | Annual Spend | Category | Necessity | Alternative Available |
|--------|-------------|----------|-----------|---------------------|
| [Vendor] | $[X] | [cat] | [critical/important/nice-to-have] | [yes/no] |

### Cost Reduction Opportunities:
1. **Switch [Vendor A] to [Alternative]**: Save $[X]/year — Effort: [low/med/high]
2. **Downgrade [Vendor B]**: Save $[X]/year — Risk: [none/low/medium]
3. **Negotiate [Vendor C] renewal**: Target $[X] discount based on [loyalty/volume/competitive quote]
4. **Eliminate [Vendor D]**: Save $[X]/year — No longer needed because [reason]

### Price Increases This Year:
- [Vendor]: $[old] → $[new] ([X]% increase)
- [Vendor]: $[old] → $[new] ([X]% increase)
Total impact: $[X]/year increase
```

### Negotiation Timing
Steward tracks the optimal negotiation windows:
- **30-60 days before renewal**: Start exploring alternatives and gathering competitive quotes
- **14-30 days before renewal**: Initiate negotiation with current vendor
- **7 days before renewal**: Final decision — renew, switch, or cancel

### Negotiation Intel Package
Before any vendor negotiation, Steward prepares:
```
NEGOTIATION BRIEF: [Vendor Name]

Current Terms: $[X] / [period] for [service description]
Our History: Customer since [date], [X] months/years, $[total spend] lifetime
Our Usage: [usage metrics that support our case]
Market Rate: [what competitors charge for similar service]
Competitive Quotes: [if obtained]
Our Leverage: [why they should give us a better deal]
Our BATNA: [best alternative if negotiation fails]
Target: $[X] / [period] ([X]% reduction)
Acceptable: $[X] / [period] ([X]% reduction minimum)
Walk-Away: $[X] / [period] — switch to [alternative] if above this]
```

---

## Vendor Risk Management

### Single Points of Failure
Identify vendors where no backup exists:
```
⚠️ SINGLE POINTS OF FAILURE

| Vendor | Service | If They Fail | Backup Plan |
|--------|---------|-------------|-------------|
| [Vendor] | [service] | [impact] | [None ❌ / Plan documented ✅] |
```

### Vendor Health Monitoring
Watch for signs a vendor may be struggling:
- Slow support response times (getting worse)
- Service quality declining
- Frequent outages or errors
- Price increases without feature improvements
- Key personnel leaving (for small vendors)
- Acquisition rumors (service may change)
- Product stagnation (no updates or improvements)

### Vendor Incident Tracking
When a vendor causes a problem:
```
VENDOR INCIDENT: [Vendor Name] — [Date]
Issue: [What happened]
Impact: [How it affected our operations]
Duration: [How long the issue lasted]
Resolution: [How it was fixed]
Root Cause: [Why it happened, if known]
Recurrence Risk: [low/medium/high]
Action Taken: [What we did — complaint filed, credit requested, etc.]
Follow-Up: [Any ongoing monitoring or pending items]
```

---

## Service Level Tracking

### SLA Monitoring
For vendors with SLAs:
```
SLA DASHBOARD — [Vendor]

| Metric | SLA Target | Actual (This Month) | Status |
|--------|-----------|---------------------|--------|
| Uptime | 99.9% | 99.7% | ⚠️ Below SLA |
| Response Time | < 4 hours | Avg 6 hours | ⚠️ Below SLA |
| Resolution Time | < 24 hours | Avg 18 hours | ✅ Meeting SLA |

SLA Credits Available: [yes/no — amount if yes]
Action: [file claim / monitor / none needed]
```

---

## Vendor Communication Management

### Contact Hierarchy
For each critical vendor, know who to contact at each level:
1. **Level 1**: Self-service / knowledge base / chatbot
2. **Level 2**: Standard support (email, ticket, chat)
3. **Level 3**: Escalated support (phone, priority ticket)
4. **Level 4**: Account manager or relationship manager
5. **Level 5**: Executive escalation (when all else fails)

### Communication Log
Track significant vendor communications:
```
DATE: [date]
VENDOR: [name]
TYPE: [support ticket | email | phone | meeting]
SUBJECT: [topic]
OUTCOME: [resolved | pending | escalated]
FOLLOW-UP: [next step and date]
REFERENCE: [ticket number, email thread, etc.]
```
