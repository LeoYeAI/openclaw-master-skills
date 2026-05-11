---
name: datadog-monitor-designer
description: Design Datadog monitors that catch real production issues without paging on noise. Covers SLO-based monitoring with multi-window multi-burn-rate alerts, the decision between threshold/anomaly/forecast/outlier/composite monitor types, tag-driven routing, downtime windows, monitor template inheritance per service tier, notification message engineering, and runbook linking. Acts as a senior SRE who has owned 4,000+ Datadog monitors and pruned them down to 600 monitors that still catch every real incident. Knows the Datadog billing levers (custom metrics, indexed logs, ingested traces), how `from`/`group_by` interact with no-data evaluation, the difference between simple alerts and multi-alerts, and which monitor types are silently expensive. Use when monitors are paging on cosmetic blips, when a service tier needs a coherent monitor set, when SLOs need turning into burn-rate alerts, or when monitor sprawl is unmanageable. Triggers on "datadog", "datadog monitor", "monitor design", "slo", "burn rate", "anomaly monitor", "forecast monitor", "composite monitor", "alert routing", "runbook", "downtime", "noisy monitor", "monitor template", "service tier", "T0", "T1".
metadata:
  tags: ["datadog", "monitoring", "observability", "slo", "sre", "alerts", "devops", "incident-management"]
---

# Datadog Monitor Designer

Design Datadog monitors that page humans only when paging is justified. Acts as a senior SRE who has run a Datadog org with 4,000 monitors, watched 90% of pages get auto-resolved with no action, and rebuilt the monitor estate around SLOs and tier templates until the false-positive rate fell from 70% to 8%.

This skill builds and tunes monitors. It does not replace your incident response process, your SLO design process, or your service catalog — it consumes them. Outputs are concrete monitor JSON (importable via Datadog API or Terraform `datadog_monitor` resource), notification message templates, downtime windows, and a per-service monitor inventory tied to ownership tags.

## Usage

Invoke when:

- Monitors page on every minor blip; on-call comp is rising
- A new T0 service is shipping and needs its monitor pack from day one
- An existing service has 80 monitors and only 6 ever fire
- SLOs were defined in a doc but never wired to alerts
- A postmortem revealed the right monitor existed but conditioned on the wrong tag set
- The Datadog bill jumped because of `avg by:` cardinality on a custom metric used in monitors
- Monitor message bodies are unparseable; runbook links are missing or rotted
- A monitor fires across all environments because nobody scoped it to `env:prod`

**Basic invocations:**
> Design a T0 monitor pack for our checkout service
> Convert our 99.9% latency SLO into burn-rate alerts
> Audit our 4,000 monitors and tell me which 80% are noise
> Write a notification template the on-call doesn't have to decode

## Inputs Required

- Datadog org + API key (or a monitor export via `datadog-monitor` Terraform / API dump)
- Service catalog: name, tier (T0/T1/T2), team owner, runbook URL, dashboard URL
- SLOs in scope (objective, window, error budget) — Datadog SLO objects or external doc
- Routing targets: PagerDuty service per team, Slack channels, on-call schedule
- Existing tag taxonomy: `env`, `service`, `team`, `criticality`, `version`, `region`
- Recent incident list (last 90 days) — for monitor coverage analysis
- Custom metric inventory + cost (Datadog → Plan & Usage → Custom Metrics)
- Constraints: budget limit, custom metric cap, log indexing limits

## Workflow

1. **Inventory existing monitors.** API: `GET /api/v1/monitor` (paginate). Tag each monitor with: type, service, tier, fired in last 90d?, ack rate, false-positive rate (acks resolved with "no action"), downstream routing. Anything that hasn't fired in 90 days and isn't tied to a documented invariant is a deletion candidate.

2. **Classify by tier.** Cross-reference the service catalog. Every monitor should be tagged `tier:T0|T1|T2|T3` and `team:<owner>`. Monitors without a tier or owner go to a triage list.

3. **Map SLOs to burn-rate alerts.** For each SLO, generate the multi-window multi-burn-rate (MWMB) monitor pair: a fast-burn alert (high rate, short window) and a slow-burn alert (low rate, long window). See the SLO recipe section.

4. **Apply tier templates.** Each tier has a base monitor set: availability, latency, saturation, error rate, dependency health. Generate the tier template with placeholder substitution for service name and metric source.

