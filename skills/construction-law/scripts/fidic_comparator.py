#!/usr/bin/env python3
"""
FIDIC Contract Form Comparator
Side-by-side comparison of FIDIC Red, Yellow, Silver, and Emerald Books.

Usage:
    python3 fidic_comparator.py --forms red,yellow,silver
    python3 fidic_comparator.py --forms red,yellow --topic risk
    python3 fidic_comparator.py --forms red,silver --topic all --format csv --output comparison.csv
"""

import argparse
import sys

COMPARISONS = {
    "overview": {
        "title": "Contract Overview",
        "items": [
            {"aspect": "Full Name", "red": "Conditions of Contract for Construction", "yellow": "Conditions of Contract for Plant & Design-Build", "silver": "Conditions of Contract for EPC/Turnkey Projects", "emerald": "Conditions of Contract for Underground Works"},
            {"aspect": "Typical Use", "red": "Employer-designed traditional works", "yellow": "Design & Build projects", "silver": "Large industrial, power, PPP/BOT", "emerald": "Tunnelling, underground construction"},
            {"aspect": "Design Responsibility", "red": "Employer", "yellow": "Contractor", "silver": "Contractor", "emerald": "Shared (GBR-based)"},
            {"aspect": "Payment Basis", "red": "Re-measurement (item rates)", "yellow": "Lump sum", "silver": "Lump sum (fixed price)", "emerald": "Re-measurement with GBR adjustment"},
            {"aspect": "Engineer Role", "red": "Yes — administers contract", "yellow": "Yes — administers contract", "silver": "No Engineer — Employer's Representative", "emerald": "Yes — with geotechnical expertise"},
            {"aspect": "Price Level", "red": "Lowest bid price", "yellow": "Medium bid price", "silver": "Highest bid price", "emerald": "Medium-High"},
            {"aspect": "Employer Involvement", "red": "High (designs + supervises)", "yellow": "Medium (sets requirements)", "silver": "Low (turnkey delivery)", "emerald": "Medium (GBR preparation)"},
        ]
    },
    "risk": {
        "title": "Risk Allocation",
        "items": [
            {"aspect": "Design Risk", "red": "Employer", "yellow": "Contractor", "silver": "Contractor", "emerald": "Shared per GBR"},
            {"aspect": "Quantity Risk", "red": "Employer (re-measurement)", "yellow": "Contractor (lump sum)", "silver": "Contractor (lump sum)", "emerald": "Employer (re-measurement)"},
            {"aspect": "Ground Conditions", "red": "Employer (unforeseeable — Cl.4.12)", "yellow": "Shared (Cl.4.12 applies)", "silver": "Contractor (deemed included)", "emerald": "Shared per GBR baseline"},
            {"aspect": "Exceptional Climate", "red": "Employer (EOT)", "yellow": "Employer (EOT)", "silver": "Contractor (no relief)", "emerald": "Employer (EOT)"},
            {"aspect": "Force Majeure", "red": "Shared (Cl.18)", "yellow": "Shared (Cl.18)", "silver": "Limited Contractor relief", "emerald": "Shared (Cl.18)"},
            {"aspect": "Changes in Law", "red": "Employer (Cl.13.6)", "yellow": "Employer (Cl.13.6)", "silver": "Contractor (limited relief)", "emerald": "Employer (Cl.13.6)"},
            {"aspect": "Errors in Requirements", "red": "Employer (own design)", "yellow": "Shared (Contractor must check)", "silver": "Contractor (deemed verified)", "emerald": "Per GBR allocation"},
            {"aspect": "Design Standard of Care", "red": "N/A (Employer designs)", "yellow": "Fitness for purpose", "silver": "Fitness for purpose", "emerald": "Fitness for purpose (within GBR)"},
            {"aspect": "Overall Risk to Contractor", "red": "LOW", "yellow": "MEDIUM", "silver": "HIGH", "emerald": "MEDIUM"},
        ]
    },
    "claims": {
        "title": "Claims & Time-Bars",
        "items": [
            {"aspect": "Notice of Claim", "red": "28 days (Cl.20.2.1)", "yellow": "28 days (Cl.20.2.1)", "silver": "28 days (Cl.20.2.1)", "emerald": "28 days (Cl.20.2.1)"},
            {"aspect": "Time-Bar Effect", "red": "Claim deemed time-barred", "yellow": "Claim deemed time-barred", "silver": "Claim deemed time-barred", "emerald": "Claim deemed time-barred"},
            {"aspect": "Detailed Claim", "red": "84 days from Notice", "yellow": "84 days from Notice", "silver": "84 days from Notice", "emerald": "84 days from Notice"},
            {"aspect": "Late Notice Safeguard (Cl.20.2.7)", "red": "Engineer must notify if late", "yellow": "Engineer must notify if late", "silver": "ER must notify if late", "emerald": "Engineer must notify if late"},
            {"aspect": "EOT Entitlement", "red": "Broad (Cl.8.4/8.5)", "yellow": "Broad (Cl.8.4/8.5)", "silver": "Very limited", "emerald": "Broad + GBR-based"},
            {"aspect": "Unforeseeable Conditions", "red": "Entitled (Cl.4.12)", "yellow": "Entitled (Cl.4.12)", "silver": "NOT entitled (deemed included)", "emerald": "Per GBR — better than baseline = Employer benefit"},
            {"aspect": "Variation Procedure", "red": "Engineer instructs (Cl.13)", "yellow": "Engineer instructs (Cl.13)", "silver": "ER instructs (limited)", "emerald": "Engineer instructs (Cl.13)"},
            {"aspect": "Cost Definition", "red": "Expenditure + overhead, NOT profit", "yellow": "Expenditure + overhead, NOT profit", "silver": "Expenditure + overhead, NOT profit", "emerald": "Expenditure + overhead, NOT profit"},
            {"aspect": "Cost + Profit Events", "red": "Cl.4.12, some Cl.13 events", "yellow": "Cl.4.12, some Cl.13 events", "silver": "Very few", "emerald": "GBR-related events"},
        ]
    },
    "disputes": {
        "title": "Dispute Resolution",
        "items": [
            {"aspect": "Dispute Board", "red": "Standing DAAB (mandatory)", "yellow": "Standing DAAB (mandatory)", "silver": "Ad hoc DAAB (optional)", "emerald": "Standing DAAB (mandatory)"},
            {"aspect": "DAAB Decision Period", "red": "84 days", "yellow": "84 days", "silver": "84 days", "emerald": "84 days"},
            {"aspect": "DAAB Decision Binding?", "red": "Binding (subject to NOD)", "yellow": "Binding (subject to NOD)", "silver": "Binding (subject to NOD)", "emerald": "Binding (subject to NOD)"},
            {"aspect": "NOD Period", "red": "28 days after DAAB decision", "yellow": "28 days after DAAB decision", "silver": "28 days after DAAB decision", "emerald": "28 days after DAAB decision"},
            {"aspect": "Arbitration", "red": "After NOD + 28 days", "yellow": "After NOD + 28 days", "silver": "After NOD + 28 days", "emerald": "After NOD + 28 days"},
            {"aspect": "Non-compliance Enforcement", "red": "Direct to arbitration (Persero)", "yellow": "Direct to arbitration (Persero)", "silver": "Direct to arbitration", "emerald": "Direct to arbitration"},
            {"aspect": "Engineer Neutrality", "red": "Must act neutrally (Cl.3.7)", "yellow": "Must act neutrally (Cl.3.7)", "silver": "No Engineer role", "emerald": "Must act neutrally (Cl.3.7)"},
        ]
    },
    "payment": {
        "title": "Payment Mechanisms",
        "items": [
            {"aspect": "Interim Payments", "red": "Monthly (Cl.14.3)", "yellow": "Monthly (Cl.14.3)", "silver": "Per milestones or monthly", "emerald": "Monthly (Cl.14.3)"},
            {"aspect": "IPC by Engineer", "red": "28 days from Statement", "yellow": "28 days from Statement", "silver": "N/A (no Engineer)", "emerald": "28 days from Statement"},
            {"aspect": "Employer Payment", "red": "56 days from Statement", "yellow": "56 days from Statement", "silver": "56 days from Statement", "emerald": "56 days from Statement"},
            {"aspect": "Late Payment Remedy", "red": "Financing charges (Cl.14.8)", "yellow": "Financing charges (Cl.14.8)", "silver": "Financing charges (Cl.14.8)", "emerald": "Financing charges (Cl.14.8)"},
            {"aspect": "Right to Suspend", "red": "42 days unpaid (Cl.16.1)", "yellow": "42 days unpaid (Cl.16.1)", "silver": "42 days unpaid (Cl.16.1)", "emerald": "42 days unpaid (Cl.16.1)"},
            {"aspect": "Retention", "red": "Per Contract Data", "yellow": "Per Contract Data", "silver": "Per Contract Data", "emerald": "Per Contract Data"},
            {"aspect": "Advance Payment", "red": "Per Contract Data (Cl.14.2)", "yellow": "Per Contract Data (Cl.14.2)", "silver": "Per Contract Data (Cl.14.2)", "emerald": "Per Contract Data (Cl.14.2)"},
            {"aspect": "Price Adjustment", "red": "Cl.13.7 (if applicable)", "yellow": "Cl.13.7 (if applicable)", "silver": "Usually excluded", "emerald": "Cl.13.7 (if applicable)"},
        ]
    },
    "termination": {
        "title": "Termination Provisions",
        "items": [
            {"aspect": "Employer Termination", "red": "Cl.15.2 (14 days notice after Notice to Correct)", "yellow": "Cl.15.2 (same)", "silver": "Cl.15.2 (same)", "emerald": "Cl.15.2 (same)"},
            {"aspect": "Employer Convenience", "red": "Cl.15.5 (at any time)", "yellow": "Cl.15.5 (at any time)", "silver": "Cl.15.5 (at any time)", "emerald": "Cl.15.5 (at any time)"},
            {"aspect": "Contractor Termination", "red": "Cl.16.2 (14 days notice)", "yellow": "Cl.16.2 (same)", "silver": "Cl.16.2 (same)", "emerald": "Cl.16.2 (same)"},
            {"aspect": "Exceptional Event Termination", "red": "Cl.18.5 (>84 days, 7 days notice)", "yellow": "Cl.18.5 (same)", "silver": "Limited", "emerald": "Cl.18.5 (same)"},
            {"aspect": "Payment on Termination", "red": "Cl.15.3/16.3 (valuation)", "yellow": "Cl.15.3/16.3 (same)", "silver": "Cl.15.3/16.3 (same)", "emerald": "Cl.15.3/16.3 (same)"},
        ]
    }
}

