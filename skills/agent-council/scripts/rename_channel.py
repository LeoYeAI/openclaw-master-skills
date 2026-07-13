#!/usr/bin/env python3
"""
Discord Channel Rename Script
Automates renaming Discord channels and updating references in OpenClaw.

Usage:
    python3 rename_channel.py --id <channel-id> --old-name <old-name> --new-name <new-name> [--workspace <workspace-dir>]

Examples:
    python3 rename_channel.py --id 1234567890 --old-name old-name --new-name new-name
    python3 rename_channel.py --id 1234567890 --old-name old-name --new-name new-name --workspace "$HOME/my-workspace"
"""

import argparse
import json
import sys
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
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


def rename_discord_channel(token: str, channel_id: str, new_name: str) -> bool:
    """Rename a Discord channel via API."""
    url = f"https://discord.com/api/v10/channels/{channel_id}"
    
    payload = {"name": new_name}
    
    req = Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        },
        method='PATCH'
    )
    
    try:
        with urlopen(req) as response:
            print(f"✅ Renamed Discord channel to #{new_name}")
            return True
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Failed to rename channel: {e.code} - {error_body}")
        return False


def update_workspace_files(workspace: Path, old_name: str, new_name: str) -> List[str]:
    """Search and update workspace files with new channel name."""
    updated_files = []
    
    # Patterns to replace
    patterns = [
        (f"#{old_name}", f"#{new_name}"),           # Channel mentions
        (f'"{old_name}"', f'"{new_name}"'),         # Quoted references
        (f"/{old_name}/", f"/{new_name}/"),         # Path-like references
    ]
    
    # Search all markdown files
    for md_file in workspace.rglob("*.md"):
        if md_file.is_file():
            content = md_file.read_text()
            original_content = content
            
            # Apply all patterns
            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)
            
            # Write back if changed
            if content != original_content:
                md_file.write_text(content)
                updated_files.append(str(md_file.relative_to(workspace)))
    
    return updated_files


def check_system_prompt_references(config: Dict[str, Any], guild_id: str, channel_id: str, old_name: str) -> Optional[str]:
    """Check if systemPrompt contains old channel name."""
    try:
        prompt = config['channels']['discord']['guilds'][guild_id]['channels'][channel_id].get('systemPrompt', '')
        if old_name in prompt:
            return prompt
    except (KeyError, TypeError):
        pass
    return None


def build_system_prompt_patch(guild_id: str, channel_id: str, old_prompt: str, old_name: str, new_name: str) -> Dict[str, Any]:
    """Build gateway config patch to update systemPrompt."""
    new_prompt = old_prompt.replace(old_name, new_name)
    return {
        "channels": {
            "discord": {
                "guilds": {
                    guild_id: {
                        "channels": {
                            channel_id: {
                                "systemPrompt": new_prompt
                            }
                        }
                    }
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Rename Discord channel and update references")
    parser.add_argument("--id", required=True, help="Channel ID")
    parser.add_argument("--old-name", required=True, help="Current channel name")
    parser.add_argument("--new-name", required=True, help="New channel name")
    parser.add_argument("--workspace", help="Workspace directory to search and update (optional)")
    
    args = parser.parse_args()
    
    channel_id = args.id
    old_name = args.old_name.lower()
    new_name = args.new_name.lower()
    workspace_dir = args.workspace or os.environ.get("OPENCLAW_WORKSPACE")
    
    print(f"🔧 Renaming channel: #{old_name} → #{new_name}")
    
    # Load config
    config = load_config()
    token, guild_id = get_discord_info(config)
    
    # 1. Rename Discord channel
    if not rename_discord_channel(token, channel_id, new_name):
        sys.exit(1)
    
    # 2. Check if systemPrompt needs updating
    old_prompt = check_system_prompt_references(config, guild_id, channel_id, old_name)
    if old_prompt:
        print(f"\n⚠️  systemPrompt contains '{old_name}' - needs updating")
        patch = build_system_prompt_patch(guild_id, channel_id, old_prompt, old_name, new_name)
        print(f"\n📝 Run this command to update systemPrompt:")
        print(f"\nopenclaw gateway config.patch --raw '{json.dumps(patch)}'")
    else:
        print(f"✅ systemPrompt does not reference old name - no update needed")
    
    # 3. Update workspace files (if workspace specified)
    if workspace_dir:
        workspace = Path(workspace_dir).expanduser()
        if not workspace.exists():
            print(f"\n⚠️  Workspace not found: {workspace}")
        else:
            print(f"\n🔍 Searching workspace for references to #{old_name}...")
            updated_files = update_workspace_files(workspace, old_name, new_name)
            
            if updated_files:
                print(f"\n✅ Updated {len(updated_files)} files:")
                for file in updated_files:
                    print(f"   - {file}")
                print(f"\n📝 Commit changes:")
                print(f"   git add -A")
                print(f"   git commit -m \"Rename channel {old_name} → {new_name}\"")
            else:
                print(f"✅ No workspace files needed updating")
    
    print(f"\n✅ Channel rename complete!")


if __name__ == "__main__":
    main()
