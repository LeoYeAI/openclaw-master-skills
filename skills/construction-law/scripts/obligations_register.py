#!/usr/bin/env python3
"""
Obligations Register Generator
Creates a comprehensive obligations register from contract form selection.
Tracks both Contractor and Employer obligations with deadlines and status.

Usage:
    python3 obligations_register.py --form fidic-red --format md
    python3 obligations_register.py --form psscoc --format csv --output obligations.csv
    python3 obligations_register.py --form fidic-red --party contractor --format md
"""

import argparse
import csv
import sys
from datetime import datetime

OBLIGATIONS = {
    "fidic-red": {
        "name": "FIDIC Red Book 2017",
        "contractor": [
            {"clause": "1.3", "obligation": "Submit Contractor's Documents per Schedule", "timing": "Per Contract Data", "priority": "High", "category": "Administration"},
            {"clause": "1.6", "obligation": "Execute Contract Agreement", "timing": "28 days from Letter of Acceptance", "priority": "High", "category": "Administration"},
            {"clause": "2.2", "obligation": "Comply with permits, licences, approvals", "timing": "Ongoing", "priority": "High", "category": "Compliance"},
            {"clause": "4.1", "obligation": "Design, execute and complete Works", "timing": "Per programme", "priority": "Critical", "category": "Works"},
            {"clause": "4.2", "obligation": "Provide Performance Security", "timing": "28 days from Letter of Acceptance", "priority": "Critical", "category": "Financial"},
            {"clause": "4.4", "obligation": "Appoint Contractor's Representative", "timing": "Before Commencement", "priority": "High", "category": "Administration"},
            {"clause": "4.8", "obligation": "Health & Safety obligations", "timing": "Ongoing", "priority": "Critical", "category": "Safety"},
            {"clause": "4.10", "obligation": "Collect and maintain Site data records", "timing": "Ongoing", "priority": "Medium", "category": "Records"},
            {"clause": "4.12", "obligation": "Notify Engineer of unforeseeable physical conditions", "timing": "As soon as practicable", "priority": "Critical", "category": "Claims"},
            {"clause": "4.18", "obligation": "Environmental protection measures", "timing": "Ongoing", "priority": "High", "category": "Compliance"},
            {"clause": "4.19", "obligation": "Supply electricity, water, other services", "timing": "As needed", "priority": "Medium", "category": "Works"},
            {"clause": "6.1", "obligation": "Employ suitable staff and labour", "timing": "Ongoing", "priority": "High", "category": "Resources"},
            {"clause": "7.1", "obligation": "Execute works with proper workmanship", "timing": "Ongoing", "priority": "Critical", "category": "Works"},
            {"clause": "8.1", "obligation": "Commence Works", "timing": "Per Commencement Date", "priority": "Critical", "category": "Programme"},
            {"clause": "8.3", "obligation": "Submit programme", "timing": "28 days from Commencement", "priority": "High", "category": "Programme"},
            {"clause": "8.3", "obligation": "Submit revised programme when required", "timing": "28 days from event/request", "priority": "High", "category": "Programme"},
            {"clause": "8.7", "obligation": "Proceed with due expedition and without delay", "timing": "Ongoing", "priority": "Critical", "category": "Programme"},
            {"clause": "9.1", "obligation": "Carry out Tests on Completion", "timing": "Before Completion", "priority": "High", "category": "Testing"},
            {"clause": "10.1", "obligation": "Apply for Taking Over Certificate", "timing": "When Works substantially complete", "priority": "High", "category": "Completion"},
            {"clause": "11.1", "obligation": "Rectify defects during DNP", "timing": "During Defects Notification Period", "priority": "High", "category": "Defects"},
            {"clause": "14.3", "obligation": "Submit monthly Interim Payment Statements", "timing": "Monthly (end of each month)", "priority": "High", "category": "Payment"},
            {"clause": "14.11", "obligation": "Submit Final Statement", "timing": "Within 84 days of DNP expiry", "priority": "High", "category": "Payment"},
            {"clause": "17.1", "obligation": "Indemnify Employer (third party claims)", "timing": "Ongoing", "priority": "High", "category": "Insurance"},
            {"clause": "18.1", "obligation": "Insure Works (CAR/EAR)", "timing": "Before Commencement", "priority": "Critical", "category": "Insurance"},
            {"clause": "20.2.1", "obligation": "Give Notice of Claim within 28 days", "timing": "28 days from awareness", "priority": "Critical", "category": "Claims"},
            {"clause": "20.2.3", "obligation": "Maintain contemporary records for claims", "timing": "Ongoing", "priority": "High", "category": "Records"},
            {"clause": "20.2.4", "obligation": "Submit fully detailed claim", "timing": "84 days from Notice of Claim", "priority": "Critical", "category": "Claims"},
        ],
        "employer": [
            {"clause": "1.6", "obligation": "Execute Contract Agreement", "timing": "28 days from Letter of Acceptance", "priority": "High", "category": "Administration"},
            {"clause": "2.1", "obligation": "Give right of access to and possession of Site", "timing": "Per Contract Data / programme", "priority": "Critical", "category": "Access"},
            {"clause": "2.4", "obligation": "Provide financial evidence/arrangements", "timing": "28 days from Contractor's request", "priority": "High", "category": "Financial"},
            {"clause": "3.1", "obligation": "Appoint Engineer", "timing": "Before Commencement", "priority": "Critical", "category": "Administration"},
            {"clause": "14.6", "obligation": "Engineer to issue IPC", "timing": "28 days from receiving Statement", "priority": "Critical", "category": "Payment"},
            {"clause": "14.7", "obligation": "Pay amount certified in IPC", "timing": "56 days from Statement date", "priority": "Critical", "category": "Payment"},
            {"clause": "14.9", "obligation": "Pay Advance Payment", "timing": "Per Contract Data", "priority": "High", "category": "Payment"},
            {"clause": "14.13", "obligation": "Issue Final Payment Certificate", "timing": "28 days after agreement/determination", "priority": "High", "category": "Payment"},
            {"clause": "20.1", "obligation": "Give Notice of Employer's Claim within 28 days", "timing": "28 days from awareness", "priority": "Critical", "category": "Claims"},
        ]
    },
    "psscoc": {
        "name": "PSSCOC (Construction Works)",
        "contractor": [
            {"clause": "4", "obligation": "Execute and complete Works", "timing": "Per programme", "priority": "Critical", "category": "Works"},
            {"clause": "5", "obligation": "Provide Performance Bond", "timing": "Before Commencement", "priority": "Critical", "category": "Financial"},
            {"clause": "7", "obligation": "No assignment without consent", "timing": "Ongoing", "priority": "High", "category": "Administration"},
            {"clause": "10", "obligation": "Appoint site agent/supervisor", "timing": "Before Commencement", "priority": "High", "category": "Administration"},
            {"clause": "11", "obligation": "Provide adequate workforce", "timing": "Ongoing", "priority": "High", "category": "Resources"},
            {"clause": "16", "obligation": "Take care of Works, materials, plant", "timing": "Until completion", "priority": "High", "category": "Works"},
            {"clause": "19", "obligation": "Provide insurance (CAR, TPL, WIC)", "timing": "Before Commencement", "priority": "Critical", "category": "Insurance"},
            {"clause": "23(1)", "obligation": "Apply for EOT within 28 days", "timing": "28 days from delay event", "priority": "Critical", "category": "EOT"},
            {"clause": "27", "obligation": "Rectify defects during maintenance period", "timing": "During DLP", "priority": "High", "category": "Defects"},
            {"clause": "32", "obligation": "Submit monthly progress claims", "timing": "Monthly", "priority": "High", "category": "Payment"},
            {"clause": "33", "obligation": "Submit final account", "timing": "Per contract period", "priority": "High", "category": "Payment"},
        ],
        "employer": [
            {"clause": "20", "obligation": "Give possession of site", "timing": "Per programme", "priority": "Critical", "category": "Access"},
            {"clause": "25", "obligation": "Issue Completion Certificate", "timing": "When works substantially complete", "priority": "High", "category": "Completion"},
            {"clause": "32", "obligation": "Certify and pay interim valuations", "timing": "Monthly", "priority": "Critical", "category": "Payment"},
            {"clause": "33", "obligation": "Certify final account", "timing": "Per contract terms", "priority": "High", "category": "Payment"},
        ]
    },
    "sia": {
        "name": "SIA Conditions (9th Edition)",
        "contractor": [
            {"clause": "1", "obligation": "Execute Works per contract documents", "timing": "Per programme", "priority": "Critical", "category": "Works"},
            {"clause": "5", "obligation": "Provide Performance Bond", "timing": "Per contract", "priority": "Critical", "category": "Financial"},
            {"clause": "10", "obligation": "Appoint site supervisor", "timing": "Before Commencement", "priority": "High", "category": "Administration"},
            {"clause": "13", "obligation": "Provide insurance", "timing": "Before Commencement", "priority": "Critical", "category": "Insurance"},
            {"clause": "23", "obligation": "Apply for EOT in writing", "timing": "Written notice required", "priority": "Critical", "category": "EOT"},
            {"clause": "27", "obligation": "Rectify defects during DLP", "timing": "During DLP", "priority": "High", "category": "Defects"},
            {"clause": "31", "obligation": "Submit progress claims", "timing": "Monthly or as specified", "priority": "High", "category": "Payment"},
            {"clause": "31", "obligation": "Submit final account", "timing": "Per contract period", "priority": "High", "category": "Payment"},
        ],
        "employer": [
            {"clause": "3", "obligation": "Appoint Architect", "timing": "Before Commencement", "priority": "Critical", "category": "Administration"},
            {"clause": "20", "obligation": "Give possession of site", "timing": "Per programme", "priority": "Critical", "category": "Access"},
            {"clause": "25", "obligation": "Issue Completion Certificate", "timing": "When substantially complete", "priority": "High", "category": "Completion"},
            {"clause": "30", "obligation": "Pay certified amounts within 30 days", "timing": "30 days from certificate", "priority": "Critical", "category": "Payment"},
        ]
    }
}

