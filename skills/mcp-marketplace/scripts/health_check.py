#!/usr/bin/env python3
"""Health check for MCP servers.

Spawns stdio servers or POSTs to HTTP servers, sends JSON-RPC initialize
+ tools/list, and returns structured health status as JSON to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError


def build_initialize_request() -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-marketplace-health-check", "version": "1.0"},
        },
    }


def build_list_tools_request() -> dict:
    return {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}


def resolve_env_vars(env: dict) -> tuple[dict, list[str]]:
    """Resolve ${VAR} references in env values using os.environ.

    Returns (resolved_dict, list_of_unresolved_var_names).
    """
    resolved = {}
    unresolved: list[str] = []
    pattern = re.compile(r"\$\{([^}]+)\}")

    for key, value in env.items():
        if not isinstance(value, str):
            resolved[key] = value
            continue

        missing_in_value: list[str] = []

        def replacer(m: re.Match) -> str:
            var_name = m.group(1)
            actual = os.environ.get(var_name)
            if actual is None:
                missing_in_value.append(var_name)
                return m.group(0)  # leave placeholder intact
            return actual

        resolved[key] = pattern.sub(replacer, value)
        unresolved.extend(missing_in_value)

    return resolved, unresolved


def load_server_by_id(base_dir: str, server_id: str) -> dict | None:
    """Load a server entry from known_servers.json by its ID (linear scan)."""
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


def build_server_command(server: dict) -> tuple[str, list[str], dict]:
    """Given server metadata, return (command, args, env) needed to spawn it."""
    install_method = server.get("installMethod", "")
    package = server.get("package", "")
    server_args = list(server.get("args", []))

    # Build env from requiredEnv
    env_template: dict[str, str] = {}
    for var_name in server.get("requiredEnv", []):
        env_template[var_name] = os.environ.get(var_name, "${" + var_name + "}")

    resolved_env, _ = resolve_env_vars(env_template)

    # Resolve any ${VAR} references inside server_args too
    arg_pattern = re.compile(r"\$\{([^}]+)\}")
    resolved_args = []
    for arg in server_args:
        if isinstance(arg, str):
            def arg_replacer(m: re.Match) -> str:
                return os.environ.get(m.group(1), m.group(0))
            resolved_args.append(arg_pattern.sub(arg_replacer, arg))
        else:
            resolved_args.append(arg)

    if install_method == "npx":
        command = "npx"
        args = ["-y", package] + resolved_args
    elif install_method == "uvx":
        command = "uvx"
        args = [package] + resolved_args
    elif install_method == "npm":
        command = package
        args = resolved_args
    elif install_method == "pip":
        # Derive module name from package (e.g. "mcp-server-foo" -> "mcp_server_foo")
        module_name = package.replace("-", "_")
        command = "python3"
        args = ["-m", module_name] + resolved_args
    else:
        # Fallback: treat package as the command
        command = package or server.get("id", "unknown")
        args = resolved_args

    return command, args, resolved_env


def _read_json_response(stdout, timeout: int) -> dict | None:
    """Read a single JSON-RPC response from stdout, handling newline-delimited
    or Content-Length framing."""
    result: list[dict | None] = [None]

    def reader() -> None:
        try:
            # Peek at first bytes to detect framing style
            first_chunk = stdout.read(1)
            if not first_chunk:
                return

            if first_chunk == b"C" or first_chunk == b"c":
                # Likely Content-Length framing
                rest_of_header = b""
                while True:
                    byte = stdout.read(1)
                    if not byte:
                        return
                    rest_of_header += byte
                    if rest_of_header.endswith(b"\r\n\r\n"):
                        break
                    # Safety limit
                    if len(rest_of_header) > 4096:
                        return

                header_line = (first_chunk + rest_of_header).decode("utf-8", errors="replace")
                match = re.search(r"Content-Length:\s*(\d+)", header_line, re.IGNORECASE)
                if match:
                    content_length = int(match.group(1))
                    body = stdout.read(content_length)
                    if body:
                        result[0] = json.loads(body)
                return

            # Newline-delimited: accumulate until we get a complete JSON line
            accumulated = first_chunk
            while True:
                byte = stdout.read(1)
                if not byte:
                    break
                accumulated += byte
                if byte in (b"\n", b"\r"):
                    line = accumulated.strip()
                    if line:
                        try:
                            result[0] = json.loads(line)
                            return
                        except json.JSONDecodeError:
                            # Not a complete JSON object yet, keep accumulating
                            pass
                    accumulated = b""
                # Safety limit
                if len(accumulated) > 1024 * 1024:
                    break

            # Try parsing whatever we accumulated
            if accumulated.strip():
                try:
                    result[0] = json.loads(accumulated.strip())
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]


def _send_request(proc: subprocess.Popen, request: dict) -> None:
    """Write a JSON-RPC request as newline-delimited JSON to the process stdin."""
    payload = json.dumps(request) + "\n"
    proc.stdin.write(payload.encode("utf-8"))
    proc.stdin.flush()


def check_stdio_server(command: str, args: list, env: dict, timeout: int) -> dict:
    """Spawn a stdio MCP server, send initialize + tools/list, return health status."""
    proc = None
    try:
        # Merge with os.environ so PATH and other essentials are inherited
        merged_env = dict(os.environ)
        merged_env.update(env)

        proc = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=merged_env,
        )

        # Send initialize
        _send_request(proc, build_initialize_request())

        init_response = _read_json_response(proc.stdout, timeout)
        if init_response is None:
            # Try to capture stderr for diagnostics
            stderr_output = ""
            try:
                stderr_output = proc.stderr.read(4096).decode("utf-8", errors="replace").strip()
            except Exception:
                pass
            return {
                "status": "unhealthy",
                "transport": "stdio",
                "initializeResponse": None,
                "tools": [],
                "toolCount": 0,
                "error": f"No response to initialize within {timeout}s"
                + (f": {stderr_output}" if stderr_output else ""),
            }

        if "error" in init_response:
            return {
                "status": "unhealthy",
                "transport": "stdio",
                "initializeResponse": init_response,
                "tools": [],
                "toolCount": 0,
                "error": f"Initialize returned error: {json.dumps(init_response['error'])}",
            }

        if "result" not in init_response:
            return {
                "status": "unhealthy",
                "transport": "stdio",
                "initializeResponse": init_response,
                "tools": [],
                "toolCount": 0,
                "error": "Initialize response missing 'result' field",
            }

        # Send tools/list
        _send_request(proc, build_list_tools_request())

        tools_response = _read_json_response(proc.stdout, timeout)
        tools: list = []
        if tools_response and "result" in tools_response:
            tools = tools_response["result"].get("tools", [])

        return {
            "status": "healthy",
            "transport": "stdio",
            "initializeResponse": init_response,
            "tools": tools,
            "toolCount": len(tools),
            "error": None,
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "transport": "stdio",
            "initializeResponse": None,
            "tools": [],
            "toolCount": 0,
            "error": f"Command not found: {command}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "transport": "stdio",
            "initializeResponse": None,
            "tools": [],
            "toolCount": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if proc is not None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            except Exception:
                pass


def check_http_server(url: str, headers: dict | None, timeout: int) -> dict:
    """POST initialize + tools/list to an HTTP MCP server, return health status."""
    try:
        # Send initialize
        init_payload = json.dumps(build_initialize_request()).encode("utf-8")
        req = Request(
            url,
            data=init_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urlopen(req, timeout=timeout) as resp:
            init_response = json.loads(resp.read().decode("utf-8"))

        if "error" in init_response:
            return {
                "status": "unhealthy",
                "transport": "http",
                "initializeResponse": init_response,
                "tools": [],
                "toolCount": 0,
                "error": f"Initialize returned error: {json.dumps(init_response['error'])}",
            }

        if "result" not in init_response:
            return {
                "status": "unhealthy",
                "transport": "http",
                "initializeResponse": init_response,
                "tools": [],
                "toolCount": 0,
                "error": "Initialize response missing 'result' field",
            }

        # Send tools/list
        tools_payload = json.dumps(build_list_tools_request()).encode("utf-8")
        tools_req = Request(
            url,
            data=tools_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        if headers:
            for k, v in headers.items():
                tools_req.add_header(k, v)

        tools: list = []
        try:
            with urlopen(tools_req, timeout=timeout) as resp:
                tools_response = json.loads(resp.read().decode("utf-8"))
                if "result" in tools_response:
                    tools = tools_response["result"].get("tools", [])
        except Exception:
            # tools/list failure is non-fatal; server is still healthy if initialize worked
            pass

        return {
            "status": "healthy",
            "transport": "http",
            "initializeResponse": init_response,
            "tools": tools,
            "toolCount": len(tools),
            "error": None,
        }

    except URLError as exc:
        return {
            "status": "error",
            "transport": "http",
            "initializeResponse": None,
            "tools": [],
            "toolCount": 0,
            "error": f"Connection failed: {exc.reason}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "transport": "http",
            "initializeResponse": None,
            "tools": [],
            "toolCount": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }


def load_server_from_config(config_path: str, server_id: str) -> dict | None:
    """Try to load server config from a .mcp.json file."""
    try:
        with open(config_path) as f:
            data = json.load(f)
        mcp_servers = data.get("mcpServers", {})
        if server_id not in mcp_servers:
            return None
        entry = mcp_servers[server_id]
        # Normalize to match known_servers.json schema
        return {
            "id": server_id,
            "transport": entry.get("transport", "stdio"),
            "installMethod": "",
            "package": "",
            "args": entry.get("args", []),
            "command": entry.get("command", ""),
            "url": entry.get("url", ""),
            "headers": entry.get("headers", {}),
            "requiredEnv": list(entry.get("env", {}).keys()),
            "_raw_env": entry.get("env", {}),
        }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Health check for MCP servers")
    parser.add_argument("--server-id", required=True, help="Server ID to check")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--config-path",
        default=None,
        help="Optional path to .mcp.json config file",
    )
    args = parser.parse_args()

    base_dir = str(Path(__file__).resolve().parent.parent)
    server_id = args.server_id

    try:
        # Try known_servers.json first
        server = load_server_by_id(base_dir, server_id)

        # Fallback to --config-path if provided and not found
        if server is None and args.config_path:
            server = load_server_from_config(args.config_path, server_id)

        if server is None:
            result = {
                "serverId": server_id,
                "status": "error",
                "transport": None,
                "initializeResponse": None,
                "tools": [],
                "toolCount": 0,
                "error": f"Server '{server_id}' not found in known_servers.json"
                + (f" or {args.config_path}" if args.config_path else ""),
            }
            json.dump(result, sys.stdout, indent=2)
            print()
            return

        transport = server.get("transport", "stdio")

        if transport == "http":
            url = server.get("url", "")
            if not url:
                result = {
                    "serverId": server_id,
                    "status": "error",
                    "transport": "http",
                    "initializeResponse": None,
                    "tools": [],
                    "toolCount": 0,
                    "error": "No URL configured for HTTP server",
                }
                json.dump(result, sys.stdout, indent=2)
                print()
                return

            # Resolve headers
            raw_headers = server.get("headers", {})
            if raw_headers:
                resolved_headers, _ = resolve_env_vars(raw_headers)
            else:
                resolved_headers = None

            check_result = check_http_server(url, resolved_headers, args.timeout)
        else:
            # stdio transport
            if server.get("command"):
                # From .mcp.json: command is already specified directly
                command = server["command"]
                server_args = list(server.get("args", []))
                raw_env = server.get("_raw_env", {})
                resolved_env, _ = resolve_env_vars(raw_env)
            else:
                command, server_args, resolved_env = build_server_command(server)

            check_result = check_stdio_server(
                command, server_args, resolved_env, args.timeout
            )

        output = {"serverId": server_id, **check_result}
        json.dump(output, sys.stdout, indent=2)
        print()

    except Exception as exc:
        result = {
            "serverId": server_id,
            "status": "error",
            "transport": None,
            "initializeResponse": None,
            "tools": [],
            "toolCount": 0,
            "error": f"Unexpected error: {type(exc).__name__}: {exc}",
        }
        json.dump(result, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
