#!/usr/bin/env python3
"""
Quick Start - One-liner topic monitoring setup.

Usage:
    python3 quick.py "AI Model Releases"
    python3 quick.py "Bitcoin price" --keywords "BTC,price,crash"
    python3 quick.py "Security vulnerabilities" --frequency hourly --importance high
"""

import sys
import argparse
import re
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import load_config, save_config, CONFIG_FILE
except ImportError:
    CONFIG_FILE = Path(__file__).parent.parent / "config.json"
    
    def load_config():
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return {"topics": [], "settings": {}}
    
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)


def generate_id(name: str) -> str:
    """Generate topic ID from name."""
    topic_id = name.lower()
    topic_id = re.sub(r'[^\w\s-]', '', topic_id)
    topic_id = re.sub(r'[-\s]+', '-', topic_id)
    return topic_id.strip('-')[:30]


def quick_add(args):
    """Quick add a topic with minimal input."""
    config = load_config()
    
    # Generate sensible defaults
    topic_id = generate_id(args.topic)
    
    # Check for duplicates
    existing_ids = [t.get("id") for t in config.get("topics", [])]
    if topic_id in existing_ids:
        print(f"⚠️  Topic '{topic_id}' already exists. Use manage_topics.py to edit.")
        sys.exit(1)
    
    # Auto-generate query if not provided
    query = args.query or f"{args.topic} news updates"
    
    # Auto-generate keywords from topic name
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    else:
        # Extract meaningful words from topic
        words = re.findall(r'\b[A-Za-z]{3,}\b', args.topic)
        keywords = list(set(words))[:5]
    
    topic = {
        "id": topic_id,
        "name": args.topic,
        "query": query,
        "keywords": keywords,
        "frequency": args.frequency,
        "importance_threshold": args.importance,
        "channels": [args.channel],
        "context": args.context or f"Monitoring {args.topic}",
        "alert_on": [],
        "created": datetime.now().isoformat()
    }
    
    if "topics" not in config:
        config["topics"] = []
    
    if "settings" not in config:
        config["settings"] = {
            "digest_day": "sunday",
            "digest_time": "18:00",
            "max_alerts_per_day": 5,
            "deduplication_window_hours": 72
        }
    
    config["topics"].append(topic)
    save_config(config)
    
    # Success output
    print()
    print("✅ Topic created!")
    print()
    print(f"   📌 {args.topic}")
    print(f"   🔍 Query: {query}")
    print(f"   🏷️  Keywords: {', '.join(keywords)}")
    print(f"   ⏰ Frequency: {args.frequency}")
    print(f"   🔔 Alert threshold: {args.importance}")
    print(f"   📱 Channel: {args.channel}")
    print()
    print("Next steps:")
    print(f"   • Test:    python3 scripts/monitor.py --topic {topic_id} --dry-run")
    print(f"   • Run:     python3 scripts/monitor.py --topic {topic_id}")
    print(f"   • Edit:    python3 scripts/manage_topics.py edit {topic_id} --frequency hourly")
    print(f"   • Remove:  python3 scripts/manage_topics.py remove {topic_id}")
    print()
    
    return topic_id


def main():
    parser = argparse.ArgumentParser(
        description="Quick Start - Add a topic to monitor in one command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "AI Model Releases"
  %(prog)s "Bitcoin price" --keywords "BTC,crash,pump"
  %(prog)s "Security CVEs" --frequency hourly --importance high
  %(prog)s "My Competitor" --query "CompanyName product launch" --channel discord
        """
    )
    
    parser.add_argument("topic", help="Topic name to monitor (e.g., 'AI News')")
    parser.add_argument("--query", "-q", help="Custom search query (auto-generated if not provided)")
    parser.add_argument("--keywords", "-k", help="Comma-separated keywords to watch for")
    parser.add_argument("--frequency", "-f", 
                       choices=["hourly", "daily", "weekly"],
                       default="daily",
                       help="How often to check (default: daily)")
    parser.add_argument("--importance", "-i",
                       choices=["high", "medium", "low"],
                       default="medium",
                       help="Alert threshold (default: medium)")
    parser.add_argument("--channel", "-c",
                       default="telegram",
                       help="Where to send alerts (default: telegram)")
    parser.add_argument("--context",
                       help="Why this topic matters to you")
    
    args = parser.parse_args()
    quick_add(args)


if __name__ == "__main__":
    main()
