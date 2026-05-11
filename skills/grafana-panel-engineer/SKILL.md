---
name: grafana-panel-engineer
description: Design Grafana dashboards engineers actually use under pressure at 3am, not pretty dashboards that look good in a vendor pitch. Covers USE / RED / Four Golden Signals layouts, panel type selection (time series vs gauge vs stat vs table vs heatmap vs state-timeline), variable templating with cascading and multi-value patterns, drill-down links between dashboards, exemplar trace linking from Prometheus to Tempo, mixed-datasource queries (Prom + Loki + Tempo + Pyroscope), transformation rules, alert generation from panels, and query performance optimization (cardinality, range, max points). Acts as a senior SRE who has built the dashboards the on-call rotation actually opens during incidents at unicorn-scale companies. Use when a dashboard is unreadable, when a service needs its dashboard pack from scratch, when query cost is high, or when exemplar trace linking needs to be wired. Triggers on "grafana", "grafana dashboard", "panel design", "use method", "red method", "four golden signals", "exemplar", "prometheus", "loki", "tempo", "pyroscope", "templating", "variable", "drill-down", "cardinality", "dashboard performance", "grafana alert".
metadata:
  tags: ["grafana", "observability", "dashboards", "monitoring", "prometheus", "loki", "tempo", "sre"]
---

# Grafana Panel Engineer

Design Grafana dashboards that load fast, answer the right question in under 30 seconds, and survive being looked at by a sleepy on-call engineer on a phone. Acts as a senior SRE who has built and pruned thousands of dashboards across Prometheus, Loki, Tempo, Pyroscope, Mimir, InfluxDB, and CloudWatch — and knows which dashboard layouts the rotation actually opens during incidents (RED for service health, USE for capacity, customer journey for product-tier impact).

This skill builds dashboards. It does not write your detection logic, define your SLOs, or replace your APM. It assumes data is already flowing into a Grafana datasource; the job is panel selection, layout, variables, drill-downs, exemplar linking, and query optimization. Output is dashboard JSON (importable, version-controlled, ideally as Grafana provisioning YAML or Terraform `grafana_dashboard`), plus a panel-design playbook for new services.

## Usage

Invoke when:

- A new service is shipping and needs its dashboard pack from day one
- An existing dashboard takes 60 seconds to load
- Engineers say "I never know which dashboard to open during an incident"
- A panel uses a query with cardinality of 50,000 series and the renderer hangs
- Exemplars from Prometheus aren't wired to Tempo traces
- Variable dropdowns produce 10,000 entries; selection is unusable
- Dashboards are duplicated across teams with subtle drift
- A dashboard alert triggers but the panel doesn't show what tripped it
- Loki + Prometheus + Tempo are all installed but never queried in the same panel
- Grafana usage analytics show the dashboard count is 1,200 but only 80 are opened in a month

**Basic invocations:**
> Build a dashboard pack for our new T0 checkout service
> Audit our 1,200 dashboards and prune the unused ones
> Wire Prometheus exemplars to Tempo traces in our HTTP latency panel
> Convert our service's dashboard from USE to RED + Four Golden Signals
> Optimize this dashboard — it takes 90s to load and hangs the browser

## Inputs Required

- Grafana URL + API key (or service-account token, ideally read-write)
- Datasource list: Prometheus/Mimir/Thanos, Loki, Tempo, Pyroscope, others
- Service catalog: name, tier (T0-T3), team owner, runbook URL
- Existing dashboard inventory (export via API: `GET /api/search?type=dash-db`)
- Metric naming conventions (Prometheus: `service_name_thing_total`, etc.)
- Trace sampling: % sampled, exemplar storage backend, trace ID propagation
- SLOs and the metrics behind them (for SLO dashboards)
- Constraints: max series per panel, query timeout, dashboard refresh rate

## Workflow

1. **Inventory existing dashboards.** API: `GET /api/search`, `GET /api/dashboards/uid/{uid}`. Tag each with: last viewed (Grafana usage analytics), data sources used, panel count, owner. Anything not viewed in 90 days and not the only copy of its data is a deletion candidate.

2. **Classify dashboards by purpose.** Service health (RED), capacity (USE), customer journey (funnel/conversion), SLO (error budget), debug (drill-down for incident response), executive (summary). Each purpose has a different layout pattern.

