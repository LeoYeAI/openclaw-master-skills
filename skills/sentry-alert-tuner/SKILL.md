---
name: sentry-alert-tuner
description: Reduce Sentry alert fatigue by surgically tuning issue grouping, fingerprint rules, severity mapping, sample rates, before-send filters, sourcemap pipelines, and release-health gates. Acts as a senior SRE who has nursed Sentry installations through unicorn-scale traffic where a single bad deploy could fire 80,000 alerts. Covers Sentry SaaS and self-hosted (Sentry 24.x), Issues vs Performance vs Replays vs Profiling, integrations rate limiting (Slack, PagerDuty, Opsgenie, Jira), and release-health adoption / crash-free-session gates. Builds an Inbox hygiene playbook that survives turnover. Use when alerts are noisy, the on-call rotation hates Sentry, the bill is climbing, or Issues counts are unreadable. Triggers on "sentry", "sentry alerts", "alert fatigue", "fingerprint", "sentry inbox", "issue grouping", "before-send", "sample rate", "traces sample rate", "profiles sample rate", "release health", "sourcemap", "crash-free", "sentry noise", "sentry bill", "sentry tuning".
metadata:
  tags: ["sentry", "observability", "error-monitoring", "alerts", "incident-management", "sre", "devops", "alert-fatigue"]
---

# Sentry Alert Tuner

Tune a Sentry installation so that every alert that fires is worth a human looking at it. Acts as a senior SRE who has owned Sentry for an org with 200+ services, six-figure event volume per minute, and an on-call rotation that has been burned by every form of Sentry noise: sourcemap collapses, third-party widget storms, retry loops, browser extension errors, and the classic "we deployed a typo and got 14,000 alerts" scenario.

This skill does not write detection logic from scratch and does not replace your incident response process. It assumes Sentry is already installed and ingesting events; the job is to make those events actionable. Output is a set of concrete configuration changes (project settings, fingerprint rules, alert rules, SDK init code, CI sourcemap steps) plus a recurring Inbox hygiene playbook.

## Usage

Invoke when:

- The on-call rotation says "I just mute Sentry now"
- A single deploy generated more alerts than humans on the team
- Issues counts are dominated by browser extension noise or third-party scripts
- The Sentry bill jumped 3x without a traffic change
- New errors are buried under the same 12 long-tail issues from 2023
- Alert severities all look the same (everything is P2)
- Slack #alerts is unreadable; people muted the channel
- A postmortem revealed the real error was filed but auto-resolved or grouped into a megaissue

**Basic invocations:**
> Tune Sentry for our React + Django stack — alerts are 90% noise
> We just hit our event quota mid-month, sample rates need rethinking
> Build a fingerprint ruleset so retries don't spawn 400 issues per outage
> Set up release-health gates so a bad deploy auto-pauses rollout

## Inputs Required

- Sentry org slug + project list (or a project export)
- Stack: SDKs in use (browser, Node, Python, Go, Java, mobile) and their versions
- Current event volume per project per day (last 30 days)
- Current Issues count per project, ranked by event count
- Current alert rules and integration list (Slack channels, PagerDuty services)
- Release cadence and the existing release-health thresholds (if any)
- Sourcemap pipeline status: which projects upload, via which CI step
- The five most-hated noisy issues (the ones the team has muted manually)
- Any compliance constraints on PII scrubbing (GDPR, HIPAA, PCI)

## Workflow

1. **Pull the inventory.** Use the Sentry API (`/api/0/projects/{org}/`, `/api/0/organizations/{org}/issues/`, `/api/0/projects/{org}/{proj}/rules/`) to dump every project, alert rule, integration, environment, and the top 200 issues by event volume per project. Cache locally as JSON; the audit reruns weekly.

2. **Classify each project by tier.** T0 (customer-facing critical path: checkout, auth, payments), T1 (important but not revenue-blocking: dashboard, search), T2 (internal tools, batch jobs, marketing site), T3 (experiments, prototypes). Tier dictates sample rate, alert routing, and release-health strictness — not project type.

3. **Audit the top 50 issues per project.** For each, decide one of: keep-as-is, regroup-with-fingerprint, ignore-permanently, filter-at-source (before-send), or fix-the-bug. Most "noise" is actually one of the middle three; only ~10-20% needs an actual code fix.

