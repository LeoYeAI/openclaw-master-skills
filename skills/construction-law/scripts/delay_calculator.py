#!/usr/bin/env python3
"""
Delay Analysis Calculator
Input delay events with dates and get critical path impact analysis.

Usage:
    python3 delay_calculator.py --baseline-start 2026-05-11 --baseline-end 2030-05-10 --events events.json
    python3 delay_calculator.py --baseline-start 2026-05-11 --baseline-end 2030-05-10 --interactive
    python3 delay_calculator.py --baseline-start 2026-05-11 --baseline-end 2030-05-10 --add "Late access|2026-06-01|2026-06-30|employer|critical" --add "Weather|2026-07-15|2026-07-25|neutral|critical"
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

def parse_date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d")

def days_between(d1, d2):
    return (d2 - d1).days

def analyse_delays(baseline_start, baseline_end, events, fmt="md", output=None):
    baseline_duration = days_between(baseline_start, baseline_end)
    
    # Sort events by start date
    events.sort(key=lambda e: e["start"])
    
    # Calculate total delays by responsibility
    employer_delay = 0
    contractor_delay = 0
    neutral_delay = 0
    concurrent_days = 0
    
    # Track occupied delay periods for concurrency detection
    employer_periods = []
    contractor_periods = []
    
    for e in events:
        duration = days_between(e["start"], e["end"])
        e["duration"] = duration
        
        if e["responsibility"] == "employer":
            employer_delay += duration
            employer_periods.append((e["start"], e["end"]))
        elif e["responsibility"] == "contractor":
            contractor_delay += duration
            contractor_periods.append((e["start"], e["end"]))
        elif e["responsibility"] == "neutral":
            neutral_delay += duration
    
    # Detect concurrent delay (overlapping employer + contractor periods)
    for ep_start, ep_end in employer_periods:
        for cp_start, cp_end in contractor_periods:
            overlap_start = max(ep_start, cp_start)
            overlap_end = min(ep_end, cp_end)
            if overlap_start < overlap_end:
                concurrent_days += days_between(overlap_start, overlap_end)
    
    # Calculate net delay (simple impacted method)
    total_critical_delay = sum(e["duration"] for e in events if e.get("critical", True))
    total_non_critical = sum(e["duration"] for e in events if not e.get("critical", True))
    
    # EOT entitlement (employer + neutral delays on critical path, minus concurrency)
    eot_entitlement = sum(e["duration"] for e in events 
                         if e["responsibility"] in ("employer", "neutral") and e.get("critical", True))
    
    # Projected completion
    projected_end = baseline_end + timedelta(days=total_critical_delay)
    eot_completion = baseline_end + timedelta(days=eot_entitlement)
    
    # Exposure analysis
    ld_exposure_days = max(0, total_critical_delay - eot_entitlement)
    
    if fmt == "md":
        lines = [
            "# Delay Analysis Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Contract Dates",
            "",
            f"| Item | Date | Days |",
            f"|------|------|------|",
            f"| Baseline Start | {baseline_start.strftime('%d %b %Y')} | — |",
            f"| Baseline Completion | {baseline_end.strftime('%d %b %Y')} | {baseline_duration} days |",
            f"| Projected Completion | {projected_end.strftime('%d %b %Y')} | {baseline_duration + total_critical_delay} days |",
            f"| Completion with EOT | {eot_completion.strftime('%d %b %Y')} | {baseline_duration + eot_entitlement} days |",
            "",
            "## Delay Events",
            "",
            "| # | Event | Start | End | Duration | Responsibility | Critical? |",
            "|---|-------|-------|-----|----------|---------------|-----------|",
        ]
        
        for i, e in enumerate(events, 1):
            critical = "✅ Yes" if e.get("critical", True) else "❌ No"
            lines.append(f"| {i} | {e['description']} | {e['start'].strftime('%d %b %Y')} | {e['end'].strftime('%d %b %Y')} | {e['duration']} days | {e['responsibility'].title()} | {critical} |")
        
        lines.extend([
            "",
            "## Delay Summary",
            "",
            "| Category | Days |",
            "|----------|------|",
            f"| Employer-caused delay (critical) | {sum(e['duration'] for e in events if e['responsibility']=='employer' and e.get('critical',True))} days |",
            f"| Contractor-caused delay (critical) | {sum(e['duration'] for e in events if e['responsibility']=='contractor' and e.get('critical',True))} days |",
            f"| Neutral delay (critical) | {sum(e['duration'] for e in events if e['responsibility']=='neutral' and e.get('critical',True))} days |",
            f"| Non-critical delay (all) | {total_non_critical} days |",
            f"| Concurrent delay detected | {concurrent_days} days |",
            f"| **Total critical delay** | **{total_critical_delay} days** |",
            "",
            "## EOT & LD Analysis",
            "",
            "| Item | Value |",
            "|------|-------|",
            f"| EOT Entitlement (employer + neutral, critical) | **{eot_entitlement} days** |",
            f"| Contractor's own delay (critical) | {sum(e['duration'] for e in events if e['responsibility']=='contractor' and e.get('critical',True))} days |",
            f"| LD Exposure (delay beyond EOT) | **{ld_exposure_days} days** |",
            f"| Concurrent delay | {concurrent_days} days |",
            "",
            "## Concurrency Note",
            "",
        ])
        
        if concurrent_days > 0:
            lines.extend([
                f"⚠️ **{concurrent_days} days of concurrent delay detected** — employer and contractor delays overlap.",
                "",
                "**Treatment depends on jurisdiction:**",
                "- **Malmaison (England)**: Contractor gets EOT but no prolongation costs for concurrent period",
                "- **Singapore**: Apportionment approach — SO/Architect may grant partial EOT",
                "- **SCL Protocol**: If true concurrency, EOT granted but costs not recoverable",
                "",
            ])
        else:
            lines.append("No concurrent delay detected.")
            lines.append("")
        
        lines.extend([
            "## Recommendations",
            "",
            "1. **Preserve notices** — ensure all delay events have been properly notified under the contract",
            "2. **Update programme** — submit revised programme showing delay impact",
            "3. **Maintain records** — daily site diaries, progress photos, resource records",
            "4. **Quantify costs** — prepare prolongation cost calculation for EOT period",
            "5. **Mitigate** — document all mitigation measures taken",
            "",
            "---",
            "",
            "⚠️ **Disclaimer**: This is a simplified impacted as-planned analysis. For complex disputes, a Time Impact Analysis (TIA) or Windows Analysis by a delay expert is recommended.",
            "",
            f"*Generated by Construction Law Skill v1.0.0*",
        ])
        
        result = "\n".join(lines)
        if output:
            with open(output, 'w') as f:
                f.write(result)
            print(f"Report written to {output}")
        else:
            print(result)

    elif fmt == "csv":
        import csv
        out = open(output, 'w', newline='') if output else sys.stdout
        writer = csv.writer(out)
        writer.writerow(["Delay Analysis Report"])
        writer.writerow(["Baseline Start", baseline_start.strftime('%Y-%m-%d')])
        writer.writerow(["Baseline Completion", baseline_end.strftime('%Y-%m-%d')])
        writer.writerow(["Baseline Duration", f"{baseline_duration} days"])
        writer.writerow(["Projected Completion", projected_end.strftime('%Y-%m-%d')])
        writer.writerow(["EOT Entitlement", f"{eot_entitlement} days"])
        writer.writerow(["LD Exposure", f"{ld_exposure_days} days"])
        writer.writerow([])
        writer.writerow(["#", "Event", "Start", "End", "Duration", "Responsibility", "Critical"])
        for i, e in enumerate(events, 1):
            writer.writerow([i, e['description'], e['start'].strftime('%Y-%m-%d'),
                           e['end'].strftime('%Y-%m-%d'), e['duration'],
                           e['responsibility'], "Yes" if e.get('critical', True) else "No"])
        if output:
            out.close()
            print(f"CSV written to {output}")

    elif fmt == "json":
        result = {
            "baseline": {"start": baseline_start.strftime('%Y-%m-%d'), "end": baseline_end.strftime('%Y-%m-%d'), "duration": baseline_duration},
            "projected_completion": projected_end.strftime('%Y-%m-%d'),
            "eot_completion": eot_completion.strftime('%Y-%m-%d'),
            "eot_entitlement_days": eot_entitlement,
            "ld_exposure_days": ld_exposure_days,
            "concurrent_delay_days": concurrent_days,
            "total_critical_delay": total_critical_delay,
            "events": [{"description": e["description"], "start": e["start"].strftime('%Y-%m-%d'),
                        "end": e["end"].strftime('%Y-%m-%d'), "duration": e["duration"],
                        "responsibility": e["responsibility"], "critical": e.get("critical", True)}
                       for e in events]
        }
        output_str = json.dumps(result, indent=2)
        if output:
            with open(output, 'w') as f:
                f.write(output_str)
            print(f"JSON written to {output}")
        else:
            print(output_str)

def main():
    parser = argparse.ArgumentParser(description="Delay Analysis Calculator")
    parser.add_argument("--baseline-start", required=True, help="Baseline start date (YYYY-MM-DD)")
    parser.add_argument("--baseline-end", required=True, help="Baseline completion date (YYYY-MM-DD)")
    parser.add_argument("--events", help="JSON file with delay events")
    parser.add_argument("--add", action="append", help="Add event: 'description|start|end|responsibility|critical/non-critical'")
    parser.add_argument("--format", default="md", choices=["md", "csv", "json"])
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    bs = parse_date(args.baseline_start)
    be = parse_date(args.baseline_end)
    events = []

    if args.events:
        with open(args.events) as f:
            raw = json.load(f)
        for e in raw:
            events.append({
                "description": e["description"],
                "start": parse_date(e["start"]),
                "end": parse_date(e["end"]),
                "responsibility": e.get("responsibility", "employer"),
                "critical": e.get("critical", True)
            })

    if args.add:
        for a in args.add:
            parts = a.split("|")
            if len(parts) < 4:
                print(f"Error: --add format is 'description|start|end|responsibility[|critical]'")
                sys.exit(1)
            events.append({
                "description": parts[0].strip(),
                "start": parse_date(parts[1]),
                "end": parse_date(parts[2]),
                "responsibility": parts[3].strip().lower(),
                "critical": parts[4].strip().lower() != "non-critical" if len(parts) > 4 else True
            })

    if not events:
        print("Error: No events provided. Use --events or --add")
        sys.exit(1)

    analyse_delays(bs, be, events, args.format, args.output)

if __name__ == "__main__":
    main()
