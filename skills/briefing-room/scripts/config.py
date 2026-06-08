#!/usr/bin/env python3
"""
Briefing Room Configuration
============================

Central configuration management for Briefing Room.
All settings in one place, with defaults and validation.
"""

import os
import sys
import json
import glob
import shutil
from pathlib import Path

# Config location
CONFIG_DIR = Path.home() / ".briefing-room"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    # Location settings (for weather)
    "location": {
        "city": "Bratislava",
        "latitude": 48.15,
        "longitude": 17.11,
        "timezone": "Europe/Bratislava",
    },

    # Language
    "language": "en",  # en, sk, de, etc.

    # Output settings
    "output": {
        "folder": str(Path.home() / "Documents" / "Briefing Room"),
        "open_folder_after": True,
    },

    # Document settings
    "document": {
        "format": "docx",       # docx, html, md
        "engine": "pandoc",     # pandoc (for docx), falls back to html
    },

    # Audio settings
    "audio": {
        "enabled": True,
        "format": "mp3",        # mp3, wav, aiff
        "tts_engine": "auto",   # auto, mlx, kokoro, builtin
        # auto = detect best available: mlx → kokoro → builtin
    },

    # TTS voice settings per language
    # Each language can specify its preferred engine + voice
    "voices": {
        "en": {
            "engine": "mlx",             # mlx, kokoro, builtin
            "mlx_voice": "af_heart",     # voice name or path to .safetensors
            "mlx_voice_blend": None,     # e.g. {"af_heart": 0.6, "af_sky": 0.4} or null
            "builtin_voice": "Samantha", # macOS say voice fallback
            "speed": 1.05,
        },
        "sk": {
            "engine": "builtin",
            "builtin_voice": "Laura (Enhanced)",
            "builtin_rate": 220,
            "speed": 1.0,
        },
        "de": {
            "engine": "builtin",
            "builtin_voice": "Petra (Premium)",
            "builtin_rate": 200,
            "speed": 1.0,
        },
    },

    # MLX-Audio settings (shared)
    "mlx_audio": {
        "path": "",              # auto-detect if empty
        "model": "mlx-community/Kokoro-82M-bf16",
        "lang_code": "a",       # 'a' for American English
    },

    # Kokoro PyTorch settings (fallback)
    "kokoro": {
        "path": "",              # auto-detect if empty
    },

    # News sections to include (order matters)
    "sections": [
        "weather",
        "social",       # X/Twitter trends
        "webtrends",    # Google Trends (web search trends)
        "world",
        "politics",
        "tech",
        "local",        # Local news (based on location.city)
        "sports",
        "markets",
        "crypto",
        "history",      # This Day in History
    ],

    # Host personality
    "host": {
        "name": "",  # Empty = auto (uses agent's own name). Set to override.
    },

    # X/Twitter trends settings
    "trends": {
        # Comma-separated getdaytrends.com region slugs (empty = worldwide)
        # Available: united-states, united-kingdom, germany, france, etc.
        # See full list: https://getdaytrends.com (footer links)
        "regions": "united-states,united-kingdom,",  # trailing comma = worldwide
    },

    # Google Trends (Web Trends) settings
    "webtrends": {
        # Comma-separated ISO country codes (empty = worldwide)
        # Examples: US, GB, DE, FR, SK
        "regions": "US,GB,",  # trailing comma = worldwide
    },

    # Search settings
    "search": {
        "country": "",           # 2-letter code, empty = auto from location
        "local_language": "",    # ISO lang code for local news search, empty = auto
    },

    # Processing
    "processing": {
        "subagent_timeout": 600,
        "cleanup_temp_files": True,
    },
}


