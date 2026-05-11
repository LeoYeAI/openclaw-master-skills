---
name: pagerduty-escalation-architect
description: Design PagerDuty escalation policies, schedules, services, response plays, and incident workflows that handle real on-call traffic without burning out the rotation. Covers follow-the-sun rotations, primary/secondary patterns, weekly handoffs, escalation timeouts matched to severity, business-hour vs always-on services, override patterns for vacations, training shadow rotations, response play composition (status pages, Slack, conference bridges, Zoom auto-create), incident workflows, and postmortem auto-generation from PagerDuty timelines. Acts as a senior SRE who has run a 200-engineer on-call program across three time zones, audited the comp model for fairness, and survived multiple SOC2 audits of escalation evidence. Use when on-call is unfair, when escalations time out before humans see them, when a new service needs its routing set up, when M&A merges two PagerDuty tenants, or when comp/fairness math is overdue. Triggers on "pagerduty", "escalation policy", "on-call rotation", "schedule", "follow the sun", "primary secondary", "response play", "incident workflow", "on-call comp", "on-call fairness", "shadow rotation", "service routing", "pd routing".
metadata:
  tags: ["pagerduty", "incident-management", "on-call", "sre", "alerts", "escalation", "devops"]
---

# PagerDuty Escalation Architect

Design and tune PagerDuty escalation policies, schedules, services, and response plays. Acts as a senior SRE who has built on-call programs across three continents, run the fairness audits when engineers complain about uneven pages, and rebuilt the routing during a merger that combined two PagerDuty tenants with conflicting taxonomies.

This skill builds the routing — schedules, escalation policies, services, response plays, business-hour rules, overrides, and the math behind on-call comp. It does not write your detection logic (that's the monitoring stack), and it does not run incidents (that's the incident commander). It assumes your alert sources are already wiring into PagerDuty; the job is what happens *after* the alert lands.

## Usage

Invoke when:

- Engineers say on-call is uneven; some weeks are 30 pages, others are 0
- A service was routed to a defunct schedule and pages went nowhere for hours
- The escalation policy times out before any human sees the page
- A new T0 service is onboarding and needs routing from day one
- A merger doubled the PagerDuty tenant and the routing is a mess
- Postmortems lack the PD timeline; nobody reconstructs the response
- On-call comp is being challenged; the fairness math needs to be defensible
- Vacation overrides are manual and break every quarter
- A status page should auto-update from PagerDuty incidents but doesn't
- SOC2 auditors want evidence of escalation timeliness

**Basic invocations:**
> Build escalation policies for our 12 services, T0 to T2
> We're going follow-the-sun across US/EU/APAC — design the schedule
> Audit our PD tenant; 80 services, 120 schedules, no idea what's used
> Generate the on-call fairness report for Q1
> Compose response plays so a P1 auto-creates a Slack channel and Zoom bridge

## Inputs Required

- PagerDuty subdomain + API token (read at minimum, write for changes)
- Service catalog: name, tier (T0-T3), team owner, expected page volume
- Engineer roster per team with time zones, vacation calendar, training status
- On-call comp policy (flat rate, hourly, comp time, etc.)
- Existing escalation policies and schedules (export via API)
- Routing requirements: business-hours-only services, follow-the-sun targets
- Integrations in use: Slack, Zoom, Statuspage, Jira, Linear, Datadog, Sentry
- Compliance constraints (SOC2, ISO27001 evidence requirements)

## Workflow

1. **Audit the existing tenant.** API calls: `GET /services`, `/escalation_policies`, `/schedules`, `/users`, `/teams`, `/response_plays`. Tag each object with last-used date (incidents API, last 90 days). Anything unused for 90+ days is a deletion candidate, with the exception of compliance-required services.

2. **Build the team roster.** Each engineer needs: time zone, on-call eligibility (probation? training shadow? full?), vacation windows for the next 6 months, language/region constraints. This drives schedule design.

3. **Map services to tiers.** Cross-reference the service catalog. Each PD service must have `tier` in its name or description and a `team` association. Untiered services go to a triage list.

4. **Design schedules per team using a documented pattern** (see Schedule Design Patterns). Most teams pick: weekly handoff Mon 09:00 local, primary + secondary, follow-the-sun if multi-region.

5. **Build escalation policies tied to severity.** Tier dictates timeouts: T0 escalates fast (5 min → 10 min → 15 min); T2 slow (30 min → 60 min → out-of-hours suppress). Document each policy's *intent* in its description field.

6. **Wire services to escalation policies.** Each PD service points to one escalation policy. Use Event Rules and Service Orchestration for routing fan-out (one alert source → multiple services based on payload).

7. **Build response plays.** Each tier has a baseline play that fires on incident trigger: post Slack channel, create Zoom, post Statuspage placeholder, page secondary on critical, link runbook. Plays are composable; build a library.