def generate_register(form, party, fmt, output=None):
    if form not in OBLIGATIONS:
        print(f"Error: Unknown form '{form}'. Available: {', '.join(OBLIGATIONS.keys())}")
        sys.exit(1)

    db = OBLIGATIONS[form]
    parties = [party] if party != "both" else ["contractor", "employer"]

    if fmt == "md":
        lines = [f"# Obligations Register — {db['name']}", "",
                 f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

        for p in parties:
            items = db.get(p, [])
            if not items:
                continue
            lines.append(f"## {p.title()} Obligations")
            lines.append("")
            lines.append("| # | Clause | Obligation | Timing | Priority | Category | Status |")
            lines.append("|---|--------|-----------|--------|----------|----------|--------|")
            for i, ob in enumerate(items, 1):
                lines.append(f"| {i} | {ob['clause']} | {ob['obligation']} | {ob['timing']} | {ob['priority']} | {ob['category']} | ⬜ Pending |")
            lines.append("")

        result = "\n".join(lines)
        if output:
            with open(output, 'w') as f:
                f.write(result)
            print(f"Register written to {output}")
        else:
            print(result)

    elif fmt == "csv":
        out = open(output, 'w', newline='') if output else sys.stdout
        writer = csv.writer(out)
        writer.writerow(["Contract Form", db["name"]])
        writer.writerow(["Generated", datetime.now().strftime('%Y-%m-%d %H:%M')])
        writer.writerow([])
        writer.writerow(["Party", "Clause", "Obligation", "Timing", "Priority", "Category", "Status", "Notes"])
        for p in parties:
            for ob in db.get(p, []):
                writer.writerow([p.title(), ob["clause"], ob["obligation"], ob["timing"], ob["priority"], ob["category"], "Pending", ""])
        if output:
            out.close()
            print(f"CSV written to {output}")

def main():
    parser = argparse.ArgumentParser(description="Generate obligations register for construction contracts")
    parser.add_argument("--form", required=True, choices=list(OBLIGATIONS.keys()))
    parser.add_argument("--party", default="both", choices=["contractor", "employer", "both"])
    parser.add_argument("--format", default="md", choices=["md", "csv"])
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    generate_register(args.form, args.party, args.format, args.output)

if __name__ == "__main__":
    main()

