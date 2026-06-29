#!/usr/bin/env python3
"""
Process pending alerts from the queue.

This script outputs alerts in a format that the OpenClaw agent can parse
and send via the message tool.

Usage:
    python3 process_alerts.py              # Show pending alerts
    python3 process_alerts.py --json       # Output as JSON for agent processing
    python3 process_alerts.py --mark-sent  # Mark all as sent (after agent sends them)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import get_pending_alerts, mark_alert_sent, clear_old_alerts


def format_alert_message(alert: dict) -> str:
    """Format an alert as a nice message."""
    if alert.get("message"):
        return alert["message"]
    
    # Build message from components
    emoji_map = {"high": "🔥", "medium": "📌", "low": "📝"}
    emoji = emoji_map.get(alert.get("priority", "medium"), "📌")
    
    lines = [
        f"{emoji} **{alert.get('topic_name', 'Alert')}**",
        "",
        f"**{alert.get('title', 'Untitled')}**",
        "",
    ]
    
    snippet = alert.get("snippet", "")
    if snippet:
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."
        lines.append(snippet)
        lines.append("")
    
    if alert.get("context"):
        lines.append(f"💡 _Context: {alert['context']}_")
        lines.append("")
    
    if alert.get("url"):
        lines.append(f"🔗 {alert['url']}")
        lines.append("")
    
    lines.append(f"📊 _Score: {alert.get('score', 0):.2f} | {alert.get('reason', '')}_")
    
    return "\n".join(lines)


def show_pending_alerts():
    """Show pending alerts in human-readable format."""
    alerts = get_pending_alerts()
    
    if not alerts:
        print("✅ No pending alerts")
        return
    
    print(f"\n📬 Pending Alerts: {len(alerts)}\n")
    
    for i, alert in enumerate(alerts, 1):
        print(f"{'='*60}")
        print(f"Alert #{i} - {alert.get('id', 'unknown')}")
        print(f"{'='*60}")
        print(f"Priority:  {alert.get('priority', 'unknown').upper()}")
        print(f"Channel:   {alert.get('channel', 'telegram')}")
        print(f"Topic:     {alert.get('topic_name', 'unknown')}")
        print(f"Title:     {alert.get('title', 'untitled')[:60]}")
        print(f"URL:       {alert.get('url', '')}")
        print(f"Score:     {alert.get('score', 0):.2f}")
        print(f"Timestamp: {alert.get('timestamp', '')}")
        print()
        print("Message Preview:")
        print("-" * 40)
        print(format_alert_message(alert))
        print()


def output_json_for_agent():
    """Output alerts as JSON for agent processing."""
    alerts = get_pending_alerts()
    
    if not alerts:
        print(json.dumps({"alerts": [], "count": 0}))
        return
    
    # Format alerts for agent
    formatted = []
    for alert in alerts:
        formatted.append({
            "id": alert.get("id"),
            "priority": alert.get("priority", "medium"),
            "channel": alert.get("channel", "telegram"),
            "target": os.environ.get("TOPIC_MONITOR_TELEGRAM_ID", ""),
            "topic_name": alert.get("topic_name"),
            "title": alert.get("title"),
            "url": alert.get("url"),
            "score": alert.get("score", 0),
            "message": format_alert_message(alert)
        })
    
    output = {
        "alerts": formatted,
        "count": len(formatted),
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(output, indent=2))


def mark_all_sent(alert_ids: list = None):
    """Mark alerts as sent."""
    alerts = get_pending_alerts()
    
    if alert_ids:
        # Mark specific alerts
        for aid in alert_ids:
            mark_alert_sent(aid)
            print(f"✅ Marked as sent: {aid}")
    else:
        # Mark all pending
        for alert in alerts:
            mark_alert_sent(alert.get("id"))
            print(f"✅ Marked as sent: {alert.get('id')}")
    
    print(f"\n✅ Marked {len(alert_ids) if alert_ids else len(alerts)} alert(s) as sent")


def main():
    parser = argparse.ArgumentParser(description="Process topic monitor alerts")
    parser.add_argument("--json", action="store_true", help="Output as JSON for agent")
    parser.add_argument("--mark-sent", nargs="*", metavar="ID", 
                       help="Mark alert(s) as sent (all if no IDs given)")
    parser.add_argument("--clear-old", type=int, metavar="HOURS",
                       help="Clear alerts older than HOURS (default: 168 = 7 days)")
    
    args = parser.parse_args()
    
    if args.clear_old:
        clear_old_alerts(args.clear_old)
        print(f"✅ Cleared alerts older than {args.clear_old} hours")
        return
    
    if args.mark_sent is not None:
        # --mark-sent with or without IDs
        if args.mark_sent:
            mark_all_sent(args.mark_sent)
        else:
            mark_all_sent()
        return
    
    if args.json:
        output_json_for_agent()
    else:
        show_pending_alerts()


if __name__ == "__main__":
    main()
