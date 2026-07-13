#!/usr/bin/env python3
"""
revenue_tracker.py — Revenue Tracker
Veritas Corporate / OpenClaw Agent

Live revenue tracking with visual dashboards, HTML reports,
milestone alerts, and learning logs.

Operations:
  init       → initialize revenue directory structure
  record     → log a revenue event
  dashboard  → ASCII visual dashboard
  report     → generate HTML report (--period week|month|quarter|all)
  goal       → set or list financial goals
  asset      → track non-revenue assets
  learn      → log a revenue learning
  stats      → quick stats summary
  milestones → show all milestones and which are reached
  anomalies  → check for anomalies across all streams

Usage:
  python3 revenue_tracker.py --init
  python3 revenue_tracker.py record --stream subscriptions --amount 97 --description "New subscriber"
  python3 revenue_tracker.py dashboard
  python3 revenue_tracker.py report --period week
  python3 revenue_tracker.py report --period month --format html
  python3 revenue_tracker.py goal --set "mrr_10k" --target 10000 --deadline "2026-06-30"
  python3 revenue_tracker.py goal --list
  python3 revenue_tracker.py asset --action add --name "Binance Capital" --value 500
  python3 revenue_tracker.py learn --category acquisition --insight "14% reply rate CTOs" --impact high
  python3 revenue_tracker.py stats
  python3 revenue_tracker.py anomalies
"""

import json
import os
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List
import math


# ─── CONFIG ────────────────────────────────────────────────────────────────
REVENUE_ROOT = Path("/workspace/revenue")
DATA_DIR     = REVENUE_ROOT / "data"
REPORTS_DIR  = REVENUE_ROOT / "reports"
SCRIPTS_DIR  = REVENUE_ROOT / "scripts"
AUDIT_LOG    = Path("/workspace/AUDIT.md")
ERRORS_LOG   = Path("/workspace/.learnings/ERRORS.md")
LEARNINGS_LOG = Path("/workspace/.learnings/LEARNINGS.md")

STATE_FILE     = DATA_DIR / "revenue_state.json"
EVENTS_FILE    = DATA_DIR / "events.jsonl"
ASSETS_FILE    = DATA_DIR / "assets.json"
GOALS_FILE     = DATA_DIR / "goals.json"
LEARNINGS_FILE = DATA_DIR / "learnings.jsonl"

STREAMS = ["subscriptions", "trading", "content", "services", "affiliate"]
EVENT_TYPES = ["new_mrr", "churn", "expansion", "one_time", "trade_win",
               "trade_loss", "refund", "affiliate_commission"]

# MRR milestones in euros
MRR_MILESTONES = [100, 500, 1_000, 2_000, 5_000, 10_000,
                  20_000, 50_000, 100_000, 500_000, 1_000_000]

CHART_WIDTH = 40


# ─── HELPERS ───────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def today_str() -> str:
    return date.today().isoformat()

def audit(msg: str):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{now_iso()}] REVENUE: {msg}")

def log_error(msg: str):
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{now_iso()}] REVENUE ERROR: {msg}")

def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_error(f"JSONDecodeError {path}: {e}")
        return None

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events

def load_state() -> dict:
    state = load_json(STATE_FILE)
    if state is None:
        state = {
            "mrr": 0.0,
            "arr": 0.0,
            "total_revenue_all_time": 0.0,
            "revenue_by_stream": {s: 0.0 for s in STREAMS},
            "mrr_by_stream": {s: 0.0 for s in STREAMS},
            "customers": 0,
            "milestones_reached": [],
            "last_updated": today_str(),
            "week_revenue": 0.0,
            "month_revenue": 0.0,
            "prev_month_mrr": 0.0,
        }
    return state

def save_state(state: dict):
    state["last_updated"] = today_str()
    state["arr"] = round(state["mrr"] * 12, 2)
    save_json(STATE_FILE, state)


# ─── PROGRESS BAR & SPARKLINE ──────────────────────────────────────────────
def progress_bar(value: float, target: float, width: int = 20) -> str:
    if target <= 0:
        return "░" * width
    pct = min(value / target, 1.0)
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar

def sparkline(values: List[float]) -> str:
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    mn, mx = min(values), max(values)
    rng = mx - mn
    if rng == 0:
        return blocks[3] * len(values)
    return "".join(blocks[int((v - mn) / rng * 7)] for v in values)