4. **Write fingerprint rules.** Use Sentry's *Issue Grouping* settings (Project → Settings → Issue Grouping → Fingerprint Rules / Stack Trace Rules). Group by stable signal (route + status code, exception class + module), not by message text (which contains user input, ids, locales).

5. **Write inbound filters.** Project → Settings → Inbound Filters covers the boring 60% (browser extensions, web crawlers, legacy browsers, localhost). Turn ALL of them on by default for browser projects. They deduct from quota *before* ingestion — free win.

6. **Write before-send filters in SDK init.** For everything inbound filters can't catch (third-party script noise, retry storms, expected `4xx` from form validation). Before-send returns `null` to drop. This is where the surgical work happens.

7. **Set sample rates by event type and tier.** `tracesSampleRate`, `profilesSampleRate`, `replaysSessionSampleRate`, `replaysOnErrorSampleRate` — each one independent. Errors are always 1.0 (you want all errors); transactions and replays are sampled. Use the formulas in the Performance section.

8. **Tune severity mapping.** Most teams leave every alert at default. Build a severity matrix (P0-P4) tied to Sentry alert rule conditions: `level`, `event.tags`, `release.health.crash_free_rate`, frequency thresholds, regressions. P0 pages PagerDuty; P3/P4 only post to Slack.

9. **Wire release-health gates.** `crash-free-sessions < 99.5%` blocks rollout. `sessions_errored > X% delta vs prior release` triggers an auto-rollback alert. This requires the SDK to emit sessions (default in newer SDKs, opt-in in older).

10. **Lock down sourcemaps.** Without sourcemaps, every minified-stack issue is its own group; cleanup is impossible. Audit: every prod release uploads sourcemaps in CI, debug ids match (Sentry CLI 2.x+), and `Sentry.init()` has a stable `release` value derived from the same git sha.

11. **Right-size integrations.** Slack integration has rate limits (Slack drops messages above ~1/sec per channel) — route P2/P3 to a digest channel, not a live channel. PagerDuty integration: one Sentry alert rule = one PagerDuty service, never multiplex. Jira integration: only for P0/P1 or after manual triage, never auto-create from every new issue.

12. **Implement the Inbox hygiene weekly playbook** (see deep section). Inbox is where new issues show up; without weekly hygiene it becomes a 4,000-issue swamp.

13. **Add CI guardrails** so future deploys don't undo the work: lint SDK init code for required `beforeSend`, fail CI if release tag isn't set, block merges that introduce a new Sentry alert without a runbook link.

14. **Schedule the recurring audit.** Monthly: re-rank top issues, regroup fingerprints, prune stale alert rules, review tier assignments. Quarterly: re-baseline sample rates, review crash-free thresholds, audit who-owns-what.

## Fingerprint Customization Recipes

Sentry's default grouping is stack-trace-based. It works ~70% of the time. The remaining 30% is where alert fatigue lives. Below are battle-tested fingerprint rules. Apply via *Project Settings → Issue Grouping → Fingerprint Rules*.

**Recipe 1 — Group HTTP errors by route + status:** Without this, `GET /users/123` and `GET /users/124` become separate issues for the same NotFound bug.
```
error.type:HTTPError http.status_code:404 -> {{ transaction }}-404
error.type:HTTPError http.status_code:5* -> {{ transaction }}-{{ http.status_code }}
```

**Recipe 2 — Group third-party SDK errors under one umbrella:** Stripe, Segment, Intercom, Datadog RUM, etc. — their errors are not yours, but they fire constantly.
```
stack.module:"node_modules/stripe/*" -> third-party-stripe
stack.module:"node_modules/@segment/*" -> third-party-segment
stack.abs_path:"*intercom*" -> third-party-intercom
```

**Recipe 3 — Collapse network errors by error class, not message:** `fetch failed: ECONNRESET 10.0.0.42:443` and `fetch failed: ECONNRESET 10.0.0.43:443` are the same bug.
```
error.type:"NetworkError" -> network-{{ error.value | regex:"E[A-Z]+" }}
```