5. **Pick the right monitor type per signal.** Threshold for known SLAs and SLOs, anomaly for diurnal seasonal metrics, forecast for trend-based saturation (disk, certs, quota), outlier for fleets where one host misbehaves, composite for "A AND B for X minutes" without doubling pages.

6. **Engineer notification messages.** Every monitor message has the same eight required elements (see Notification Anatomy). Use Datadog template variables (`{{value}}`, `{{host.name}}`, `{{ #is_alert }}…{{ /is_alert }}`) for live data; static text for runbook URL and severity.

7. **Wire tag-driven routing.** `@pagerduty-<service>` for P0/P1, `@slack-<channel>` for P2/P3. Routing is in the message body, scoped by `{{ #is_alert }}` so resolved-events don't re-page.

8. **Set downtime windows.** Deploy windows, maintenance windows, known-noisy windows. Use `Downtime` API with scope filters (`env:prod service:checkout`); document expected duration.

9. **Configure no-data behavior.** `notify_no_data: true` is correct for "this metric should always have data" (heartbeats, uptime). For sparse metrics, `notify_no_data: false` plus a separate uptime monitor. Never default to `true` on every monitor — it pages on deploys.

10. **Group by stable dimensions only.** `group by: host` on auto-scaling fleets explodes alert count on scale-up. Group by `service`, `env`, `cluster`, `customer-tier`. Avoid `host` and `pod_name` in monitor groupings unless the monitor is host-specific.

11. **Test the monitor.** Dry-run with `Test Notifications` button or API `POST /api/v1/monitor/{id}/notify`. Verify routing, message rendering, runbook link, severity. Fire-drill once per quarter via the Datadog `mute_status_handle` or by deliberately tripping the threshold in a synthetic.

12. **Document the monitor.** Each monitor has a `runbook_url` tag and the runbook link in the message. The runbook covers: what the monitor means, what to check first, who to escalate to, common causes, common false positives.

13. **Schedule audits.** Monthly: stale monitor pruning, false-positive review. Quarterly: tier template refresh, SLO re-baselining, cost review.

## Monitor Type Decision Tree

Datadog has nine monitor types; most teams use Threshold for everything. That's how you get 4,000 monitors that don't catch real issues. Pick the type that matches the signal shape.

```
What are you alerting on?
├── A static SLA / SLO threshold (latency < 500ms, error rate < 1%)
│     → Metric Threshold monitor
│
├── A trend that crosses a threshold over time (disk fills, quota exhaust, cert expiry)
│     → Forecast monitor (linear or seasonal forecast)
│
├── A metric with a strong daily/weekly seasonality (traffic, signups)
│     → Anomaly monitor (agile, robust, or basic algorithm)
│
├── One host/pod/instance behaving differently from its peers
│     → Outlier monitor (DBSCAN, MAD, or scaledZ)
│
├── A condition that requires multiple signals to all be true
│     → Composite monitor (AND of two metric monitors)
│
├── An event happening (deploy, security finding, audit log)
│     → Event monitor or Event-V2 monitor
│
├── A log pattern occurring at rate
│     → Log monitor (don't use Threshold on a log-based metric — Log monitor is cheaper)
│
├── An external endpoint being reachable
│     → Synthetic monitor (browser or API test)
│
└── A process / service running on a host
      → Process monitor (legacy) or Service Check monitor
```

**Rules of thumb:**
- Anomaly monitors are great for *unexpected* changes but terrible for known invariants. Use them on traffic, not error rate.
- Forecast monitors require >2 weeks of history; don't use on new metrics.
- Outlier monitors silently break when the fleet has <5 members. Set a min-host gate.
- Composite monitors don't multiply cost; they reduce alert count by AND'ing.
- Log monitors index all matched logs — they cost on log volume, not metric count.

## Service Tier Templates

Each tier ships with a fixed monitor pack. A new T0 service goes from zero to fully covered in 15 minutes by importing the template.

### T0 Critical (revenue path, auth, payments)

