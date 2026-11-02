# Crisis Statement Templates

Adapted from a contribution by @fyscleaning-jpg (PR #381).

Structures for the most common crisis statements. Fill in real specifics. Nothing ships with brackets still in it. For when to use each one, see [crisis-communications.md](crisis-communications.md).

## Contents
- Holding statement
- Full incident statement
- Data breach / security incident notification
- Product outage statement
- Customer harm / apology statement
- Billing or pricing error statement
- Public postmortem

## Holding Statement

Use in the first 30-60 minutes, before facts are confirmed.

```
We're aware of [specific issue: outage / reports of X / the incident described in Y].

We're actively investigating and will share a full update by [specific time].

[Optional: In the meantime, [status page link / workaround].]
```

Say nothing about cause, scope, or who's affected. That belongs in the full statement once confirmed.

## Full Incident Statement

```
[What happened, in one or two plain-language sentences.]

[Who is affected. Be specific: "customers on the X plan," "users who signed up before [date]," "all users in [region]."]

[What is confirmed, and what is still under investigation.]

[What we're doing about it right now.]

[What affected people should do, if anything.]

[When we'll share the next update.]

[A direct contact or channel for questions.]
```

## Data Breach / Security Incident Notification

Have legal counsel review this before it goes out. Notification deadlines and required content vary by jurisdiction and data type, and counsel decides which apply. Keep the responsibility and apology language only once counsel has cleared it.

```
Subject: Important security update about your [Company] account

We're writing to tell you about a security incident that [affected / may have affected] your account.

What happened: [How it was discovered, when, and by whom (internal team, external researcher, customer report).]

What information was involved: [Be exact. If scope is still being confirmed: "We have confirmed [X] was affected. We are still investigating whether [Y] was affected and will update you by [date] either way."]

What we've done: [Containment steps, e.g. "We patched the vulnerability, rotated affected credentials, and engaged an outside security firm to audit the fix."]

What you should do: [Concrete steps: reset your password, turn on two-factor authentication, watch your statements for [specific activity].]

What we're changing: [The process or system change that prevents a repeat.]

We're sorry for the concern this has caused. If you have questions, contact us at [contact] and we will respond within [timeframe].
```

## Product Outage Statement

**Initial (status page or pinned post):**
```
We're experiencing [specific symptom, e.g. "elevated error rates on [feature]" or "a full service outage"] affecting [scope: all users / users in region X / users on plan Y].

We're investigating and will post an update by [time].
```

**Resolution:**
```
This incident was resolved as of [time].

Root cause: [Plain-language summary. Save the full technical detail for the postmortem.]

Duration: [start] to [end], affecting [scope].

What's changing: [Specific prevention step.]

We're sorry for the disruption. [If applicable: credit details and how they'll be applied automatically, with no request needed.]
```

## Customer Harm / Apology Statement

For one customer's bad experience that has gone public. Contact the customer privately first. A public apology they haven't seen, or one that contradicts what you told them, makes it worse.

```
We saw [customer]'s experience with [specific situation], and we're sorry. [State plainly what went wrong, without "if" language.]

[What we're doing to make it right for this customer.]

[What we're changing so it doesn't happen to others. Name the change, not "we're reviewing our processes."]

We've reached out to [customer] directly and will keep working with them until this is resolved.
```

## Billing or Pricing Error Statement

Lead with the fix already underway. Don't ask affected customers to come forward.

```
We found an error that [specific issue, e.g. "overcharged customers on the annual plan between [dates]"], affecting [number or percentage] of customers.

We've already [issued refunds / applied credits / fixed the billing logic]. You don't need to do anything. [Refunds / credits] will appear by [date]. If you don't see it by then, contact us at [channel].

This happened because [brief, honest root cause, e.g. "a bug in our billing migration"]. We've fixed it and added [specific safeguard] to catch this before it reaches customers.

We're sorry for the trouble and appreciate your patience.
```

## Public Postmortem

For Tier 3 and 4 incidents, published once the crisis is resolved and root cause is confirmed.

```
# [Incident name]: Postmortem

Summary: [2-3 sentences: what happened, impact, duration.]

Timeline:
- [Time]: [Event, e.g. issue introduced, first reports, internal escalation, fix deployed, fully resolved]

Root cause: [Specific technical or process cause. Avoid vague phrases like "a configuration issue."]

Impact: [Who and what was affected, scope, duration.]

What we're changing:
1. [Specific, verifiable change, e.g. "added automated rollback on failed deploys"]
2. [Specific, verifiable change]

What went well: [Optional. E.g. fast detection, clear internal communication.]

What we'd do differently: [Honest gaps in the response, beyond the technical cause.]
```

Vague commitments ("we'll do better") are forgettable. Specific, checkable ones rebuild trust.
