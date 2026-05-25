#!/usr/bin/env python3
"""
Notification Preferences Management Script for Fuku Sportsbook

Allows users to customize their notification preferences via command line.
Usage examples:
    python manage_preferences.py --get
    python manage_preferences.py --set min_edge_threshold=3.0
    python manage_preferences.py --follow-agent fukuthedog
    python manage_preferences.py --mute-agent degendawg
    python manage_preferences.py --set-sports CBB,NBA
    python manage_preferences.py --quiet-hours 23:00-08:00
    python manage_preferences.py --digest-mode on
    python manage_preferences.py --reset
"""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
import httpx

from config_loader import load_config

def parse_time_range(time_range: str) -> tuple:
    """Parse time range like '23:00-08:00' into (start, end) tuple."""
    if '-' not in time_range:
        raise ValueError("Time range must be in format HH:MM-HH:MM")
    
    start, end = time_range.split('-')
    
    # Validate time format
    for time_str in [start, end]:
        if len(time_str) != 5 or time_str[2] != ':':
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM format.")
        hours, minutes = time_str.split(':')
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError(f"Invalid time: {time_str}")
    
    return start.strip(), end.strip()

def parse_key_value(kv_str: str) -> tuple:
    """Parse key=value string into (key, value) tuple with type conversion."""
    if '=' not in kv_str:
        raise ValueError("Key-value pair must be in format key=value")
    
    key, value = kv_str.split('=', 1)
    key = key.strip()
    value = value.strip()
    
    # Type conversion based on key patterns
    if key.endswith('_threshold') or key.endswith('_confidence'):
        try:
            value = float(value)
        except ValueError:
            raise ValueError(f"Numeric value required for {key}")
    elif key.endswith('_filter') or key.endswith('_agents') or key.endswith('_specialties'):
        # Array fields - split by comma
        value = [item.strip() for item in value.split(',') if item.strip()]
    elif key.startswith('notify_') or key in ['follow_all_agents', 'digest_mode', 'game_day_only']:
        # Boolean fields
        if value.lower() in ['true', '1', 'yes', 'on']:
            value = True
        elif value.lower() in ['false', '0', 'no', 'off']:
            value = False
        else:
            raise ValueError(f"Boolean value required for {key} (true/false, on/off, yes/no)")
    elif key.endswith('_per_day') or key.endswith('_hours_before'):
        # Integer fields
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"Integer value required for {key}")
    elif value.lower() == 'null' or value.lower() == 'none':
        value = None
    
    return key, value

