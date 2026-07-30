#!/usr/bin/env python3
"""Manage installed MCP servers: list, record, remove, info, status, update-status."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "mcp-marketplace"
STATE_FILE = STATE_DIR / "installed_servers.json"


def ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"version": 1, "servers": {}}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        # Corrupt file — back up and start fresh
        backup = STATE_FILE.with_suffix(".json.bak")
        STATE_FILE.rename(backup)
        return {"version": 1, "servers": {}}


def save_state(state: dict):
    ensure_state_dir()
    tmp_file = STATE_FILE.with_suffix(".json.tmp")
    fd = os.open(str(tmp_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.rename(str(tmp_file), str(STATE_FILE))


def _find_config_path(server_id: str) -> str | None:
    """Check common config file locations for a server entry."""
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
                if server_id in config.get("mcpServers", {}):
                    return str(p)
            except (json.JSONDecodeError, KeyError, OSError):
                continue
    return None


def _check_config_exists(server_id: str) -> bool:
    return _find_config_path(server_id) is not None


def action_list(state: dict) -> dict:
    servers = state.get("servers", {})
    enriched = {}
    for sid, info in servers.items():
        enriched[sid] = {**info, "configPresent": _check_config_exists(sid)}
    return {"action": "list", "count": len(servers), "servers": enriched}


def action_record(
    state: dict,
    server_id: str,
    package: str,
    transport: str,
    install_method: str,
    via_bundle: bool = False,
    source: str = "curated",
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    state["servers"][server_id] = {
        "installedAt": now,
        "package": package,
        "transport": transport,
        "installMethod": install_method,
        "source": source,
        "installedViaBundle": via_bundle,
        "status": "active",
    }
    save_state(state)
    return {
        "action": "record",
        "serverId": server_id,
        "recorded": True,
        "server": state["servers"][server_id],
    }


def action_remove(state: dict, server_id: str) -> dict:
    if server_id not in state.get("servers", {}):
        return {"action": "remove", "serverId": server_id, "removed": False, "error": "Server not found in state"}
    del state["servers"][server_id]
    save_state(state)
    return {"action": "remove", "serverId": server_id, "removed": True}


def action_info(state: dict, server_id: str) -> dict:
    servers = state.get("servers", {})
    if server_id not in servers:
        return {"action": "info", "serverId": server_id, "found": False, "error": "Server not found in state"}
    return {
        "action": "info",
        "serverId": server_id,
        "found": True,
        "server": servers[server_id],
    }


def action_status(state: dict, server_id: str) -> dict:
    """Check if a specific server is recorded and return enriched info."""
    servers = state.get("servers", {})
    if server_id not in servers:
        return {"action": "status", "serverId": server_id, "found": False, "error": "Server not found in state"}
    server = servers[server_id]
    config_path = _find_config_path(server_id)
    return {
        "action": "status",
        "serverId": server_id,
        "found": True,
        "server": server,
        "configPath": config_path,
        "configPresent": config_path is not None,
    }


def action_update_status(state: dict, server_id: str, new_status: str) -> dict:
    """Update the status field of a recorded server."""
    if server_id not in state.get("servers", {}):
        return {"action": "update-status", "serverId": server_id, "updated": False, "error": "Not found"}
    state["servers"][server_id]["status"] = new_status
    state["servers"][server_id]["lastChecked"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    return {"action": "update-status", "serverId": server_id, "updated": True, "status": new_status}


def main():
    parser = argparse.ArgumentParser(description="Manage installed MCP servers")
    parser.add_argument("--action", required=True, choices=["list", "record", "remove", "info", "status", "update-status"])
    parser.add_argument("--server-id", default=None)
    parser.add_argument("--package", default=None)
    parser.add_argument("--transport", default=None)
    parser.add_argument("--install-method", default=None)
    parser.add_argument("--via-bundle", action="store_true")
    parser.add_argument("--source", default="curated", choices=["curated", "npm", "smithery"])
    parser.add_argument("--status", default=None, choices=["active", "inactive", "error"])
    args = parser.parse_args()

    ensure_state_dir()
    state = load_state()

    if args.action == "list":
        result = action_list(state)
    elif args.action == "record":
        if not all([args.server_id, args.package, args.transport, args.install_method]):
            json.dump(
                {"error": "record action requires --server-id, --package, --transport, and --install-method"},
                sys.stdout,
                indent=2,
            )
            print()
            sys.exit(1)
        result = action_record(state, args.server_id, args.package, args.transport, args.install_method, args.via_bundle, args.source)
    elif args.action == "remove":
        if not args.server_id:
            json.dump({"error": "remove action requires --server-id"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        result = action_remove(state, args.server_id)
    elif args.action == "info":
        if not args.server_id:
            json.dump({"error": "info action requires --server-id"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        result = action_info(state, args.server_id)
    elif args.action == "status":
        if not args.server_id:
            json.dump({"error": "status action requires --server-id"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        result = action_status(state, args.server_id)
    elif args.action == "update-status":
        if not args.server_id or not args.status:
            json.dump({"error": "update-status action requires --server-id and --status"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        result = action_update_status(state, args.server_id, args.status)
    else:
        json.dump({"error": f"Unknown action: {args.action}"}, sys.stdout, indent=2)
        print()
        sys.exit(1)

    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
