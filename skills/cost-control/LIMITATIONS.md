# Cost Control System — Known Limitations

This document outlines the current limitations and known issues with the Cost Control System.

---

## 1. Clock Skew Between System and API

### Problem
Cost tracking relies on system time. If your system clock is out of sync with the API provider's billing system, costs may be attributed to the wrong time window.

### Impact
- Daily reset may happen at wrong time (if UTC offset is incorrect)
- 15-minute rolling windows may not align with API billing windows
- Could trigger emergency mode prematurely or miss threshold breaches

### Workarounds
- **Sync system clock:** Use NTP (`ntpdate`, `chrony`, or `systemd-timesyncd`)
- **Force UTC:** Ensure system timezone is UTC or configured correctly
- **Verify alignment:** Compare cost log timestamps with API billing dashboard

### Future Fix
Add timezone validation and warnings on startup

---

## 2. Delayed Cost Reporting

### Problem
Some APIs don't provide real-time usage data. For example:
- AWS: Costs update hourly or daily, not per-request
- OpenAI: Usage quotas update every ~60 seconds
- Stripe: Billing data lags by minutes

### Impact
- Cost tracker may underestimate spend in real-time
- Actual bill could exceed tracker's totals
- Emergency mode may trigger too late

### Workarounds
- **Conservative thresholds:** Set emergency threshold below actual budget (e.g., $5 emergency for $10 budget)
- **Estimate conservatively:** Overestimate cost per call rather than underestimate
- **Reconcile daily:** Compare tracker totals with API dashboard

### Current Status
Tracker only knows what you tell it via `record_call()`. It doesn't fetch usage from API directly.

---

## 3. Watchdog Reliability (Cron Timing Jitter)

### Problem
External watchdog runs via cron every 2 minutes. Cron timing isn't guaranteed:
- May run late if system is under load
- Won't run if cron daemon is stopped
- May miss threshold breach between checks

### Impact
- Up to 2-minute delay before watchdog detects runaway cost
- In extreme cases, could burn $0.50-$1.00 during delay

### Workarounds
- **Reduce cron interval:** Run every 1 minute instead of 2 (trade-off: more overhead)
- **Monitor cron health:** Alert if watchdog log hasn't updated in 5+ minutes
- **Lower watchdog thresholds:** Set kill threshold closer to emergency threshold

### Future Fix
Replace cron with systemd timer (more reliable scheduling) or built-in thread

---

## 4. Multi-Process Coordination

### Problem
Cost tracker uses local file-based state. Multiple processes accessing the same state file will have inconsistent cost totals.

### Impact
- Cannot track costs across multiple processes accurately
- Race conditions on state file writes
- Daily totals may be undercounted

