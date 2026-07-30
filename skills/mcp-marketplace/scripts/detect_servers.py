#!/usr/bin/env python3
"""Detect MCP server packages installed on the system but not yet configured."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def load_known_servers(base_dir: str) -> list[dict]:
    path = Path(base_dir) / "assets" / "known_servers.json"
    try:
        with open(path) as f:
            return json.load(f)["servers"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def _find_configured_servers() -> set[str]:
    """Check common config file locations for already-configured servers."""
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


def scan_npm_globals() -> dict[str, str]:
    """Scan npm global packages. Returns {package_name: version}."""
    if not shutil.which("npm"):
        return {}
    try:
        result = subprocess.run(
            ["npm", "list", "-g", "--json", "--depth=0"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        deps = data.get("dependencies", {})
        return {pkg: info.get("version", "unknown") for pkg, info in deps.items()}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {}


def scan_pip_packages() -> dict[str, str]:
    """Scan pip packages. Returns {package_name: version}."""
    pip_cmd = "pip3" if shutil.which("pip3") else "pip" if shutil.which("pip") else None
    if not pip_cmd:
        return {}
    try:
        result = subprocess.run(
            [pip_cmd, "list", "--format=json"],
            capture_output=True, text=True, timeout=15,
        )
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {}


def scan_uv_tools() -> dict[str, str]:
    """Scan uv tool packages. Returns {package_name: version}."""
    if not shutil.which("uv"):
        return {}
    try:
        result = subprocess.run(
            ["uv", "tool", "list"],
            capture_output=True, text=True, timeout=15,
        )
        # Parse output format: "package-name v1.2.3"
        tools = {}
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("-"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1].lstrip("v")
                tools[name] = version
        return tools
    except (subprocess.TimeoutExpired, OSError):
        return {}


def match_packages(known_servers: list[dict], installed_packages: dict[str, dict]) -> list[dict]:
    """Match installed packages against known server catalog."""
    matches = []
    for server in known_servers:
        package = server.get("package", "")
        # Check if the package name matches any installed package
        for pkg_name, pkg_info in installed_packages.items():
            # Match by exact package name or by the last segment (e.g., "@scope/name" matches "name")
            pkg_base = package.split("/")[-1] if "/" in package else package
            if pkg_name == package or pkg_name == pkg_base:
                matches.append({
                    "serverId": server["id"],
                    "displayName": server["displayName"],
                    "package": package,
                    "installedPackage": pkg_name,
                    "version": pkg_info["version"],
                    "source": pkg_info["source"],
                    "installMethod": server["installMethod"],
                })
                break
    return matches


def main():
    parser = argparse.ArgumentParser(description="Detect installed MCP server packages")
    parser.add_argument("--verbose", action="store_true", help="Include scan details")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    known_servers = load_known_servers(str(base_dir))
    configured = _find_configured_servers()

    # Scan all package managers
    all_packages = {}

    npm_pkgs = scan_npm_globals()
    for name, version in npm_pkgs.items():
        all_packages[name] = {"version": version, "source": "npm-global"}

    pip_pkgs = scan_pip_packages()
    for name, version in pip_pkgs.items():
        all_packages[name] = {"version": version, "source": "pip"}

    uv_pkgs = scan_uv_tools()
    for name, version in uv_pkgs.items():
        all_packages[name] = {"version": version, "source": "uv-tool"}

    # Match against catalog
    detected = match_packages(known_servers, all_packages)

    # Classify as configured vs unconfigured
    already_configured = []
    unconfigured = []
    for d in detected:
        if d["serverId"] in configured:
            d["configured"] = True
            already_configured.append(d)
        else:
            d["configured"] = False
            unconfigured.append(d)

    output = {
        "action": "detect",
        "totalScanned": len(all_packages),
        "totalDetected": len(detected),
        "unconfigured": unconfigured,
        "alreadyConfigured": already_configured,
    }

    if args.verbose:
        output["scanDetails"] = {
            "npmGlobalCount": len(npm_pkgs),
            "pipCount": len(pip_pkgs),
            "uvToolCount": len(uv_pkgs),
        }

    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
