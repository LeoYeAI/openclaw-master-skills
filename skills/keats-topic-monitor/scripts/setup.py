#!/usr/bin/env python3
"""
Interactive onboarding wizard for topic-monitor skill.
Runs on first use when no config.json exists.
"""

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
CONFIG_EXAMPLE = SKILL_DIR / "config.example.json"


def print_welcome():
    """Print welcome message."""
    print()
    print("=" * 55)
    print("  🔍 Topic Monitor - Setup Wizard")
    print("=" * 55)
    print()
    print("Welcome! Let's set up your personal topic monitoring.")
    print("I'll ask a few questions to understand what you want to track.")
    print()
    print("You can always edit config.json later to fine-tune things.")
    print()


def prompt(question: str, default: str = None) -> str:
    """Prompt user for input with optional default."""
    if default:
        question = f"{question} [{default}]: "
    else:
        question = f"{question}: "
    
    response = input(question).strip()
    return response if response else (default or "")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt for yes/no answer."""
    default_hint = "Y/n" if default else "y/N"
    response = input(f"{question} ({default_hint}): ").strip().lower()
    
    if not response:
        return default
    return response in ('y', 'yes', 'ja', 'si', 'oui')


def prompt_choice(question: str, choices: list, default: str = None) -> str:
    """Prompt for choice from list."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        marker = " *" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        response = input(f"\nEnter number or value [{default or choices[0]}]: ").strip()
        
        if not response:
            return default or choices[0]
        
        # Check if it's a number
        try:
            idx = int(response)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]
        except ValueError:
            pass
        
        # Check if it's a valid choice
        response_lower = response.lower()
        for choice in choices:
            if choice.lower() == response_lower:
                return choice
        
        print(f"  Please enter a number 1-{len(choices)} or a valid option.")


def prompt_multiline(question: str, hint: str = None) -> list:
    """Prompt for multiple lines of input."""
    print(f"\n{question}")
    if hint:
        print(f"  {hint}")
    print("  (Enter each item on a new line. Empty line when done)")
    print()
    
    items = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        items.append(line)
    
    return items


def prompt_keywords(topic_name: str) -> list:
    """Prompt for keywords for a topic."""
    print(f"\n  Keywords to watch for in '{topic_name}'?")
    print("  (comma-separated, e.g.: release, update, announcement)")
    
    response = input("  > ").strip()
    if not response:
        return []
    
    keywords = [k.strip() for k in response.split(",") if k.strip()]
    return keywords


