"""Shared utilities for the website-style-images skill."""

import logging
import os
import re
import unicodedata

import yaml


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text or "website"


def load_yaml(path: str) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_env_vars(config: dict) -> dict:
    """Resolve ${ENV_VAR:default} patterns in config string values."""
    pattern = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

    def _resolve(value):
        if isinstance(value, str):
            def replacer(m):
                env_var, default = m.group(1), m.group(2)
                return os.environ.get(env_var, default if default is not None else m.group(0))
            return pattern.sub(replacer, value)
        elif isinstance(value, dict):
            return {k: _resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_resolve(v) for v in value]
        return value

    return _resolve(config)


def get_skill_dir() -> str:
    """Return the skill root directory (parent of scripts/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_visual_root() -> str:
    """Return the visual project root directory."""
    return os.path.dirname(os.path.dirname(get_skill_dir()))
