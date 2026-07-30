#!/usr/bin/env python3
"""Generate .mcp.json config entries for MCP servers."""
from __future__ import annotations

import argparse
import json
import os
import platform
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


CLIENT_CONFIG_PATHS = {
    "openclaw": {
        "key": "mcpServers",
        "description": "OpenClaw project config",
    },
    "claude-desktop": {
        "key": "mcpServers",
        "description": "Claude Desktop config",
    },
    "claude-code": {
        "key": "mcpServers",
        "description": "Claude Code project config",
    },
    "cursor": {
        "key": "mcpServers",
        "description": "Cursor editor config",
    },
}


def _claude_desktop_path() -> Path:
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def get_config_path(client: str) -> Path:
    """Return the config file path for the given client."""
    if client == "claude-desktop":
        return _claude_desktop_path()
    elif client == "cursor":
        return Path.cwd() / ".cursor" / "mcp.json"
    else:  # openclaw, claude-code
        return Path.cwd() / ".mcp.json"


def detect_client() -> str:
    """Detect which MCP client is likely running based on environment."""
    if os.environ.get("OPENCLAW_HOME"):
        return "openclaw"
    if os.environ.get("CLAUDE_CODE"):
        return "claude-code"
    if os.environ.get("CURSOR_SESSION"):
        return "cursor"
    if _claude_desktop_path().exists():
        return "claude-desktop"
    return "openclaw"


def build_stdio_config(
    server: dict, custom_env: dict | None, custom_args: list | None
) -> dict:
    method = server["installMethod"]
    package = server["package"]
    base_args = list(server.get("args", []))

    if method == "npx":
        command = "npx"
        args = ["-y", package] + base_args
    elif method == "uvx":
        command = "uvx"
        args = [package] + base_args
    elif method == "npm":
        command = package
        args = base_args
    elif method == "pip":
        module_name = package.replace("-", "_")
        command = "python3"
        args = ["-m", module_name] + base_args
    elif method == "docker":
        command = "docker"
        volume_args = []
        for vol in server.get("dockerVolumes", []):
            volume_args.extend(["-v", vol])
        port_args = []
        for port in server.get("dockerPorts", []):
            port_args.extend(["-p", port])
        args = ["run", "-i", "--rm"] + volume_args + port_args + [server["dockerImage"]] + base_args
    else:
        command = package
        args = base_args

    if custom_args:
        args.extend(custom_args)

    env = {}
    for var in server.get("requiredEnv", []):
        env[var] = f"${{{var}}}"
    if custom_env:
        env.update(custom_env)

    config = {"type": "stdio", "command": command, "args": args}
    if env:
        config["env"] = env

    return config


def build_http_config(server: dict, custom_env: dict | None) -> dict:
    config = {"type": "http", "url": server["package"]}

    required = server.get("requiredEnv", [])
    if required:
        token_var = required[0]
        config["headers"] = {"Authorization": f"Bearer ${{{token_var}}}"}

    return config


def build_auth_guidance(server: dict) -> dict:
    required = server.get("requiredEnv", [])
    links = server.get("requiredEnvLinks", {})
    descriptions = server.get("requiredEnvDescriptions", {})
    auth_type = server.get("authType", "token")

    instructions = []
    for var in required:
        instruction = {
            "envVar": var,
            "description": descriptions.get(var, f"Required for {server['displayName']}"),
            "shellCommand": f"export {var}=<your-value-here>",
        }
        if var in links:
            instruction["generateUrl"] = links[var]
        instructions.append(instruction)

    result = {"requiredEnv": required, "authType": auth_type, "instructions": instructions}

    if auth_type == "oauth":
        oauth_config = server.get("oauthConfig", {})
        result["oauthProvider"] = oauth_config.get("provider", "unknown")
        result["oauthScopes"] = oauth_config.get("scopes", [])
        result["oauthSetupSteps"] = oauth_config.get("setupSteps", [])
        result["referenceDoc"] = "references/oauth-patterns.md"

    return result


def main():
    parser = argparse.ArgumentParser(description="Build MCP server config entry")
    parser.add_argument("--server-id", required=True, help="Server ID from catalog")
    parser.add_argument("--custom-env", default=None, help="JSON object of custom env overrides")
    parser.add_argument("--custom-args", default=None, help="JSON array of additional args")
    parser.add_argument(
        "--client",
        default=None,
        choices=["openclaw", "claude-desktop", "claude-code", "cursor"],
        help="Target client (auto-detected if omitted)",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    server = load_server_by_id(str(base_dir), args.server_id)

    if not server:
        json.dump({"error": f"Server '{args.server_id}' not found in catalog"}, sys.stdout, indent=2)
        print()
        sys.exit(1)

    try:
        custom_env = json.loads(args.custom_env) if args.custom_env else None
    except json.JSONDecodeError:
        json.dump({"error": "Invalid JSON in --custom-env"}, sys.stdout, indent=2)
        print()
        sys.exit(1)

    try:
        custom_args = json.loads(args.custom_args) if args.custom_args else None
    except json.JSONDecodeError:
        json.dump({"error": "Invalid JSON in --custom-args"}, sys.stdout, indent=2)
        print()
        sys.exit(1)

    if server["transport"] == "stdio":
        config_entry = build_stdio_config(server, custom_env, custom_args)
    else:
        config_entry = build_http_config(server, custom_env)

    client = args.client or detect_client()

    # Check compatibility
    compat_path = Path(__file__).resolve().parent / "check_compatibility.py"
    if compat_path.exists():
        import subprocess
        compat_result = subprocess.run(
            ["python3", str(compat_path), "--server-id", args.server_id, "--client", client],
            capture_output=True, text=True
        )
        if compat_result.returncode != 0:
            try:
                compat_data = json.loads(compat_result.stdout)
                json.dump({
                    "error": "Compatibility issue detected",
                    "compatibility": compat_data,
                }, sys.stdout, indent=2)
                print()
                sys.exit(1)
            except json.JSONDecodeError:
                pass  # If compat check fails to parse, continue anyway

    client_info = CLIENT_CONFIG_PATHS[client]
    config_path = get_config_path(client)

    output = {
        "serverId": server["id"],
        "configEntry": {server["id"]: config_entry},
        "authGuidance": build_auth_guidance(server),
        "mergeTarget": str(config_path),
        "client": client,
        "clientDescription": client_info["description"],
        "configKey": client_info["key"],
    }
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