def create_topic_id(name: str) -> str:
    """Create a safe ID from topic name."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    topic_id = name.lower()
    topic_id = topic_id.replace(" ", "-")
    topic_id = "".join(c for c in topic_id if c.isalnum() or c == "-")
    topic_id = "-".join(filter(None, topic_id.split("-")))  # Remove duplicate hyphens
    return topic_id[:30]  # Limit length


def gather_topics() -> list:
    """Gather topic configurations interactively."""
    topics = []
    
    print("-" * 55)
    print("📋 STEP 1: Topics to Monitor")
    print("-" * 55)
    
    topic_names = prompt_multiline(
        "What topics do you want to monitor?",
        "Examples: AI Models, Security Alerts, Product Updates"
    )
    
    if not topic_names:
        print("\n⚠️  No topics entered. You can add them later with manage_topics.py")
        return []
    
    print(f"\nGreat! Let's configure each of your {len(topic_names)} topics.\n")
    
    for i, name in enumerate(topic_names, 1):
        print(f"\n--- Topic {i}/{len(topic_names)}: {name} ---")
        
        # Search query
        default_query = f"{name} news updates"
        query = prompt(f"  Search query for '{name}'", default_query)
        
        # Keywords
        keywords = prompt_keywords(name)
        
        topic = {
            "id": create_topic_id(name),
            "name": name,
            "query": query,
            "keywords": keywords,
            "frequency": None,  # Will be set globally
            "importance_threshold": None,  # Will be set globally
            "channels": ["telegram"],
            "context": "",
            "alert_on": ["keyword_exact_match"],
            "ignore_sources": [],
            "boost_sources": []
        }
        topics.append(topic)
    
    return topics


def gather_settings() -> dict:
    """Gather global settings interactively."""
    print()
    print("-" * 55)
    print("⚙️  STEP 2: Monitoring Settings")
    print("-" * 55)
    
    # Frequency
    frequency = prompt_choice(
        "How often should I check for updates?",
        ["hourly", "daily", "weekly"],
        default="daily"
    )
    
    # Importance threshold
    print("\nImportance threshold determines when you get alerts:")
    print("  • high = Only alert for major news")
    print("  • medium = Alert for moderately important updates")
    print("  • low = Alert for anything relevant")
    
    importance = prompt_choice(
        "\nImportance threshold for alerts?",
        ["low", "medium", "high"],
        default="medium"
    )
    
    # Weekly digest
    print()
    print("-" * 55)
    print("📊 STEP 3: Weekly Digest")
    print("-" * 55)
    
    print("\nThe weekly digest compiles lower-priority findings")
    print("so you don't miss interesting but non-urgent updates.")
    
    digest_enabled = prompt_yes_no("\nEnable weekly digest?", default=True)
    
    digest_day = "sunday"
    if digest_enabled:
        digest_day = prompt_choice(
            "Which day should I send the digest?",
            ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            default="sunday"
        )
    
    settings = {
        "frequency": frequency,
        "importance_threshold": importance,
        "digest_enabled": digest_enabled,
        "digest_day": digest_day,
        "digest_time": "18:00",
        "max_alerts_per_day": 5,
        "max_alerts_per_topic_per_day": 2,
        "deduplication_window_hours": 72,
        "learning_enabled": True,
        "quiet_hours": {
            "enabled": False,
            "start": "22:00",
            "end": "08:00"
        }
    }
    
    return settings


def build_config(topics: list, settings: dict) -> dict:
    """Build the final config object."""
    # Apply global frequency and importance to topics
    for topic in topics:
        topic["frequency"] = settings.pop("frequency")
        topic["importance_threshold"] = settings.pop("importance_threshold")
    
    # Load channel config from example
    channels = {
        "telegram": {
            "enabled": True,
            "chat_id": None,
            "silent": False,
            "effects": {
                "high_importance": "🔥",
                "medium_importance": "📌"
            }
        },
        "discord": {
            "enabled": False,
            "webhook_url": None,
            "username": "Topic Monitor",
            "avatar_url": None
        },
        "email": {
            "enabled": False,
            "to": None,
            "from": "monitor@yourdomain.com",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": None,
            "smtp_password": None
        }
    }
    
    config = {
        "topics": topics,
        "settings": settings,
        "channels": channels
    }
    
    return config


def save_config(config: dict):
    """Save config to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def print_summary(config: dict):
    """Print configuration summary."""
    print()
    print("=" * 55)
    print("  ✅ Setup Complete!")
    print("=" * 55)
    print()
    
    topics = config.get("topics", [])
    settings = config.get("settings", {})
    
    print(f"📋 Topics configured: {len(topics)}")
    for topic in topics:
        print(f"   • {topic['name']}")
        print(f"     Query: {topic['query'][:40]}...")
        print(f"     Keywords: {', '.join(topic['keywords'][:3])}{'...' if len(topic['keywords']) > 3 else ''}")
        print(f"     Frequency: {topic['frequency']}, Threshold: {topic['importance_threshold']}")
    
    print()
    print(f"⚙️  Settings:")
    print(f"   • Weekly digest: {'Enabled' if settings.get('digest_enabled', True) else 'Disabled'}")
    if settings.get('digest_enabled', True):
        print(f"   • Digest day: {settings.get('digest_day', 'sunday').capitalize()}")
    print(f"   • Max alerts/day: {settings.get('max_alerts_per_day', 5)}")
    print(f"   • Learning mode: {'Enabled' if settings.get('learning_enabled', True) else 'Disabled'}")
    
    print()
    print("📁 Config saved to: config.json")
    print()
    print("-" * 55)
    print("Next Steps:")
    print("-" * 55)
    print()
    print("1. Test your topics:")
    print("   python3 scripts/monitor.py --dry-run --verbose")
    print()
    print("2. Set up automated monitoring:")
    print("   python3 scripts/setup_cron.py")
    print()
    print("3. Manage topics later:")
    print("   python3 scripts/manage_topics.py list")
    print("   python3 scripts/manage_topics.py add \"New Topic\" --query \"...\"")
    print()
    print("Happy monitoring! 🔍")
    print()


def main():
    """Main entry point."""
    # Check if config already exists
    if CONFIG_FILE.exists():
        print()
        print("⚠️  config.json already exists!")
        print()
        overwrite = prompt_yes_no("Do you want to start fresh and overwrite it?", default=False)
        if not overwrite:
            print("\nKeeping existing config. Use manage_topics.py to edit topics.")
            print("Or delete config.json and run setup again.")
            sys.exit(0)
        print()
    
    print_welcome()
    
    try:
        # Gather information
        topics = gather_topics()
        settings = gather_settings()
        
        # Build and save config
        config = build_config(topics, settings)
        save_config(config)
        
        # Show summary
        print_summary(config)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled. No changes made.")
        sys.exit(1)
    except EOFError:
        print("\n\n⚠️  Input ended. No changes made.")
        sys.exit(1)


if __name__ == "__main__":
    main()
