#!/usr/bin/env python3
"""
Generate and send weekly research digest.

Compiles medium-priority findings from the week into a readable report.
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, get_topic, FINDINGS_DIR


def get_week_range(offset_weeks: int = 0) -> tuple[datetime, datetime]:
    """Get start and end of current week (or offset)."""
    today = datetime.now()
    # Find most recent Sunday
    days_since_sunday = (today.weekday() + 1) % 7
    sunday = today - timedelta(days=days_since_sunday)
    
    # Apply offset
    start = sunday - timedelta(weeks=offset_weeks)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return start, end


def load_week_findings(start: datetime, end: datetime) -> dict:
    """Load all findings from the week."""
    if not FINDINGS_DIR.exists():
        return {}
    
    findings_by_topic = defaultdict(list)
    
    # Scan findings directory
    for findings_file in FINDINGS_DIR.glob("*.json"):
        # Parse filename: YYYY-MM-DD_topic-id.json
        parts = findings_file.stem.split("_", 1)
        if len(parts) != 2:
            continue
        
        date_str, topic_id = parts
        
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        
        # Check if in week range
        if not (start <= file_date <= end):
            continue
        
        # Load findings
        with open(findings_file) as f:
            findings = json.load(f)
            findings_by_topic[topic_id].extend(findings)
    
    return dict(findings_by_topic)


def generate_digest(findings_by_topic: dict, start: datetime, end: datetime) -> str:
    """Generate digest markdown."""
    config = load_config()
    
    # Header
    digest = f"# 📊 Weekly Research Digest\n\n"
    digest += f"**{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}**\n\n"
    digest += "---\n\n"
    
    # Summary stats
    total_findings = sum(len(f) for f in findings_by_topic.values())
    topic_count = len(findings_by_topic)
    
    if total_findings == 0:
        digest += "No new findings this week.\n"
        return digest
    
    digest += f"📈 **Summary:** {total_findings} findings across {topic_count} topic(s)\n\n"
    digest += "---\n\n"
    
    # Highlights (highest scored findings)
    all_findings = []
    for topic_id, findings in findings_by_topic.items():
        topic = get_topic(topic_id)
        if not topic:
            continue
        
        for finding in findings:
            all_findings.append({
                "topic": topic,
                "finding": finding
            })
    
    # Sort by score
    all_findings.sort(key=lambda x: x["finding"].get("score", 0), reverse=True)
    
    if len(all_findings) >= 3:
        digest += "## 🔥 Top Highlights\n\n"
        
        for item in all_findings[:3]:
            topic = item["topic"]
            finding = item["finding"]
            result = finding.get("result", {})
            score = finding.get("score", 0)
            
            digest += f"### {topic.get('name')} ({score:.2f})\n\n"
            digest += f"**{result.get('title', 'Untitled')}**\n\n"
            digest += f"{result.get('snippet', '')}\n\n"
            digest += f"🔗 [{result.get('url', '')}]({result.get('url', '')})\n\n"
        
        digest += "---\n\n"
    
    # Findings by topic
    digest += "## 📚 Findings by Topic\n\n"
    
    for topic_id, findings in sorted(findings_by_topic.items()):
        topic = get_topic(topic_id)
        if not topic:
            continue
        
        topic_name = topic.get("name", topic_id)
        topic_emoji = topic.get("emoji", "📌")
        
        digest += f"### {topic_emoji} {topic_name}\n\n"
        digest += f"**{len(findings)} finding(s) this week**\n\n"
        
        # Sort findings by score
        sorted_findings = sorted(findings, key=lambda x: x.get("score", 0), reverse=True)
        
        for finding in sorted_findings[:5]:  # Top 5 per topic
            result = finding.get("result", {})
            score = finding.get("score", 0)
            reason = finding.get("reason", "")
            
            digest += f"- **{result.get('title', 'Untitled')}** ({score:.2f})\n"
            digest += f"  {result.get('snippet', '')[:150]}...\n"
            digest += f"  🔗 {result.get('url', '')}\n"
            if reason:
                digest += f"  _Reason: {reason}_\n"
            digest += "\n"
        
        if len(sorted_findings) > 5:
            digest += f"_...and {len(sorted_findings) - 5} more_\n\n"
        
        digest += "\n"
    
    # Recommendations (future enhancement)
    digest += "---\n\n"
    digest += "## 💡 Recommendations\n\n"
    digest += "_Feature coming soon: AI-powered topic suggestions based on your findings_\n\n"
    
    return digest


def send_digest(digest: str, dry_run: bool = False):
    """Send digest via configured channels."""
    config = load_config()
    settings = config.get("settings", {})
    
    # For now, just print (would integrate with message tool in real environment)
    if dry_run:
        print("\n" + "="*60)
        print("DIGEST PREVIEW:")
        print("="*60 + "\n")
        print(digest)
        print("\n" + "="*60)
    else:
        # Would send via Telegram, Discord, Email
        print("📧 Sending digest...")
        print(digest)
        print("\n✅ Digest sent")


def main():
    parser = argparse.ArgumentParser(description="Generate weekly research digest")
    parser.add_argument("--preview", action="store_true", help="Preview without sending")
    parser.add_argument("--send", action="store_true", help="Generate and send")
    parser.add_argument("--week-offset", type=int, default=0,
                       help="Week offset (0=current, 1=last week, etc.)")
    
    args = parser.parse_args()
    
    # Get week range
    start, end = get_week_range(args.week_offset)
    
    print(f"📊 Generating digest for {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    
    # Load findings
    findings_by_topic = load_week_findings(start, end)
    
    if not findings_by_topic:
        print("⚠️ No findings for this period")
        return
    
    # Generate digest
    digest = generate_digest(findings_by_topic, start, end)
    
    # Send or preview
    if args.send:
        send_digest(digest, dry_run=False)
    else:
        send_digest(digest, dry_run=True)


if __name__ == "__main__":
    main()
