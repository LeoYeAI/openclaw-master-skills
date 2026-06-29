#!/usr/bin/env python3
"""
Topic management CLI for proactive-research.

Usage:
    python3 manage_topics.py add "Topic Name" --query "search" --keywords "a,b,c"
    python3 manage_topics.py list
    python3 manage_topics.py edit <id> --frequency hourly
    python3 manage_topics.py remove <id>
    python3 manage_topics.py test <id>
"""

import sys
import argparse
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, save_config, get_topic
from monitor import search_topic, monitor_topic, load_state, get_settings


def generate_id(name: str) -> str:
    """Generate topic ID from name."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    topic_id = name.lower()
    topic_id = re.sub(r'[^\w\s-]', '', topic_id)
    topic_id = re.sub(r'[-\s]+', '-', topic_id)
    return topic_id.strip('-')


def add_topic(args):
    """Add a new topic."""
    config = load_config()
    
    # Generate ID
    topic_id = args.id or generate_id(args.name)
    
    # Check for duplicates
    existing_ids = [t.get("id") for t in config.get("topics", [])]
    if topic_id in existing_ids:
        print(f"❌ Topic with ID '{topic_id}' already exists", file=sys.stderr)
        sys.exit(1)
    
    # Build topic
    topic = {
        "id": topic_id,
        "name": args.name,
        "query": args.query,
        "keywords": args.keywords.split(",") if args.keywords else [],
        "frequency": args.frequency,
        "importance_threshold": args.importance,
        "channels": args.channels.split(",") if args.channels else ["telegram"],
        "context": args.context or "",
        "alert_on": args.alert_on.split(",") if args.alert_on else [],
        "ignore_sources": [],
        "boost_sources": []
    }
    
    # Add to config
    if "topics" not in config:
        config["topics"] = []
    
    config["topics"].append(topic)
    save_config(config)
    
    print(f"✅ Added topic: {args.name} ({topic_id})")
    print(f"   Query: {args.query}")
    print(f"   Frequency: {args.frequency}")
    print(f"   Importance: {args.importance}")


def list_topics(args):
    """List all topics."""
    config = load_config()
    topics = config.get("topics", [])
    
    if not topics:
        print("No topics configured")
        return
    
    print(f"\n📋 Configured Topics ({len(topics)})\n")
    
    for topic in topics:
        print(f"{'='*60}")
        print(f"ID:         {topic.get('id')}")
        print(f"Name:       {topic.get('name')}")
        print(f"Query:      {topic.get('query')}")
        print(f"Keywords:   {', '.join(topic.get('keywords', []))}")
        print(f"Frequency:  {topic.get('frequency')}")
        print(f"Importance: {topic.get('importance_threshold')}")
        print(f"Channels:   {', '.join(topic.get('channels', []))}")
        if topic.get('context'):
            print(f"Context:    {topic.get('context')}")
        print()


def edit_topic(args):
    """Edit an existing topic."""
    config = load_config()
    topics = config.get("topics", [])
    
    # Find topic
    topic_idx = None
    for idx, topic in enumerate(topics):
        if topic.get("id") == args.topic_id:
            topic_idx = idx
            break
    
    if topic_idx is None:
        print(f"❌ Topic '{args.topic_id}' not found", file=sys.stderr)
        sys.exit(1)
    
    topic = topics[topic_idx]
    
    # Update fields
    if args.name:
        topic["name"] = args.name
    if args.query:
        topic["query"] = args.query
    if args.keywords:
        topic["keywords"] = args.keywords.split(",")
    if args.frequency:
        topic["frequency"] = args.frequency
    if args.importance:
        topic["importance_threshold"] = args.importance
    if args.channels:
        topic["channels"] = args.channels.split(",")
    if args.context:
        topic["context"] = args.context
    if args.alert_on:
        topic["alert_on"] = args.alert_on.split(",")
    
    # Save
    topics[topic_idx] = topic
    config["topics"] = topics
    save_config(config)
    
    print(f"✅ Updated topic: {topic.get('name')} ({args.topic_id})")


def remove_topic(args):
    """Remove a topic."""
    config = load_config()
    topics = config.get("topics", [])
    
    # Find and remove
    new_topics = [t for t in topics if t.get("id") != args.topic_id]
    
    if len(new_topics) == len(topics):
        print(f"❌ Topic '{args.topic_id}' not found", file=sys.stderr)
        sys.exit(1)
    
    config["topics"] = new_topics
    save_config(config)
    
    print(f"✅ Removed topic: {args.topic_id}")


def test_topic(args):
    """Test a topic (search without saving)."""
    topic = get_topic(args.topic_id)
    
    if not topic:
        print(f"❌ Topic '{args.topic_id}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"🧪 Testing topic: {topic.get('name')}\n")
    
    # Run monitor in dry-run mode
    state = load_state()
    settings = get_settings()
    
    monitor_topic(topic, state, settings, dry_run=True, verbose=True)


def main():
    parser = argparse.ArgumentParser(description="Manage research topics")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new topic")
    add_parser.add_argument("name", help="Topic name")
    add_parser.add_argument("--id", help="Custom topic ID (auto-generated if not provided)")
    add_parser.add_argument("--query", required=True, help="Search query")
    add_parser.add_argument("--keywords", help="Comma-separated keywords")
    add_parser.add_argument("--frequency", choices=["hourly", "daily", "weekly"], 
                           default="daily", help="Check frequency")
    add_parser.add_argument("--importance", choices=["high", "medium", "low"],
                           default="medium", help="Importance threshold")
    add_parser.add_argument("--channels", default="telegram", 
                           help="Comma-separated channels (telegram,discord,email)")
    add_parser.add_argument("--context", help="Why this topic matters to you")
    add_parser.add_argument("--alert-on", help="Comma-separated alert conditions")
    add_parser.set_defaults(func=add_topic)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all topics")
    list_parser.set_defaults(func=list_topics)
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit a topic")
    edit_parser.add_argument("topic_id", help="Topic ID to edit")
    edit_parser.add_argument("--name", help="New name")
    edit_parser.add_argument("--query", help="New query")
    edit_parser.add_argument("--keywords", help="New keywords (comma-separated)")
    edit_parser.add_argument("--frequency", choices=["hourly", "daily", "weekly"])
    edit_parser.add_argument("--importance", choices=["high", "medium", "low"])
    edit_parser.add_argument("--channels", help="New channels (comma-separated)")
    edit_parser.add_argument("--context", help="New context")
    edit_parser.add_argument("--alert-on", help="New alert conditions (comma-separated)")
    edit_parser.set_defaults(func=edit_topic)
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a topic")
    remove_parser.add_argument("topic_id", help="Topic ID to remove")
    remove_parser.set_defaults(func=remove_topic)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a topic")
    test_parser.add_argument("topic_id", help="Topic ID to test")
    test_parser.set_defaults(func=test_topic)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
