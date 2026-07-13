#!/usr/bin/env python3
"""
Clawsight UXR Observer — Generate daily report

Reads observations.jsonl and surveys.jsonl for a given day,
generates a comprehensive markdown report with task breakdown and verbatim gallery.

Usage:
    python3 generate_report.py [YYYY-MM-DD]  # defaults to today
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def get_base_path():
    """Get the UXR observer base directory."""
    return Path.home() / ".uxr-observer"

def load_jsonl(filepath):
    """Load all records from a JSONL file."""
    records = []
    if not filepath.exists():
        return records
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def get_session_date_str(args):
    """Parse date argument or use today."""
    if len(args) > 1:
        date_str = args[1]
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Validate format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)
    
    return date_str

def compute_metrics(observations, surveys):
    """Compute summary metrics."""
    total_tasks = len([o for o in observations if o.get("observation_type") == "interaction"])
    total_surveys = len(surveys)
    
    post_task_surveys = [s for s in surveys if s.get("survey_type") == "post_task"]
    end_of_day_surveys = [s for s in surveys if s.get("survey_type") == "end_of_day"]
    
    # Calculate average post-task satisfaction
    ratings = [s.get("responses", {}).get("experience_rating", 0) for s in post_task_surveys]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Count frustration/delight
    frustration_count = len([s for s in post_task_surveys if s.get("responses", {}).get("experienced_frustration") == "yes"])
    delight_count = len([s for s in post_task_surveys if s.get("responses", {}).get("best_part")])
    
    # Overall day rating
    overall_rating = 0
    if end_of_day_surveys:
        overall_rating = end_of_day_surveys[0].get("responses", {}).get("overall_rating", 0)
    
    return {
        "total_tasks": total_tasks,
        "post_task_surveys": len(post_task_surveys),
        "total_surveys": total_surveys,
        "avg_rating": round(avg_rating, 1),
        "overall_rating": overall_rating,
        "frustration_count": frustration_count,
        "delight_count": delight_count,
    }

def build_verbatim_gallery(observations, surveys):
    """Organize all verbatims by theme."""
    gallery = {
        "positive": [],
        "friction": [],
        "expectations": [],
        "suggestions": [],
    }
    
    # Extract verbatims from observations
    for obs in observations:
        for verb in obs.get("verbatims", []):
            header = verb.get("header", "")
            quote = verb.get("quote", "")
            if header and quote:
                if "delight" in header.lower() or "positive" in header.lower():
                    gallery["positive"].append((header, quote))
                elif "frustrat" in header.lower() or "pain" in header.lower():
                    gallery["friction"].append((header, quote))
                elif "expect" in header.lower():
                    gallery["expectations"].append((header, quote))
                elif "suggest" in header.lower() or "change" in header.lower() or "wish" in header.lower():
                    gallery["suggestions"].append((header, quote))
    
    # Extract verbatims from survey responses
    for survey in surveys:
        responses = survey.get("responses", {})
        
        # Best part (positive)
        if responses.get("best_part"):
            gallery["positive"].append(("Valued aspect", responses.get("best_part")))
        
        # Frustration detail
        if responses.get("frustration_detail"):
            gallery["friction"].append(("Reported friction", responses.get("frustration_detail")))
        
        # One change (suggestions)
        if responses.get("one_change"):
            gallery["suggestions"].append(("User-suggested change", responses.get("one_change")))
    
    return gallery

def format_report(date_str, metrics, observations, surveys, gallery, end_of_day):
    """Generate markdown report."""
    lines = []
    
    lines.append(f"# UXR Daily Report — {date_str}\n")
    
    # Summary
    lines.append("## Summary")
    if metrics["total_tasks"] > 0:
        summary = f"Completed {metrics['total_tasks']} tasks with {metrics['post_task_surveys']} post-task surveys. "
        summary += f"Average satisfaction: {metrics['avg_rating']}/5. "
        if metrics["frustration_count"] > 0:
            summary += f"Experienced {metrics['frustration_count']} frustrated moment(s). "
        summary += f"Overall day rating: {metrics['overall_rating']}/5."
        lines.append(summary)
    else:
        lines.append("No tasks completed today.")
    lines.append("")
    
    # By the Numbers
    lines.append("## By the Numbers")
    lines.append(f"- **Tasks completed:** {metrics['total_tasks']}")
    lines.append(f"- **Post-task surveys completed:** {metrics['post_task_surveys']} / {metrics['total_surveys']} ({int(metrics['post_task_surveys']/max(metrics['total_tasks'], 1)*100)}%)")
    lines.append(f"- **Average post-task satisfaction:** {metrics['avg_rating']}/5")
    lines.append(f"- **Overall day rating:** {metrics['overall_rating']}/5")
    lines.append(f"- **Tasks with reported frustration:** {metrics['frustration_count']}")
    lines.append(f"- **Tasks with reported delight:** {metrics['delight_count']}")
    lines.append("")
    
    # Task-by-Task Breakdown
    if observations:
        lines.append("## Task-by-Task Breakdown\n")
        task_num = 1
        for obs in observations:
            if obs.get("observation_type") != "interaction":
                continue
            
            lines.append(f"### Task {task_num}: {obs.get('task_category', 'other').title()}")
            lines.append(f"**What happened:** {obs.get('task_context_summary', 'N/A')}")
            
            # Try to find matching survey
            survey_match = None
            for survey in surveys:
                if survey.get("related_observation_id") == obs.get("id"):
                    survey_match = survey
                    break
            
            if survey_match:
                responses = survey_match.get("responses", {})
                rating = responses.get("experience_rating", "N/A")
                lines.append(f"**Rating:** {rating}/5")
                lines.append(f"**Frustration reported:** {'Yes' if responses.get('experienced_frustration') == 'yes' else 'No'}")
                lines.append("")
                
                if responses.get("rating_rationale"):
                    lines.append("**[User's rationale for rating]**")
                    lines.append(f"> \"{responses.get('rating_rationale')}\"")
                    lines.append("")
                
                if responses.get("frustration_detail"):
                    lines.append("**[What frustrated the user]**")
                    lines.append(f"> \"{responses.get('frustration_detail')}\"")
                    lines.append("")
                
                if responses.get("best_part"):
                    lines.append("**[What the user valued most]**")
                    lines.append(f"> \"{responses.get('best_part')}\"")
                    lines.append("")
            
            friction = obs.get("friction_signals", [])
            sentiment = obs.get("sentiment_signals", [])
            if friction and friction != ["none"]:
                lines.append(f"**Observed friction signals:** {', '.join(friction)}")
            if sentiment:
                lines.append(f"**Observed sentiment signals:** {', '.join(sentiment)}")
            
            lines.append("\n---\n")
            task_num += 1
    
    # Verbatim Gallery
    lines.append("## Verbatim Gallery\n")
    lines.append("All notable quotes organized thematically:\n")
    
    if gallery["positive"]:
        lines.append("### Positive Experiences")
        for header, quote in gallery["positive"]:
            lines.append(f"**[{header}]**")
            lines.append(f"> \"{quote}\"")
            lines.append("")
    
    if gallery["friction"]:
        lines.append("### Pain Points & Frustrations")
        for header, quote in gallery["friction"]:
            lines.append(f"**[{header}]**")
            lines.append(f"> \"{quote}\"")
            lines.append("")
    
    if gallery["expectations"]:
        lines.append("### Expectations & Mental Models")
        for header, quote in gallery["expectations"]:
            lines.append(f"**[{header}]**")
            lines.append(f"> \"{quote}\"")
            lines.append("")
    
    if gallery["suggestions"]:
        lines.append("### Suggestions & Wishes")
        for header, quote in gallery["suggestions"]:
            lines.append(f"**[{header}]**")
            lines.append(f"> \"{quote}\"")
            lines.append("")
    
    # End-of-Day Reflection
    if end_of_day:
        lines.append("## End-of-Day Reflection\n")
        responses = end_of_day.get("responses", {})
        lines.append(f"**Overall day rating:** {responses.get('overall_rating', 'N/A')}/5\n")
        
        if responses.get("rating_rationale"):
            lines.append("**[Why the user gave this score]**")
            lines.append(f"> \"{responses.get('rating_rationale')}\"")
            lines.append("")
        
        if responses.get("frustration_details"):
            lines.append("**[Frustrating moments recalled]**")
            lines.append(f"> \"{responses.get('frustration_details')}\"")
            lines.append("")
        
        if responses.get("delight_details"):
            lines.append("**[What impressed the user]**")
            lines.append(f"> \"{responses.get('delight_details')}\"")
            lines.append("")
        
        if responses.get("one_change"):
            lines.append("**[What the user would change]**")
            lines.append(f"> \"{responses.get('one_change')}\"")
            lines.append("")
        
        if responses.get("additional_thoughts"):
            lines.append("**[Additional thoughts]**")
            lines.append(f"> \"{responses.get('additional_thoughts')}\"")
            lines.append("")
    
    # Patterns & Insights
    lines.append("## Patterns & Insights\n")
    lines.append("### What's Working Well")
    if metrics["delight_count"] > 0:
        lines.append(f"- Users experienced {metrics['delight_count']} moment(s) of delight. Positive interactions contribute to overall satisfaction.")
    else:
        lines.append("- Continue exploring what drives satisfaction.")
    lines.append("")
    
    lines.append("### Recurring Pain Points")
    if metrics["frustration_count"] > 0:
        lines.append(f"- {metrics['frustration_count']} frustrated moment(s) reported. Review friction signals above for patterns.")
    else:
        lines.append("- No major friction points reported today.")
    lines.append("")
    
    lines.append("### Emerging Themes")
    lines.append("- Track patterns across multiple days for deeper insights.")
    lines.append("")
    
    # Recommendations
    lines.append("## Recommendations\n")
    if metrics["frustration_count"] > 0:
        lines.append("1. Investigate reported friction points. Can any be resolved to smooth future workflows?")
    lines.append("2. Maintain practices that drive delight — they're working well.")
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("*This report was generated locally by Clawsight. No data has been transmitted externally.*")
    lines.append(f"*Report file: ~/.uxr-observer/reports/{date_str}-daily-report.md*")
    lines.append("*To share: ask OpenClaw to email it, or download and share it yourself.*")
    
    return "\n".join(lines)

def main():
    date_str = get_session_date_str(sys.argv)
    base_path = get_base_path()
    session_dir = base_path / "sessions" / date_str
    
    # Load data
    observations = load_jsonl(session_dir / "observations.jsonl")
    surveys = load_jsonl(session_dir / "surveys.jsonl")
    
    if not observations and not surveys:
        print(f"No data found for {date_str}", file=sys.stderr)
        return 1
    
    # Compute metrics
    metrics = compute_metrics(observations, surveys)
    
    # Build verbatim gallery
    gallery = build_verbatim_gallery(observations, surveys)
    
    # Get end-of-day survey if exists
    end_of_day = next((s for s in surveys if s.get("survey_type") == "end_of_day"), None)
    
    # Generate report
    report = format_report(date_str, metrics, observations, surveys, gallery, end_of_day)
    
    # Save report
    report_file = base_path / "reports" / f"{date_str}-daily-report.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ Report generated: {report_file}")
    print(f"\nReport preview:")
    print("=" * 60)
    print(report[:500] + "..." if len(report) > 500 else report)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
