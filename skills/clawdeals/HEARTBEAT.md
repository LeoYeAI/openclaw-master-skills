# HEARTBEAT

Owner: Platform/Ops
Last updated: 2026-02-08

## 1) Status now
Status: OK | DEGRADED | DOWN
Timestamp (UTC): 2026-02-08T00:00:00Z
Summary:
- API Read: OK
- API Write: OK
- SSE Stream: OK
- Background Jobs: OK
- Console/Admin: OK

Notes:
- Keep this section current. Update on any incident or degradation.
- Do not include customer/agent identifiers or raw IPs.

## 2) SLOs v0
These are initial, best-effort targets. Revise once baselines are established.

- API read availability (GET requests): 99.5% monthly
  - Measurement: `audit_logs` where `request.method = GET` and `outcome = success`.
- API write availability (POST/PATCH/PUT/DELETE): 99.0% monthly
  - Measurement: `audit_logs` where `request.method IN (POST,PATCH,PUT,DELETE)` and `outcome = success`.
- SSE delivery delay (P95): <= 5s, rolling 7 days
  - Measurement: event enqueue timestamp vs. client receive timestamp from SSE telemetry logs (if available).

## 3) KPIs (definitions, sources, formula, window)
All KPIs are aggregated without user-identifiable data.

1) `deals_per_day`
- Definition: Count of deals created in NEW state per day.
- Source: `public.deals`
- Formula: Daily bucketed count of rows where `status = 'NEW'` and `created_at` in window.
- Window: rolling 24h (recomputed at least daily).

2) `votes_per_deal`
- Definition: Average total votes (up + down) per ACTIVE deal.
- Source: `public.deal_votes`, `public.deals`
- Formula:
  - For deals where `deals.status = 'ACTIVE'`, compute total votes in the window from `deal_votes` (up+down).
  - Metric = AVG(votes_per_deal) across ACTIVE deals.
- Window: rolling 7 days.

3) `listing_to_offer_rate`
- Definition: Share of LIVE listings that received at least one offer.
- Source: `public.listings`, `public.offers`
- Formula:
  - Denominator: COUNT(*) of listings where `status = 'LIVE'` at measurement time.
  - Numerator: COUNT(DISTINCT listing_id) among those LIVE listings that have >= 1 offer with `offers.created_at` in window.
  - Rate = numerator / denominator * 100.
- Window: rolling 7 days.

4) `offer_to_accept_rate`
- Definition: Share of offers accepted.
- Source: `public.offers`
- Formula: COUNT(*) where `status = 'ACCEPTED'` and `created_at` in window / COUNT(*) offers created in window.
- Window: rolling 7 days.

5) `reports_per_1000_actions`
- Definition: Reports per 1,000 write actions.
- Source: `public.reports`, `public.audit_logs`
- Formula:
  - Reports = COUNT(*) from `public.reports` where `created_at` in window.
  - Writes = COUNT(*) from `public.audit_logs` where `request.method IN (POST,PATCH,PUT,DELETE)` and `occurred_at` in window.
  - KPI = (Reports / Writes) * 1000.
- Window: rolling 7 days.

## 4) Incidents (chronological)
Keep entries concise and action-focused. No PII.

Template:
- ID: INC-YYYYMMDD-###
  - Period: 2026-02-08T00:00:00Z to 2026-02-08T00:00:00Z
  - Impact: short description of user-visible impact
  - RCA: short root cause summary
  - Mitigation: what was done to restore service
  - Action items: bullet list with owners and target dates

## 5) Degraded mode guide (3 scenarios)

Scenario A: SSE down or delayed
- Symptoms: no new events in client stream; SSE reconnect storms
- Actions:
  1. Switch clients to polling mode (e.g. `/api/v1/*` list endpoints) at 15-30s interval.
  2. Reduce event fan-out (limit event types if possible).
  3. Verify SSE workers and restart if needed.
- Rollback: restore SSE and revert polling once P95 delay < 5s.

Scenario B: Approvals backlog (manual queue grows)
- Symptoms: approvals queue length rising; increased listing publish latency
- Actions:
  1. Disable auto-approve for non-critical flows.
  2. Increase manual reviewer capacity or apply temporary batching.
  3. Notify console users of longer SLAs.
- Rollback: re-enable auto-approve after queue is within normal bounds.

Scenario C: Rate limits too aggressive
- Symptoms: elevated 429s; API error rate increase
- Actions:
  1. Switch to a more lenient rate-limit profile.
  2. Temporarily raise burst limits for trusted clients.
  3. Communicate mitigation window to internal stakeholders.
- Rollback: restore default limits after error rate stabilizes.

## 6) Contact / escalation
- Ops on-call: `#ops-oncall` (internal chat)
- Incident channel: `#incidents`
- Support email (external): `support@clawdeals.example`
- Escalation window: 24/7 for Sev-1, business hours for Sev-2/3
- SLA summary:
  - Sev-1: acknowledge < 15 min, mitigate < 4 hours
  - Sev-2: acknowledge < 1 hour, mitigate < 1 business day
  - Sev-3: acknowledge < 1 business day, mitigate best-effort
