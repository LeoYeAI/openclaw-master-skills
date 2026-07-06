#!/usr/bin/env python3
"""Generate or merge an OpenClaw config for the Poetize blog automation skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

SKILL_KEY = "poetize-blog-automation"
PLACEHOLDER_API_KEY = "replace-with-poetize-api-key"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a usable OpenClaw config for the Poetize blog automation skill."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the generated OpenClaw JSON config.",
    )
    parser.add_argument(
        "--existing-config",
        help="Optional existing OpenClaw JSON config to merge into.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("POETIZE_API_KEY"),
        help="Poetize API key. Defaults to POETIZE_API_KEY when present.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("POETIZE_BASE_URL"),
        help="Poetize base URL. Defaults to POETIZE_BASE_URL or inferred repo settings.",
    )
    parser.add_argument(
        "--allow-placeholder-api-key",
        action="store_true",
        help="Allow generating config with a placeholder apiKey when the real key is unavailable.",
    )
    parser.add_argument(
        "--disable-watch",
        action="store_true",
        help="Do not set skills.load.watch/watchDebounceMs in the generated config.",
    )
    return parser.parse_args()


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def normalize_base_url(raw_url: str) -> str:
    sanitized = raw_url.strip()
    if not sanitized:
        die("Invalid base URL: empty")

    sanitized = sanitized.rstrip("/")
    if sanitized.lower().endswith("/api"):
        sanitized = sanitized[:-4].rstrip("/")

    parsed = urlparse(sanitized)
    if not parsed.scheme or not parsed.netloc:
        die(f"Invalid base URL: {raw_url}")
    normalized = parsed._replace(path="", params="", query="", fragment="")
    return urlunparse(normalized).rstrip("/")


def infer_base_url(explicit_base_url: str | None, repo_root: Path) -> str:
    if explicit_base_url:
        return normalize_base_url(explicit_base_url)

    env_values = parse_env_file(repo_root / ".env")
    if not env_values:
        env_values = parse_env_file(repo_root / ".env.example")

    site_url = str(env_values.get("SITE_URL") or "").strip()
    if site_url:
        return normalize_base_url(site_url)

    primary_domain = str(env_values.get("PRIMARY_DOMAIN") or "localhost").strip()
    scheme = "https" if truthy(env_values.get("ENABLE_HTTPS")) else "http"
    return normalize_base_url(f"{scheme}://{primary_domain}")


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        die(f"JSON file does not exist: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON in {path}: {exc}")

    if not isinstance(data, dict):
        die(f"JSON config must be an object: {path}")
    return data


def ensure_object(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if value is None:
        value = {}
        parent[key] = value
    if not isinstance(value, dict):
        die(f"Expected '{key}' to be a JSON object.")
    return value


def ensure_string_list(parent: dict[str, Any], key: str) -> list[str]:
    value = parent.get(key)
    if value is None:
        value = []
        parent[key] = value
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        die(f"Expected '{key}' to be a JSON array of strings.")
    return value


def build_config(
    existing_config: dict[str, Any],
    *,
    extra_skill_dir: Path,
    base_url: str,
    api_key: str,
    disable_watch: bool,
) -> dict[str, Any]:
    config = json.loads(json.dumps(existing_config))
    skills = ensure_object(config, "skills")
    load = ensure_object(skills, "load")
    extra_dirs = ensure_string_list(load, "extraDirs")
    extra_dir_str = str(extra_skill_dir)
    if extra_dir_str not in extra_dirs:
        extra_dirs.append(extra_dir_str)

    if not disable_watch:
        load.setdefault("watch", True)
        load.setdefault("watchDebounceMs", 250)

    entries = ensure_object(skills, "entries")
    entry = ensure_object(entries, SKILL_KEY)
    entry["enabled"] = True
    entry["apiKey"] = api_key

    env_values = ensure_object(entry, "env")
    env_values["POETIZE_BASE_URL"] = base_url
    return config


def main() -> None:
    args = parse_args()

    script_path = Path(__file__).resolve()
    skill_root = script_path.parents[1]
    openclaw_skills_dir = skill_root.parent
    repo_root = skill_root.parents[1]

    api_key = str(args.api_key or "").strip()
    if not api_key:
        if args.allow_placeholder_api_key:
            api_key = PLACEHOLDER_API_KEY
        else:
            die("Missing --api-key or POETIZE_API_KEY.")

    base_url = infer_base_url(args.base_url, repo_root)

    existing_config: dict[str, Any] = {}
    if args.existing_config:
        existing_config = load_json_object(Path(args.existing_config))

    generated = build_config(
        existing_config,
        extra_skill_dir=openclaw_skills_dir,
        base_url=base_url,
        api_key=api_key,
        disable_watch=args.disable_watch,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(generated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote OpenClaw config: {output_path}")
    print(f"Skill directory source: {openclaw_skills_dir}")
    print(f"Configured skill entry: {SKILL_KEY}")
    print(f"Configured base URL: {base_url}")
    if api_key == PLACEHOLDER_API_KEY:
        print("Configured apiKey is still a placeholder. Replace it before running OpenClaw.")


if __name__ == "__main__":
    main()