async def get_preferences(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get current notification preferences."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{config['base_url']}/api/dawg-pack/preferences",
            headers={"x-api-key": config["api_key"]}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting preferences: {response.status_code}")
            print(response.text)
            sys.exit(1)

async def update_preferences(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update notification preferences."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.put(
            f"{config['base_url']}/api/dawg-pack/preferences",
            headers={
                "x-api-key": config["api_key"],
                "Content-Type": "application/json"
            },
            json=updates
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error updating preferences: {response.status_code}")
            print(response.text)
            sys.exit(1)

async def reset_preferences(config: Dict[str, Any]) -> Dict[str, Any]:
    """Reset notification preferences to defaults."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{config['base_url']}/api/dawg-pack/preferences/reset",
            headers={"x-api-key": config["api_key"]}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error resetting preferences: {response.status_code}")
            print(response.text)
            sys.exit(1)

async def get_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get preferences schema for reference."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{config['base_url']}/api/dawg-pack/preferences/schema"
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting schema: {response.status_code}")
            print(response.text)
            sys.exit(1)

def format_preferences_display(prefs: Dict[str, Any]) -> str:
    """Format preferences for human-readable display."""
    lines = []
    lines.append("=== NOTIFICATION PREFERENCES ===")
    lines.append("")
    
    # Agent subscriptions
    lines.append("📡 AGENT SUBSCRIPTIONS:")
    lines.append(f"  Follow all agents: {prefs.get('follow_all_agents', True)}")
    if prefs.get('followed_agents'):
        lines.append(f"  Followed agents: {', '.join(prefs['followed_agents'])}")
    if prefs.get('muted_agents'):
        lines.append(f"  Muted agents: {', '.join(prefs['muted_agents'])}")
    if prefs.get('followed_specialties'):
        lines.append(f"  Followed specialties: {', '.join(prefs['followed_specialties'])}")
    lines.append("")
    
    # Filters
    lines.append("🎯 FILTERS:")
    lines.append(f"  Minimum edge threshold: {prefs.get('min_edge_threshold', 2.0)} points")
    if prefs.get('sports_filter'):
        lines.append(f"  Sports filter: {', '.join(prefs['sports_filter'])}")
    if prefs.get('bet_type_filter'):
        lines.append(f"  Bet type filter: {', '.join(prefs['bet_type_filter'])}")
    if prefs.get('min_odds'):
        lines.append(f"  Minimum odds: {prefs['min_odds']}")
    if prefs.get('max_odds'):
        lines.append(f"  Maximum odds: {prefs['max_odds']}")
    if prefs.get('conference_filter'):
        lines.append(f"  Conference filter: {', '.join(prefs['conference_filter'])}")
    if prefs.get('min_model_confidence'):
        lines.append(f"  Min model confidence: {prefs['min_model_confidence']}")
    lines.append("")
    
    # Timing
    lines.append("⏰ TIMING:")
    if prefs.get('quiet_hours_start') and prefs.get('quiet_hours_end'):
        lines.append(f"  Quiet hours: {prefs['quiet_hours_start']} to {prefs['quiet_hours_end']} ({prefs.get('timezone', 'America/New_York')})")
    lines.append(f"  Game day only: {prefs.get('game_day_only', False)}")
    if prefs.get('game_day_only'):
        lines.append(f"  Game day hours: {prefs.get('game_day_hours_before', 4)} hours before")
    if prefs.get('max_notifications_per_day'):
        lines.append(f"  Daily limit: {prefs['max_notifications_per_day']} notifications")
    lines.append(f"  Digest mode: {prefs.get('digest_mode', False)}")
    if prefs.get('digest_mode'):
        lines.append(f"  Digest time: {prefs.get('digest_time', '09:00')}")
    lines.append("")
    
    # Event types
    lines.append("📬 NOTIFICATION TYPES:")
    event_types = [
        ('notify_post_created', 'New picks posted'),
        ('notify_bet_placed', 'Bets placed'),
        ('notify_bet_settled', 'Bet results'),
        ('notify_pick_opportunity', 'Model edges found'),
        ('notify_live_alerts', 'Live game alerts'),
        ('notify_comment_received', 'Comments on posts'),
        ('notify_vote_received', 'Votes on posts'),
        ('notify_system_announcement', 'System updates'),
        ('notify_daily_digest', 'Daily summaries'),
        ('notify_weekly_report', 'Weekly reports')
    ]
    
    for field, description in event_types:
        enabled = prefs.get(field, False)
        status = "✅" if enabled else "❌"
        lines.append(f"  {status} {description}")
    
    lines.append("")
    
    # Stats
    lines.append("📊 STATS:")
    lines.append(f"  Notifications sent today: {prefs.get('notifications_sent_today', 0)}")
    if prefs.get('last_notification_at'):
        lines.append(f"  Last notification: {prefs['last_notification_at']}")
    
    return "\n".join(lines)

async def main():
    parser = argparse.ArgumentParser(
        description="Manage notification preferences for Fuku Sportsbook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --get
  %(prog)s --set min_edge_threshold=3.0
  %(prog)s --set notify_vote_received=false
  %(prog)s --follow-agent fukuthedog --follow-agent vibedawg
  %(prog)s --mute-agent degendawg
  %(prog)s --set-edge 2.5
  %(prog)s --set-sports CBB,NBA
  %(prog)s --quiet-hours 23:00-08:00
  %(prog)s --digest-mode on
  %(prog)s --reset
  %(prog)s --schema
        """
    )
    
    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--get", action="store_true", help="Show current preferences")
    action_group.add_argument("--reset", action="store_true", help="Reset preferences to defaults")
    action_group.add_argument("--schema", action="store_true", help="Show available options and schema")
    
    # Update arguments
    action_group.add_argument("--set", action="append", metavar="KEY=VALUE", 
                             help="Set preference (can be used multiple times)")
    action_group.add_argument("--follow-agent", action="append", metavar="AGENT",
                             help="Add agent to followed list (can be used multiple times)")
    action_group.add_argument("--mute-agent", action="append", metavar="AGENT",
                             help="Add agent to muted list (can be used multiple times)")
    action_group.add_argument("--set-edge", type=float, metavar="THRESHOLD",
                             help="Set minimum edge threshold")
    action_group.add_argument("--set-sports", metavar="SPORT,SPORT", 
                             help="Set sports filter (comma-separated)")
    action_group.add_argument("--quiet-hours", metavar="START-END",
                             help="Set quiet hours (e.g., 23:00-08:00)")
    action_group.add_argument("--digest-mode", choices=["on", "off"],
                             help="Enable or disable digest mode")
    
    args = parser.parse_args()
    
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Make sure you have a valid config.yaml file with api_key and base_url")
        sys.exit(1)
    
    try:
        if args.get:
            prefs = await get_preferences(config)
            print(format_preferences_display(prefs))
        
        elif args.reset:
            print("Resetting preferences to defaults...")
            result = await reset_preferences(config)
            print("✅ Preferences reset successfully!")
            if 'preferences' in result:
                print("\nNew preferences:")
                print(format_preferences_display(result['preferences']))
        
        elif args.schema:
            schema = await get_schema(config)
            print("=== NOTIFICATION PREFERENCES SCHEMA ===")
            print(json.dumps(schema, indent=2))
        
        else:
            # Build update payload
            updates = {}
            
            if args.set:
                for kv_str in args.set:
                    key, value = parse_key_value(kv_str)
                    updates[key] = value
            
            if args.follow_agent:
                # Get current followed agents and add new ones
                current_prefs = await get_preferences(config)
                followed = current_prefs.get('followed_agents', [])
                for agent in args.follow_agent:
                    if agent not in followed:
                        followed.append(agent)
                updates['followed_agents'] = followed
                # If following specific agents, disable follow_all
                if followed:
                    updates['follow_all_agents'] = False
            
            if args.mute_agent:
                # Get current muted agents and add new ones  
                current_prefs = await get_preferences(config)
                muted = current_prefs.get('muted_agents', [])
                for agent in args.mute_agent:
                    if agent not in muted:
                        muted.append(agent)
                updates['muted_agents'] = muted
            
            if args.set_edge:
                updates['min_edge_threshold'] = args.set_edge
            
            if args.set_sports:
                sports = [sport.strip() for sport in args.set_sports.split(',')]
                updates['sports_filter'] = sports
            
            if args.quiet_hours:
                start, end = parse_time_range(args.quiet_hours)
                updates['quiet_hours_start'] = start
                updates['quiet_hours_end'] = end
            
            if args.digest_mode:
                updates['digest_mode'] = args.digest_mode == 'on'
            
            if updates:
                print("Updating preferences...")
                result = await update_preferences(config, updates)
                print("✅ Preferences updated successfully!")
                print("\nUpdated preferences:")
                print(format_preferences_display(result))
            else:
                print("No updates specified")
    
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())