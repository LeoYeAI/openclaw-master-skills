#!/usr/bin/env python3
"""Compare before/after transformation with side-by-side detection scores."""
import argparse, sys
from pathlib import Path
from detect import detect
from transform import transform

def main():
    parser = argparse.ArgumentParser(description="Compare AI detection before/after transformation")
    parser.add_argument("input", nargs="?", help="Input file (or stdin)")
    parser.add_argument("-a", "--aggressive", action="store_true", help="Use aggressive mode")
    parser.add_argument("-o", "--output", help="Save transformed text to file")
    args = parser.parse_args()
    
    text = Path(args.input).read_text() if args.input else sys.stdin.read()
    
    before = detect(text)
    transformed, changes = transform(text, aggressive=args.aggressive)
    after = detect(transformed)
    
    icons = {"very high": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    
    print(f"\n{'='*60}")
    print("BEFORE → AFTER COMPARISON")
    print(f"{'='*60}\n")
    
    print(f"{'Metric':<25} {'Before':<15} {'After':<15} {'Change':<10}")
    print(f"{'-'*60}")
    
    issue_diff = after.total_issues - before.total_issues
    issue_sign = "+" if issue_diff > 0 else ""
    print(f"{'Issues':<25} {before.total_issues:<15} {after.total_issues:<15} {issue_sign}{issue_diff}")
    
    print(f"{'AI Probability':<25} {icons.get(before.ai_probability,'')} {before.ai_probability:<12} {icons.get(after.ai_probability,'')} {after.ai_probability:<12}")
    print(f"{'Word Count':<25} {before.word_count:<15} {after.word_count:<15} {after.word_count - before.word_count:+}")
    
    if changes:
        print(f"\n{'='*60}")
        print(f"TRANSFORMATIONS ({len(changes)})")
        print(f"{'='*60}")
        for c in changes:
            print(f"  • {c}")
    
    reduction = before.total_issues - after.total_issues
    if reduction > 0:
        pct = (reduction / before.total_issues * 100) if before.total_issues else 0
        print(f"\n✓ Reduced {reduction} issues ({pct:.0f}% improvement)")
    elif reduction < 0:
        print(f"\n⚠ Issues increased by {-reduction}")
    else:
        print(f"\n— No change in issue count")
    
    if args.output:
        Path(args.output).write_text(transformed)
        print(f"\n→ Saved to {args.output}")

if __name__ == "__main__":
    main()
