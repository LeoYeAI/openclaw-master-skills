#!/usr/bin/env python3
"""Resolve server bundles and plan bulk installations."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def load_bundles(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "server_bundles.json"
    try:
        with open(path) as f:
            return json.load(f)["bundles"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def load_known_servers(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "known_servers.json"
    try:
        with open(path) as f:
            data = json.load(f)
        return {s["id"]: s for s in data["servers"]}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def load_installed_state() -> dict:
    state_file = Path.home() / ".openclaw" / "mcp-marketplace" / "installed_servers.json"
    if not state_file.exists():
        return {}
    try:
        with open(state_file) as f:
            return json.load(f).get("servers", {})
    except (json.JSONDecodeError, KeyError):
        return {}


def _find_config_servers() -> set:
    """Check common config files for already-configured servers."""
    configured = set()
    paths = [
        Path.cwd() / ".mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
    ]
    if platform.system() == "Darwin":
        paths.append(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
    elif platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            paths.append(Path(appdata) / "Claude" / "claude_desktop_config.json")
    else:
        paths.append(Path.home() / ".config" / "claude" / "claude_desktop_config.json")

    for p in paths:
        if p.exists():
            try:
                with open(p) as f:
                    config = json.load(f)
                configured.update(config.get("mcpServers", {}).keys())
            except (json.JSONDecodeError, OSError):
                continue
    return configured


def resolve_bundle(base_dir: str, bundle_name: str) -> dict:
    bundles = load_bundles(base_dir)

    if bundle_name == "__list__":
        return {
            "action": "list-bundles",
            "bundles": {
                name: {"displayName": b["displayName"], "description": b["description"], "serverCount": len(b["servers"])}
                for name, b in bundles.items()
            },
        }

    if bundle_name not in bundles:
        return {"error": f"Bundle '{bundle_name}' not found. Available: {', '.join(bundles.keys())}"}

    bundle = bundles[bundle_name]
    known = load_known_servers(base_dir)
    installed = load_installed_state()
    configured = _find_config_servers()

    servers_plan = []
    for sid in bundle["servers"]:
        server_info = known.get(sid)
        status = "not-installed"
        if sid in installed:
            status = "installed"
        if sid in configured:
            status = "configured"

        entry = {
            "serverId": sid,
            "displayName": server_info["displayName"] if server_info else sid,
            "status": status,
        }
        if server_info:
            entry["installMethod"] = server_info["installMethod"]
            entry["requiredEnv"] = server_info.get("requiredEnv", [])
        servers_plan.append(entry)

    to_install = [s for s in servers_plan if s["status"] == "not-installed"]
    already_done = [s for s in servers_plan if s["status"] in ("installed", "configured")]

    return {
        "action": "resolve-bundle",
        "bundleName": bundle_name,
        "displayName": bundle["displayName"],
        "description": bundle["description"],
        "totalServers": len(bundle["servers"]),
        "toInstall": to_install,
        "alreadyInstalled": already_done,
        "installCount": len(to_install),
        "skipCount": len(already_done),
    }


def main():
    parser = argparse.ArgumentParser(description="Resolve server bundles for bulk installation")
    parser.add_argument("--bundle", required=True, help="Bundle name or '__list__' to list all bundles")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    result = resolve_bundle(str(base_dir), args.bundle)
    json.dump(result, sys.stdout, indent=2)
    print()

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