| Monitor | Type | Threshold | Window | Notify |
|---------|------|-----------|--------|--------|
| Availability (HTTP 5xx rate) | Metric Threshold | >0.5% over 5m | 5m | P0 → PagerDuty (urgent) |
| p99 Latency | Metric Threshold | >1.5x SLO over 10m | 10m | P1 → PagerDuty (high) |
| Error budget burn (fast) | SLO burn-rate | 14.4x burn over 1h | 1h | P0 → PagerDuty (urgent) |
| Error budget burn (slow) | SLO burn-rate | 6x burn over 6h | 6h | P1 → PagerDuty (high) |
| Saturation (CPU/mem) | Forecast | >85% in 24h | 24h forecast | P2 → Slack |
| Dependency health | Composite | upstream availability < 99% AND request rate > 100/s | 5m | P2 → Slack |
| Deploy regression | Anomaly | error rate +3σ post-deploy | 30m | P1 → PagerDuty (high) |
| No-data (heartbeat) | Metric Threshold (notify_no_data) | no data for 5m | 5m | P1 → PagerDuty (high) |
| Cost anomaly (AWS bill tag) | Anomaly | +2σ on 7d window | 24h | P3 → Slack digest |

### T1 Important (dashboards, search, internal APIs)

| Monitor | Type | Threshold | Window | Notify |
|---------|------|-----------|--------|--------|
| Availability | Metric Threshold | >2% over 10m | 10m | P2 → Slack live |
| p95 Latency | Metric Threshold | >2x baseline over 15m | 15m | P3 → Slack digest |
| Error budget burn | SLO burn-rate | 6x burn over 6h | 6h | P2 → Slack live |
| Saturation | Forecast | >90% in 48h | 48h forecast | P3 → Slack digest |
| Deploy regression | Anomaly | error rate +3σ post-deploy | 1h | P2 → Slack live |
| No-data | Metric Threshold | no data for 15m | 15m | P3 → Slack digest |

### T2 Best-effort (internal tools, batch jobs, marketing)

| Monitor | Type | Threshold | Window | Notify |
|---------|------|-----------|--------|--------|
| Availability | Metric Threshold | >5% over 30m | 30m | P3 → Slack digest |
| Job failure (batch) | Event monitor | failed job event | event | P3 → Slack digest |
| Cron heartbeat | Synthetic / heartbeat | missed schedule by 2x interval | 2x | P3 → Slack digest |

T3 (experiments, prototypes) get **no monitors**. If they need monitoring they're not T3.

## SLO-Driven Monitoring Recipe (Multi-Window Multi-Burn-Rate)

The SRE workbook standard. Every SLO turns into two paired alerts: fast-burn (catches fast-burning incidents) and slow-burn (catches slow-burning ones). Single-window burn-rate alerts either page too late or page on noise.

**Definitions** (assuming 30-day SLO window, 99.9% objective, error budget = 0.1% = 43.2 minutes):

```
fast_burn_rate  = 14.4   # exhaust full budget in (30d / 14.4) = 50 hours
slow_burn_rate  =  6     # exhaust in 30d / 6 = 5 days
fast_window     =  1h    # short evaluation, fast detection
slow_window     =  6h    # longer evaluation, fewer false positives
```

**The two monitors per SLO:**

```yaml
# Fast-burn (page urgently)
type: slo alert
slo: <slo_id>
threshold:
  - critical: 14.4
  - warning: 6
threshold_windows:
  - critical: 1h
  - warning: 5m   # short-window check to confirm
notify: "@pagerduty-{{service}}"
message: "🔥 Fast burn: {{value}}x error budget consumption in last 1h"

# Slow-burn (page during business hours)
type: slo alert
slo: <slo_id>
threshold:
  - critical: 6
  - warning: 3
threshold_windows:
  - critical: 6h
  - warning: 30m
notify: "@slack-{{team}}"
message: "🐌 Slow burn: {{value}}x error budget consumption in last 6h"
```

**Burn-rate cheatsheet:**

| Burn rate | Time to exhaust | Use as |
|-----------|-----------------|--------|
| 1x        | 30 days (full window) | baseline (no alert) |
| 2x        | 15 days | tracking, no alert |
| 6x        | 5 days  | slow-burn alert (P2) |
| 14.4x     | 50 hours | fast-burn alert (P1) |
| 36x       | 20 hours | critical fast-burn (P0) |

For **availability SLOs**, the `good_events / total_events` formulation maps directly to Datadog SLOs. For **latency SLOs**, define `good = requests with p95 < threshold`, `total = all requests`. Datadog supports both via SLO objects.

## Notification Message Anatomy

