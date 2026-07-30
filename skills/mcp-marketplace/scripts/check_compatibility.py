#!/usr/bin/env python3
"""Check MCP server and client compatibility."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_compatibility_matrix(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "compatibility_matrix.json"
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"clients": {}, "serverOverrides": {}}


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


def check_compatibility(base_dir: str, server_id: str, client: str) -> dict:
    matrix = load_compatibility_matrix(base_dir)
    server = load_server_by_id(base_dir, server_id)

    if not server:
        return {
            "compatible": False,
            "serverId": server_id,
            "client": client,
            "error": f"Server '{server_id}' not found in catalog",
        }

    client_info = matrix.get("clients", {}).get(client)
    if not client_info:
        return {
            "compatible": True,
            "serverId": server_id,
            "client": client,
            "warning": f"Client '{client}' not in compatibility matrix — assuming compatible",
        }

    warnings = []
    compatible = True

    # Check transport compatibility
    transport = server.get("transport", "stdio")
    if transport not in client_info.get("supportedTransports", []):
        compatible = False
        warnings.append(
            f"{client_info['displayName']} does not support {transport} transport. "
            f"Supported: {', '.join(client_info['supportedTransports'])}"
        )

    # Check env var resolution
    if not client_info.get("envResolution", True) and server.get("requiredEnv"):
        warnings.append(
            f"{client_info['displayName']} may not resolve ${{VAR}} references automatically. "
            "You may need to hardcode values in the config (not recommended for secrets)."
        )

    # Check server-specific overrides
    overrides = matrix.get("serverOverrides", {}).get(server_id, {})
    if client in overrides.get("incompatible", []):
        compatible = False
        warnings.append(overrides.get("reason", "Server is incompatible with this client"))

    # Include client notes if any
    if client_info.get("notes"):
        warnings.append(client_info["notes"])

    result = {
        "compatible": compatible,
        "serverId": server_id,
        "serverName": server.get("displayName", server_id),
        "client": client,
        "clientName": client_info["displayName"],
        "transport": transport,
    }
    if warnings:
        result["warnings"] = warnings

    return result


def main():
    parser = argparse.ArgumentParser(description="Check MCP server and client compatibility")
    parser.add_argument("--server-id", required=True, help="Server ID from catalog")
    parser.add_argument(
        "--client",
        required=True,
        choices=["openclaw", "claude-desktop", "claude-code", "cursor"],
        help="Target client",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    result = check_compatibility(str(base_dir), args.server_id, args.client)
    json.dump(result, sys.stdout, indent=2)
    print()

    if not result.get("compatible", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