def mini_chart(values: List[float], labels: List[str] = None,
               title: str = "", height: int = 6, width: int = 50) -> List[str]:
    """Generate a simple ASCII line chart."""
    if not values or all(v == 0 for v in values):
        return [f"  {title}: (no data)"]

    mn = 0
    mx = max(values) * 1.1 if max(values) > 0 else 1
    rows = []

    for row in range(height, -1, -1):
        threshold = mn + (mx - mn) * row / height
        line = f"  {threshold:>5.0f} ┤"
        prev_above = None
        for i, v in enumerate(values):
            above = v >= threshold
            if prev_above is None:
                line += "─" if above else " "
            elif above and prev_above:
                line += "─"
            elif above and not prev_above:
                line += "╭"
            elif not above and prev_above:
                line += "╯"
            else:
                line += " "
            prev_above = above
        rows.append(line)

    # X axis
    rows.append("        " + "┴" + "─" * len(values))
    if labels:
        label_line = "        "
        step = max(1, len(labels) // 6)
        for i, lbl in enumerate(labels):
            if i % step == 0:
                label_line += lbl[:4].center(step)
        rows.append(label_line)

    return rows


# ─── OPERATIONS ────────────────────────────────────────────────────────────

def op_init():
    for d in [DATA_DIR, REPORTS_DIR, SCRIPTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    state = load_state()
    save_state(state)

    if not GOALS_FILE.exists():
        save_json(GOALS_FILE, {"goals": []})
    if not ASSETS_FILE.exists():
        save_json(ASSETS_FILE, {"assets": [], "total_eur": 0})

    audit("Revenue tracker initialized")
    print("✅ Revenue tracker initialized")
    print(f"   Root: {REVENUE_ROOT}")
    print(f"   ✓ data/ (state, events, assets, goals, learnings)")
    print(f"   ✓ reports/")


def op_record(stream: str, amount: float, currency: str,
              description: str, event_type: str,
              client_id: Optional[str] = None):
    if stream not in STREAMS:
        print(f"❌ Unknown stream: {stream}. Valid: {STREAMS}")
        sys.exit(1)

    # Convert to EUR (simplified — extend with forex if needed)
    amount_eur = amount
    if currency.upper() == "USDT":
        amount_eur = amount  # treat as EUR equivalent for now

    event = {
        "id":          f"{stream}-{now_iso().replace(':', '-')}",
        "date":        today_str(),
        "timestamp":   now_iso(),
        "stream":      stream,
        "type":        event_type,
        "amount_eur":  round(amount_eur, 2),
        "currency":    currency.upper(),
        "description": description,
        "client_id":   client_id,
    }

    append_jsonl(EVENTS_FILE, event)

    # Update state
    state = load_state()

    # Determine MRR impact
    mrr_impact = 0.0
    is_one_time = False

    if event_type == "new_mrr":
        mrr_impact = amount_eur
        state["customers"] += 1
    elif event_type == "expansion":
        mrr_impact = amount_eur
    elif event_type == "churn":
        mrr_impact = -amount_eur
        state["customers"] = max(0, state["customers"] - 1)
    elif event_type in ("one_time", "trade_win", "affiliate_commission"):
        is_one_time = True
    elif event_type == "trade_loss":
        is_one_time = True
        amount_eur = -abs(amount_eur)
    elif event_type == "refund":
        is_one_time = True
        amount_eur = -abs(amount_eur)

    if mrr_impact != 0:
        state["mrr"] = round(max(0, state["mrr"] + mrr_impact), 2)
        state["mrr_by_stream"][stream] = round(
            max(0, state["mrr_by_stream"].get(stream, 0) + mrr_impact), 2
        )

    if amount_eur > 0:
        state["total_revenue_all_time"] = round(
            state["total_revenue_all_time"] + amount_eur, 2
        )
        state["revenue_by_stream"][stream] = round(
            state.get("revenue_by_stream", {}).get(stream, 0) + amount_eur, 2
        )

    # Check milestones
    new_milestones = _check_milestones(state)

    save_state(state)
    audit(f"Revenue recorded: {stream}/{event_type} €{amount_eur} — {description}")

    print(f"✅ Recorded: €{abs(amount_eur):.2f} [{stream}/{event_type}]")
    print(f"   MRR now: €{state['mrr']:,.2f}")

    if new_milestones:
        for ms in new_milestones:
            print(f"\n   🎯 MILESTONE: {ms}")

    # Auto-update dashboard after every revenue event
    _auto_update_dashboard(state, event)

    return event, new_milestones


def _auto_update_dashboard(state: dict, event: dict):
    """
    Auto-update tracking dashboard after every revenue event.
    Priority order:
      1. Google Sheets (via gog — agent's Google Workspace integration)
      2. Notion (via virtual-desktop)
      3. HTML dashboard (local fallback — always works)

    This function outputs structured instructions the agent executes
    immediately after recording a revenue event.
    """
    mrr   = state["mrr"]
    arr   = mrr * 12
    total = state.get("total_revenue_all_time", 0)
    phase = _detect_phase(mrr)
    today = today_str()

    # ── ALWAYS: Update local HTML dashboard (fallback, always generated) ──
    _update_html_dashboard(state)

    # ── OUTPUT: Instructions for the agent to update external dashboards ──
    print(f"\n{'─'*56}")
    print(f"  📊 DASHBOARD UPDATE REQUIRED")
    print(f"{'─'*56}")
    print(f"  Event:  {event['stream']}/{event['type']} +€{abs(event['amount_eur']):.2f}")
    print(f"  MRR:    €{mrr:,.2f}   ARR: €{arr:,.2f}")
    print(f"  Phase:  {phase['number']} — {phase['name']}")
    print(f"  Total:  €{total:,.2f} all time")
    print(f"{'─'*56}")
    print(f"\n  AGENT — execute in this order:")
    print(f"\n  1️⃣  GOOGLE SHEETS (preferred)")
    print(f"     Skill: wesley-web-operator (gog)")
    print(f"     Sheet: 'Veritas Revenue Tracker'")
    print(f"     Action: append to 'Events' tab:")
    print(f"       Date={today} | Stream={event['stream']} | Type={event['type']}")
    print(f"       Amount=€{abs(event['amount_eur']):.2f} | Desc={event['description']}")
    print(f"       MRR={mrr} | Total={total}")
    print(f"     Action: update 'Dashboard' tab cells:")
    print(f"       B2=€{mrr:,.2f} (MRR)")
    print(f"       B3=€{arr:,.2f} (ARR)")
    print(f"       B4=€{total:,.2f} (All time)")
    print(f"       B5={state.get('customers',0)} (Customers)")
    print(f"       B6=Phase {phase['number']} (Phase)")
    print(f"\n  2️⃣  NOTION (fallback if Sheets unavailable)")
    print(f"     Skill: virtual-desktop")
    print(f"     Database: 'Revenue Tracker'")
    print(f"     Action: create new entry with same fields as above")
    print(f"     Action: update Summary page KPIs")
    print(f"\n  3️⃣  HTML DASHBOARD (always available — local)")
    print(f"     File: {REPORTS_DIR}/dashboard.html")
    print(f"     ✅ Already updated automatically")
    print(f"{'─'*56}")


def _update_html_dashboard(state: dict):
    """Generate/update local HTML dashboard — always runs, no external deps."""
    mrr    = state["mrr"]
    arr    = mrr * 12
    total  = state.get("total_revenue_all_time", 0)
    phase  = _detect_phase(mrr)
    cust   = state.get("customers", 0)
    today  = today_str()

    # MRR by stream bars
    stream_html = ""
    streams_data = state.get("mrr_by_stream", {})
    max_v = max(streams_data.values()) if any(streams_data.values()) else 1
    colors = {
        "subscriptions": "#22c55e", "trading": "#3b82f6",
        "content": "#f59e0b", "services": "#8b5cf6", "affiliate": "#06b6d4"
    }
    for s, v in sorted(streams_data.items(), key=lambda x: -x[1]):
        if v <= 0:
            continue
        pct = v / max_v * 100
        color = colors.get(s, "#6b7280")
        stream_html += f"""
        <div class="bar-row">
          <span class="bar-label">{s}</span>
          <div class="bar-bg">
            <div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
          </div>
          <span class="bar-val">€{v:,.0f}/mo</span>
        </div>"""

    # Goal progress bars
    goals_data = load_json(GOALS_FILE) or {"goals": []}
    goals_html = ""
    for g in goals_data.get("goals", []):
        if g.get("status") != "active":
            continue
        target = g.get("target", 1)
        current = mrr if g.get("metric") == "mrr" else total
        pct = min(current / target * 100, 100) if target > 0 else 0
        goals_html += f"""
        <div class="goal-row">
          <div class="goal-name">{g.get('name','—')}
            <span class="goal-pct">{pct:.1f}%</span>
          </div>
          <div class="goal-bg">
            <div class="goal-fill" style="width:{pct:.1f}%"></div>
          </div>
        </div>"""

    if not goals_html:
        for t, lbl in [(10000,"€10K MRR"),(50000,"€50K MRR"),(1000000,"€1M ARR")]:
            pct = min(mrr / t * 100, 100)
            goals_html += f"""
        <div class="goal-row">
          <div class="goal-name">{lbl}
            <span class="goal-pct">{pct:.1f}%</span>
          </div>
          <div class="goal-bg">
            <div class="goal-fill" style="width:{pct:.1f}%"></div>
          </div>
        </div>"""

    # Recent events
    events = read_jsonl(EVENTS_FILE)[-10:]
    events_html = ""
    for e in reversed(events):
        a = e.get("amount_eur", 0)
        color = "#22c55e" if a >= 0 else "#ef4444"
        sign = "+" if a >= 0 else ""
        events_html += f"""
        <tr>
          <td>{e.get('date','—')}</td>
          <td>{e.get('stream','—')}</td>
          <td>{e.get('type','—')}</td>
          <td style="color:{color};font-weight:600">{sign}€{abs(a):,.2f}</td>
          <td class="muted">{e.get('description','—')[:40]}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>Revenue Dashboard — Veritas Corporate</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#0a0a0a;color:#e0e0e0;padding:24px}}
  .container{{max-width:960px;margin:0 auto}}
  h1{{font-size:1.4rem;color:#22c55e;margin-bottom:4px}}
  .subtitle{{color:#555;font-size:0.8rem;margin-bottom:24px}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
             gap:12px;margin-bottom:24px}}
  .kpi{{background:#111;border:1px solid #1e1e1e;border-radius:8px;padding:16px}}
  .kpi-label{{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;
              color:#555;margin-bottom:6px}}
  .kpi-value{{font-size:1.6rem;font-weight:700;color:#22c55e}}
  .kpi-sub{{font-size:0.75rem;color:#666;margin-top:4px}}
  .card{{background:#111;border:1px solid #1e1e1e;border-radius:8px;
         padding:20px;margin-bottom:16px}}
  .card-title{{font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;
               color:#555;margin-bottom:16px}}
  .bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
  .bar-label{{width:110px;font-size:0.82rem;color:#ccc}}
  .bar-bg{{flex:1;background:#1e1e1e;border-radius:4px;height:18px;overflow:hidden}}
  .bar-fill{{height:100%;border-radius:4px;transition:width 0.4s}}
  .bar-val{{width:90px;text-align:right;font-size:0.82rem;color:#22c55e;font-weight:600}}
  .goal-row{{margin-bottom:12px}}
  .goal-name{{display:flex;justify-content:space-between;font-size:0.82rem;
              color:#ccc;margin-bottom:4px}}
  .goal-pct{{color:#22c55e}}
  .goal-bg{{background:#1e1e1e;border-radius:4px;height:14px;overflow:hidden}}
  .goal-fill{{background:linear-gradient(90deg,#22c55e,#86efac);
              height:100%;border-radius:4px;transition:width 0.4s}}
  table{{width:100%;border-collapse:collapse;font-size:0.82rem}}
  th{{text-align:left;color:#555;font-size:0.7rem;text-transform:uppercase;
      letter-spacing:1px;padding:8px 6px;border-bottom:1px solid #1e1e1e}}
  td{{padding:8px 6px;border-bottom:1px solid #141414;color:#ccc}}
  .muted{{color:#555}}
  .phase-badge{{display:inline-block;background:#0d2818;color:#22c55e;
                border:1px solid #22c55e;border-radius:4px;
                padding:3px 10px;font-size:0.75rem}}
  .footer{{text-align:center;color:#333;font-size:0.7rem;margin-top:24px}}
</style>
</head>
<body>
<div class="container">
  <h1>📈 Revenue Dashboard</h1>
  <div class="subtitle">Veritas Corporate · Updated {today} · Auto-refreshes every 60s</div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">MRR</div>
      <div class="kpi-value">€{mrr:,.0f}</div>
      <div class="kpi-sub">ARR: €{arr:,.0f}</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">All Time</div>
      <div class="kpi-value">€{total:,.0f}</div>
      <div class="kpi-sub">Since launch</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Customers</div>
      <div class="kpi-value">{cust}</div>
      <div class="kpi-sub">Active subscribers</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Phase</div>
      <div class="kpi-value" style="font-size:1.2rem">{phase['number']}</div>
      <div class="kpi-sub">{phase['name']}</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">MRR by Stream</div>
    {stream_html if stream_html else '<p class="muted">No stream data yet</p>'}
  </div>

  <div class="card">
    <div class="card-title">Goal Progress</div>
    {goals_html}
  </div>

  <div class="card">
    <div class="card-title">Recent Events</div>
    <table>
      <thead><tr>
        <th>Date</th><th>Stream</th><th>Type</th>
        <th>Amount</th><th>Description</th>
      </tr></thead>
      <tbody>{events_html}</tbody>
    </table>
  </div>

  <div class="footer">
    Veritas Corporate — Agent Revenue Tracker — {today}
  </div>
</div>
</body>
</html>"""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    dash_path = REPORTS_DIR / "dashboard.html"
    dash_path.write_text(html, encoding="utf-8")
    print(f"  ✅ HTML dashboard updated: {dash_path}")


def _check_milestones(state: dict) -> List[str]:
    new = []
    reached = state.get("milestones_reached", [])
    mrr = state["mrr"]

    for ms in MRR_MILESTONES:
        key = f"mrr_{ms}"
        if mrr >= ms and key not in reached:
            reached.append(key)
            new.append(f"€{ms:,} MRR reached! 🚀")

    # Customer milestones
    customers = state.get("customers", 0)
    for n in [1, 5, 10, 25, 50, 100]:
        key = f"customers_{n}"
        if customers >= n and key not in reached:
            reached.append(key)
            new.append(f"{n} paying customer{'s' if n > 1 else ''} reached!")

    state["milestones_reached"] = reached
    return new


def op_dashboard():
    state = load_state()
    events = read_jsonl(EVENTS_FILE)

    mrr  = state["mrr"]
    arr  = mrr * 12
    prev = state.get("prev_month_mrr", 0)
    growth_pct = ((mrr - prev) / prev * 100) if prev > 0 else 0
    growth_sign = "▲ +" if growth_pct >= 0 else "▼ "
    total = state.get("total_revenue_all_time", 0)

    # Revenue by stream this month
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    month_events = [e for e in events if e.get("date", "") >= month_start]
    stream_month = {s: 0.0 for s in STREAMS}
    for e in month_events:
        s = e.get("stream", "")
        if s in stream_month and e.get("amount_eur", 0) > 0:
            stream_month[s] += e["amount_eur"]
    month_total = sum(stream_month.values())

    # MRR weekly trend (last 8 weeks)
    weekly_mrr = _get_weekly_mrr(events, 8)

    # Goals
    goals_data = load_json(GOALS_FILE) or {"goals": []}
    goals = goals_data.get("goals", [])

    # Learnings (last 3)
    learnings = read_jsonl(LEARNINGS_FILE)[-3:] if LEARNINGS_FILE.exists() else []

    W = 64  # box width
    lines = []
    def box(text="", pad=True):
        if pad:
            lines.append(f"║  {text:<{W-4}}║")
        else:
            lines.append(text)

    lines.append("╔" + "═" * (W-2) + "╗")
    box(f"📈 REVENUE DASHBOARD — {today_str()}")
    lines.append("╠" + "═" * (W-2) + "╣")
    box(f"MRR      €{mrr:>10,.2f}  {growth_sign}{abs(growth_pct):.1f}% vs last month")
    box(f"ARR      €{arr:>10,.2f}")
    box(f"Total    €{total:>10,.2f}  (all time)")
    box(f"Customers: {state.get('customers', 0)}")

    # Phase
    phase = _detect_phase(mrr)
    box(f"Phase    {phase['number']} — {phase['name']}")
    lines.append("╠" + "═" * (W-2) + "╣")
    box("PROGRESS TOWARD GOALS")
    box()

    active_goals = [g for g in goals if g.get("status") == "active"]
    if active_goals:
        for g in active_goals[:4]:
            target   = g.get("target", 0)
            current  = mrr if g.get("metric") == "mrr" else total
            pct      = min(current / target * 100, 100) if target > 0 else 0
            bar      = progress_bar(current, target, 20)
            name     = g.get("name", "goal")[:18]
            deadline = g.get("deadline", "—")
            weeks_left = _weeks_until(deadline)
            box(f"  {name:<18} {bar} {pct:>5.1f}%  {weeks_left}")
    else:
        # Default goals based on phase
        for target in [10_000, 50_000, 1_000_000]:
            pct = min(mrr / target * 100, 100) if target > 0 else 0
            bar = progress_bar(mrr, target, 20)
            label = f"€{target//1000}K MRR" if target < 1_000_000 else "€1M ARR"
            box(f"  {label:<18} {bar} {pct:>5.1f}%")

    lines.append("╠" + "═" * (W-2) + "╣")
    box("REVENUE BY STREAM (this month)")
    box()
    if month_total > 0:
        for s in STREAMS:
            v   = stream_month.get(s, 0)
            pct = v / month_total * 100 if month_total > 0 else 0
            bar = progress_bar(v, month_total, 20)
            box(f"  {s:<14} {bar}  €{v:>7,.0f}  {pct:>5.1f}%")
    else:
        box("  No revenue recorded this month yet.")

    lines.append("╠" + "═" * (W-2) + "╣")
    box("MRR TREND (last 8 weeks)")
    box()
    if any(v > 0 for v in weekly_mrr):
        spark = sparkline(weekly_mrr)
        box(f"  {spark}  (€{min(v for v in weekly_mrr if v>=0):,.0f} → €{max(weekly_mrr):,.0f})")
        chart_lines = mini_chart(weekly_mrr, height=4, width=50)
        for cl in chart_lines:
            box(cl)
    else:
        box("  No weekly data yet.")

    lines.append("╠" + "═" * (W-2) + "╣")

    # Assets
    assets_data = load_json(ASSETS_FILE)
    if assets_data and assets_data.get("assets"):
        box("ASSETS")
        for a in assets_data["assets"][:3]:
            box(f"  {a.get('name','—'):<25} €{a.get('value_eur',0):>8,.2f}")
        lines.append("╠" + "═" * (W-2) + "╣")

    box("TOP LEARNINGS")
    if learnings:
        for l in learnings[-3:]:
            icon = "✅" if l.get("impact") == "high" else "⚠️ "
            box(f"  {icon} [{l.get('category','—')}] {l.get('insight','')[:45]}")
    else:
        box("  No learnings logged yet.")

    lines.append("╚" + "═" * (W-2) + "╝")

    print("\n".join(lines))
    return state


def _detect_phase(mrr: float) -> dict:
    phases = [
        (1, "Proof of Concept",   0,         10_000),
        (2, "Product-Market Fit", 10_000,    50_000),
        (3, "Scale",              50_000,   500_000),
        (4, "Expansion",         500_000, 10_000_000),
        (5, "Domination",     10_000_000, float("inf")),
    ]
    for n, name, mn, mx in phases:
        if mn <= mrr < mx:
            return {"number": n, "name": name, "target": mx}
    return {"number": 5, "name": "Domination", "target": float("inf")}


def _get_weekly_mrr(events: List[dict], n_weeks: int) -> List[float]:
    """Reconstruct MRR history week by week from events."""
    today = date.today()
    weeks = []
    running_mrr = 0.0

    # Collect all MRR-impacting events sorted by date
    mrr_events = sorted(
        [e for e in events if e.get("type") in ("new_mrr", "churn", "expansion")],
        key=lambda x: x.get("date", "")
    )

    for w in range(n_weeks - 1, -1, -1):
        week_end = today - timedelta(weeks=w)
        week_end_str = week_end.isoformat()
        mrr = 0.0
        for e in mrr_events:
            if e.get("date", "") <= week_end_str:
                t = e.get("type")
                a = e.get("amount_eur", 0)
                if t == "new_mrr":
                    mrr += a
                elif t == "churn":
                    mrr -= a
                elif t == "expansion":
                    mrr += a
        weeks.append(max(0, round(mrr, 2)))

    return weeks


def _weeks_until(deadline_str: str) -> str:
    try:
        d = date.fromisoformat(deadline_str)
        delta = (d - date.today()).days
        if delta < 0:
            return "OVERDUE"
        weeks = delta // 7
        return f"~{weeks}w left"
    except Exception:
        return ""


def op_report(period: str = "week", fmt: str = "console"):
    events = read_jsonl(EVENTS_FILE)
    state  = load_state()
    today  = date.today()

    # Date range
    if period == "week":
        start = (today - timedelta(days=7)).isoformat()
        label = "Last 7 Days"
    elif period == "month":
        start = today.replace(day=1).isoformat()
        label = f"Month of {today.strftime('%B %Y')}"
    elif period == "quarter":
        q_month = ((today.month - 1) // 3) * 3 + 1
        start = today.replace(month=q_month, day=1).isoformat()
        label = f"Q{(today.month-1)//3+1} {today.year}"
    else:
        start = "2000-01-01"
        label = "All Time"

    period_events = [e for e in events if e.get("date", "") >= start]

    # Aggregate
    revenue_total = sum(e.get("amount_eur", 0) for e in period_events
                        if e.get("amount_eur", 0) > 0)
    by_stream     = {s: 0.0 for s in STREAMS}
    by_type       = {}
    for e in period_events:
        s = e.get("stream", "unknown")
        t = e.get("type", "unknown")
        a = e.get("amount_eur", 0)
        if a > 0:
            by_stream[s] = round(by_stream.get(s, 0) + a, 2)
            by_type[t]   = round(by_type.get(t, 0) + a, 2)

    new_customers = sum(1 for e in period_events if e.get("type") == "new_mrr")
    churned       = sum(1 for e in period_events if e.get("type") == "churn")
    learnings     = read_jsonl(LEARNINGS_FILE)
    period_learnings = [l for l in learnings if l.get("date", "") >= start]

    if fmt == "html":
        html = _generate_html_report(
            label, period_events, revenue_total, by_stream,
            new_customers, churned, period_learnings, state
        )
        report_path = REPORTS_DIR / f"{today_str()}.html"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path.write_text(html, encoding="utf-8")
        print(f"✅ HTML report saved: {report_path}")
        return str(report_path)

    # Console report
    print(f"\n{'='*56}")
    print(f"  📊 REVENUE REPORT — {label}")
    print(f"{'='*56}")
    print(f"  Total revenue:   €{revenue_total:>10,.2f}")
    print(f"  New customers:   {new_customers}")
    print(f"  Churned:         {churned}")
    print(f"\n  By Stream:")
    for s, v in sorted(by_stream.items(), key=lambda x: -x[1]):
        if v > 0:
            pct = v / revenue_total * 100 if revenue_total > 0 else 0
            bar = progress_bar(v, revenue_total, 15)
            print(f"    {s:<16} {bar} €{v:>8,.2f}  {pct:.1f}%")
    print(f"\n  By Type:")
    for t, v in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {t:<20} €{v:>8,.2f}")
    if period_learnings:
        print(f"\n  Learnings ({len(period_learnings)}):")
        for l in period_learnings[:5]:
            icon = "✅" if l.get("impact") == "high" else "→ "
            print(f"    {icon} [{l.get('category')}] {l.get('insight','')[:50]}")
    print(f"{'='*56}")


def _generate_html_report(label, events, revenue_total, by_stream,
                          new_customers, churned, learnings, state) -> str:
    """Generate a visual HTML report with inline CSS charts."""
    today = today_str()
    mrr   = state.get("mrr", 0)
    arr   = mrr * 12
    total_all_time = state.get("total_revenue_all_time", 0)

    # Stream bars HTML
    stream_bars = ""
    max_v = max(by_stream.values()) if any(by_stream.values()) else 1
    for s, v in sorted(by_stream.items(), key=lambda x: -x[1]):
        if v <= 0:
            continue
        pct = v / max_v * 100
        color = {"subscriptions": "#4CAF50", "trading": "#2196F3",
                 "content": "#FF9800", "services": "#9C27B0",
                 "affiliate": "#00BCD4"}.get(s, "#607D8B")
        stream_bars += f"""
        <div class="bar-row">
          <span class="bar-label">{s}</span>
          <div class="bar-bg">
            <div class="bar-fill" style="width:{pct:.1f}%;background:{color}"></div>
          </div>
          <span class="bar-value">€{v:,.2f}</span>
        </div>"""

    # MRR trend sparkline as CSS bars
    weekly_mrr = _get_weekly_mrr(events, 8)
    max_w = max(weekly_mrr) if any(weekly_mrr) else 1
    trend_bars = ""
    for i, v in enumerate(weekly_mrr):
        h = int(v / max_w * 80) if max_w > 0 else 0
        trend_bars += f'<div class="spark-bar" style="height:{h}px" title="€{v:,.0f}"></div>'

    # Goals HTML
    goals_data = load_json(GOALS_FILE) or {"goals": []}
    goals_html = ""
    for g in goals_data.get("goals", []):
        if g.get("status") != "active":
            continue
        target = g.get("target", 1)
        current = mrr if g.get("metric") == "mrr" else total_all_time
        pct = min(current / target * 100, 100) if target > 0 else 0
        goals_html += f"""
        <div class="goal-row">
          <div class="goal-name">{g.get('name','goal')}</div>
          <div class="goal-bar-bg">
            <div class="goal-bar-fill" style="width:{pct:.1f}%"></div>
          </div>
          <div class="goal-pct">{pct:.1f}%</div>
        </div>"""

    if not goals_html:
        for target, label_g in [(10_000, "€10K MRR"), (50_000, "€50K MRR"), (1_000_000, "€1M ARR")]:
            pct = min(mrr / target * 100, 100)
            goals_html += f"""
        <div class="goal-row">
          <div class="goal-name">{label_g}</div>
          <div class="goal-bar-bg">
            <div class="goal-bar-fill" style="width:{pct:.1f}%"></div>
          </div>
          <div class="goal-pct">{pct:.1f}%</div>
        </div>"""

    # Learnings HTML
    learnings_html = ""
    for l in learnings[-5:]:
        icon = "✅" if l.get("impact") == "high" else "💡"
        learnings_html += f"""
        <div class="learning-row">
          <span class="learning-icon">{icon}</span>
          <span class="learning-cat">[{l.get('category','—')}]</span>
          <span class="learning-text">{l.get('insight','')}</span>
        </div>"""

    phase = _detect_phase(mrr)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Revenue Report — {label}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f0f0f; color: #e0e0e0; padding: 24px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; color: #4CAF50; margin-bottom: 4px; }}
  .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px;
           padding: 16px; }}
  .card-label {{ color: #888; font-size: 0.75rem; text-transform: uppercase;
                 letter-spacing: 1px; margin-bottom: 6px; }}
  .card-value {{ font-size: 1.8rem; font-weight: 700; color: #4CAF50; }}
  .card-sub {{ font-size: 0.8rem; color: #aaa; margin-top: 4px; }}
  .section {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px;
              padding: 20px; margin-bottom: 20px; }}
  .section-title {{ font-size: 0.85rem; color: #888; text-transform: uppercase;
                    letter-spacing: 1px; margin-bottom: 16px; }}
  .bar-row {{ display: flex; align-items: center; margin-bottom: 10px; gap: 10px; }}
  .bar-label {{ width: 120px; font-size: 0.85rem; color: #ccc; }}
  .bar-bg {{ flex: 1; background: #2a2a2a; border-radius: 4px; height: 20px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
  .bar-value {{ width: 90px; text-align: right; font-size: 0.85rem; color: #4CAF50; font-weight: 600; }}
  .spark {{ display: flex; align-items: flex-end; gap: 4px; height: 90px; padding: 8px 0; }}
  .spark-bar {{ flex: 1; background: #2196F3; border-radius: 2px 2px 0 0; min-height: 2px; }}
  .goal-row {{ margin-bottom: 12px; }}
  .goal-name {{ font-size: 0.85rem; color: #ccc; margin-bottom: 4px; }}
  .goal-bar-bg {{ background: #2a2a2a; border-radius: 4px; height: 16px; overflow: hidden; }}
  .goal-bar-fill {{ background: linear-gradient(90deg, #4CAF50, #8BC34A);
                   height: 100%; border-radius: 4px; transition: width 0.3s; }}
  .goal-pct {{ font-size: 0.75rem; color: #888; margin-top: 2px; text-align: right; }}
  .learning-row {{ display: flex; gap: 8px; padding: 8px 0;
                   border-bottom: 1px solid #2a2a2a; font-size: 0.85rem; }}
  .learning-icon {{ flex-shrink: 0; }}
  .learning-cat {{ color: #4CAF50; flex-shrink: 0; }}
  .learning-text {{ color: #ccc; }}
  .phase-badge {{ display: inline-block; background: #1e3a1e; color: #4CAF50;
                  border: 1px solid #4CAF50; border-radius: 4px;
                  padding: 4px 12px; font-size: 0.8rem; }}
  .footer {{ text-align: center; color: #444; font-size: 0.75rem; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
  <h1>📈 Revenue Report</h1>
  <div class="subtitle">{label} — Generated {today}</div>

  <div class="grid">
    <div class="card">
      <div class="card-label">MRR</div>
      <div class="card-value">€{mrr:,.0f}</div>
      <div class="card-sub">ARR: €{arr:,.0f}</div>
    </div>
    <div class="card">
      <div class="card-label">Period Revenue</div>
      <div class="card-value">€{revenue_total:,.0f}</div>
      <div class="card-sub">All time: €{total_all_time:,.0f}</div>
    </div>
    <div class="card">
      <div class="card-label">New Customers</div>
      <div class="card-value">{new_customers}</div>
      <div class="card-sub">Churned: {churned}</div>
    </div>
    <div class="card">
      <div class="card-label">Phase</div>
      <div class="card-value" style="font-size:1.2rem">{phase['number']}</div>
      <div class="card-sub">{phase['name']}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">MRR Trend — Last 8 Weeks</div>
    <div class="spark">{trend_bars}</div>
  </div>

  <div class="section">
    <div class="section-title">Revenue by Stream</div>
    {stream_bars if stream_bars else '<p style="color:#666">No revenue recorded in this period.</p>'}
  </div>

  <div class="section">
    <div class="section-title">Goal Progress</div>
    {goals_html}
  </div>

  <div class="section">
    <div class="section-title">Revenue Learnings</div>
    {learnings_html if learnings_html else '<p style="color:#666">No learnings logged yet.</p>'}
  </div>

  <div class="footer">
    Veritas Corporate — Agent Revenue Tracker — {today}
  </div>
</div>
</body>
</html>"""


def op_goal(set_name=None, target=None, deadline=None,
            metric="mrr", list_goals=False):
    goals_data = load_json(GOALS_FILE) or {"goals": []}

    if list_goals:
        state = load_state()
        goals = goals_data.get("goals", [])
        if not goals:
            print("  No active goals. Set one with --set")
            return
        print(f"\n{'─'*50}")
        print(f"  🎯 GOALS")
        print(f"{'─'*50}")
        for g in goals:
            t = g.get("target", 0)
            current = state["mrr"] if g.get("metric") == "mrr" else \
                      state.get("total_revenue_all_time", 0)
            pct = min(current / t * 100, 100) if t > 0 else 0
            bar = progress_bar(current, t, 20)
            print(f"  {g.get('name'):<20} {bar} {pct:>5.1f}%  target: €{t:,.0f}  by {g.get('deadline','—')}")
        return

    if set_name and target:
        goal = {
            "name":     set_name,
            "target":   float(target),
            "metric":   metric,
            "deadline": deadline or "—",
            "status":   "active",
            "created":  today_str(),
        }
        goals = goals_data.get("goals", [])
        goals = [g for g in goals if g.get("name") != set_name]
        goals.append(goal)
        goals_data["goals"] = goals
        save_json(GOALS_FILE, goals_data)
        print(f"✅ Goal set: {set_name} — €{target:,.0f} by {deadline or '—'}")


def op_asset(action: str, name: str = "", value: float = 0,
             currency: str = "EUR"):
    assets_data = load_json(ASSETS_FILE) or {"assets": [], "total_eur": 0}
    assets = assets_data.get("assets", [])

    if action == "list":
        if not assets:
            print("  No assets tracked.")
            return
        total = sum(a.get("value_eur", 0) for a in assets)
        print(f"\n{'─'*50}")
        print(f"  💰 ASSETS — Total: €{total:,.2f}")
        print(f"{'─'*50}")
        for a in assets:
            print(f"  {a.get('name','—'):<30} €{a.get('value_eur',0):>10,.2f}  ({a.get('currency','EUR')})")
        return

    if action == "add" and name:
        value_eur = value  # simplified
        asset = {
            "name":      name,
            "value":     value,
            "currency":  currency.upper(),
            "value_eur": value_eur,
            "added":     today_str(),
            "updated":   today_str(),
        }
        assets = [a for a in assets if a.get("name") != name]
        assets.append(asset)
        assets_data["assets"] = assets
        assets_data["total_eur"] = sum(a.get("value_eur", 0) for a in assets)
        save_json(ASSETS_FILE, assets_data)
        print(f"✅ Asset tracked: {name} — €{value_eur:,.2f}")

    elif action == "update" and name:
        for a in assets:
            if a.get("name") == name:
                a["value"] = value
                a["value_eur"] = value
                a["updated"] = today_str()
                break
        assets_data["total_eur"] = sum(a.get("value_eur", 0) for a in assets)
        save_json(ASSETS_FILE, assets_data)
        print(f"✅ Asset updated: {name} — €{value:,.2f}")


def op_learn(category: str, insight: str, impact: str = "medium",
             stream: str = ""):
    entry = {
        "date":     today_str(),
        "category": category,
        "insight":  insight,
        "impact":   impact,
        "stream":   stream,
        "action":   "",
    }
    append_jsonl(LEARNINGS_FILE, entry)

    # Also append to global LEARNINGS.md
    LEARNINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNINGS_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n## [{today_str()}] Revenue Learning — {category}\n")
        f.write(f"**Insight**: {insight}\n")
        f.write(f"**Impact**: {impact}\n")
        if stream:
            f.write(f"**Stream**: {stream}\n")

    icon = "✅" if impact == "high" else "💡"
    print(f"{icon} Learning logged: [{category}] {insight}")


def op_stats():
    state    = load_state()
    events   = read_jsonl(EVENTS_FILE)
    learnings = read_jsonl(LEARNINGS_FILE)
    assets   = load_json(ASSETS_FILE) or {}

    mrr    = state.get("mrr", 0)
    total  = state.get("total_revenue_all_time", 0)
    phase  = _detect_phase(mrr)
    n_events = len(events)

    print(f"\n{'='*50}")
    print(f"  📈 REVENUE STATS — {today_str()}")
    print(f"{'='*50}")
    print(f"  MRR:        €{mrr:>10,.2f}")
    print(f"  ARR:        €{mrr*12:>10,.2f}")
    print(f"  All time:   €{total:>10,.2f}")
    print(f"  Customers:  {state.get('customers', 0)}")
    print(f"  Phase:      {phase['number']} — {phase['name']}")
    print(f"  Events:     {n_events}")
    print(f"  Learnings:  {len(learnings)}")
    print(f"  Assets:     {len(assets.get('assets', []))}  (€{assets.get('total_eur',0):,.2f})")
    milestones = state.get("milestones_reached", [])
    print(f"  Milestones: {len(milestones)} reached")
    print(f"{'='*50}")


def op_anomalies():
    events = read_jsonl(EVENTS_FILE)
    state  = load_state()
    today  = date.today()
    anomalies = []

    # 1. No revenue in 7 days
    recent = [e for e in events
              if e.get("date", "") >= (today - timedelta(days=7)).isoformat()
              and e.get("amount_eur", 0) > 0]
    if not recent:
        anomalies.append(("🟡 WARNING", "No revenue recorded in the last 7 days"))

    # 2. Multiple churns in 24h
    today_events = [e for e in events if e.get("date") == today_str()]
    churns_today = [e for e in today_events if e.get("type") == "churn"]
    if len(churns_today) >= 3:
        anomalies.append(("🔴 CRITICAL", f"{len(churns_today)} churn events today"))

    # 3. MRR negative (shouldn't happen but guard)
    if state.get("mrr", 0) < 0:
        anomalies.append(("🔴 CRITICAL", "MRR is negative — data integrity issue"))

    # 4. No learning logged in 14 days
    learnings = read_jsonl(LEARNINGS_FILE)
    if learnings:
        last_learning = max(l.get("date", "") for l in learnings)
        days_since = (today - date.fromisoformat(last_learning)).days
        if days_since > 14:
            anomalies.append(("🟡 WARNING", f"No learning logged in {days_since} days"))

    print(f"\n{'─'*50}")
    print(f"  🔍 ANOMALY CHECK — {today_str()}")
    print(f"{'─'*50}")
    if anomalies:
        for level, msg in anomalies:
            print(f"  {level}: {msg}")
    else:
        print(f"  ✅ No anomalies detected")
    print(f"{'─'*50}")
    return anomalies


# ─── MAIN ──────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Revenue Tracker — Veritas Corporate"
    )
    parser.add_argument("--init", action="store_true")
    sub = parser.add_subparsers(dest="op")

    sub.add_parser("dashboard")
    sub.add_parser("stats")
    sub.add_parser("anomalies")

    p_rec = sub.add_parser("record")
    p_rec.add_argument("--stream",      required=True, choices=STREAMS)
    p_rec.add_argument("--amount",      required=True, type=float)
    p_rec.add_argument("--currency",    default="EUR")
    p_rec.add_argument("--description", required=True)
    p_rec.add_argument("--type",        dest="event_type", default="one_time",
                       choices=EVENT_TYPES)
    p_rec.add_argument("--client-id",   default=None)

    p_rep = sub.add_parser("report")
    p_rep.add_argument("--period", default="week",
                       choices=["week", "month", "quarter", "all"])
    p_rep.add_argument("--format", default="console", choices=["console", "html"])

    p_goal = sub.add_parser("goal")
    p_goal.add_argument("--set",      default=None)
    p_goal.add_argument("--target",   type=float, default=None)
    p_goal.add_argument("--deadline", default=None)
    p_goal.add_argument("--metric",   default="mrr", choices=["mrr", "total"])
    p_goal.add_argument("--list",     action="store_true")

    p_asset = sub.add_parser("asset")
    p_asset.add_argument("--action",   required=True, choices=["add","update","list"])
    p_asset.add_argument("--name",     default="")
    p_asset.add_argument("--value",    type=float, default=0)
    p_asset.add_argument("--currency", default="EUR")

    p_learn = sub.add_parser("learn")
    p_learn.add_argument("--category", required=True)
    p_learn.add_argument("--insight",  required=True)
    p_learn.add_argument("--impact",   default="medium",
                         choices=["high", "medium", "low"])
    p_learn.add_argument("--stream",   default="")

    args = parser.parse_args()

    if args.init:
        op_init()
        return

    if args.op is None:
        parser.print_help()
        return

    if   args.op == "dashboard": op_dashboard()
    elif args.op == "stats":     op_stats()
    elif args.op == "anomalies": op_anomalies()
    elif args.op == "record":
        op_record(args.stream, args.amount, args.currency,
                  args.description, args.event_type, args.client_id)
    elif args.op == "report":
        op_report(args.period, args.format)
    elif args.op == "goal":
        op_goal(args.set, args.target, args.deadline,
                args.metric, args.list)
    elif args.op == "asset":
        op_asset(args.action, args.name, args.value, args.currency)
    elif args.op == "learn":
        op_learn(args.category, args.insight, args.impact, args.stream)


if __name__ == "__main__":
    main()