3. **Pick a layout pattern per dashboard.** USE (Utilization/Saturation/Errors) for resource panels — CPU, memory, disk, network. RED (Rate/Errors/Duration) for request-driven services. Four Golden Signals for full service health. Customer journey for product flows. See Dashboard Layouts.

4. **Pick the right panel type per metric.** Time series for trends, stat for current value with trend sparkline, gauge for "% of capacity" only, heatmap for distributions and percentile streaks, table for top-N, state-timeline for service state, bar gauge for ranked comparison. See Panel Type Decision Tree.

5. **Design variables (templating).** Variables drive reusability. Cascade environment → cluster → namespace → service → instance. Use `Multi-value` and `Include All` carefully — they explode query cardinality. See Variable Templating Patterns.

6. **Build the queries.** PromQL with `rate()` for counters, `histogram_quantile()` for histograms, `irate()` only for short-window debug. Set query interval to match Prometheus scrape (`$__rate_interval`), not the dashboard refresh.

7. **Add drill-down links.** Each panel that shows a metric for a service should link to the deeper service dashboard. Each error-rate panel should link to logs (Loki) and traces (Tempo) filtered to the same time range and labels.

8. **Wire exemplars.** Prometheus histograms with exemplar support emit trace IDs alongside latency buckets. Configure the panel's "Exemplars" toggle and link to Tempo with `${__value.raw}` as the trace ID.

9. **Optimize for performance.** Limit cardinality (`topk`, `bottomk`), set max points (`Max data points` panel option), use recording rules for expensive queries, push aggregation to Prometheus where possible. See Performance Optimization.

10. **Set dashboard refresh + time range defaults.** Refresh: 30s for live ops dashboards, 5m for everything else, off for debug dashboards. Default time range: last 1h for ops, last 24h for trend dashboards.

11. **Add panel descriptions.** Every panel has a description: what the metric means, what's normal, what's bad, link to runbook. Right-click info icon shows it.

12. **Generate alerts from panels.** Grafana unified alerting: from a panel, build an alert rule with the same query. Tie alert annotations to dashboard panel link so on-call gets a deep-link to the panel.

13. **Provision via code.** Dashboard JSON in git, deployed via Grafana provisioning YAML or Terraform. UI edits drift; provisioning prevents drift.

14. **Schedule audits.** Monthly: stale dashboard pruning (Grafana usage analytics), variable cardinality audit, query cost review. Quarterly: layout refresh, datasource audit.

## Dashboard Layouts

### USE Method (Brendan Gregg)

For *resources*: CPU, memory, disk, network, file handles. Three panels per resource.

```
[ Utilization % ]   [ Saturation (queue depth, runqueue) ]   [ Errors / sec ]
```

Layout: one row per resource (CPU row, Memory row, Disk row, Network row). Each row has 3 panels in U/S/E order. Time series, stacked by host or pod, top-10 by `topk(10, ...)`.

**When to use:** capacity / fleet health dashboards. Not for service health (use RED).

### RED Method (Tom Wilkie)

For *services*: Rate (req/s), Errors (errors/s or %), Duration (p50/p95/p99).

```
Row 1 — Top-line:
  [ Rate (req/s) ]   [ Error rate (%) ]   [ p99 Duration (ms) ]
Row 2 — Per-endpoint:
  [ Rate by endpoint (stacked) ]   [ Error rate by endpoint (table top-10) ]   [ Duration heatmap ]
Row 3 — Per-status:
  [ Status code breakdown (stacked area) ]   [ 5xx by endpoint ]   [ Slow endpoints (table) ]
```

**When to use:** any request-driven service (HTTP, gRPC, message queue consumer). Default for T0/T1 services.

### Four Golden Signals (Google SRE Book)

Latency, Traffic, Errors, Saturation. RED + saturation.

```
Row 1: [ Traffic (req/s) ] [ Errors (%) ] [ Latency p99 ] [ Saturation (CPU/mem) ]
Row 2: [ Traffic by version (deploy overlay) ] [ Errors by error class ] [ Latency heatmap with exemplars ] [ Saturation forecast ]
Row 3: [ Throughput vs latency scatter ] [ Top errors (table) ] [ Slow queries (table from logs) ] [ Capacity headroom % ]
```

