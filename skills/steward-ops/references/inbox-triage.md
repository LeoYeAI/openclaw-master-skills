# Inbox Triage & Email Management

## Purpose
Steward's inbox triage is the single highest-impact operational skill. The average knowledge worker receives
100-200 emails per day. Of those, fewer than 10 genuinely require human judgment. Steward's job is to find
those 10 and make every other email invisible.

---

## Multi-Account Architecture

Steward manages multiple email accounts simultaneously. Each account has different roles, sender profiles,
and priority logic.

### Account Configuration Model
For each email account, maintain a profile:
```
Account: [name/label]
Address: [email address]
Role: [primary business | secondary business | personal | shared/team]
Primary Use: [what this inbox is for]
High-Priority Senders: [list of VIP senders — clients, partners, family, etc.]
Expected Automated Traffic: [what automated emails are normal here]
Response SLA: [how fast does this inbox typically need responses]
```

For example, if the principal has a "hutch" account (primary business) and a "goodneighbor" account
(brand/project), each gets its own profile with different priority logic.

---

## The Classification Engine

Every email that enters the system gets classified through a multi-stage pipeline:

### Stage 1: Source Classification
Categorize the sender immediately:

| Sender Type | Examples | Default Handling |
|-------------|----------|-----------------|
| **VIP Human** | Known clients, partners, family, boss | Always surface — P1 minimum |
| **Known Human** | Colleagues, vendors, acquaintances | Surface if action-required |
| **Unknown Human** | Cold outreach, new contacts | Evaluate content before classifying |
| **Transactional System** | Stripe, PayPal, banks, shipping | Extract key data, classify by content |
| **Platform Notification** | Amazon, Etsy, KDP, Reddit, social media | Check for action-required, else batch |
| **Marketing/Newsletter** | Subscribed lists, promotional | Archive or batch for weekly digest |
| **Automated Alert** | Monitoring systems, cron jobs, uptime | Check for anomalies, else discard |
| **Spam/Irrelevant** | Obvious junk, phishing attempts | Discard immediately |

### Stage 2: Content Analysis
For emails that pass Stage 1, analyze the content:

**Action-Required Signals** (surface these):
- Direct questions to the principal ("Can you...?", "Will you...?", "What do you think about...?")
- Explicit requests for approval, review, or sign-off
- Deadlines mentioned in the body ("by Friday", "before end of month", "ASAP")
- Payment/financial action needed ("invoice attached", "payment failed", "refund requested")
- Account issues ("suspended", "restricted", "action required", "verify your identity")
- Legal/compliance language ("notice", "violation", "terms updated", "required by law")
- Shipping/delivery problems ("returned", "undeliverable", "damaged", "lost")
- Customer complaints or negative feedback requiring response
- Meeting invitations or schedule changes
- Contract or agreement documents requiring review