8. **Set business-hour rules.** Some services should never page at 3am (internal tools, marketing site). Use schedule "layers" — restricted to business hours — that fall through to a digest queue out-of-hours.

9. **Configure overrides for vacation.** Calendar integration (Google Calendar) auto-overrides; manual overrides are a backup. Document the swap process in the runbook so engineers don't manually edit schedules.

10. **Set up training shadow rotations.** New on-call engineers shadow for 4-8 weeks: get the same pages, no notification responsibility, debrief with primary. Implement as a parallel layer that doesn't escalate.

11. **Wire integrations.** Slack: incident channels auto-created, status posts on state changes. Zoom: bridge auto-created on P0/P1. Statuspage: incident drafts on customer-facing services. Jira/Linear: post-incident ticket auto-created with timeline.

12. **Wire incident workflows.** PagerDuty Incident Workflows trigger on conditions (priority, service, payload field). Use them to fork response plays, auto-add stakeholders, run command-line tools.

13. **Generate the fairness report.** Per-engineer page count, page count outside business hours, weekend page count, escalations missed. Ship monthly. See Fairness Math section.

14. **Schedule audits.** Monthly: stale-services pruning, override audit, fairness review. Quarterly: tier reassignment, schedule pattern review. Annually: compliance evidence export.

## Schedule Design Patterns

The biggest source of on-call pain is the schedule. Pick one of these patterns deliberately; mixing patterns inside one team breaks fairness math.

### Pattern 1 — Weekly Handoff, Single Region, Primary + Secondary

The default for teams of 6-12 engineers in one time zone. Each engineer is primary one week per N weeks; secondary the week before and after primary.

```
Schedule: <team>-primary
  Layer 1: rotation 7 days, Mon 09:00 local, members [A, B, C, D, E, F]
Schedule: <team>-secondary
  Layer 1: rotation 7 days, Mon 09:00 local, members [B, C, D, E, F, A]   # offset by 1
```

Pages first hit primary (5 min) → secondary (10 min) → manager (20 min). Comp: flat rate per primary week; secondary at 0.3x rate.

### Pattern 2 — Follow-the-Sun (US / EU / APAC)

For 24/7 critical services with engineers in three regions. Each region holds the rotation during their business day.

```
Schedule: <team>-fts
  Layer 1: members [A_us, B_us, C_us], 09:00–17:00 PT, Mon–Fri
  Layer 2: members [D_eu, E_eu, F_eu], 09:00–17:00 CET, Mon–Fri
  Layer 3: members [G_apac, H_apac, I_apac], 09:00–17:00 SGT, Mon–Fri
  Final layer: weekend rotation across all members
```

Each engineer is on-call only during their business day. Weekend rotation rotates fairly across all 9. Pages between regions auto-handoff at layer boundaries — no engineer is paged at 3am unless the weekend rotation is on them.

Caveat: requires all three regions to be staffed. If APAC has 1 engineer, you're back to a single-point rotation. Start with US+EU follow-the-sun, add APAC when staffing supports it.

### Pattern 3 — Daily Rotation, Small Team

For teams of 3-5 where weekly is too long (one engineer is "on" 25% of all weeks). Daily rotation flattens load.

```
Schedule: <team>-daily
  Layer 1: rotation 1 day, Mon–Fri 09:00 local, members [A, B, C, D]
  Layer 2 (weekend): rotation 2 days, Sat 09:00 local, members [A, B, C, D]
```

Comp tracked daily. Trade-off: more handoffs = more dropped context. Document handoff in a daily on-call log.

### Pattern 4 — Business-Hours-Only with Escalation Fallback

For T2 services that genuinely don't need 24/7 coverage. Pages route to schedule during business hours; out-of-hours pages go to a digest queue or higher-tier rotation.

```
Schedule: <team>-bh
  Layer 1: rotation 7 days, members [A, B, C, D], 08:00–20:00 local, Mon–Fri
  No final layer (out-of-hours = no on-call)
Escalation policy: <team>-bh-policy
  Step 1: <team>-bh schedule (10 min)
  Step 2: <platform>-fallback schedule (20 min)
  Step 3: drop to digest queue (no further escalation)
```

If out-of-hours coverage is needed, the platform team's always-on rotation absorbs it.

### Pattern 5 — Mixed Severity (Two Schedules per Team)

Higher-severity pages route to a tighter schedule; lower-severity to a more relaxed one. Useful when one team owns both T0 and T2 services.

```
Schedule: <team>-critical
  Layer 1: weekly rotation, only senior engineers
Schedule: <team>-standard
  Layer 1: weekly rotation, full team including juniors
Service routing:
  T0 services → <team>-critical
  T1/T2 services → <team>-standard
```

## Escalation Policy Tiers

