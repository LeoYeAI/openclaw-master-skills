#!/usr/bin/env python3
"""
Browserbase Session Manager for OpenClaw
=========================================
A CLI tool for creating and managing persistent Browserbase cloud browser
sessions with authentication persistence via Contexts.

Usage:
    python3 browserbase_manager.py <command> [options]

Commands:
    install             Install Python deps + Playwright Chromium (best-effort)
    setup               Validate credentials and run a smoke test
    list-projects       List accessible Browserbase projects (helps find Project ID)
    create-context      Create a new persistent context
    delete-context      Delete a context
    list-contexts       List locally saved named contexts
    create-workspace    Create a named workspace (context + tab history)
    list-workspaces     List local workspaces
    get-workspace       Get workspace details
    delete-workspace    Delete a local workspace (optionally delete remote context)
    start-workspace     Create a keep-alive session for a workspace and optionally restore tabs
    resume-workspace    Reconnect to an existing workspace session or start a new one
    snapshot-workspace  Save current open tabs to workspace state
    stop-workspace      Snapshot tabs and terminate the active workspace session
    create-session      Create a new browser session
    list-sessions       List all sessions
    get-session         Get session details
    terminate-session   Terminate a running session
    navigate            Navigate to a URL in a session
    list-tabs           List open tabs in the primary browser context
    new-tab             Open a new tab (optionally navigate immediately)
    switch-tab          Switch to a specific tab by index or URL match
    close-tab           Close a tab by index or URL match
    click               Click an element on the current/selected tab
    type                Type/fill text into an element
    press               Press a key on the page or focused element
    wait-for            Wait for selector/text/url/load-state conditions
    go-back             Navigate back in history
    go-forward          Navigate forward in history
    reload              Reload the current page
    read-page           Read the current page text/html/links
    execute-js          Execute JavaScript in a session
    screenshot          Take a screenshot of the current page
    get-cookies         Get cookies from a session
    get-recording       Fetch session rrweb recording events (JSON)
    get-downloads       Download files saved during the session (archive)
    get-logs            Get session logs
    handoff             Create/check/clear a human handoff request for a session/workspace
    live-url            Get live debug URL for a session

Environment Variables:
    BROWSERBASE_API_KEY       Your Browserbase API key (required)
    BROWSERBASE_PROJECT_ID    Your Browserbase project ID (required)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Local state (named contexts + workspaces)
# ---------------------------------------------------------------------------

_WORKSPACE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")
_BROWSERBASE_API_BASE = "https://api.browserbase.com/v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_dir() -> str:
    """Return the directory used for local skill state."""
    base = os.environ.get("BROWSERBASE_CONFIG_DIR", os.path.expanduser("~/.browserbase"))
    os.makedirs(base, exist_ok=True)
    return base


def _contexts_path() -> str:
    """Return path to the local config file that stores named contexts."""
    return os.path.join(_state_dir(), "contexts.json")


def _load_contexts() -> dict[str, str]:
    """Load the name→context_id map from disk."""
    path = _contexts_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save_contexts(data: dict[str, str]) -> None:
    """Save the name→context_id map to disk."""
    path = _contexts_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _resolve_context(name_or_id: str) -> str:
    """Resolve a context name to its ID, or return the raw ID if not found."""
    contexts = _load_contexts()
    return contexts.get(name_or_id, name_or_id)


def _workspaces_dir() -> str:
    path = os.path.join(_state_dir(), "workspaces")
    os.makedirs(path, exist_ok=True)
    return path


def _handoffs_dir() -> str:
    path = os.path.join(_state_dir(), "handoffs")
    os.makedirs(path, exist_ok=True)
    return path


def _handoff_path(session_id: str) -> str:
    # Session ids are typically UUIDs; sanitize just in case.
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", session_id)
    return os.path.join(_handoffs_dir(), f"{safe}.json")


def _load_handoff_file(session_id: str) -> Optional[dict[str, Any]]:
    path = _handoff_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_handoff_file(session_id: str, data: Optional[dict[str, Any]]) -> None:
    path = _handoff_path(session_id)
    if data is None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        return
    data["updated_at"] = _utc_now_iso()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _validate_workspace_name(name: str) -> None:
    if not _WORKSPACE_NAME_RE.match(name):
        raise ValueError(
            "Invalid workspace name. Use 1-64 chars: letters, digits, '_' or '-', starting with a letter/digit."
        )


def _workspace_path(name: str) -> str:
    _validate_workspace_name(name)
    return os.path.join(_workspaces_dir(), f"{name}.json")


def _load_workspace(name: str) -> dict[str, Any]:
    path = _workspace_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Workspace '{name}' not found. Create it with: create-workspace --name {name}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_workspace(name: str, data: dict[str, Any]) -> None:
    path = _workspace_path(name)
    data["updated_at"] = _utc_now_iso()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _list_workspaces() -> list[str]:
    names: list[str] = []
    for fn in os.listdir(_workspaces_dir()):
        if not fn.endswith(".json"):
            continue
        names.append(fn[:-5])
    names.sort()
    return names


def _resolve_session_id(session_id: Optional[str], workspace: Optional[str]) -> tuple[str, Optional[dict[str, Any]]]:
    if session_id and workspace:
        raise ValueError("Provide either --session-id or --workspace, not both.")
    if workspace:
        ws = _load_workspace(workspace)
        active = ws.get("active_session_id")
        if not active:
            raise ValueError(f"Workspace '{workspace}' has no active session. Run: start-workspace --name {workspace}")
        return str(active), ws
    if session_id:
        return session_id, None
    raise ValueError("Missing session identifier. Provide --session-id or --workspace.")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_env(name: str) -> str:
    """Get a required environment variable or exit with an error."""
    value = os.environ.get(name)
    if not value:
        output_error(f"Environment variable {name} is not set. "
                     f"Set it or configure via OpenClaw's skills.entries[\"browserbase-sessions\"].env "
                     f"(and you can use skills.entries[\"browserbase-sessions\"].apiKey for BROWSERBASE_API_KEY).")
        sys.exit(1)
    return value


def output_json(data: dict[str, Any]) -> None:
    """Print JSON output to stdout."""
    print(json.dumps(data, indent=2, default=str))


def output_error(message: str) -> None:
    """Print an error as JSON to stdout."""
    output_json({"status": "error", "error": message})


def get_client():
    """Initialize and return a Browserbase client."""
    try:
        from browserbase import Browserbase
    except ImportError:
        output_error(
            f"Dependencies not installed (missing 'browserbase'). Run: python3 \"{os.path.abspath(__file__)}\" install"
        )
        sys.exit(1)

    api_key = get_env("BROWSERBASE_API_KEY")
    return Browserbase(api_key=api_key)


def get_project_id() -> str:
    """Get the Browserbase project ID."""
    return get_env("BROWSERBASE_PROJECT_ID")


def _download_api_to_file(*, url: str, output_path: str, headers: dict[str, str]) -> dict[str, Any]:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp, open(output_path, "wb") as f:
            n = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                n += len(chunk)
            return {
                "ok": True,
                "status_code": getattr(resp, "status", None),
                "content_type": resp.headers.get("Content-Type"),
                "bytes_written": n,
            }
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "status_code": getattr(e, "code", None),
            "error": f"HTTP {getattr(e, 'code', '')}: {getattr(e, 'reason', '')}".strip(),
        }
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"Network error: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Setup & Validation
# ---------------------------------------------------------------------------

def _requirements_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")


def _truncate_output(s: str, limit: int = 4000) -> str:
    if not s:
        return ""
    if len(s) <= limit:
        return s
    return s[:limit] + f"\n... [truncated, total {len(s)} chars]"


def _run_subprocess(argv: list[str]) -> tuple[bool, dict[str, Any]]:
    """Run a subprocess and return (ok, info)."""
    try:
        cp = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True, {
            "returncode": cp.returncode,
            "stdout": _truncate_output(cp.stdout),
            "stderr": _truncate_output(cp.stderr),
        }
    except FileNotFoundError as e:
        return False, {"error": f"Command not found: {argv[0]}", "detail": str(e)}
    except subprocess.CalledProcessError as e:
        return False, {
            "returncode": e.returncode,
            "stdout": _truncate_output(getattr(e, "stdout", "") or ""),
            "stderr": _truncate_output(getattr(e, "stderr", "") or ""),
        }
    except Exception as e:
        return False, {"error": str(e)}


def _install_deps(*, prefer_uv: bool = True) -> list[dict[str, Any]]:
    """Install Python deps + Playwright Chromium. Does not require Browserbase env vars."""
    steps: list[dict[str, Any]] = []

    req_path = _requirements_path()
    if not os.path.exists(req_path):
        raise FileNotFoundError(f"requirements.txt not found at {req_path}")

    # uv/pip install behavior depends on whether we're in a venv.
    # - In a venv: install into that venv.
    # - Outside a venv (e.g., Homebrew Python with PEP 668): install into the
    #   current interpreter with break-system-packages semantics so setup can
    #   complete without manual environment bootstrapping.
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    uv = shutil.which("uv") if prefer_uv else None
    if uv:
        if in_venv:
            steps.append({
                "step": "installer",
                "status": "ok",
                "message": f"Using uv at {uv} (target prefix: {sys.prefix})",
            })
            pip_argv = ["uv", "pip", "install", "--prefix", sys.prefix, "-r", req_path]
        else:
            steps.append({
                "step": "installer",
                "status": "ok",
                "message": (
                    "Using uv with --system --break-system-packages "
                    "(non-venv Python detected)"
                ),
            })
            pip_argv = ["uv", "pip", "install", "--system", "--break-system-packages", "-r", req_path]
    else:
        if in_venv:
            steps.append({"step": "installer", "status": "ok", "message": "Using pip in active virtual environment"})
            pip_argv = [sys.executable, "-m", "pip", "install", "-r", req_path]
        else:
            steps.append({
                "step": "installer",
                "status": "ok",
                "message": "Using pip with --break-system-packages (non-venv Python detected)",
            })
            pip_argv = [sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", req_path]

    ok, info = _run_subprocess(pip_argv)
    steps.append({"step": "python_deps", "status": "ok" if ok else "error", "argv": pip_argv, **info})
    if not ok:
        return steps

    pw_argv = [sys.executable, "-m", "playwright", "install", "chromium"]
    ok, info = _run_subprocess(pw_argv)
    steps.append({"step": "playwright_chromium", "status": "ok" if ok else "error", "argv": pw_argv, **info})
    return steps


def cmd_install(args: argparse.Namespace) -> None:
    """Install Python deps + Playwright Chromium."""
    try:
        steps = _install_deps(prefer_uv=not getattr(args, "no_uv", False))
    except Exception as e:
        output_json({
            "status": "error",
            "command": "install",
            "error": str(e),
        })
        sys.exit(1)

    ok = all(step.get("status") == "ok" for step in steps if step.get("step") != "installer")
    output_json({
        "status": "success" if ok else "error",
        "command": "install",
        "steps": steps,
        "message": "Dependencies installed." if ok else "Install failed. Review steps for details.",
    })
    if not ok:
        sys.exit(1)


def cmd_setup(args: argparse.Namespace) -> None:
    """Validate credentials and run a full smoke test."""
    steps = []

    # Step 1: Check env vars
    try:
        api_key = get_env("BROWSERBASE_API_KEY")
        project_id = get_env("BROWSERBASE_PROJECT_ID")
        steps.append({"step": "env_vars", "status": "ok",
                       "message": "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID are set."})
    except SystemExit:
        sys.exit(1)  # get_env already printed the error

    # Optional: install deps
    if getattr(args, "install", False):
        try:
            install_steps = _install_deps(prefer_uv=True)
            steps.extend(install_steps)
            if any(s.get("status") == "error" for s in install_steps):
                output_json({"status": "error", "command": "setup", "steps": steps})
                sys.exit(1)
        except Exception as e:
            steps.append({"step": "install", "status": "error", "message": str(e)})
            output_json({"status": "error", "command": "setup", "steps": steps})
            sys.exit(1)

    # Step 2: Check SDK import
    try:
        from browserbase import Browserbase
        steps.append({"step": "sdk_import", "status": "ok",
                       "message": "browserbase SDK imported successfully."})
    except ImportError:
        steps.append({"step": "sdk_import", "status": "error",
                       "message": f"browserbase package not installed. Run: python3 \"{os.path.abspath(__file__)}\" install"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 3: Check Playwright
    try:
        from playwright.sync_api import sync_playwright
        steps.append({"step": "playwright_import", "status": "ok",
                       "message": "playwright imported successfully."})
    except ImportError:
        steps.append({"step": "playwright_import", "status": "error",
                       "message": f"playwright not installed. Run: python3 \"{os.path.abspath(__file__)}\" install"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 4: Test API connection — list sessions
    client = Browserbase(api_key=api_key)
    try:
        list(client.sessions.list())
        steps.append({"step": "api_connection", "status": "ok",
                       "message": "Successfully connected to Browserbase API."})
    except Exception as e:
        steps.append({"step": "api_connection", "status": "error",
                       "message": f"API connection failed: {e}"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 5: Smoke test — create session, navigate, terminate
    try:
        session = client.sessions.create(
            project_id=project_id,
            # Python SDK expects snake_case keys; the API uses camelCase.
            browser_settings={
                "solve_captchas": True,
                "record_session": True,
                "log_session": True,
            },
        )
        steps.append({"step": "create_session", "status": "ok",
                       "session_id": session.id,
                       "message": "Test session created."})
    except Exception as e:
        steps.append({"step": "create_session", "status": "error",
                       "message": f"Failed to create test session: {e}"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 6: Navigate via Playwright CDP
    navigate_ok = False
    pw = None
    browser = None
    try:
        pw = sync_playwright().start()
        connect_url = session.connect_url
        if not connect_url:
            connect_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session.id}"
        browser = pw.chromium.connect_over_cdp(connect_url)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
        title = page.title()
        navigate_ok = True
        steps.append({"step": "playwright_navigate", "status": "ok",
                       "title": title,
                       "message": f"Navigated to example.com — title: '{title}'"})
    except Exception as e:
        steps.append({"step": "playwright_navigate", "status": "error",
                       "message": f"Playwright navigation failed: {e}"})
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            if pw:
                pw.stop()
        except Exception:
            pass

    # Step 7: Terminate test session
    try:
        client.sessions.update(session.id, status="REQUEST_RELEASE", project_id=project_id)
        steps.append({"step": "terminate_session", "status": "ok",
                       "message": "Test session terminated."})
    except Exception as e:
        steps.append({"step": "terminate_session", "status": "warning",
                       "message": f"Cleanup warning (non-fatal): {e}"})

    overall = "success" if navigate_ok else "partial"
    output_json({
        "status": overall,
        "command": "setup",
        "steps": steps,
        "message": "All checks passed. Skill is ready to use." if overall == "success"
                   else "Setup completed with warnings. Review steps above."
    })


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def cmd_list_projects(args: argparse.Namespace) -> None:
    """List Browserbase projects visible to the API key (useful if Project ID is unknown)."""
    client = get_client()

    try:
        projects = list(client.projects.list())
        out = []
        for p in projects:
            out.append({
                "project_id": getattr(p, "id", None),
                "name": getattr(p, "name", None),
                "created_at": str(getattr(p, "created_at", "")),
            })
        output_json({
            "status": "success",
            "command": "list-projects",
            "count": len(out),
            "projects": out,
            "message": "Projects listed. Set BROWSERBASE_PROJECT_ID to one of the project_id values above.",
        })
    except Exception as e:
        output_error(f"Failed to list projects: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Context Management
# ---------------------------------------------------------------------------

def cmd_create_context(args: argparse.Namespace) -> None:
    """Create a new persistent context for storing authentication state."""
    client = get_client()
    project_id = get_project_id()

    try:
        context = client.contexts.create(project_id=project_id)

        # If a name was provided, save it locally
        if args.name:
            contexts = _load_contexts()
            contexts[args.name] = context.id
            _save_contexts(contexts)

        result: dict[str, Any] = {
            "status": "success",
            "command": "create-context",
            "context_id": context.id,
            "project_id": project_id,
            "message": "Context created. Use this context_id (or its name) when creating "
                       "sessions to persist authentication state (cookies, local storage)."
        }
        if args.name:
            result["name"] = args.name
        output_json(result)
    except Exception as e:
        output_error(f"Failed to create context: {e}")
        sys.exit(1)


def cmd_delete_context(args: argparse.Namespace) -> None:
    """Delete a persistent context. This is permanent and irreversible."""
    import urllib.request
    import urllib.error

    context_id = _resolve_context(args.context_id)
    try:
        _delete_context_remote(context_id)
        _remove_named_context(context_id)
        output_json({
            "status": "success",
            "command": "delete-context",
            "context_id": context_id,
            "message": "Context deleted permanently."
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        output_error(f"Failed to delete context (HTTP {e.code}): {body}")
        sys.exit(1)
    except Exception as e:
        output_error(f"Failed to delete context: {e}")
        sys.exit(1)


def _delete_context_remote(context_id: str) -> None:
    import urllib.request
    import urllib.error

    api_key = get_env("BROWSERBASE_API_KEY")
    url = f"https://api.browserbase.com/v1/contexts/{context_id}"

    req = urllib.request.Request(url, method="DELETE", headers={
        "X-BB-API-Key": api_key,
    })

    # Raises urllib.error.HTTPError on non-2xx.
    with urllib.request.urlopen(req):
        return


def cmd_list_contexts(args: argparse.Namespace) -> None:
    """List all locally saved named contexts."""
    contexts = _load_contexts()
    output_json({
        "status": "success",
        "command": "list-contexts",
        "count": len(contexts),
        "contexts": [{"name": k, "context_id": v} for k, v in contexts.items()],
    })


def _remove_named_context(context_id: str) -> None:
    """Remove a context_id from the named contexts file."""
    contexts = _load_contexts()
    to_remove = [k for k, v in contexts.items() if v == context_id]
    if to_remove:
        for k in to_remove:
            del contexts[k]
        _save_contexts(contexts)


# ---------------------------------------------------------------------------
# Session Lifecycle
# ---------------------------------------------------------------------------

def cmd_create_session(args: argparse.Namespace) -> None:
    """Create a new Browserbase browser session."""
    client = get_client()
    project_id = get_project_id()

    # Resolve context name → ID if needed
    context_id = _resolve_context(args.context_id) if args.context_id else None

    # Build browser settings (Python SDK expects snake_case keys).
    # Captcha solving + recording are ON by default on Browserbase; be explicit so
    # flags like --no-record actually take effect.
    browser_settings: dict[str, Any] = {
        "solve_captchas": not args.no_solve_captchas,
        "record_session": not args.no_record,
        "log_session": not getattr(args, "no_logs", False),
    }

    if context_id:
        browser_settings["context"] = {
            "id": context_id,
            "persist": args.persist,
        }

    if args.block_ads:
        browser_settings["block_ads"] = True

    if args.viewport_width and args.viewport_height:
        browser_settings["viewport"] = {
            "width": args.viewport_width,
            "height": args.viewport_height,
        }

    # Build session params
    session_params: dict[str, Any] = {
        "project_id": project_id,
        "browser_settings": browser_settings,
    }

    if args.keep_alive:
        session_params["keep_alive"] = True

    if args.timeout:
        session_params["timeout"] = max(60, min(21600, args.timeout))

    if args.proxy:
        session_params["proxies"] = True

    if args.region:
        session_params["region"] = args.region

    try:
        session = client.sessions.create(**session_params)
        live_urls = _get_live_urls_safe(client, session.id)

        result: dict[str, Any] = {
            "status": "success",
            "command": "create-session",
            "session_id": session.id,
            "connect_url": session.connect_url,
            "session_status": getattr(session, "status", "RUNNING"),
            "created_at": str(getattr(session, "created_at", "")),
            "expires_at": str(getattr(session, "expires_at", "")),
            "keep_alive": args.keep_alive,
            "region": getattr(session, "region", args.region or "us-west-2"),
            "captcha_solving": not args.no_solve_captchas,
            "recording": not args.no_record,
            "logging": not getattr(args, "no_logs", False),
        }
        _attach_human_handoff(result, live_urls, session_id=session.id)

        if context_id:
            result["context_id"] = context_id
            result["persist"] = args.persist

        if hasattr(session, "selenium_remote_url") and session.selenium_remote_url:
            result["selenium_remote_url"] = session.selenium_remote_url
            result["signing_key"] = getattr(session, "signing_key", None)

        result["message"] = (
            "Session created with captcha solving"
            + (" and recording" if not args.no_record else "")
            + (" and logging" if not getattr(args, "no_logs", False) else "")
            + " enabled. Use connect_url with Playwright's "
            "connect_over_cdp() or the navigate/execute-js commands. "
            "Share human_handoff.share_url (or human_control_url) with the user for remote control. "
            "You have 5 minutes to connect before the session auto-terminates."
        )

        output_json(result)
    except Exception as e:
        output_error(f"Failed to create session: {e}")
        sys.exit(1)


def cmd_list_sessions(args: argparse.Namespace) -> None:
    """List all sessions."""
    client = get_client()

    try:
        sessions = client.sessions.list()
        session_list = []

        for s in sessions:
            entry = {
                "session_id": s.id,
                "status": getattr(s, "status", "unknown"),
                "created_at": str(getattr(s, "created_at", "")),
                "region": getattr(s, "region", ""),
                "keep_alive": getattr(s, "keep_alive", False),
                "context_id": getattr(s, "context_id", None),
            }

            if args.status and str(getattr(s, "status", "")).upper() != args.status.upper():
                continue

            session_list.append(entry)

        output_json({
            "status": "success",
            "command": "list-sessions",
            "count": len(session_list),
            "sessions": session_list,
        })
    except Exception as e:
        output_error(f"Failed to list sessions: {e}")
        sys.exit(1)


def cmd_get_session(args: argparse.Namespace) -> None:
    """Get details for a specific session."""
    client = get_client()

    try:
        session_id, _ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
        s = client.sessions.retrieve(session_id)
        result = {
            "status": "success",
            "command": "get-session",
            "session_id": s.id,
            "session_status": getattr(s, "status", "unknown"),
            "created_at": str(getattr(s, "created_at", "")),
            "started_at": str(getattr(s, "started_at", "")),
            "ended_at": str(getattr(s, "ended_at", "")),
            "expires_at": str(getattr(s, "expires_at", "")),
            "region": getattr(s, "region", ""),
            "keep_alive": getattr(s, "keep_alive", False),
            "context_id": getattr(s, "context_id", None),
            "avg_cpu_usage": getattr(s, "avg_cpu_usage", None),
            "memory_usage": getattr(s, "memory_usage", None),
            "proxy_bytes": getattr(s, "proxy_bytes", None),
        }
        if getattr(args, "workspace", None) and _ws is not None:
            result["workspace"] = str(args.workspace)
            result["pending_handoff"] = _ws.get("pending_handoff")
        else:
            result["pending_handoff"] = _load_handoff_file(str(s.id))
        output_json(result)
    except Exception as e:
        output_error(f"Failed to get session: {e}")
        sys.exit(1)


def cmd_terminate_session(args: argparse.Namespace) -> None:
    """Terminate a running session."""
    client = get_client()
    project_id = get_project_id()

    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
        if ws is not None and getattr(args, "workspace", None):
            # Prefer the workspace stop path so we persist tab state + auth.
            info = _stop_workspace_session_internal(
                client=client, project_id=project_id, workspace_name=str(args.workspace), ws=ws
            )
            output_json({
                "status": "success",
                "command": "terminate-session",
                "workspace": str(args.workspace),
                "session_id": session_id,
                **info,
                "message": (
                    "Workspace session termination requested. Tabs were snapshotted (best-effort) and "
                    "auth state will be saved back to the context. Wait a few seconds before starting "
                    "a new session with the same workspace/context."
                ),
            })
            return

        client.sessions.update(
            session_id,
            status="REQUEST_RELEASE",
            project_id=project_id,
        )

        output_json({
            "status": "success",
            "command": "terminate-session",
            "session_id": session_id,
            "message": "Session termination requested. If using a context with "
                       "persist=true, wait a few seconds for context sync before "
                       "creating a new session with the same context."
        })
    except Exception as e:
        output_error(f"Failed to terminate session: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Workspaces (context + last session + tab state)
# ---------------------------------------------------------------------------

def cmd_create_workspace(args: argparse.Namespace) -> None:
    """Create a local workspace backed by a Browserbase Context."""
    client = get_client()
    project_id = get_project_id()

    try:
        _validate_workspace_name(args.name)
    except ValueError as e:
        output_error(str(e))
        sys.exit(1)

    path = _workspace_path(args.name)
    if os.path.exists(path) and not args.force:
        output_error(
            f"Workspace '{args.name}' already exists. Use --force to overwrite or pick a different name."
        )
        sys.exit(1)

    try:
        if args.context_id:
            context_id = _resolve_context(args.context_id)
        else:
            ctx = client.contexts.create(project_id=project_id)
            context_id = ctx.id

        now = _utc_now_iso()
        ws: dict[str, Any] = {
            "name": args.name,
            "context_id": context_id,
            "active_session_id": None,
            "tabs": [],
            "tabs_captured_at": None,
            "history": [],
            "created_at": now,
            "updated_at": now,
        }
        _save_workspace(args.name, ws)

        # Also save it as a named context for backward-compatible flows.
        contexts = _load_contexts()
        contexts.setdefault(args.name, context_id)
        _save_contexts(contexts)

        output_json({
            "status": "success",
            "command": "create-workspace",
            "workspace": args.name,
            "workspace_path": path,
            "context_id": context_id,
            "message": (
                "Workspace created. Use start-workspace to open a keep-alive browser that "
                "persists login (cookies/storage) via the context, and snapshot-workspace/stop-workspace "
                "to save and restore tab state."
            ),
        })
    except Exception as e:
        output_error(f"Failed to create workspace: {e}")
        sys.exit(1)


def cmd_list_workspaces(args: argparse.Namespace) -> None:
    """List local workspaces."""
    workspaces = []
    for name in _list_workspaces():
        try:
            ws = _load_workspace(name)
            workspaces.append({
                "name": name,
                "context_id": ws.get("context_id"),
                "active_session_id": ws.get("active_session_id"),
                "tabs_count": len(ws.get("tabs") or []),
                "updated_at": ws.get("updated_at"),
            })
        except Exception:
            workspaces.append({"name": name, "error": "Failed to read workspace file."})

    output_json({
        "status": "success",
        "command": "list-workspaces",
        "count": len(workspaces),
        "workspaces": workspaces,
    })


def cmd_get_workspace(args: argparse.Namespace) -> None:
    """Get workspace details."""
    try:
        ws = _load_workspace(args.name)
        output_json({
            "status": "success",
            "command": "get-workspace",
            "workspace": args.name,
            "workspace_path": _workspace_path(args.name),
            "data": ws,
        })
    except Exception as e:
        output_error(f"Failed to get workspace: {e}")
        sys.exit(1)


def cmd_delete_workspace(args: argparse.Namespace) -> None:
    """Delete a local workspace; optionally delete the remote context."""
    try:
        ws = _load_workspace(args.name)
    except Exception as e:
        output_error(f"Failed to load workspace: {e}")
        sys.exit(1)

    context_id = ws.get("context_id")
    active_session_id = ws.get("active_session_id")

    # Optionally delete the remote context (destructive).
    if args.delete_context:
        if active_session_id:
            output_error(
                f"Workspace '{args.name}' still has an active session ({active_session_id}). "
                "Stop it first: stop-workspace --name "
                f"{args.name}"
            )
            sys.exit(1)
        if context_id:
            try:
                _delete_context_remote(str(context_id))
                _remove_named_context(str(context_id))
            except Exception as e:
                output_error(f"Failed to delete remote context {context_id}: {e}")
                sys.exit(1)

    # Delete local file.
    try:
        os.remove(_workspace_path(args.name))
    except Exception as e:
        output_error(f"Failed to delete workspace file: {e}")
        sys.exit(1)

    output_json({
        "status": "success",
        "command": "delete-workspace",
        "workspace": args.name,
        "deleted_remote_context": bool(args.delete_context),
        "context_id": context_id,
        "message": "Workspace deleted.",
    })


def _create_session_internal(
    *,
    client,
    project_id: str,
    context_id: Optional[str] = None,
    persist: bool = True,
    keep_alive: bool = False,
    timeout_s: Optional[int] = None,
    region: Optional[str] = None,
    proxy: bool = False,
    block_ads: bool = False,
    record: bool = True,
    log: bool = True,
    solve_captchas: bool = True,
    viewport_width: Optional[int] = None,
    viewport_height: Optional[int] = None,
):
    browser_settings: dict[str, Any] = {
        "solve_captchas": solve_captchas,
        "record_session": record,
        "log_session": log,
    }

    if context_id:
        browser_settings["context"] = {
            "id": context_id,
            "persist": persist,
        }

    if block_ads:
        browser_settings["block_ads"] = True

    if viewport_width and viewport_height:
        browser_settings["viewport"] = {"width": viewport_width, "height": viewport_height}

    session_params: dict[str, Any] = {
        "project_id": project_id,
        "browser_settings": browser_settings,
    }

    if keep_alive:
        session_params["keep_alive"] = True

    if timeout_s:
        session_params["timeout"] = max(60, min(21600, timeout_s))

    if proxy:
        session_params["proxies"] = True

    if region:
        session_params["region"] = region

    return client.sessions.create(**session_params)


def _live_urls_to_dict(live_urls: Any) -> dict[str, Any]:
    pages_out = []
    for p in getattr(live_urls, "pages", []) or []:
        pages_out.append({
            "id": getattr(p, "id", None),
            "url": getattr(p, "url", None),
            "title": getattr(p, "title", None),
            "debugger_url": getattr(p, "debugger_url", None),
            "debugger_fullscreen_url": getattr(p, "debugger_fullscreen_url", None),
            "favicon_url": getattr(p, "favicon_url", None),
        })
    return {
        "debugger_url": getattr(live_urls, "debugger_url", None),
        "debugger_fullscreen_url": getattr(live_urls, "debugger_fullscreen_url", None),
        "ws_url": getattr(live_urls, "ws_url", None),
        "pages": pages_out,
    }


def _get_live_urls_safe(client, session_id: str) -> Optional[dict[str, Any]]:
    try:
        return _live_urls_to_dict(client.sessions.debug(session_id))
    except Exception:
        return None


def _attach_human_handoff(
    result: dict[str, Any],
    live_urls: Optional[dict[str, Any]],
    *,
    workspace: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    debugger_url = live_urls.get("debugger_url") if isinstance(live_urls, dict) else None
    fullscreen_url = live_urls.get("debugger_fullscreen_url") if isinstance(live_urls, dict) else None
    context_label = f"workspace '{workspace}'" if workspace else (f"session {session_id}" if session_id else "browser")

    result["live_urls"] = live_urls
    result["human_control_url"] = debugger_url
    result["human_control_fullscreen_url"] = fullscreen_url
    result["human_handoff"] = {
        "status": "ready" if debugger_url else "unavailable",
        "share_url": debugger_url,
        "share_fullscreen_url": fullscreen_url,
        "share_text": (
            f"I opened {context_label}. Take remote control here: {debugger_url}"
            if debugger_url
            else None
        ),
        "share_markdown": (
            f"I opened {context_label}. Take remote control here: [Open Browser]({debugger_url})"
            if debugger_url
            else None
        ),
        "share_text_fullscreen": (
            f"I opened {context_label}. Take remote control (fullscreen) here: {fullscreen_url}"
            if fullscreen_url
            else None
        ),
        "share_markdown_fullscreen": (
            f"I opened {context_label}. Take remote control (fullscreen) here: [Open Browser (Fullscreen)]({fullscreen_url})"
            if fullscreen_url
            else None
        ),
        "note": (
            "Send share_url to the user so they can take control in Browserbase Live Debugger."
            if debugger_url
            else "Live debugger URL unavailable right now. Retry with the live-url command."
        ),
    }


def _collect_tabs_from_browser(browser: Any) -> list[dict[str, Any]]:
    tabs: list[dict[str, Any]] = []

    for ctx in getattr(browser, "contexts", []) or []:
        for p in getattr(ctx, "pages", []) or []:
            url = getattr(p, "url", None)
            if not url:
                continue
            if url.startswith(("chrome-extension://", "devtools://")):
                continue
            try:
                title = p.title()
            except Exception:
                title = None
            tabs.append({"url": url, "title": title})
    return tabs


def _restore_tabs_in_browser(browser: Any, tabs: list[dict[str, Any]], max_tabs: int) -> int:
    urls: list[str] = []
    for t in tabs:
        url = (t or {}).get("url")
        if not url:
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        urls.append(url)

    if not urls:
        return 0
    if max_tabs > 0:
        urls = urls[:max_tabs]

    contexts = getattr(browser, "contexts", []) or []
    context = contexts[0] if contexts else browser.new_context()
    pages = getattr(context, "pages", []) or []
    first_page = pages[0] if pages else context.new_page()

    restored = 0
    for i, url in enumerate(urls):
        page = first_page if i == 0 else context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            restored += 1
        except Exception:
            # If a URL fails to load (auth wall, blocked, etc.), keep going.
            continue
    return restored


def _append_ws_history(ws: dict[str, Any], entry: dict[str, Any], cap: int = 2000) -> None:
    history = ws.get("history")
    if not isinstance(history, list):
        history = []
    history.append(entry)
    if len(history) > cap:
        history = history[-cap:]
    ws["history"] = history


def _get_pending_handoff(
    *,
    session_id: Optional[str],
    ws: Optional[dict[str, Any]],
    workspace_name: Optional[str],
) -> Optional[dict[str, Any]]:
    if workspace_name and ws is not None:
        return ws.get("pending_handoff")
    if session_id:
        return _load_handoff_file(session_id)
    return None


def _set_pending_handoff(
    *,
    session_id: Optional[str],
    ws: Optional[dict[str, Any]],
    workspace_name: Optional[str],
    handoff: Optional[dict[str, Any]],
    history_type: Optional[str] = None,
) -> None:
    if workspace_name and ws is not None:
        if handoff is None:
            ws.pop("pending_handoff", None)
        else:
            ws["pending_handoff"] = handoff
        if history_type:
            _append_ws_history(ws, {"ts": _utc_now_iso(), "type": history_type, "session_id": session_id})
        _save_workspace(workspace_name, ws)
        return
    if session_id:
        _save_handoff_file(session_id, handoff)


def cmd_start_workspace(args: argparse.Namespace) -> None:
    """Start a workspace session (keep-alive by default) and optionally restore tabs."""
    client = get_client()
    project_id = get_project_id()

    try:
        ws = _load_workspace(args.name)
    except Exception as e:
        output_error(f"Failed to load workspace: {e}")
        sys.exit(1)

    context_id = ws.get("context_id")
    if not context_id:
        output_error(f"Workspace '{args.name}' is missing context_id.")
        sys.exit(1)

    # If there's an active session, either reuse it or stop it first.
    prev_stop_info = None
    active = ws.get("active_session_id")
    if active:
        if args.force_new:
            try:
                prev_stop_info = _stop_workspace_session_internal(
                    client=client, project_id=project_id, workspace_name=args.name, ws=ws
                )
            except Exception:
                # If we can't stop it, continue anyway (but the old session may still be running).
                prev_stop_info = {"warning": "Failed to stop previous session; starting a new one anyway."}
        else:
            # If it's still running, don't create a new one.
            try:
                s = client.sessions.retrieve(str(active))
                status = str(getattr(s, "status", "")).upper()
                if status == "RUNNING":
                    live_urls = _get_live_urls_safe(client, str(active))
                    result: dict[str, Any] = {
                        "status": "success",
                        "command": "start-workspace",
                        "workspace": args.name,
                        "session_id": str(active),
                        "session_status": status,
                        "connect_url": getattr(s, "connect_url", None),
                        "pending_handoff": ws.get("pending_handoff"),
                        "message": (
                            "Workspace already has a running session. Reconnected. "
                            "Share human_handoff.share_url with the user for remote control."
                        ),
                    }
                    _attach_human_handoff(result, live_urls, workspace=args.name, session_id=str(active))
                    output_json(result)
                    return
            except Exception:
                pass
            # Clear stale session id and continue.
            ws["active_session_id"] = None
            _save_workspace(args.name, ws)

    try:
        session = _create_session_internal(
            client=client,
            project_id=project_id,
            context_id=str(context_id),
            persist=True,
            keep_alive=not args.no_keep_alive,
            timeout_s=args.timeout,
            region=args.region,
            proxy=args.proxy,
            block_ads=args.block_ads,
            record=not args.no_record,
            log=not getattr(args, "no_logs", False),
            solve_captchas=not args.no_solve_captchas,
            viewport_width=args.viewport_width,
            viewport_height=args.viewport_height,
        )
    except Exception as e:
        output_error(f"Failed to start workspace session: {e}")
        sys.exit(1)

    ws["active_session_id"] = session.id
    ws["last_started_at"] = _utc_now_iso()
    _save_workspace(args.name, ws)

    # Ensure we connect at least once. Browserbase sessions have a "connect within 5 minutes"
    # requirement; a warm Playwright CDP connect prevents early auto-termination.
    restored_tabs = 0
    playwright_error = None
    tabs_snapshot: Optional[list[dict[str, Any]]] = None
    try:
        pw, browser, _page = _connect_playwright(session.id)
        try:
            if args.restore_tabs and (ws.get("tabs") or []):
                restored_tabs = _restore_tabs_in_browser(browser, ws.get("tabs") or [], args.max_tabs)
            tabs_snapshot = _collect_tabs_from_browser(browser)
        finally:
            try:
                browser.close()
            except Exception:
                pass
            try:
                pw.stop()
            except Exception:
                pass
    except Exception as e:
        playwright_error = str(e)

    if tabs_snapshot is not None:
        ws["tabs"] = tabs_snapshot
        ws["tabs_captured_at"] = _utc_now_iso()
        _append_ws_history(ws, {
            "ts": _utc_now_iso(),
            "type": "start",
            "session_id": session.id,
            "restored_tabs": restored_tabs,
        })
        _save_workspace(args.name, ws)

    live_urls = _get_live_urls_safe(client, session.id)

    result: dict[str, Any] = {
        "status": "success",
        "command": "start-workspace",
        "workspace": args.name,
        "context_id": str(context_id),
        "session_id": session.id,
        "connect_url": getattr(session, "connect_url", None),
        "session_status": getattr(session, "status", "RUNNING"),
        "keep_alive": not args.no_keep_alive,
        "timeout": args.timeout,
        "captcha_solving": not args.no_solve_captchas,
        "recording": not args.no_record,
        "logging": not getattr(args, "no_logs", False),
        "pending_handoff": ws.get("pending_handoff"),
        "restored_tabs": restored_tabs,
        "tabs_snapshot_count": len(tabs_snapshot) if tabs_snapshot is not None else None,
        "playwright_error": playwright_error,
        "previous_session": prev_stop_info,
        "message": (
            "Workspace session started. Share human_handoff.share_url (or human_control_url) with the user, "
            "then use live_urls.debugger_url to open the browser while chatting, "
            "and use snapshot-workspace/stop-workspace to persist tabs + login between sessions."
        ),
    }
    _attach_human_handoff(result, live_urls, workspace=args.name, session_id=session.id)
    output_json(result)


def cmd_resume_workspace(args: argparse.Namespace) -> None:
    """Reconnect to an existing workspace session, or start a new one if needed."""
    client = get_client()

    if getattr(args, "force_new", False):
        cmd_start_workspace(args)
        return

    try:
        ws = _load_workspace(args.name)
    except Exception as e:
        output_error(f"Failed to load workspace: {e}")
        sys.exit(1)

    active = ws.get("active_session_id")
    if active:
        try:
            s = client.sessions.retrieve(str(active))
            status = str(getattr(s, "status", "")).upper()
            if status == "RUNNING":
                live_urls = None
                live_urls = _get_live_urls_safe(client, str(active))

                result: dict[str, Any] = {
                    "status": "success",
                    "command": "resume-workspace",
                    "workspace": args.name,
                    "session_id": str(active),
                    "session_status": status,
                    "connect_url": getattr(s, "connect_url", None),
                    "pending_handoff": ws.get("pending_handoff"),
                    "message": "Workspace session is still running. Reconnected. Share human_handoff.share_url with the user for remote control.",
                }
                _attach_human_handoff(result, live_urls, workspace=args.name, session_id=str(active))
                output_json(result)
                return
        except Exception:
            # If we can't retrieve it, we'll start fresh.
            pass

        # Clear stale session id.
        ws["active_session_id"] = None
        _save_workspace(args.name, ws)

    # Start a new session using the same args.
    cmd_start_workspace(args)


def cmd_snapshot_workspace(args: argparse.Namespace) -> None:
    """Save current open tabs to workspace state (used to restore later)."""
    client = get_client()

    try:
        ws = _load_workspace(args.name)
    except Exception as e:
        output_error(f"Failed to load workspace: {e}")
        sys.exit(1)

    session_id = args.session_id or ws.get("active_session_id")
    if not session_id:
        output_error(f"Workspace '{args.name}' has no active session. Start it first: start-workspace --name {args.name}")
        sys.exit(1)

    tabs = []
    try:
        pw, browser, _page = _connect_playwright(str(session_id))
        try:
            tabs = _collect_tabs_from_browser(browser)
        finally:
            try:
                browser.close()
            except Exception:
                pass
            try:
                pw.stop()
            except Exception:
                pass
    except Exception as e:
        output_error(f"Failed to snapshot workspace tabs: {e}")
        sys.exit(1)

    ws["tabs"] = tabs
    ws["tabs_captured_at"] = _utc_now_iso()
    _append_ws_history(ws, {
        "ts": _utc_now_iso(),
        "type": "snapshot",
        "session_id": str(session_id),
        "tabs_count": len(tabs),
    })
    _save_workspace(args.name, ws)

    output_json({
        "status": "success",
        "command": "snapshot-workspace",
        "workspace": args.name,
        "session_id": str(session_id),
        "tabs_count": len(tabs),
        "tabs": tabs,
        "message": "Workspace tabs saved.",
    })


def _stop_workspace_session_internal(*, client, project_id: str, workspace_name: str, ws: dict[str, Any]) -> dict[str, Any]:
    session_id = ws.get("active_session_id")
    if not session_id:
        return {"message": "Workspace has no active session."}

    snapshot_warning = None
    tabs_count = None
    try:
        pw, browser, _page = _connect_playwright(str(session_id))
        try:
            tabs = _collect_tabs_from_browser(browser)
        finally:
            try:
                browser.close()
            except Exception:
                pass
            try:
                pw.stop()
            except Exception:
                pass

        ws["tabs"] = tabs
        ws["tabs_captured_at"] = _utc_now_iso()
        tabs_count = len(tabs)
        _append_ws_history(ws, {
            "ts": _utc_now_iso(),
            "type": "snapshot",
            "session_id": str(session_id),
            "tabs_count": tabs_count,
        })
        _save_workspace(workspace_name, ws)
    except Exception:
        snapshot_warning = "Snapshot failed; continuing to terminate session."

    client.sessions.update(
        str(session_id),
        status="REQUEST_RELEASE",
        project_id=project_id,
    )

    ws["active_session_id"] = None
    ws["last_stopped_at"] = _utc_now_iso()
    _append_ws_history(ws, {
        "ts": _utc_now_iso(),
        "type": "stop",
        "session_id": str(session_id),
    })
    _save_workspace(workspace_name, ws)

    return {
        "terminated_session_id": str(session_id),
        "snapshot_warning": snapshot_warning,
        "tabs_count": tabs_count,
    }


def cmd_stop_workspace(args: argparse.Namespace) -> None:
    """Snapshot tabs and terminate the active workspace session."""
    client = get_client()
    project_id = get_project_id()

    try:
        ws = _load_workspace(args.name)
    except Exception as e:
        output_error(f"Failed to load workspace: {e}")
        sys.exit(1)

    try:
        info = _stop_workspace_session_internal(
            client=client, project_id=project_id, workspace_name=args.name, ws=ws
        )
        output_json({
            "status": "success",
            "command": "stop-workspace",
            "workspace": args.name,
            **info,
            "message": (
                "Workspace session termination requested. Because workspace sessions use persist=true, "
                "auth state will be saved back to the context. Wait a few seconds before starting a new session."
            ) if info.get("terminated_session_id") else info.get("message", ""),
        })
    except Exception as e:
        output_error(f"Failed to stop workspace session: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Browser Automation (via Playwright CDP)
# ---------------------------------------------------------------------------

def _connect_playwright(session_id: str):
    """Connect to a session via Playwright CDP and return (playwright, browser, page)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        output_error(
            f"Dependencies not installed (missing 'playwright'). Run: python3 \"{os.path.abspath(__file__)}\" install"
        )
        sys.exit(1)

    client = get_client()

    try:
        session = client.sessions.retrieve(session_id)
    except Exception as e:
        output_error(f"Failed to retrieve session {session_id}: {e}")
        sys.exit(1)

    connect_url = getattr(session, "connect_url", None)
    if not connect_url:
        api_key = get_env("BROWSERBASE_API_KEY")
        connect_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(connect_url)
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
            pages = context.pages
            page = pages[0] if pages else context.new_page()
        else:
            context = browser.new_context()
            page = context.new_page()
        return pw, browser, page
    except Exception as e:
        pw.stop()
        output_error(f"Failed to connect to session via CDP: {e}")
        sys.exit(1)