**FYI-Only Signals** (batch for briefing, don't interrupt):
- Order confirmations (no action needed)
- Successful payment receipts
- Shipping tracking updates (unless there's a problem)
- Platform analytics/reports
- Social media notifications (likes, follows, comments — unless from VIP)
- Newsletter content that matches principal's interests
- System status updates (all healthy)
- Subscription renewal confirmations (already processed)

**Auto-Archive Signals** (remove from view entirely):
- Marketing emails the principal never engages with
- Duplicate notifications (same event, multiple channels)
- Automated "no-reply" confirmations for routine actions
- Social media digest emails
- App update notifications
- Terms of service update emails (unless they affect the business materially)
- Promotional offers from services the principal doesn't use
- Password reset emails that weren't requested (flag as security concern if pattern detected)

### Stage 3: Priority Assignment
Apply the universal priority framework (P0-P4) to action-required items:

**P0 — Surface immediately:**
- Payment failure on revenue-generating product or service
- Account suspension or ban notice
- Security breach notification
- Legal notice or demand
- Client emergency

**P1 — Surface within 4 hours or next briefing:**
- Client/customer emails requiring response within 24 hours
- Time-sensitive business opportunities
- Invoices due within 72 hours
- Platform policy changes affecting active products
- Partner/collaborator requests with deadlines

**P2 — Surface in daily briefing:**
- Non-urgent business emails requiring response this week
- Vendor communications about upcoming renewals
- Performance reports and analytics
- Follow-up emails from previous conversations
- Meeting-related communications

**P3 — Batch for weekly review:**
- Industry news and updates
- Non-urgent vendor communications
- Feature announcements from tools/platforms
- Networking/community emails
- Educational content and resources

### Stage 4: Action Extraction
For every action-required email, extract:
```
FROM: [sender name and relationship]
ACCOUNT: [which inbox]
SUBJECT: [email subject line]
RECEIVED: [timestamp]
PRIORITY: [P0-P4]
ACTION REQUIRED: [specific action in imperative form — "Approve the vendor contract", "Reply to Sarah's pricing question"]
DEADLINE: [when this needs to be done, extracted from email or inferred]
CONTEXT: [1-2 sentences of relevant background]
RECOMMENDATION: [if Steward has a suggestion, state it]
```

---

## Thread Intelligence

### Thread Tracking
Steward doesn't just process individual emails — it tracks conversation threads:
- **Thread state**: Is this thread awaiting our reply, awaiting their reply, or closed?
- **Thread aging**: How long since the last message? Is this going stale?
- **Thread escalation**: Has the tone shifted? Is the other party getting frustrated?
- **Thread context**: What's the full history? What commitments have been made?

### Follow-Up Detection
When the principal sends an email, Steward should:
1. Note the expected response timeframe (explicit or inferred)
2. Set a follow-up trigger if no response is received
3. Surface the "no response" alert at the appropriate time
4. Provide the original context so the principal can follow up efficiently

Default follow-up windows:
- Client emails: 48 hours
- Vendor/partner emails: 72 hours
- Cold outreach sent: 5 business days
- Application/submission: 10 business days
- Government/legal: 15 business days

---

## Email Output Formats

### The Triage Report (used in daily briefing or standalone)
```markdown
## Inbox Triage — [Date] [Time]

### 🔴 ACTION REQUIRED ([count] items)

**1. [Subject Line Summary]** — P[X]
From: [sender] | Account: [inbox] | Received: [time]
Action: [specific action needed]
Deadline: [when]
Context: [1-2 sentences]
[Recommendation if applicable]

**2. [Subject Line Summary]** — P[X]
...

### 🟡 FYI — Worth Knowing ([count] items)

- [One-line summary of each FYI item with sender]
- ...

### ✅ Handled Silently ([count] items archived/filtered)

[Brief summary: "42 marketing emails archived, 8 shipping confirmations filed, 12 social notifications cleared"]
```

### The Quick Scan (for "anything urgent?" queries)
```markdown
## Quick Scan — [Time]

[X] items need you across [Y] accounts.

**Most urgent**: [One-line description of the single most important item]
**Also needs you**: [Bullet list of other action items, max 5]
**All clear on**: [Things that are fine — "No payment issues. No account alerts. No client emergencies."]
```

---

## Email Intelligence Patterns

### Sender Reputation Tracking
Over time, Steward builds a model of each sender:
- **Response rate**: Does the principal usually reply to this sender? → Adjust priority
- **Engagement pattern**: Does the principal open emails from this sender? → Adjust visibility
- **Sender cadence**: How often does this sender email? → Detect anomalies (sudden spike = investigate)
- **Sender type drift**: Has a newsletter started sending promotional content? → Reclassify

### Automated Email Parsing
For transactional emails from known platforms, extract structured data:

| Platform Type | Extract |
|--------------|---------|
| Payment processors (Stripe, PayPal) | Amount, status, customer, product, failure reason |
| E-commerce (Amazon, Etsy, Shopify) | Order ID, product, amount, status, tracking |
| Publishing (KDP, Draft2Digital) | Title, sales data, royalty amount, review alerts |
| Hosting/SaaS (AWS, Vercel, domains) | Service, status change, renewal date, amount |
| Banking/Finance | Transaction amount, category, balance alert, fraud alert |
| Shipping (USPS, UPS, FedEx) | Tracking number, status, ETA, exceptions |

### Anomaly Detection
Flag unusual patterns:
- Sudden increase in emails from a specific sender
- Payment failure emails after a period of successful charges
- Multiple password reset emails (potential security issue)
- Platform emails about policy changes (could affect business)
- Emails from unknown senders referencing the principal by name with specific details (potential phishing)
- Bounce-back emails indicating delivery issues with outbound mail

---

## Advanced Inbox Operations

### Email Batching Strategy
Not all emails need to be processed in real-time. Steward batches non-urgent items:

| Batch Cycle | What Goes In It |
|-------------|----------------|
| **Real-time** | P0 and P1 items only |
| **Morning briefing** | P2 items accumulated overnight |
| **Midday check** | P2 items accumulated in the morning |
| **End-of-day** | Day's P3 items summarized |
| **Weekly digest** | P4 items, newsletter highlights, FYI roundup |

### Multi-Account Conflict Resolution
When the same sender appears across multiple accounts, or when a thread spans accounts:
- Consolidate the thread in the triage report
- Note which account each message came from
- Recommend which account to reply from
- Flag if a personal message arrived in a business inbox (or vice versa)

### Email-to-Task Conversion
When an email contains an action item but doesn't need an email reply:
1. Extract the task with full context
2. Add it to the task capture system (see `references/task-capture.md`)
3. Mark the email as "processed — task created"
4. Set the appropriate reminder based on the task deadline
5. Link the task back to the email for reference

### Auto-Response Intelligence
Steward NEVER sends emails without explicit approval. However, Steward CAN:
- Draft response suggestions for the principal to review
- Flag emails where a template response would be appropriate
- Identify emails that could be delegated
- Recommend "no response needed" for emails that don't warrant one
- Queue draft responses for batch approval

---

## Inbox Health Metrics
Track these to ensure the system is performing well:

- **Triage accuracy**: Are items correctly prioritized? (Measure by principal overrides)
- **False positive rate**: How many surfaced items didn't actually need attention?
- **False negative rate**: How many important items were missed? (This is the critical one)
- **Processing latency**: Time from email receipt to triage completion
- **Action item completion rate**: What percentage of extracted actions get completed?
- **Thread resolution time**: How long do active threads stay open?
- **Inbox zero achievement**: How often is the inbox fully processed?