FORM_NAMES = {
    "red": "Red Book",
    "yellow": "Yellow Book",
    "silver": "Silver Book",
    "emerald": "Emerald Book"
}

def compare(forms, topic, fmt, output):
    form_list = [f.strip().lower() for f in forms.split(",")]
    for f in form_list:
        if f not in FORM_NAMES:
            print(f"Error: Unknown form '{f}'. Available: {', '.join(FORM_NAMES.keys())}")
            sys.exit(1)

    topics = list(COMPARISONS.keys()) if topic == "all" else [topic]
    for t in topics:
        if t not in COMPARISONS:
            print(f"Error: Unknown topic '{t}'. Available: {', '.join(COMPARISONS.keys())}, all")
            sys.exit(1)

    if fmt == "md":
        lines = ["# FIDIC Contract Comparison", "",
                 f"**Forms:** {', '.join(FORM_NAMES[f] for f in form_list)}",
                 f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
                 ""]

        for t in topics:
            comp = COMPARISONS[t]
            lines.append(f"## {comp['title']}")
            lines.append("")
            header = "| Aspect | " + " | ".join(FORM_NAMES[f] for f in form_list) + " |"
            sep = "|--------|" + "|".join("------" for _ in form_list) + "|"
            lines.append(header)
            lines.append(sep)
            for item in comp["items"]:
                row = f"| **{item['aspect']}** | " + " | ".join(item.get(f, "N/A") for f in form_list) + " |"
                lines.append(row)
            lines.append("")

        result = "\n".join(lines)
        if output:
            with open(output, 'w') as f:
                f.write(result)
            print(f"Comparison written to {output}")
        else:
            print(result)

    elif fmt == "csv":
        import csv
        out = open(output, 'w', newline='') if output else sys.stdout
        writer = csv.writer(out)
        for t in topics:
            comp = COMPARISONS[t]
            writer.writerow([comp["title"]])
            writer.writerow(["Aspect"] + [FORM_NAMES[f] for f in form_list])
            for item in comp["items"]:
                writer.writerow([item["aspect"]] + [item.get(f, "N/A") for f in form_list])
            writer.writerow([])
        if output:
            out.close()
            print(f"CSV written to {output}")

def main():
    parser = argparse.ArgumentParser(description="FIDIC Contract Form Comparator")
    parser.add_argument("--forms", required=True, help="Comma-separated forms: red,yellow,silver,emerald")
    parser.add_argument("--topic", default="all",
                       choices=list(COMPARISONS.keys()) + ["all"],
                       help="Comparison topic (default: all)")
    parser.add_argument("--format", default="md", choices=["md", "csv"])
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    compare(args.forms, args.topic, args.format, args.output)

if __name__ == "__main__":
    main()
