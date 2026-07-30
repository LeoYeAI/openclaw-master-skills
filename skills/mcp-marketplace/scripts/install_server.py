#!/usr/bin/env python3
"""Check prerequisites and generate install commands for MCP server packages.

This script does NOT execute install commands. It checks prerequisites
and returns the exact command the agent should run via its Bash tool.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def load_server_by_id(base_dir: str, server_id: str) -> dict | None:
    path = Path(base_dir) / "assets" / "known_servers.json"
    try:
        with open(path) as f:
            servers = json.load(f)["servers"]
        for s in servers:
            if s["id"] == server_id:
                return s
        return None
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def check_command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_prerequisites(install_method: str) -> dict:
    if install_method == "npx":
        missing = []
        if not check_command_exists("npx"):
            missing.append("npx")
        if not check_command_exists("node"):
            missing.append("node")
        return {
            "met": len(missing) == 0,
            "missing": missing,
            "suggestion": "Install Node.js from https://nodejs.org" if missing else "",
        }
    elif install_method == "npm":
        met = check_command_exists("npm")
        return {
            "met": met,
            "missing": [] if met else ["npm"],
            "suggestion": "" if met else "Install Node.js from https://nodejs.org",
        }
    elif install_method == "uvx":
        if check_command_exists("uvx"):
            return {"met": True, "missing": [], "suggestion": ""}
        if check_command_exists("uv"):
            return {"met": True, "missing": [], "suggestion": ""}
        return {
            "met": False,
            "missing": ["uvx"],
            "suggestion": "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh",
        }
    elif install_method == "pip":
        if check_command_exists("pip3"):
            return {"met": True, "missing": [], "suggestion": ""}
        if check_command_exists("pip"):
            return {"met": True, "missing": [], "suggestion": ""}
        return {
            "met": False,
            "missing": ["pip"],
            "suggestion": "Install pip: python3 -m ensurepip --upgrade",
        }
    elif install_method == "http":
        return {"met": True, "missing": [], "suggestion": ""}
    elif install_method == "docker":
        met = check_command_exists("docker")
        return {
            "met": met,
            "missing": [] if met else ["docker"],
            "suggestion": "" if met else "Install Docker from https://docs.docker.com/get-docker/",
        }
    else:
        return {
            "met": False,
            "missing": [install_method],
            "suggestion": f"Unknown install method: {install_method}",
        }


def build_install_command(server: dict) -> dict:
    """Return the command the agent should run to install/verify the package."""
    method = server["installMethod"]
    package = server["package"]

    if method == "npx":
        return {
            "command": f"npx -y {package} --help",
            "description": f"Verify {package} is available via npx (downloads on first use)",
            "note": "npx packages don't need global install — they download on demand",
        }
    elif method == "npm":
        return {
            "command": f"npm install -g {package}",
            "description": f"Install {package} globally via npm",
            "note": "Requires npm write permissions. Use sudo if needed.",
        }
    elif method == "uvx":
        return {
            "command": f"uvx {package} --help",
            "description": f"Verify {package} is available via uvx (downloads on first use)",
            "fallbackCommand": f"uv tool install {package}",
            "note": "uvx packages resolve on demand. If verification fails, try the fallback command.",
        }
    elif method == "pip":
        pip_cmd = "pip3" if check_command_exists("pip3") else "pip"
        return {
            "command": f"{pip_cmd} install {package}",
            "description": f"Install {package} via {pip_cmd}",
            "note": "Consider using a virtual environment for isolation.",
        }
    elif method == "http":
        return {
            "command": None,
            "description": f"No installation needed for HTTP server '{server['displayName']}'",
            "note": "Just configure the URL in .mcp.json",
        }
    elif method == "docker":
        return {
            "command": f"docker pull {server['dockerImage']}",
            "description": f"Pull Docker image {server['dockerImage']}",
            "note": "After pulling, the server runs via docker run in the MCP config",
            "runCommand": f"docker run -i --rm {server['dockerImage']}",
        }
    else:
        return {
            "command": None,
            "description": f"Unknown install method: {method}",
            "note": "",
        }


def main():
    parser = argparse.ArgumentParser(description="Check prerequisites and generate install commands for MCP servers")
    parser.add_argument("--server-id", required=True, help="Server ID from catalog")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    server = load_server_by_id(str(base_dir), args.server_id)

    if not server:
        json.dump({"error": f"Server '{args.server_id}' not found in catalog"}, sys.stdout, indent=2)
        print()
        sys.exit(1)

    method = server["installMethod"]
    prereqs = check_prerequisites(method)
    install_cmd = build_install_command(server)

    output = {
        "serverId": server["id"],
        "installMethod": method,
        "package": server["package"],
        "prerequisitesMet": prereqs["met"],
        "prerequisites": prereqs,
        "installCommand": install_cmd,
    }
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