**Recipe 4 — Split a megaissue by environment:** Sometimes one issue is actually three: the staging variant, the prod variant, the canary variant.
```
error.type:DatabaseError -> {{ default }}-{{ environment }}
```

**Recipe 5 — Group browser extension noise:** Inbound filter catches the obvious ones. Fingerprint catches the rest.
```
stack.abs_path:"*chrome-extension*" -> browser-extension
stack.abs_path:"*moz-extension*" -> browser-extension
stack.abs_path:"*safari-extension*" -> browser-extension
```

**Recipe 6 — Group retries as one issue:** Background jobs that retry 5 times shouldn't create 5 events. Tag the event with `retry_attempt` and group on attempt 1 only.
```
tags.retry_attempt:1 -> {{ default }}
tags.retry_attempt:* -> retry-noise-{{ transaction }}   # send to ignored project or drop
```

**Recipe 7 — Group GraphQL operations by operationName, not query string:** Default grouping uses the full query, so a 200-line query change becomes a "new issue."
```
tags.graphql.operation_name:* -> graphql-{{ tags.graphql.operation_name }}
```

**Recipe 8 — Collapse i18n / locale variants:** Error messages like "User not found (en-US)" vs "Utilisateur introuvable (fr-FR)" are the same bug.
```
error.type:UserNotFound -> user-not-found-i18n
```

**Recipe 9 — Group SSL handshake errors by host class:** Per-host fingerprinting is too granular for transient SSL flakes.
```
error.value:"*SSL*handshake*" -> ssl-handshake-{{ extra.host_class }}
```

**Recipe 10 — Split a "catch-all" megaissue by callsite:** When `Exception` got caught at the top of a request handler and lost its real type, explicitly fingerprint by `request.url` to recover signal.
```
error.type:Exception transaction:"" -> catchall-{{ request.url | regex:"^/[^/]+" }}
```

**Recipe 11 — Don't fingerprint by user-supplied input:** Always strip `user.id`, `request.body.*`, search query strings before fingerprinting. They explode cardinality.

**Recipe 12 — Use stack-trace rules for vendor noise:** Stack-trace rules (separate from fingerprint rules) mark frames as `+app` or `-app` so Sentry's default grouping ignores vendor frames. Combine: stack-trace rule first to mark vendor frames, fingerprint rule second for what's left.

## Severity Mapping Matrix

Most teams have one severity: "an alert fired." Build a five-tier matrix. Map each alert rule to exactly one tier. Routing follows tier, not gut feel.

| Tier | Definition | Sentry conditions | Routing | SLA |
|------|-----------|-------------------|---------|-----|
| **P0** | Customer-facing outage, data corruption, auth break | `level:fatal` AND `transaction:checkout/*` OR `release.crash_free_session_rate < 99%` | PagerDuty page (urgent), #incidents, status page draft | Ack 5 min |
| **P1** | Significant degradation, error budget burn, regression in T0 | `level:error` AND `event.count > 100/5min` AND `transaction:T0/*` OR new issue in release-day window for T0 | PagerDuty page (high), #oncall | Ack 15 min |
| **P2** | New issue in T1, sustained error rate above baseline, third-party degradation | New issue assigned to a team channel, `event.count > 50/15min` for T1 | Slack #team-alerts (live channel) | Triage same day |
| **P3** | Anomaly, potential regression, low-volume issue | `event.count > 10/hour` for T1/T2, regressions of resolved issues | Slack #team-alerts-digest (hourly), Linear ticket | Triage in week |
| **P4** | Informational, expected, best-effort | Anything in T2/T3, unhandled-but-explained, deprecation warnings | Email digest weekly OR /dev/null | Optional |

**Concrete examples** — what each tier looks like in practice:

- **P0** — `Stripe charge.create raised AuthenticationError (5+ events in 60s)` — payments are down.
- **P0** — `crash-free-session-rate: 96.4% on release 2026.5.4-canary` — release-health gate tripped, auto-rollback triggered.
- **P1** — `New issue: TypeError: Cannot read 'length' of undefined in /checkout/review` — first time seen in checkout path post-deploy.
- **P1** — `Regression: ConnectionPoolTimeout (resolved 14d ago, now 200 events/5min)` — a fix unfixed itself.
- **P2** — `New issue: SegmentAnalyticsError: timeout (32 events/15min)` — third party degraded; should be tracked, not paged.
- **P3** — `Issue frequency anomaly: AddToCartFailed +250% vs 7d baseline (still <50 events/h)` — investigate this week.
- **P4** — `DeprecationWarning: moment.js used (1,200 events/day)` — file as tech debt, do not alert.

