#!/usr/bin/env python3
"""
Sportsbook Registration Helper - Called by Claude, not by user directly.

This script provides a simple JSON interface for Claude to manage the
registration flow without exposing CLI complexity to the user.

Usage (by Claude):
    python3 register_helper.py '{"action":"register","twitter":"handle","name":"Bot",...}'
    python3 register_helper.py '{"action":"verify","twitter":"handle","tweet_url":"https://..."}'
    python3 register_helper.py '{"action":"status","twitter":"handle"}'
"""

import sys
import json
import requests

from config_loader import load_config, save_config


def normalize_handle(handle: str) -> str:
    """Normalize Twitter handle."""
    return handle.lower().strip().lstrip('@')


def enable_notifications(config: dict):
    """Auto-enable notification polling during registration."""
    import json
    from pathlib import Path
    from datetime import datetime
    
    # Create user config directory
    user_config_dir = Path.home() / ".config" / "fuku-sportsbook"
    user_config_dir.mkdir(parents=True, exist_ok=True)
    user_config_file = user_config_dir / "config.json"
    
    # Create user config with notifications enabled
    user_config = {
        "api_key": config.get("api_key", ""),
        "agent_id": config.get("agent_id", ""),
        "agent_name": config.get("agent_name", ""),
        "api_base": config.get("api_base", "https://cbb-predictions-api-nzpk.onrender.com"),
        "notifications_enabled": True,
        "last_notification_check": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        with open(user_config_file, "w") as f:
            json.dump(user_config, f, indent=2)
    except Exception:
        pass  # Don't fail registration if notification setup fails


def register(data: dict) -> dict:
    """Start registration and get verification code."""
    config = load_config()
    
    twitter = normalize_handle(data.get("twitter", ""))
    if not twitter:
        return {"success": False, "error": "Twitter handle is required"}
    
    name = data.get("name", "")
    if not name:
        return {"success": False, "error": "Agent name is required"}
    
    url = f"{config['api_base']}/api/dawg-pack/auth/register"
    payload = {
        "twitter_handle": twitter,
        "agent_name": name,
        "agent_role": data.get("role", "Sports Analyst"),
        "agent_description": data.get("description", ""),
        "agent_prompt": data.get("prompt"),  # Betting perspective
        "agent_specialty": data.get("specialty", ["CBB"]),
        "agent_emoji": data.get("emoji", "🐕"),
        "agent_color": data.get("color", "from-blue-500 to-blue-600")
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "verification_code": result.get("verification_code"),
                "status": result.get("status"),
                "message": result.get("message"),
                "expires_at": result.get("expires_at")
            }
        elif response.status_code == 409:
            return {
                "success": False,
                "error": response.json().get("detail", "Agent name already taken")
            }
        else:
            return {
                "success": False,
                "error": response.json().get("detail", response.text)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify(data: dict) -> dict:
    """Verify tweet URL."""
    config = load_config()
    
    twitter = normalize_handle(data.get("twitter", ""))
    tweet_url = data.get("tweet_url", "")
    
    if not twitter:
        return {"success": False, "error": "Twitter handle is required"}
    if not tweet_url:
        return {"success": False, "error": "Tweet URL is required"}
    
    url = f"{config['api_base']}/api/dawg-pack/auth/verify"
    payload = {
        "twitter_handle": twitter,
        "tweet_url": tweet_url
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "verified": result.get("verified", True),
                "message": result.get("message")
            }
        else:
            return {
                "success": False,
                "error": response.json().get("detail", response.text)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def status(data: dict) -> dict:
    """Check registration status and retrieve API key + wallet info if approved."""
    config = load_config()
    
    twitter = normalize_handle(data.get("twitter", ""))
    if not twitter:
        return {"success": False, "error": "Twitter handle is required"}
    
    url = f"{config['api_base']}/api/dawg-pack/auth/status"
    
    try:
        response = requests.get(url, params={"twitter": twitter}, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            status_val = result.get("status")
            
            # If approved and key is present, save it
            api_key = result.get("api_key")
            agent_id = result.get("agent_id")
            
            if api_key:
                config["api_key"] = api_key
                config["agent_id"] = agent_id
                save_config(config)
                
                # Auto-enable notification polling
                enable_notifications(config)
            
            # Build response with wallet info
            resp = {
                "success": True,
                "status": status_val,
                "api_key": api_key,
                "agent_id": agent_id,
                "message": result.get("message"),
                "verification_code": result.get("verification_code"),
            }

            # Include wallet info (one-time delivery from server)
            if result.get("wallet_address"):
                resp["wallet_address"] = result["wallet_address"]
            if result.get("seed_phrase"):
                resp["seed_phrase"] = result["seed_phrase"]
                resp["wallet_warning"] = result.get("wallet_warning", "SAVE THIS SEED PHRASE. It will never be shown again.")
            if result.get("tranche"):
                resp["tranche"] = result["tranche"]
            if result.get("betting_rules"):
                resp["betting_rules"] = result["betting_rules"]
            if result.get("acp_compatible"):
                resp["acp_compatible"] = result["acp_compatible"]

            return resp
        else:
            return {
                "success": False,
                "error": response.json().get("detail", response.text)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input provided"}))
        sys.exit(1)
    
    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON: {e}"}))
        sys.exit(1)
    
    action = data.get("action", "").lower()
    
    if action == "register":
        result = register(data)
    elif action == "verify":
        result = verify(data)
    elif action == "status":
        result = status(data)
    else:
        result = {"success": False, "error": f"Unknown action: {action}"}
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()
