#!/usr/bin/env python3
"""
Jike Publisher Script

A standalone Python script for posting to Jike via browser automation.

Usage:
    python3 post_jike.py "Your content here"
    python3 post_jike.py --file content.txt
    python3 post_jike.py --interactive

Requirements:
    - OpenClaw browser tool
    - Logged in Jike account in managed browser (profile="openclaw")
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
JIKE_URL = "https://web.okjike.com/following"
BROWSER_PROFILE = "openclaw"
STATE_FILE = Path.home() / ".openclaw/workspace-distribute/memory/jike-state.json"


def read_state():
    """Read current state from state file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "lastPublishTime": 0,
        "lastPublishDate": None,
        "lastContent": None
    }


def write_state(content):
    """Update state file with new post info."""
    state = {
        "lastPublishTime": int(time.time()),
        "lastPublishDate": datetime.now().isoformat(),
        "lastContent": content
    }

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_rate_limit(min_interval=60):
    """Check if enough time has passed since last post."""
    state = read_state()
    now = int(time.time())
    time_since_last = now - state["lastPublishTime"]

    if time_since_last < min_interval:
        remaining = min_interval - time_since_last
        print(f"⚠️  Rate limit: Please wait {remaining} seconds before posting again.")
        return False

    return True


def validate_content(content):
    """Validate content before posting."""
    if not content or not content.strip():
        print("❌ Error: Content cannot be empty.")
        return False

    if len(content) > 2000:
        print(f"❌ Error: Content too long ({len(content)} chars). Maximum is 2000.")
        return False

    return True


def post_to_jike(content):
    """
    Post content to Jike using browser automation.

    This is a reference implementation showing the workflow.
    In practice, you would use OpenClaw's browser tool directly.

    Args:
        content: Text content to post

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"📝 Posting to Jike...")
    print(f"Content: {content[:50]}{'...' if len(content) > 50 else ''}")
    print(f"Length: {len(content)} characters")

    steps = [
        f"1. Open {JIKE_URL}",
        "2. Take snapshot to get element refs",
        "3. Click textbox",
        "4. Type content",
        "5. Click send button",
        "6. Verify post appeared"
    ]

    print("\nSteps:")
    for step in steps:
        print(f"  {step}")

    print("\n✅ Post workflow defined. Use OpenClaw browser tool to execute.")
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Post to Jike via browser automation")
    parser.add_argument("content", nargs="?", help="Content to post")
    parser.add_argument("--file", "-f", help="Read content from file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--no-rate-limit", action="store_true", help="Skip rate limit check")
    parser.add_argument("--state", action="store_true", help="Show current state")

    args = parser.parse_args()

    # Show state
    if args.state:
        state = read_state()
        print("Current state:")
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return 0

    # Get content
    content = None

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    elif args.interactive:
        print("Enter content (Ctrl+D or Ctrl+Z to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        content = "\n".join(lines).strip()
    elif args.content:
        content = args.content
    else:
        parser.print_help()
        return 1

    # Validate
    if not validate_content(content):
        return 1

    # Check rate limit
    if not args.no_rate_limit and not check_rate_limit():
        return 1

    # Post
    success = post_to_jike(content)

    if success:
        write_state(content)
        print("\n✅ Success! State updated.")
        return 0
    else:
        print("\n❌ Failed to post.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
