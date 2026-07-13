#!/usr/bin/env python3
"""
Discord Channel Setup Script
Automates the creation and configuration of Discord channels for OpenClaw.

Usage:
    python3 setup_channel.py --name <channel-name> --context <context> [--category-id <category-id>] [--id <channel-id>]

Examples:
    python3 setup_channel.py --name fitness --context "Fitness tracking and workout planning"
    python3 setup_channel.py --name research --context "Deep research" --category-id "1234567890"
    python3 setup_channel.py --name personal-finance --id 1466184336901537897 --context "Personal finance"
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Configuration
CONFIG_FILE = Path.home() / ".openclaw" / "config.json"


def load_config() -> Dict[str, Any]:
    """Load OpenClaw configuration."""
    if not CONFIG_FILE.exists():
        print(f"❌ Config not found: {CONFIG_FILE}")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_discord_info(config: Dict[str, Any]) -> tuple[str, str]:
    """Extract Discord bot token and guild ID from config."""
    try:
        token = config['channels']['discord']['token']
        guild_id = list(config['channels']['discord']['guilds'].keys())[0]
        return token, guild_id
    except (KeyError, IndexError):
        print("❌ Discord configuration not found in config")
        sys.exit(1)


def channel_exists(token: str, guild_id: str, channel_name: str) -> Optional[str]:
    """Check if a channel with the given name already exists. Returns channel ID if found."""
    url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
    req = Request(url, headers={"Authorization": f"Bot {token}"})
    
    try:
        with urlopen(req) as response:
            channels = json.loads(response.read())
            for channel in channels:
                if channel.get('name') == channel_name and channel.get('type') == 0:  # Text channel
                    return channel['id']
    except HTTPError:
        return None
    
    return None


def create_discord_channel(token: str, guild_id: str, channel_name: str, category_id: Optional[str] = None) -> Optional[str]:
    """Create a new Discord text channel."""
    url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
    
    payload = {
        "name": channel_name,
        "type": 0,  # Text channel
    }
    
    if category_id:
        payload["parent_id"] = category_id
    
    req = Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        },
        method='POST'
    )
    
    try:
        with urlopen(req) as response:
            result = json.loads(response.read())
            return result['id']
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Failed to create channel: {e.code} - {error_body}")
        return None


def build_gateway_config(channel_id: str, guild_id: str, context: str) -> Dict[str, Any]:
    """Build gateway config patch for the channel."""
    return {
        "channels": {
            "discord": {
                "guilds": {
                    guild_id: {
                        "channels": {
                            channel_id: {
                                "allow": True,
                                "requireMention": False,
                                "systemPrompt": context
                            }
                        }
                    }
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Setup Discord channel for OpenClaw")
    parser.add_argument("--name", required=True, help="Channel name (e.g., 'fitness', 'personal-finance')")
    parser.add_argument("--id", help="Channel ID if it already exists")
    parser.add_argument("--context", help="Channel context/purpose")
    parser.add_argument("--category-id", help="Discord category ID to place channel in (optional)")
    
    args = parser.parse_args()
    
    channel_name = args.name.lower()
    channel_id = args.id
    context = args.context
    category_id = args.category_id or os.environ.get("DISCORD_CATEGORY_ID")
    
    print(f"🔧 Setting up Discord channel: #{channel_name}")
    
    # Validate context is provided
    if not context:
        print("❌ Error: --context is required")
        print("   Specify the channel's purpose with --context \"Your description here\"")
        sys.exit(1)
    
    # Load config
    config = load_config()
    token, guild_id = get_discord_info(config)
    
    # Check if channel exists or create it
    if not channel_id:
        print(f"🔍 Checking if channel #{channel_name} exists...")
        channel_id = channel_exists(token, guild_id, channel_name)
        
        if channel_id:
            print(f"✅ Found existing channel: {channel_id}")
        else:
            print(f"📝 Channel doesn't exist. Creating it...")
            
            if category_id:
                print(f"   Using category ID: {category_id}")
            else:
                print(f"   Creating uncategorized channel (no category specified)")
            
            channel_id = create_discord_channel(token, guild_id, channel_name, category_id)
            if not channel_id:
                sys.exit(1)
            
            print(f"✅ Created channel #{channel_name} (ID: {channel_id})")
    
    # Build gateway config patch
    patch = build_gateway_config(channel_id, guild_id, context)
    
    print(f"\n✅ Channel #{channel_name} setup complete!")
    print(f"   Channel ID: {channel_id}")
    print(f"   Context: {context}")
    print(f"\n📝 Run this command to apply the gateway config:")
    print(f"\nopenclaw gateway config.patch --raw '{json.dumps(patch)}'")
    print(f"\n⚠️  Gateway will restart automatically after applying config.")


if __name__ == "__main__":
    main()
