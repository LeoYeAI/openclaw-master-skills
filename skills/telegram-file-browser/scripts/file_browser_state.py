#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
DEFAULT_RUNTIME_STATE_PATH = DEFAULT_WORKSPACE_ROOT / ".openclaw" / "telegram-file-browser" / "state.json"


def default_workspace_root() -> Path:
    return DEFAULT_WORKSPACE_ROOT


def default_runtime_state_path() -> Path:
    return DEFAULT_RUNTIME_STATE_PATH


def path_label(path: str) -> str:
    p = Path(path).expanduser()
    try:
        return str(p).replace(str(Path.home()), "~", 1)
    except Exception:
        return str(p)


def load_state(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_state(path: str, state: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def init_state(root: str, current: Optional[str] = None) -> Dict[str, Any]:
    current = current or root
    return {
        "root": root,
        "current": current,
        "stack": [],
        "liveMessageId": None,
        "menuVersion": 1,
        "lastCallback": None,
        "lastCallbackAt": None,
        "views": {}
    }


def push_path(state: Dict[str, Any], current: str, new_path: str) -> Dict[str, Any]:
    stack = state.setdefault("stack", [])
    if current:
        stack.append(current)
    state["current"] = new_path
    return state


def pop_path(state: Dict[str, Any]) -> Optional[str]:
    stack = state.setdefault("stack", [])
    if not stack:
        return None
    prev = stack.pop()
    state["current"] = prev
    return prev


def set_live_message_id(state: Dict[str, Any], message_id: Optional[object]) -> Dict[str, Any]:
    state["liveMessageId"] = None if message_id is None else str(message_id)
    return state


def bump_menu_version(state: Dict[str, Any]) -> Dict[str, Any]:
    state["menuVersion"] = int(state.get("menuVersion", 0)) + 1
    return state


def remember_callback(state: Dict[str, Any], callback: str) -> Dict[str, Any]:
    state["lastCallback"] = callback
    state["lastCallbackAt"] = time.time()
    return state


def is_duplicate_callback(state: Dict[str, Any], callback: str, window_seconds: float = 2.0) -> bool:
    last = state.get("lastCallback")
    at = state.get("lastCallbackAt")
    if last != callback or at is None:
        return False
    try:
        return (time.time() - float(at)) < window_seconds
    except Exception:
        return False