### Workarounds
- **Single process only:** Run one tracker instance per application
- **Separate state files:** Use different `state_dir` per process (but can't aggregate)
- **External aggregation:** Write costs to shared database, aggregate separately

### Future Fix
Redis or database backend for distributed cost tracking

---

## 5. No Built-In Retry Logic

### Problem
If emergency flag file write fails (disk full, permissions issue), emergency mode may not trigger.

### Impact
- Process continues making expensive API calls despite breaching threshold
- No failsafe if state persistence fails

### Workarounds
- **Monitor disk space:** Alert if state directory partition is >80% full
- **Verify file permissions:** Ensure tracker has write access to state directory
- **Manual kill switch:** Use `kill_switch.py` as backup

### Current Status
Logs errors but doesn't retry or raise exceptions

---

## 6. No Cost Reconciliation

### Problem
Tracker doesn't verify its cost totals against actual API billing.

### Impact
- Tracker may undercount if `record_call()` is missed due to bugs
- Tracker may overcount if calls are retried but only billed once
- No way to detect drift between tracker and actual bill

### Workarounds
- **Daily reconciliation:** Compare `cost_daily` with API dashboard
- **Alert on large discrepancies:** Manual script to compare tracker vs. API
- **Audit trail:** Review `cost_log.jsonl` against API usage logs

### Future Fix
Built-in reconciliation with API billing data

---

## 7. Single-Currency Only

### Problem
Tracker assumes all costs are in one currency (e.g., USD). Cannot track mixed currencies.

### Impact
- Cannot use for multi-region deployments with local currency pricing
- Cannot compare costs across different APIs with different currencies

### Workarounds
- **Convert to USD:** Manually convert costs to USD before calling `record_call()`
- **Separate trackers:** One tracker per currency, manual aggregation

### Future Fix
Multi-currency support with exchange rate handling

---

## 8. No Built-In Logging

### Problem
Cost tracker uses `print()` for logging. Not configurable, no log levels, no rotation.

### Impact
- Limited integration with existing logging frameworks
- No control over verbosity
- Logs mix with stdout

### Workarounds
- **Override `_log()`:** Subclass `CostTracker` and replace `_log()` with your logger

### Example Override
```python
import logging

class MyTracker(CostTracker):
    def _log(self, message: str):
        logging.info(f"[CostTracker] {message}")
```

### Future Fix
Configurable logger (pass `logging.Logger` instance)

---

## 9. No Real-Time Streaming Metrics

### Problem
Cost stats are only available via polling (`get_stats()`). No real-time push notifications.

### Impact
- Cannot integrate with monitoring tools (Prometheus, Grafana, Datadog)
- No real-time dashboards

### Workarounds
- **Periodic export:** Poll `get_stats()` every 60s, push to monitoring system
- **Custom integration:** Modify `_save_state()` to also push to metrics API

### Future Fix
Built-in Prometheus exporter or StatsD integration

---

## 10. Emergency Recovery Requires Manual Intervention

### Problem
Once emergency mode is triggered, it **cannot** auto-recover. Manual intervention required.

### Impact
- If emergency was false alarm (e.g., one-time spike), system stays paused until operator intervenes
- Requires human in the loop to clear emergency flag

### Workarounds
- **Alerting:** Ensure alert callback notifies operator immediately
- **Automatic escalation:** If emergency flag exists for >1 hour, send escalation alert

### Design Decision
This is **intentional**. Emergency mode means something went wrong. Auto-recovery could mask a serious issue (e.g., infinite loop). Manual review ensures root cause is understood before resuming.

---

## 11. Watchdog PID File Assumption

### Problem
External watchdog assumes PID file exists at `state/app.pid`. If your app doesn't create this file, watchdog can't kill the process.

### Impact
- Tier 3 (kill switch) won't work without PID file
- Watchdog will detect threshold breach but can't stop the process

### Workarounds
- **Create PID file:** Write `os.getpid()` to `state/app.pid` on startup
- **Modify watchdog:** Update `PID_FILE` path in `cost_watchdog.py`
- **Use process name:** Modify watchdog to find process by name instead of PID

### Example PID File Creation
```python
import os

pid = os.getpid()
with open("state/app.pid", "w") as f:
    f.write(str(pid))
```

---

## 12. No Support for Prepaid Credits

### Problem
Tracker counts costs but doesn't know about prepaid credits or quotas.

### Impact
- Cannot warn "80% of quota used"
- Cannot prevent exceeding prepaid credit limit
- Only tracks absolute cost, not remaining balance

### Workarounds
- **Calculate remaining:** Manually track `quota_total - tracker.cost_daily`
- **Threshold adjustment:** Set `cost_daily_cap` = remaining quota
- **External monitoring:** Use API provider's quota alerts

### Future Fix
Built-in quota tracking with remaining balance

---

## 13. Performance with High-Frequency APIs

### Problem
Recording costs is O(1), but rolling window calculation is O(N) where N = calls in window.

### Impact
- For very high-frequency APIs (1000+ calls/min), cost calculation may lag
- Threshold checks may add latency to API call path

### Workarounds
- **Async recording:** Offload `record_call()` to background thread/queue
- **Sample recording:** Only record every Nth call (trade-off: less accurate)
- **Optimize window:** Reduce `_calls.maxlen` from 5000 to 1000

### Current Status
Not optimized for >100 calls/second

---

## 14. No Built-In Dashboard

### Problem
Cost Control is code-only. No web UI, no visualization, no dashboard.

### Impact
- Must read state file or logs to see current costs
- No real-time monitoring view
- Not accessible to non-technical users

### Workarounds
- **Custom dashboard:** Build web UI that reads `state/cost_tracker.json`
- **CLI tool:** Write script to query tracker state
- **Log parsing:** Parse logs for monitoring

### Future Fix
Built-in web dashboard (Flask/FastAPI)

---

## 15. External Watchdog Doesn't Auto-Start

### Problem
External watchdog must be deployed via cron manually. Not integrated into application.

### Impact
- Forgot to deploy watchdog? No Tier 3 protection.
- Cron not running on dev machine? No watchdog.

### Workarounds
- **Deployment checklist:** Add "deploy watchdog cron" to production checklist
- **Health check:** Monitor watchdog log, alert if not updating
- **Systemd integration:** Use systemd timer instead of cron (more reliable)

### Future Fix
Built-in watchdog thread (no external process needed)

---

## Summary Table

| Limitation | Severity | Workaround Available? | Planned Fix |
|------------|----------|----------------------|-------------|
| Clock skew | Medium | Yes (NTP sync) | Timezone validation |
| Delayed cost reporting | Medium | Yes (conservative thresholds) | API reconciliation |
| Watchdog timing jitter | Low | Yes (reduce interval) | Systemd timer |
| Multi-process | Medium | No (single process only) | Redis backend |
| No retry logic | Low | Yes (monitor disk space) | Built-in retry |
| No reconciliation | Medium | Yes (manual comparison) | API integration |
| Single-currency | Low | Yes (convert to USD) | Multi-currency |
| No logging | Low | Yes (override `_log()`) | Configurable logger |
| No streaming metrics | Medium | Yes (poll + push) | Prometheus exporter |
| Manual recovery | N/A | Intentional design | None (by design) |
| PID file assumption | Low | Yes (create PID file) | Process name fallback |
| No prepaid credits | Medium | Yes (calculate remaining) | Quota tracking |
| High-frequency perf | Low | Yes (async recording) | Optimize window calc |
| No dashboard | Low | Yes (custom UI) | Built-in dashboard |
| Watchdog not auto-start | Medium | Yes (deployment checklist) | Built-in thread |

---

## Contributing Fixes

If you have solutions to any of these limitations, we'd love to hear from you!

- 🐛 **Report issues:** GitHub issues
- 💡 **Suggest improvements:** Discord or Twitter
- 🔧 **Submit PRs:** We review everything

---

## Philosophy

Cost Control is **production-ready for most use cases**, but not perfect. We document limitations honestly so you can make informed decisions.

**Use it if:**
- You need reliable cost protection for expensive APIs
- You can work within the limitations (or implement workarounds)
- You value safety over feature completeness

**Don't use it if:**
- You need multi-process distributed cost tracking (use Redis/database)
- You need real-time reconciliation with API billing (use native SDK quotas)
- You need sub-second protection for 1000+ calls/second (optimize or sample)

---

**Questions? Found a limitation we missed?**

💬 Discord: https://discord.com/invite/clawd  
🐦 Twitter: https://x.com/TheShadowyRose