Escalation timeouts must match severity. Generic 30-30-30 timeouts mean T0 outages escalate to nobody for 90 minutes.

### T0 Critical Escalation Policy

```
Step 1: Primary on-call (5 min ack timeout)
Step 2: Secondary on-call (10 min ack timeout)
Step 3: Team lead (15 min)
Step 4: Engineering manager + Director on-call (no further timeout)
Loop: re-trigger from Step 1 every 30 min if not resolved
```

Notification rules per user: at Step 1, push + SMS + voice. SMS-only for international teammates without push.

### T1 Important Escalation Policy

```
Step 1: Primary on-call (10 min)
Step 2: Secondary on-call (20 min)
Step 3: Team lead (30 min)
No re-trigger loop (let humans drive)
```

### T2 Best-Effort Escalation Policy

```
Step 1: Primary on-call (30 min)
Step 2: Team digest channel (no escalation, just notify)
```

### Suppression Layers

For known-noisy services or non-business-hour T2 services:

```
Step 1: Primary on-call (business hours only via schedule layer)
Step 2: Out-of-hours: append to incident digest queue, no notification
```

**Hard rules:**
- Every escalation policy must end at a real human (or named team), never at "no further escalation" without an explicit fallback.
- Every step has an ack timeout and a target. No naked steps.
- Document the *intent* in the escalation policy description, not just the team name.

## Service Routing Decision Tree

How does an incoming alert reach the right service / escalation policy / responder?

```
Alert source (Datadog, Sentry, CloudWatch, custom)
  → Integration sends to PD Service or Global Event Orchestration

Decide where the routing logic lives:

1. Source-side routing (e.g. one Datadog @pagerduty-<service> per service)
   ✅ Simple, debuggable
   ✅ Works for 1:1 source-to-service mapping
   ❌ Doesn't scale when one source feeds many services with conditions

2. PD Service Orchestration (per-service rules)
   ✅ Conditions on payload fields
   ✅ Mute, suppress, or transform
   ❌ Per-service silos; can't share rules across services

3. PD Global Event Orchestration
   ✅ Org-wide rules; route by service/team/severity tag in the payload
   ✅ Catch-all for misrouted events
   ❌ Can be a tangle if not maintained

Recommendation:
- Source-side routing for clean 1:1 cases (90% of services)
- Service Orchestration for service-specific suppression / transformation
- Global Event Orchestration for catch-all and cross-cutting rules (priority mapping, dedupe)
```

**Fan-out patterns:**
- One alert → multiple services: use Global Event Orchestration to clone events with different routing keys, or use a Response Play that auto-adds responders from other teams.
- Many alerts → one service with dedupe: PD's incident dedupe key (set in payload) collapses duplicates. Use stable keys: `<service>-<alert_id>`, never timestamps.

## Response Play Library

Response plays are reusable bundles of "things that happen when an incident triggers." Build a library of named plays. Each service references the plays it needs.

### Play 1 — `play_war_room_critical`

For P0/P1 incidents.

```
Actions:
  - Create Slack channel #inc-{{ incident.id }}
  - Post Slack channel notification to #incidents
  - Create Zoom bridge; post URL to channel
  - Add responders: incident commander on-call, scribe on-call
  - Post Statuspage incident draft (if customer-facing service)
  - Add status update template to incident
```

### Play 2 — `play_silent_track`

For P2 incidents — tracked, not war-roomed.

```
Actions:
  - Post Slack thread to #team-oncall
  - Add a Linear issue with timeline link
  - No Zoom, no Statuspage, no extra responders
```

### Play 3 — `play_security_incident`

For security-tagged incidents.

```
Actions:
  - Create private Slack channel #sec-inc-{{ incident.id }}
  - Add security on-call + CISO + legal counsel
  - DO NOT post to public Slack channels or Statuspage
  - Add evidence preservation reminder
```

### Play 4 — `play_data_corruption`

For data-loss-suspected incidents.

```
Actions:
  - Page DBA on-call + data engineering lead
  - Lock affected dataset (action via runbook link)
  - Snapshot current backups
  - War room (#inc-{{ incident.id }}) with read-only access for stakeholders
```

### Play 5 — `play_release_regression`

When deploy regression alert triggers.

```
Actions:
  - Add release engineer on-call
  - Link to deploy dashboard with last 5 deploys
  - Suggested action: "rollback first, debug after" — link to rollback runbook
```

### Play 6 — `play_dependency_outage`

When upstream dependency (Stripe, Auth0, AWS) is down.

```
Actions:
  - Post to #vendor-status channel
  - Suppress related child incidents (mute_status_handle)
  - Post Statuspage with dependency status
  - Skip secondary escalation (waiting on vendor, no human action)
```

### Play 7 — `play_business_hours_only`

For T2 services that page only during business hours.