A pageable Datadog notification has eight required elements. Anything missing is a footgun for the on-call. Use this template literally.

```markdown
# 1. SEVERITY + ONE-LINE TITLE
🚨 [P1] checkout-svc p99 latency above SLO

# 2. CURRENT STATE (template variable)
Current value: {{value}}ms (threshold: 1500ms)
Affected scope: {{scope.name}} env:{{env.name}} region:{{region.name}}

# 3. TIME WINDOW
Triggered at {{last_triggered_at}}
Evaluation window: last 10 minutes

# 4. RUNBOOK LINK (HARD REQUIREMENT)
Runbook: https://runbooks.example.com/checkout/p99-latency
Dashboard: https://app.datadoghq.com/dashboard/abc-checkout

# 5. RECENT CHANGES (auto-injected via Datadog Events overlay)
{{ #is_alert }}
Last deploy: {{ event.deploy.version }} at {{ event.deploy.timestamp }}
{{ /is_alert }}

# 6. WHO TO PAGE (routing)
{{ #is_alert }}
@pagerduty-checkout @slack-checkout-oncall
{{ /is_alert }}
{{ #is_recovery }}
@slack-checkout-oncall  ← only post recovery to Slack, NOT PagerDuty
{{ /is_recovery }}

# 7. WHAT TO CHECK FIRST (3 bullets max)
- Is upstream payment-svc healthy? (check service map)
- Did a deploy land in the last 30 min? (releases dashboard)
- Are we in a known traffic spike? (traffic dashboard)

# 8. ESCALATION
If unresolved after 15 min, escalate to @platform-team.
Owner: {{tag.team}} | Tier: {{tag.tier}}
```

**Datadog-specific tips:**
- Use `{{ #is_alert }}` blocks for alert-only content. Recovery messages should only post to Slack, never re-page PD.
- `{{ #is_no_data }}` is a separate state — the message should differ from `is_alert`.
- `{{ scope.name }}` resolves to the grouping; for multi-alerts it's the failing group, for simple alerts it's the whole monitor scope.
- Embed runbook + dashboard as hard URLs, not Datadog-internal links — the on-call may be on a phone without Datadog SSO.

## Tag Strategy

Tags drive routing, downtime, dashboard filters, and cost attribution. A bad tag taxonomy makes the entire monitor estate brittle. Lock these five tags before designing any monitor.

| Tag | Required | Values | Purpose |
|-----|----------|--------|---------|
| `env` | Yes | `prod`, `staging`, `dev`, `canary` | Scope monitors; never alert on non-prod by default |
| `service` | Yes | `checkout`, `auth`, `search`, ... | Routing, ownership, service map |
| `team` | Yes | `payments`, `platform`, `data`, ... | Routing, on-call mapping |
| `tier` | Yes | `T0`, `T1`, `T2`, `T3` | Template inheritance, severity defaults |
| `version` | Yes | git sha or semver | Deploy regression detection, downtime per release |
| `region` | If multi-region | `us-east-1`, `eu-west-1`, ... | Scope, regional outage isolation |
| `customer_tier` | If B2B | `enterprise`, `pro`, `free` | Prioritise enterprise-impacting alerts |

**Hard rules:**
- Every monitor MUST scope to `env:prod` (or explicit env) — no environment-blind monitors.
- Every monitor MUST have `service` and `team` tags so routing works.
- Don't tag with anything that has unbounded cardinality (`user_id`, `request_id`, `session_id`) — they don't help monitors and they explode metric cost.
- Tag values are case-sensitive in Datadog: `Service:Checkout` ≠ `service:checkout`. Lowercase always.

## Composite Monitor Patterns

Composite monitors (`monitor_a && monitor_b`) reduce false positives by requiring multiple signals. They're underused because most teams default to standalone thresholds.

**Pattern 1 — Error rate AND traffic floor.** A 100% error rate on 3 requests/min is noise; on 10k requests/min it's an outage.
```
composite: error_rate > 5% AND request_rate > 100/sec for 5min
```

**Pattern 2 — Latency AND deploy correlation.** p99 latency rising AND a recent deploy = regression. Either alone is normal traffic variance.
```
composite: p99_latency > SLO * 1.5 AND deploys_in_last_30m > 0
```

