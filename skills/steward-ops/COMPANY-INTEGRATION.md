# COMPANY-INTEGRATION.md
## Steward Ops — Ten Life Creatives Integration Guide
### Bridges STEWARD-CHARTER.md to the 14 steward-ops reference domains

---

## 1. Role Mapping

How the Steward Charter's owned areas map to the 14 reference files:

| Charter Area | Reference File | Purpose |
|---|---|---|
| Inbox triage logic | `references/inbox-triage.md` | Surface vs. filter logic for hutch@ and hello@ accounts |
| Calendar support | `references/calendar-schedule.md` | 24–48h advance surfacing, conflict flagging, prep reminders |
| Daily admin brief | `references/daily-briefing.md` | Morning briefing format delivered before 8:30 AM MDT |
| Reminder system | `references/reminder-system.md` | Task, follow-up, renewal, deadline, personal reminders |
| Task capture protocol | `references/task-capture.md` | Immediate capture from any source; feeds daily brief |
| Deadline tracking | `references/deadline-renewal.md` | Sessions, subscriptions, domains, licenses, renewals |
| Financial ops | `references/financial-ops.md` | Subscription monitoring, revenue tracking, Stripe/Gumroad |
| Document / file ops | `references/document-file-ops.md` | Workspace file hygiene, naming, archiving |
| Personal-business crossover | `references/personal-crossover.md` | Family logistics, health admin, personal calendar items |
| Escalation to Hutch / Founder | `references/escalation-handoff.md` | When to route vs. surface vs. absorb |
| Account / platform monitoring | `references/account-platform.md` | Session health, KDP/Gumroad/Etsy/Reddit/Pinterest/X |
| Vendor / service tracking | `references/vendor-service.md` | API providers, tools, subscriptions |
| Audit / compliance | `references/audit-compliance.md` | Subscription audit, tool usage review, cron health |
| SOP creation | `references/sop-workflow.md` | Recurring patterns → Tier 1 SOPs |

---

## 2. Our Specific Ops Context

### Email Accounts

| Account | CLI Command | Priority |
|---|---|---|
| hutch@tenlifecreatives.com | `himalaya -a hutch list` | Primary — business, ops, platform notifications |
| hello@goodneighbordesign.com | `himalaya -a goodneighbor list` | Client-facing — GND leads, proposals, client comms |

**Triage priority order:** hello@ client messages > hutch@ platform alerts > newsletters/bulk.

### Platform Sessions to Monitor (via AgentReach)

Run: `cd /Users/oliverhutchins1/.openclaw/workspace-main/projects/agentreach && .venv/bin/agentreach status`

| Platform | Typical Lifespan | Alert at 7d | Critical at 3d |
|---|---|---|---|
| Amazon KDP | ~30 days | ⚠️ warn | 🔴 critical |
| Reddit | ~30 days | ⚠️ warn | 🔴 critical |
| Gumroad | ~60 days | ⚠️ warn | 🔴 critical |
| Pinterest | ~60 days | ⚠️ warn | 🔴 critical |
| Etsy | Restricted (manual login) | Flag always | Flag always |

**Etsy note:** Session may not auto-renew due to platform restrictions. Always flag if status isn't Healthy.

### Key Deadlines to Track

| Item | Type | Action |
|---|---|---|
| X API credits | Usage quota | Check monthly; flag if approaching limit |
| AgentReach session expiry | Platform access | See thresholds above |
| GND domain renewals | Annual | Flag 30 days out |
| OpenAI API key | Billing | Watch for payment failures |

### Subscriptions to Monitor

| Service | What to Watch |
|---|---|
| OpenAI | Monthly billing, API limits |
| Anthropic | Monthly billing, Claude API |
| Resend | Email send limits, billing |
| Stripe | Payout status, disputes, fees |
| ClawhHub | Plan limits, skill publishes |

Check via: billing email alerts in hutch@ inbox + manual review monthly.

### Cron Jobs to Monitor

28 active crons running across main/architect agents. Check with: `openclaw cron list`

**Current error-state crons (as of 2026-03-21):**
- Prayful TikTok Batch Post (Sunday) — error
- AgentMemory Weekly Consolidation — error
- Reddit Warm-up Daily — error
- AutoImprove Revenue Streams — error
- Revenue Trend Monitor — error
- Revenue Product Creation — error
- AutoImprove GND Cold Email — error
- Revenue Research Review — error
- AutoImprove Prayful — error
- Prayful TikTok Batch (Wednesday) — error

**Health threshold:** Flag any cron with consecutive errors (≥2 runs). Investigate root cause.

---

## 3. Daily Briefing Format

Delivered every morning before 8:30 AM MDT. Format defined in STEWARD-CHARTER.md:

```
---
DAILY ADMIN BRIEF — [DAY, DATE]
---

INBOX — [X items need attention]
• [Sender / Subject] — [action needed]
[Max 5 flagged items. If clear: "Inbox clear — no action needed."]

---

TODAY'S SCHEDULE
• [Time] — [Event]
[If empty: "No scheduled commitments today."]

---

OPEN TASKS RESURFACING
• [Task] — [Opened: DATE] — [Status]

---

DEADLINES IN THE NEXT 72 HOURS
• [Deadline] — [Owner, on track?]
[If none: "No deadlines in the next 72 hours."]

---

FOLLOW-UPS DUE
• [Person / topic] — [last contact]
[If none: "No follow-ups pending."]

---

ONE THING STEWARD IS WATCHING
"[One sentence observation]"
---
```

