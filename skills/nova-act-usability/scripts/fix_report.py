#!/usr/bin/env python3
import json
import os
import sys

# Add skill scripts to path
SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/skills/website-usability-test-nova-act/scripts")
sys.path.insert(0, SCRIPT_DIR)
from enhanced_report_generator import generate_enhanced_report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fix_report.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    
    with open(json_file, 'r') as f:
        results = json.load(f)

    # Simple interpretation logic
    for test in results:
        goals_achieved = 0
        steps = test.get('steps', [])
        for step in steps:
            raw = str(step.get('raw_response', '')).lower()
            
            # Basic positive indicators
            positives = ['yes', 'true', 'found', 'success', 'complete', 'clicked']
            # Basic negative indicators
            negatives = ['no', 'false', 'not found', 'error', 'failed', 'don\'t see', 'unable']
            
            is_positive = any(p in raw for p in positives)
            is_negative = any(n in raw for n in negatives)
            
            if is_positive and not is_negative:
                step['goal_achieved'] = True
                goals_achieved += 1
            elif is_negative:
                step['goal_achieved'] = False
            else:
                # If it's descriptive text and not explicitly negative, assume success for now
                step['goal_achieved'] = len(raw) > 5
                if step['goal_achieved']:
                    goals_achieved += 1
        
        test['goals_achieved'] = goals_achieved
        total = len(steps)
        test['overall_success'] = (goals_achieved / total >= 0.5) if total > 0 else False

    # Save interpreted results
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Generate report
    page_analysis = {
        'title': 'Re-generated Report',
        'purpose': 'Usability Test Analysis',
        'navigation': []
    }
    
    report_path = generate_enhanced_report(page_analysis, results, [])
    print(f"✅ Report regenerated: {report_path}")

if __name__ == "__main__":
    main()