**When to use:** full service health for T0 services. Most flexible single dashboard.

### Customer Journey Layout

For end-to-end product flows (signup, checkout, search-to-purchase). Each panel = one step in the funnel.

```
Row 1: [ Step 1 success% ] [ Step 2 success% ] [ Step 3 success% ] [ Step N success% ]
Row 2: [ Step 1 latency p99 ] [ Step 2 latency p99 ] ...
Row 3: [ Drop-off Sankey or stacked bar ]   [ Bottleneck step over time ]
Row 4: [ Per-segment funnel (enterprise vs free) ]   [ Errors at top drop-off step ]
```

**When to use:** product-tier dashboards, exec dashboards, SRE dashboards for revenue-path services.

### SLO / Error Budget Layout

```
Row 1 (top-line): [ Current SLO % ] [ Error budget remaining % ] [ Burn rate now (1h) ] [ Burn rate now (6h) ]
Row 2: [ SLO over time (30d) ] [ Error budget burndown ] [ Bad events (errors+slow) over time ]
Row 3: [ Burn rate alerts (firing now) ] [ SLO violations by reason ] [ Reliability incident annotations ]
```

**When to use:** dedicated SLO dashboard, one per critical service. Linked from RED dashboard.

### Debug / Incident Drill-Down Layout

```
Row 1: [ Service health stat ] [ Recent deploys (annotation table) ] [ Active incidents ]
Row 2: [ Logs panel (Loki, last 15m, error level) ]
Row 3: [ Traces panel (Tempo, slowest 10) ]   [ Profile flame graph (Pyroscope, last 5m) ]
Row 4: [ Top errors by message (table) ]   [ Top slow endpoints (table) ]
```

**When to use:** opened during an active incident. Refresh = off (you want to study a frozen window). Time range = "last 1 hour" with a quick-pick to "since incident start."

## Panel Type Decision Tree

```
What does the panel show?
├── A value over time
│     ├── Multiple series, comparing trends           → Time series (line)
│     ├── Stacked composition (sums to a total)        → Time series (stacked area)
│     ├── Distribution at each timestamp               → Heatmap
│     └── Discrete state changes                       → State timeline
│
├── A current value (single number)
│     ├── Just the number, with trend sparkline         → Stat
│     ├── % of a maximum (CPU, disk)                    → Gauge
│     ├── A categorical status (UP/DOWN/DEGRADED)        → Stat (with thresholds for color)
│     └── A list of values (status per host)             → Bar gauge or stat-list
│
├── Top-N (top errors, slowest queries, biggest pods)
│     ├── With multiple columns                         → Table
│     ├── With one ranked metric                        → Bar gauge
│     └── With log lines                                → Logs panel
│
├── Distribution (histogram of latency, request size)
│     ├── At one moment                                 → Histogram
│     └── Over time                                     → Heatmap (with exemplars if available)
│
├── Geographic (per-region, per-country)
│     └── Geomap
│
├── Logs                                                → Logs panel (Loki)
├── Traces                                              → Traces panel (Tempo)
└── Profiles                                            → Flame graph (Pyroscope)
```

**Rules of thumb:**
- **Don't use gauges for trends.** Gauges are "% of a static cap." If the cap changes (auto-scaling), the gauge lies. Use stat with a threshold instead.
- **Heatmap > 99th percentile time series for latency.** Heatmap shows the *shape* of the distribution, not just the tail.
- **State timeline > stacked time series for service state.** "UP/DOWN/DEGRADED" reads instantly on a state timeline; on stacked time series, it's a guess.
- **Tables > stacked everything for top-N.** Stacked time series with 50 series is unreadable; a table sorted by the latest value is.

## Variable Templating Patterns

Variables drive reusability. Done badly, they break dashboards or explode cost.

### Pattern 1 — Cascading Variables

Each variable depends on the one above. Picking `cluster` filters `namespace`, picking `namespace` filters `service`.

```
$env       = label_values(up, env)
$cluster   = label_values(up{env="$env"}, cluster)
$namespace = label_values(up{env="$env",cluster="$cluster"}, namespace)
$service   = label_values(up{env="$env",cluster="$cluster",namespace="$namespace"}, service)
```