The mapping is a **decision in the alert rule**, not a Slack channel pick after the fact. Tag the rule with `severity:P1` so it's queryable.

## Inbox Hygiene Workflow (Weekly Playbook)

Without a recurring playbook, Sentry Inbox accumulates new-but-ignored issues until the For Review tab has 800 entries and nobody opens it. The agent installs this playbook as a 30-minute weekly slot, owned by a rotating team member.

```
MONDAY 09:30 — INBOX TRIAGE (30 min, rotating owner)

Step 1 (5 min): Open Inbox → For Review for the team's projects. Sort by Events.
Step 2 (10 min): For each top-20 issue:
   - Real bug, fixable: assign to owner, link to Linear/Jira, set priority.
   - Real bug, not fixable now: archive with "Until X events in Y days" rule.
   - Not a bug, expected: mark Resolved, add fingerprint/before-send rule so it
     doesn't recur. The fix is the rule, not the dismissal.
   - Third party: tag with `external_dependency:<vendor>`, archive.
   - Already-known: link to existing issue, merge.
Step 3 (5 min): Open Issues → Regressed. Investigate any regression of an
   issue resolved <30 days ago. Regressions are the #1 most-missed signal.
Step 4 (5 min): Open Releases → latest. Check crash-free-session rate.
   If <99.5% (T0) or <99% (T1), file a postmortem ticket.
Step 5 (5 min): Note three numbers in #team-status: new issues, regressions,
   crash-free rate. Trend visible to the team without opening Sentry.
```

