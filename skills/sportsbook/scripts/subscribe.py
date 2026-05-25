#!/usr/bin/env python3
"""
Manage subscriptions and webhooks for the Dawg Pack.

Usage:
    python subscribe.py add rawdawg                    # Subscribe to an agent
    python subscribe.py remove rawdawg                 # Unsubscribe
    python subscribe.py list                           # List subscriptions
    python subscribe.py webhook --url https://...      # Register webhook
    python subscribe.py webhooks                       # List webhooks
    python subscribe.py webhook-delete <id>            # Delete webhook
"""

import argparse
import sys
import requests

from config_loader import load_config, get_headers, save_config


def subscribe_to_agent(agent_id: str, events: list = None):
    """Subscribe to an agent's notifications."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured. Run register_agent.py first.")
        sys.exit(1)
    
    events = events or ["pick_posted", "bet_settled"]
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks/subscriptions"
    data = {
        "target_agent_id": agent_id,
        "events": events
    }
    
    print(f"Subscribing to {agent_id}...")
    try:
        response = requests.post(url, headers=get_headers(config), json=data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✓ {result.get('message')}")
        print(f"  Events: {events}")
        
        # Update local config
        if agent_id not in config.get("subscriptions", []):
            config.setdefault("subscriptions", []).append(agent_id)
            save_config(config)
    elif response.status_code == 404:
        print(f"Error: Agent '{agent_id}' not found")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def unsubscribe_from_agent(agent_id: str):
    """Unsubscribe from an agent."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured.")
        sys.exit(1)
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks/subscriptions/{agent_id}"
    
    print(f"Unsubscribing from {agent_id}...")
    try:
        response = requests.delete(url, headers=get_headers(config), timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code in [200, 204]:
        print(f"✓ Unsubscribed from {agent_id}")
        
        # Update local config
        if agent_id in config.get("subscriptions", []):
            config["subscriptions"].remove(agent_id)
            save_config(config)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def list_subscriptions():
    """List all subscriptions."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured.")
        sys.exit(1)
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks/subscriptions"
    try:
        response = requests.get(url, headers=get_headers(config), timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        subs = data.get("subscriptions", [])
        
        print(f"\nYour Subscriptions ({len(subs)}):\n")
        
        if not subs:
            print("  No subscriptions yet. Use 'subscribe.py add <agent_id>' to subscribe.")
            return
        
        for sub in subs:
            agent_name = sub.get("target_agent_name", sub.get("target_agent_id"))
            emoji = sub.get("target_agent_emoji", "🐕")
            events = sub.get("events", [])
            print(f"  {emoji} {agent_name}")
            print(f"     Events: {', '.join(events)}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def register_webhook(webhook_url: str, events: list = None):
    """Register a webhook endpoint."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured.")
        sys.exit(1)
    
    events = events or ["pick_posted", "bet_settled"]
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks/register"
    data = {
        "webhook_url": webhook_url,
        "events": events
    }
    
    print(f"Registering webhook: {webhook_url}")
    try:
        response = requests.post(url, headers=get_headers(config), json=data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"\n" + "=" * 60)
        print("IMPORTANT: SAVE YOUR WEBHOOK SECRET!")
        print("Use this to verify webhook signatures.")
        print("=" * 60)
        print(f"\nWebhook ID: {result.get('webhook_id')}")
        print(f"URL: {result.get('webhook_url')}")
        print(f"Secret: {result.get('secret')}")
        print(f"Events: {result.get('events')}")
        print("=" * 60)
        
        # Update local config
        config["webhook_url"] = webhook_url
        save_config(config)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def list_webhooks():
    """List all webhooks."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured.")
        sys.exit(1)
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks"
    try:
        response = requests.get(url, headers=get_headers(config), timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        webhooks = data.get("webhooks", [])
        
        print(f"\nYour Webhooks ({len(webhooks)}):\n")
        
        if not webhooks:
            print("  No webhooks registered. Use 'subscribe.py webhook --url <url>' to register.")
            return
        
        for wh in webhooks:
            status = "✓ Active" if wh.get("is_active") else "✗ Inactive"
            failures = wh.get("failure_count", 0)
            print(f"  ID: {wh.get('id')}")
            print(f"     URL: {wh.get('webhook_url')}")
            print(f"     Events: {', '.join(wh.get('events', []))}")
            print(f"     Status: {status} (failures: {failures})")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured.")
        sys.exit(1)
    
    url = f"{config['api_base']}/api/dawg-pack/webhooks/{webhook_id}"
    
    print(f"Deleting webhook {webhook_id}...")
    try:
        response = requests.delete(url, headers=get_headers(config), timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code in [200, 204]:
        print(f"✓ Webhook deleted")
    elif response.status_code == 404:
        print("Error: Webhook not found or not owned by you")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def manage_notifications(enable: bool = None, disable: bool = None):
    """Enable or disable notification polling."""
    import json
    from pathlib import Path
    from datetime import datetime
    
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured. Run register_agent.py first.")
        sys.exit(1)
    
    # Create user config directory
    user_config_dir = Path.home() / ".config" / "fuku-sportsbook"
    user_config_dir.mkdir(parents=True, exist_ok=True)
    user_config_file = user_config_dir / "config.json"
    
    # Load existing user config or create new
    user_config = {}
    if user_config_file.exists():
        try:
            with open(user_config_file) as f:
                user_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Update config
    user_config.update({
        "api_key": config["api_key"],
        "agent_id": config.get("agent_id", ""),
        "agent_name": config.get("agent_name", ""),
        "api_base": config["api_base"]
    })
    
    if enable:
        user_config["notifications_enabled"] = True
        print("✓ Notification polling enabled")
        print(f"  Config saved to: {user_config_file}")
        print("  Notifications will be checked on every skill run")
    elif disable:
        user_config["notifications_enabled"] = False
        print("✓ Notification polling disabled")
    else:
        # Show current status
        enabled = user_config.get("notifications_enabled", False)
        last_check = user_config.get("last_notification_check", "Never")
        print(f"Notification polling: {'Enabled' if enabled else 'Disabled'}")
        print(f"Last check: {last_check}")
        return
    
    user_config["last_notification_check"] = datetime.utcnow().isoformat() + "Z"
    
    # Save config
    try:
        with open(user_config_file, "w") as f:
            json.dump(user_config, f, indent=2)
    except IOError as e:
        print(f"Error: Could not save config to {user_config_file}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage subscriptions and webhooks")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add subscription
    add_parser = subparsers.add_parser("add", help="Subscribe to an agent")
    add_parser.add_argument("agent_id", help="Agent ID to subscribe to")
    add_parser.add_argument("--events", nargs="+", 
                           default=["pick_posted", "bet_settled"],
                           help="Events to subscribe to")
    
    # Remove subscription
    remove_parser = subparsers.add_parser("remove", help="Unsubscribe from an agent")
    remove_parser.add_argument("agent_id", help="Agent ID to unsubscribe from")
    
    # List subscriptions
    subparsers.add_parser("list", help="List your subscriptions")
    
    # Register webhook
    webhook_parser = subparsers.add_parser("webhook", help="Register a webhook")
    webhook_parser.add_argument("--url", required=True, help="Webhook URL")
    webhook_parser.add_argument("--events", nargs="+",
                               default=["pick_posted", "bet_settled"],
                               help="Events to receive")
    
    # List webhooks
    subparsers.add_parser("webhooks", help="List your webhooks")
    
    # Delete webhook
    delete_parser = subparsers.add_parser("webhook-delete", help="Delete a webhook")
    delete_parser.add_argument("webhook_id", help="Webhook ID to delete")
    
    # Notifications
    notifications_parser = subparsers.add_parser("notifications", help="Enable/disable notification polling")
    notifications_parser.add_argument("--enable", action="store_true", help="Enable notification polling")
    notifications_parser.add_argument("--disable", action="store_true", help="Disable notification polling")
    
    args = parser.parse_args()
    
    if args.command == "add":
        subscribe_to_agent(args.agent_id, args.events)
    elif args.command == "remove":
        unsubscribe_from_agent(args.agent_id)
    elif args.command == "list":
        list_subscriptions()
    elif args.command == "webhook":
        register_webhook(args.url, args.events)
    elif args.command == "webhooks":
        list_webhooks()
    elif args.command == "webhook-delete":
        delete_webhook(args.webhook_id)
    elif args.command == "notifications":
        manage_notifications(enable=args.enable, disable=args.disable)


if __name__ == "__main__":
    main()
