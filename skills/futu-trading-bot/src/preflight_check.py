#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Preflight checks for Futu Trade Bot Skills.

This module avoids importing business modules so it can detect environment
issues before `futu` SDK import side effects happen.
"""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_FUTU_CONFIG = {
    "host": "127.0.0.1",
    "port": 11111,
    "security_firm": "FUTUSECURITIES",
    "trade_password": "",
    "trade_password_md5": "",
    "default_env": "SIMULATE",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _check(name: str, ok: bool, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"name": name, "ok": ok, "message": message}
    if details:
        item["details"] = details
    return item


def check_python_version() -> Dict[str, Any]:
    version = sys.version_info
    return _check(
        "python_version",
        version >= (3, 10),
        f"Python {version.major}.{version.minor}.{version.micro}",
        {"required": ">=3.10"},
    )


def check_futu_installed() -> Dict[str, Any]:
    ok = importlib.util.find_spec("futu") is not None
    return _check("futu_installed", ok, "futu package is installed" if ok else "futu package is not installed")


def find_config_file() -> Tuple[Optional[Path], List[Path]]:
    root = _project_root()
    candidates = [
        root / "json" / "config.json",
        root / "json" / "config_example.json",
        root / "json" / "config.example.json",
    ]
    for path in candidates:
        if path.exists():
            return path, candidates
    return None, candidates


def check_config_file() -> Tuple[Dict[str, Any], Optional[Path]]:
    config_path, candidates = find_config_file()
    if config_path is None:
        return (
            _check(
                "config_file",
                False,
                "No config file found",
                {"candidates": [str(path) for path in candidates]},
            ),
            None,
        )
    return (
        _check("config_file", True, f"Found config file: {config_path.relative_to(_project_root())}"),
        config_path,
    )


def load_config(config_path: Path) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _check("config_parse", False, f"Config JSON parse failed: {exc}"), None
    except Exception as exc:
        return _check("config_parse", False, f"Config load failed: {exc}"), None
    return _check("config_parse", True, "Config JSON parsed successfully"), config


def check_futu_config(config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    futu_config = dict(DEFAULT_FUTU_CONFIG)
    futu_config.update(config.get("futu_api", {}))

    host = futu_config.get("host")
    port = futu_config.get("port")
    security_firm = futu_config.get("security_firm")

    problems: List[str] = []
    if not isinstance(host, str) or not host.strip():
        problems.append("host is missing or invalid")
    if not isinstance(port, int):
        problems.append("port must be an integer")
    if not isinstance(security_firm, str) or not security_firm.strip():
        problems.append("security_firm is missing or invalid")

    return _check(
        "futu_config",
        not problems,
        "Futu config looks valid" if not problems else "; ".join(problems),
        {"host": host, "port": port, "security_firm": security_firm},
    ), futu_config


def check_password_config(config: Dict[str, Any]) -> Dict[str, Any]:
    futu_config = config.get("futu_api", {})
    has_password = bool(futu_config.get("trade_password")) or bool(futu_config.get("trade_password_md5"))
    return _check(
        "trade_password",
        has_password,
        "Trade password is configured" if has_password else "Trade password is not configured (quote-only use may still work)",
    )


def check_opend_connectivity(host: str, port: int, timeout: float = 1.5) -> Dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return _check("opend_connectivity", True, f"Connected to OpenD at {host}:{port}")
    except Exception as exc:
        return _check("opend_connectivity", False, f"Cannot connect to OpenD at {host}:{port}: {exc}")


def check_futu_log_dir_writable() -> Dict[str, Any]:
    log_dir = Path.home() / ".com.futunn.FutuOpenD" / "Log"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        probe = log_dir / ".preflight_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return _check("futu_log_dir", True, f"Writable log directory: {log_dir}")
    except Exception as exc:
        return _check("futu_log_dir", False, f"Cannot write Futu OpenD log directory: {log_dir}: {exc}")


def detect_sandbox_risk(log_dir_check: Dict[str, Any], opend_check: Dict[str, Any]) -> Dict[str, Any]:
    markers = {
        "container": os.environ.get("CONTAINER_SANDBOX"),
        "sandbox": os.environ.get("SANDBOX"),
        "codex_env": os.environ.get("CODEX_SANDBOX"),
        "openclaw": os.environ.get("OPENCLAW_STATE_DIR"),
    }
    reasons: List[str] = []
    if not log_dir_check["ok"]:
        reasons.append("cannot write ~/.com.futunn.FutuOpenD/Log")
    if markers["openclaw"]:
        reasons.append("running inside an OpenClaw-managed environment")
    if markers["sandbox"] or markers["container"] or markers["codex_env"]:
        reasons.append("sandbox-related environment marker detected")
    if not opend_check["ok"]:
        reasons.append("OpenD is not reachable from the current runtime")

    ok = len(reasons) == 0
    message = "No obvious sandbox restriction detected" if ok else "Potential restricted runtime detected: " + "; ".join(reasons)
    return _check("sandbox_risk", ok, message, {"markers": markers})


def build_suggestions(checks: List[Dict[str, Any]], futu_config: Optional[Dict[str, Any]]) -> List[str]:
    failed = {item["name"] for item in checks if not item["ok"]}
    suggestions: List[str] = []
    if "futu_installed" in failed:
        suggestions.append("Install dependencies first, for example: pip install -e .")
    if "config_file" in failed:
        suggestions.append("Create json/config.json from json/config_example.json and fill in your Futu settings.")
    if "opend_connectivity" in failed and futu_config:
        suggestions.append(f"Make sure Futu OpenD is running and reachable at {futu_config['host']}:{futu_config['port']}.")
    if "futu_log_dir" in failed or "sandbox_risk" in failed:
        suggestions.append("If you are running in OpenClaw/Codex or another restricted sandbox, rerun in host/elevated mode.")
    return suggestions


def run_preflight() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(check_python_version())
    checks.append(check_futu_installed())

    config_file_check, config_path = check_config_file()
    checks.append(config_file_check)

    config: Optional[Dict[str, Any]] = None
    futu_config: Optional[Dict[str, Any]] = None

    if config_path is not None:
        config_parse_check, config = load_config(config_path)
        checks.append(config_parse_check)

    if config is not None:
        futu_config_check, futu_config = check_futu_config(config)
        checks.append(futu_config_check)
        checks.append(check_password_config(config))
        checks.append(check_opend_connectivity(futu_config["host"], futu_config["port"]))
    else:
        checks.append(_check("opend_connectivity", False, "Skipped because config is unavailable"))

    log_dir_check = check_futu_log_dir_writable()
    checks.append(log_dir_check)

    opend_check = next(item for item in checks if item["name"] == "opend_connectivity")
    checks.append(detect_sandbox_risk(log_dir_check, opend_check))

    success = all(item["ok"] for item in checks if item["name"] != "trade_password")
    return {
        "success": success,
        "summary": "Preflight passed" if success else "Preflight failed",
        "checks": checks,
        "suggestions": build_suggestions(checks, futu_config),
    }


def main() -> int:
    result = run_preflight()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