def _primary_context(browser: Any) -> Any:
    contexts = list(getattr(browser, "contexts", []) or [])
    return contexts[0] if contexts else browser.new_context()


def _primary_pages(context: Any, *, create_if_empty: bool = True) -> list[Any]:
    pages = list(getattr(context, "pages", []) or [])
    if not pages and create_if_empty:
        pages = [context.new_page()]
    return pages


def _list_tabs_in_context(context: Any) -> list[dict[str, Any]]:
    tabs: list[dict[str, Any]] = []
    pages = _primary_pages(context, create_if_empty=True)
    for i, page in enumerate(pages):
        url = getattr(page, "url", "") or ""
        if url.startswith(("chrome-extension://", "devtools://")):
            continue
        try:
            title = page.title()
        except Exception:
            title = None
        tabs.append({
            "tab_index": i,
            "url": url,
            "title": title,
        })
    return tabs


def _select_page(
    browser: Any,
    *,
    tab_index: Optional[int] = None,
    tab_url_contains: Optional[str] = None,
) -> tuple[Any, list[Any], Any, int]:
    if tab_index is not None and tab_url_contains:
        raise ValueError("Provide either --tab-index or --tab-url-contains, not both.")

    context = _primary_context(browser)
    pages = _primary_pages(context, create_if_empty=True)

    selected_index = 0
    if tab_index is not None:
        if tab_index < 0 or tab_index >= len(pages):
            raise ValueError(
                f"Tab index {tab_index} is out of range. Open tabs: 0..{max(0, len(pages) - 1)}"
            )
        selected_index = tab_index
    elif tab_url_contains:
        needle = tab_url_contains.lower()
        match_index = None
        for i, page in enumerate(pages):
            if needle in ((getattr(page, "url", "") or "").lower()):
                match_index = i
                break
        if match_index is None:
            raise ValueError(f"No tab found with URL containing: {tab_url_contains}")
        selected_index = match_index

    page = pages[selected_index]
    try:
        page.bring_to_front()
    except Exception:
        pass
    return context, pages, page, selected_index


