"""
Configuration loader for sportsbook skill scripts.
"""

import os
import json
import yaml
from pathlib import Path

# Default API base
DEFAULT_API_BASE = "https://cbb-predictions-api-nzpk.onrender.com"

# Skill directory
SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"

# User config directory
USER_CONFIG_DIR = Path.home() / ".config" / "fuku-sportsbook"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from config.yaml and user config directory"""
    config = {}
    
    # First try user config directory (JSON format)
    if USER_CONFIG_FILE.exists():
        try:
            with open(USER_CONFIG_FILE) as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Then try skill directory config (YAML format)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                yaml_config = yaml.safe_load(f) or {}
                # Merge YAML config, but user config takes precedence
                for key, value in yaml_config.items():
                    if key not in config:
                        config[key] = value
        except yaml.YAMLError as e:
            print(f"Warning: Invalid YAML in {CONFIG_FILE}: {e}")
        except IOError as e:
            print(f"Warning: Error reading {CONFIG_FILE}: {e}")
    
    # If no config found anywhere
    if not config:
        print(f"Warning: No config found. Checked:")
        print(f"  - {USER_CONFIG_FILE}")
        print(f"  - {CONFIG_FILE}")
        print("Run register_agent.py to set up your agent")
    
    # Allow env vars to override everything
    return {
        "api_key": os.environ.get("DAWG_PACK_API_KEY", config.get("api_key", "")),
        "agent_id": os.environ.get("DAWG_PACK_AGENT_ID", config.get("agent_id", "")),
        "agent_name": config.get("agent_name", ""),
        "api_base": os.environ.get("DAWG_PACK_API_BASE", config.get("api_base", DEFAULT_API_BASE)),
        "webhook_url": config.get("webhook_url", ""),
        "subscriptions": config.get("subscriptions", []),
        "notifications_enabled": config.get("notifications_enabled", False),
        "last_notification_check": config.get("last_notification_check", "")
    }


def save_config(config: dict):
    """Save configuration to config.yaml"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    except IOError as e:
        print(f"Error: Could not save config to {CONFIG_FILE}: {e}")


def get_headers(config: dict) -> dict:
    """Get request headers with API key"""
    headers = {"Content-Type": "application/json"}
    if config.get("api_key"):
        headers["X-Dawg-Pack-Key"] = config["api_key"]
    return headers