**Pattern 3 — Multi-region quorum.** Alert only when 2 of 3 regions are degraded.
```
composite: us_east_errors > 1% AND eu_west_errors > 1%
```

**Pattern 4 — Saturation AND queue depth.** CPU high alone is fine if work is getting done; CPU high AND queue growing = real problem.
```
composite: cpu_avg > 80% AND queue_depth > queue_depth_baseline * 2
```

**Pattern 5 — Dependency degraded AND own service degraded.** Don't alert when the upstream is down (alert the upstream's owners); only alert when the upstream's degradation impacts you.
```
composite: upstream_error_rate > 1% AND own_p99 > SLO
```

**Mute the children.** When a composite owns the signal, mute the underlying monitors so they don't double-page. Use Datadog's `mute_status_handle` or set the child monitor priority to "tracked, no notification."

## Downtime, Maintenance, and Mute Patterns

Pages during planned maintenance burn trust. Schedule downtime — don't tell humans to ignore alerts.

**Recurring downtime for deploy windows:**
```yaml
type: downtime
scope: "env:prod service:checkout deploy:active"
recurrence: rrule "FREQ=WEEKLY;BYDAY=TU;BYHOUR=14"
duration: 30m
message: "Tuesday deploy window — alerts suppressed"
```

**One-shot downtime for DB upgrade:**
```yaml
scope: "env:prod database:rds-prod-001"
start: 2026-05-10T02:00:00Z
end:   2026-05-10T04:00:00Z
mute_first_recovery_notification: true   # don't celebrate recovery while still in maintenance
```

**Smart mute for canary deploys:** mute the canary's tag for 30 minutes after deploy, but keep the rest of prod alerting normally.
```
scope: "env:prod canary:true"
duration: 30m
trigger: post-deploy webhook
```

**Mute on incident:** during an active P0 incident, mute downstream child alerts so the war room isn't flooded with secondary effects.
```
scope: "incident:INC-1234"   # via tag pushed to all downstream services
auto-unmute: 30 min after incident.resolved=true
```

**Anti-pattern: human-applied mutes.** "I'll mute it for an hour" gets forgotten. Always set an explicit end time.

## No-Data, Sparse-Data, and Heartbeat Monitors

Datadog's `notify_no_data` and `no_data_timeframe` are the most-misconfigured options.

**Decision matrix:**

| Signal | notify_no_data | no_data_timeframe | Notes |
|--------|---------------|-------------------|-------|
| Heartbeat (cron, scheduled job) | true | 2x interval | "Job runs every 1h" → no_data_timeframe = 2h |
| Always-on service traffic | true | 10m | Genuine "no traffic" is an outage |
| Sparse error metric | false | n/a | No errors = no data ≠ alert |
| User-action metric (signups) | false | n/a | Quiet hours are normal |
| Saturation metric | true | 30m | Agent died = no data = blind |
| Synthetic check | true | 5m | Synthetic failure = no test = page |

**Heartbeat pattern (the right way to monitor a cron):**
```
metric: my.cron.heartbeat (statsd counter, sent at end of each run)
monitor: max(last_2h):default(my.cron.heartbeat{job:nightly-export}, 0) < 1
notify_no_data: true
no_data_timeframe: 120
```

The `default(metric, 0)` trick converts "no data" into "value 0" so the threshold fires reliably. More robust than `notify_no_data` alone, which has subtle behaviour around evaluation windows.

## Cost Levers (Custom Metrics, Indexed Logs, Ingested Traces)

Datadog billing has three big levers. Monitors interact with all of them.

**Custom metrics:** billed per unique timeseries (metric name × tag combo) per month. A monitor `avg by (service, customer_id) over (...)` with 10,000 customers = 10,000 timeseries per metric. Stop tagging by anything user-cardinality. Use `service`, `env`, `region` only.

**Indexed logs:** billed per log indexed (not just ingested). Log monitors index matched logs. A pattern like `*` indexes every log = bankruptcy. Always scope log monitors to a specific service + level + pattern.

**Ingested traces:** billed per million spans. Trace-based monitors (APM monitors) consume ingestion budget. Use head-based sampling to drop non-error traces; tail-based for nuanced sampling on errors.

**The 80/20 cost audit:**
1. `Plan & Usage → Custom Metrics` — top 10 metrics by timeseries count
2. For each: which monitor uses it? Drop unused, refactor high-cardinality
3. `Plan & Usage → Logs` — top 10 indexes by volume; cut indexing rules to scope
4. `Plan & Usage → APM` — drop service catalog entries for retired services