def _sync_workspace_from_browser(
    *,
    workspace_name: Optional[str],
    ws: Optional[dict[str, Any]],
    browser: Any,
    session_id: str,
    history_entry: dict[str, Any],
    result: dict[str, Any],
) -> None:
    if not workspace_name or ws is None:
        return
    try:
        tabs = _collect_tabs_from_browser(browser)
        ws["tabs"] = tabs
        ws["tabs_captured_at"] = _utc_now_iso()
        entry = {"ts": _utc_now_iso(), "session_id": session_id, **history_entry}
        _append_ws_history(ws, entry)
        _save_workspace(workspace_name, ws)
        result["workspace_tabs_count"] = len(tabs)
    except Exception as e:
        result["workspace_update_error"] = str(e)


def _resolve_session_workspace(args: argparse.Namespace) -> tuple[str, Optional[dict[str, Any]], Optional[str]]:
    session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    workspace_name = str(args.workspace) if getattr(args, "workspace", None) else None
    return session_id, ws, workspace_name


def cmd_navigate(args: argparse.Namespace) -> None:
    """Navigate to a URL in a browser session."""
    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, page = _connect_playwright(session_id)

    try:
        response = page.goto(args.url, wait_until="domcontentloaded", timeout=30000)

        result: dict[str, Any] = {
            "status": "success",
            "command": "navigate",
            "session_id": session_id,
            "url": args.url,
            "final_url": page.url,
            "title": page.title(),
            "http_status": response.status if response else None,
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)

        if args.extract_text:
            text = page.evaluate("""
                () => {
                    const body = document.body;
                    if (!body) return '';
                    const clone = body.cloneNode(true);
                    clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                    return clone.innerText || clone.textContent || '';
                }
            """)
            max_len = 50000
            if len(text) > max_len:
                text = text[:max_len] + f"\n\n... [truncated, total {len(text)} chars]"
            result["text_content"] = text

        if args.screenshot:
            full = getattr(args, "full_page", False)
            page.screenshot(path=args.screenshot, full_page=full)
            result["screenshot_path"] = args.screenshot

        # If using a workspace, keep local tab state + history in sync.
        if ws is not None and getattr(args, "workspace", None):
            try:
                tabs = _collect_tabs_from_browser(browser)
                ws["tabs"] = tabs
                ws["tabs_captured_at"] = _utc_now_iso()
                _append_ws_history(ws, {
                    "ts": _utc_now_iso(),
                    "type": "navigate",
                    "session_id": session_id,
                    "url": args.url,
                    "final_url": page.url,
                    "title": page.title(),
                    "http_status": response.status if response else None,
                })
                _save_workspace(str(args.workspace), ws)
                result["workspace_tabs_count"] = len(tabs)
            except Exception as e:
                result["workspace_update_error"] = str(e)

        output_json(result)
    except Exception as e:
        output_error(f"Navigation failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_list_tabs(args: argparse.Namespace) -> None:
    """List open tabs in the primary browser context."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        context = _primary_context(browser)
        tabs = _list_tabs_in_context(context)
        result: dict[str, Any] = {
            "status": "success",
            "command": "list-tabs",
            "session_id": session_id,
            "tabs_count": len(tabs),
            "tabs": tabs,
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={"type": "list-tabs", "tabs_count": len(tabs)},
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Failed to list tabs: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_new_tab(args: argparse.Namespace) -> None:
    """Open a new tab and optionally navigate."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        context = _primary_context(browser)
        page = context.new_page()
        if args.url:
            response = page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)
            http_status = response.status if response else None
        else:
            http_status = None
        try:
            page.bring_to_front()
        except Exception:
            pass
        pages = _primary_pages(context, create_if_empty=True)
        tab_index = next((i for i, p in enumerate(pages) if p == page), len(pages) - 1)
        result: dict[str, Any] = {
            "status": "success",
            "command": "new-tab",
            "session_id": session_id,
            "tab_index": tab_index,
            "url": page.url,
            "title": page.title(),
            "http_status": http_status,
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "new-tab",
                "tab_index": tab_index,
                "url": page.url,
                "title": page.title(),
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Failed to open a new tab: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_switch_tab(args: argparse.Namespace) -> None:
    """Switch to a tab by index or URL match."""
    if args.tab_index is None and not args.tab_url_contains:
        output_error("Provide --tab-index or --tab-url-contains.")
        sys.exit(1)

    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        result: dict[str, Any] = {
            "status": "success",
            "command": "switch-tab",
            "session_id": session_id,
            "tab_index": tab_index,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "switch-tab",
                "tab_index": tab_index,
                "url": page.url,
                "title": page.title(),
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Failed to switch tab: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_close_tab(args: argparse.Namespace) -> None:
    """Close a tab by index or URL match."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        context, pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        closed_url = page.url
        try:
            closed_title = page.title()
        except Exception:
            closed_title = None

        if len(pages) <= 1:
            context.new_page()
        page.close()

        tabs = _list_tabs_in_context(context)
        result: dict[str, Any] = {
            "status": "success",
            "command": "close-tab",
            "session_id": session_id,
            "closed_tab_index": tab_index,
            "closed_url": closed_url,
            "closed_title": closed_title,
            "tabs_count": len(tabs),
            "tabs": tabs,
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "close-tab",
                "closed_tab_index": tab_index,
                "closed_url": closed_url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Failed to close tab: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_click(args: argparse.Namespace) -> None:
    """Click an element in the selected tab."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        page.click(
            args.selector,
            timeout=args.timeout_ms,
            button=args.button,
            click_count=args.click_count,
        )
        if args.wait_for_load:
            page.wait_for_load_state("domcontentloaded", timeout=args.timeout_ms)

        result: dict[str, Any] = {
            "status": "success",
            "command": "click",
            "session_id": session_id,
            "tab_index": tab_index,
            "selector": args.selector,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "click",
                "tab_index": tab_index,
                "selector": args.selector,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Click failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_type(args: argparse.Namespace) -> None:
    """Type or fill text in an element."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        if args.clear:
            page.fill(args.selector, args.text, timeout=args.timeout_ms)
        else:
            page.click(args.selector, timeout=args.timeout_ms)
            page.type(args.selector, args.text, timeout=args.timeout_ms, delay=args.delay_ms)
        if args.press_enter:
            page.press(args.selector, "Enter", timeout=args.timeout_ms)

        result: dict[str, Any] = {
            "status": "success",
            "command": "type",
            "session_id": session_id,
            "tab_index": tab_index,
            "selector": args.selector,
            "chars": len(args.text),
            "clear": bool(args.clear),
            "press_enter": bool(args.press_enter),
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "type",
                "tab_index": tab_index,
                "selector": args.selector,
                "chars": len(args.text),
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Type failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_press(args: argparse.Namespace) -> None:
    """Press a keyboard key on the page or in an element."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        if args.selector:
            page.press(args.selector, args.key, timeout=args.timeout_ms)
        else:
            page.keyboard.press(args.key)

        result: dict[str, Any] = {
            "status": "success",
            "command": "press",
            "session_id": session_id,
            "tab_index": tab_index,
            "key": args.key,
            "selector": args.selector,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "press",
                "tab_index": tab_index,
                "key": args.key,
                "selector": args.selector,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Press failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_wait_for(args: argparse.Namespace) -> None:
    """Wait for selector/text/url/load-state conditions."""
    if not any([args.selector, args.text, args.url_contains, args.load_state]):
        output_error("Provide at least one condition: --selector, --text, --url-contains, or --load-state.")
        sys.exit(1)

    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        waited_for: list[str] = []
        if args.load_state:
            page.wait_for_load_state(args.load_state, timeout=args.timeout_ms)
            waited_for.append(f"load_state:{args.load_state}")
        if args.selector:
            page.wait_for_selector(args.selector, timeout=args.timeout_ms, state=args.selector_state)
            waited_for.append(f"selector:{args.selector}")
        if args.text:
            page.wait_for_function(
                "(needle) => !!document.body && document.body.innerText.includes(needle)",
                args.text,
                timeout=args.timeout_ms,
            )
            waited_for.append(f"text:{args.text}")
        if args.url_contains:
            page.wait_for_function(
                "(needle) => window.location.href.includes(needle)",
                args.url_contains,
                timeout=args.timeout_ms,
            )
            waited_for.append(f"url_contains:{args.url_contains}")

        result: dict[str, Any] = {
            "status": "success",
            "command": "wait-for",
            "session_id": session_id,
            "tab_index": tab_index,
            "waited_for": waited_for,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "wait-for",
                "tab_index": tab_index,
                "waited_for": waited_for,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Wait condition failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_go_back(args: argparse.Namespace) -> None:
    """Go back in browser history."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        response = page.go_back(wait_until="domcontentloaded", timeout=args.timeout_ms)
        result: dict[str, Any] = {
            "status": "success",
            "command": "go-back",
            "session_id": session_id,
            "tab_index": tab_index,
            "navigated": response is not None,
            "http_status": response.status if response else None,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "go-back",
                "tab_index": tab_index,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"go-back failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_go_forward(args: argparse.Namespace) -> None:
    """Go forward in browser history."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        response = page.go_forward(wait_until="domcontentloaded", timeout=args.timeout_ms)
        result: dict[str, Any] = {
            "status": "success",
            "command": "go-forward",
            "session_id": session_id,
            "tab_index": tab_index,
            "navigated": response is not None,
            "http_status": response.status if response else None,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "go-forward",
                "tab_index": tab_index,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"go-forward failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_reload(args: argparse.Namespace) -> None:
    """Reload the current page."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        response = page.reload(wait_until="domcontentloaded", timeout=args.timeout_ms)
        result: dict[str, Any] = {
            "status": "success",
            "command": "reload",
            "session_id": session_id,
            "tab_index": tab_index,
            "http_status": response.status if response else None,
            "url": page.url,
            "title": page.title(),
        }
        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "reload",
                "tab_index": tab_index,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Reload failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_read_page(args: argparse.Namespace) -> None:
    """Read text/html/links from the selected tab."""
    try:
        session_id, ws, workspace_name = _resolve_session_workspace(args)
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, _page = _connect_playwright(session_id)

    try:
        _context, _pages, page, tab_index = _select_page(
            browser,
            tab_index=args.tab_index,
            tab_url_contains=args.tab_url_contains,
        )
        text_content = page.evaluate("""
            () => {
                const body = document.body;
                if (!body) return '';
                const clone = body.cloneNode(true);
                clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                return clone.innerText || clone.textContent || '';
            }
        """)
        text_total = len(text_content)
        if args.max_text_chars > 0 and text_total > args.max_text_chars:
            text_content = text_content[:args.max_text_chars] + f"\n\n... [truncated, total {text_total} chars]"

        result: dict[str, Any] = {
            "status": "success",
            "command": "read-page",
            "session_id": session_id,
            "tab_index": tab_index,
            "url": page.url,
            "title": page.title(),
            "text_length": text_total,
            "text_content": text_content,
        }

        if args.include_html:
            html_content = page.content()
            html_total = len(html_content)
            if args.max_html_chars > 0 and html_total > args.max_html_chars:
                html_content = html_content[:args.max_html_chars] + f"\n\n... [truncated, total {html_total} chars]"
            result["html_length"] = html_total
            result["html_content"] = html_content

        if args.include_links:
            links = page.eval_on_selector_all(
                "a[href]",
                """(els) => els.map((a) => ({
                    text: (a.innerText || '').trim(),
                    href: a.href || a.getAttribute('href') || ''
                }))""",
            )
            result["links_count"] = len(links)
            result["links"] = links[: max(0, args.max_links)]

        if workspace_name:
            result["workspace"] = workspace_name
        _sync_workspace_from_browser(
            workspace_name=workspace_name,
            ws=ws,
            browser=browser,
            session_id=session_id,
            history_entry={
                "type": "read-page",
                "tab_index": tab_index,
                "url": page.url,
            },
            result=result,
        )
        output_json(result)
    except Exception as e:
        output_error(f"Failed to read page: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_screenshot(args: argparse.Namespace) -> None:
    """Take a screenshot of the current page without navigating."""
    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, page = _connect_playwright(session_id)

    try:
        full = getattr(args, "full_page", False)
        page.screenshot(path=args.output, full_page=full)
        result: dict[str, Any] = {
            "status": "success",
            "command": "screenshot",
            "session_id": session_id,
            "current_url": page.url,
            "title": page.title(),
            "screenshot_path": args.output,
            "full_page": full,
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)

        if ws is not None and getattr(args, "workspace", None):
            try:
                tabs = _collect_tabs_from_browser(browser)
                ws["tabs"] = tabs
                ws["tabs_captured_at"] = _utc_now_iso()
                _append_ws_history(ws, {
                    "ts": _utc_now_iso(),
                    "type": "screenshot",
                    "session_id": session_id,
                    "url": page.url,
                    "output": args.output,
                    "full_page": full,
                })
                _save_workspace(str(args.workspace), ws)
                result["workspace_tabs_count"] = len(tabs)
            except Exception as e:
                result["workspace_update_error"] = str(e)

        output_json(result)
    except Exception as e:
        output_error(f"Screenshot failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_execute_js(args: argparse.Namespace) -> None:
    """Execute JavaScript code in a browser session."""
    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, page = _connect_playwright(session_id)

    try:
        result_value = page.evaluate(args.code)
        result: dict[str, Any] = {
            "status": "success",
            "command": "execute-js",
            "session_id": session_id,
            "code": args.code,
            "result": result_value,
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)

        if ws is not None and getattr(args, "workspace", None):
            try:
                tabs = _collect_tabs_from_browser(browser)
                ws["tabs"] = tabs
                ws["tabs_captured_at"] = _utc_now_iso()
                _append_ws_history(ws, {
                    "ts": _utc_now_iso(),
                    "type": "execute-js",
                    "session_id": session_id,
                    "url": page.url,
                    "code": args.code,
                })
                _save_workspace(str(args.workspace), ws)
                result["workspace_tabs_count"] = len(tabs)
            except Exception as e:
                result["workspace_update_error"] = str(e)

        output_json(result)
    except Exception as e:
        output_error(f"JavaScript execution failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_get_cookies(args: argparse.Namespace) -> None:
    """Get all cookies from a browser session."""
    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    pw, browser, page = _connect_playwright(session_id)

    try:
        context = page.context
        cookies = context.cookies()
        result: dict[str, Any] = {
            "status": "success",
            "command": "get-cookies",
            "session_id": session_id,
            "cookie_count": len(cookies),
            "cookies": cookies,
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)

        if ws is not None and getattr(args, "workspace", None):
            try:
                tabs = _collect_tabs_from_browser(browser)
                ws["tabs"] = tabs
                ws["tabs_captured_at"] = _utc_now_iso()
                _append_ws_history(ws, {
                    "ts": _utc_now_iso(),
                    "type": "get-cookies",
                    "session_id": session_id,
                    "url": page.url,
                })
                _save_workspace(str(args.workspace), ws)
                result["workspace_tabs_count"] = len(tabs)
            except Exception as e:
                result["workspace_update_error"] = str(e)

        output_json(result)
    except Exception as e:
        output_error(f"Failed to get cookies: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Recordings, Logs & Debug
# ---------------------------------------------------------------------------

def cmd_get_recording(args: argparse.Namespace) -> None:
    """Fetch the session rrweb recording events (JSON) and save to a file."""
    client = get_client()

    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
        recording = client.sessions.recording.retrieve(session_id)

        # Browserbase returns rrweb events (JSON). Handle either plain dict/list
        # or SDK model objects.
        data: Any
        if isinstance(recording, (dict, list)):
            data = recording
        elif hasattr(recording, "model_dump"):
            try:
                data = recording.model_dump()
            except TypeError:
                data = recording.model_dump(mode="json")
        elif hasattr(recording, "to_dict"):
            data = recording.to_dict()
        elif hasattr(recording, "dict"):
            data = recording.dict()
        else:
            try:
                data = list(recording)  # type: ignore[arg-type]
            except Exception:
                data = recording

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        file_size = os.path.getsize(args.output) if os.path.exists(args.output) else 0
        event_count = len(data) if isinstance(data, list) else None
        result: dict[str, Any] = {
            "status": "success",
            "command": "get-recording",
            "session_id": session_id,
            "output_path": args.output,
            "file_size_bytes": file_size,
            "rrweb_event_count": event_count,
            "message": f"rrweb recording saved to {args.output} ({file_size:,} bytes)."
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)
        if ws is not None and getattr(args, "workspace", None):
            try:
                _append_ws_history(ws, {"ts": _utc_now_iso(), "type": "get-recording", "session_id": session_id})
                _save_workspace(str(args.workspace), ws)
            except Exception:
                pass
        output_json(result)
    except Exception as e:
        output_error(f"Failed to get recording: {e}")
        sys.exit(1)


def cmd_get_downloads(args: argparse.Namespace) -> None:
    """Download the session downloads archive to a file."""
    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
    except Exception as e:
        output_error(str(e))
        sys.exit(1)

    api_key = get_env("BROWSERBASE_API_KEY")
    url = f"{_BROWSERBASE_API_BASE}/sessions/{session_id}/downloads"
    info = _download_api_to_file(
        url=url,
        output_path=args.output,
        headers={"X-BB-API-Key": api_key},
    )
    if not info.get("ok"):
        output_error(f"Failed to download session downloads: {info.get('error') or 'unknown error'}")
        sys.exit(1)

    file_size = os.path.getsize(args.output) if os.path.exists(args.output) else 0
    result: dict[str, Any] = {
        "status": "success",
        "command": "get-downloads",
        "session_id": session_id,
        "output_path": args.output,
        "file_size_bytes": file_size,
        "content_type": info.get("content_type"),
        "message": f"Downloads archive saved to {args.output} ({file_size:,} bytes).",
    }
    if getattr(args, "workspace", None):
        result["workspace"] = str(args.workspace)
    if ws is not None and getattr(args, "workspace", None):
        try:
            _append_ws_history(ws, {"ts": _utc_now_iso(), "type": "get-downloads", "session_id": session_id})
            _save_workspace(str(args.workspace), ws)
        except Exception:
            pass
    output_json(result)


def cmd_get_logs(args: argparse.Namespace) -> None:
    """Get logs from a session."""
    client = get_client()

    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
        logs_response = client.sessions.logs.list(session_id)

        # Parse the log entries
        log_entries = []
        if hasattr(logs_response, "__iter__"):
            for entry in logs_response:
                log_entries.append({
                    "timestamp": str(getattr(entry, "timestamp", "")),
                    "method": getattr(entry, "method", ""),
                    "params": getattr(entry, "params", None),
                })
        else:
            log_entries = [str(logs_response)]

        result: dict[str, Any] = {
            "status": "success",
            "command": "get-logs",
            "session_id": session_id,
            "log_count": len(log_entries),
            "logs": log_entries[:200],  # Cap at 200 entries to avoid huge output
        }
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)
        if ws is not None and getattr(args, "workspace", None):
            try:
                _append_ws_history(ws, {"ts": _utc_now_iso(), "type": "get-logs", "session_id": session_id})
                _save_workspace(str(args.workspace), ws)
            except Exception:
                pass
        output_json(result)
    except Exception as e:
        output_error(f"Failed to get logs: {e}")
        sys.exit(1)


def cmd_live_url(args: argparse.Namespace) -> None:
    """Get the live debug URL for a session."""
    client = get_client()

    try:
        session_id, ws = _resolve_session_id(getattr(args, "session_id", None), getattr(args, "workspace", None))
        live_dict = _get_live_urls_safe(client, session_id)
        if live_dict is None:
            output_error("Failed to fetch live debugger URLs for this session right now.")
            sys.exit(1)

        result: dict[str, Any] = {
            "status": "success",
            "command": "live-url",
            "session_id": session_id,
            **live_dict,
        }
        _attach_human_handoff(
            result,
            live_dict,
            workspace=str(args.workspace) if getattr(args, "workspace", None) else None,
            session_id=session_id,
        )
        if getattr(args, "workspace", None):
            result["workspace"] = str(args.workspace)
            if ws is not None:
                result["pending_handoff"] = ws.get("pending_handoff")
        else:
            result["pending_handoff"] = _load_handoff_file(str(session_id))
        if ws is not None and getattr(args, "workspace", None):
            try:
                _append_ws_history(ws, {"ts": _utc_now_iso(), "type": "live-url", "session_id": session_id})
                _save_workspace(str(args.workspace), ws)
            except Exception:
                pass
        output_json(result)
    except Exception as e:
        output_error(f"Failed to get live URL: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Human Handoff (Human-in-the-loop)
# ---------------------------------------------------------------------------

def _handoff_conditions_from_args(args: argparse.Namespace) -> dict[str, Any]:
    conditions: dict[str, Any] = {}
    for key in [
        "selector",
        "selector_state",
        "text",
        "url_contains",
        "title_contains",
        "load_state",
        "cookie_name",
        "cookie_domain_contains",
        "local_storage_key",
        "session_storage_key",
    ]:
        value = getattr(args, key, None)
        if value is not None:
            conditions[key] = value
    return conditions


def _handoff_has_any_check(conditions: dict[str, Any]) -> bool:
    return any(
        conditions.get(k)
        for k in [
            "selector",
            "text",
            "url_contains",
            "title_contains",
            "load_state",
            "cookie_name",
            "local_storage_key",
            "session_storage_key",
        ]
    )


def _handoff_completion_hint(conditions: dict[str, Any]) -> Optional[str]:
    parts: list[str] = []
    if conditions.get("url_contains"):
        parts.append(f"URL contains '{conditions['url_contains']}'")
    if conditions.get("title_contains"):
        parts.append(f"title contains '{conditions['title_contains']}'")
    if conditions.get("text"):
        parts.append(f"page text contains '{conditions['text']}'")
    if conditions.get("selector"):
        state = conditions.get("selector_state") or "visible"
        parts.append(f"selector is {state}: {conditions['selector']}")
    if conditions.get("cookie_name"):
        dom = conditions.get("cookie_domain_contains")
        if dom:
            parts.append(f"cookie '{conditions['cookie_name']}' exists (domain contains '{dom}')")
        else:
            parts.append(f"cookie '{conditions['cookie_name']}' exists")
    if conditions.get("local_storage_key"):
        parts.append(f"localStorage['{conditions['local_storage_key']}'] exists")
    if conditions.get("session_storage_key"):
        parts.append(f"sessionStorage['{conditions['session_storage_key']}'] exists")
    if conditions.get("load_state"):
        parts.append(f"load state is '{conditions['load_state']}'")
    if not parts:
        return None
    return "; ".join(parts)


def _check_selector_condition(page: Any, selector: str, selector_state: str) -> bool:
    # Avoid Playwright auto-waits; do an immediate DOM check.
    js = """
        (selector) => {
          const el = document.querySelector(selector);
          if (!el) return { attached: false, visible: false };
          const rect = el.getBoundingClientRect();
          const style = window.getComputedStyle(el);
          const visible = (
            rect.width > 0 &&
            rect.height > 0 &&
            style &&
            style.visibility !== 'hidden' &&
            style.display !== 'none' &&
            style.opacity !== '0'
          );
          return { attached: true, visible };
        }
    """
    try:
        info = page.evaluate(js, selector)
        attached = bool((info or {}).get("attached"))
        visible = bool((info or {}).get("visible"))
        if selector_state == "attached":
            return attached
        if selector_state == "detached":
            return not attached
        if selector_state == "visible":
            return visible
        if selector_state == "hidden":
            return not visible
        return False
    except Exception:
        return False


def _check_text_condition(page: Any, text: str) -> bool:
    try:
        return bool(page.evaluate("(needle) => !!document.body && document.body.innerText.includes(needle)", text))
    except Exception:
        return False


def _check_storage_condition(page: Any, *, kind: str, key: str) -> bool:
    if kind not in ("local", "session"):
        return False
    try:
        if kind == "local":
            return bool(page.evaluate("(k) => localStorage.getItem(k) !== null", key))
        return bool(page.evaluate("(k) => sessionStorage.getItem(k) !== null", key))
    except Exception:
        return False


def _check_load_state_condition(page: Any, load_state: str) -> bool:
    # For check flows, do a cheap readyState check when possible.
    try:
        if load_state == "load":
            return bool(page.evaluate("() => document.readyState === 'complete'"))
        if load_state == "domcontentloaded":
            return bool(page.evaluate("() => ['interactive','complete'].includes(document.readyState)"))
        if load_state == "networkidle":
            try:
                page.wait_for_load_state("networkidle", timeout=250)
                return True
            except Exception:
                return False
    except Exception:
        return False
    return False


def _cookie_match(c: dict[str, Any], *, name: str, domain_contains: Optional[str]) -> bool:
    if c.get("name") != name:
        return False
    if domain_contains:
        return domain_contains.lower() in str(c.get("domain", "")).lower()
    return True


def _check_handoff_conditions_on_page(
    page: Any,
    *,
    conditions: dict[str, Any],
    match: str = "all",
) -> tuple[bool, dict[str, Any]]:
    results: dict[str, Any] = {}
    checks: list[bool] = []

    selector = conditions.get("selector")
    if selector:
        selector_state = conditions.get("selector_state") or "visible"
        cond_ok = _check_selector_condition(page, str(selector), str(selector_state))
        results["selector"] = {"selector": selector, "state": selector_state, "ok": cond_ok}
        checks.append(cond_ok)

    text = conditions.get("text")
    if text:
        cond_ok = _check_text_condition(page, str(text))
        results["text"] = {"text": text, "ok": cond_ok}
        checks.append(cond_ok)

    url_contains = conditions.get("url_contains")
    if url_contains:
        cond_ok = str(url_contains) in (getattr(page, "url", "") or "")
        results["url_contains"] = {"needle": url_contains, "ok": cond_ok, "url": getattr(page, "url", None)}
        checks.append(cond_ok)

    title_contains = conditions.get("title_contains")
    if title_contains:
        try:
            title = page.title()
        except Exception:
            title = None
        cond_ok = title is not None and str(title_contains) in title
        results["title_contains"] = {"needle": title_contains, "ok": cond_ok, "title": title}
        checks.append(cond_ok)

    load_state = conditions.get("load_state")
    if load_state:
        cond_ok = _check_load_state_condition(page, str(load_state))
        results["load_state"] = {"load_state": load_state, "ok": cond_ok}
        checks.append(cond_ok)

    cookie_name = conditions.get("cookie_name")
    if cookie_name:
        domain_contains = conditions.get("cookie_domain_contains")
        cookies: list[dict[str, Any]] = []
        try:
            cookies = list(page.context.cookies())
        except Exception:
            cookies = []
        cond_ok = any(_cookie_match(c, name=str(cookie_name), domain_contains=domain_contains) for c in cookies)
        results["cookie_name"] = {
            "name": cookie_name,
            "domain_contains": domain_contains,
            "ok": cond_ok,
            "cookie_count": len(cookies),
        }
        checks.append(cond_ok)

    local_key = conditions.get("local_storage_key")
    if local_key:
        cond_ok = _check_storage_condition(page, kind="local", key=str(local_key))
        results["local_storage_key"] = {"key": local_key, "ok": cond_ok}
        checks.append(cond_ok)

    session_key = conditions.get("session_storage_key")
    if session_key:
        cond_ok = _check_storage_condition(page, kind="session", key=str(session_key))
        results["session_storage_key"] = {"key": session_key, "ok": cond_ok}
        checks.append(cond_ok)

    if match not in ("all", "any"):
        match = "all"
    ok = all(checks) if match == "all" else any(checks)
    return ok, results


def _check_handoff_once(
    browser: Any,
    *,
    tab_index: Optional[int],
    tab_url_contains: Optional[str],
    conditions: dict[str, Any],
    match: str,
) -> dict[str, Any]:
    context = _primary_context(browser)
    pages = _primary_pages(context, create_if_empty=True)
    tabs = _list_tabs_in_context(context)

    candidates: list[tuple[int, Any]] = []
    if tab_index is not None or tab_url_contains:
        try:
            _ctx, _pages, page, idx = _select_page(browser, tab_index=tab_index, tab_url_contains=tab_url_contains)
            candidates = [(idx, page)]
        except Exception as e:
            return {
                "done": False,
                "error": str(e),
                "tabs": tabs,
            }
    else:
        for i, p in enumerate(pages):
            url = getattr(p, "url", "") or ""
            if url.startswith(("chrome-extension://", "devtools://")):
                continue
            candidates.append((i, p))

    last_checked: Optional[dict[str, Any]] = None
    for idx, page in candidates:
        ok, cond_results = _check_handoff_conditions_on_page(page, conditions=conditions, match=match)
        try:
            title = page.title()
        except Exception:
            title = None
        if ok:
            return {
                "done": True,
                "matched_tab_index": idx,
                "url": getattr(page, "url", None),
                "title": title,
                "condition_results": cond_results,
                "tabs": tabs,
            }
        if last_checked is None:
            last_checked = {
                "checked_tab_index": idx,
                "checked_url": getattr(page, "url", None),
                "checked_title": title,
                "condition_results": cond_results,
            }

    # Not done; include last-seen state for tab 0 if present.
    fallback_url = None
    fallback_title = None
    if pages:
        try:
            fallback_url = pages[0].url
        except Exception:
            fallback_url = None
        try:
            fallback_title = pages[0].title()
        except Exception:
            fallback_title = None

    out = {
        "done": False,
        "current_url": fallback_url,
        "current_title": fallback_title,
        "tabs": tabs,
    }
    if last_checked is not None:
        out.update(last_checked)
    return out


def cmd_handoff(args: argparse.Namespace) -> None:
    """
    Create/check/clear a human handoff request.

    This is a lightweight state machine:
    - action=set: store the human instructions + completion checks (selector/text/url/cookie/storage)
    - action=check: evaluate checks once, and mark done if satisfied
    - action=wait: poll checks until satisfied or timeout
    - action=get: return stored handoff (if any)
    - action=clear: remove stored handoff
    """
    action = str(getattr(args, "action", "") or "").lower().strip()
    if action not in ("set", "get", "check", "wait", "clear"):
        output_error("Invalid --action. Use one of: set, get, check, wait, clear.")
        sys.exit(1)

    workspace_name = str(args.workspace) if getattr(args, "workspace", None) else None
    ws: Optional[dict[str, Any]] = None
    session_id: Optional[str] = getattr(args, "session_id", None)

    if workspace_name:
        try:
            ws = _load_workspace(workspace_name)
        except Exception as e:
            output_error(f"Failed to load workspace: {e}")
            sys.exit(1)
        if not session_id:
            active = ws.get("active_session_id")
            session_id = str(active) if active else None

    if not session_id and action in ("set", "check", "wait"):
        if workspace_name:
            output_error(
                f"Workspace '{workspace_name}' has no active session. Start it first: start-workspace --name {workspace_name}"
            )
        else:
            output_error("Missing session identifier. Provide --session-id or --workspace.")
        sys.exit(1)

    # Load existing handoff state.
    existing = _get_pending_handoff(session_id=session_id, ws=ws, workspace_name=workspace_name)

    if action == "get":
        output_json({
            "status": "success",
            "command": "handoff",
            "action": "get",
            "workspace": workspace_name,
            "session_id": session_id,
            "handoff": existing,
        })
        return

    if action == "clear":
        _set_pending_handoff(
            session_id=session_id,
            ws=ws,
            workspace_name=workspace_name,
            handoff=None,
            history_type="handoff_clear" if workspace_name else None,
        )
        output_json({
            "status": "success",
            "command": "handoff",
            "action": "clear",
            "workspace": workspace_name,
            "session_id": session_id,
            "message": "Handoff cleared.",
        })
        return

    if action == "set":
        instructions = getattr(args, "instructions", None)
        if not instructions:
            output_error("Missing --instructions for handoff set.")
            sys.exit(1)

        conditions = _handoff_conditions_from_args(args)
        if not _handoff_has_any_check(conditions):
            output_error(
                "Provide at least one completion check: "
                "--selector/--text/--url-contains/--title-contains/--cookie-name/--local-storage-key/--session-storage-key/--load-state"
            )
            sys.exit(1)

        completion_hint = _handoff_completion_hint(conditions)
        match_mode = str(getattr(args, "match", None) or "all").lower().strip()
        if match_mode not in ("all", "any"):
            match_mode = "all"
        handoff: dict[str, Any] = {
            "id": f"handoff_{_utc_now_iso()}",
            "created_at": _utc_now_iso(),
            "status": "pending",
            "instructions": instructions,
            "conditions": conditions,
            "completion_hint": completion_hint,
            "match": match_mode,
            "tab_index": getattr(args, "tab_index", None),
            "tab_url_contains": getattr(args, "tab_url_contains", None),
        }
        _set_pending_handoff(
            session_id=session_id,
            ws=ws,
            workspace_name=workspace_name,
            handoff=handoff,
            history_type="handoff_set" if workspace_name else None,
        )

        # Best-effort attach live debugger URL so the agent can paste it immediately.
        live_urls = None
        try:
            client = get_client()
            live_urls = _get_live_urls_safe(client, str(session_id))
        except Exception:
            live_urls = None

        result: dict[str, Any] = {
            "status": "success",
            "command": "handoff",
            "action": "set",
            "workspace": workspace_name,
            "session_id": session_id,
            "handoff": handoff,
            "message": "Handoff set. Send the instructions + human_handoff.share_url to the user, then check later.",
        }
        if live_urls is not None:
            _attach_human_handoff(result, live_urls, workspace=workspace_name, session_id=str(session_id))

        # Convenience: a ready-to-send message payload for the agent.
        share_text = ((result.get("human_handoff") or {}).get("share_text")) if isinstance(result.get("human_handoff"), dict) else None
        share_md = ((result.get("human_handoff") or {}).get("share_markdown")) if isinstance(result.get("human_handoff"), dict) else None
        if share_text or share_md:
            stop_line_text = f"Stop when: {completion_hint}" if completion_hint else ""
            stop_line_md = f"Stop when: {completion_hint}" if completion_hint else ""
            result["suggested_user_message"] = {
                "text": "\n".join([
                    "Human step needed:",
                    instructions.strip(),
                    stop_line_text,
                    "",
                    share_text or "",
                    "Keep the tab open. I'll detect completion and continue automatically.",
                    "If it doesn't continue, reply 'done' and I'll re-check.",
                ]).strip(),
                "markdown": "\n".join([
                    "**Human step needed:**",
                    instructions.strip(),
                    stop_line_md,
                    "",
                    share_md or "",
                    "Keep the tab open. I'll detect completion and continue automatically.",
                    "If it doesn't continue, reply **done** and I'll re-check.",
                ]).strip(),
            }
        output_json(result)
        return

    # check / wait
    if not existing:
        output_json({
            "status": "success",
            "command": "handoff",
            "action": action,
            "workspace": workspace_name,
            "session_id": session_id,
            "handoff": None,
            "done": False,
            "message": "No handoff is currently set.",
        })
        return

    conditions = dict((existing or {}).get("conditions") or {})
    tab_index = (existing or {}).get("tab_index")
    tab_url_contains = (existing or {}).get("tab_url_contains")
    match_mode = str((existing or {}).get("match") or "all").lower().strip()
    if match_mode not in ("all", "any"):
        match_mode = "all"

    timeout_ms = int(getattr(args, "timeout_ms", 0) or 0)
    if action == "check":
        timeout_ms = 0
    if action == "wait" and timeout_ms <= 0:
        timeout_ms = 300000  # 5 min default for wait

    pw, browser, _page = _connect_playwright(str(session_id))
    try:
        started = time.time()
        last = None
        while True:
            last = _check_handoff_once(
                browser,
                tab_index=tab_index,
                tab_url_contains=tab_url_contains,
                conditions=conditions,
                match=match_mode,
            )
            if last.get("done"):
                existing["status"] = "done"
                existing["done_at"] = _utc_now_iso()
                _set_pending_handoff(
                    session_id=session_id,
                    ws=ws,
                    workspace_name=workspace_name,
                    handoff=existing,
                    history_type="handoff_done" if workspace_name else None,
                )
                break

            if action == "check":
                break

            elapsed_ms = int((time.time() - started) * 1000)
            if elapsed_ms >= timeout_ms:
                break
            time.sleep(0.5)

        result: dict[str, Any] = {
            "status": "success",
            "command": "handoff",
            "action": action,
            "workspace": workspace_name,
            "session_id": session_id,
            "handoff": existing,
            **(last or {}),
        }

        # If we are operating on a workspace, sync tab snapshot so the agent can "take back over"
        # after the human has been driving in the live debugger.
        if workspace_name and ws is not None:
            try:
                tabs_snapshot = _collect_tabs_from_browser(browser)
                ws["tabs"] = tabs_snapshot
                ws["tabs_captured_at"] = _utc_now_iso()
                _append_ws_history(ws, {
                    "ts": _utc_now_iso(),
                    "type": "handoff_check",
                    "session_id": session_id,
                    "done": bool(result.get("done")),
                    "matched_tab_index": result.get("matched_tab_index"),
                })
                _save_workspace(workspace_name, ws)
                result["workspace_tabs_count"] = len(tabs_snapshot)
            except Exception as e:
                result["workspace_update_error"] = str(e)

        # If not done, include a fresh live debugger URL when possible.
        if not result.get("done"):
            try:
                client = get_client()
                live_urls = _get_live_urls_safe(client, str(session_id))
                if live_urls is not None:
                    _attach_human_handoff(result, live_urls, workspace=workspace_name, session_id=str(session_id))
            except Exception:
                pass

            # Provide a ready-to-send reprompt message for the user.
            if isinstance(result.get("human_handoff"), dict):
                instructions = str((existing or {}).get("instructions") or "").strip()
                completion_hint = (existing or {}).get("completion_hint") or _handoff_completion_hint(conditions)
                share_text = str(result["human_handoff"].get("share_text") or "").strip()
                share_md = str(result["human_handoff"].get("share_markdown") or "").strip()
                if instructions and (share_text or share_md):
                    stop_line_text = f"Stop when: {completion_hint}" if completion_hint else ""
                    stop_line_md = f"Stop when: {completion_hint}" if completion_hint else ""
                    result["suggested_user_message"] = {
                        "text": "\n".join([
                            "Human step needed:",
                            instructions,
                            stop_line_text,
                            "",
                            share_text,
                            "Keep the tab open. I'll detect completion and continue automatically.",
                            "If it doesn't continue, reply 'done' and I'll re-check.",
                        ]).strip(),
                        "markdown": "\n".join([
                            "**Human step needed:**",
                            instructions,
                            stop_line_md,
                            "",
                            share_md,
                            "Keep the tab open. I'll detect completion and continue automatically.",
                            "If it doesn't continue, reply **done** and I'll re-check.",
                        ]).strip(),
                    }

        output_json(result)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# CLI Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browserbase Session Manager for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- install --
    p_install = subparsers.add_parser("install", help="Install Python deps + Playwright Chromium")
    p_install.add_argument("--no-uv", action="store_true", default=False,
                           help="Do not use uv even if installed; use pip instead")
    p_install.set_defaults(func=cmd_install)

    # -- setup --
    p_setup = subparsers.add_parser("setup", help="Validate credentials and smoke test")
    p_setup.add_argument("--install", action="store_true", default=False,
                         help="Install Python deps + Playwright Chromium before running checks")
    p_setup.set_defaults(func=cmd_setup)

    # -- list-projects --
    p_lp = subparsers.add_parser("list-projects", help="List Browserbase projects for this API key")
    p_lp.set_defaults(func=cmd_list_projects)

    # -- create-context --
    p_cc = subparsers.add_parser("create-context", help="Create a persistent context")
    p_cc.add_argument("--name", default=None,
                       help="Friendly name for this context (e.g. 'github', 'slack')")
    p_cc.set_defaults(func=cmd_create_context)

    # -- delete-context --
    p_dc = subparsers.add_parser("delete-context", help="Delete a context (permanent)")
    p_dc.add_argument("--context-id", required=True,
                       help="Context ID or name to delete")
    p_dc.set_defaults(func=cmd_delete_context)

    # -- list-contexts --
    p_lc = subparsers.add_parser("list-contexts", help="List saved named contexts")
    p_lc.set_defaults(func=cmd_list_contexts)

    # -- create-workspace --
    p_cw = subparsers.add_parser("create-workspace", help="Create a named workspace (context + tab history)")
    p_cw.add_argument("--name", required=True, help="Workspace name (letters/digits, '_' or '-', 1-64 chars)")
    p_cw.add_argument("--context-id", default=None, help="Use an existing context ID or name instead of creating one")
    p_cw.add_argument("--force", action="store_true", default=False, help="Overwrite existing workspace file")
    p_cw.set_defaults(func=cmd_create_workspace)

    # -- list-workspaces --
    p_lw = subparsers.add_parser("list-workspaces", help="List local workspaces")
    p_lw.set_defaults(func=cmd_list_workspaces)

    # -- get-workspace --
    p_gw = subparsers.add_parser("get-workspace", help="Get workspace details")
    p_gw.add_argument("--name", required=True, help="Workspace name")
    p_gw.set_defaults(func=cmd_get_workspace)

    # -- delete-workspace --
    p_dw = subparsers.add_parser("delete-workspace", help="Delete a local workspace")
    p_dw.add_argument("--name", required=True, help="Workspace name")
    p_dw.add_argument("--delete-context", action="store_true", default=False,
                      help="Also delete the remote Browserbase context (destructive)")
    p_dw.set_defaults(func=cmd_delete_workspace)

    # -- start-workspace --
    p_sw = subparsers.add_parser("start-workspace", help="Start a keep-alive session for a workspace")
    p_sw.add_argument("--name", required=True, help="Workspace name")
    p_sw.add_argument("--force-new", action="store_true", default=False,
                      help="Start a new session even if the workspace already has an active one")
    p_sw.add_argument("--no-keep-alive", action="store_true", default=False,
                      help="Disable keep-alive (keep-alive is ON by default for workspaces)")
    p_sw.add_argument("--timeout", type=int, default=3600,
                      help="Session timeout in seconds (60-21600). Default: 3600")
    p_sw.add_argument("--no-restore-tabs", dest="restore_tabs", action="store_false", default=True,
                      help="Do not restore previously-saved tabs")
    p_sw.add_argument("--max-tabs", type=int, default=15,
                      help="Max tabs to restore (0 = no cap). Default: 15")
    p_sw.add_argument("--region", default=None,
                      choices=["us-west-2", "us-east-1", "eu-central-1", "ap-southeast-1"],
                      help="Session region")
    p_sw.add_argument("--proxy", action="store_true", default=False,
                      help="Enable proxy")
    p_sw.add_argument("--block-ads", action="store_true", default=False,
                      help="Block ads")
    p_sw.add_argument("--no-record", action="store_true", default=False,
                      help="Disable session recording (recording is ON by default)")
    p_sw.add_argument("--no-logs", action="store_true", default=False,
                      help="Disable session logging (logging is ON by default)")
    p_sw.add_argument("--no-solve-captchas", action="store_true", default=False,
                      help="Disable captcha solving (captcha solving is ON by default)")
    p_sw.add_argument("--viewport-width", type=int, default=None,
                      help="Viewport width in pixels")
    p_sw.add_argument("--viewport-height", type=int, default=None,
                      help="Viewport height in pixels")
    p_sw.set_defaults(func=cmd_start_workspace)

    # -- resume-workspace --
    p_rw = subparsers.add_parser("resume-workspace", help="Reconnect to a workspace session or start a new one")
    p_rw.add_argument("--name", required=True, help="Workspace name")
    p_rw.add_argument("--force-new", action="store_true", default=False,
                      help="Always start a new session (even if one is running)")
    p_rw.add_argument("--no-keep-alive", action="store_true", default=False,
                      help="Disable keep-alive (keep-alive is ON by default for workspaces)")
    p_rw.add_argument("--timeout", type=int, default=3600,
                      help="Session timeout in seconds (60-21600). Default: 3600")
    p_rw.add_argument("--no-restore-tabs", dest="restore_tabs", action="store_false", default=True,
                      help="Do not restore previously-saved tabs")
    p_rw.add_argument("--max-tabs", type=int, default=15,
                      help="Max tabs to restore (0 = no cap). Default: 15")
    p_rw.add_argument("--region", default=None,
                      choices=["us-west-2", "us-east-1", "eu-central-1", "ap-southeast-1"],
                      help="Session region")
    p_rw.add_argument("--proxy", action="store_true", default=False,
                      help="Enable proxy")
    p_rw.add_argument("--block-ads", action="store_true", default=False,
                      help="Block ads")
    p_rw.add_argument("--no-record", action="store_true", default=False,
                      help="Disable session recording (recording is ON by default)")
    p_rw.add_argument("--no-logs", action="store_true", default=False,
                      help="Disable session logging (logging is ON by default)")
    p_rw.add_argument("--no-solve-captchas", action="store_true", default=False,
                      help="Disable captcha solving (captcha solving is ON by default)")
    p_rw.add_argument("--viewport-width", type=int, default=None,
                      help="Viewport width in pixels")
    p_rw.add_argument("--viewport-height", type=int, default=None,
                      help="Viewport height in pixels")
    p_rw.set_defaults(func=cmd_resume_workspace)

    # -- snapshot-workspace --
    p_snap = subparsers.add_parser("snapshot-workspace", help="Save current open tabs to workspace state")
    p_snap.add_argument("--name", required=True, help="Workspace name")
    p_snap.add_argument("--session-id", default=None, help="Override session ID (defaults to workspace active session)")
    p_snap.set_defaults(func=cmd_snapshot_workspace)

    # -- stop-workspace --
    p_stop = subparsers.add_parser("stop-workspace", help="Snapshot tabs and terminate the active workspace session")
    p_stop.add_argument("--name", required=True, help="Workspace name")
    p_stop.set_defaults(func=cmd_stop_workspace)

    # -- create-session --
    p_cs = subparsers.add_parser("create-session", help="Create a new browser session")
    p_cs.add_argument("--context-id",
                       help="Context ID or name for auth persistence")
    p_cs.add_argument("--persist", dest="persist", action="store_true", default=True,
                       help="Save auth state back to context on session close (default: on)")
    p_cs.add_argument("--no-persist", dest="persist", action="store_false",
                       help="Disable context persistence on close (not recommended)")
    p_cs.add_argument("--keep-alive", action="store_true", default=False,
                       help="Keep session alive after disconnection")
    p_cs.add_argument("--timeout", type=int, default=None,
                       help="Session timeout in seconds (60-21600)")
    p_cs.add_argument("--region", default=None,
                       choices=["us-west-2", "us-east-1", "eu-central-1", "ap-southeast-1"],
                       help="Session region")
    p_cs.add_argument("--proxy", action="store_true", default=False,
                       help="Enable proxy")
    p_cs.add_argument("--block-ads", action="store_true", default=False,
                       help="Block ads")
    p_cs.add_argument("--no-record", action="store_true", default=False,
                       help="Disable session recording (recording is ON by default)")
    p_cs.add_argument("--no-logs", action="store_true", default=False,
                       help="Disable session logging (logging is ON by default)")
    p_cs.add_argument("--no-solve-captchas", action="store_true", default=False,
                       help="Disable captcha solving (captcha solving is ON by default)")
    p_cs.add_argument("--viewport-width", type=int, default=None,
                       help="Viewport width in pixels")
    p_cs.add_argument("--viewport-height", type=int, default=None,
                       help="Viewport height in pixels")
    p_cs.set_defaults(func=cmd_create_session)

    # -- list-sessions --
    p_ls = subparsers.add_parser("list-sessions", help="List all sessions")
    p_ls.add_argument("--status", default=None,
                       choices=["RUNNING", "COMPLETED", "ERROR", "TIMED_OUT"],
                       help="Filter by status")
    p_ls.set_defaults(func=cmd_list_sessions)

    # -- get-session --
    p_gs = subparsers.add_parser("get-session", help="Get session details")
    p_gs.add_argument("--session-id", default=None, help="Session ID")
    p_gs.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_gs.set_defaults(func=cmd_get_session)

    # -- terminate-session --
    p_ts = subparsers.add_parser("terminate-session", help="Terminate a session")
    p_ts.add_argument("--session-id", default=None, help="Session ID to terminate")
    p_ts.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_ts.set_defaults(func=cmd_terminate_session)

    # -- navigate --
    p_nav = subparsers.add_parser("navigate", help="Navigate to a URL")
    p_nav.add_argument("--session-id", default=None, help="Session ID")
    p_nav.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_nav.add_argument("--url", required=True, help="URL to navigate to")
    p_nav.add_argument("--extract-text", action="store_true", default=False,
                        help="Extract visible text content from the page")
    p_nav.add_argument("--screenshot", default=None,
                        help="Path to save a screenshot")
    p_nav.add_argument("--full-page", action="store_true", default=False,
                        help="Capture full scrollable page (not just viewport)")
    p_nav.set_defaults(func=cmd_navigate)

    # -- list-tabs --
    p_lt = subparsers.add_parser("list-tabs", help="List open tabs")
    p_lt.add_argument("--session-id", default=None, help="Session ID")
    p_lt.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_lt.set_defaults(func=cmd_list_tabs)

    # -- new-tab --
    p_nt = subparsers.add_parser("new-tab", help="Open a new tab (optionally navigate)")
    p_nt.add_argument("--session-id", default=None, help="Session ID")
    p_nt.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_nt.add_argument("--url", default="about:blank", help="URL to open in the new tab (default: about:blank)")
    p_nt.add_argument("--timeout-ms", type=int, default=30000, help="Navigation timeout in milliseconds")
    p_nt.set_defaults(func=cmd_new_tab)

    # -- switch-tab --
    p_st = subparsers.add_parser("switch-tab", help="Switch tab by index or URL match")
    p_st.add_argument("--session-id", default=None, help="Session ID")
    p_st.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_st.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_st.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_st.set_defaults(func=cmd_switch_tab)

    # -- close-tab --
    p_ct = subparsers.add_parser("close-tab", help="Close tab by index or URL match")
    p_ct.add_argument("--session-id", default=None, help="Session ID")
    p_ct.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_ct.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context (default: 0)")
    p_ct.add_argument("--tab-url-contains", default=None, help="Close first tab whose URL contains this text")
    p_ct.set_defaults(func=cmd_close_tab)

    # -- click --
    p_click = subparsers.add_parser("click", help="Click an element")
    p_click.add_argument("--session-id", default=None, help="Session ID")
    p_click.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_click.add_argument("--selector", required=True, help="CSS selector to click")
    p_click.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_click.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_click.add_argument("--button", default="left", choices=["left", "right", "middle"], help="Mouse button")
    p_click.add_argument("--click-count", type=int, default=1, help="Number of clicks")
    p_click.add_argument("--wait-for-load", action="store_true", default=False,
                         help="Wait for domcontentloaded after clicking")
    p_click.add_argument("--timeout-ms", type=int, default=10000, help="Action timeout in milliseconds")
    p_click.set_defaults(func=cmd_click)

    # -- type --
    p_type = subparsers.add_parser("type", help="Type or fill text into an element")
    p_type.add_argument("--session-id", default=None, help="Session ID")
    p_type.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_type.add_argument("--selector", required=True, help="CSS selector to target")
    p_type.add_argument("--text", required=True, help="Text to input")
    p_type.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_type.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_type.add_argument("--clear", action="store_true", default=False,
                        help="Use fill() semantics (clear existing value first)")
    p_type.add_argument("--press-enter", action="store_true", default=False, help="Press Enter after typing")
    p_type.add_argument("--delay-ms", type=int, default=0, help="Delay between typed chars (ms)")
    p_type.add_argument("--timeout-ms", type=int, default=10000, help="Action timeout in milliseconds")
    p_type.set_defaults(func=cmd_type)

    # -- press --
    p_press = subparsers.add_parser("press", help="Press a keyboard key")
    p_press.add_argument("--session-id", default=None, help="Session ID")
    p_press.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_press.add_argument("--key", required=True, help="Key to press (e.g. Enter, Escape, Control+a)")
    p_press.add_argument("--selector", default=None, help="Optional selector to focus/press on")
    p_press.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_press.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_press.add_argument("--timeout-ms", type=int, default=10000, help="Action timeout in milliseconds")
    p_press.set_defaults(func=cmd_press)

    # -- wait-for --
    p_wait = subparsers.add_parser("wait-for", help="Wait for selector/text/url/load-state conditions")
    p_wait.add_argument("--session-id", default=None, help="Session ID")
    p_wait.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_wait.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_wait.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_wait.add_argument("--selector", default=None, help="Wait for this CSS selector")
    p_wait.add_argument("--selector-state", default="visible",
                        choices=["attached", "detached", "visible", "hidden"],
                        help="State for --selector waits")
    p_wait.add_argument("--text", default=None, help="Wait until page text includes this string")
    p_wait.add_argument("--url-contains", default=None, help="Wait until URL contains this string")
    p_wait.add_argument("--load-state", default=None,
                        choices=["load", "domcontentloaded", "networkidle"],
                        help="Wait for this Playwright load state")
    p_wait.add_argument("--timeout-ms", type=int, default=30000, help="Wait timeout in milliseconds")
    p_wait.set_defaults(func=cmd_wait_for)

    # -- go-back --
    p_back = subparsers.add_parser("go-back", help="Go back in browser history")
    p_back.add_argument("--session-id", default=None, help="Session ID")
    p_back.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_back.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_back.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_back.add_argument("--timeout-ms", type=int, default=30000, help="Navigation timeout in milliseconds")
    p_back.set_defaults(func=cmd_go_back)

    # -- go-forward --
    p_fwd = subparsers.add_parser("go-forward", help="Go forward in browser history")
    p_fwd.add_argument("--session-id", default=None, help="Session ID")
    p_fwd.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_fwd.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_fwd.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_fwd.add_argument("--timeout-ms", type=int, default=30000, help="Navigation timeout in milliseconds")
    p_fwd.set_defaults(func=cmd_go_forward)

    # -- reload --
    p_reload = subparsers.add_parser("reload", help="Reload the current page")
    p_reload.add_argument("--session-id", default=None, help="Session ID")
    p_reload.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_reload.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_reload.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_reload.add_argument("--timeout-ms", type=int, default=30000, help="Navigation timeout in milliseconds")
    p_reload.set_defaults(func=cmd_reload)

    # -- read-page --
    p_read = subparsers.add_parser("read-page", help="Read page text/html/links")
    p_read.add_argument("--session-id", default=None, help="Session ID")
    p_read.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_read.add_argument("--tab-index", type=int, default=None, help="Tab index in the primary context")
    p_read.add_argument("--tab-url-contains", default=None, help="Select first tab whose URL contains this text")
    p_read.add_argument("--max-text-chars", type=int, default=50000, help="Max text chars to return (0 = unlimited)")
    p_read.add_argument("--include-html", action="store_true", default=False, help="Include page HTML in output")
    p_read.add_argument("--max-html-chars", type=int, default=200000, help="Max HTML chars to return (0 = unlimited)")
    p_read.add_argument("--include-links", action="store_true", default=False, help="Include extracted anchor links")
    p_read.add_argument("--max-links", type=int, default=100, help="Max links to return")
    p_read.set_defaults(func=cmd_read_page)

    # -- screenshot --
    p_ss = subparsers.add_parser("screenshot", help="Screenshot current page")
    p_ss.add_argument("--session-id", default=None, help="Session ID")
    p_ss.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_ss.add_argument("--output", required=True, help="Path to save screenshot")
    p_ss.add_argument("--full-page", action="store_true", default=False,
                       help="Capture full scrollable page")
    p_ss.set_defaults(func=cmd_screenshot)

    # -- execute-js --
    p_js = subparsers.add_parser("execute-js", help="Execute JavaScript")
    p_js.add_argument("--session-id", default=None, help="Session ID")
    p_js.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_js.add_argument("--code", required=True, help="JavaScript code to execute")
    p_js.set_defaults(func=cmd_execute_js)

    # -- get-cookies --
    p_ck = subparsers.add_parser("get-cookies", help="Get session cookies")
    p_ck.add_argument("--session-id", default=None, help="Session ID")
    p_ck.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_ck.set_defaults(func=cmd_get_cookies)

    # -- get-recording --
    p_rec = subparsers.add_parser("get-recording", help="Fetch session rrweb recording events")
    p_rec.add_argument("--session-id", default=None, help="Session ID")
    p_rec.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_rec.add_argument("--output", required=True,
                        help="Path to save rrweb events (e.g. /tmp/session.rrweb.json)")
    p_rec.set_defaults(func=cmd_get_recording)

    # -- get-downloads --
    p_dl = subparsers.add_parser("get-downloads", help="Download files saved during the session (archive)")
    p_dl.add_argument("--session-id", default=None, help="Session ID")
    p_dl.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_dl.add_argument("--output", required=True, help="Path to save the downloads archive (e.g. /tmp/downloads.zip)")
    p_dl.set_defaults(func=cmd_get_downloads)

    # -- get-logs --
    p_log = subparsers.add_parser("get-logs", help="Get session logs")
    p_log.add_argument("--session-id", default=None, help="Session ID")
    p_log.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_log.set_defaults(func=cmd_get_logs)

    # -- handoff --
    p_ho = subparsers.add_parser("handoff", help="Manage a human handoff (set/check/wait/clear)")
    p_ho.add_argument("--action", required=True, choices=["set", "get", "check", "wait", "clear"],
                      help="Handoff action")
    p_ho.add_argument("--session-id", default=None, help="Session ID")
    p_ho.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_ho.add_argument("--instructions", default=None,
                      help="(set) Human instructions to perform in the live debugger")
    p_ho.add_argument("--tab-index", type=int, default=None,
                      help="(set) Tab index to monitor (optional)")
    p_ho.add_argument("--tab-url-contains", default=None,
                      help="(set) Monitor the first tab whose URL contains this text (optional)")
    p_ho.add_argument("--selector", default=None, help="(set) Completion check: CSS selector")
    p_ho.add_argument("--selector-state", default="visible",
                      choices=["attached", "detached", "visible", "hidden"],
                      help="(set) Required selector state")
    p_ho.add_argument("--text", default=None, help="(set) Completion check: page text contains")
    p_ho.add_argument("--url-contains", dest="url_contains", default=None, help="(set) Completion check: URL contains")
    p_ho.add_argument("--title-contains", dest="title_contains", default=None,
                      help="(set) Completion check: title contains")
    p_ho.add_argument("--load-state", dest="load_state", default=None,
                      choices=["load", "domcontentloaded", "networkidle"],
                      help="(set) Completion check: page load state")
    p_ho.add_argument("--cookie-name", dest="cookie_name", default=None,
                      help="(set) Completion check: cookie exists (by name)")
    p_ho.add_argument("--cookie-domain-contains", dest="cookie_domain_contains", default=None,
                      help="(set) Optional cookie domain substring filter")
    p_ho.add_argument("--local-storage-key", dest="local_storage_key", default=None,
                      help="(set) Completion check: localStorage key exists")
    p_ho.add_argument("--session-storage-key", dest="session_storage_key", default=None,
                      help="(set) Completion check: sessionStorage key exists")
    p_ho.add_argument("--match", choices=["all", "any"], default="all",
                      help="(set) Combine multiple checks with all=AND (default) or any=OR")
    p_ho.add_argument("--timeout-ms", type=int, default=0,
                      help="(wait) Max time to wait for completion (ms). Default for wait: 300000")
    p_ho.set_defaults(func=cmd_handoff)

    # -- live-url --
    p_lu = subparsers.add_parser("live-url", help="Get live debug URL")
    p_lu.add_argument("--session-id", default=None, help="Session ID")
    p_lu.add_argument("--workspace", default=None, help="Use the active session from a workspace")
    p_lu.set_defaults(func=cmd_live_url)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
        except SystemExit:
            raise
        except Exception as e:
            cmd = getattr(args, "command", "command")
            output_error(f"{cmd} failed: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