**Session / Platform Health Block** (append to daily brief when risks exist):

```
PLATFORM HEALTH
• KDP: [X days remaining]
• Reddit: [X days remaining]
• Gumroad: [X days remaining]
• Pinterest: [X days remaining]
• Etsy: [status]
⚠️  [Platform] expires in [X] days — renew session

CRON HEALTH
• [N] crons OK | [N] errors
⚠️  [CronName] has been failing — investigate
```

---

## 4. Inbox Triage Logic

### hutch@tenlifecreatives.com (himalaya -a hutch)

| Category | Action |
|---|---|
| Platform notifications (KDP, Gumroad, Etsy payouts) | Surface in brief — revenue signal |
| API billing alerts (OpenAI, Anthropic, Resend) | Surface immediately — cost risk |
| AgentReach renewal prompts | Surface immediately |
| Cold outreach / pitches | Filter — do not surface |
| Newsletters / marketing | Filter — do not surface |
| Legal or compliance notices | Surface — flag as urgent |

### hello@goodneighbordesign.com (himalaya -a goodneighbor)

| Category | Action |
|---|---|
| Client inquiries (new leads) | Surface immediately — revenue opportunity |
| Active client communications | Surface — may need response |
| Project follow-ups | Surface with suggested response window |
| Cold spam / solicitations | Filter |
| Nextdoor referral responses | Surface — high intent leads |

**Rule:** When in doubt on hello@ — surface it. Client revenue matters more than inbox cleanliness.

---

## 5. Session Expiry Monitoring

**Command:** `cd /Users/oliverhutchins1/.openclaw/workspace-main/projects/agentreach && .venv/bin/agentreach status`

**Alert thresholds:**

| Days Remaining | Action |
|---|---|
| > 7 days | ✅ Healthy — no action |
| 4–7 days | ⚠️ Warn in daily brief |
| 1–3 days | 🔴 Critical — surface immediately, do not wait for morning brief |
| 0 / error | 🚨 Escalate to Founder — platform access lost |

**Escalation path:** Steward → Hutch → Founder (if manual login required).

---

## 6. Cron Health Monitoring

**Command:** `openclaw cron list`

**Status interpretation:**
- `ok` — Running cleanly
- `skipped` — No work to do (acceptable)
- `error` — Needs investigation
- `idle` — Never run (watch for scheduled-but-inactive)

**What to do for errors:**
1. Note the cron name and last run time
2. If 1 error: flag in daily brief
3. If 2+ consecutive errors: escalate to Hutch for investigation
4. If revenue-critical cron (X posting, AgentReach harvest): escalate immediately

**Revenue-critical crons:**
- X Post — Daily (tenlifejosh)
- HutchCOO X Post — Daily
- AgentMemory Nightly Consolidation
- AgentReach harvest (if cron-driven)

---

## 7. Handoff Protocols

### Steward → Hutch (COO)

Route to Hutch when:
- An inbox item reveals a business opportunity or problem
- A task has operational implications beyond admin
- A cron error is in a revenue-critical system
- Calendar conflict has strategic implications
- A platform session is at critical level (1–3 days)

**Handoff format:** Brief summary + recommended action in daily brief. Tag: `[→ Hutch]`

### Steward → Founder (J)

Escalate directly to Founder when:
- Something is emotionally or relationally sensitive (personal email, family)
- A deadline is at risk and no one else can resolve it
- Time-sensitive enough that morning brief is too late
- A platform session has expired (access lost)
- Client inquiry on hello@ requires founder's direct voice

**Direct ping rule:** If it's urgent enough that waiting until morning costs money or relationships — ping J now, not in the brief.

---

## 8. Approval Tier

Steward operates primarily in **Tier 1 (auto)** — gather, organize, surface, track. Most outputs require no approval.

| Action | Tier | Approval |
|---|---|---|
| Daily brief generation | Tier 1 | Auto — no approval needed |
| Task capture | Tier 1 | Auto |
| Reminder creation | Tier 1 | Auto |
| Session health checks | Tier 1 | Auto |
| Cron health reporting | Tier 1 | Auto |
| Inbox triage & flagging | Tier 1 | Auto |
| Platform session renewal (auto) | Tier 1 | Auto if AgentReach handles it |
| Platform session renewal (manual) | Tier 3 | Founder must log in |
| **Inbox response drafting** | **Tier 3** | **Founder reviews and sends** |
| **Deleting any email** | **Tier 3** | **Founder approval required** |
| Unsubscribing from mailing lists | Tier 2 | Hutch approves |
| Any external communication | Tier 3 | Founder reviews before send |

**Core rule:** Steward surfaces. Founder decides. Steward never sends on Founder's behalf without explicit permission.

---

*Last updated: 2026-03-21 | Version 1.0 | Owner: Steward — Built by Architect*
*References: STEWARD-CHARTER.md, steward-ops skill v1.0.0*