## Anti-patterns

- **Threshold monitor on every metric.** Most metrics need anomaly or forecast. Threshold pages on every diurnal pattern.
- **`group_by: host` on autoscaling fleets.** Scale-up doubles your monitor count overnight; scale-down breaks no-data evaluation. Group by service, not host.
- **`notify_no_data: true` everywhere.** Pages on every deploy, network blip, agent restart. Use only for true heartbeats with a separate uptime monitor.
- **No `env:prod` scope.** Monitor fires on dev's broken laptop. Always scope to env.
- **Same monitor across all environments.** Prod thresholds are not staging thresholds. Clone with template variables.
- **Single-window burn-rate alert.** Either pages too late (long window) or on noise (short window). Always use multi-window multi-burn-rate.
- **Custom metric in monitor with high tag cardinality.** Each unique tag combo is a custom metric — Datadog charges per timeseries. `user_id` in a monitor scope = bankruptcy.
- **Notification message with no runbook link.** On-call has no idea what to do. Runbook URL is mandatory.
- **Auto-resolving without auto-recovery message.** People don't trust resolutions. Send recovery to Slack with `{{ #is_recovery }}` block.
- **Composite monitor of three child monitors that also alert independently.** Both children fire AND the composite fires — triple page. Mute children when composite owns the signal.
- **No downtime windows for known maintenance.** PagerDuty fires during your scheduled DB upgrade. Schedule downtime via API, not "I'll mute it manually."
- **Monitor sprawl with no owner tag.** When the team disbands, monitors live forever, alerting nobody. Owner tag is mandatory; orphans get auto-deleted after 30 days.
- **Anomaly monitors on error rate.** Errors are not seasonal; anomaly detects "different from baseline" which is what threshold already does. Use anomaly only on traffic-shaped metrics.
- **Forecast monitor on a 3-day-old metric.** Forecast needs >2 weeks of history. New metrics produce wild forecasts.
- **Outlier monitor on fleets of <5.** With 4 hosts, "outlier" means "1 of 4," which is just "one host has a problem." Use threshold instead.
- **Same alert message across 80 monitors.** Engineers stop reading. Each monitor's message is unique to that signal, with the right runbook link.
- **PagerDuty integration key shared across services.** All alerts route to the same PD service; routing inside PD becomes guesswork. One Datadog `@pagerduty-X` per service.
- **`avg over` instead of `min over` for SLO checks.** Avg masks brief spikes. SLO breaches are about thresholds being crossed, not averages — use `min`/`max` for breach detection.
- **Editing monitors in UI without Terraform sync.** Drift between code and reality. All monitor edits via Terraform `datadog_monitor` resource or via API with audit log.
- **Forgetting `evaluation_delay`.** When metrics arrive 30s late (common with batch ingestion), an alert evaluating the last minute sees zero data. Set `evaluation_delay: 60` to compensate.
- **Treating monitor count as a KPI.** "We have 4,000 monitors" is bad, not good. The right number is "every signal that matters has exactly one monitor."

## Exit Criteria

- Every monitor in the org tagged with `env`, `service`, `team`, `tier`, `runbook_url`
- Tier templates (T0/T1/T2) imported and applied to every service in the catalog
- Every SLO has a paired multi-window multi-burn-rate alert (fast + slow)
- Notification messages follow the eight-element template; runbook + dashboard URLs present
- Routing matches severity: P0/P1 → PagerDuty, P2/P3 → Slack live/digest
- Downtime windows scheduled for all known maintenance and deploy windows
- No-data behavior set per monitor based on signal sparsity (no global default)
- All `group_by` clauses use stable dimensions; no `host`/`pod_name` groupings on autoscaling fleets
- Custom metric usage audited; high-cardinality offenders refactored or dropped
- Monitor inventory diff: ≥40% reduction in count, ≥70% reduction in noisy pages, no measurable miss in incident detection (verified against last 90 days)
- Monthly recurring audit scheduled with a named owner per service
- Quarterly tier template refresh cadence in calendar
- New-service onboarding doc references the tier template import command (Terraform / API)
- All monitors have a corresponding entry in the service catalog dashboard for visibility
