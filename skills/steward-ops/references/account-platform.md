# Account & Platform Monitoring

## Purpose
The principal operates across multiple digital platforms — each with its own authentication sessions,
restrictions, policies, and operational requirements. A single expired session or missed policy update
can take down an entire revenue stream. Steward maintains continuous awareness of every platform's
health, session status, policy changes, and restrictions.

---

## Platform Registry

### Platform Profile Format
For every platform the principal uses, maintain a complete profile:

```
PLATFORM: [Name]
URL: [Primary URL]
Account Email: [which email is associated]
Account Type: [free | paid plan name | enterprise]
Monthly Cost: [$X or free]
Primary Use: [what this platform is used for — selling, publishing, marketing, tools, etc.]
Revenue Generating: [yes | no — if yes, estimated monthly revenue]

SESSION:
  Auth Type: [OAuth | API key | session cookie | MFA | password]
  Session Duration: [how long sessions last before re-auth]
  Last Authenticated: [date]
  Expires: [date/time]
  Re-Auth Method: [how to renew the session]
  Re-Auth URL: [direct link to login/auth page]

PRODUCTS/LISTINGS:
  Active Products: [count and list]
  Product Status: [all active | some paused | some restricted]
  Last Checked: [date]

RESTRICTIONS:
  Known Restrictions: [any current platform restrictions]
  Restriction History: [past restrictions and their causes]
  Policy Compliance: [current compliance status]

MONITORING:
  Check Frequency: [daily | weekly | on-session-expiry]
  Key Metrics: [what to check — sales, views, status, etc.]
  Alert Conditions: [what triggers an alert]
```

---

## Platform-Specific Monitoring Playbooks

### Amazon KDP (Kindle Direct Publishing)
**What to monitor:**
- AgentReach session expiration (~29 days)
- Book/product publication status
- Sales and royalty reports
- Review alerts (new reviews, negative reviews)
- Quality notifications from Amazon
- Policy updates affecting content or publishing

**Session management:**
- Track auth date and calculate expiry
- Alert at 7, 3, and 1 day before expiry
- Include re-authorization steps in every alert
- Verify product access after re-authentication

**Health checks:**
- Are all listings active and buyable?
- Any suppressed or blocked listings?
- Any quality complaints or policy notifications?
- Sales trends normal or anomalous?

**Alert triggers:**
- Session within 7 days of expiry
- Listing suppressed or removed
- Quality notification received
- Sales drop >50% vs previous period
- New negative review (1-2 stars)
- Policy change notification

### Etsy
**What to monitor:**
- API/session status
- Listing visibility and health
- Shop standing and star seller status
- Policy restrictions (Etsy has frequent policy updates)
- Payment processing status
- Seasonal traffic patterns

**Platform-specific concerns:**
- Etsy frequently updates policies — monitor for changes that affect listing content,
  categories, or fees
- Star seller status has specific metrics — track the components
- Listing quality score affects visibility — monitor impressions/views
- Shipping deadlines and tracking requirements
- Etsy Ads performance if running

**Alert triggers:**
- Shop standing change
- Listing deactivated or restricted
- Policy update affecting active listings
- Payment hold or reserve change
- Star seller metric at risk
- Etsy Ads budget depleted or underperforming

### Stripe
**What to monitor:**
- Dashboard session status
- Payment success/failure rates
- Payout schedule and status
- Dispute/chargeback activity
- Product and pricing configurations
- Webhook health (if applicable)
- API key rotation schedule

**Health checks:**
- All products active and correctly priced?
- Payment success rate normal?
- Any pending disputes or chargebacks?
- Payouts processing on schedule?
- Any flagged or held payments?

**Alert triggers:**
- Payment failure rate spike
- New dispute or chargeback
- Payout delayed or held
- Product configuration error
- API key approaching rotation deadline
- Account verification required

### Reddit (API/Bot Access)
**What to monitor:**
- OAuth token status (~29 days)
- API rate limit usage
- Subreddit access status
- Account standing
- API policy changes

**Alert triggers:**
- Token within 7 days of expiry
- Rate limit approaching threshold (>80%)
- Account action from moderators
- API policy change notification

### Google Workspace / Google APIs
**What to monitor:**
- OAuth refresh token status
- API quota usage
- Google Workspace subscription status
- Google Business Profile (if applicable)
- Google Ads account (if applicable)

**Alert triggers:**
- OAuth token invalidated (rare but critical)
- API quota exceeded or approaching limit
- Subscription payment issue
- Policy compliance notification

### Social Media Platforms (General)
**What to monitor:**
- Account health and standing
- Content moderation actions
- Follower/engagement metrics (notable changes only)
- Platform policy updates
- API/integration status
- Advertising account status (if applicable)

**Alert triggers:**
- Account warning or restriction
- Content removed or flagged
- Engagement drop >40% (suggests algorithm or policy change)
- API deprecation notice
- Platform terms of service update

