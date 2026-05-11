#!/usr/bin/env python3
"""
Notice Calendar Generator
Generates a notice/obligations calendar from a contract form selection.
Outputs CSV or Markdown table with all time-bars, notice periods, and key dates.

Usage:
    python3 notice_calendar.py --form fidic-red --format md
    python3 notice_calendar.py --form psscoc --format csv
    python3 notice_calendar.py --form sia --format csv --output notices.csv
    python3 notice_calendar.py --form fidic-yellow --commencement 2026-05-11 --completion 2030-05-10
"""

import argparse
import csv
import io
import sys
from datetime import datetime, timedelta

NOTICE_DATABASES = {
    "fidic-red": {
        "name": "FIDIC Red Book 2017 (Conditions of Contract for Construction)",
        "notices": [
            {"clause": "1.3", "event": "Contractor's Documents submission", "period": "As per Schedule", "recipient": "Engineer", "consequence": "Delay to programme", "category": "Administration"},
            {"clause": "4.12", "event": "Unforeseeable Physical Conditions encountered", "period": "As soon as practicable", "recipient": "Engineer", "consequence": "Loss of entitlement if not notified", "category": "Claims"},
            {"clause": "8.3", "event": "Programme submission", "period": "28 days from Commencement Date", "recipient": "Engineer", "consequence": "Payment may be withheld", "category": "Programme"},
            {"clause": "8.3", "event": "Revised programme submission", "period": "28 days from request/event", "recipient": "Engineer", "consequence": "Payment may be withheld", "category": "Programme"},
            {"clause": "8.4", "event": "EOT application", "period": "Under Clause 20.2 procedure", "recipient": "Engineer", "consequence": "Time-barred under 20.2", "category": "EOT"},
            {"clause": "13.3", "event": "Variation proposal response", "period": "As instructed by Engineer", "recipient": "Engineer", "consequence": "Engineer may instruct alternative", "category": "Variations"},
            {"clause": "14.3", "event": "Interim Payment Statement", "period": "Monthly (end of each month)", "recipient": "Engineer", "consequence": "Late payment", "category": "Payment"},
            {"clause": "14.6", "event": "Engineer issues IPC", "period": "28 days from receiving Statement", "recipient": "Contractor", "consequence": "Financing charges apply", "category": "Payment"},
            {"clause": "14.7", "event": "Employer payment due", "period": "56 days from Statement (if no IPC)", "recipient": "Contractor", "consequence": "Suspension/termination rights", "category": "Payment"},
            {"clause": "15.1", "event": "Notice to Correct", "period": "Reasonable period to correct", "recipient": "Contractor", "consequence": "May lead to termination", "category": "Default"},
            {"clause": "15.2", "event": "Termination by Employer", "period": "14 days notice after Notice to Correct", "recipient": "Contractor", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "16.1", "event": "Contractor's right to suspend", "period": "42 days after IPC due date unpaid", "recipient": "Employer", "consequence": "Works suspended", "category": "Payment"},
            {"clause": "16.2", "event": "Termination by Contractor", "period": "14 days notice", "recipient": "Employer", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "18.2", "event": "Exceptional Event notice", "period": "14 days from awareness", "recipient": "Other Party", "consequence": "Loss of entitlement", "category": "Force Majeure"},
            {"clause": "18.5", "event": "Optional termination (Exceptional Event >84 days)", "period": "7 days notice", "recipient": "Other Party", "consequence": "Contract terminated", "category": "Force Majeure"},
            {"clause": "20.2.1", "event": "Notice of Claim (Contractor)", "period": "28 days from awareness", "recipient": "Engineer", "consequence": "TIME-BARRED — claim lost", "category": "Claims"},
            {"clause": "20.2.4", "event": "Fully detailed claim submission", "period": "84 days from Notice of Claim", "recipient": "Engineer", "consequence": "Claim may be reduced", "category": "Claims"},
            {"clause": "20.2.7", "event": "Engineer notifies late notice", "period": "14 days from receiving late notice", "recipient": "Contractor", "consequence": "If Engineer fails to notify, time-bar may not apply", "category": "Claims"},
            {"clause": "20.1", "event": "Notice of Claim (Employer)", "period": "28 days from awareness", "recipient": "Contractor", "consequence": "TIME-BARRED — claim lost", "category": "Claims"},
            {"clause": "21.4", "event": "Referral to DAAB", "period": "28 days after Engineer's determination (or failure)", "recipient": "DAAB", "consequence": "Lose right to refer", "category": "Disputes"},
            {"clause": "21.4.4", "event": "Notice of Dissatisfaction (NOD)", "period": "28 days after DAAB decision", "recipient": "Other Party", "consequence": "Decision becomes FINAL & BINDING", "category": "Disputes"},
            {"clause": "21.6", "event": "Arbitration notice", "period": "After NOD + 28 days cooling off", "recipient": "Other Party", "consequence": "Must arbitrate or accept DAAB decision", "category": "Disputes"},
        ]
    },
    "fidic-yellow": {
        "name": "FIDIC Yellow Book 2017 (Conditions of Contract for Plant & Design-Build)",
        "notices": [
            {"clause": "5.1", "event": "Contractor's design documents submission", "period": "Per programme", "recipient": "Engineer", "consequence": "Delay to programme", "category": "Design"},
            {"clause": "5.1", "event": "Notify Engineer of errors in Employer's Requirements", "period": "As soon as discovered", "recipient": "Engineer", "consequence": "Contractor bears risk if should have discovered", "category": "Design"},
            {"clause": "8.3", "event": "Programme submission", "period": "28 days from Commencement Date", "recipient": "Engineer", "consequence": "Payment may be withheld", "category": "Programme"},
            {"clause": "13.3", "event": "Variation proposal response", "period": "As instructed by Engineer", "recipient": "Engineer", "consequence": "Engineer may instruct alternative", "category": "Variations"},
            {"clause": "14.3", "event": "Interim Payment Statement", "period": "Monthly", "recipient": "Engineer", "consequence": "Late payment", "category": "Payment"},
            {"clause": "20.2.1", "event": "Notice of Claim (Contractor)", "period": "28 days from awareness", "recipient": "Engineer", "consequence": "TIME-BARRED — claim lost", "category": "Claims"},
            {"clause": "20.2.4", "event": "Fully detailed claim submission", "period": "84 days from Notice of Claim", "recipient": "Engineer", "consequence": "Claim may be reduced", "category": "Claims"},
            {"clause": "20.1", "event": "Notice of Claim (Employer)", "period": "28 days from awareness", "recipient": "Contractor", "consequence": "TIME-BARRED — claim lost", "category": "Claims"},
            {"clause": "21.4", "event": "Referral to DAAB", "period": "28 days after Engineer's determination", "recipient": "DAAB", "consequence": "Lose right to refer", "category": "Disputes"},
            {"clause": "21.4.4", "event": "NOD", "period": "28 days after DAAB decision", "recipient": "Other Party", "consequence": "Decision becomes FINAL & BINDING", "category": "Disputes"},
        ]
    },
    "psscoc": {
        "name": "PSSCOC (Public Sector Standard Conditions of Contract — Construction Works)",
        "notices": [
            {"clause": "14", "event": "Variation order issued by SO", "period": "As instructed", "recipient": "Contractor", "consequence": "Must comply; dispute valuation later", "category": "Variations"},
            {"clause": "23(1)", "event": "EOT application", "period": "28 days from commencement of delay event", "recipient": "SO", "consequence": "May lose EOT entitlement", "category": "EOT"},
            {"clause": "23(1)", "event": "EOT application — particulars", "period": "Include cause, expected duration, mitigation measures", "recipient": "SO", "consequence": "Incomplete application may be rejected", "category": "EOT"},
            {"clause": "24", "event": "Delay certificate issued by SO", "period": "After completion date passed without EOT", "recipient": "Contractor", "consequence": "Liquidated damages apply", "category": "Delay"},
            {"clause": "25", "event": "Completion certificate application", "period": "When works substantially complete", "recipient": "SO", "consequence": "Delays DLP start and payment release", "category": "Completion"},
            {"clause": "27", "event": "Defects notification during maintenance period", "period": "During DLP (typically 12 months)", "recipient": "Contractor", "consequence": "Must rectify at own cost", "category": "Defects"},
            {"clause": "32", "event": "Interim payment valuation", "period": "Monthly", "recipient": "SO", "consequence": "Delays payment", "category": "Payment"},
            {"clause": "33", "event": "Final account submission", "period": "Within period stated in contract", "recipient": "SO", "consequence": "Delays final payment", "category": "Payment"},
            {"clause": "37", "event": "Determination by Employer — notice", "period": "Notice required before determination", "recipient": "Contractor", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "38", "event": "Determination by Contractor", "period": "Notice for non-payment/employer default", "recipient": "Employer", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "40", "event": "Dispute — mediation request", "period": "As per dispute resolution clause", "recipient": "Other Party", "consequence": "Proceed to arbitration if unresolved", "category": "Disputes"},
        ]
    },
    "sia": {
        "name": "SIA Conditions (9th Edition 2010)",
        "notices": [
            {"clause": "11", "event": "Variation instruction by Architect", "period": "As instructed", "recipient": "Contractor", "consequence": "Must comply", "category": "Variations"},
            {"clause": "23(1)", "event": "EOT application", "period": "Written notice required", "recipient": "Architect", "consequence": "May lose entitlement", "category": "EOT"},
            {"clause": "24(1)", "event": "Delay certificate", "period": "Architect certifies after completion date", "recipient": "Contractor", "consequence": "LDs apply from certificate date", "category": "Delay"},
            {"clause": "25", "event": "Completion certificate application", "period": "When substantially complete", "recipient": "Architect", "consequence": "DLP starts; retention release triggered", "category": "Completion"},
            {"clause": "27", "event": "Defects schedule", "period": "During DLP (typically 12 months)", "recipient": "Contractor", "consequence": "Must rectify at own cost", "category": "Defects"},
            {"clause": "30", "event": "Interim certificate by Architect", "period": "Monthly or as specified", "recipient": "Employer", "consequence": "Payment due within 30 days", "category": "Payment"},
            {"clause": "31", "event": "Final account submission", "period": "Within specified period after completion", "recipient": "Architect/QS", "consequence": "Delays final payment", "category": "Payment"},
            {"clause": "33", "event": "Determination by Employer", "period": "Notice required", "recipient": "Contractor", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "34", "event": "Determination by Contractor", "period": "Notice for non-payment", "recipient": "Employer", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "37", "event": "Arbitration notice", "period": "Per dispute resolution clause", "recipient": "Other Party", "consequence": "Dispute referred to arbitration", "category": "Disputes"},
        ]
    },
    "nec4": {
        "name": "NEC4 Engineering and Construction Contract",
        "notices": [
            {"clause": "15.1", "event": "Early warning notification", "period": "As soon as aware of matter that could affect cost/time/quality", "recipient": "Project Manager", "consequence": "Loss of entitlement to additional time/cost", "category": "Early Warning"},
            {"clause": "61.3", "event": "Compensation event notification", "period": "8 weeks from awareness", "recipient": "Project Manager", "consequence": "TIME-BARRED — event not notified", "category": "Claims"},
            {"clause": "62.3", "event": "Compensation event quotation", "period": "3 weeks from instruction to quote", "recipient": "Project Manager", "consequence": "PM may make own assessment", "category": "Claims"},
            {"clause": "64.1", "event": "PM response to CE quotation", "period": "2 weeks from receiving quotation", "recipient": "Contractor", "consequence": "Quotation deemed accepted", "category": "Claims"},
            {"clause": "50.1", "event": "Payment application", "period": "Per assessment dates in Contract Data", "recipient": "Project Manager", "consequence": "Delays payment", "category": "Payment"},
            {"clause": "91.2", "event": "Termination notice", "period": "Per termination table", "recipient": "Other Party", "consequence": "Contract terminated", "category": "Default"},
            {"clause": "W1/W2", "event": "Dispute referral to Adjudicator", "period": "4 weeks from notification of dispute", "recipient": "Adjudicator", "consequence": "Lose right to refer specific dispute", "category": "Disputes"},
        ]
    }
}