**Tip:** set "Refresh = On Time Range Change" so variable values update if the time range moves. Without it, deleted services stay in the dropdown.

### Pattern 2 — Multi-Value with Bounded "All"

Multi-value lets users select multiple services; `Include All` adds an "all" option. The catch: "all" generates a giant regex that bombs PromQL.

```
Variable: $service
Type: query
Query: label_values(http_requests_total{env="$env"}, service)
Multi-value: yes
Include All: yes
Custom all value: .*
Sort: Alphabetical (asc)
```

**Tip:** in the panel query, use `service=~"$service"` (regex match, not equality). Custom all value `.*` matches everything without bombing the parser.

### Pattern 3 — Bounded Cardinality (Top-N variable)

If `service` has 5,000 values, the dropdown is unusable. Bound it:

```
Variable: $service
Query: topk(50, sum by (service) (rate(http_requests_total[5m])))
Refresh: On time range change
```

Top 50 by traffic. Engineers care about the busy ones; the long tail goes to a separate "all services" debug dashboard.

### Pattern 4 — Custom Constants for Quick Filters

```
Variable: $window
Type: custom
Values: 1m,5m,15m,1h,6h,1d
Default: 5m
```

Used in queries: `rate(http_requests_total[$window])`. User toggles via dropdown.

### Pattern 5 — Datasource Variable

```
Variable: $datasource
Type: datasource
Query: prometheus
```

Lets the dashboard work across multiple Prometheus instances (region-specific). Panel datasource is `$datasource`. Useful for global dashboards that drill into per-region data.

### Pattern 6 — Interval Variable for Auto-Sizing Buckets

```
Variable: $interval
Type: interval
Values: 1m, 5m, 1h, 6h, 1d
Auto Option: enabled
```

PromQL: `rate(http_requests_total[$interval])`. With Auto enabled, the interval scales with the time range (zoom out → larger buckets).

## Exemplar Trace Linking (Prom → Tempo)

Exemplars are trace IDs attached to Prometheus histogram buckets. They turn a "this latency is high" panel into "this latency is high AND here are the exact traces of slow requests."

**Prerequisites:**
- Prometheus 2.26+ with `--enable-feature=exemplar-storage`
- Application emits histograms with exemplars (OpenTelemetry SDK does this by default for HTTP histograms)
- Tempo (or Jaeger/Zipkin) datasource configured in Grafana

**Configure the panel:**

```yaml
type: timeseries        # or heatmap
datasource: prometheus
targets:
  - expr: histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
    exemplar: true       # ← turn it on
fieldConfig:
  defaults:
    custom:
      showPoints: auto
options:
  exemplars:
    color: red
```

**Wire the exemplar to Tempo:**

```yaml
# In datasource provisioning
datasources:
  - name: Prometheus
    type: prometheus
    jsonData:
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: tempo-uid
          urlDisplayLabel: "View trace"
```

Click an exemplar dot in the panel → opens Tempo with that trace. The most-asked-for-but-rarely-implemented Grafana feature.

**Common gotcha:** the exemplar label must be `trace_id` (or whatever your `exemplarTraceIdDestinations.name` says) on the histogram; OTel SDK uses `trace_id` by default but custom instrumentation often uses `traceID` or `tid`. Match exactly.

## Performance Optimization

Slow dashboards are unused dashboards. Common offenders and fixes:

**Cardinality:** A query like `sum by (pod) (rate(http_requests_total[5m]))` over 50,000 pods returns 50,000 series. Browser dies. Fix:
```
topk(20, sum by (pod) (rate(http_requests_total[5m])))
```
Top-20 visible; long tail invisible. Pair with a "view all pods" button that links to a dedicated debug dashboard.

**Range:** `rate(metric[1h])` over 24h with 1m resolution returns 1,440 points × N series. Use `$__rate_interval` (auto-scales with range) instead of fixed window:
```
rate(http_requests_total[$__rate_interval])
```

**Max data points:** every panel has a "Max data points" option (default 100-200). Set explicitly to match panel width in pixels. More points = more rendering load and no extra information.

