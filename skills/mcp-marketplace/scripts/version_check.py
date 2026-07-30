#!/usr/bin/env python3
"""Check for available updates for installed MCP servers."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError


STATE_DIR = Path.home() / ".openclaw" / "mcp-marketplace"
STATE_FILE = STATE_DIR / "installed_servers.json"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"servers": {}}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"servers": {}}


def get_npm_latest_version(package: str) -> str | None:
    """Query npm registry for latest version."""
    try:
        url = f"https://registry.npmjs.org/{package}/latest"
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("version")
    except (URLError, json.JSONDecodeError, OSError):
        return None


def get_npm_installed_version(package: str) -> str | None:
    """Check locally installed npm global package version."""
    if not shutil.which("npm"):
        return None
    try:
        result = subprocess.run(
            ["npm", "list", "-g", package, "--json", "--depth=0"],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(result.stdout)
        deps = data.get("dependencies", {})
        if package in deps:
            return deps[package].get("version")
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def get_pypi_latest_version(package: str) -> str | None:
    """Query PyPI for latest version."""
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("info", {}).get("version")
    except (URLError, json.JSONDecodeError, OSError):
        return None


def get_pip_installed_version(package: str) -> str | None:
    """Check locally installed pip package version."""
    pip_cmd = "pip3" if shutil.which("pip3") else "pip" if shutil.which("pip") else None
    if not pip_cmd:
        return None
    try:
        result = subprocess.run(
            [pip_cmd, "show", package],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
        return None
    except (subprocess.TimeoutExpired, OSError):
        return None


def check_server_version(server_id: str, server_info: dict) -> dict:
    """Check version status for a single server."""
    method = server_info.get("installMethod", "")
    package = server_info.get("package", "")

    result = {
        "serverId": server_id,
        "package": package,
        "installMethod": method,
        "currentVersion": None,
        "latestVersion": None,
        "updateAvailable": False,
        "updateCommand": None,
        "note": None,
    }

    if method == "npx":
        # npx always resolves latest on run — no explicit update needed
        latest = get_npm_latest_version(package)
        result["latestVersion"] = latest
        result["note"] = "npx resolves the latest version on each run — no update needed"
        return result

    elif method == "npm":
        current = get_npm_installed_version(package)
        latest = get_npm_latest_version(package)
        result["currentVersion"] = current
        result["latestVersion"] = latest
        if current and latest and current != latest:
            result["updateAvailable"] = True
            result["updateCommand"] = f"npm update -g {package}"
        return result

    elif method == "uvx":
        # uvx resolves latest on run — similar to npx
        result["note"] = "uvx resolves the latest version on each run — no update needed"
        return result

    elif method == "pip":
        current = get_pip_installed_version(package)
        latest = get_pypi_latest_version(package)
        result["currentVersion"] = current
        result["latestVersion"] = latest
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"
        if current and latest and current != latest:
            result["updateAvailable"] = True
            result["updateCommand"] = f"{pip_cmd} install --upgrade {package}"
        return result

    elif method == "http":
        result["note"] = "HTTP servers are managed remotely — no local update needed"
        return result

    elif method == "docker":
        result["note"] = "Run 'docker pull <image>' to get the latest version"
        if package:
            result["updateCommand"] = f"docker pull {server_info.get('dockerImage', package)}"
        return result

    else:
        result["note"] = f"Unknown install method: {method}"
        return result


def main():
    parser = argparse.ArgumentParser(description="Check for MCP server updates")
    parser.add_argument("--server-id", default=None, help="Check specific server (omit for all)")
    args = parser.parse_args()

    state = load_state()
    servers = state.get("servers", {})

    if not servers:
        json.dump({"action": "version-check", "servers": [], "note": "No servers installed"}, sys.stdout, indent=2)
        print()
        return

    results = []
    if args.server_id:
        if args.server_id not in servers:
            json.dump({"error": f"Server '{args.server_id}' not found in installed servers"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        results.append(check_server_version(args.server_id, servers[args.server_id]))
    else:
        for sid, info in servers.items():
            results.append(check_server_version(sid, info))

    updates_available = [r for r in results if r["updateAvailable"]]

    output = {
        "action": "version-check",
        "totalChecked": len(results),
        "updatesAvailable": len(updates_available),
        "servers": results,
    }
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
