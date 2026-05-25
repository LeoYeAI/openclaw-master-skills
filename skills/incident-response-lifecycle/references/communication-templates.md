# Communication Templates

Notification and status update templates for incident response
communications. Organized by audience and severity level.

## Executive Notification Template

```
Subject: [P1/P2] Incident — [Service Name] — [Brief Description]

Severity:        [P1 Critical / P2 High]
Status:          [Investigating / Identified / Monitoring / Resolved]
Start Time:      [UTC timestamp]
Duration So Far: [hours:minutes]
Incident Commander: [name]

BUSINESS IMPACT:
- Users affected: [count or percentage]
- Services impacted: [list]
- Revenue impact: [estimated hourly impact or "under assessment"]
- Customer SLA breach: [yes/no — details if yes]

CURRENT STATUS:
[2–3 sentences: what is happening, what we know, what we are doing]

ESTIMATED RESOLUTION:
[time estimate or "under investigation — next update at [time]"]

NEXT UPDATE: [time UTC]
```

## Technical Notification Template

```
Subject: [Severity] Incident [ID] — [Component] — [Symptom]

Incident ID:     [tracking number]
Severity:        [P1/P2/P3]
Affected Systems: [device names, IP ranges, service names]
Start Time:      [UTC timestamp]
Technical Lead:  [name]

SYMPTOMS:
- [observable symptom 1]
- [observable symptom 2]

CURRENT HYPOTHESIS:
[what we think is happening and why]

INVESTIGATION STATUS:
- [what has been checked]
- [what is being checked now]
- [what is queued for investigation]

ACTIONS NEEDED:
- [specific asks of this technical audience]

Bridge Call: [link/number] at [time]
```

## Customer-Facing Notification Template

```
Subject: Service Impact — [Service Name]

We are aware of an issue affecting [service description].

IMPACT:
[plain-language description of what customers experience]

WORKAROUND:
[if available — specific steps customers can take]
[if not available — "We are working to resolve this as quickly
as possible."]

ESTIMATED RESOLUTION: [time or "we will provide an update by [time]"]

We apologize for the inconvenience and will provide updates as
the situation progresses.
```

## Regulatory Notification Template

```
Subject: Formal Incident Notification — [Organization] — [Date]

Reporting Organization: [legal entity name]
Incident Reference:     [tracking number]
Date of Discovery:      [date and time UTC]
Date of Occurrence:     [date and time UTC, if different from discovery]
Notification Deadline:  [per applicable regulation]

NATURE OF INCIDENT:
[factual description — what occurred, not speculation]

DATA AFFECTED:
[types of data involved, number of records if known]

INDIVIDUALS AFFECTED:
[number and categories of affected individuals, if applicable]

CONTAINMENT MEASURES:
[actions taken to limit the incident]

REMEDIATION PLAN:
[planned or completed corrective actions]

CONTACT:
[name, title, phone, email for follow-up questions]
```

## Status Update Template

```
INCIDENT STATUS UPDATE — [Incident ID] — Update #[N]
Time: [UTC timestamp]
Severity: [P1/P2/P3]
Status: [Investigating / Identified / Monitoring / Resolved]

SINCE LAST UPDATE:
- [what changed, what was discovered, what was tried]

CURRENT STATE:
- [where the investigation stands now]

NEXT STEPS:
- [what will be done before the next update]

ESTIMATED RESOLUTION: [time or "still under investigation"]
NEXT UPDATE: [time UTC]
```

## Bridge Call Runbook

### Opening (IC reads)

1. State incident ID, current severity, and duration
2. Confirm attendees and roles (IC, Tech Lead, Comms Lead, Scribe)
3. Remind participants: Scribe is recording — state your name
   before speaking

### Agenda (fixed order, every bridge call)

1. **Technical status** — Tech Lead summarizes current state, findings
   since last call, active investigation threads
2. **Communication status** — Comms Lead reports notifications sent,
   responses received, upcoming notification obligations
3. **Hypothesis board** — review current hypotheses (investigating,
   confirmed, ruled out), add new hypotheses
4. **Decisions needed** — IC solicits any decisions required (severity
   change, escalation, resource requests, customer notification)
5. **Action items** — review open items, assign new items with owners
   and deadlines
6. **Next call** — IC sets time for next bridge call per severity
   cadence

### Closing (IC reads)

1. Summarize decisions made on this call
2. Confirm action items and owners
3. State next bridge call time
4. Remind: update the incident ticket with findings before next call

## Post-Incident Review Invitation Template

```
Subject: Post-Incident Review — [Incident ID] — [Date/Time]

You are invited to the post-incident review for:

Incident ID:    [tracking number]
Incident Title: [brief description]
Severity:       [P1/P2/P3]
Duration:       [start] — [end] ([total hours])
Resolution:     [one-line summary of fix]

REVIEW DETAILS:
Date:  [within 72 hours of resolution]
Time:  [time and timezone]
Location: [room or video link]
Duration: [60–90 minutes]
Facilitator: [name]

PREPARATION:
- Review the incident timeline in [ticket link]
- Bring your notes on what happened from your perspective
- This is a blameless review — we focus on systems and
  processes, not individuals

AGENDA:
1. Timeline walkthrough (20 min)
2. Root cause analysis — 5-whys (20 min)
3. Contributing factors discussion (15 min)
4. Action item generation (15 min)
5. Wrap-up and follow-up scheduling (5 min)
```

## Incident Closure Notification Template

```
Subject: [RESOLVED] Incident [ID] — [Service Name] — Closed

Incident ID:     [tracking number]
Severity:        [P1/P2/P3/P4]
Duration:        [start] — [end] ([total hours])
Status:          RESOLVED

RESOLUTION SUMMARY:
[2–3 sentences: what was wrong, what fixed it, how we confirmed]

FINAL IMPACT:
- Users affected: [actual count]
- Services impacted: [list]
- SLA breach: [yes/no — details]

NEXT STEPS:
- Post-incident review scheduled for [date]
- Enhanced monitoring in effect until [date/time]
- Action items tracked in [ticket system link]

Thank you to everyone who contributed to resolving this incident.
```
