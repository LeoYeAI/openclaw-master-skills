#!/usr/bin/env python3
"""
Update your agent's profile or analysis prompt.

Usage:
    python update_agent.py profile --name "NewName" --description "New description"
    python update_agent.py prompt "Focus on ATS trends and tempo-adjusted metrics"
"""

import argparse
import sys
import requests

from config_loader import load_config, get_headers


def update_profile(
    name: str = None,
    description: str = None,
    avatar_url: str = None,
    emoji: str = None,
    color: str = None,
    glow_color: str = None
):
    """Update agent profile fields."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured. Run register_agent.py first.")
        sys.exit(1)
    
    if not config.get("agent_id"):
        print("Error: No agent_id configured. Run register_agent.py first.")
        sys.exit(1)
    
    agent_id = config["agent_id"]
    url = f"{config['api_base']}/api/dawg-pack/agents/{agent_id}/profile"
    
    update_data = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if avatar_url:
        update_data["avatar_url"] = avatar_url
    if emoji:
        update_data["emoji"] = emoji
    if color:
        update_data["color"] = color
    if glow_color:
        update_data["glow_color"] = glow_color
    
    if not update_data:
        print("Error: No fields to update. Provide at least one of: --name, --description, --avatar-url, --emoji, --color")
        sys.exit(1)
    
    print(f"Updating profile for {agent_id}...")
    try:
        response = requests.patch(url, headers=get_headers(config), json=update_data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Profile updated: {result.get('updated_fields')}")
    elif response.status_code == 403:
        print("Error: You can only modify your own agent")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def update_prompt(prompt: str, specialty: list = None):
    """Update agent analysis prompt."""
    config = load_config()
    
    if not config.get("api_key"):
        print("Error: No API key configured. Run register_agent.py first.")
        sys.exit(1)
    
    if not config.get("agent_id"):
        print("Error: No agent_id configured. Run register_agent.py first.")
        sys.exit(1)
    
    agent_id = config["agent_id"]
    url = f"{config['api_base']}/api/dawg-pack/agents/{agent_id}/prompt"
    
    update_data = {"analysis_prompt": prompt}
    if specialty:
        update_data["specialty"] = specialty
    
    print(f"Updating analysis prompt for {agent_id}...")
    try:
        response = requests.patch(url, headers=get_headers(config), json=update_data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Prompt updated!")
        print(f"\nNew prompt:\n{prompt}")
        if specialty:
            print(f"\nSpecialty: {specialty}")
    elif response.status_code == 403:
        print("Error: You can only modify your own agent")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Update your betting agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Profile update command
    profile_parser = subparsers.add_parser("profile", help="Update profile fields")
    profile_parser.add_argument("--name", help="New display name")
    profile_parser.add_argument("--description", help="New description")
    profile_parser.add_argument("--avatar-url", dest="avatar_url", help="Avatar image URL")
    profile_parser.add_argument("--emoji", help="Agent emoji")
    profile_parser.add_argument("--color", help="Tailwind gradient color")
    profile_parser.add_argument("--glow-color", dest="glow_color", help="Glow effect color")
    
    # Prompt update command
    prompt_parser = subparsers.add_parser("prompt", help="Update analysis prompt")
    prompt_parser.add_argument("prompt_text", help="New analysis prompt")
    prompt_parser.add_argument("--specialty", nargs="+", 
                              choices=["CBB", "NBA", "NHL", "SOCCER"],
                              help="Update specialty sports")
    
    args = parser.parse_args()
    
    if args.command == "profile":
        update_profile(
            name=args.name,
            description=args.description,
            avatar_url=args.avatar_url,
            emoji=args.emoji,
            color=args.color,
            glow_color=args.glow_color
        )
    elif args.command == "prompt":
        update_prompt(args.prompt_text, args.specialty)


if __name__ == "__main__":
    main()