**Recording rules:** queries computed at query time on every dashboard load. Push to Prometheus recording rules for ones used in many dashboards:
```yaml
# In Prometheus rules
- record: service:http_request_rate:5m
  expr: sum by (service, status) (rate(http_requests_total[5m]))
```
Dashboard query becomes `service:http_request_rate:5m` — pre-computed, instant.

**Query timeout:** set per-datasource (Prometheus default is 30s, Loki 60s). Long timeouts make slow dashboards feel hung; cut to 15s and let the user retry with a smaller range.

**Refresh rate:** dashboards refreshing every 5s with 20 panels = 240 queries/min. Most ops dashboards need 30s, debug dashboards need OFF (you want a frozen window).

**Mixed datasources:** the "Mixed" datasource lets one panel query Prom + Loki. It runs both in parallel — fine for small queries, terrible if Loki is slow. Use sparingly; prefer separate panels with shared variables.

**Loki query patterns:** logs are line-streams. Always include a `{label}` matcher first to scope; full-text search over 1B lines hangs.
```
{service="checkout", env="prod"} |= "ERROR" | json | line_format "{{.message}}"
```

**Panel re-use vs duplication:** Grafana library panels (saved as reusable) update everywhere on edit. Use for shared "service health" mini-panels across many dashboards.

## Anti-patterns

- **Per-team dashboard sprawl with 80% overlap.** Each team copies the platform dashboard and edits 5 panels. Use library panels and a shared base dashboard with team-specific extensions.
- **Gauges for autoscaled resources.** "75% of CPU" looks fine until the autoscaler doubles the fleet — now 75% is half what it was. Use stat with thresholds.
- **No exemplars wired despite Tempo being installed.** The single highest-leverage Grafana feature, skipped because nobody set up `exemplarTraceIdDestinations`.
- **Variable dropdowns with 10,000 entries.** Engineers can't find their service. Bound to top-N or use a search-as-you-type.
- **`up` queries to populate every variable.** Cardinality bomb on large fleets. Use a more specific recording rule.
- **Stacked time series for top errors.** With 30 errors stacked, nothing is readable. Use a table sorted by current value.
- **Dashboards built in UI, never exported.** UI edits drift; one engineer's local edits diverge from prod. Provision via JSON in git or Terraform.
- **Refresh rate 5s on dashboards nobody watches live.** Every viewer's browser hammers Prometheus. Default to 30s; only ops dashboards need 5s.
- **No panel descriptions.** New on-call has no idea what the metric means. Description is a 30-second writeup, saves hours.
- **Drill-down links that lose time range.** Clicking from RED dashboard to logs jumps to "last 6h" — wrong. Pass `${__from}` and `${__to}` in the link.
- **Mixed-datasource panels with one slow side.** The whole panel waits on the slow datasource. Separate panels with shared variables.
- **Alerts defined in Grafana but using a different query than the panel.** Panel shows green, alert fires. Always alert on the same query the panel renders.

## Exit Criteria

- Every T0 service has a RED + Four Golden Signals dashboard provisioned via JSON in git
- Every T0 service has an SLO / error-budget dashboard linked from RED dashboard
- Capacity dashboards use USE method consistently
- Customer journey dashboards exist for top 3 product flows
- Variables follow cascading or bounded-cardinality patterns; no unbounded multi-value `Include All`
- Exemplars wired from Prometheus histograms to Tempo for at least the latency panels in T0/T1 services
- Drill-down links connect: RED → Logs (Loki, scoped) → Traces (Tempo, scoped) → Profile (Pyroscope, scoped)
- Performance baseline: every T0 dashboard loads in <5s, no panel >2s
- Stale dashboard pruning: ≥40% reduction in dashboard count, no impact on actually-used dashboards (verified via Grafana usage analytics)
- Library panels in use for shared mini-panels across dashboards
- All dashboards provisioned via Grafana provisioning YAML or Terraform; no UI-only dashboards in prod
- Panel descriptions present on every panel of T0 dashboards
- Grafana unified alerting rules tied to the same queries as their corresponding panels
- Monthly recurring audit scheduled with a named owner per team
- Documented runbook for "how to add a new service dashboard" referencing the layout templates
- Dashboard JSON snapshots versioned in git with PR-based review
