import json
from pathlib import Path
import requests

CONFIG = json.loads(Path("mcp_config.json").read_text(encoding="utf-8"))
AUTH_TOKEN = CONFIG["auth_token"]

BASE = "https://api-mcp.51ifind.com:8643/ds-mcp-servers"
SERVERS = {
    "stock": f"{BASE}/hexin-ifind-ds-stock-mcp",
    "fund": f"{BASE}/hexin-ifind-ds-fund-mcp",
    "edb": f"{BASE}/hexin-ifind-ds-edb-mcp",
    "news": f"{BASE}/hexin-ifind-ds-news-mcp",
}

_sessions = {}
_req_ids = {}


def _next_id(t):
    _req_ids[t] = _req_ids.get(t, 0) + 1
    return _req_ids[t]


def _headers(t=None):
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": AUTH_TOKEN,
    }
    if t in _sessions:
        h["Mcp-Session-Id"] = _sessions[t]
    return h


def _post(t, payload, timeout=60):
    resp = requests.post(
        SERVERS[t],
        json=payload,
        headers=_headers(t),
        verify=False,
        timeout=timeout,
    )
    data = None
    if resp.text.strip():
        try:
            data = resp.json()
        except Exception:
            data = resp.text
    return resp, data


def _init(t):
    if t in _sessions:
        return

    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(t),
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "http-client", "version": "1.0.0"},
        },
    }

    resp, data = _post(t, payload, timeout=30)
    resp.raise_for_status()

    session_id = resp.headers.get("Mcp-Session-Id")
    if not session_id:
        raise RuntimeError(f"initialize 成功但未返回 Mcp-Session-Id: {data}")

    _sessions[t] = session_id

    notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    requests.post(
        SERVERS[t],
        json=notify,
        headers=_headers(t),
        verify=False,
        timeout=10,
    )


def call(server_type, tool_name, params):
    if server_type not in SERVERS:
        raise ValueError(f"unknown server_type: {server_type}")

    _init(server_type)

    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(server_type),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params,
        },
    }

    resp, data = _post(server_type, payload)

    if isinstance(data, dict) and "error" in data:
        return {
            "ok": False,
            "status_code": resp.status_code,
            "error": data["error"],
            "raw": data,
        }

    resp.raise_for_status()
    return {
        "ok": True,
        "status_code": resp.status_code,
        "data": data,
    }


def list_tools(server_type):
    if server_type not in SERVERS:
        raise ValueError(f"unknown server_type: {server_type}")

    _init(server_type)

    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(server_type),
        "method": "tools/list",
        "params": {},
    }

    resp, data = _post(server_type)

    if isinstance(data, dict) and "error" in data:
        return {
            "ok": False,
            "status_code": resp.status_code,
            "error": data["error"],
            "raw": data,
        }

    resp.raise_for_status()

    return {
        "ok": True,
        "status_code": resp.status_code,
        "data": data,
    }


if __name__ == "__main__":
    print("未调用工具函数及输入查询参数，请按照说明文档发起请求")    