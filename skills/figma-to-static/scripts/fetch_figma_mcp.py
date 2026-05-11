#!/usr/bin/env python3
"""Fetch Figma node metadata, screenshots, and design context via MCP protocol.

Auth modes:
1) Explicit env token (recommended): FIGMA_MCP_TOKEN
2) Optional Claude credentials mode (--allow-claude-credentials)

Notable features:
- Auto refresh expired/near-expiry OAuth token when using Claude credentials mode
- Reuse a single MCP session for batch node extraction
- Optional bundle action to fetch metadata + screenshot + context in one run
"""

import argparse
import base64
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

MCP_URL = "https://mcp.figma.com/mcp"
PROTOCOL_VERSION = "2025-03-26"
DEFAULT_CRED_PATH = os.path.expanduser("~/.claude/.credentials.json")
TOKEN_REFRESH_MARGIN_MS = 2 * 60 * 1000
DEFAULT_AUTH_SERVER = "https://api.figma.com"


def fix_encoding(text):
    """Fix mojibake: latin1-encoded UTF-8 bytes."""
    try:
        fixed = text.encode("latin1").decode("utf-8")
        if "å" in text and any("\u4e00" <= c <= "\u9fff" for c in fixed):
            return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return text


def _load_credential_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_figma_oauth_entry(cred):
    for k, v in cred.get("mcpOAuth", {}).items():
        if isinstance(v, dict) and (v.get("serverName") == "figma" or k.startswith("figma|")):
            return k, v
    return None, None


def _discover_token_endpoint(entry):
    state = entry.get("discoveryState") or {}
    auth_server = state.get("authorizationServerUrl") or DEFAULT_AUTH_SERVER
    well_known = auth_server.rstrip("/") + "/.well-known/oauth-authorization-server"

    try:
        req = Request(well_known, headers={"Accept": "application/json"})
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        endpoint = data.get("token_endpoint")
        if endpoint:
            return endpoint
    except Exception:
        pass

    # Figma default fallback
    if auth_server.startswith("https://api.figma.com"):
        return "https://api.figma.com/v1/oauth/token"

    return None


def _atomic_write_json(path, data):
    parent = Path(path).parent
    parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(parent), encoding="utf-8") as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    os.replace(tmp_path, path)


def _refresh_token_if_needed(cred_path, cred, entry_key, entry):
    exp = int(entry.get("expiresAt") or 0)
    now_ms = int(time.time() * 1000)

    if exp and exp - now_ms > TOKEN_REFRESH_MARGIN_MS:
        return entry.get("accessToken"), False

    refresh_token = entry.get("refreshToken")
    client_id = entry.get("clientId")
    client_secret = entry.get("clientSecret")

    if not refresh_token or not client_id or not client_secret:
        if exp and exp <= now_ms:
            return None, False
        return entry.get("accessToken"), False

    token_endpoint = _discover_token_endpoint(entry)
    if not token_endpoint:
        if exp and exp <= now_ms:
            return None, False
        return entry.get("accessToken"), False

    form = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    req = Request(
        token_endpoint,
        data=urlencode(form).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"WARNING: Failed to refresh Figma MCP token: {e}", file=sys.stderr)
        if exp and exp <= now_ms:
            return None, False
        return entry.get("accessToken"), False

    new_access = payload.get("access_token")
    if not new_access:
        print("WARNING: Token refresh response missing access_token", file=sys.stderr)
        if exp and exp <= now_ms:
            return None, False
        return entry.get("accessToken"), False

    expires_in = int(payload.get("expires_in") or 3600)
    new_exp_ms = int(time.time() * 1000) + expires_in * 1000

    entry["accessToken"] = new_access
    entry["expiresAt"] = new_exp_ms
    if payload.get("refresh_token"):
        entry["refreshToken"] = payload["refresh_token"]

    cred.setdefault("mcpOAuth", {})[entry_key] = entry
    try:
        _atomic_write_json(cred_path, cred)
    except Exception as e:
        print(f"WARNING: Refreshed token but failed to persist credentials: {e}", file=sys.stderr)

    return new_access, True