def generate_calendar(form, fmt, output=None, commencement=None, completion=None):
    if form not in NOTICE_DATABASES:
        print(f"Error: Unknown form '{form}'. Available: {', '.join(NOTICE_DATABASES.keys())}")
        sys.exit(1)

    db = NOTICE_DATABASES[form]
    notices = db["notices"]

    # Sort by category then clause
    notices.sort(key=lambda x: (x["category"], x["clause"]))

    if fmt == "csv":
        output_stream = open(output, 'w', newline='') if output else sys.stdout
        writer = csv.writer(output_stream)
        writer.writerow(["Contract Form", db["name"]])
        if commencement:
            writer.writerow(["Commencement Date", commencement])
        if completion:
            writer.writerow(["Completion Date", completion])
        writer.writerow([])
        writer.writerow(["Clause", "Event/Obligation", "Notice Period", "Recipient", "Consequence of Non-Compliance", "Category"])
        for n in notices:
            writer.writerow([n["clause"], n["event"], n["period"], n["recipient"], n["consequence"], n["category"]])
        if output:
            output_stream.close()
            print(f"CSV written to {output}")

    elif fmt == "md":
        lines = []
        lines.append(f"# Notice Calendar — {db['name']}")
        lines.append("")
        if commencement:
            lines.append(f"**Commencement Date:** {commencement}")
        if completion:
            lines.append(f"**Completion Date:** {completion}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Group by category
        categories = {}
        for n in notices:
            cat = n["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(n)

        for cat, items in categories.items():
            lines.append(f"## {cat}")
            lines.append("")
            lines.append("| Clause | Event/Obligation | Period | Recipient | Consequence |")
            lines.append("|--------|-----------------|--------|-----------|-------------|")
            for n in items:
                lines.append(f"| {n['clause']} | {n['event']} | {n['period']} | {n['recipient']} | {n['consequence']} |")
            lines.append("")

        result = "\n".join(lines)
        if output:
            with open(output, 'w') as f:
                f.write(result)
            print(f"Markdown written to {output}")
        else:
            print(result)

def main():
    parser = argparse.ArgumentParser(description="Generate notice/obligations calendar for construction contracts")
    parser.add_argument("--form", required=True, choices=list(NOTICE_DATABASES.keys()),
                       help="Contract form")
    parser.add_argument("--format", default="md", choices=["md", "csv"],
                       help="Output format (default: md)")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--commencement", help="Commencement date (YYYY-MM-DD)")
    parser.add_argument("--completion", help="Completion date (YYYY-MM-DD)")
    args = parser.parse_args()
    generate_calendar(args.form, args.format, args.output, args.commencement, args.completion)

if __name__ == "__main__":
    main()