```
Actions:
  - If outside business hours: snooze incident until next business day 09:00
  - If inside: standard notify
```

### Play 8 — `play_postmortem_kickoff`

Triggered on incident resolution (workflow, not response play, but related).

```
Actions:
  - Create postmortem doc from PD timeline
  - Auto-fill: incident summary, timeline, responders, services affected, duration
  - Assign to incident commander
  - Set due date: 5 business days
```

## On-call Fairness Math

When engineers feel on-call is uneven, you need numbers. Build a monthly fairness report that scores each engineer.

**Inputs (PD API: `GET /incidents` filtered by service, time, responder):**
- Pages per engineer per month
- Pages outside business hours (22:00–08:00 local)
- Weekend pages
- Holiday pages (per local holiday calendar)
- Escalations to that engineer (received as step 2/3)
- Avg ack time
- Total on-call hours (schedule-derived)

**Compute fairness scores:**

```
weighted_pages = pages
               + 1.5 * out_of_hours_pages
               + 2.0 * weekend_pages
               + 3.0 * holiday_pages

pages_per_oncall_hour = weighted_pages / on_call_hours

team_median = median(pages_per_oncall_hour for each engineer)
fairness_index = pages_per_oncall_hour / team_median
  - 1.0 = exactly fair
  - >1.5 = significantly above median (investigate)
  - <0.5 = significantly below (training opportunity, or schedule gap)
```

**Comp formulas (pick one, document, stick to it):**

```
Flat rate (simplest):
  comp_per_week = $X for primary, $X * 0.3 for secondary, $X * 2 for holidays

Per-page (incentivizes silencing noise):
  comp = base_oncall_rate + (pages * per_page_rate)
  ⚠ Risk: incentivizes acking & dismissing; only use with strict ack-quality audit

Hour-based (most defensible):
  comp = on_call_hours * hourly_rate
       + actual_response_hours * response_hourly_rate (1.5x base)
```

**Action thresholds** (when the fairness report flags an outlier):
- Single engineer >1.5 fairness index for 2 consecutive months → schedule rebuild + training
- Service with >3x team median → tier review; service likely under-tiered
- Whole team's median rising month-over-month → noisy alerts, run the alert audit

**SOC2 / compliance evidence:**
- Export schedule + escalation policy + incident response history quarterly
- Retain for the audit window (typically 1-2 years)
- Use PD's exports + a versioned archive (S3 with object lock)

## Anti-patterns

- **Single-person schedules.** "Joe is always on-call" is a single point of failure. Always 2+ members per layer with a fallback.
- **Generic 30-30-30 escalation timeouts.** T0 outages escalate to humans 90 min late. Match timeouts to severity.
- **Manual vacation overrides.** Engineers forget; pages go to vacationing teammate. Use Google Calendar integration for auto-overrides.
- **Per-service escalation policies that all look the same.** 80 nearly-identical policies. Use 3-5 tier-based templates referenced by all services.
- **Response plays that fire on every incident.** "Auto-create Slack channel" on every P3 makes 200 channels a week. Scope plays to severity.
- **No training shadow rotation.** New engineers ack their first real page at 3am. Shadow for 4-8 weeks first.
- **Escalation that ends at "no further escalation".** If primary and secondary are both unreachable, the page dies. Always end at a manager or platform team.
- **Per-page comp without ack-quality audit.** Engineers ack and dismiss to inflate comp. Audit ack→resolution time.
- **Postmortems written from memory, not the PD timeline.** Timeline is canonical truth. Auto-extract via API.
- **Statuspage manually updated during incidents.** Slow + error-prone. Wire PD Workflow → Statuspage with templates per service.
- **One escalation policy across teams.** When a payments page lands on the search team, response is slow. Per-team or per-service routing.
- **Override + schedule conflicts that nobody notices.** PD allows overrides that contradict the schedule. Audit weekly.

## Exit Criteria

- Every PD service has tier (T0/T1/T2) and team in name or description
- Every service points to a tier-appropriate escalation policy
- Every escalation policy has documented intent in its description
- Every schedule follows one of the documented patterns; no ad-hoc layers
- Vacation overrides automated via calendar integration; manual overrides documented
- Training shadow rotation in place for any team taking new on-call engineers
- Response play library defined; each service uses 1-3 plays from the library
- Slack, Zoom, Statuspage integrations wired and tested via fire-drill
- Incident workflows configured for postmortem auto-generation
- Monthly fairness report scheduled; first 3 months baselined
- Comp policy documented; matches actual schedule load
- Compliance evidence export scheduled and retained
- Stale services pruning: ≥30% reduction in service count, no impact on real routing
- Documented runbook for "how to add a new service to PagerDuty" (including tier assignment, schedule pick, response plays, integration wiring)
- Quarterly review cadence in calendar with named owner per team