def get_token(allow_claude_credentials=False, credentials_path=None):
    """Read Figma MCP OAuth token.

    Priority:
    1) FIGMA_MCP_TOKEN env var (explicit)
    2) Claude credentials file (only when allow_claude_credentials=True)
    """
    tok = os.environ.get("FIGMA_MCP_TOKEN")
    if tok:
        return tok

    if not allow_claude_credentials:
        return None

    cred_path = os.path.expanduser(credentials_path or DEFAULT_CRED_PATH)

    try:
        cred = _load_credential_file(cred_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARNING: Cannot read {cred_path}: {e}", file=sys.stderr)
        return None

    entry_key, entry = _find_figma_oauth_entry(cred)
    if not entry:
        return None

    token, refreshed = _refresh_token_if_needed(cred_path, cred, entry_key, entry)
    if refreshed:
        print("INFO: Refreshed Figma MCP token from Claude credentials", file=sys.stderr)
    return token


def print_setup_guide():
    """Print onboarding when Claude CLI + MCP are missing."""
    has_claude = shutil.which("claude") is not None

    print("ERROR: No Figma MCP token found.", file=sys.stderr)
    print("", file=sys.stderr)
    print("MCP priority is highest for this skill.", file=sys.stderr)
    print("One-click setup (recommended, do this first):", file=sys.stderr)
    print("  bash scripts/setup_claude_mcp.sh", file=sys.stderr)
    print("  After browser consent, return Authentication Code (code#state)", file=sys.stderr)
    print("  or the full callback URL for diagnostics:", file=sys.stderr)
    print("  https://platform.claude.com/oauth/code/callback?code=...&state=...", file=sys.stderr)
    print("  (Replying only 'done/好了' is insufficient in remote handoff flows)", file=sys.stderr)
    print("", file=sys.stderr)
    print("Manual onboarding (if one-click is unavailable):", file=sys.stderr)

    if not has_claude:
        print("  1) Install Claude CLI:", file=sys.stderr)
        print("     npm install -g @anthropic-ai/claude-code", file=sys.stderr)
    else:
        print("  1) Claude CLI detected ✅", file=sys.stderr)

    print("  2) Login (first try):", file=sys.stderr)
    print("     claude auth login", file=sys.stderr)
    print("     If headless flow stalls: run 'claude' and finish interactive login (paste code#state)", file=sys.stderr)
    print("  3) Add Figma MCP server:", file=sys.stderr)
    print("     claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp", file=sys.stderr)
    print("  4) Complete MCP auth in Claude UI:", file=sys.stderr)
    print("     claude  # then run /mcp, select figma, Authenticate/Connect", file=sys.stderr)
    print("  5) Verify:", file=sys.stderr)
    print("     claude mcp list  # expect figma ... Connected", file=sys.stderr)
    print("", file=sys.stderr)
    print("Run this script with one of these explicit auth modes:", file=sys.stderr)
    print("  A) export FIGMA_MCP_TOKEN=<token>  (recommended explicit mode)", file=sys.stderr)
    print("  B) --allow-claude-credentials      (read ~/.claude/.credentials.json)", file=sys.stderr)
    print("", file=sys.stderr)
    print("If callback is rejected as invalid/stale, restart login and use only the newest authorize URL.", file=sys.stderr)
    print("Optional state check:", file=sys.stderr)
    print("  python3 scripts/parse_claude_oauth_callback.py --auth-url \"<latest_auth_url>\" --callback-url \"<callback_url>\"", file=sys.stderr)
    print("Fallback (without MCP): use Figma REST API with FIGMA_TOKEN + fetch_figma_rest.py", file=sys.stderr)


def mcp_call(token, method_or_tool, params=None, call_id=1):
    """Send a JSON-RPC request to Figma MCP and return parsed result."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-protocol-version": PROTOCOL_VERSION,
    }

    if "/" not in method_or_tool:
        payload = {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": "tools/call",
            "params": {"name": method_or_tool, "arguments": params or {}},
        }
    else:
        payload = {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": method_or_tool,
            "params": params or {},
        }

    data = json.dumps(payload).encode()
    req = Request(MCP_URL, data=data, headers=headers)
    try:
        with urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else str(e)
        raise RuntimeError(f"MCP HTTP {e.code}: {detail[:400]}") from e
    except URLError as e:
        raise RuntimeError(f"MCP network error: {e}") from e

    results = []
    for line in body.splitlines():
        if line.startswith("data:"):
            raw = line[5:].strip()
            if raw:
                results.append(json.loads(raw))

    if results:
        return results[0]
    return json.loads(body)


def init_session(token):
    return mcp_call(
        token,
        "initialize",
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "figma-to-static", "version": "1.1"},
        },
        call_id=0,
    )


def action_tools(token):
    resp = mcp_call(token, "tools/list", {}, call_id=2)
    tools = resp.get("result", {}).get("tools", [])
    print(f"Available Figma MCP tools ({len(tools)}):")
    for t in tools:
        desc = (t.get("description") or "")[:80]
        print(f"  {t['name']}: {desc}")
    return tools


def action_info(token, file_key):
    who = mcp_call(token, "whoami", {}, call_id=2)
    who_text = who.get("result", {}).get("content", [{}])[0].get("text", "")
    print("=== whoami ===")
    print(who_text)


def action_metadata(token, file_key, node_id, out_dir, call_id=3):
    args = {
        "fileKey": file_key,
        "nodeId": node_id,
        "clientFrameworks": "html-css",
        "clientLanguages": "html,css",
    }
    resp = mcp_call(token, "get_metadata", args, call_id=call_id)
    result = resp.get("result", {})
    content = result.get("content", [])
    text = content[0].get("text", "") if content else ""
    text = fix_encoding(text)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    safe_node = node_id.replace(":", "-")
    outfile = out / f"metadata-{safe_node}.xml"
    outfile.write_text(text, encoding="utf-8")
    print(f"Metadata saved: {outfile} ({len(text)} chars, {len(text.splitlines())} lines)")

    m = re.search(r'<frame id="([^"]+)" name="([^"]+)".*?width="([^"]+)" height="([^"]+)"', text)
    if m:
        print(f"  Frame: {m.group(2)} ({m.group(3)}×{m.group(4)})")
    return str(outfile)


def action_context(token, file_key, node_id, out_dir, call_id=4):
    args = {
        "fileKey": file_key,
        "nodeId": node_id,
    }
    resp = mcp_call(token, "get_design_context", args, call_id=call_id)
    result = resp.get("result", {})
    content = result.get("content", [])
    text = content[0].get("text", "") if content else ""
    text = fix_encoding(text)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    safe_node = node_id.replace(":", "-")
    outfile = out / f"context-{safe_node}.txt"
    outfile.write_text(text, encoding="utf-8")
    print(f"Design context saved: {outfile} ({len(text)} chars)")
    return str(outfile)


def action_screenshot(token, file_key, node_id, out_dir, call_id=5):
    args = {
        "fileKey": file_key,
        "nodeId": node_id,
    }
    resp = mcp_call(token, "get_screenshot", args, call_id=call_id)
    result = resp.get("result", {})
    content = result.get("content", [])

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    safe_node = node_id.replace(":", "-")

    saved = []
    for item in content:
        if item.get("type") == "image":
            data = item.get("data", "")
            mime = item.get("mimeType", "image/png")
            ext = "png" if "png" in mime else "jpg"
            fname = out / f"screenshot-{safe_node}.{ext}"
            fname.write_bytes(base64.b64decode(data))
            print(f"Screenshot saved: {fname} ({fname.stat().st_size} bytes)")
            saved.append(str(fname))
        elif item.get("type") == "text":
            text = fix_encoding(item.get("text", ""))
            fname = out / f"screenshot-{safe_node}-info.txt"
            fname.write_text(text, encoding="utf-8")
            saved.append(str(fname))

    if not saved:
        raw = out / f"screenshot-{safe_node}-raw.json"
        raw.write_text(json.dumps(resp, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"No image found in response. Raw saved: {raw}")
        saved.append(str(raw))

    return saved


def action_variables(token, file_key, out_dir):
    args = {"fileKey": file_key}
    resp = mcp_call(token, "get_variable_defs", args, call_id=6)
    result = resp.get("result", {})
    content = result.get("content", [])
    text = content[0].get("text", "") if content else ""
    text = fix_encoding(text)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    outfile = out / "variables.txt"
    outfile.write_text(text, encoding="utf-8")
    print(f"Variables saved: {outfile} ({len(text)} chars)")
    return str(outfile)


def parse_node_ids(node_id, node_ids):
    ids = []
    if node_id:
        ids.append(node_id)
    if node_ids:
        raw = [s.strip() for s in re.split(r"[,\s]+", node_ids) if s.strip()]
        ids.extend(raw)

    # Preserve order, dedupe
    seen = set()
    deduped = []
    for nid in ids:
        if nid not in seen:
            deduped.append(nid)
            seen.add(nid)
    return deduped


def main():
    p = argparse.ArgumentParser(description="Fetch Figma data via MCP protocol")
    p.add_argument("--file-key", help="Figma file key from URL")
    p.add_argument("--node-id", help="Single node ID (e.g. 0:6715)")
    p.add_argument("--node-ids", help="Comma/space-separated node IDs for batch mode")
    p.add_argument(
        "--action",
        choices=["metadata", "screenshot", "context", "info", "tools", "variables", "bundle"],
        default="metadata",
    )
    p.add_argument("--out-dir", default="./mcp-assets")
    p.add_argument(
        "--allow-claude-credentials",
        action="store_true",
        help="Allow reading Claude credential file for MCP token (~/.claude/.credentials.json)",
    )
    p.add_argument(
        "--credentials-path",
        default=None,
        help="Optional path to Claude credentials file (used only with --allow-claude-credentials)",
    )
    args = p.parse_args()

    token = get_token(
        allow_claude_credentials=args.allow_claude_credentials,
        credentials_path=args.credentials_path,
    )
    if not token:
        print_setup_guide()
        sys.exit(1)

    init_session(token)

    if args.action == "tools":
        action_tools(token)
        return

    if args.action == "info":
        if not args.file_key:
            p.error("--file-key required for info action")
        action_info(token, args.file_key)
        return

    if args.action == "variables":
        if not args.file_key:
            p.error("--file-key required for variables action")
        action_variables(token, args.file_key, args.out_dir)
        return

    if not args.file_key:
        p.error("--file-key required for this action")

    node_list = parse_node_ids(args.node_id, args.node_ids)
    if not node_list:
        p.error("Provide --node-id or --node-ids for this action")

    all_outputs = []
    for i, node_id in enumerate(node_list, start=1):
        print(f"\n=== Node {i}/{len(node_list)}: {node_id} ===")
        call_base = 10 + i * 10

        if args.action == "metadata":
            all_outputs.append(action_metadata(token, args.file_key, node_id, args.out_dir, call_id=call_base))
        elif args.action == "screenshot":
            all_outputs.extend(action_screenshot(token, args.file_key, node_id, args.out_dir, call_id=call_base))
        elif args.action == "context":
            all_outputs.append(action_context(token, args.file_key, node_id, args.out_dir, call_id=call_base))
        elif args.action == "bundle":
            all_outputs.append(action_metadata(token, args.file_key, node_id, args.out_dir, call_id=call_base))
            all_outputs.extend(action_screenshot(token, args.file_key, node_id, args.out_dir, call_id=call_base + 1))
            all_outputs.append(action_context(token, args.file_key, node_id, args.out_dir, call_id=call_base + 2))

    print("\nBatch complete.")
    print(f"Outputs: {len(all_outputs)} file(s)")


if __name__ == "__main__":
    main()
