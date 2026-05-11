#!/usr/bin/env python3
"""
Singapore SOP Act Payment Timeline Calculator
Calculates all statutory deadlines from a payment claim date.

Usage:
    python3 sop_calculator.py --claim-date 2026-06-30
    python3 sop_calculator.py --claim-date 2026-06-30 --response-period 14
    python3 sop_calculator.py --claim-date 2026-06-30 --format csv --output sop_timeline.csv
"""

import argparse
import sys
from datetime import datetime, timedelta

def calc_timeline(claim_date_str, response_period=21, fmt="md", output=None):
    claim_date = datetime.strptime(claim_date_str, "%Y-%m-%d")
    
    # Key dates
    response_deadline = claim_date + timedelta(days=response_period)
    
    # Entitlement to adjudicate: 7 days after response deadline (if no response or dispute)
    adjudication_entitlement = response_deadline + timedelta(days=1)
    
    # Adjudication application: within 7 days of entitlement
    adjudication_app_deadline = adjudication_entitlement + timedelta(days=7)
    
    # Adjudication response: 7 days from receiving application
    adjudication_response = adjudication_app_deadline + timedelta(days=7)
    
    # Adjudicator's determination: 7 days (extendable to 14)
    determination_min = adjudication_response + timedelta(days=7)
    determination_max = adjudication_response + timedelta(days=14)
    
    # Payment of adjudicated amount: 7 days from determination
    payment_min = determination_min + timedelta(days=7)
    payment_max = determination_max + timedelta(days=7)
    
    # Direct payment from principal: if respondent fails to pay
    direct_payment = payment_max + timedelta(days=1)
    
    # Smash and grab scenario
    smash_grab_note = "If NO payment response served by respondent, respondent CANNOT raise withholding reasons in adjudication."

    timeline = [
        {"day": 0, "date": claim_date, "event": "Payment Claim served", "section": "s.10", "action": "Claimant", "critical": True,
         "note": "Must state claimed amount and be served on respondent"},
        {"day": response_period, "date": response_deadline, "event": "Payment Response deadline", "section": "s.11", "action": "Respondent", "critical": True,
         "note": f"Must respond within {response_period} days. FAILURE = smash and grab exposure"},
        {"day": response_period + 1, "date": adjudication_entitlement, "event": "Entitlement to adjudicate arises", "section": "s.12", "action": "Claimant", "critical": False,
         "note": "If no response, or dispute on amount"},
        {"day": response_period + 8, "date": adjudication_app_deadline, "event": "Adjudication application deadline", "section": "s.13", "action": "Claimant", "critical": True,
         "note": "Must apply within 7 days of entitlement. MISS THIS = lose right to adjudicate this claim"},
        {"day": response_period + 15, "date": adjudication_response, "event": "Adjudication response deadline", "section": "s.15", "action": "Respondent", "critical": True,
         "note": "7 days from receiving application"},
        {"day": response_period + 22, "date": determination_min, "event": "Adjudicator's determination (earliest)", "section": "s.17", "action": "Adjudicator", "critical": False,
         "note": "7 days from response (may extend to 14 with consent)"},
        {"day": response_period + 29, "date": determination_max, "event": "Adjudicator's determination (latest)", "section": "s.17", "action": "Adjudicator", "critical": True,
         "note": "14 days maximum (with consent of claimant)"},
        {"day": response_period + 29 + 7, "date": payment_min, "event": "Payment due (earliest)", "section": "s.22", "action": "Respondent", "critical": False,
         "note": "7 days from determination"},
        {"day": response_period + 36 + 7, "date": payment_max, "event": "Payment due (latest)", "section": "s.22", "action": "Respondent", "critical": True,
         "note": "7 days from latest determination date"},
        {"day": response_period + 44, "date": direct_payment, "event": "Direct payment from principal available", "section": "s.21", "action": "Claimant", "critical": False,
         "note": "If respondent fails to pay adjudicated amount"},
    ]

    if fmt == "md":
        lines = [
            "# SOP Act Payment Timeline",
            "",
            f"**Payment Claim Date:** {claim_date.strftime('%d %B %Y')} ({claim_date.strftime('%A')})",
            f"**Payment Response Period:** {response_period} days",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Timeline",
            "",
            "| Day | Date | Event | Section | Action By | Critical |",
            "|-----|------|-------|---------|-----------|----------|",
        ]
        for t in timeline:
            critical = "⚠️ YES" if t["critical"] else ""
            day_str = f"D+{t['day']}" if t['day'] > 0 else "D0"
            lines.append(f"| {day_str} | {t['date'].strftime('%d %b %Y')} ({t['date'].strftime('%a')}) | {t['event']} | {t['section']} | {t['action']} | {critical} |")
        
        lines.extend([
            "",
            "## Key Warnings",
            "",
            f"### ⚠️ Smash and Grab",
            f"{smash_grab_note}",
            "",
            "### ⚠️ Time-Bar",
            "Adjudication application must be made within **7 days** of entitlement arising. Missing this deadline = lose right to adjudicate for this payment claim cycle.",
            "",
            "### ⚠️ Temporarily Binding",
            "Adjudication determination is **temporarily binding** — pay now, argue later. The adjudicated amount must be paid even if respondent intends to challenge in arbitration/court.",
            "",
            "### ⚠️ Cannot Contract Out",
            "Section 36: Any provision in a contract that purports to exclude, modify, or restrict the operation of the SOP Act is **void**.",
            "",
            "## Notes",
            "",
            "- All dates assume calendar days (not business days)",
            "- If a deadline falls on a weekend/public holiday, check whether the SOP Act extends to the next business day",
            "- Payment response period defaults to 21 days; check your contract for a shorter period",
            "- Claimant can serve a fresh payment claim for the same work in the next payment cycle (repeat claims permitted)",
            "",
            "---",
            f"*Generated by Construction Law Skill v1.0.0*",
        ])
        
        result = "\n".join(lines)
        if output:
            with open(output, 'w') as f:
                f.write(result)
            print(f"Timeline written to {output}")
        else:
            print(result)

    elif fmt == "csv":
        import csv
        out = open(output, 'w', newline='') if output else sys.stdout
        writer = csv.writer(out)
        writer.writerow(["Payment Claim Date", claim_date.strftime('%Y-%m-%d')])
        writer.writerow(["Response Period", f"{response_period} days"])
        writer.writerow([])
        writer.writerow(["Day", "Date", "Day of Week", "Event", "Section", "Action By", "Critical", "Notes"])
        for t in timeline:
            day_str = f"D+{t['day']}" if t['day'] > 0 else "D0"
            writer.writerow([day_str, t['date'].strftime('%Y-%m-%d'), t['date'].strftime('%A'),
                           t['event'], t['section'], t['action'],
                           "YES" if t['critical'] else "", t['note']])
        if output:
            out.close()
            print(f"CSV written to {output}")

def main():
    parser = argparse.ArgumentParser(description="SOP Act Payment Timeline Calculator")
    parser.add_argument("--claim-date", required=True, help="Payment claim date (YYYY-MM-DD)")
    parser.add_argument("--response-period", type=int, default=21, help="Payment response period in days (default: 21)")
    parser.add_argument("--format", default="md", choices=["md", "csv"], help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()
    calc_timeline(args.claim_date, args.response_period, args.format, args.output)

if __name__ == "__main__":
    main()