def get_config_dir() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    config = deep_copy(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
            config = deep_merge(config, user_config)
        except json.JSONDecodeError as e:
            print(f"⚠️  Config corrupted: {e}",
                  file=sys.stderr)
            print(f"   Using defaults. Fix or delete: "
                  f"{CONFIG_FILE}", file=sys.stderr)
        except IOError:
            pass
    return config


def save_config(config: dict) -> None:
    get_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_value(key: str, default=None):
    config = load_config()
    keys = key.split('.')
    value = config
    try:
        for k in keys:
            if isinstance(value, list):
                k = int(k)
            value = value[k]
        return value
    except (KeyError, TypeError, IndexError, ValueError):
        return default


SAFE_OUTPUT_PREFIXES = [
    os.path.realpath(os.path.expanduser("~/Documents")),
    os.path.realpath(os.path.expanduser("~/Desktop")),
    os.path.realpath(os.path.expanduser("~/Downloads")),
    os.path.realpath(os.path.expanduser("~/.briefing-room")),
    os.path.realpath("/tmp"),
]

def _validate_output_path(path: str) -> bool:
    """Reject output.folder paths outside safe directories."""
    expanded = os.path.realpath(os.path.expanduser(path))
    return any(expanded.startswith(prefix) for prefix in SAFE_OUTPUT_PREFIXES)

def set_value(key: str, value) -> bool:
    if key == "output.folder" and isinstance(value, str):
        if not _validate_output_path(value):
            print(f"Error: output.folder must be under ~/Documents, ~/Desktop, ~/Downloads, ~/.briefing-room, or /tmp", file=sys.stderr)
            return False
    config = load_config()
    keys = key.split('.')
    target = config
    for k in keys[:-1]:
        if isinstance(target, list):
            try:
                k = int(k)
            except ValueError:
                return False
            if k < 0 or k >= len(target):
                return False
            target = target[k]
        else:
            if k not in target:
                target[k] = {}
            target = target[k]
    last = keys[-1]
    if isinstance(target, list):
        try:
            last = int(last)
        except ValueError:
            return False
        if 0 <= last < len(target):
            target[last] = value
        else:
            return False
    else:
        target[last] = value
    save_config(config)
    return True


def deep_copy(obj):
    if isinstance(obj, dict):
        return {k: deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_copy(v) for v in obj]
    return obj


def deep_merge(base: dict, override: dict) -> dict:
    result = deep_copy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deep_copy(value)
    return result


def reset_to_defaults() -> None:
    save_config(deep_copy(DEFAULT_CONFIG))


def detect_mlx_path() -> str:
    """Find MLX-Audio installation."""
    candidates = [
        Path.home() / ".openclaw" / "tools" / "mlx-audio",
        Path.home() / ".local" / "share" / "mlx-audio",
        Path.home() / "mlx-audio",
    ]
    for p in candidates:
        if (p / ".venv" / "bin" / "python3").exists():
            return str(p)
    return ""


def detect_kokoro_path() -> str:
    """Find Kokoro PyTorch installation."""
    candidates = [
        Path.home() / ".openclaw" / "tools" / "kokoro",
        Path.home() / ".local" / "share" / "kokoro",
        Path("/tmp") / "kokoro-coreml",
        Path.home() / "kokoro-coreml",
    ]
    for p in candidates:
        venv = p / ".venv" / "bin" / "python3"
        if venv.exists():
            return str(p)
    return ""


def detect_tts_engine(lang: str = "en") -> str:
    """Detect best available TTS engine for a language."""
    config = load_config()
    voice_cfg = config.get("voices", {}).get(lang, {})
    preferred = voice_cfg.get("engine", "auto")

    if preferred != "auto":
        return preferred

    # For non-English, prefer builtin (Apple TTS has good multilingual voices)
    if lang != "en":
        return "builtin"

    # For English: mlx → kokoro → builtin
    if detect_mlx_path():
        return "mlx"
    if detect_kokoro_path():
        return "kokoro"
    return "builtin"


def resolve_voice_path(config: dict) -> str:
    """Resolve the voice file path for MLX-Audio."""
    lang = config.get("language", "en")
    voice_cfg = config.get("voices", {}).get(lang, config.get("voices", {}).get("en", {}))
    blend = voice_cfg.get("mlx_voice_blend")
    voice = voice_cfg.get("mlx_voice", "af_heart")

    if blend and isinstance(blend, dict):
        # Look for pre-blended .safetensors in HuggingFace cache
        model = config.get("mlx_audio", {}).get("model", "mlx-community/Kokoro-82M-bf16")
        model_slug = model.replace("/", "--")
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{model_slug}"

        # Build expected filename from blend
        parts = []
        for v, w in sorted(blend.items(), key=lambda x: -x[1]):
            parts.append(f"{v}_{int(w * 100)}")
        blend_name = "_".join(parts) + ".safetensors"

        # Search snapshots
        matches = glob.glob(str(cache_dir / "snapshots" / "*" / "voices" / blend_name))
        if matches:
            return matches[0]

        # Try without blend — fall back to single voice
        matches = glob.glob(str(cache_dir / "snapshots" / "*" / "voices" / f"{voice}.safetensors"))
        if matches:
            return matches[0]

    # Single voice name — return as-is (mlx-audio resolves it)
    return voice


def print_config() -> None:
    config = load_config()
    print(json.dumps(config, indent=2))


def print_status() -> None:
    """Print a status summary with detected capabilities."""
    config = load_config()
    loc = config["location"]
    lang = config["language"]

    print("📻 Briefing Room — Configuration")
    print("=" * 45)
    print(f"Config: {CONFIG_FILE}")
    print()
    print(f"Location: {loc['city']} ({loc['latitude']}, {loc['longitude']})")
    print(f"Language: {lang}")
    print(f"Output:   {config['output']['folder']}")
    print(f"Document: {config['document']['format']} ({config['document']['engine']})")
    print(f"Audio:    {'enabled' if config['audio']['enabled'] else 'disabled'} ({config['audio']['format']})")
    print()

    print("TTS Engines:")
    mlx = detect_mlx_path()
    kokoro = detect_kokoro_path()
    print(f"  {'✓' if mlx else '✗'} MLX-Audio: {mlx or 'not found'}")
    print(f"  {'✓' if kokoro else '✗'} Kokoro:    {kokoro or 'not found'}")
    print(f"  ✓ Built-in:  macOS say (always available)")
    print()

    print("Voice Config:")
    for lang_code, vcfg in config.get("voices", {}).items():
        engine = vcfg.get("engine", "auto")
        if engine == "auto":
            engine = f"auto → {detect_tts_engine(lang_code)}"
        voice_name = vcfg.get("mlx_voice", vcfg.get("builtin_voice", "default"))
        print(f"  {lang_code}: {engine} ({voice_name})")
    print()

    print(f"Sections: {', '.join(config.get('sections', []))}")

    # Check dependencies
    print()
    print("Dependencies:")
    for name, cmd in [("curl", "curl"), ("pandoc", "pandoc"), ("ffmpeg", "ffmpeg")]:
        found = shutil.which(cmd)
        print(f"  {'✓' if found else '✗'} {name}")


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "status":
        print_status()

    elif sys.argv[1] == "show":
        print_config()

    elif sys.argv[1] == "get" and len(sys.argv) == 3:
        value = get_value(sys.argv[2])
        print(value if value is not None else "(not set)")

    elif sys.argv[1] == "set" and len(sys.argv) == 4:
        key, value = sys.argv[2], sys.argv[3]
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        if set_value(key, value):
            print(f"Set {key} = {value}")
        else:
            print(f"⚠️  Could not set {key} (invalid path?)")

    elif sys.argv[1] == "reset":
        reset_to_defaults()
        print("Config reset to defaults.")

    elif sys.argv[1] == "path":
        print(CONFIG_FILE)

    elif sys.argv[1] == "init":
        # First-run setup — create config with defaults
        if CONFIG_FILE.exists():
            print(f"Config already exists: {CONFIG_FILE}")
        else:
            save_config(deep_copy(DEFAULT_CONFIG))
            print(f"Created config: {CONFIG_FILE}")
            print("Edit it to customize location, language, and voices.")
        print_status()

    else:
        print("Usage:")
        print("  python config.py              # Show status")
        print("  python config.py show         # Show raw config JSON")
        print("  python config.py get KEY      # Get value (dot notation)")
        print("  python config.py set KEY VAL  # Set value")
        print("  python config.py init         # Create default config")
        print("  python config.py reset        # Reset to defaults")
        print("  python config.py path         # Show config file path")