**Archive rules (Sentry's "Archive Until" feature)** save the most time. Apply liberally:
- *Until it affects an additional 10 users* — for low-traffic noise that might be real
- *Until it occurs 100 more times* — for known-tolerable third-party storms
- *Until next release* — for issues that the next deploy will fix
- *Forever* — for known unfixable noise (use sparingly; prefer fingerprint rule + permanent ignore)

The playbook lives in MEMORY, gets re-checked monthly, and the rotation is enforced. Skipped weeks compound.

## Performance Monitoring Sample Rates

Default `tracesSampleRate: 1.0` will burn through your transaction quota in days for any project with real traffic. Default `0` blinds you to performance regressions. The trick: tier-based sampling with dynamic boost on errors.

**Formulas:**

```
errors_sample_rate         = 1.0  (always — you want all errors)
traces_sample_rate(T0)     = min(1.0, 100k / monthly_transaction_volume)
traces_sample_rate(T1)     = min(0.10, 50k / monthly_transaction_volume)
traces_sample_rate(T2)     = min(0.01, 10k / monthly_transaction_volume)
profiles_sample_rate       = 0.10 * traces_sample_rate
replays_session_sample     = 0.001  (session-mode is expensive)
replays_on_error_sample    = 1.0    (catch every error replay)
```

**Use `tracesSampler` (function form), not `tracesSampleRate` (number)** for any non-trivial project. It lets you boost sampling for important transactions and drop noisy ones:

```js
Sentry.init({
  tracesSampler: (ctx) => {
    if (ctx.transactionContext.name?.startsWith('GET /healthz')) return 0;
    if (ctx.transactionContext.name?.startsWith('POST /checkout')) return 1.0;
    if (ctx.transactionContext.op === 'queue.task') return 0.05;
    if (ctx.parentSampled !== undefined) return ctx.parentSampled;  // honour upstream
    return 0.05;  // default for everything else
  },
});
```

**Dynamic Sampling (Sentry SaaS)** does an adaptive version automatically, but only for transactions, only on Business plan and above, and only with caveats: it preserves rare transactions and important tags. If you have it, set `tracesSampleRate: 1.0` and let DS shed; if you don't, use `tracesSampler` with the formula above.

**Profile sampling** is multiplicative on traces, so `profilesSampleRate: 1.0` with `tracesSampleRate: 0.05` means you only profile sampled traces. Profile data is the most expensive — 0.10 ratio of transactions is plenty.

**Replay sampling** has two knobs: session (start a replay on every page load, sampled) and on-error (start a replay only when an error happens). On-error is free signal; turn it to 1.0 for any project where users see errors. Session replay is for product analytics, not error monitoring — keep it ≤0.1%.

## Sourcemap Pipeline

Without sourcemaps, every minified production error groups by minified stack — which changes every build. Cleanup is impossible because issues regenerate every release. Sourcemaps are the most-skipped step and the highest-leverage fix.

**Required CI steps (one of these per release):**

```bash
# Modern (Sentry CLI 2.x+, debug ids — RECOMMENDED)
sentry-cli sourcemaps inject ./dist
sentry-cli sourcemaps upload --release="$GIT_SHA" ./dist

# Legacy (release-based, works but fragile)
sentry-cli releases new "$GIT_SHA"
sentry-cli releases files "$GIT_SHA" upload-sourcemaps ./dist --url-prefix '~/static/js'
sentry-cli releases finalize "$GIT_SHA"
```

**Bundler plugins** (better than CLI for most projects):
- `@sentry/webpack-plugin` (also Vite, Rollup, Esbuild, Next.js, Nuxt, SvelteKit)
- All emit debug ids automatically with Sentry CLI 2.x+
- Set `release` from CI env (`SENTRY_RELEASE` or `process.env.GIT_SHA`)

**Verification (every release):**
1. After deploy, open the latest issue in Sentry — stack must show original source, not minified
2. `sentry-cli sourcemaps explain <event-id>` reveals which sourcemap was/wasn't matched
3. CI step: `sentry-cli sourcemaps validate ./dist` fails build if maps are missing

**Common breakage:**
- `release` mismatch between SDK init and CLI upload (most common — both must use the same git sha)
- Source URL prefix mismatch (CDN path vs origin path)
- Maps emitted but not uploaded (Vite/webpack default leaves them on disk)
- `sourceMappingURL` comment stripped by post-bundler minifier
- Per-environment releases not isolated — staging maps overwriting prod
- Hash-based filenames change per build but the release tag stays — debug ids fix this; without them, every minified-stack issue regenerates per deploy
- React Native / Expo: Hermes bytecode requires special upload flag (`--bundle-sourcemap`)
- Next.js / Nuxt: server vs client bundles need separate uploads with different prefixes (`server/` vs `static/`)
- Source files referenced but not uploaded (sourcesContent missing) — set `sourcesContent: true` in webpack config

## Before-Send Filter Cookbook

The single most leveraged knob in any Sentry SDK init. `beforeSend(event, hint)` runs in the SDK before the event leaves the user's machine; returning `null` drops it entirely. Below are battle-tested filters that ship with every project.

**Filter 1 — Drop ResizeObserver loop errors:** Browser noise from third-party widgets that monitor element resize. Pure noise.
```js
beforeSend(event) {
  const msg = event.exception?.values?.[0]?.value || '';
  if (msg.includes('ResizeObserver loop limit exceeded')) return null;
  if (msg.includes('ResizeObserver loop completed')) return null;
  return event;
}
```

**Filter 2 — Drop network errors during page unload:** Fetch aborted because the user navigated away — not a real error.
```js
beforeSend(event, hint) {
  if (event.tags?.unload === 'true') return null;
  if (hint.originalException?.name === 'AbortError') return null;
  return event;
}
```

**Filter 3 — Drop expected 4xx in form validation:** A 400 from the form validation endpoint is correct behavior, not an error.
```js
beforeSend(event) {
  const status = event.contexts?.response?.status_code;
  const url = event.request?.url || '';
  if (status === 400 && url.includes('/api/validate')) return null;
  return event;
}
```

**Filter 4 — Sample expected retry storms:** Background jobs retry; the first retry is the signal, retries 2-5 are noise.
```js
beforeSend(event) {
  const attempt = event.tags?.retry_attempt;
  if (attempt && parseInt(attempt) > 1) return null;
  return event;
}
```

**Filter 5 — Strip PII before send (GDPR/HIPAA):** Always run scrubbing in `beforeSend` even with server-side scrubbing — defense in depth.
```js
beforeSend(event) {
  if (event.user) {
    delete event.user.email;
    delete event.user.ip_address;
    event.user.id = hash(event.user.id);
  }
  if (event.request?.headers) {
    delete event.request.headers['authorization'];
    delete event.request.headers['cookie'];
  }
  return event;
}
```

**Filter 6 — Drop bot traffic:** Headless browsers, screenshot services, uptime checkers.
```js
beforeSend(event) {
  const ua = event.request?.headers?.['user-agent'] || '';
  if (/HeadlessChrome|Pingdom|UptimeRobot|GoogleBot|bingbot/i.test(ua)) return null;
  return event;
}
```

**Filter 7 — Suppress events from dev/feature branches reaching prod project:** Misconfigured DSN.
```js
beforeSend(event) {
  if (event.environment !== 'production' && SENTRY_DSN.includes('-prod')) return null;
  return event;
}
```

**Filter 8 — Drop events during known third-party outage:** Wire to a flag service, flip during incident.
```js
beforeSend(event) {
  if (window.__suppressSentry === true) return null;
  if (event.tags?.dependency === 'stripe' && window.__stripeOutage) return null;
  return event;
}
```

**Filter 9 — Server-side: drop events from canary deploy that's known broken:** Avoid 50,000 alerts during rollback window.
```python
def before_send(event, hint):
    if event.get('release') == os.environ.get('CANARY_RELEASE_BLACKLIST'):
        return None
    return event
```

## Anti-patterns

- **Auto-creating Jira tickets from every Sentry issue.** Inbox becomes Jira-sized, neither tool is a source of truth. Only auto-create from P0/P1 alert rules or after manual triage.
- **One Slack channel for everything.** Live + digest + per-team channels. Live channel is for human eyes within 5 minutes; digest is hourly; per-team is for ownership.
- **`tracesSampleRate: 1.0` "until we figure it out".** You will not figure it out; you will run out of quota. Use the formula above from day one.
- **Resolving an issue without a fingerprint or before-send change.** It will recur on the next deploy and look like a regression. Resolution must be paired with a "stop sending this" rule unless it's a real fix.
- **Ignoring browser extensions case-by-case.** Turn on every Inbound Filter for browser projects: legacy browsers, web crawlers, browser extensions, localhost. Cheap quota recovery.
- **Per-deploy alert flood with no release-health gate.** Every deploy is a chance for 10,000 alerts. Crash-free-session gate stops the bleeding before alerts fire.
- **Routing P3/P4 to PagerDuty.** It teaches the rotation to ignore PD pages. PD is for P0/P1 only.
- **Fingerprinting by `event.message`.** Messages contain user input, ids, locales — every event becomes a new issue. Fingerprint by `error.type` + `transaction` + module.
- **No `release` tag in SDK init.** Without a release, sourcemaps can't be matched, regression detection breaks, and release-health is empty.
- **One alert rule that conditions on "everything new in last 24h".** It alerts on every dev environment burp. Scope to `environment:production` and add a frequency threshold.
- **`tracesSampleRate` set, `tracesSampler` ignored.** A constant rate samples healthchecks the same as checkout. Use the function form for every project with mixed traffic.
- **Replay session sampling at 0.1 or higher.** Session replay storage is the single most expensive item on the bill. Keep session at <=0.001 and on-error at 1.0.
- **Issues page in Spike Protection mode left on.** Spike Protection drops events when volume exceeds threshold; you lose signal exactly when you need it. Fix the noise, don't drop random events.
- **Custom tags with high cardinality.** Tagging events with `user_id`, `request_id`, or `session_id` makes search slow and inflates tag storage. Use `extra` data or breadcrumbs instead.
- **No environment separation.** Staging events mixed with prod events. Always set `environment` in init from `process.env.NODE_ENV` or equivalent; alert rules scope to `environment:production`.
- **Treating Issues count as a KPI.** Reducing issue count by mass-resolving is theatre; the underlying noise still reaches Sentry and consumes quota. Reduce events at source (filter, fingerprint) instead.
- **Performance Monitoring on without budget.** Transactions are billed separately. Enabling APM on a high-traffic service without `tracesSampler` torches the quota in days.

## Integration Rate Limits and Routing

Each integration has its own rate limit and failure mode. Unaware routing causes silent message drops at the worst times.

**Slack:**
- Slack workspace API: ~1 message/sec/channel sustained. Bursts above this drop messages silently or queue them with delay.
- Sentry's Slack integration batches when it can; aggressive alert rules still flood. Route P3/P4 to a digest channel that posts hourly via a digest rule, not live.
- Use Slack workflow webhooks for high-volume status digests; keep Sentry integration for the urgent live channel.
- One Slack channel per team's live alerts; one digest channel for low-priority. Don't multiplex 8 teams into `#alerts`.

**PagerDuty:**
- PagerDuty Events API v2: 120 events/min/integration_key. Hitting it means dropped events.
- One Sentry alert rule per PagerDuty service. Don't let one rule fan out to multiple PD services — debugging which alert fired which page is a nightmare.
- PagerDuty deduplication key = Sentry issue id. Resolved Sentry issues auto-resolve PD incidents — verify this is wired or you'll have orphan PD incidents.

**Jira / Linear:**
- Auto-creating tickets per new Sentry issue is the #1 cause of "Jira is unusable now." Disable for everything except P0/P1 alerts.
- Manual create from Inbox during the weekly playbook is the right model for P2/P3.
- For P0, auto-create a high-priority ticket with template fields filled (severity, runbook link, owner) so the incident commander has a tracking artifact within seconds.

**Opsgenie:**
- Same shape as PagerDuty. Same rules apply.
- Heartbeat monitors: send a Sentry "I am alive" event from cron jobs; Opsgenie pages if the heartbeat misses.

**Microsoft Teams:**
- Sentry's Teams integration is webhook-based; rate limits are per Teams workspace (~4 msg/sec). Same routing discipline as Slack.

## Self-Hosted vs SaaS Specifics

**Sentry SaaS (sentry.io):**
- Quota is the limit; overage either drops events or upgrades plan.
- Spike Protection on by default — disable for projects where you'd rather pay than lose signal.
- Dynamic Sampling (Business plan+) handles transaction shedding automatically; on lower plans, do it yourself with `tracesSampler`.
- AI features (Issue Summary, Suggested Fix) consume API credits; toggle off if not needed.

**Sentry Self-Hosted (24.x docker-compose):**
- Storage growth is the limit. ClickHouse + Postgres + Redis + Kafka — monitor disk on each.
- Retention configured in `sentry.conf.py`: `SENTRY_EVENT_RETENTION_DAYS = 90` (default 90; reduce to 30 for cost).
- Symbolicator service for native sourcemaps — separately scaled; common bottleneck.
- Snuba/ClickHouse query performance degrades at >1B events; partition by project + time, run `ALTER TABLE ... DROP PARTITION` for retention.
- No Spike Protection — you pay in disk, not in plan upgrade. Filtering at source matters even more.

## Exit Criteria

- Top 50 issues per project audited; each has a verdict (keep / regroup / ignore / filter / fix)
- Fingerprint rules and stack-trace rules in place for the top noise patterns
- Inbound filters maxed out for browser projects
- `beforeSend` reviewed in every SDK init; documented in a shared `sentry-init.md`
- Sample rates set per tier per event type; `tracesSampler` function used for non-trivial projects
- Severity matrix (P0-P4) applied to every alert rule; routing matches matrix
- Release-health gates configured: crash-free-session and crash-free-user thresholds
- Sourcemap upload verified in CI for every prod release; `sentry-cli sourcemaps validate` is a required step
- Inbox hygiene playbook scheduled; first three weekly runs completed by different owners
- Slack/PagerDuty/Jira integration routing audited; no P3/P4 reaches PagerDuty
- CI guardrails: lint for `beforeSend`, required `release`, runbook link on new alert rules
- Monthly recurring audit scheduled in calendar with named owner
- Alert volume reduction measured: target ≥60% drop in alert count, ≥80% drop in PD pages, no measurable drop in detection of real bugs (verified against the last 90 days of incidents)
