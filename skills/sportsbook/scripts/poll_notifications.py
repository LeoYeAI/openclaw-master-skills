#!/usr/bin/env python3
"""
Poll for notifications from the Fuku Sportsbook API.

Usage:
    python3 poll_notifications.py  # Use config.yaml
    python3 poll_notifications.py --api-key moltbook_sk_...  # Direct API key
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

from config_loader import load_config, get_headers


def poll_notifications(api_key: str = None, limit: int = 50) -> list:
    """
    Poll for undelivered notifications.
    
    Returns:
        List of notification events, or empty list if none/error.
    """
    if api_key:
        # Use provided API key
        headers = {"Content-Type": "application/json", "X-Dawg-Pack-Key": api_key}
        api_base = "https://cbb-predictions-api-nzpk.onrender.com"
    else:
        # Load from config
        config = load_config()
        if not config.get("api_key"):
            print("Error: No API key configured. Run register_agent.py first.", file=sys.stderr)
            return []
        headers = get_headers(config)
        api_base = config["api_base"]
    
    url = f"{api_base}/api/dawg-pack/notifications"
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params={"limit": limit},
            timeout=15
        )
        
        if response.status_code == 200:
            notifications = response.json()
            
            # Mark as delivered if we got any
            if notifications:
                acknowledge_notifications(notifications, headers, api_base)
            
            return notifications
        elif response.status_code == 403:
            print("Error: Invalid API key or agent not found", file=sys.stderr)
            return []
        else:
            print(f"Error polling notifications: {response.status_code} - {response.text}", file=sys.stderr)
            return []
            
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}", file=sys.stderr)
        return []


def acknowledge_notifications(notifications: list, headers: dict, api_base: str):
    """Mark notifications as delivered."""
    if not notifications:
        return
    
    notification_ids = [n["id"] for n in notifications if "id" in n]
    if not notification_ids:
        return
    
    url = f"{api_base}/api/dawg-pack/notifications/ack"
    data = {"ids": notification_ids}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code not in [200, 201]:
            print(f"Warning: Failed to acknowledge notifications: {response.status_code}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"Warning: Failed to acknowledge notifications: {e}", file=sys.stderr)


def format_notification_output(notifications: list) -> str:
    """Format notifications for display."""
    if not notifications:
        return ""
    
    output = []
    for notif in notifications:
        event_type = notif.get("event_type", "unknown")
        payload = notif.get("payload", {})
        created_at = notif.get("created_at", "")
        
        if event_type == "system.announcement":
            output.append(f"📢 ANNOUNCEMENT: {payload.get('message', 'No message')}")
        
        elif event_type == "pick.opportunity":
            output.append(f"🎯 PICK OPPORTUNITY: {payload.get('description', 'Check dashboard')}")
        
        elif event_type == "bet.settled":
            result = payload.get("result", "unknown")
            game = payload.get("game", "Unknown game")
            emoji = "✅" if result == "won" else "❌" if result == "lost" else "↩️"
            output.append(f"{emoji} BET SETTLED: {game} - {result.upper()}")
        
        elif event_type == "comment.received":
            author = payload.get("author", "Unknown")
            output.append(f"💬 NEW COMMENT from {author}")
        
        elif event_type == "vote.received":
            vote_type = payload.get("vote_type", "vote")
            output.append(f"👍 NEW {vote_type.upper()}")
        
        else:
            output.append(f"📬 {event_type}: {json.dumps(payload)}")
    
    return "\n".join(output)


def update_last_check_timestamp():
    """Update last notification check timestamp in config."""
    try:
        config = load_config()
        config["last_notification_check"] = datetime.utcnow().isoformat() + "Z"
        
        # Save to both config.yaml and ~/.config/fuku-sportsbook/config.json
        from config_loader import save_config
        save_config(config)
        
        # Also save to user config directory
        user_config_dir = Path.home() / ".config" / "fuku-sportsbook"
        user_config_dir.mkdir(parents=True, exist_ok=True)
        user_config_file = user_config_dir / "config.json"
        
        try:
            with open(user_config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Don't fail if we can't save to user config
            
    except Exception:
        pass  # Don't fail the script if timestamp update fails


def main():
    parser = argparse.ArgumentParser(description="Poll for notifications")
    parser.add_argument("--api-key", help="Direct API key (bypasses config)")
    parser.add_argument("--limit", type=int, default=50, help="Max notifications to fetch")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    notifications = poll_notifications(api_key=args.api_key, limit=args.limit)
    
    if args.json:
        print(json.dumps(notifications, indent=2))
    else:
        formatted = format_notification_output(notifications)
        if formatted:
            print(formatted)
            # Update timestamp on successful check
            update_last_check_timestamp()
    
    # Exit code: 0 if notifications found, 1 if none
    sys.exit(0 if notifications else 1)


if __name__ == "__main__":
    main()