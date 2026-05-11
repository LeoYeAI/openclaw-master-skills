#!/usr/bin/env python3
"""
ceo_metrics.py — CEO Master Metrics Calculator
Veritas Corporate / OpenClaw Agent

Calculates all strategic KPIs the CEO-agent needs to make decisions:
  - MRR, ARR, MRR growth
  - CAC (Customer Acquisition Cost)
  - LTV (Customer Lifetime Value)
  - LTV/CAC ratio
  - CAC Payback Period
  - Churn rate
  - ROI per acquisition channel
  - Funnel conversion rates (stage by stage)
  - Weekly revenue velocity
  - Phase detection (Phase 1→5)

Usage:
  python3 ceo_metrics.py metrics_data.json
  python3 ceo_metrics.py metrics_data.json --format json
  python3 ceo_metrics.py metrics_data.json --telegram
  python3 ceo_metrics.py --sample   (generates sample input file)

Input: JSON file (see sample below or run --sample)
Output: CEO dashboard + recommendations + phase detection
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Optional


# ─── PHASE THRESHOLDS (monthly revenue in euros) ───────────────────────────
PHASES = {
    1: {"name": "Proof of Concept",   "min": 0,       "max": 10_000},
    2: {"name": "Product-Market Fit", "min": 10_000,  "max": 50_000},
    3: {"name": "Scale",              "min": 50_000,  "max": 500_000},
    4: {"name": "Expansion",          "min": 500_000, "max": 10_000_000},
    5: {"name": "Domination",         "min": 10_000_000, "max": float("inf")},
}

# ─── BENCHMARKS ─────────────────────────────────────────────────────────────
BENCHMARKS = {
    "ltv_cac_min":        3.0,    # LTV/CAC must be > 3x to be healthy
    "ltv_cac_great":      5.0,    # LTV/CAC > 5x is excellent
    "churn_max_monthly":  0.05,   # < 5%/month is acceptable
    "churn_great":        0.02,   # < 2%/month is great
    "email_open_rate":    0.40,   # > 40% is good
    "email_reply_rate":   0.05,   # > 5% is good (top: 15-25%)
    "cold_conversion":    0.02,   # 2% cold → paying = solid
    "cac_payback_max":    12,     # < 12 months payback = healthy
    "cac_payback_great":  6,      # < 6 months = excellent
}


def load_data(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_phase(mrr: float) -> dict:
    for num, phase in PHASES.items():
        if phase["min"] <= mrr < phase["max"]:
            return {"number": num, **phase}
    return {"number": 5, **PHASES[5]}


def calc_mrr(data: dict) -> dict:
    """MRR, ARR, growth, velocity."""
    current   = data.get("mrr_current", 0)
    previous  = data.get("mrr_previous", 0)
    arr       = current * 12
    growth_eur = current - previous
    growth_pct = ((current - previous) / previous * 100) if previous > 0 else 0
    weeks_to_next = 0
    if current > 0 and growth_eur > 0:
        phase = detect_phase(current)
        gap = phase["max"] - current
        weekly_velocity = growth_eur / 4  # monthly growth / 4 weeks
        weeks_to_next = round(gap / weekly_velocity) if weekly_velocity > 0 else 999

    return {
        "mrr":             round(current, 2),
        "arr":             round(arr, 2),
        "mrr_previous":    round(previous, 2),
        "mrr_growth_eur":  round(growth_eur, 2),
        "mrr_growth_pct":  round(growth_pct, 1),
        "weeks_to_next_phase": weeks_to_next,
    }


def calc_cac(data: dict) -> dict:
    """CAC per channel and blended."""
    channels = data.get("channels", {})
    results  = {}
    total_spend = 0
    total_customers = 0

    for channel, info in channels.items():
        spend     = info.get("spend_eur", 0)
        customers = info.get("new_customers", 0)
        cac = round(spend / customers, 2) if customers > 0 else 0
        results[channel] = {
            "spend":         spend,
            "new_customers": customers,
            "cac":           cac,
        }
        total_spend     += spend
        total_customers += customers

    blended_cac = round(total_spend / total_customers, 2) if total_customers > 0 else 0

    return {
        "by_channel":    results,
        "total_spend":   round(total_spend, 2),
        "total_new_customers": total_customers,
        "blended_cac":   blended_cac,
    }


def calc_ltv(data: dict) -> dict:
    """LTV, LTV/CAC, payback period."""
    avg_revenue_per_customer = data.get("avg_monthly_revenue_per_customer", 0)
    avg_gross_margin         = data.get("gross_margin_pct", 0.70)  # default 70%
    churn_monthly            = data.get("churn_rate_monthly", 0.05)
    blended_cac              = data.get("_blended_cac", 0)  # injected from cac calc

    # LTV = (avg revenue × gross margin) / churn
    if churn_monthly > 0:
        ltv = round((avg_revenue_per_customer * avg_gross_margin) / churn_monthly, 2)
    else:
        ltv = 0

    ltv_cac_ratio = round(ltv / blended_cac, 2) if blended_cac > 0 else 0

    # Payback = CAC / (monthly revenue per customer × gross margin)
    monthly_contribution = avg_revenue_per_customer * avg_gross_margin
    payback_months = round(blended_cac / monthly_contribution, 1) if monthly_contribution > 0 else 0

    # Avg customer lifetime in months
    avg_lifetime_months = round(1 / churn_monthly, 1) if churn_monthly > 0 else 0

    return {
        "ltv":                  ltv,
        "ltv_cac_ratio":        ltv_cac_ratio,
        "payback_months":       payback_months,
        "avg_lifetime_months":  avg_lifetime_months,
        "avg_monthly_revenue":  avg_revenue_per_customer,
        "gross_margin_pct":     round(avg_gross_margin * 100, 1),
    }


def calc_churn(data: dict) -> dict:
    """Churn rate, churned revenue, net revenue retention."""
    customers_start  = data.get("customers_start_of_month", 0)
    customers_lost   = data.get("customers_lost_this_month", 0)
    mrr_lost         = data.get("mrr_lost_to_churn", 0)
    mrr_expansion    = data.get("mrr_expansion", 0)  # upsells
    mrr_current      = data.get("mrr_current", 0)

    churn_rate = round(customers_lost / customers_start, 4) if customers_start > 0 else 0
    churn_pct  = round(churn_rate * 100, 2)

    # Net Revenue Retention = (MRR end - MRR from new customers) / MRR start
    # Simplified: (MRR - churned + expansion) / MRR previous
    mrr_previous = data.get("mrr_previous", mrr_current)
    if mrr_previous > 0:
        nrr = round(((mrr_current - mrr_lost + mrr_expansion) / mrr_previous) * 100, 1)
    else:
        nrr = 100.0

    return {
        "churn_rate_monthly":    churn_rate,
        "churn_pct":             churn_pct,
        "customers_lost":        customers_lost,
        "mrr_lost_eur":          mrr_lost,
        "mrr_expansion_eur":     mrr_expansion,
        "net_revenue_retention": nrr,
    }


def calc_funnel(data: dict) -> dict:
    """Stage-by-stage funnel conversion rates."""
    funnel = data.get("funnel", {})
    stages = [
        "prospects_contacted",
        "prospects_replied",
        "leads_qualified",
        "calls_booked",
        "proposals_sent",
        "customers_won",
    ]

    results  = {}
    previous = None
    previous_name = None

    for stage in stages:
        count = funnel.get(stage, 0)
        if previous is not None and previous > 0:
            conversion = round(count / previous * 100, 1)
            results[stage] = {
                "count":            count,
                "conversion_from_prev": f"{conversion}%",
                "from_stage":       previous_name,
            }
        else:
            results[stage] = {"count": count, "conversion_from_prev": "—", "from_stage": "—"}
        previous      = count
        previous_name = stage

    # Overall: prospects → customers
    top   = funnel.get("prospects_contacted", 0)
    bottom = funnel.get("customers_won", 0)
    overall = round(bottom / top * 100, 2) if top > 0 else 0

    # Find the biggest drop-off
    bottleneck = None
    worst_rate = 100.0
    prev_count = None
    prev_stage = None
    for stage in stages:
        count = funnel.get(stage, 0)
        if prev_count is not None and prev_count > 0:
            rate = count / prev_count * 100
            if rate < worst_rate:
                worst_rate = rate
                bottleneck = f"{prev_stage} → {stage} ({round(rate, 1)}% conversion)"
        prev_count = count
        prev_stage = stage

    return {
        "stages":             results,
        "overall_conversion": f"{overall}%",
        "bottleneck":         bottleneck,
    }


def calc_channel_roi(data: dict) -> dict:
    """ROI per acquisition channel."""
    channels = data.get("channels", {})
    results  = {}

    for channel, info in channels.items():
        spend    = info.get("spend_eur", 0)
        revenue  = info.get("revenue_generated_eur", 0)
        if spend > 0:
            roi  = round(((revenue - spend) / spend) * 100, 1)
            roas = round(revenue / spend, 2)
        else:
            roi, roas = 0, 0
        results[channel] = {
            "spend_eur":   spend,
            "revenue_eur": revenue,
            "roi_pct":     roi,
            "roas":        roas,
            "status":      "✅" if roi > 100 else ("⚠️" if roi > 0 else "❌"),
        }

    # Best channel
    if results:
        best = max(results.items(), key=lambda x: x[1]["roi_pct"])
        worst = min(results.items(), key=lambda x: x[1]["roi_pct"])
    else:
        best = worst = (None, {})

    return {
        "by_channel": results,
        "best_channel":  best[0],
        "worst_channel": worst[0],
    }


def generate_recommendations(metrics: dict) -> list:
    """Generate CEO-level action recommendations based on metrics."""
    recs = []
    ltv    = metrics["ltv"]
    cac    = metrics["cac"]
    churn  = metrics["churn"]
    mrr_m  = metrics["mrr"]
    funnel = metrics["funnel"]
    phase  = metrics["phase"]

    # LTV/CAC health
    ratio = ltv["ltv_cac_ratio"]
    if ratio < BENCHMARKS["ltv_cac_min"]:
        recs.append({
            "priority": "🔴 CRITICAL",
            "area":     "Unit Economics",
            "finding":  f"LTV/CAC ratio is {ratio}x — below minimum 3x threshold.",
            "action":   "Either reduce CAC (optimize acquisition channels) or increase LTV "
                        "(raise prices, reduce churn, add upsells). Fix this before scaling.",
        })
    elif ratio >= BENCHMARKS["ltv_cac_great"]:
        recs.append({
            "priority": "🟢 OPPORTUNITY",
            "area":     "Unit Economics",
            "finding":  f"LTV/CAC ratio is {ratio}x — excellent. Safe to scale acquisition.",
            "action":   "Double acquisition spend on best-performing channel.",
        })

    # Churn
    churn_rate = churn["churn_rate_monthly"]
    if churn_rate > BENCHMARKS["churn_max_monthly"]:
        recs.append({
            "priority": "🔴 CRITICAL",
            "area":     "Retention",
            "finding":  f"Monthly churn is {churn['churn_pct']}% — above 5% threshold.",
            "action":   "Pause new acquisition. Fix retention first. "
                        "Survey churned customers. Fix the product/offer.",
        })

    # CAC payback
    payback = ltv["payback_months"]
    if payback > BENCHMARKS["cac_payback_max"]:
        recs.append({
            "priority": "🟡 WARNING",
            "area":     "Payback Period",
            "finding":  f"CAC payback is {payback} months — above 12-month ceiling.",
            "action":   "Increase average order value or reduce acquisition costs.",
        })

    # MRR growth
    growth = mrr_m["mrr_growth_pct"]
    if growth < 0:
        recs.append({
            "priority": "🔴 CRITICAL",
            "area":     "Revenue",
            "finding":  f"MRR is declining ({growth}% vs last month).",
            "action":   "Emergency: diagnose churn source + reactivate cold leads today.",
        })
    elif growth < 10 and phase["number"] <= 2:
        recs.append({
            "priority": "🟡 WARNING",
            "area":     "Growth Velocity",
            "finding":  f"MRR growth is {growth}% — too slow for Phase {phase['number']}.",
            "action":   "Double outreach volume. Test new ICP or offer angle this week.",
        })

    # Funnel bottleneck
    bn = funnel.get("bottleneck")
    if bn:
        recs.append({
            "priority": "🟡 WARNING",
            "area":     "Funnel",
            "finding":  f"Biggest drop-off: {bn}",
            "action":   "Focus optimization here first — this is where leads are leaking.",
        })

    # Channel ROI
    roi_data = metrics.get("channel_roi", {})
    for ch, stats in roi_data.get("by_channel", {}).items():
        if stats["roi_pct"] < 0:
            recs.append({
                "priority": "🟡 WARNING",
                "area":     f"Channel ROI — {ch}",
                "finding":  f"{ch} has negative ROI ({stats['roi_pct']}%).",
                "action":   f"Stop spending on {ch} until ROI is positive. Reallocate budget.",
            })

    # Phase-specific
    if phase["number"] == 1:
        recs.append({
            "priority": "📋 PHASE 1 FOCUS",
            "area":     "Priority",
            "finding":  "Phase 1: Proof of Concept — only one metric matters.",
            "action":   "Get to 10 paying customers. Nothing else. No optimization yet.",
        })
    elif phase["number"] == 2:
        recs.append({
            "priority": "📋 PHASE 2 FOCUS",
            "area":     "Priority",
            "finding":  "Phase 2: retention before acquisition.",
            "action":   "Measure NPS. Survey churned users. Fix retention lever first.",
        })

    if not recs:
        recs.append({
            "priority": "🟢 ALL GREEN",
            "area":     "Status",
            "finding":  "All key metrics are within healthy ranges.",
            "action":   "Identify top-performing channel and double down.",
        })

    return recs


def format_telegram(metrics: dict, recs: list) -> str:
    """Format compact Telegram report."""
    mrr   = metrics["mrr"]
    ltv   = metrics["ltv"]
    churn = metrics["churn"]
    phase = metrics["phase"]

    lines = [
        f"📊 *CEO Weekly Metrics*",
        f"",
        f"*Revenue*",
        f"MRR: €{mrr['mrr']:,.0f} ({'+' if mrr['mrr_growth_pct'] >= 0 else ''}{mrr['mrr_growth_pct']}%)",
        f"ARR: €{mrr['arr']:,.0f}",
        f"",
        f"*Unit Economics*",
        f"CAC: €{metrics['cac']['blended_cac']:,.0f}",
        f"LTV: €{ltv['ltv']:,.0f}",
        f"LTV/CAC: {ltv['ltv_cac_ratio']}x",
        f"Payback: {ltv['payback_months']} months",
        f"",
        f"*Retention*",
        f"Churn: {churn['churn_pct']}%/month",
        f"NRR: {churn['net_revenue_retention']}%",
        f"",
        f"*Phase*: {phase['number']} — {phase['name']}",
        f"Next phase in: {mrr['weeks_to_next_phase']} weeks",
        f"",
        f"*Top Actions*",
    ]
    for rec in recs[:3]:  # Top 3 only for Telegram
        lines.append(f"{rec['priority']}: {rec['action']}")

    return "\n".join(lines)


def format_console(metrics: dict, recs: list) -> str:
    """Format full console report."""
    mrr    = metrics["mrr"]
    ltv    = metrics["ltv"]
    cac    = metrics["cac"]
    churn  = metrics["churn"]
    phase  = metrics["phase"]
    funnel = metrics["funnel"]
    roi    = metrics.get("channel_roi", {})

    lines = [
        "=" * 60,
        "  CEO METRICS DASHBOARD",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        f"  PHASE {phase['number']} — {phase['name'].upper()}",
        f"  Target: €{PHASES[phase['number']]['max']:,.0f}/month MRR",
        f"  Next phase in: {mrr['weeks_to_next_phase']} weeks (est.)",
        "",
        "─" * 60,
        "  REVENUE",
        "─" * 60,
        f"  MRR current:   €{mrr['mrr']:>10,.2f}",
        f"  MRR previous:  €{mrr['mrr_previous']:>10,.2f}",
        f"  Growth:        {'+' if mrr['mrr_growth_pct'] >= 0 else ''}{mrr['mrr_growth_pct']}%  (€{mrr['mrr_growth_eur']:+,.0f})",
        f"  ARR:           €{mrr['arr']:>10,.2f}",
        "",
        "─" * 60,
        "  UNIT ECONOMICS",
        "─" * 60,
        f"  Blended CAC:   €{cac['blended_cac']:>10,.2f}",
        f"  LTV:           €{ltv['ltv']:>10,.2f}",
        f"  LTV/CAC ratio: {ltv['ltv_cac_ratio']:>10.2f}x  {'✅' if ltv['ltv_cac_ratio'] >= 3 else '❌'} (target: >3x)",
        f"  Payback period:{ltv['payback_months']:>9.1f} mo  {'✅' if ltv['payback_months'] <= 12 else '❌'} (target: <12mo)",
        f"  Avg lifetime:  {ltv['avg_lifetime_months']:>9.1f} mo",
        f"  Gross margin:  {ltv['gross_margin_pct']:>9.1f}%",
        "",
        "─" * 60,
        "  RETENTION",
        "─" * 60,
        f"  Monthly churn: {churn['churn_pct']:>10.2f}%  {'✅' if churn['churn_rate_monthly'] <= 0.05 else '❌'} (target: <5%)",
        f"  Customers lost:{churn['customers_lost']:>10}",
        f"  MRR lost:      €{churn['mrr_lost_eur']:>9,.2f}",
        f"  MRR expansion: €{churn['mrr_expansion_eur']:>9,.2f}",
        f"  NRR:           {churn['net_revenue_retention']:>10.1f}%  {'✅' if churn['net_revenue_retention'] >= 100 else '⚠️'} (target: >100%)",
        "",
        "─" * 60,
        "  ACQUISITION — CAC BY CHANNEL",
        "─" * 60,
    ]

    for ch, info in cac["by_channel"].items():
        lines.append(f"  {ch:<20} CAC: €{info['cac']:>8,.0f}  |  {info['new_customers']} customers  |  spend: €{info['spend']:,.0f}")

    lines += [
        "",
        "─" * 60,
        "  CHANNEL ROI",
        "─" * 60,
    ]
    for ch, info in roi.get("by_channel", {}).items():
        lines.append(
            f"  {ch:<20} ROI: {info['roi_pct']:>+7.1f}%  |  ROAS: {info['roas']:.2f}x  {info['status']}"
        )
    if roi.get("best_channel"):
        lines.append(f"  → Best:  {roi['best_channel']}")
    if roi.get("worst_channel"):
        lines.append(f"  → Worst: {roi['worst_channel']}")

    lines += [
        "",
        "─" * 60,
        "  FUNNEL CONVERSION",
        "─" * 60,
    ]
    for stage, info in funnel["stages"].items():
        name = stage.replace("_", " ").title()
        conv = info["conversion_from_prev"]
        lines.append(f"  {name:<30} {info['count']:>6}  conv: {conv}")
    lines += [
        f"  Overall (prospect → customer): {funnel['overall_conversion']}",
        f"  Bottleneck: {funnel['bottleneck']}",
        "",
        "─" * 60,
        "  CEO RECOMMENDATIONS",
        "─" * 60,
    ]
    for rec in recs:
        lines += [
            f"  {rec['priority']} [{rec['area']}]",
            f"  Finding: {rec['finding']}",
            f"  Action:  {rec['action']}",
            "",
        ]

    lines += ["=" * 60]
    return "\n".join(lines)


def generate_sample_input() -> dict:
    """Generate a sample input JSON file with realistic data."""
    return {
        "_comment": "CEO Metrics input file — fill with real data from your Google Sheet tracker",
        "_updated": datetime.now().strftime("%Y-%m-%d"),

        "mrr_current":  4200,
        "mrr_previous": 3100,

        "avg_monthly_revenue_per_customer": 97,
        "gross_margin_pct": 0.85,
        "churn_rate_monthly": 0.04,

        "customers_start_of_month": 35,
        "customers_lost_this_month": 2,
        "mrr_lost_to_churn": 194,
        "mrr_expansion": 291,

        "channels": {
            "cold_email": {
                "spend_eur": 0,
                "new_customers": 8,
                "revenue_generated_eur": 776,
            },
            "linkedin": {
                "spend_eur": 0,
                "new_customers": 4,
                "revenue_generated_eur": 388,
            },
            "organic_content": {
                "spend_eur": 0,
                "new_customers": 3,
                "revenue_generated_eur": 291,
            },
            "paid_ads": {
                "spend_eur": 300,
                "new_customers": 2,
                "revenue_generated_eur": 194,
            },
        },

        "funnel": {
            "prospects_contacted": 500,
            "prospects_replied":   38,
            "leads_qualified":     18,
            "calls_booked":        8,
            "proposals_sent":      7,
            "customers_won":       5,
        },
    }


def run(filepath: str, fmt: str = "console", telegram: bool = False) -> dict:
    data = load_data(filepath)

    # Build metrics
    mrr_metrics   = calc_mrr(data)
    cac_metrics   = calc_cac(data)
    data["_blended_cac"] = cac_metrics["blended_cac"]
    ltv_metrics   = calc_ltv(data)
    churn_metrics = calc_churn(data)
    funnel_metrics = calc_funnel(data)
    roi_metrics   = calc_channel_roi(data)
    phase         = detect_phase(mrr_metrics["mrr"])

    metrics = {
        "mrr":         mrr_metrics,
        "cac":         cac_metrics,
        "ltv":         ltv_metrics,
        "churn":       churn_metrics,
        "funnel":      funnel_metrics,
        "channel_roi": roi_metrics,
        "phase":       phase,
        "generated_at": datetime.now().isoformat(),
    }

    recs = generate_recommendations(metrics)
    metrics["recommendations"] = recs

    if fmt == "json":
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
    elif telegram:
        print(format_telegram(metrics, recs))
    else:
        print(format_console(metrics, recs))

    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="CEO Metrics Calculator — Veritas Corporate"
    )
    parser.add_argument("input", nargs="?", help="Path to metrics_data.json")
    parser.add_argument("--format", choices=["console", "json"], default="console")
    parser.add_argument("--telegram", action="store_true", help="Compact Telegram format")
    parser.add_argument("--sample", action="store_true", help="Generate sample input file")
    args = parser.parse_args()

    if args.sample:
        sample = generate_sample_input()
        outpath = "metrics_data.json"
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)
        print(f"✅ Sample input generated: {outpath}")
        print("   Fill it with your real data, then run:")
        print(f"   python3 ceo_metrics.py {outpath}")
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    run(args.input, fmt=args.format, telegram=args.telegram)


if __name__ == "__main__":
    main()
