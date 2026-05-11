"""
seo-agi environment and configuration loader.
Reads API keys from ~/.config/seo-agi/.env or os.environ.
Resolves paths relative to the skill installation directory.
"""

import os
import json
from pathlib import Path

# Skill root is two levels up from this file (scripts/lib/env.py -> .)
SKILL_DIR = Path(__file__).resolve().parent.parent.parent

OUTPUT_DIR = Path.home() / "Documents" / "SEO-AGI"
DATA_DIR = Path.home() / ".local" / "share" / "seo-agi"
CONFIG_DIR = Path.home() / ".config" / "seo-agi"
ENV_FILE = CONFIG_DIR / ".env"

DEFAULT_CONFIG = {
    "default_location": 2840,
    "default_language": "en",
    "default_site": "",
    "serp_depth": 10,
    "save_research": True,
    "output_dir": str(OUTPUT_DIR),
}


def load_env() -> dict:
    """
    Load environment variables.
    Reads from ~/.config/seo-agi/.env first, then overlays os.environ.
    """
    env = {}

    # First, try the config file
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        env[key] = value

    # Then overlay with os.environ
    for key in [
        "DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD",
        "GSC_SERVICE_ACCOUNT_PATH", "GSC_CLIENT_ID",
        "GSC_CLIENT_SECRET", "GSC_REFRESH_TOKEN",
        "AHREFS_API_KEY", "SEMRUSH_API_KEY",
    ]:
        val = os.environ.get(key)
        if val:
            env[key] = val

    return env


def load_config() -> dict:
    """Load user config, merged with defaults."""
    config = DEFAULT_CONFIG.copy()
    config_file = CONFIG_DIR / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass
    return config


def get_credentials() -> dict:
    """Get API credentials with availability flags."""
    env = load_env()

    creds = {
        "dataforseo_login": env.get("DATAFORSEO_LOGIN", ""),
        "dataforseo_password": env.get("DATAFORSEO_PASSWORD", ""),
        "gsc_service_account_path": env.get("GSC_SERVICE_ACCOUNT_PATH", ""),
        "gsc_client_id": env.get("GSC_CLIENT_ID", ""),
        "gsc_client_secret": env.get("GSC_CLIENT_SECRET", ""),
        "gsc_refresh_token": env.get("GSC_REFRESH_TOKEN", ""),
        "ahrefs_api_key": env.get("AHREFS_API_KEY", ""),
        "semrush_api_key": env.get("SEMRUSH_API_KEY", ""),
    }

    creds["has_dataforseo"] = bool(
        creds["dataforseo_login"] and creds["dataforseo_password"]
    )
    creds["has_gsc"] = bool(
        creds["gsc_service_account_path"]
        or (creds["gsc_client_id"] and creds["gsc_client_secret"])
    )
    creds["has_ahrefs"] = bool(creds["ahrefs_api_key"])
    creds["has_semrush"] = bool(creds["semrush_api_key"])

    return creds


def ensure_dirs():
    """Create output directories if they don't exist."""
    config = load_config()
    output_dir = Path(config["output_dir"]).expanduser()

    for subdir in ["research", "briefs", "pages", "rewrites"]:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "research").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)


def check_setup() -> dict:
    """Check setup status and return a summary."""
    creds = get_credentials()
    config = load_config()

    return {
        "runtime": "claude-code",
        "skill_dir": str(SKILL_DIR),
        "config_dir_exists": CONFIG_DIR.exists(),
        "env_file_exists": ENV_FILE.exists(),
        "has_dataforseo": creds["has_dataforseo"],
        "has_gsc": creds["has_gsc"],
        "has_ahrefs": creds["has_ahrefs"],
        "has_semrush": creds["has_semrush"],
        "default_location": config["default_location"],
        "default_language": config["default_language"],
        "mode": _determine_mode(creds),
    }


def _determine_mode(creds: dict) -> str:
    """Determine operational mode based on available credentials."""
    if creds["has_dataforseo"] and creds["has_gsc"]:
        return "full"
    elif creds["has_dataforseo"]:
        return "dataforseo-only"
    elif creds["has_gsc"]:
        return "gsc-only"
    else:
        return "fallback"