### Domain Registrar / DNS / Hosting
**What to monitor:**
- Domain expiration dates
- SSL certificate expiration
- DNS configuration (no unauthorized changes)
- Hosting uptime and resource usage
- CDN status (if applicable)
- Email deliverability (SPF, DKIM, DMARC records)

**Alert triggers:**
- Domain renewal within 90 days (auto-renew OFF) or 30 days (auto-renew ON)
- SSL expiration within 30 days
- DNS record changed
- Hosting resource limit approaching (storage, bandwidth)
- Email deliverability issue detected

---

## Cross-Platform Health Dashboard

### The Platform Status Board
A visual overview of all platform health:

```markdown
## Platform Status — [Date]

| Platform | Session | Products | Revenue | Issues |
|----------|---------|----------|---------|--------|
| KDP | ✅ 22d left | 3 active | $XX/mo | None |
| Etsy | ✅ Active | 5 active | $XX/mo | 1 review issue |
| Stripe | ✅ Active | 4 products | $XX/mo | None |
| Reddit | ⚠️ 5d left | N/A | N/A | Re-auth needed |
| [Domain] | ✅ 340d left | N/A | N/A | None |

### Action Needed:
- Reddit: Re-authenticate before [date]
- Etsy: Address review issue on [product]

### All Clear:
- KDP, Stripe, Domain — no issues detected
```

---

## Platform Policy Change Monitoring

### Policy Change Detection
When a platform updates its policies:
1. Assess impact on current products/listings
2. Determine compliance deadline
3. Identify specific changes that require action
4. Prioritize by severity and deadline
5. Create action items for compliance

### Policy Change Alert Format
```
📋 POLICY CHANGE: [Platform]

What changed: [Summary of the policy change]
Effective: [date]
Impact: [how this affects our products/listings/account]
Action required: [specific changes needed for compliance]
Deadline: [when we must be compliant]
Risk if non-compliant: [what happens — listing removal, account suspension, etc.]
```

---

## Session Lifecycle Management

### Session States
```
ACTIVE ──→ EXPIRING_SOON ──→ EXPIRED
  ↑              │                │
  └──── RENEWED ←┘                │
  ↑                               │
  └──────── RE-AUTHORIZED ←──────┘
```

### Session Monitoring Protocol
1. **On authentication**: Record the auth timestamp and calculate expiry
2. **Daily check**: Calculate days remaining for all sessions
3. **Alert window**: Begin alerting at the appropriate lead time (varies by platform)
4. **Renewal prompt**: Provide complete re-auth instructions
5. **Post-renewal**: Verify the session is active and products are accessible
6. **Failure handling**: If re-auth fails, escalate with troubleshooting steps

### Session Dependency Mapping
Map what depends on each session:
```
KDP Session
├── Product: Legacy Letters (listing management)
├── Product: [Other KDP products]
├── Access: Sales dashboard
├── Access: Royalty reports
└── Access: Marketing tools

If KDP session expires:
→ Cannot update listings
→ Cannot access sales data
→ Cannot run promotions
→ Revenue continues but is unmanaged
```

---

## Platform Risk Assessment

### Risk Categories

**Revenue Risk**: Platform accounts that directly generate revenue
- Severity: Critical
- Monitoring: Daily
- Session management: Aggressive (alert at 10+ days before expiry)

**Operational Risk**: Platforms essential for business operations (email, hosting, tools)
- Severity: High
- Monitoring: Weekly
- Session management: Standard (alert at 7 days before expiry)

**Growth Risk**: Platforms used for marketing and growth (social media, ads)
- Severity: Medium
- Monitoring: Weekly
- Session management: Standard

**Convenience Risk**: Nice-to-have tools and services
- Severity: Low
- Monitoring: Monthly
- Session management: Basic (alert at 3 days before expiry)

### Platform Concentration Risk
If too much revenue depends on a single platform, flag it:
```
⚠️ CONCENTRATION RISK

[Platform] accounts for [X]% of total revenue ($[X]/month).
If this platform experiences downtime, policy changes, or account issues,
[describe impact].

Consider: Diversification into [alternative platforms/channels]
```

---

## Platform Maintenance Schedule

### Daily (automated):
- Check session expiration timers
- Monitor for payment failure emails from platforms
- Check for policy change notifications
- Scan for account warnings or restrictions

### Weekly:
- Review platform metrics for anomalies
- Check API usage against limits
- Verify all listings are active and healthy
- Review any pending platform communications

### Monthly:
- Full platform audit (every platform in the registry)
- Review and update platform profiles
- Check for new platform features or changes
- Assess platform costs against value
- Update monitoring configurations if needed

### Quarterly:
- Strategic platform review — are we on the right platforms?
- Concentration risk assessment
- Platform cost optimization
- Competitor platform analysis
- Platform roadmap review (if published)
