#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import shlex
import signal
import subprocess
import sys
import textwrap
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse


DEFAULT_BROWSER_BIN = "openclaw"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def short_json(value: Any, max_len: int = 220) -> str:
    raw = json.dumps(value, ensure_ascii=False)
    if len(raw) <= max_len:
        return raw
    return raw[: max_len - 3] + "..."


def parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return {}
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    lines = stripped.splitlines()
    for idx in range(len(lines)):
        candidate = "\n".join(lines[idx:]).strip()
        if not candidate:
            continue
        if candidate[0] not in "[{":
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    for pos, ch in enumerate(stripped):
        if ch not in "[{":
            continue
        candidate = stripped[pos:].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("unable to locate JSON payload", stripped, 0)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_if_exists(src_path: Optional[str], dst_path: Path) -> Optional[str]:
    if not src_path:
        return None
    src = Path(src_path).expanduser()
    if not src.exists():
        return src_path
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst_path)
    return str(dst_path)


def resolve_command_prefix(browser_bin: str, browser_cmd: Optional[str]) -> List[str]:
    if browser_cmd:
        parsed = shlex.split(browser_cmd)
        if not parsed:
            raise ValueError("--browser-cmd is empty after parsing")
        return parsed

    if shutil.which(browser_bin):
        return [browser_bin]

    script_file = Path(__file__).resolve()
    repo_src_dir = script_file.parents[3]
    package_json = repo_src_dir / "package.json"
    if package_json.exists() and shutil.which("pnpm"):
        return ["pnpm", "--dir", str(repo_src_dir), "openclaw"]

    raise RuntimeError(
        f"cannot find browser command: '{browser_bin}' not in PATH and pnpm fallback unavailable"
    )


def default_scenario_root() -> Path:
    script_file = Path(__file__).resolve()
    project_root = script_file.parents[4]
    repo_scenario_root = project_root / "demo" / "scenarios"
    if repo_scenario_root.is_dir():
        return repo_scenario_root.resolve()
    skill_root = script_file.parents[1]
    skill_scenario_root = skill_root / "scenarios"
    if skill_scenario_root.is_dir():
        return skill_scenario_root.resolve()
    return repo_scenario_root.resolve()


def default_scenario_registry_path() -> Path:
    return (default_scenario_root() / "registry.json").resolve()


def load_scenario_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"scenario registry not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("scenario registry must be a JSON object")

    raw_scenarios = raw.get("scenarios")
    if not isinstance(raw_scenarios, dict) or not raw_scenarios:
        raise ValueError("scenario registry.scenarios must be a non-empty object")

    resolved: Dict[str, Dict[str, Any]] = {}
    for sid_raw, cfg in raw_scenarios.items():
        sid = str(sid_raw).strip()
        if not sid:
            continue

        rel_path: Optional[str] = None
        if isinstance(cfg, str):
            rel_path = cfg.strip()
            entry_meta: Dict[str, Any] = {}
        elif isinstance(cfg, dict):
            entry_meta = dict(cfg)
            rel_path = str(cfg.get("path") or "").strip()
        else:
            continue

        if not rel_path:
            continue

        candidate = Path(rel_path)
        if not candidate.is_absolute():
            candidate = (path.parent / candidate).resolve()
        else:
            candidate = candidate.resolve()
        resolved[sid] = {
            "path": str(candidate),
            "meta": entry_meta,
        }

    if not resolved:
        raise ValueError("scenario registry has no valid scenario entries")

    default_id = str(raw.get("defaultScenarioId") or "").strip()
    if default_id and default_id not in resolved:
        raise ValueError(f"defaultScenarioId not found in registry: {default_id}")

    return {
        "registryPath": str(path),
        "defaultScenarioId": default_id or None,
        "scenarios": resolved,
    }


def resolve_scenario_input(args: argparse.Namespace) -> Tuple[Path, Dict[str, Any]]:
    scenario_root = default_scenario_root()
    registry_path = (
        Path(str(args.scenario_registry)).expanduser().resolve()
        if isinstance(args.scenario_registry, str) and args.scenario_registry.strip()
        else default_scenario_registry_path()
    )
    allow_direct_path = bool(args.allow_direct_scenario_path)
    force_direct_path = bool(getattr(args, "force_direct_scenario_path", False))
    scenario_id = str(args.scenario_id).strip() if isinstance(args.scenario_id, str) else ""
    direct_path = str(args.scenario).strip() if isinstance(args.scenario, str) else ""

    registry = load_scenario_registry(registry_path)
    registry_scenarios = registry.get("scenarios", {})
    default_id = str(registry.get("defaultScenarioId") or "").strip()

    selected_id = scenario_id
    if not selected_id and not direct_path and default_id:
        selected_id = default_id

    if selected_id:
        selected = registry_scenarios.get(selected_id)
        if not isinstance(selected, dict):
            known = sorted(registry_scenarios.keys())
            raise RuntimeError(
                f"unknown scenario-id: {selected_id}; available={known}"
            )
        scenario_path = Path(str(selected.get("path") or "")).resolve()
        if not path_within(scenario_path, scenario_root):
            raise RuntimeError(
                f"registry scenario path is outside default root: {scenario_path}"
            )
        return scenario_path, {
            "source": "scenario-id",
            "scenarioId": selected_id,
            "registryPath": str(registry_path),
            "allowDirectScenarioPath": allow_direct_path,
            "defaultScenarioId": default_id or None,
        }

    if direct_path:
        if not allow_direct_path:
            raise RuntimeError(
                "已启用场景锁定：请使用 --scenario-id 运行注册场景。"
                "若确需临时直传路径，请显式加 --allow-direct-scenario-path。"
            )
        if not force_direct_path:
            selected = registry_scenarios.get(default_id) if default_id else None
            if isinstance(selected, dict):
                fallback_path = Path(str(selected.get("path") or "")).resolve()
                if not path_within(fallback_path, scenario_root):
                    raise RuntimeError(
                        f"registry default scenario path is outside default root: {fallback_path}"
                    )
                return fallback_path, {
                    "source": "direct-path-fallback-default",
                    "scenarioId": default_id,
                    "registryPath": str(registry_path),
                    "allowDirectScenarioPath": allow_direct_path,
                    "forceDirectScenarioPath": force_direct_path,
                    "requestedScenarioPath": direct_path,
                    "fallbackReason": "direct_path_requires_force",
                    "defaultScenarioId": default_id or None,
                }
            raise RuntimeError(
                "检测到直传场景请求，但未显式确认强制直传。"
                "请改用 --scenario-id；若必须直传路径，请追加 --force-direct-scenario-path。"
            )
        scenario_path = Path(direct_path).expanduser().resolve()
        return scenario_path, {
            "source": "direct-path",
            "scenarioId": None,
            "registryPath": str(registry_path),
            "allowDirectScenarioPath": allow_direct_path,
            "forceDirectScenarioPath": force_direct_path,
            "defaultScenarioId": default_id or None,
        }

    raise RuntimeError(
        "缺少场景选择参数。请传 --scenario-id；若需要临时路径模式，请显式传 --scenario + --allow-direct-scenario-path。"
    )


def path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def parse_scenario_meta(scenario: Dict[str, Any]) -> Dict[str, Any]:
    meta = scenario.get("meta")
    if not isinstance(meta, dict):
        return {}
    return meta


def list_openclaw_browser_processes() -> List[Dict[str, Any]]:
    try:
        proc = subprocess.run(
            ["ps", "-Ao", "pid,command"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return []
    lines = proc.stdout.splitlines()
    out: List[Dict[str, Any]] = []
    for line in lines[1:]:
        row = line.strip()
        if not row:
            continue
        parts = row.split(None, 1)
        if len(parts) < 2:
            continue
        pid_raw, cmd = parts
        if "Google Chrome.app/Contents/MacOS/Google Chrome" not in cmd:
            continue
        if "--user-data-dir=" not in cmd:
            continue
        if ".openclaw/browser/" not in cmd:
            continue
        pid = safe_int(pid_raw, -1)
        if pid <= 0:
            continue
        out.append({"pid": pid, "command": cmd})
    return out


def cleanup_extra_openclaw_browser_processes(
    *,
    keep_pid: Optional[int],
) -> Dict[str, Any]:
    procs = list_openclaw_browser_processes()
    if not procs:
        return {"detected": [], "terminated": [], "errors": []}

    detected = [int(item.get("pid", -1)) for item in procs if safe_int(item.get("pid"), -1) > 0]
    terminated: List[int] = []
    errors: List[str] = []
    for item in procs:
        pid = safe_int(item.get("pid"), -1)
        if pid <= 0:
            continue
        if keep_pid and pid == keep_pid:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            terminated.append(pid)
        except Exception as exc:
            errors.append(f"pid={pid}: {exc}")

    if terminated:
        time.sleep(0.8)
    return {"detected": detected, "terminated": terminated, "errors": errors}


class StepFailure(Exception):
    pass


@dataclass
class BrowserCLI:
    command_prefix: List[str]
    profile: str
    verbose: bool = False

    def run(
        self,
        args: List[str],
        *,
        expect_json: bool = True,
        timeout_sec: int = 30,
        allow_failure: bool = False,
    ) -> Any:
        cmd = [*self.command_prefix, "browser", "--browser-profile", self.profile]
        if expect_json:
            cmd.append("--json")
        cmd.extend(args)

        if self.verbose:
            print(f"[auto-qa] run: {' '.join(cmd)}", file=sys.stderr)

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            check=False,
        )

        if proc.returncode != 0 and not allow_failure:
            detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
            raise RuntimeError(f"command failed: {' '.join(cmd)}; {detail}")

        if not expect_json:
            return proc.stdout.strip()

        text = proc.stdout.strip()
        if not text:
            return {}
        try:
            return parse_json_output(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"command returned non-JSON output: {' '.join(cmd)}; output={text[:300]}"
            ) from exc


def list_browser_tabs(browser: BrowserCLI) -> List[Dict[str, Any]]:
    try:
        payload = browser.run(["tabs"], expect_json=True, timeout_sec=12, allow_failure=True)
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    raw_tabs = payload.get("tabs")
    if not isinstance(raw_tabs, list):
        return []
    return [item for item in raw_tabs if isinstance(item, dict)]


def has_open_tabs(browser: BrowserCLI) -> bool:
    return len(list_browser_tabs(browser)) > 0


def focus_tab_for_visual(browser: BrowserCLI, preferred_target_id: Optional[str] = None) -> Optional[str]:
    candidates: List[str] = []
    if isinstance(preferred_target_id, str) and preferred_target_id.strip():
        candidates.append(preferred_target_id.strip())

    tabs = list_browser_tabs(browser)
    page_tabs = [t for t in tabs if str(t.get("type") or "page").strip().lower() == "page"]
    non_blank = [t for t in page_tabs if not str(t.get("url") or "").strip().lower().startswith("about:blank")]
    ordered = [*non_blank, *[t for t in page_tabs if t not in non_blank]]
    for tab in ordered:
        tid = str(tab.get("targetId") or "").strip()
        if tid and tid not in candidates:
            candidates.append(tid)

    for tid in candidates:
        try:
            browser.run(["focus", tid], expect_json=True, timeout_sec=10)
            return tid
        except Exception:
            continue
    return None


def wait_millis(browser: BrowserCLI, ms: int) -> None:
    if ms <= 0:
        return
    timeout_sec = max(5, int(ms / 1000) + 5)
    try:
        browser.run(["wait", "--time", str(ms)], expect_json=True, timeout_sec=timeout_sec, allow_failure=True)
    except Exception:
        pass


def to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_non_negative_int(value: Any, default: int) -> int:
    parsed = to_int(value, default)
    return parsed if parsed >= 0 else default


def to_pattern_list(value: Any) -> List[str]:
    if isinstance(value, str):
        cleaned = value.strip().lower()
        return [cleaned] if cleaned else []
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip().lower())
    return out


def extract_target_id(payload: Any) -> Optional[str]:
    if not isinstance(payload, dict):
        return None
    raw = payload.get("targetId")
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def is_unknown_ref_error(exc: Exception) -> bool:
    return "unknown ref" in str(exc).lower()


def normalize_hint_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def extract_quoted_fragments(text: str) -> List[str]:
    pairs = [
        ("'", "'"),
        ('"', '"'),
        ("“", "”"),
        ("‘", "’"),
        ("「", "」"),
        ("『", "』"),
    ]
    fragments: List[str] = []
    for left, right in pairs:
        start = 0
        while True:
            begin = text.find(left, start)
            if begin < 0:
                break
            end = text.find(right, begin + len(left))
            if end < 0:
                break
            candidate = text[begin + len(left) : end].strip()
            if candidate:
                fragments.append(candidate)
            start = end + len(right)
    return fragments


def collect_ref_recovery_hints(step: Dict[str, Any]) -> List[str]:
    raw_hints: List[str] = []
    for key in ("refHint", "textHint", "targetText", "name", "text", "value", "expected"):
        value = step.get(key)
        if isinstance(value, str) and value.strip():
            raw_hints.append(value.strip())
    list_hints = step.get("refHints")
    if isinstance(list_hints, list):
        for item in list_hints:
            if isinstance(item, str) and item.strip():
                raw_hints.append(item.strip())
    for text in list(raw_hints):
        raw_hints.extend(extract_quoted_fragments(text))

    out: List[str] = []
    seen: set[str] = set()
    for item in raw_hints:
        norm = normalize_hint_text(item)
        if len(norm) < 2 or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out[:10]


def select_ref_candidate_by_hints(
    refs: Any,
    hints: List[str],
    *,
    action: str,
) -> Optional[Dict[str, Any]]:
    if not isinstance(refs, dict) or not refs or not hints:
        return None

    role_bonus_map = {
        "click": {"link": 3, "button": 3, "menuitem": 2, "tab": 2},
        "type": {"textbox": 4, "searchbox": 4, "combobox": 3},
        "hover": {"link": 2, "button": 2},
        "scroll": {},
    }
    role_bonus = role_bonus_map.get(action, {})
    best: Optional[Dict[str, Any]] = None

    for ref, meta in refs.items():
        if not isinstance(ref, str) or not ref.strip():
            continue
        if not isinstance(meta, dict):
            continue
        name = normalize_hint_text(str(meta.get("name") or ""))
        role = normalize_hint_text(str(meta.get("role") or ""))
        if not name:
            continue
        score = 0
        matched_hint = ""
        for hint in hints:
            if name == hint:
                score = 100
                matched_hint = hint
                break
            if hint in name:
                score = max(score, 80)
                matched_hint = hint
            elif name in hint and len(name) >= 2:
                score = max(score, 60)
                matched_hint = hint
        score += int(role_bonus.get(role, 0))
        if score <= 0:
            continue
        candidate = {
            "ref": ref.strip(),
            "name": str(meta.get("name") or ""),
            "role": role,
            "score": score,
            "matchedHint": matched_hint,
        }
        if best is None or int(candidate["score"]) > int(best["score"]):
            best = candidate

    return best


def recover_unknown_ref_with_snapshot(
    browser: BrowserCLI,
    step: Dict[str, Any],
    *,
    action: str,
    missing_ref: str,
) -> Tuple[Optional[str], Dict[str, Any]]:
    hints = collect_ref_recovery_hints(step)
    recovery: Dict[str, Any] = {
        "triggered": True,
        "reason": "unknown_ref",
        "action": action,
        "originalRef": missing_ref,
        "hints": hints,
    }

    try:
        snapshot = browser.run(
            ["snapshot", "--interactive", "--labels"],
            expect_json=True,
            timeout_sec=30,
            allow_failure=True,
        )
    except Exception as exc:
        recovery["snapshotError"] = str(exc)
        return None, recovery

    recovery["snapshotTargetId"] = extract_target_id(snapshot)
    refs = snapshot.get("refs") if isinstance(snapshot, dict) else None
    if not isinstance(refs, dict) or not refs:
        recovery["snapshotRefsCount"] = 0
        recovery["resolved"] = False
        recovery["failure"] = "snapshot_refs_empty"
        return None, recovery

    recovery["snapshotRefsCount"] = len(refs)
    if missing_ref in refs:
        recovery["resolved"] = True
        recovery["strategy"] = "same_ref_after_fresh_snapshot"
        recovery["resolvedRef"] = missing_ref
        return missing_ref, recovery

    candidate = select_ref_candidate_by_hints(refs, hints, action=action)
    if candidate:
        recovery["resolved"] = True
        recovery["strategy"] = "name_hint_match"
        recovery["resolvedRef"] = candidate.get("ref")
        recovery["matchedName"] = candidate.get("name")
        recovery["matchedHint"] = candidate.get("matchedHint")
        recovery["matchedScore"] = candidate.get("score")
        return str(candidate.get("ref") or ""), recovery

    recovery["resolved"] = False
    recovery["failure"] = "no_candidate_after_fresh_snapshot"
    return None, recovery


def is_trace_already_running_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "trace already running" in text or ("already running" in text and "trace" in text)


def normalize_console_item(item: Any, step_id: str) -> Dict[str, Any]:
    if isinstance(item, dict):
        level = str(item.get("level") or item.get("type") or "info")
        message = str(item.get("message") or item.get("text") or short_json(item))
        timestamp = str(item.get("timestamp") or item.get("time") or now_iso())
    else:
        level = "info"
        message = str(item)
        timestamp = now_iso()
    return {
        "level": level,
        "message": message,
        "timestamp": timestamp,
        "stepId": step_id,
    }


def normalize_error_item(item: Any, step_id: str) -> Dict[str, Any]:
    if isinstance(item, dict):
        message = str(item.get("message") or short_json(item))
        timestamp = str(item.get("timestamp") or now_iso())
        name = item.get("name")
    else:
        message = str(item)
        timestamp = now_iso()
        name = None
    full = f"{name}: {message}" if name else message
    return {
        "level": "error",
        "message": full,
        "timestamp": timestamp,
        "stepId": step_id,
    }


def normalize_request_item(item: Any, step_id: str) -> Dict[str, Any]:
    if isinstance(item, dict):
        status_raw = item.get("status")
        status = int(status_raw) if isinstance(status_raw, (int, float)) else None
        latency_raw = item.get("latencyMs")
        latency = int(latency_raw) if isinstance(latency_raw, (int, float)) else None
        return {
            "url": str(item.get("url") or ""),
            "method": str(item.get("method") or "GET"),
            "status": status,
            "latencyMs": latency,
            "stepId": step_id,
            "timestamp": str(item.get("timestamp") or now_iso()),
            "failureText": item.get("failureText"),
        }
    return {
        "url": "",
        "method": "GET",
        "status": None,
        "latencyMs": None,
        "stepId": step_id,
        "timestamp": now_iso(),
        "failureText": str(item),
    }


def collect_step_evidence(
    browser: BrowserCLI,
    step_id: str,
    seen_console: set[str],
    verbose: bool = False,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    console_out: List[Dict[str, Any]] = []
    network_out: List[Dict[str, Any]] = []

    try:
        console_payload = browser.run(["console"], expect_json=True, timeout_sec=20, allow_failure=True)
        for msg in console_payload.get("messages", []) if isinstance(console_payload, dict) else []:
            fp = hashlib.sha1(
                json.dumps(msg, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            if fp in seen_console:
                continue
            seen_console.add(fp)
            console_out.append(normalize_console_item(msg, step_id))
    except Exception as exc:
        if verbose:
            print(f"[auto-qa] collect console failed: {exc}", file=sys.stderr)

    try:
        errors_payload = browser.run(
            ["errors", "--clear"], expect_json=True, timeout_sec=20, allow_failure=True
        )
        for err in errors_payload.get("errors", []) if isinstance(errors_payload, dict) else []:
            console_out.append(normalize_error_item(err, step_id))
    except Exception as exc:
        if verbose:
            print(f"[auto-qa] collect errors failed: {exc}", file=sys.stderr)

    try:
        requests_payload = browser.run(
            ["requests", "--clear"], expect_json=True, timeout_sec=20, allow_failure=True
        )
        for req in requests_payload.get("requests", []) if isinstance(requests_payload, dict) else []:
            network_out.append(normalize_request_item(req, step_id))
    except Exception as exc:
        if verbose:
            print(f"[auto-qa] collect requests failed: {exc}", file=sys.stderr)

    return console_out, network_out


def capture_screenshot(
    browser: BrowserCLI,
    step: Dict[str, Any],
    step_id: str,
    screenshots_dir: Path,
    label: str,
) -> Optional[str]:
    cmd: List[str] = ["screenshot"]
    if bool(step.get("fullPage", False)):
        cmd.append("--full-page")
    if isinstance(step.get("ref"), str) and step.get("ref"):
        cmd.extend(["--ref", str(step["ref"])])
    if isinstance(step.get("element"), str) and step.get("element"):
        cmd.extend(["--element", str(step["element"])])
    image_type = str(step.get("imageType") or "png").lower()
    if image_type in {"png", "jpeg"}:
        cmd.extend(["--type", image_type])

    result = browser.run(cmd, expect_json=True, timeout_sec=30)
    src_path = result.get("path") if isinstance(result, dict) else None
    ext = ".jpg" if image_type == "jpeg" else ".png"
    dst = screenshots_dir / f"{step_id}-{label}{ext}"
    copied = copy_if_exists(src_path, dst)
    return copied


def run_step(
    browser: BrowserCLI,
    step: Dict[str, Any],
    step_id: str,
    artifact_dir: Path,
    screenshots_dir: Path,
    auto_screenshot: bool,
    visual_config: Optional[Dict[str, Any]] = None,
    attempt_no: int = 1,
) -> Dict[str, Any]:
    action = str(step.get("action") or "").strip()
    expected = step.get("expected")
    target = step.get("target") or step.get("ref") or step.get("url") or ""

    started = now_iso()
    started_ts = datetime.now(timezone.utc)
    status = "passed"
    actual: Any = ""
    screenshot_path: Optional[str] = None
    step_target_id: Optional[str] = None
    extra_artifacts: Dict[str, Any] = {}
    visual = visual_config if isinstance(visual_config, dict) else {}
    visual_enabled = bool(visual.get("enabled", False))
    pre_action_wait_ms = to_non_negative_int(
        step.get("preActionWaitMs"),
        to_non_negative_int(visual.get("preActionWaitMs"), 0),
    )
    post_action_wait_ms = to_non_negative_int(
        step.get("postActionWaitMs"),
        to_non_negative_int(visual.get("postActionWaitMs"), 0),
    )
    highlight_wait_ms = to_non_negative_int(
        step.get("highlightWaitMs"),
        to_non_negative_int(visual.get("highlightWaitMs"), 400),
    )

    try:
        if visual_enabled and pre_action_wait_ms > 0 and action not in {"wait"}:
            wait_millis(browser, pre_action_wait_ms)

        if action == "open":
            url = str(step.get("url") or "").strip()
            if not url:
                raise StepFailure("open action missing url")
            result = browser.run(["open", url], expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(result) or step_target_id
            actual = f"opened {result.get('url') or url}"

        elif action == "navigate":
            url = str(step.get("url") or "").strip()
            if not url:
                raise StepFailure("navigate action missing url")
            result = browser.run(["navigate", url], expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(result) or step_target_id
            actual = f"navigated {result.get('url') or url}"

        elif action == "snapshot":
            cmd = ["snapshot"]
            fmt = str(step.get("format") or "").strip()
            if fmt in {"ai", "aria"}:
                cmd.extend(["--format", fmt])
            if bool(step.get("interactive", False)):
                cmd.append("--interactive")
            if bool(step.get("compact", False)):
                cmd.append("--compact")
            if isinstance(step.get("limit"), int):
                cmd.extend(["--limit", str(step["limit"])])
            if isinstance(step.get("depth"), int):
                cmd.extend(["--depth", str(step["depth"])])
            if bool(step.get("labels", False)):
                cmd.append("--labels")
            if isinstance(step.get("selector"), str) and step.get("selector"):
                cmd.extend(["--selector", str(step["selector"])])

            result = browser.run(cmd, expect_json=True, timeout_sec=30)
            snap_dir = artifact_dir / "snapshots"
            snap_dir.mkdir(parents=True, exist_ok=True)
            snap_path = snap_dir / f"{step_id}-a{attempt_no}.json"
            write_json(snap_path, result)
            extra_artifacts["snapshot"] = str(snap_path)
            actual = f"snapshot captured ({result.get('format', 'unknown')})"

        elif action == "click":
            ref = str(step.get("ref") or "").strip()
            if not ref:
                raise StepFailure("click action missing ref")
            recover_unknown_ref = bool(step.get("recoverUnknownRef", True))
            if visual_enabled and bool(step.get("highlightBeforeClick", visual.get("highlightBeforeClick", True))):
                browser.run(["highlight", ref], expect_json=False, timeout_sec=20, allow_failure=True)
                wait_millis(browser, highlight_wait_ms)
            def build_click_cmd(click_ref: str) -> List[str]:
                cmd: List[str] = ["click", click_ref]
                if bool(step.get("double", False)):
                    cmd.append("--double")
                if isinstance(step.get("button"), str) and step.get("button"):
                    cmd.extend(["--button", str(step["button"])])
                return cmd

            used_ref = ref
            recovery_info: Optional[Dict[str, Any]] = None
            try:
                result = browser.run(build_click_cmd(used_ref), expect_json=True, timeout_sec=30)
            except Exception as exc:
                if not recover_unknown_ref or not is_unknown_ref_error(exc):
                    raise
                recovered_ref, recovery_info = recover_unknown_ref_with_snapshot(
                    browser,
                    step,
                    action="click",
                    missing_ref=used_ref,
                )
                if recovery_info:
                    extra_artifacts["refRecovery"] = recovery_info
                if not recovered_ref:
                    raise StepFailure(
                        f"click failed: unknown ref '{used_ref}' and recovery unresolved"
                    ) from exc
                used_ref = recovered_ref
                if visual_enabled and bool(
                    step.get("highlightBeforeClick", visual.get("highlightBeforeClick", True))
                ):
                    browser.run(["highlight", used_ref], expect_json=False, timeout_sec=20, allow_failure=True)
                    wait_millis(browser, highlight_wait_ms)
                result = browser.run(build_click_cmd(used_ref), expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(result) or step_target_id
            if recovery_info and used_ref != ref:
                actual = f"clicked ref={used_ref} (recovered_from={ref})"
            else:
                actual = f"clicked ref={used_ref}"

        elif action == "type":
            ref = str(step.get("ref") or "").strip()
            text = str(step.get("text") or "")
            if not ref:
                raise StepFailure("type action missing ref")
            if visual_enabled and bool(step.get("highlightBeforeType", visual.get("highlightBeforeType", True))):
                browser.run(["highlight", ref], expect_json=False, timeout_sec=20, allow_failure=True)
                wait_millis(browser, highlight_wait_ms)
            cmd = ["type", ref, text]
            if bool(step.get("submit", False)):
                cmd.append("--submit")
            if bool(step.get("slowly", False)):
                cmd.append("--slowly")
            result = browser.run(cmd, expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(result) or step_target_id
            actual = f"typed ref={ref}"

        elif action == "press":
            key = str(step.get("key") or "").strip()
            if not key:
                raise StepFailure("press action missing key")
            result = browser.run(["press", key], expect_json=True, timeout_sec=20)
            step_target_id = extract_target_id(result) or step_target_id
            actual = f"pressed key={key}"

        elif action in {"back", "go_back"}:
            back_steps = max(1, to_int(step.get("steps"), 1))
            back_wait_ms = to_non_negative_int(step.get("waitMs"), 900)
            used_fallback = False
            result: Any = None
            for _ in range(back_steps):
                try:
                    result = browser.run(["back"], expect_json=True, timeout_sec=20)
                except Exception:
                    used_fallback = True
                    result = browser.run(
                        ["evaluate", "--fn", "() => { history.back(); return window.location.href || ''; }"],
                        expect_json=True,
                        timeout_sec=20,
                    )
                wait_millis(browser, back_wait_ms)
            step_target_id = extract_target_id(result) or step_target_id
            current_url = ""
            if isinstance(result, dict):
                current = result.get("current")
                if isinstance(current, dict):
                    current_url = str(current.get("url") or "")
                if not current_url:
                    current_url = str(result.get("url") or result.get("result") or result.get("value") or "")
            fallback_text = " via history.back()" if used_fallback else ""
            actual = f"back x{back_steps} complete{fallback_text} -> {current_url or short_json(result)}"

        elif action == "wait":
            cmd = ["wait"]
            selector = step.get("selector")
            if isinstance(selector, str) and selector.strip():
                cmd.append(selector.strip())
            if isinstance(step.get("timeMs"), int):
                cmd.extend(["--time", str(step["timeMs"])])
            if isinstance(step.get("text"), str) and step.get("text"):
                cmd.extend(["--text", str(step["text"])])
            if isinstance(step.get("textGone"), str) and step.get("textGone"):
                cmd.extend(["--text-gone", str(step["textGone"])])
            if isinstance(step.get("url"), str) and step.get("url"):
                cmd.extend(["--url", str(step["url"])])
            if isinstance(step.get("load"), str) and step.get("load"):
                cmd.extend(["--load", str(step["load"])])
            if isinstance(step.get("fn"), str) and step.get("fn"):
                cmd.extend(["--fn", str(step["fn"])])
            if isinstance(step.get("timeoutMs"), int):
                cmd.extend(["--timeout-ms", str(step["timeoutMs"])])
            result = browser.run(cmd, expect_json=True, timeout_sec=40)
            step_target_id = extract_target_id(result) or step_target_id
            actual = "wait complete"

        elif action == "evaluate":
            fn = str(step.get("fn") or "").strip()
            if not fn:
                raise StepFailure("evaluate action missing fn")
            cmd = ["evaluate", "--fn", fn]
            if isinstance(step.get("ref"), str) and step.get("ref"):
                cmd.extend(["--ref", str(step["ref"])])
            result = browser.run(cmd, expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(result) or step_target_id
            value = result.get("result")
            if "assertEquals" in step and value != step.get("assertEquals"):
                raise StepFailure(
                    f"evaluate assertEquals failed; expected={short_json(step.get('assertEquals'))}, actual={short_json(value)}"
                )
            if "assertContains" in step:
                needle = str(step.get("assertContains"))
                if needle not in str(value):
                    raise StepFailure(
                        f"evaluate assertContains failed; needle={needle}, actual={short_json(value)}"
                    )
            actual = f"evaluate result={short_json(value)}"

        elif action == "hover":
            ref = str(step.get("ref") or "").strip()
            if not ref:
                raise StepFailure("hover action missing ref")
            if visual_enabled and bool(step.get("highlightBeforeHover", True)):
                browser.run(["highlight", ref], expect_json=False, timeout_sec=20, allow_failure=True)
                wait_millis(browser, highlight_wait_ms)
            result = browser.run(["hover", ref], expect_json=True, timeout_sec=20)
            step_target_id = extract_target_id(result) or step_target_id
            actual = f"hovered ref={ref}"

        elif action == "scroll":
            ref = str(step.get("ref") or "").strip()
            if ref:
                if visual_enabled and bool(step.get("highlightBeforeScroll", True)):
                    browser.run(["highlight", ref], expect_json=False, timeout_sec=20, allow_failure=True)
                    wait_millis(browser, highlight_wait_ms)
                result = browser.run(["scrollintoview", ref], expect_json=True, timeout_sec=20)
                step_target_id = extract_target_id(result) or step_target_id
                actual = f"scrolled ref={ref} into view"
            else:
                delta_y = to_int(step.get("deltaY"), 900)
                js = (
                    "() => {"
                    " const before = window.scrollY || 0;"
                    f" window.scrollBy(0, {delta_y});"
                    " const after = window.scrollY || 0;"
                    " return { before, after, moved: after !== before };"
                    " }"
                )
                result = browser.run(["evaluate", "--fn", js], expect_json=True, timeout_sec=25)
                step_target_id = extract_target_id(result) or step_target_id
                payload = result.get("result")
                moved = payload.get("moved") if isinstance(payload, dict) else None
                if "assertEquals" in step and moved != step.get("assertEquals"):
                    raise StepFailure(
                        f"scroll assertEquals failed; expected={short_json(step.get('assertEquals'))}, actual={short_json(moved)}"
                    )
                actual = f"scroll deltaY={delta_y}, moved={short_json(moved)}"

        elif action == "click_link_same_origin":
            include_patterns = to_pattern_list(step.get("includeTextAny"))
            exclude_patterns = to_pattern_list(step.get("excludeTextAny"))
            max_candidates = max(1, to_non_negative_int(step.get("maxCandidates"), 10))
            same_origin_only = bool(step.get("sameOriginOnly", True))

            snapshot = browser.run(
                ["snapshot", "--interactive", "--labels"],
                expect_json=True,
                timeout_sec=30,
            )
            step_target_id = extract_target_id(snapshot) or step_target_id
            refs = snapshot.get("refs") if isinstance(snapshot, dict) else None
            if not isinstance(refs, dict) or not refs:
                raise StepFailure("click_link_same_origin failed: no refs from snapshot")

            candidates: List[Dict[str, Any]] = []
            for ref, meta in refs.items():
                if not isinstance(ref, str) or not ref.strip():
                    continue
                if not isinstance(meta, dict):
                    continue
                role = str(meta.get("role") or "").strip().lower()
                if role != "link":
                    continue
                name = str(meta.get("name") or "").strip()
                name_lower = name.lower()
                if include_patterns and not any(pat in name_lower for pat in include_patterns):
                    continue
                if exclude_patterns and any(pat in name_lower for pat in exclude_patterns):
                    continue
                score = 0
                if include_patterns:
                    score += sum(1 for pat in include_patterns if pat in name_lower)
                if name:
                    score += 1
                candidates.append({"ref": ref.strip(), "name": name, "score": score})

            if not candidates:
                raise StepFailure("click_link_same_origin failed: no link candidate matched filters")
            candidates.sort(key=lambda item: item.get("score", 0), reverse=True)
            candidates = candidates[:max_candidates]

            origin_res = browser.run(
                ["evaluate", "--fn", "() => window.location.origin || ''"],
                expect_json=True,
                timeout_sec=20,
            )
            current_res = browser.run(
                ["evaluate", "--fn", "() => window.location.href || ''"],
                expect_json=True,
                timeout_sec=20,
            )
            current_origin = str(origin_res.get("result") or "").strip()
            current_href = str(current_res.get("result") or "").strip()
            selected: Optional[Dict[str, Any]] = None

            for item in candidates:
                ref = str(item.get("ref") or "").strip()
                href_res = browser.run(
                    ["evaluate", "--ref", ref, "--fn", "(el) => (el && el.href) ? String(el.href) : ''"],
                    expect_json=True,
                    timeout_sec=20,
                    allow_failure=True,
                )
                href = str(href_res.get("result") or "").strip() if isinstance(href_res, dict) else ""
                if not href:
                    continue
                if href == current_href:
                    continue
                if same_origin_only and current_origin and not href.startswith(current_origin):
                    continue
                selected = {"ref": ref, "name": item.get("name"), "href": href}
                break

            if selected is None:
                fallback = candidates[0]
                selected = {
                    "ref": str(fallback.get("ref") or ""),
                    "name": fallback.get("name"),
                    "href": "",
                }

            chosen_ref = str(selected.get("ref") or "").strip()
            if not chosen_ref:
                raise StepFailure("click_link_same_origin failed: selected ref empty")

            target_href = str(selected.get("href") or "").strip()
            if target_href:
                set_ss = (
                    "() => {"
                    " try {"
                    "   sessionStorage.setItem('__autoqa_prev_url', window.location.href || '');"
                    f"   sessionStorage.setItem('__autoqa_target_url', {json.dumps(target_href)});"
                    " } catch (e) {}"
                    " return true;"
                    " }"
                )
                browser.run(
                    ["evaluate", "--fn", set_ss],
                    expect_json=True,
                    timeout_sec=20,
                    allow_failure=True,
                )

            if visual_enabled and bool(step.get("highlightBeforeClick", visual.get("highlightBeforeClick", True))):
                browser.run(["highlight", chosen_ref], expect_json=False, timeout_sec=20, allow_failure=True)
                wait_millis(browser, highlight_wait_ms)

            click_res = browser.run(["click", chosen_ref], expect_json=True, timeout_sec=30)
            step_target_id = extract_target_id(click_res) or step_target_id
            selected_name = str(selected.get("name") or "").strip()
            selected_href = str(selected.get("href") or "").strip()
            extra_artifacts["selectedLink"] = {
                "ref": chosen_ref,
                "name": selected_name,
                "href": selected_href,
                "sameOriginOnly": same_origin_only,
            }
            actual = f"clicked link ref={chosen_ref}, name={selected_name or '-'}, href={selected_href or '-'}"

        elif action == "assert_url_contains":
            needle = str(step.get("value") or "").strip()
            if not needle:
                raise StepFailure("assert_url_contains missing value")
            result = browser.run(
                ["evaluate", "--fn", "() => window.location.href"],
                expect_json=True,
                timeout_sec=20,
            )
            step_target_id = extract_target_id(result) or step_target_id
            href = str(result.get("result") or "")
            if needle not in href:
                raise StepFailure(f"url should contain '{needle}', actual='{href}'")
            actual = f"url={href}"

        elif action == "assert_text_contains":
            needle = str(step.get("value") or "").strip()
            if not needle:
                raise StepFailure("assert_text_contains missing value")
            result = browser.run(
                [
                    "evaluate",
                    "--fn",
                    "() => document.body ? document.body.innerText : ''",
                ],
                expect_json=True,
                timeout_sec=20,
            )
            step_target_id = extract_target_id(result) or step_target_id
            body_text = str(result.get("result") or "")
            if needle not in body_text:
                raise StepFailure(f"page text does not include '{needle}'")
            actual = f"text includes '{needle}'"

        elif action == "screenshot":
            screenshot_path = capture_screenshot(
                browser, step, step_id, screenshots_dir, f"a{attempt_no}-manual"
            )
            actual = f"screenshot={screenshot_path or 'n/a'}"

        elif action == "noop":
            actual = str(step.get("note") or "noop")

        else:
            raise StepFailure(f"unsupported action: {action}")

    except Exception as exc:
        status = "failed"
        actual = str(exc)

    if status == "passed" and visual_enabled and post_action_wait_ms > 0 and action not in {"wait"}:
        wait_millis(browser, post_action_wait_ms)

    if action != "screenshot":
        should_capture = status == "failed" or bool(step.get("captureScreenshot", auto_screenshot))
        if should_capture:
            try:
                shot = capture_screenshot(browser, step, step_id, screenshots_dir, f"a{attempt_no}-{status}")
                if shot:
                    screenshot_path = shot
            except Exception as exc:
                extra_artifacts["screenshotError"] = str(exc)

    ended = now_iso()
    duration_ms = int((datetime.now(timezone.utc) - started_ts).total_seconds() * 1000)
    result: Dict[str, Any] = {
        "stepId": step_id,
        "action": action,
        "target": target,
        "expected": expected,
        "actual": actual,
        "status": status,
        "startedAt": started,
        "endedAt": ended,
        "durationMs": duration_ms,
    }
    if screenshot_path:
        result["screenshot"] = screenshot_path
    if step_target_id:
        result["targetId"] = step_target_id
    if extra_artifacts:
        result["artifacts"] = extra_artifacts
    result["attempt"] = attempt_no
    return result


def run_step_with_retries(
    browser: BrowserCLI,
    step: Dict[str, Any],
    step_id: str,
    artifact_dir: Path,
    screenshots_dir: Path,
    auto_screenshot: bool,
    visual_config: Optional[Dict[str, Any]],
    max_retries: int,
    retry_wait_ms: int,
) -> Dict[str, Any]:
    total_attempts = max(1, max_retries + 1)
    attempts: List[Dict[str, Any]] = []
    final_result: Optional[Dict[str, Any]] = None

    for attempt_no in range(1, total_attempts + 1):
        attempt_result = run_step(
            browser=browser,
            step=step,
            step_id=step_id,
            artifact_dir=artifact_dir,
            screenshots_dir=screenshots_dir,
            auto_screenshot=auto_screenshot,
            visual_config=visual_config,
            attempt_no=attempt_no,
        )
        attempts.append(attempt_result)
        final_result = attempt_result

        if attempt_result.get("status") == "passed":
            break

        if attempt_no < total_attempts and retry_wait_ms > 0:
            try:
                browser.run(
                    ["wait", "--time", str(retry_wait_ms)],
                    expect_json=True,
                    timeout_sec=max(5, int(retry_wait_ms / 1000) + 5),
                    allow_failure=True,
                )
            except Exception:
                pass

    if final_result is None:
        raise RuntimeError(f"step {step_id} produced no attempt result")

    if len(attempts) == 1:
        return final_result

    merged = dict(final_result)
    merged["attempts"] = attempts
    merged["attemptCount"] = len(attempts)
    merged["retriesUsed"] = max(0, len(attempts) - 1)
    return merged


def infer_root_causes(
    failed_steps: List[Dict[str, Any]],
    console_entries: List[Dict[str, Any]],
    network_entries: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    causes: List[Dict[str, Any]] = []

    failed_text = " ".join(str(s.get("actual", "")).lower() for s in failed_steps)
    console_text = " ".join(str(c.get("message", "")).lower() for c in console_entries)

    server_errors = [r for r in network_entries if isinstance(r.get("status"), int) and r["status"] >= 500]
    client_errors = [
        r
        for r in network_entries
        if isinstance(r.get("status"), int) and 400 <= int(r["status"]) < 500
    ]

    if server_errors:
        causes.append(
            {
                "title": "后端接口异常（5xx）导致前端流程中断",
                "confidence": 0.88,
                "evidence": f"5xx requests={len(server_errors)}",
            }
        )

    if "typeerror" in console_text or "referenceerror" in console_text:
        causes.append(
            {
                "title": "前端运行时异常（TypeError/ReferenceError）",
                "confidence": 0.83,
                "evidence": "console 中出现运行时错误关键字",
            }
        )

    if "ref" in failed_text or "not found" in failed_text or "timeout" in failed_text:
        causes.append(
            {
                "title": "页面元素定位不稳定（ref 漂移/元素状态未就绪）",
                "confidence": 0.78,
                "evidence": "失败信息包含 ref/not found/timeout",
            }
        )

    if "url should contain" in failed_text:
        causes.append(
            {
                "title": "路由跳转或状态机未达到预期",
                "confidence": 0.74,
                "evidence": "URL 断言失败",
            }
        )

    if client_errors and not causes:
        causes.append(
            {
                "title": "请求参数或权限问题（4xx）",
                "confidence": 0.7,
                "evidence": f"4xx requests={len(client_errors)}",
            }
        )

    if not causes:
        causes.append(
            {
                "title": "组合因素导致失败（需结合 trace 复盘）",
                "confidence": 0.55,
                "evidence": "当前证据不足以单点归因",
            }
        )

    return causes[:3]


def build_fix_plan(
    run_id: str,
    failed_steps: List[Dict[str, Any]],
    gate_violations: List[Dict[str, Any]],
    console_entries: List[Dict[str, Any]],
    network_entries: List[Dict[str, Any]],
    trace_path: Optional[str],
) -> Dict[str, Any]:
    if not failed_steps and not gate_violations:
        return {
            "runId": run_id,
            "generatedAt": now_iso(),
            "status": "no-fix-needed",
            "summary": "All scenario steps and gate checks passed. No blocking issue detected.",
            "issueSummary": [],
            "rootCauses": [],
            "checkDirections": [],
            "changeDirections": [],
            "acceptanceCriteria": [
                "保持当前场景为回归基线，后续改动后必须重复通过。",
                "若业务流程变更，及时更新 scenario 断言与步骤。",
            ],
            "rollbackConditions": [],
            "evidence": {
                "failedSteps": [],
                "gateViolations": [],
                "consoleCount": len(console_entries),
                "networkCount": len(network_entries),
                "trace": trace_path,
            },
        }

    issues = [
        {
            "stepId": step.get("stepId"),
            "action": step.get("action"),
            "expected": step.get("expected"),
            "actual": step.get("actual"),
            "severity": step.get("severity") or step.get("failureClassification", {}).get("category"),
            "screenshot": step.get("screenshot"),
        }
        for step in failed_steps
    ]
    issues.extend(
        [
            {
                "stepId": item.get("stepId"),
                "action": f"gate:{item.get('gate')}",
                "expected": "门禁规则通过",
                "actual": item.get("message"),
                "severity": item.get("severity"),
                "screenshot": None,
                "evidence": item.get("evidence"),
            }
            for item in gate_violations
        ]
    )

    root_input = list(failed_steps)
    if not root_input:
        root_input = [
            {
                "stepId": item.get("stepId"),
                "action": f"gate:{item.get('gate')}",
                "actual": item.get("message"),
            }
            for item in gate_violations
        ]
    root_causes = infer_root_causes(root_input, console_entries, network_entries)

    check_directions = [
        "按失败 stepId 对照 trace 回放，确认实际 DOM 与交互顺序。",
        "核查失败步骤前后 5 秒内 console error 与 network 异常是否同源。",
        "确认 ref 对应元素在交互时刻是否可见、可点击、未被遮挡。",
        "对照 gateViolations 检查同域资源与关键 API 是否存在 4xx/5xx。",
    ]

    change_directions = [
        "优先修复高置信根因（按 fix_plan.rootCauses 顺序）。",
        "为关键按钮增加状态兜底（禁用态提示、失败后重试或降级跳转）。",
        "补充针对失败路径的自动回归步骤，避免回归遗漏。",
    ]

    acceptance = [
        "失败步骤对应场景重新执行通过。",
        "相关步骤无新增 console error。",
        "相关请求无新增 5xx/关键 4xx。",
    ]

    rollback = [
        "修复后失败率上升或出现新的阻断错误时回滚。",
        "关键业务路径（P0）任一项失败即触发回滚评估。",
    ]

    return {
        "runId": run_id,
        "generatedAt": now_iso(),
        "issueSummary": issues,
        "rootCauses": root_causes,
        "checkDirections": check_directions,
        "changeDirections": change_directions,
        "acceptanceCriteria": acceptance,
        "rollbackConditions": rollback,
        "evidence": {
            "failedSteps": [step.get("stepId") for step in failed_steps],
            "gateViolations": gate_violations,
            "consoleCount": len(console_entries),
            "networkCount": len(network_entries),
            "trace": trace_path,
        },
    }


def build_next_window_prompt(
    fix_plan: Dict[str, Any],
    artifact_dir: Path,
    report_dir: Path,
) -> str:
    issues = fix_plan.get("issueSummary", [])
    root_causes = fix_plan.get("rootCauses", [])
    first_issue = issues[0] if issues else {}

    if not issues:
        return textwrap.dedent(
            f"""
            本轮 AutoQA 未发现阻断失败（步骤与门禁断言均通过）。

            建议下一步：
            1) 将当前场景作为回归基线保留。
            2) 新增一个“故意失败”场景验证告警与修复链路。
            3) 若确认进入修复阶段，请先指定新失败样例并重新执行。

            证据位置：
            - steps: {artifact_dir / 'steps.json'}
            - console: {artifact_dir / 'console.json'}
            - network: {artifact_dir / 'network.json'}
            - screenshots: {artifact_dir / 'screenshots'}
            """
        ).strip() + "\n"

    lines: List[str] = []
    lines.append("问题：")
    lines.append(str(first_issue.get("actual") or "存在失败步骤，请优先处理阻断项。"))
    lines.append("")
    lines.append("证据位置：")
    lines.append(f"- steps: {artifact_dir / 'steps.json'}")
    lines.append(f"- console: {artifact_dir / 'console.json'}")
    lines.append(f"- network: {artifact_dir / 'network.json'}")
    lines.append(f"- screenshots: {artifact_dir / 'screenshots'}")
    lines.append(f"- trace: {artifact_dir / 'trace.zip'}")
    lines.append("")
    lines.append("高概率原因（按优先级）：")
    for idx, item in enumerate(root_causes, start=1):
        lines.append(
            f"{idx}) {item.get('title')}（置信度 {item.get('confidence', 0)}，证据：{item.get('evidence', '-') }）"
        )

    lines.append("")
    lines.append("请按以下顺序执行：")
    for idx, item in enumerate(fix_plan.get("checkDirections", []), start=1):
        lines.append(f"{idx}) {item}")
    base = len(fix_plan.get("checkDirections", []))
    for jdx, item in enumerate(fix_plan.get("changeDirections", []), start=1):
        lines.append(f"{base + jdx}) {item}")

    lines.append("")
    lines.append("验收标准：")
    for item in fix_plan.get("acceptanceCriteria", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("完成修复后，请重新运行本脚本并覆盖生成最新报告：")
    lines.append(f"- report dir: {report_dir}")
    return "\n".join(lines).strip() + "\n"


def build_standby_prompt() -> str:
    return textwrap.dedent(
        """
        已完成自动诊断并生成修复任务包。
        若您确认，请回复“开始修复”。
        系统将自动执行最多3轮：修改 -> 回归 -> 报告更新。
        """
    ).strip() + "\n"


def build_report_html(report: Dict[str, Any]) -> str:
    summary = report.get("summary", {})
    steps = report.get("steps", [])
    gate_violations = report.get("gateViolations", [])
    blocking_issues = summary.get("blockingIssues", [])

    step_rows = []
    for step in steps:
        status = str(step.get("status") or "")
        cls = "ok" if status == "passed" else "fail"
        failure_cls = ""
        if status != "passed":
            category = step.get("failureClassification", {}).get("category")
            if category:
                failure_cls = f"{category}"
        attempt_count = step.get("attemptCount") or 1
        step_rows.append(
            "<tr>"
            f"<td>{html.escape(str(step.get('stepId', '')))}</td>"
            f"<td>{html.escape(str(step.get('action', '')))}</td>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(str(attempt_count))}</td>"
            f"<td>{html.escape(str(failure_cls))}</td>"
            f"<td>{html.escape(str(step.get('expected', '')))}</td>"
            f"<td class=\"{cls}\">{html.escape(str(step.get('actual', '')))}</td>"
            "</tr>"
        )

    gate_rows = []
    for item in gate_violations:
        severity = str(item.get("severity") or "").lower()
        occurrences = max(1, safe_int(item.get("occurrences"), 1))
        message = str(item.get("message", ""))
        if occurrences > 1:
            message = f"{message} (x{occurrences})"
        gate_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('id', '')))}</td>"
            f"<td>{html.escape(str(item.get('gate', '')))}</td>"
            f"<td><span class=\"sev sev-{html.escape(severity)}\">{html.escape(str(item.get('severity', '')))}</span></td>"
            f"<td>{html.escape(str(item.get('stepId', '')))}</td>"
            f"<td>{html.escape(message)}</td>"
            "</tr>"
        )

    blocking_rows = []
    for item in blocking_issues:
        blocking_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('stepId', '')))}</td>"
            f"<td>{html.escape(str(item.get('action', '')))}</td>"
            f"<td>{html.escape(str(item.get('severity', '')))}</td>"
            f"<td>{html.escape(str(item.get('reason', '')))}</td>"
            "</tr>"
        )

    release_decision = str(summary.get("releaseDecision", "NO_GO"))
    go_no_go = str(summary.get("goNoGo", "NO-GO"))

    risk_raw = str(summary.get("riskLevel", "high")).lower()
    risk_level = risk_raw if risk_raw in {"low", "medium", "high"} else "high"

    counts = summary.get("gateViolationCountsBySeverity", {})
    blocker_count = safe_int(counts.get("blocker"), 0)
    critical_count = safe_int(counts.get("critical"), 0)
    major_count = safe_int(counts.get("major"), 0)

    pass_rate = safe_float(summary.get("passRate"), 0.0)
    pass_width = max(0.0, min(100.0, pass_rate))

    review_status_raw = str(summary.get("reviewStatus", "consistent")).strip().lower()
    review_status = review_status_raw if review_status_raw in {"consistent", "needs_inspection"} else "consistent"
    review_conclusion = str(
        summary.get("reviewConclusion")
        or ("复核需进一步检验" if review_status == "needs_inspection" else "复核一致")
    )
    review_findings_raw = summary.get("reviewFindings")
    review_findings: List[str] = []
    if isinstance(review_findings_raw, list):
        for item in review_findings_raw:
            text = str(item).strip()
            if text:
                review_findings.append(text)
    review_mode = str(summary.get("reviewMode", "analysis_only")).strip().lower()
    review_mismatch_count = max(0, safe_int(summary.get("reviewMismatchCount"), 0))
    if review_mode == "analysis_plus_showcase":
        review_scope_text = f"复核范围：关键链路复跑校验；差异项 {review_mismatch_count} 条。"
    else:
        review_scope_text = "复核范围：主执行一致性检查。"

    failure_breakdown = summary.get("failureBreakdown", {})
    env_failed = safe_int(failure_breakdown.get("environment"), 0)
    product_failed = safe_int(failure_breakdown.get("product"), 0)
    unknown_failed = safe_int(failure_breakdown.get("unknown"), 0)
    coverage = summary.get("coverage", {})
    step_coverage_rate = safe_float(coverage.get("stepCoverageRate"), 0.0)
    return_edge_coverage_rate = safe_float(coverage.get("returnEdgeCoverageRate"), 100.0)
    return_edge_pass_rate = safe_float(coverage.get("returnEdgePassRate"), 100.0)
    planned_return_edges = max(0, safe_int(coverage.get("plannedReturnEdges"), 0))
    executed_return_edges = max(0, safe_int(coverage.get("executedReturnEdges"), 0))
    planned_max_depth = max(1, safe_int(coverage.get("plannedMaxDepth"), 1))
    executed_max_depth = max(1, safe_int(coverage.get("executedMaxDepth"), 1))

    decision_badge_cls = "go"
    if go_no_go == "NO-GO":
        decision_badge_cls = "nogo"
    elif go_no_go == "CONDITIONAL-GO":
        decision_badge_cls = "cond"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>AutoQA Report - {html.escape(str(report.get("runId", "")))}</title>
<style>
:root {{
  --bg: #f5f7fb;
  --panel: #ffffff;
  --text: #132033;
  --muted: #5e6a7d;
  --line: #dde3ee;
  --good: #0e8f59;
  --warn: #b07500;
  --bad: #b42318;
  --hero-start: #0b203f;
  --hero-end: #1a4f91;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: radial-gradient(circle at 15% 20%, #dce9ff 0%, #f5f7fb 55%); color: var(--text); font-family: "Avenir Next", "PingFang SC", "Noto Sans SC", sans-serif; }}
.page {{ max-width: 1240px; margin: 24px auto 40px; padding: 0 16px; }}
.hero {{ border-radius: 16px; padding: 20px 24px; color: #fff; background: linear-gradient(120deg, var(--hero-start), var(--hero-end)); box-shadow: 0 14px 36px rgba(9, 25, 46, 0.24); }}
.hero h1 {{ margin: 0; font-size: 30px; letter-spacing: 0.2px; }}
.hero .meta {{ margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.7; }}
.panel {{ border: 1px solid var(--line); border-radius: 14px; background: var(--panel); margin-top: 16px; padding: 16px; box-shadow: 0 8px 20px rgba(15, 33, 59, 0.08); }}
.panel h2 {{ margin: 0 0 12px; font-size: 18px; }}
.kv {{ display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: center; margin-bottom: 10px; }}
.grid {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 10px; }}
.card {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: linear-gradient(180deg, #fff, #f9fbff); }}
.card .label {{ font-size: 12px; color: var(--muted); }}
.card .value {{ margin-top: 7px; font-weight: 700; font-size: 24px; }}
.badge {{ display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.badge.go {{ background: #dff8ec; color: var(--good); }}
.badge.cond {{ background: #fff3d6; color: var(--warn); }}
.badge.nogo {{ background: #ffe3e0; color: var(--bad); }}
.badge.risk-low {{ background: #dff8ec; color: var(--good); }}
.badge.risk-medium {{ background: #fff3d6; color: var(--warn); }}
.badge.risk-high {{ background: #ffe3e0; color: var(--bad); }}
.badge.review-consistent {{ background: #dff8ec; color: var(--good); }}
.badge.review-needs_inspection {{ background: #ffe3e0; color: var(--bad); }}
.progress {{ width: 100%; height: 10px; border-radius: 999px; background: #e9eef7; overflow: hidden; margin-top: 10px; }}
.progress > span {{ display: block; height: 100%; width: {pass_width}%; background: linear-gradient(90deg, #15b36d, #23cf8a); }}
.caption {{ margin-top: 6px; font-size: 12px; color: var(--muted); }}
.list {{ margin: 0; padding-left: 20px; }}
.list li {{ margin: 6px 0; }}
.table {{ width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden; }}
.table th, .table td {{ border: 1px solid var(--line); padding: 9px 10px; font-size: 13px; vertical-align: top; }}
.table th {{ background: #eef3fb; color: #25344b; text-align: left; }}
.table tr:nth-child(even) td {{ background: #fbfdff; }}
.ok {{ color: var(--good); font-weight: 600; }}
.fail {{ color: var(--bad); font-weight: 600; }}
.sev {{ display: inline-block; border-radius: 10px; padding: 2px 8px; font-size: 12px; }}
.sev-blocker {{ background: #ffe3e0; color: var(--bad); }}
.sev-critical {{ background: #ffdbe3; color: #9f1239; }}
.sev-major {{ background: #fff3d6; color: var(--warn); }}
.sev-minor {{ background: #eceff4; color: #4a5568; }}
.hint {{ color: var(--muted); font-size: 13px; margin-bottom: 8px; }}
@media (max-width: 980px) {{
  .grid {{ grid-template-columns: repeat(2, minmax(120px, 1fr)); }}
}}
</style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>AutoQA 测试报告</h1>
      <div class="meta">
        runId: {html.escape(str(report.get("runId", "")))}<br/>
        scenario: {html.escape(str(report.get("scenario", "")))}<br/>
        generatedAt: {html.escape(str(report.get("generatedAt", "")))}
      </div>
    </section>

    <section class="panel">
      <h2>执行结论</h2>
      <div class="kv">
        <span class="badge {decision_badge_cls}">{html.escape(go_no_go)}</span>
        <span>发布建议：<strong>{html.escape(release_decision)}</strong></span>
        <span>风险等级：<span class="badge risk-{html.escape(risk_level)}">{html.escape(risk_level.upper())}</span></span>
      </div>
      <div class="progress"><span></span></div>
      <div class="caption">步骤通过率：{pass_rate}%（门禁阈值基于场景 gates.minPassRate）</div>
      <div class="grid" style="margin-top:12px;">
        <div class="card"><div class="label">总步骤</div><div class="value">{summary.get('totalSteps', 0)}</div></div>
        <div class="card"><div class="label">通过</div><div class="value">{summary.get('passedSteps', 0)}</div></div>
        <div class="card"><div class="label">失败</div><div class="value">{summary.get('failedSteps', 0)}</div></div>
        <div class="card"><div class="label">门禁违规</div><div class="value">{summary.get('gateViolations', 0)}</div></div>
        <div class="card"><div class="label">执行步通过率</div><div class="value">{pass_rate}%</div></div>
      </div>
    </section>

    <section class="panel">
      <h2>复核结论</h2>
      <div class="kv">
        <span class="badge review-{html.escape(review_status)}">{html.escape(review_conclusion)}</span>
      </div>
      <div class="hint">{html.escape(review_scope_text)}</div>
      {'<ul class="list">' + ''.join(f'<li>{html.escape(str(item))}</li>' for item in review_findings) + '</ul>' if review_findings else '<div class="hint">关键结论与证据链一致，当前未发现需进一步检验项。</div>'}
    </section>

    <section class="panel">
      <h2>风险拆解</h2>
      <div class="grid">
        <div class="card"><div class="label">Blocker</div><div class="value">{blocker_count}</div></div>
        <div class="card"><div class="label">Critical</div><div class="value">{critical_count}</div></div>
        <div class="card"><div class="label">Major</div><div class="value">{major_count}</div></div>
        <div class="card"><div class="label">环境失败</div><div class="value">{env_failed}</div></div>
        <div class="card"><div class="label">产品失败</div><div class="value">{product_failed}</div></div>
      </div>
      <div class="caption">未知分类失败：{unknown_failed}</div>
    </section>

    <section class="panel">
      <h2>覆盖指标</h2>
      <div class="grid">
        <div class="card"><div class="label">步骤覆盖率</div><div class="value">{step_coverage_rate}%</div></div>
        <div class="card"><div class="label">返回边覆盖率</div><div class="value">{return_edge_coverage_rate}%</div></div>
        <div class="card"><div class="label">返回边通过率</div><div class="value">{return_edge_pass_rate}%</div></div>
        <div class="card"><div class="label">返回边（计划/执行）</div><div class="value">{planned_return_edges}/{executed_return_edges}</div></div>
        <div class="card"><div class="label">深度覆盖（计划/执行）</div><div class="value">{planned_max_depth}/{executed_max_depth}</div></div>
      </div>
    </section>

    <section class="panel">
      <h2>发布门禁理由</h2>
      <ul class="list">
        {''.join(f'<li>{html.escape(str(r))}</li>' for r in summary.get('releaseDecisionReasons', []) or ['无'])}
      </ul>
    </section>

    <section class="panel">
      <h2>阻断项</h2>
      <table class="table">
        <thead>
          <tr><th>stepId</th><th>action</th><th>severity</th><th>reason</th></tr>
        </thead>
        <tbody>
          {''.join(blocking_rows) if blocking_rows else '<tr><td colspan="4">无阻断项</td></tr>'}
        </tbody>
      </table>
    </section>

    <section class="panel">
      <h2>门禁违规清单</h2>
      <div class="hint">默认规则：console error、同域 network 4xx/5xx 计入门禁；可在 scenario.gates 覆盖。</div>
      <table class="table">
        <thead>
          <tr><th>id</th><th>gate</th><th>severity</th><th>stepId</th><th>message</th></tr>
        </thead>
        <tbody>
          {''.join(gate_rows) if gate_rows else '<tr><td colspan="5">无门禁违规</td></tr>'}
        </tbody>
      </table>
    </section>

    <section class="panel">
      <h2>步骤明细</h2>
      <table class="table">
        <thead>
          <tr><th>stepId</th><th>action</th><th>status</th><th>attempts</th><th>failureType</th><th>expected</th><th>actual</th></tr>
        </thead>
        <tbody>
          {''.join(step_rows) if step_rows else '<tr><td colspan="7">无步骤数据</td></tr>'}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


_SCENARIO_VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")


def _render_scenario_value(value: Any, variables: Dict[str, str]) -> Any:
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            if key in variables:
                return str(variables[key])
            return match.group(0)

        return _SCENARIO_VAR_PATTERN.sub(repl, value)
    if isinstance(value, list):
        return [_render_scenario_value(item, variables) for item in value]
    if isinstance(value, dict):
        return {k: _render_scenario_value(v, variables) for k, v in value.items()}
    return value


def parse_scenario_var_overrides(raw_items: Any) -> Dict[str, str]:
    if not isinstance(raw_items, list):
        return {}
    out: Dict[str, str] = {}
    for raw in raw_items:
        if not isinstance(raw, str):
            continue
        text = raw.strip()
        if not text:
            continue
        if "=" not in text:
            raise ValueError(f"invalid --scenario-var: {text}; expected key=value")
        key, value = text.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"invalid --scenario-var key in: {text}")
        out[key] = value.strip()
    return out


_KNOWN_ACTIONS = frozenset([
    "open", "navigate", "snapshot", "click", "type", "press", "back",
    "wait", "evaluate", "hover", "scroll", "click_link_same_origin",
    "assert_url_contains", "assert_text_contains", "screenshot", "noop",
])


def _validate_scenario_steps(steps: List[Dict[str, Any]], path: Path) -> None:
    """Pre-flight check: catch common errors before execution starts."""
    errors: List[str] = []
    for idx, step in enumerate(steps):
        label = f"step[{idx}]"
        if not isinstance(step, dict):
            errors.append(f"{label}: must be a JSON object, got {type(step).__name__}")
            continue
        action = step.get("action")
        if not isinstance(action, str) or not action.strip():
            errors.append(f"{label}: missing or empty 'action' field")
        elif action.strip() not in _KNOWN_ACTIONS:
            errors.append(
                f"{label}: unknown action '{action.strip()}' "
                f"(supported: {', '.join(sorted(_KNOWN_ACTIONS))})"
            )
        action_str = (action or "").strip() if isinstance(action, str) else ""
        if action_str in ("open", "navigate"):
            url = step.get("url")
            if not isinstance(url, str) or not url.strip():
                errors.append(f"{label} ({action_str}): missing 'url'")
        elif action_str in ("click", "hover", "type"):
            ref = step.get("ref")
            if not isinstance(ref, str) or not ref.strip():
                errors.append(f"{label} ({action_str}): missing 'ref'")
        elif action_str in ("assert_url_contains", "assert_text_contains"):
            val = step.get("value")
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{label} ({action_str}): missing 'value'")
    if errors:
        header = f"scenario validation failed ({path.name}, {len(errors)} error(s)):"
        raise ValueError(header + "\n  - " + "\n  - ".join(errors))


def load_scenario(path: Path, cli_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"scenario not found: {path}")
    try:
        raw_text = path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"scenario JSON syntax error in {path.name}: {exc.msg} "
            f"(line {exc.lineno}, col {exc.colno})"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("scenario must be a JSON object")
    scenario_vars_raw = data.get("variables")
    scenario_vars: Dict[str, str] = {}
    if isinstance(scenario_vars_raw, dict):
        for key, value in scenario_vars_raw.items():
            if not isinstance(key, str):
                continue
            normalized_key = key.strip()
            if not normalized_key:
                continue
            scenario_vars[normalized_key] = str(value)
    if isinstance(cli_variables, dict):
        for key, value in cli_variables.items():
            scenario_vars[str(key)] = str(value)
    if scenario_vars:
        data = _render_scenario_value(data, scenario_vars)
        data["resolvedVariables"] = scenario_vars
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("scenario.steps must be a non-empty array")
    _validate_scenario_steps(steps, path)
    return data


def ensure_step_id(step: Dict[str, Any], idx: int) -> str:
    sid = step.get("id")
    if isinstance(sid, str) and sid.strip():
        return sid.strip()
    return f"step-{idx:03d}"


def safe_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def safe_float(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


def validate_scenario_access(
    *,
    scenario_path: Path,
    scenario: Dict[str, Any],
    allow_external: bool,
    allow_legacy: bool,
) -> Dict[str, Any]:
    meta = parse_scenario_meta(scenario)
    is_legacy = bool(meta.get("legacy", False))
    if is_legacy and not allow_legacy:
        raise RuntimeError(
            "检测到 legacy 场景，默认拒绝执行。若确认要跑，请显式加 --allow-legacy-scenario。"
        )

    default_root = default_scenario_root()
    if not allow_external and not path_within(scenario_path, default_root):
        raise RuntimeError(
            f"场景路径不在默认白名单目录内：{default_root}。"
            "为防误跑旧剧本，默认只允许该目录。若需例外，请显式加 --allow-external-scenario。"
        )

    return {
        "defaultScenarioRoot": str(default_root),
        "allowExternalScenario": allow_external,
        "legacy": is_legacy,
    }


def normalize_host(host: str) -> str:
    normalized = host.strip().lower()
    if normalized.startswith("www."):
        return normalized[4:]
    return normalized


def host_from_url(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if not parsed.hostname:
        return None
    return normalize_host(parsed.hostname)


def normalize_gate_message(text: str) -> str:
    return " ".join(text.strip().lower().split())


def canonicalize_url_for_gate(url: str) -> str:
    raw = url.strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
    except Exception:
        return raw
    if not parsed.scheme or not parsed.netloc:
        return raw
    path = parsed.path or "/"
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def normalize_patterns(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for item in values:
        if isinstance(item, str) and item.strip():
            out.append(item.strip().lower())
    return out


def match_any_pattern(text: str, patterns: List[str]) -> bool:
    content = text.lower()
    return any(pat in content for pat in patterns)


def extract_target_hosts(
    scenario_steps: List[Any],
    network_entries: List[Dict[str, Any]],
) -> List[str]:
    hosts: set[str] = set()
    for raw_step in scenario_steps:
        if not isinstance(raw_step, dict):
            continue
        action = str(raw_step.get("action") or "").strip().lower()
        if action not in {"open", "navigate"}:
            continue
        url = raw_step.get("url")
        if not isinstance(url, str) or not url.strip():
            continue
        host = host_from_url(url.strip())
        if host:
            hosts.add(host)

    if hosts:
        return sorted(hosts)

    # Fallback: if scenario has no explicit open/navigate URL, infer from first-party traffic.
    observed: Dict[str, int] = {}
    for item in network_entries:
        url = item.get("url")
        if not isinstance(url, str):
            continue
        host = host_from_url(url)
        if not host:
            continue
        observed[host] = observed.get(host, 0) + 1
    if not observed:
        return []
    return [max(observed, key=observed.get)]


def build_visual_config(scenario: Dict[str, Any]) -> Dict[str, Any]:
    visual = scenario.get("visual") if isinstance(scenario.get("visual"), dict) else {}
    return {
        "enabled": bool(visual.get("enabled", False)),
        "focusTabBeforeStep": bool(visual.get("focusTabBeforeStep", False)),
        "preActionWaitMs": to_non_negative_int(visual.get("preActionWaitMs"), 0),
        "postActionWaitMs": to_non_negative_int(visual.get("postActionWaitMs"), 0),
        "highlightBeforeClick": bool(visual.get("highlightBeforeClick", True)),
        "highlightBeforeType": bool(visual.get("highlightBeforeType", True)),
        "highlightWaitMs": to_non_negative_int(visual.get("highlightWaitMs"), 400),
    }


def build_gate_config(scenario: Dict[str, Any]) -> Dict[str, Any]:
    gates = scenario.get("gates") if isinstance(scenario.get("gates"), dict) else {}
    console_cfg = gates.get("console") if isinstance(gates.get("console"), dict) else {}
    network_cfg = gates.get("network") if isinstance(gates.get("network"), dict) else {}

    return {
        "enabled": bool(gates.get("enabled", True)),
        "minPassRate": safe_float(gates.get("minPassRate"), 95.0),
        "console": {
            "errorAsFailure": bool(console_cfg.get("errorAsFailure", True)),
            "ignoreMessagePatterns": normalize_patterns(console_cfg.get("ignoreMessagePatterns")),
        },
        "network": {
            "sameOrigin4xxAsFailure": bool(network_cfg.get("sameOrigin4xxAsFailure", True)),
            "sameOrigin5xxAsFailure": bool(network_cfg.get("sameOrigin5xxAsFailure", True)),
            "thirdParty5xxAsFailure": bool(network_cfg.get("thirdParty5xxAsFailure", False)),
            "ignoreUrlPatterns": normalize_patterns(network_cfg.get("ignoreUrlPatterns")),
            "ignoreStatusCodes": [
                safe_int(v, -1)
                for v in (network_cfg.get("ignoreStatusCodes") if isinstance(network_cfg.get("ignoreStatusCodes"), list) else [])
                if isinstance(v, (int, float, str))
            ],
        },
    }


def build_exploration_config(scenario: Dict[str, Any]) -> Dict[str, Any]:
    raw = scenario.get("exploration")
    cfg = raw if isinstance(raw, dict) else {}
    return {
        "enabled": bool(cfg.get("enabled", True)),
        "maxDepth": max(1, to_int(cfg.get("maxDepth"), 3)),
        "maxChildrenPerNode": max(1, to_int(cfg.get("maxChildrenPerNode"), 2)),
        "maxPages": max(1, to_int(cfg.get("maxPages"), 10)),
        "maxDurationMinutes": max(1, to_int(cfg.get("maxDurationMinutes"), 8)),
        "sameOriginOnly": bool(cfg.get("sameOriginOnly", True)),
    }


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=""))


def _discover_links_on_page(
    browser: BrowserCLI,
    page_url: str,
    current_depth: int,
    start_origin: str,
    same_origin_only: bool,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    try:
        snapshot = browser.run(
            ["snapshot", "--interactive", "--labels"],
            expect_json=True,
            timeout_sec=30,
        )
        refs = snapshot.get("refs") if isinstance(snapshot, dict) else None
        if not isinstance(refs, dict) or not refs:
            return found

        for ref, meta in refs.items():
            if not isinstance(ref, str) or not ref.strip():
                continue
            if not isinstance(meta, dict):
                continue
            role = str(meta.get("role") or "").strip().lower()
            if role != "link":
                continue
            name = str(meta.get("name") or "").strip()

            try:
                href_result = browser.run(
                    [
                        "evaluate",
                        "--ref",
                        ref.strip(),
                        "--fn",
                        "(el) => (el && el.href) ? String(el.href) : ''",
                    ],
                    expect_json=True,
                    timeout_sec=15,
                    allow_failure=True,
                )
                href = (
                    str(href_result.get("result") or "").strip()
                    if isinstance(href_result, dict)
                    else ""
                )
            except Exception:
                continue

            if not href:
                continue
            lower = href.lower()
            if lower.startswith(("javascript:", "mailto:", "tel:", "data:")):
                continue

            normalized = _normalize_url(href)
            if normalized == _normalize_url(page_url):
                continue

            if same_origin_only and start_origin:
                parsed = urlparse(href)
                link_origin = f"{parsed.scheme}://{parsed.netloc}"
                if link_origin != start_origin:
                    continue

            found.append(
                {
                    "ref": ref.strip(),
                    "name": name,
                    "href": href,
                    "normalizedHref": normalized,
                    "sourceUrl": page_url,
                    "depth": current_depth + 1,
                }
            )
    except Exception as exc:
        if verbose:
            print(
                f"[auto-qa:explore] link discovery failed on {page_url}: {exc}",
                file=sys.stderr,
            )
    return found


def run_exploration_phase(
    *,
    browser: BrowserCLI,
    exploration_cfg: Dict[str, Any],
    artifact_dir: Path,
    screenshots_dir: Path,
    seen_console: set,
    health_checks: List[Dict[str, Any]],
    verbose: bool = False,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "enabled": False,
        "pagesVisited": [],
        "linksDiscovered": [],
        "explorationSteps": [],
        "consoleEvidence": [],
        "networkEvidence": [],
        "totalPagesVisited": 0,
        "totalLinksDiscovered": 0,
        "totalLinksFollowed": 0,
        "maxDepthReached": 0,
        "stoppedReason": "not_started",
        "durationMs": 0,
        "warnings": [],
    }

    if not exploration_cfg.get("enabled", True):
        result["stoppedReason"] = "disabled"
        return result

    result["enabled"] = True
    max_depth = max(1, exploration_cfg.get("maxDepth", 3))
    max_children = max(1, exploration_cfg.get("maxChildrenPerNode", 5))
    max_pages = max(1, exploration_cfg.get("maxPages", 30))
    max_duration_min = max(1, exploration_cfg.get("maxDurationMinutes", 15))
    same_origin_only = exploration_cfg.get("sameOriginOnly", True)

    start_time = time.time()
    deadline = start_time + max_duration_min * 60

    try:
        origin_res = browser.run(
            ["evaluate", "--fn", "() => window.location.origin || ''"],
            expect_json=True,
            timeout_sec=20,
        )
        href_res = browser.run(
            ["evaluate", "--fn", "() => window.location.href || ''"],
            expect_json=True,
            timeout_sec=20,
        )
        start_origin = str(origin_res.get("result") or "").strip()
        start_url = str(href_res.get("result") or "").strip()
    except Exception as exc:
        result["warnings"].append(f"cannot determine current URL: {exc}")
        result["stoppedReason"] = "browser_error"
        return result

    if not start_url or not start_origin:
        result["warnings"].append("current URL/origin is empty; skipping exploration")
        result["stoppedReason"] = "no_start_url"
        return result

    visited: set[str] = {_normalize_url(start_url)}
    queue: List[Tuple[str, int]] = []
    pages_visited: List[Dict[str, Any]] = []
    links_discovered: List[Dict[str, Any]] = []
    exploration_steps: List[Dict[str, Any]] = []
    console_evidence: List[Dict[str, Any]] = []
    network_evidence: List[Dict[str, Any]] = []
    max_depth_reached = 0
    stopped_reason = "queue_empty"

    pages_visited.append(
        {
            "url": start_url,
            "normalizedUrl": _normalize_url(start_url),
            "depth": 0,
            "status": "ok",
            "source": "predefined_steps",
        }
    )

    initial_links = _discover_links_on_page(
        browser, start_url, 0, start_origin, same_origin_only, verbose
    )
    children_added = 0
    for link in initial_links:
        links_discovered.append(link)
        norm = link["normalizedHref"]
        if norm not in visited and children_added < max_children:
            if link["depth"] <= max_depth:
                queue.append((link["href"], link["depth"]))
                visited.add(norm)
                children_added += 1

    page_count = 1
    step_counter = 0

    while queue:
        if time.time() >= deadline:
            stopped_reason = "max_duration_reached"
            break
        if page_count >= max_pages:
            stopped_reason = "max_pages_reached"
            break

        url, depth = queue.pop(0)
        if depth > max_depth:
            continue

        step_counter += 1
        step_id = f"explore-{step_counter:03d}"
        step_started = now_iso()
        step_started_ts = datetime.now(timezone.utc)
        step_status = "passed"
        step_actual = ""
        page_title = ""

        try:
            browser.run(["open", url], expect_json=True, timeout_sec=45)
            browser.run(
                ["wait", "--time", "2000"],
                expect_json=True,
                timeout_sec=10,
                allow_failure=True,
            )
        except Exception as exc:
            step_status = "failed"
            step_actual = f"navigation failed: {exc}"
            exploration_steps.append(
                {
                    "stepId": step_id,
                    "action": "explore_navigate",
                    "target": url,
                    "expected": f"page loads at depth {depth}",
                    "actual": step_actual,
                    "status": step_status,
                    "depth": depth,
                    "startedAt": step_started,
                    "endedAt": now_iso(),
                    "durationMs": int(
                        (datetime.now(timezone.utc) - step_started_ts).total_seconds()
                        * 1000
                    ),
                }
            )
            continue

        try:
            landed_res = browser.run(
                ["evaluate", "--fn", "() => window.location.href || ''"],
                expect_json=True,
                timeout_sec=15,
            )
            landed_url = str(landed_res.get("result") or "").strip()
        except Exception:
            landed_url = url

        try:
            title_res = browser.run(
                ["evaluate", "--fn", "() => document.title || ''"],
                expect_json=True,
                timeout_sec=10,
                allow_failure=True,
            )
            page_title = (
                str(title_res.get("result") or "").strip()
                if isinstance(title_res, dict)
                else ""
            )
        except Exception:
            pass

        page_count += 1
        if depth > max_depth_reached:
            max_depth_reached = depth

        step_actual = f"navigated to {landed_url} (title: {page_title})"

        screenshot_path: Optional[str] = None
        try:
            shot = browser.run(["screenshot"], expect_json=True, timeout_sec=30)
            src = shot.get("path") if isinstance(shot, dict) else None
            if isinstance(src, str) and src.strip():
                src_p = Path(src).expanduser()
                if src_p.exists():
                    dst = screenshots_dir / f"{step_id}-explore.png"
                    shutil.copy2(src_p, dst)
                    screenshot_path = str(dst)
        except Exception as exc:
            if verbose:
                print(
                    f"[auto-qa:explore] screenshot failed for {url}: {exc}",
                    file=sys.stderr,
                )

        c_items, n_items = collect_step_evidence(
            browser=browser,
            step_id=step_id,
            seen_console=seen_console,
            verbose=verbose,
        )
        console_evidence.extend(c_items)
        network_evidence.extend(n_items)

        health = run_health_check(browser, f"explore-{step_id}")
        health_checks.append(health)
        if not health.get("ok"):
            step_status = "failed"
            step_actual += f"; health check failed: {health.get('issues', [])}"

        error_count = sum(
            1
            for c in c_items
            if str(c.get("level") or "").lower() == "error"
        )

        pages_visited.append(
            {
                "url": landed_url,
                "normalizedUrl": _normalize_url(landed_url),
                "depth": depth,
                "title": page_title,
                "status": step_status,
                "screenshotPath": screenshot_path,
                "consoleErrors": error_count,
                "source": "exploration",
            }
        )

        exploration_steps.append(
            {
                "stepId": step_id,
                "action": "explore_navigate",
                "target": url,
                "expected": f"page loads at depth {depth}",
                "actual": step_actual,
                "status": step_status,
                "depth": depth,
                "startedAt": step_started,
                "endedAt": now_iso(),
                "durationMs": int(
                    (datetime.now(timezone.utc) - step_started_ts).total_seconds()
                    * 1000
                ),
                "screenshotPath": screenshot_path,
                "pageTitle": page_title,
                "landedUrl": landed_url,
            }
        )

        if depth < max_depth and page_count < max_pages:
            page_links = _discover_links_on_page(
                browser, landed_url, depth, start_origin, same_origin_only, verbose
            )
            children_added_inner = 0
            for link in page_links:
                links_discovered.append(link)
                norm = link["normalizedHref"]
                if norm not in visited and children_added_inner < max_children:
                    if link["depth"] <= max_depth:
                        queue.append((link["href"], link["depth"]))
                        visited.add(norm)
                        children_added_inner += 1

    if page_count >= max_pages and stopped_reason == "queue_empty":
        stopped_reason = "max_pages_reached"

    elapsed_ms = int((time.time() - start_time) * 1000)

    all_known_urls = {p["normalizedUrl"] for p in pages_visited}
    for lnk in links_discovered:
        all_known_urls.add(lnk["normalizedHref"])
    total_discoverable = len(all_known_urls)
    pages_visited_count = len(pages_visited)
    page_coverage = (
        round((pages_visited_count / total_discoverable) * 100, 2)
        if total_discoverable
        else 0.0
    )
    link_coverage = (
        round(
            (
                len([p for p in pages_visited if p.get("source") == "exploration"])
                / len(links_discovered)
            )
            * 100,
            2,
        )
        if links_discovered
        else 0.0
    )

    result.update(
        {
            "pagesVisited": pages_visited,
            "linksDiscovered": links_discovered,
            "explorationSteps": exploration_steps,
            "consoleEvidence": console_evidence,
            "networkEvidence": network_evidence,
            "totalPagesVisited": pages_visited_count,
            "totalLinksDiscovered": len(links_discovered),
            "totalLinksFollowed": len(
                [p for p in pages_visited if p.get("source") == "exploration"]
            ),
            "maxDepthReached": max_depth_reached,
            "stoppedReason": stopped_reason,
            "durationMs": elapsed_ms,
            "startUrl": start_url,
            "startOrigin": start_origin,
            "config": exploration_cfg,
            "pageCoverageRate": page_coverage,
            "linkCoverageRate": link_coverage,
        }
    )

    if verbose:
        print(
            f"[auto-qa:explore] done: {pages_visited_count} pages, "
            f"{len(links_discovered)} links discovered, "
            f"depth {max_depth_reached}, stopped={stopped_reason}, "
            f"{elapsed_ms}ms",
            file=sys.stderr,
        )

    return result


def is_return_edge_step(raw_step: Any) -> bool:
    if not isinstance(raw_step, dict):
        return False
    action = str(raw_step.get("action") or "").strip().lower()
    if action in {"back", "go_back"}:
        return True
    if bool(raw_step.get("returnEdge")):
        return True
    return False


def build_coverage_metrics(
    *,
    scenario_steps: List[Any],
    executed_steps: List[Dict[str, Any]],
) -> Dict[str, Any]:
    scenario_by_id: Dict[str, Dict[str, Any]] = {}
    planned_step_count = len(scenario_steps)
    planned_return_edges = 0
    max_depth_planned = 1
    for idx, raw_step in enumerate(scenario_steps):
        if not isinstance(raw_step, dict):
            continue
        step_id = ensure_step_id(raw_step, idx + 1)
        scenario_by_id[step_id] = raw_step
        if is_return_edge_step(raw_step):
            planned_return_edges += 1
        depth = max(1, safe_int(raw_step.get("depth"), 1))
        max_depth_planned = max(max_depth_planned, depth)

    executed_step_count = len(executed_steps)
    passed_step_count = len([step for step in executed_steps if step.get("status") == "passed"])

    executed_return_edges = 0
    passed_return_edges = 0
    max_depth_executed = 1
    for step in executed_steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("stepId") or "").strip()
        raw_step = scenario_by_id.get(step_id)
        if raw_step is None:
            continue
        depth = max(1, safe_int(raw_step.get("depth"), 1))
        max_depth_executed = max(max_depth_executed, depth)
        if is_return_edge_step(raw_step):
            executed_return_edges += 1
            if step.get("status") == "passed":
                passed_return_edges += 1

    step_coverage_rate = round((executed_step_count / planned_step_count) * 100, 2) if planned_step_count else 0.0
    step_pass_rate = round((passed_step_count / executed_step_count) * 100, 2) if executed_step_count else 0.0
    return_edge_coverage_rate = (
        round((executed_return_edges / planned_return_edges) * 100, 2)
        if planned_return_edges
        else 100.0
    )
    return_edge_pass_rate = (
        round((passed_return_edges / executed_return_edges) * 100, 2)
        if executed_return_edges
        else (100.0 if planned_return_edges == 0 else 0.0)
    )
    depth_coverage_rate = (
        round((max_depth_executed / max_depth_planned) * 100, 2)
        if max_depth_planned
        else 0.0
    )

    return {
        "plannedSteps": planned_step_count,
        "executedSteps": executed_step_count,
        "passedSteps": passed_step_count,
        "stepCoverageRate": step_coverage_rate,
        "stepPassRate": step_pass_rate,
        "plannedReturnEdges": planned_return_edges,
        "executedReturnEdges": executed_return_edges,
        "passedReturnEdges": passed_return_edges,
        "returnEdgeCoverageRate": return_edge_coverage_rate,
        "returnEdgePassRate": return_edge_pass_rate,
        "plannedMaxDepth": max_depth_planned,
        "executedMaxDepth": max_depth_executed,
        "depthCoverageRate": depth_coverage_rate,
    }


def evaluate_gate_violations(
    gate_cfg: Dict[str, Any],
    target_hosts: List[str],
    console_entries: List[Dict[str, Any]],
    network_entries: List[Dict[str, Any]],
    console_path: Path,
    network_path: Path,
) -> List[Dict[str, Any]]:
    if not gate_cfg.get("enabled", True):
        return []

    violations: List[Dict[str, Any]] = []
    dedupe_index: Dict[str, Dict[str, Any]] = {}
    console_cfg = gate_cfg.get("console", {})
    network_cfg = gate_cfg.get("network", {})

    def append_violation(item: Dict[str, Any], dedupe_key: Optional[str] = None) -> None:
        fp = dedupe_key or hashlib.sha1(
            json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        existing = dedupe_index.get(fp)
        if existing:
            existing["occurrences"] = safe_int(existing.get("occurrences"), 1) + 1
            evidence = existing.get("evidence")
            if not isinstance(evidence, dict):
                evidence = {}
                existing["evidence"] = evidence
            step_ids_raw = evidence.get("stepIds")
            step_ids: List[str] = []
            if isinstance(step_ids_raw, list):
                step_ids = [str(v) for v in step_ids_raw if isinstance(v, str) and v.strip()]
            else:
                prev_step_id = existing.get("stepId")
                if isinstance(prev_step_id, str) and prev_step_id.strip():
                    step_ids = [prev_step_id]
            step_id = item.get("stepId")
            if isinstance(step_id, str) and step_id.strip() and step_id not in step_ids:
                step_ids.append(step_id)
            if step_ids:
                evidence["stepIds"] = step_ids
            return
        dedupe_index[fp] = item
        item["id"] = f"GATE-{len(violations) + 1:03d}"
        item["occurrences"] = 1
        evidence = item.get("evidence")
        step_id = item.get("stepId")
        if isinstance(evidence, dict) and isinstance(step_id, str) and step_id.strip():
            evidence["stepIds"] = [step_id]
        violations.append(item)

    if console_cfg.get("errorAsFailure", True):
        ignore_patterns = console_cfg.get("ignoreMessagePatterns", [])
        for entry in console_entries:
            level = str(entry.get("level") or "").lower()
            if level != "error":
                continue
            message = str(entry.get("message") or "")
            if ignore_patterns and match_any_pattern(message, ignore_patterns):
                continue
            dedupe_key = f"console|console.error|{normalize_gate_message(message)}"
            append_violation(
                {
                    "type": "console",
                    "gate": "console.error",
                    "severity": "critical",
                    "blockRelease": True,
                    "title": "Console 出现 error 日志",
                    "message": message,
                    "stepId": entry.get("stepId"),
                    "evidence": {
                        "consolePath": str(console_path),
                    },
                },
                dedupe_key=dedupe_key,
            )

    ignore_status = {
        status for status in network_cfg.get("ignoreStatusCodes", []) if isinstance(status, int) and status >= 0
    }
    ignore_url_patterns = network_cfg.get("ignoreUrlPatterns", [])
    target_set = {normalize_host(h) for h in target_hosts if isinstance(h, str) and h}

    for entry in network_entries:
        status_raw = entry.get("status")
        if not isinstance(status_raw, int):
            continue
        status = int(status_raw)
        if status < 400:
            continue
        if status in ignore_status:
            continue

        url = str(entry.get("url") or "")
        if ignore_url_patterns and match_any_pattern(url, ignore_url_patterns):
            continue

        host = host_from_url(url) or ""
        same_origin = bool(target_set) and host in target_set
        severity: Optional[str] = None
        gate = ""
        title = ""
        block_release = False

        if same_origin and status >= 500 and network_cfg.get("sameOrigin5xxAsFailure", True):
            severity = "blocker"
            gate = "network.same_origin.5xx"
            title = "同域网络请求 5xx"
            block_release = True
        elif same_origin and 400 <= status < 500 and network_cfg.get("sameOrigin4xxAsFailure", True):
            severity = "critical"
            gate = "network.same_origin.4xx"
            title = "同域网络请求 4xx"
            block_release = True
        elif (not same_origin) and status >= 500 and network_cfg.get("thirdParty5xxAsFailure", False):
            severity = "major"
            gate = "network.third_party.5xx"
            title = "第三方网络请求 5xx"
            block_release = False

        if not severity:
            continue

        method = str(entry.get("method") or "GET").upper()
        url_canonical = canonicalize_url_for_gate(url)
        dedupe_key = f"network|{gate}|{method}|{status}|{url_canonical}"
        append_violation(
            {
                "type": "network",
                "gate": gate,
                "severity": severity,
                "blockRelease": block_release,
                "title": title,
                "message": f"{method} {url} -> {status}",
                "stepId": entry.get("stepId"),
                "url": url,
                "method": method,
                "status": status,
                "sameOrigin": same_origin,
                "evidence": {
                    "networkPath": str(network_path),
                },
            },
            dedupe_key=dedupe_key,
        )

    return violations


def count_violations_by_severity(violations: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"blocker": 0, "critical": 0, "major": 0, "minor": 0}
    for item in violations:
        severity = str(item.get("severity") or "minor").lower()
        if severity not in counts:
            severity = "minor"
        counts[severity] += 1
    return counts


def decide_release(
    failed_step_count: int,
    pass_rate: float,
    min_pass_rate: float,
    violation_counts: Dict[str, int],
) -> Dict[str, Any]:
    blocker = int(violation_counts.get("blocker", 0))
    critical = int(violation_counts.get("critical", 0))
    major = int(violation_counts.get("major", 0))

    reasons: List[str] = []
    decision = "GO"
    go_no_go = "GO"

    if failed_step_count > 0:
        reasons.append(f"存在失败步骤: {failed_step_count}")
    if pass_rate < min_pass_rate:
        reasons.append(f"通过率 {pass_rate}% 低于阈值 {min_pass_rate}%")
    if blocker > 0:
        reasons.append(f"存在 blocker 级门禁违规: {blocker}")
    if critical > 0:
        reasons.append(f"存在 critical 级门禁违规: {critical}")

    if failed_step_count > 0 or pass_rate < min_pass_rate or blocker > 0 or critical > 0:
        decision = "NO_GO"
        go_no_go = "NO-GO"
    elif major > 0:
        decision = "CONDITIONAL_GO"
        go_no_go = "CONDITIONAL-GO"
        reasons.append(f"存在 major 级风险项: {major}")

    if decision == "NO_GO":
        risk = "high"
    elif decision == "CONDITIONAL_GO":
        risk = "medium"
    else:
        risk = "low"

    return {
        "releaseDecision": decision,
        "goNoGo": go_no_go,
        "riskLevel": risk,
        "reasons": reasons,
    }


def build_review_summary(
    *,
    go_no_go: str,
    release_decision: str,
    blocking_issues: List[Dict[str, Any]],
    step_trace_map: Dict[str, Any],
    trace_expected: bool,
    trace_exists: bool,
    showcase_recheck: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    findings: List[str] = []

    decision_map = {
        "GO": "GO",
        "CONDITIONAL-GO": "CONDITIONAL_GO",
        "NO-GO": "NO_GO",
    }
    expected_release_decision = decision_map.get(go_no_go)
    if expected_release_decision and release_decision != expected_release_decision:
        findings.append(
            f"发布建议与结论映射不一致：goNoGo={go_no_go}，releaseDecision={release_decision}"
        )

    if release_decision == "GO" and len(blocking_issues) > 0:
        findings.append("发布建议为 GO，但阻断项非空。")

    step_trace_status = str(step_trace_map.get("status") or "").strip().lower()
    if step_trace_status == "error":
        trace_reason = step_trace_map.get("summary", {}).get("reason")
        if isinstance(trace_reason, str) and trace_reason.strip():
            findings.append(f"Trace 对齐失败：{trace_reason.strip()}")
        else:
            findings.append("Trace 对齐失败：step_trace_map 状态为 error。")

    if trace_expected and not trace_exists:
        findings.append("本次运行应生成 trace，但未找到 trace.zip。")

    if isinstance(showcase_recheck, dict) and bool(showcase_recheck.get("enabled")):
        showcase_status = str(showcase_recheck.get("status") or "").strip().lower()
        mismatches = showcase_recheck.get("mismatches")
        mismatch_items = mismatches if isinstance(mismatches, list) else []
        if showcase_status == "needs_inspection":
            if mismatch_items:
                preview = mismatch_items[:5]
                for item in preview:
                    if not isinstance(item, dict):
                        continue
                    step_id = str(item.get("stepId") or "-")
                    analysis_status = str(item.get("analysisStatus") or "-")
                    showcase_status_text = str(item.get("showcaseStatus") or "-")
                    findings.append(
                        f"复核差异：{step_id}（主执行={analysis_status}，复核执行={showcase_status_text}）"
                    )
                if len(mismatch_items) > len(preview):
                    findings.append(f"复核差异其余 {len(mismatch_items) - len(preview)} 项请进一步检验。")
            else:
                findings.append("复核执行与主执行存在差异，需进一步检验。")
        elif showcase_status == "partial_timeout":
            findings.append("复核执行触发时间预算并提前停止，本轮仅完成部分复核。")

    if findings:
        return {
            "reviewStatus": "needs_inspection",
            "reviewConclusion": "复核需进一步检验",
            "reviewFindings": findings,
        }

    return {
        "reviewStatus": "consistent",
        "reviewConclusion": "复核一致",
        "reviewFindings": [],
    }


def parse_iso_to_epoch_ms(value: Any) -> Optional[int]:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return int(dt.timestamp() * 1000)


def epoch_ms_to_iso(value: int) -> str:
    dt = datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def run_openclaw_command(
    command_prefix: List[str],
    args: List[str],
    *,
    expect_json: bool = True,
    timeout_sec: int = 60,
) -> Any:
    cmd = [*command_prefix, *args]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RuntimeError(f"command failed: {' '.join(cmd)}; {detail}")
    if not expect_json:
        return proc.stdout.strip()
    return parse_json_output(proc.stdout)


def should_defer_trace_start(
    *,
    no_trace: bool,
    mode: str,
    scenario_steps: List[Any],
    start_index: int,
) -> bool:
    if no_trace:
        return False
    normalized = mode.strip().lower()
    if normalized == "after-first-step":
        return True
    if normalized == "immediate":
        return False
    if start_index >= len(scenario_steps):
        return False
    first = scenario_steps[start_index]
    if not isinstance(first, dict):
        return False
    action = str(first.get("action") or "").strip().lower()
    return action in {"open", "navigate"}


def build_step_trace_map(
    *,
    run_id: str,
    steps: List[Dict[str, Any]],
    trace_path: Path,
) -> Dict[str, Any]:
    output: Dict[str, Any] = {
        "runId": run_id,
        "generatedAt": now_iso(),
        "tracePath": str(trace_path),
        "status": "not_available",
        "summary": {},
        "steps": [],
    }

    windows: List[Dict[str, Any]] = []
    for step in steps:
        start_ms = parse_iso_to_epoch_ms(step.get("startedAt"))
        end_ms = parse_iso_to_epoch_ms(step.get("endedAt"))
        if start_ms is None or end_ms is None:
            continue
        if end_ms < start_ms:
            end_ms = start_ms
        window = {
            "stepId": step.get("stepId"),
            "action": step.get("action"),
            "status": step.get("status"),
            "startMs": start_ms,
            "endMs": end_ms,
            "startAt": epoch_ms_to_iso(start_ms),
            "endAt": epoch_ms_to_iso(end_ms),
            "durationMs": end_ms - start_ms,
            "trace": {
                "eventCount": 0,
                "screencastFrames": 0,
                "apiCalls": [],
                "console": [],
                "network": [],
            },
        }
        windows.append(window)

    output["steps"] = windows

    if not trace_path.exists():
        output["status"] = "missing"
        output["summary"] = {"reason": "trace zip not found"}
        return output

    if not windows:
        output["status"] = "no-step-window"
        output["summary"] = {"reason": "steps missing timestamps"}
        return output

    try:
        with zipfile.ZipFile(trace_path, "r") as zf:
            names = set(zf.namelist())
            trace_lines: List[str] = []
            network_lines: List[str] = []
            if "trace.trace" in names:
                trace_lines = zf.read("trace.trace").decode("utf-8", "replace").splitlines()
            if "trace.network" in names:
                network_lines = zf.read("trace.network").decode("utf-8", "replace").splitlines()

            base_wall_ms: Optional[float] = None
            base_mono: Optional[float] = None
            total_trace_events = 0
            total_network_events = 0
            unmatched_trace_events = 0
            unmatched_network_events = 0

            def assign_trace_event(
                event_ms: float,
                item: Dict[str, Any],
            ) -> bool:
                matched = False
                for win in windows:
                    start_ms = int(win["startMs"]) - 300
                    end_ms = int(win["endMs"]) + 1200
                    if start_ms <= event_ms <= end_ms:
                        matched = True
                        trace_part = win["trace"]
                        trace_part["eventCount"] += 1
                        etype = str(item.get("type") or "")
                        if etype == "screencast-frame":
                            trace_part["screencastFrames"] += 1
                        elif etype == "console":
                            if len(trace_part["console"]) < 8:
                                trace_part["console"].append(
                                    {
                                        "level": item.get("messageType"),
                                        "text": item.get("text"),
                                        "time": epoch_ms_to_iso(int(event_ms)),
                                    }
                                )
                        elif etype == "before":
                            call_name = item.get("apiName") or item.get("method")
                            if call_name and len(trace_part["apiCalls"]) < 12:
                                trace_part["apiCalls"].append(
                                    {
                                        "name": call_name,
                                        "time": epoch_ms_to_iso(int(event_ms)),
                                    }
                                )
                return matched

            for line in trace_lines:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                total_trace_events += 1
                if obj.get("type") == "context-options":
                    wall_raw = obj.get("wallTime")
                    mono_raw = obj.get("monotonicTime")
                    if isinstance(wall_raw, (int, float)) and isinstance(mono_raw, (int, float)):
                        base_wall_ms = float(wall_raw)
                        base_mono = float(mono_raw)

                raw_time = obj.get("time")
                if not isinstance(raw_time, (int, float)):
                    raw_time = obj.get("timestamp")
                if not isinstance(raw_time, (int, float)) or base_wall_ms is None or base_mono is None:
                    continue
                event_ms = float(base_wall_ms + (float(raw_time) - float(base_mono)))
                if not assign_trace_event(event_ms, obj):
                    unmatched_trace_events += 1

            for line in network_lines:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "resource-snapshot":
                    continue
                snap = obj.get("snapshot")
                if not isinstance(snap, dict):
                    continue
                started = parse_iso_to_epoch_ms(snap.get("startedDateTime"))
                if started is None:
                    continue
                req = snap.get("request") if isinstance(snap.get("request"), dict) else {}
                resp = snap.get("response") if isinstance(snap.get("response"), dict) else {}
                network_item = {
                    "method": req.get("method"),
                    "url": req.get("url"),
                    "status": resp.get("status"),
                    "time": epoch_ms_to_iso(started),
                }
                total_network_events += 1
                matched = False
                for win in windows:
                    start_ms = int(win["startMs"]) - 300
                    end_ms = int(win["endMs"]) + 1200
                    if start_ms <= started <= end_ms:
                        matched = True
                        net_list = win["trace"]["network"]
                        if len(net_list) < 12:
                            net_list.append(network_item)
                if not matched:
                    unmatched_network_events += 1

            output["status"] = "ok"
            output["summary"] = {
                "traceEventsTotal": total_trace_events,
                "networkEventsTotal": total_network_events,
                "unmatchedTraceEvents": unmatched_trace_events,
                "unmatchedNetworkEvents": unmatched_network_events,
                "traceLineCount": len(trace_lines),
                "networkLineCount": len(network_lines),
                "hasTraceFile": "trace.trace" in names,
                "hasNetworkFile": "trace.network" in names,
            }
            return output
    except Exception as exc:
        output["status"] = "error"
        output["summary"] = {"reason": str(exc)}
        return output


def capture_report_fullpage_screenshot(
    *,
    browser: BrowserCLI,
    report_html_path: Path,
    report_dir: Path,
) -> Optional[str]:
    report_url = report_html_path.resolve().as_uri()
    opened_target: Optional[str] = None
    try:
        opened = browser.run(["open", report_url], expect_json=True, timeout_sec=45)
        if isinstance(opened, dict):
            target_id = str(opened.get("targetId") or "").strip()
            if target_id:
                opened_target = target_id
        browser.run(["wait", "--time", "1800"], expect_json=True, timeout_sec=25, allow_failure=True)
        shot = browser.run(["screenshot", "--full-page"], expect_json=True, timeout_sec=90)
        src = shot.get("path") if isinstance(shot, dict) else None
        if not isinstance(src, str) or not src.strip():
            return None
        src_path = Path(src).expanduser()
        if not src_path.exists():
            return None
        dst = report_dir / "report_full.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst)
        compat = report_dir / "report_screenshot.png"
        if compat != dst:
            shutil.copy2(dst, compat)
        return str(dst)
    finally:
        if opened_target:
            try:
                browser.run(["close", opened_target], expect_json=True, timeout_sec=25, allow_failure=True)
            except Exception:
                pass


def parse_session_notify_route(item: Dict[str, Any], preferred_channel: Optional[str]) -> Optional[Dict[str, Any]]:
    key = str(item.get("key") or "").strip()
    if not key:
        return None
    parts = key.split(":")
    if len(parts) < 5:
        return None
    channel = parts[2].strip().lower()
    if preferred_channel and channel != preferred_channel:
        return None
    kind = parts[3].strip().lower()
    identity = ":".join(parts[4:]).strip()
    if not identity:
        return None

    target = identity
    if channel == "discord":
        if kind == "channel":
            target = f"channel:{identity}"
        elif kind in {"dm", "direct", "user"}:
            target = f"user:{identity}"
    return {
        "channel": channel,
        "target": target,
        "key": key,
        "kind": kind,
        "ageMs": safe_int(item.get("age"), -1),
        "updatedAt": safe_int(item.get("updatedAt"), 0),
    }


def infer_notify_route_from_status(
    *,
    command_prefix: List[str],
    preferred_channel: Optional[str],
    max_session_age_ms: Optional[int],
) -> Optional[Dict[str, Any]]:
    payload = run_openclaw_command(
        command_prefix,
        ["status", "--json"],
        expect_json=True,
        timeout_sec=30,
    )
    sessions = payload.get("sessions", {}) if isinstance(payload, dict) else {}
    recent = sessions.get("recent", []) if isinstance(sessions, dict) else []
    if not isinstance(recent, list):
        return None

    recent_sorted = sorted(
        [item for item in recent if isinstance(item, dict)],
        key=lambda x: safe_int(x.get("updatedAt"), 0),
        reverse=True,
    )

    for item in recent_sorted:
        route = parse_session_notify_route(item, preferred_channel=preferred_channel)
        if route is None:
            continue
        age_ms = safe_int(route.get("ageMs"), -1)
        if isinstance(max_session_age_ms, int) and max_session_age_ms > 0 and age_ms >= 0 and age_ms > max_session_age_ms:
            continue
        return route
    return None


def send_report_notification(
    *,
    command_prefix: List[str],
    channel: str,
    target: str,
    message: str,
    media_path: Optional[str],
    account_id: Optional[str],
) -> Dict[str, Any]:
    cmd = ["message", "send", "--channel", channel, "--target", target, "--message", message, "--json"]
    if media_path:
        cmd.extend(["--media", media_path])
    if isinstance(account_id, str) and account_id.strip():
        cmd.extend(["--account", account_id.strip()])
    result = run_openclaw_command(command_prefix, cmd, expect_json=True, timeout_sec=120)
    return result if isinstance(result, dict) else {"raw": result}


def run_health_check(browser: BrowserCLI, label: str) -> Dict[str, Any]:
    check: Dict[str, Any] = {
        "label": label,
        "timestamp": now_iso(),
        "ok": True,
        "issues": [],
        "status": {},
    }
    try:
        status = browser.run(["status"], expect_json=True, timeout_sec=8, allow_failure=True)
        if isinstance(status, dict):
            check["status"] = {
                "enabled": status.get("enabled"),
                "running": status.get("running"),
                "cdpReady": status.get("cdpReady"),
                "profile": status.get("profile"),
            }
            if status.get("enabled") is not True:
                check["ok"] = False
                check["issues"].append("browser_disabled")
            if status.get("running") is not True:
                check["ok"] = False
                check["issues"].append("browser_not_running")
        else:
            check["ok"] = False
            check["issues"].append("invalid_status_payload")
    except Exception as exc:
        check["ok"] = False
        check["issues"].append(f"status_check_failed:{exc}")
    return check


def classify_failure(
    step_result: Dict[str, Any],
    step_console: List[Dict[str, Any]],
    step_network: List[Dict[str, Any]],
    latest_health: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if step_result.get("status") == "passed":
        return {"category": "none", "reason": "passed", "confidence": 1.0}

    actual_text = str(step_result.get("actual") or "").lower()
    env_keywords = [
        "can't reach",
        "cannot connect",
        "cdp",
        "context closed",
        "browser has been closed",
        "target closed",
        "gateway",
        "browser_not_running",
    ]
    if any(k in actual_text for k in env_keywords):
        return {"category": "environment", "reason": "browser_or_gateway_unavailable", "confidence": 0.9}

    if latest_health and latest_health.get("ok") is False:
        return {"category": "environment", "reason": "health_check_not_ok", "confidence": 0.82}

    has_console_error = any(str(item.get("level", "")).lower() == "error" for item in step_console)
    has_http_error = any(
        isinstance(item.get("status"), int) and int(item["status"]) >= 400 for item in step_network
    )
    if has_console_error or has_http_error:
        return {"category": "product", "reason": "runtime_or_http_failure", "confidence": 0.85}

    product_keywords = ["assert", "url should contain", "text does not include", "not found"]
    if any(k in actual_text for k in product_keywords):
        return {"category": "product", "reason": "assertion_or_locator_failure", "confidence": 0.75}

    timeout_keywords = ["timeout", "timed out"]
    if any(k in actual_text for k in timeout_keywords):
        return {"category": "environment", "reason": "possible_background_throttling_or_timing", "confidence": 0.6}

    return {"category": "unknown", "reason": "insufficient_signal", "confidence": 0.4}


def resolve_resume_from_run(
    output_root: Path,
    resume_run_id: str,
) -> Tuple[str, str]:
    report_path = output_root / "reports" / f"run-{resume_run_id}" / "report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"resume report not found: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    blocking = report.get("summary", {}).get("blockingIssues", [])
    if isinstance(blocking, list):
        for item in blocking:
            if isinstance(item, dict) and isinstance(item.get("stepId"), str):
                return resume_run_id, item["stepId"]
    steps = report.get("steps", [])
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict) and step.get("status") == "failed" and isinstance(step.get("stepId"), str):
                return resume_run_id, step["stepId"]
    raise ValueError(f"run-{resume_run_id} has no failed step for resume")


def resolve_resume_from_latest_failed(
    output_root: Path,
    scenario_path: Path,
) -> Tuple[str, str]:
    reports_root = output_root / "reports"
    if not reports_root.exists():
        raise FileNotFoundError(f"reports directory not found: {reports_root}")

    candidates: List[Path] = sorted(
        reports_root.glob("run-*/report.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for report_path in candidates:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        report_scenario = str(report.get("scenarioPath") or "")
        if report_scenario and Path(report_scenario).resolve() != scenario_path.resolve():
            continue

        blocking = report.get("summary", {}).get("blockingIssues", [])
        if isinstance(blocking, list):
            for item in blocking:
                if isinstance(item, dict) and isinstance(item.get("stepId"), str):
                    run_name = report_path.parent.name
                    run_id = run_name[4:] if run_name.startswith("run-") else run_name
                    return run_id, item["stepId"]
    raise ValueError("no previous failed run found for this scenario")


def resolve_start_index(
    scenario_steps: List[Any],
    resume_step_id: str,
) -> int:
    for idx, raw_step in enumerate(scenario_steps):
        if isinstance(raw_step, dict) and ensure_step_id(raw_step, idx + 1) == resume_step_id:
            return idx
    raise ValueError(f"step id not found in scenario: {resume_step_id}")


def build_analysis_visual_config(base_visual: Dict[str, Any]) -> Dict[str, Any]:
    visual = dict(base_visual or {})
    visual["enabled"] = False
    visual["focusTabBeforeStep"] = False
    visual["preActionWaitMs"] = 0
    visual["postActionWaitMs"] = 0
    visual["highlightBeforeClick"] = False
    visual["highlightBeforeType"] = False
    visual["highlightWaitMs"] = 0
    return visual


def build_showcase_visual_config(base_visual: Dict[str, Any]) -> Dict[str, Any]:
    visual = dict(base_visual or {})
    visual["enabled"] = True
    visual["focusTabBeforeStep"] = True
    visual["preActionWaitMs"] = max(160, to_non_negative_int(visual.get("preActionWaitMs"), 220))
    visual["postActionWaitMs"] = max(320, to_non_negative_int(visual.get("postActionWaitMs"), 420))
    visual["highlightBeforeClick"] = True
    visual["highlightBeforeType"] = True
    visual["highlightWaitMs"] = max(300, to_non_negative_int(visual.get("highlightWaitMs"), 420))
    return visual


def build_trace_event_count_map(step_trace_map: Dict[str, Any]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if not isinstance(step_trace_map, dict):
        return counts
    rows = step_trace_map.get("steps")
    if not isinstance(rows, list):
        return counts
    for item in rows:
        if not isinstance(item, dict):
            continue
        step_id = str(item.get("stepId") or "").strip()
        if not step_id:
            continue
        trace = item.get("trace")
        event_count = 0
        if isinstance(trace, dict):
            event_count = max(0, safe_int(trace.get("eventCount"), 0))
        counts[step_id] = event_count
    return counts


def select_showcase_step_ids(
    *,
    analysis_steps: List[Dict[str, Any]],
    step_trace_map: Dict[str, Any],
) -> Dict[str, Any]:
    ordered_ids: List[str] = []
    status_by_step: Dict[str, str] = {}
    for step in analysis_steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("stepId") or "").strip()
        if not step_id or step_id in status_by_step:
            continue
        ordered_ids.append(step_id)
        status_by_step[step_id] = str(step.get("status") or "").strip().lower()

    if not ordered_ids:
        return {
            "selectedStepIds": [],
            "mainChainStepIds": [],
            "failedChainStepIds": [],
            "failedStepIds": [],
            "traceBackedSelection": False,
            "selectionReason": "analysis_no_steps",
        }

    failed_step_ids = [sid for sid in ordered_ids if status_by_step.get(sid) == "failed"]
    first_failed_index: Optional[int] = None
    for idx, sid in enumerate(ordered_ids):
        if sid in failed_step_ids:
            first_failed_index = idx
            break

    if first_failed_index is None:
        main_chain_ids = list(ordered_ids)
    else:
        main_chain_ids = ordered_ids[: first_failed_index + 1]

    trace_counts = build_trace_event_count_map(step_trace_map)
    if trace_counts:
        trace_backed_main = [sid for sid in main_chain_ids if safe_int(trace_counts.get(sid), 0) > 0]
        if trace_backed_main:
            if main_chain_ids and main_chain_ids[0] not in trace_backed_main:
                trace_backed_main = [main_chain_ids[0], *trace_backed_main]
            dedup: List[str] = []
            seen: set[str] = set()
            for sid in trace_backed_main:
                if sid in seen:
                    continue
                seen.add(sid)
                dedup.append(sid)
            main_chain_ids = dedup

    id_to_index = {sid: idx for idx, sid in enumerate(ordered_ids)}
    failed_chain_set: set[str] = set()
    for sid in failed_step_ids:
        idx = id_to_index.get(sid)
        if idx is None:
            continue
        for pos in [idx - 1, idx, idx + 1]:
            if 0 <= pos < len(ordered_ids):
                failed_chain_set.add(ordered_ids[pos])
    failed_chain_ids = [sid for sid in ordered_ids if sid in failed_chain_set]

    selected: List[str] = []
    seen_selected: set[str] = set()
    for sid in [*main_chain_ids, *failed_chain_ids]:
        if sid in seen_selected:
            continue
        seen_selected.add(sid)
        selected.append(sid)

    if not selected:
        selected = list(ordered_ids)

    return {
        "selectedStepIds": selected,
        "mainChainStepIds": main_chain_ids,
        "failedChainStepIds": failed_chain_ids,
        "failedStepIds": failed_step_ids,
        "traceBackedSelection": bool(trace_counts),
        "selectionReason": "main_and_failed_from_analysis_trace",
    }


def run_showcase_recheck_phase(
    *,
    enabled: bool,
    browser: BrowserCLI,
    scenario_steps: List[Any],
    analysis_steps: List[Dict[str, Any]],
    step_trace_map: Dict[str, Any],
    artifact_dir: Path,
    auto_screenshot: bool,
    base_visual_config: Dict[str, Any],
    continue_on_failure: bool,
    max_step_retries: int,
    retry_wait_ms: int,
    time_budget_ms: int,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "enabled": enabled,
        "mode": "showcase-recheck",
        "executedSteps": 0,
        "passedSteps": 0,
        "failedSteps": 0,
        "passRate": 0.0,
        "status": "skipped",
        "mismatches": [],
        "warnings": [],
        "timedOut": False,
        "artifacts": {},
    }
    if not enabled:
        return result

    analysis_status_by_step: Dict[str, str] = {}
    for step in analysis_steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("stepId") or "").strip()
        if not step_id:
            continue
        analysis_status_by_step[step_id] = str(step.get("status") or "")
    if not analysis_status_by_step:
        result["warnings"].append("analysis run has no executed steps; showcase recheck skipped")
        return result

    selection = select_showcase_step_ids(
        analysis_steps=analysis_steps,
        step_trace_map=step_trace_map,
    )
    selected_step_ids_raw = selection.get("selectedStepIds")
    selected_step_ids = selected_step_ids_raw if isinstance(selected_step_ids_raw, list) else []
    selected_step_set = {str(v) for v in selected_step_ids if isinstance(v, str) and v.strip()}
    if not selected_step_set:
        result["warnings"].append("showcase selected step set is empty; fallback to analysis executed steps")
        selected_step_set = {sid for sid in analysis_status_by_step.keys() if sid}
        selection["selectedStepIds"] = [sid for sid in analysis_status_by_step.keys() if sid]
    result["selection"] = selection

    showcase_dir = artifact_dir / "showcase"
    showcase_screenshots_dir = showcase_dir / "screenshots"
    showcase_dir.mkdir(parents=True, exist_ok=True)
    showcase_screenshots_dir.mkdir(parents=True, exist_ok=True)
    steps_path = showcase_dir / "steps.json"

    showcase_visual = build_showcase_visual_config(base_visual_config)

    steps_out: List[Dict[str, Any]] = []
    last_target_id: Optional[str] = None
    write_json(steps_path, steps_out)
    budget = max(0, safe_int(time_budget_ms, 0))
    started_monotonic = time.monotonic()
    timeout_reached = False

    for idx, raw_step in enumerate(scenario_steps):
        if budget > 0:
            elapsed_ms = int((time.monotonic() - started_monotonic) * 1000)
            if elapsed_ms >= budget:
                timeout_reached = True
                result["warnings"].append(
                    f"showcase time budget reached: {elapsed_ms}ms >= {budget}ms; stop recheck early"
                )
                break

        if not isinstance(raw_step, dict):
            continue
        step_id = ensure_step_id(raw_step, idx + 1)
        if step_id not in analysis_status_by_step:
            continue
        if step_id not in selected_step_set:
            continue

        step_payload = dict(raw_step)
        action = str(step_payload.get("action") or "").strip()
        if action == "open":
            step_payload["action"] = "navigate"

        if showcase_visual.get("enabled") and showcase_visual.get("focusTabBeforeStep"):
            focused = focus_tab_for_visual(browser, preferred_target_id=last_target_id)
            if focused:
                last_target_id = focused

        step_retries = max(0, safe_int(step_payload.get("maxRetries"), max_step_retries))
        step_result = run_step_with_retries(
            browser=browser,
            step=step_payload,
            step_id=step_id,
            artifact_dir=showcase_dir,
            screenshots_dir=showcase_screenshots_dir,
            auto_screenshot=auto_screenshot,
            visual_config=showcase_visual,
            max_retries=step_retries,
            retry_wait_ms=retry_wait_ms,
        )
        steps_out.append(step_result)
        write_json(steps_path, steps_out)

        step_target_id = step_result.get("targetId")
        if isinstance(step_target_id, str) and step_target_id.strip():
            last_target_id = step_target_id.strip()
        if action == "open":
            artifacts = step_result.get("artifacts") if isinstance(step_result.get("artifacts"), dict) else {}
            artifacts["showcaseOverride"] = "open->navigate(same-tab)"
            step_result["artifacts"] = artifacts

        expected_status = analysis_status_by_step.get(step_id)
        actual_status = str(step_result.get("status") or "")
        if expected_status != actual_status:
            result["mismatches"].append(
                {
                    "stepId": step_id,
                    "analysisStatus": expected_status,
                    "showcaseStatus": actual_status,
                    "action": step_result.get("action"),
                    "actual": step_result.get("actual"),
                }
            )
            if not continue_on_failure:
                break

    executed_steps = len(steps_out)
    passed_steps = len([step for step in steps_out if step.get("status") == "passed"])
    failed_steps = len([step for step in steps_out if step.get("status") == "failed"])
    pass_rate = round((passed_steps / executed_steps) * 100, 2) if executed_steps else 0.0

    result["executedSteps"] = executed_steps
    result["passedSteps"] = passed_steps
    result["failedSteps"] = failed_steps
    result["passRate"] = pass_rate
    if timeout_reached:
        result["status"] = "partial_timeout"
        result["timedOut"] = True
    else:
        result["status"] = "consistent" if not result["mismatches"] else "needs_inspection"
    result["artifacts"] = {
        "dir": str(showcase_dir),
        "stepsPath": str(steps_path),
        "screenshotsDir": str(showcase_screenshots_dir),
        "timeBudgetMs": budget,
        "elapsedMs": int((time.monotonic() - started_monotonic) * 1000),
    }
    return result


def run_autoqa(args: argparse.Namespace) -> int:
    scenario_path, scenario_selector = resolve_scenario_input(args)
    scenario_var_overrides = parse_scenario_var_overrides(args.scenario_var)
    scenario = load_scenario(scenario_path, scenario_var_overrides)
    scenario_policy = validate_scenario_access(
        scenario_path=scenario_path,
        scenario=scenario,
        allow_external=bool(args.allow_external_scenario),
        allow_legacy=bool(args.allow_legacy_scenario),
    )
    scenario_steps: List[Any] = scenario.get("steps", [])

    run_id = args.run_id or default_run_id()
    output_root = Path(args.output_root).resolve()
    artifact_dir = output_root / "artifacts" / f"run-{run_id}"
    report_dir = output_root / "reports" / f"run-{run_id}"
    screenshots_dir = artifact_dir / "screenshots"

    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    command_prefix = resolve_command_prefix(args.browser_bin, args.browser_cmd)
    browser = BrowserCLI(command_prefix=command_prefix, profile=args.browser_profile, verbose=args.verbose)

    steps_out: List[Dict[str, Any]] = []
    console_out: List[Dict[str, Any]] = []
    network_out: List[Dict[str, Any]] = []
    seen_console: set[str] = set()
    warnings: List[str] = []
    health_checks: List[Dict[str, Any]] = []
    if scenario_selector.get("source") == "direct-path":
        warnings.append("scenario selector uses direct-path mode; registry lock bypassed by explicit allow-direct-scenario-path.")
    elif scenario_selector.get("source") == "direct-path-fallback-default":
        requested = str(scenario_selector.get("requestedScenarioPath") or "")
        fallback_id = str(scenario_selector.get("scenarioId") or "")
        fallback_reason = str(scenario_selector.get("fallbackReason") or "")
        warnings.append(
            "scenario selector received direct-path request; "
            f"fallback to registry default scenario-id={fallback_id} "
            f"(requested={requested}, reason={fallback_reason or 'unspecified'})."
        )

    started_at = now_iso()
    trace_started = False
    trace_start_failed = False
    trace_start_retry_used = False
    trace_start_retry_wait_ms = 1200
    trace_path = artifact_dir / "trace.zip"
    health_mode = str(args.health_check_interval).strip().lower()
    if health_mode not in {"off", "on-failure", "each-step"}:
        health_mode = "on-failure"

    max_step_retries = max(0, safe_int(args.max_step_retries, 1))
    retry_wait_ms = max(0, safe_int(args.retry_wait_ms, 800))
    trace_start_mode = str(args.trace_start_mode or "auto").strip().lower()
    showcase_recheck_enabled = bool(args.showcase_recheck)
    showcase_continue_on_failure = bool(args.showcase_continue_on_failure)
    showcase_max_step_retries = max(0, safe_int(args.showcase_max_step_retries, 0))
    showcase_retry_wait_ms = max(0, safe_int(args.showcase_retry_wait_ms, 500))
    showcase_time_budget_ms = max(0, safe_int(args.showcase_time_budget_ms, 90000))

    resume_step_id: Optional[str] = args.resume_from_step_id
    resume_source: Optional[str] = None
    resume_from_run_id: Optional[str] = None
    resume_mode_count = sum(
        1
        for v in [bool(args.resume_from_step_id), bool(args.resume_from_run_id), bool(args.resume_last_failed)]
        if v
    )
    if resume_mode_count > 1:
        warnings.append("multiple resume options detected; precedence: step-id > run-id > latest-failed")

    if not resume_step_id and args.resume_from_run_id:
        resume_from_run_id, resume_step_id = resolve_resume_from_run(output_root, args.resume_from_run_id)
        resume_source = "run-id"

    if not resume_step_id and bool(args.resume_last_failed):
        resume_from_run_id, resume_step_id = resolve_resume_from_latest_failed(output_root, scenario_path)
        resume_source = "latest-failed"

    start_index = 0
    if resume_step_id:
        start_index = resolve_start_index(scenario_steps, resume_step_id)
        if resume_source is None:
            resume_source = "step-id"

    if args.auto_start_browser:
        try:
            browser.run(["start"], expect_json=True, timeout_sec=20)
        except Exception as exc:
            warnings.append(f"browser start failed: {exc}")

    status_payload: Dict[str, Any] = {}
    try:
        status_raw = browser.run(["status"], expect_json=True, timeout_sec=10)
        if isinstance(status_raw, dict):
            status_payload = status_raw
    except Exception as exc:
        raise RuntimeError(
            "无法连接 openclaw browser。请确认 OpenClaw 网关与浏览器服务可用，或加 --auto-start-browser。"
        ) from exc

    current_browser_pid = safe_int(status_payload.get("pid"), -1)
    orphan_cleanup: Dict[str, Any] = {
        "enabled": bool(args.cleanup_orphan_openclaw_processes),
        "detected": [],
        "terminated": [],
        "errors": [],
        "keptPid": current_browser_pid if current_browser_pid > 0 else None,
    }
    if bool(args.cleanup_orphan_openclaw_processes):
        cleanup = cleanup_extra_openclaw_browser_processes(
            keep_pid=current_browser_pid if current_browser_pid > 0 else None,
        )
        if isinstance(cleanup, dict):
            orphan_cleanup.update(cleanup)
        terminated = cleanup.get("terminated", []) if isinstance(cleanup, dict) else []
        errors = cleanup.get("errors", []) if isinstance(cleanup, dict) else []
        detected = cleanup.get("detected", []) if isinstance(cleanup, dict) else []
        if detected and len(detected) > 1:
            warnings.append(
                f"orphan openclaw chrome detected: pids={detected}; kept={current_browser_pid if current_browser_pid > 0 else 'none'}"
            )
        if terminated:
            warnings.append(f"orphan openclaw chrome cleaned: terminated pids={terminated}")
        if errors:
            warnings.append(f"orphan cleanup errors: {short_json(errors)}")

    pre_health = run_health_check(browser, "pre-run")
    health_checks.append(pre_health)
    if not pre_health.get("ok"):
        warnings.append(f"pre-run health check not ok: {short_json(pre_health.get('issues', []))}")

    try:
        browser.run(["errors", "--clear"], expect_json=True, timeout_sec=15, allow_failure=True)
        browser.run(["requests", "--clear"], expect_json=True, timeout_sec=15, allow_failure=True)
    except Exception as exc:
        warnings.append(f"pre-clear debug logs failed: {exc}")

    if not args.no_trace and has_open_tabs(browser):
        stale_trace_path = artifact_dir / "trace-preflight-cleanup.zip"
        try:
            browser.run(
                ["trace", "stop", "--out", str(stale_trace_path)],
                expect_json=True,
                timeout_sec=35,
            )
            if stale_trace_path.exists():
                stale_trace_path.unlink(missing_ok=True)
            warnings.append("trace preflight cleanup: stale trace session stopped.")
        except Exception as exc:
            detail = str(exc).lower()
            if "no active trace" not in detail:
                warnings.append(f"trace preflight cleanup failed: {exc}")

    trace_started_at_step: Optional[str] = None
    defer_trace_start = should_defer_trace_start(
        no_trace=bool(args.no_trace),
        mode=trace_start_mode,
        scenario_steps=scenario_steps,
        start_index=start_index,
    )
    if defer_trace_start and not args.no_trace:
        warnings.append("trace start deferred until first executed step (avoid initial about:blank tab).")

    def start_trace_with_policy(
        *,
        label: str,
        started_marker: str,
        preexisting_marker: str,
    ) -> Tuple[bool, Optional[str], bool]:
        nonlocal trace_start_retry_used
        try:
            browser.run(["trace", "start"], expect_json=True, timeout_sec=15)
            return True, started_marker, False
        except Exception as exc:
            if is_trace_already_running_error(exc):
                warnings.append(f"{label} skipped: trace already running; reuse existing trace session.")
                return True, preexisting_marker, False
            warnings.append(f"{label} failed: {exc}")

        if trace_start_retry_used:
            return False, None, True

        trace_start_retry_used = True
        cooldown_ms = max(0, trace_start_retry_wait_ms)
        if cooldown_ms > 0:
            try:
                browser.run(
                    ["wait", "--time", str(cooldown_ms)],
                    expect_json=True,
                    timeout_sec=max(5, int(cooldown_ms / 1000) + 5),
                    allow_failure=True,
                )
            except Exception:
                pass
        try:
            browser.run(["trace", "start"], expect_json=True, timeout_sec=15)
            warnings.append(f"{label} retry succeeded after {cooldown_ms}ms cooldown.")
            return True, f"{started_marker}:retry", False
        except Exception as exc:
            if is_trace_already_running_error(exc):
                warnings.append(f"{label} retry skipped: trace already running; reuse existing trace session.")
                return True, preexisting_marker, False
            warnings.append(f"{label} retry failed: {exc}")
            return False, None, True

    if not args.no_trace and not defer_trace_start:
        started, marker, terminal_failed = start_trace_with_policy(
            label="trace start",
            started_marker="pre-step",
            preexisting_marker="pre-existing",
        )
        trace_started = started
        trace_started_at_step = marker
        trace_start_failed = terminal_failed

    visual_cfg = build_visual_config(scenario)
    analysis_visual_cfg = build_analysis_visual_config(visual_cfg)
    last_target_id: Optional[str] = None
    auto_screenshot = bool(scenario.get("autoScreenshot", True))
    analysis_auto_screenshot = bool(scenario.get("analysisAutoScreenshot", False))
    showcase_auto_screenshot = bool(scenario.get("showcaseAutoScreenshot", auto_screenshot))
    continue_on_failure = True

    failed = False
    for idx in range(start_index, len(scenario_steps)):
        raw_step = scenario_steps[idx]
        order = idx + 1

        if not isinstance(raw_step, dict):
            steps_out.append(
                {
                    "stepId": f"step-{order:03d}",
                    "action": "invalid",
                    "target": "",
                    "expected": None,
                    "actual": "step item is not a JSON object",
                    "status": "failed",
                    "startedAt": now_iso(),
                    "endedAt": now_iso(),
                    "durationMs": 0,
                }
            )
            failed = True
            if not continue_on_failure:
                break
            continue

        step_id = ensure_step_id(raw_step, order)
        step_retries = max(0, safe_int(raw_step.get("maxRetries"), max_step_retries))
        if analysis_visual_cfg.get("enabled") and analysis_visual_cfg.get("focusTabBeforeStep"):
            focused = focus_tab_for_visual(browser, preferred_target_id=last_target_id)
            if focused:
                last_target_id = focused
        step_result = run_step_with_retries(
            browser=browser,
            step=raw_step,
            step_id=step_id,
            artifact_dir=artifact_dir,
            screenshots_dir=screenshots_dir,
            auto_screenshot=analysis_auto_screenshot,
            visual_config=analysis_visual_cfg,
            max_retries=step_retries,
            retry_wait_ms=retry_wait_ms,
        )

        c_items, n_items = collect_step_evidence(
            browser=browser,
            step_id=step_id,
            seen_console=seen_console,
            verbose=args.verbose,
        )
        console_out.extend(c_items)
        network_out.extend(n_items)

        if health_mode == "each-step" or (health_mode == "on-failure" and step_result.get("status") != "passed"):
            health_checks.append(run_health_check(browser, f"after-{step_id}"))

        latest_health = health_checks[-1] if health_checks else None
        classification = classify_failure(
            step_result=step_result,
            step_console=c_items,
            step_network=n_items,
            latest_health=latest_health,
        )
        if step_result.get("status") != "passed":
            step_result["failureClassification"] = classification

        steps_out.append(step_result)
        step_target_id = step_result.get("targetId")
        if isinstance(step_target_id, str) and step_target_id.strip():
            last_target_id = step_target_id.strip()

        if not args.no_trace and defer_trace_start and not trace_started and not trace_start_failed:
            started, marker, terminal_failed = start_trace_with_policy(
                label="trace start (deferred)",
                started_marker=step_id,
                preexisting_marker=f"{step_id}:pre-existing",
            )
            if started:
                trace_started = True
                trace_started_at_step = marker
            if terminal_failed:
                trace_start_failed = True

        if step_result["status"] != "passed":
            failed = True
            if not continue_on_failure:
                break

    if trace_started:
        if has_open_tabs(browser):
            try:
                browser.run(
                    ["trace", "stop", "--out", str(trace_path)],
                    expect_json=True,
                    timeout_sec=45,
                )
            except Exception as exc:
                warnings.append(f"trace stop failed: {exc}")
        else:
            warnings.append("trace stop skipped: no browser tabs available.")

    write_json(artifact_dir / "steps.json", steps_out)
    write_json(artifact_dir / "console.json", console_out)
    write_json(artifact_dir / "network.json", network_out)
    write_json(artifact_dir / "health_checks.json", health_checks)
    console_path = artifact_dir / "console.json"
    network_path = artifact_dir / "network.json"

    failed_steps = [s for s in steps_out if s.get("status") == "failed"]
    passed_steps = [s for s in steps_out if s.get("status") == "passed"]
    executed_steps = len(steps_out)
    scenario_total_steps = len(scenario_steps)
    skipped_steps = max(0, start_index)
    pass_rate = round((len(passed_steps) / executed_steps) * 100, 2) if executed_steps else 0.0
    exploration_cfg = build_exploration_config(scenario)
    exploration_cfg["enabled"] = True
    exploration_cfg["maxDepth"] = 3
    exploration_cfg["analysisPolicy"] = "full_no_visual_depth3"
    coverage_metrics = build_coverage_metrics(
        scenario_steps=scenario_steps,
        executed_steps=steps_out,
    )
    gate_cfg = build_gate_config(scenario)
    target_hosts = extract_target_hosts(scenario_steps, network_out)
    gate_violations = evaluate_gate_violations(
        gate_cfg=gate_cfg,
        target_hosts=target_hosts,
        console_entries=console_out,
        network_entries=network_out,
        console_path=console_path,
        network_path=network_path,
    )
    gate_violation_counts = count_violations_by_severity(gate_violations)
    release = decide_release(
        failed_step_count=len(failed_steps),
        pass_rate=pass_rate,
        min_pass_rate=safe_float(gate_cfg.get("minPassRate"), 95.0),
        violation_counts=gate_violation_counts,
    )
    go_no_go = str(release.get("goNoGo", "NO-GO"))
    blocking = (
        [
            {
                "stepId": s.get("stepId"),
                "action": s.get("action"),
                "reason": s.get("actual"),
            }
            for s in failed_steps
        ]
        + [
            {
                "stepId": item.get("stepId"),
                "action": f"gate:{item.get('gate')}",
                "reason": item.get("message"),
                "severity": item.get("severity"),
            }
            for item in gate_violations
            if bool(item.get("blockRelease"))
        ]
    )
    failure_breakdown = {"environment": 0, "product": 0, "unknown": 0}
    for s in failed_steps:
        cls = s.get("failureClassification", {})
        category = str(cls.get("category") or "unknown")
        if category not in failure_breakdown:
            category = "unknown"
        failure_breakdown[category] += 1

    retried_steps = [s for s in steps_out if safe_int(s.get("retriesUsed"), 0) > 0]
    retries_used_total = sum(max(0, safe_int(s.get("retriesUsed"), 0)) for s in steps_out)
    started_from_step_id: Optional[str] = None
    if scenario_steps and start_index < len(scenario_steps):
        raw_start = scenario_steps[start_index]
        if isinstance(raw_start, dict):
            started_from_step_id = ensure_step_id(raw_start, start_index + 1)

    step_trace_map_path = report_dir / "step_trace_map.json"
    step_trace_map = build_step_trace_map(
        run_id=run_id,
        steps=steps_out,
        trace_path=trace_path,
    )
    write_json(step_trace_map_path, step_trace_map)
    if step_trace_map.get("status") == "error":
        warnings.append(f"step trace map parse failed: {step_trace_map.get('summary', {}).get('reason')}")

    showcase_recheck = run_showcase_recheck_phase(
        enabled=showcase_recheck_enabled,
        browser=browser,
        scenario_steps=scenario_steps,
        analysis_steps=steps_out,
        step_trace_map=step_trace_map,
        artifact_dir=artifact_dir,
        auto_screenshot=showcase_auto_screenshot,
        base_visual_config=visual_cfg,
        continue_on_failure=showcase_continue_on_failure,
        max_step_retries=showcase_max_step_retries,
        retry_wait_ms=showcase_retry_wait_ms,
        time_budget_ms=showcase_time_budget_ms,
    )
    if str(showcase_recheck.get("status") or "").strip().lower() == "needs_inspection":
        warnings.append("showcase recheck found status mismatch with main execution")
    elif str(showcase_recheck.get("status") or "").strip().lower() == "partial_timeout":
        warnings.append("showcase recheck stopped early due to time budget; final report kept analysis result with partial recheck")

    review_summary = build_review_summary(
        go_no_go=go_no_go,
        release_decision=str(release.get("releaseDecision", "NO_GO")),
        blocking_issues=blocking,
        step_trace_map=step_trace_map,
        trace_expected=not bool(args.no_trace),
        trace_exists=trace_path.exists(),
        showcase_recheck=showcase_recheck,
    )

    report = {
        "runId": run_id,
        "generatedAt": now_iso(),
        "scenario": scenario.get("name") or scenario_path.name,
        "scenarioPath": str(scenario_path),
        "artifactDir": str(artifact_dir),
        "reportDir": str(report_dir),
        "summary": {
            "goNoGo": go_no_go,
            "releaseDecision": release.get("releaseDecision"),
            "riskLevel": release.get("riskLevel"),
            "releaseDecisionReasons": release.get("reasons", []),
            "totalSteps": executed_steps,
            "scenarioTotalSteps": scenario_total_steps,
            "executedSteps": executed_steps,
            "skippedByResume": skipped_steps,
            "passedSteps": len(passed_steps),
            "failedSteps": len(failed_steps),
            "passRate": pass_rate,
            "gateViolations": len(gate_violations),
            "gateViolationCountsBySeverity": gate_violation_counts,
            "blockingIssues": blocking,
            "failureBreakdown": failure_breakdown,
            "coverage": coverage_metrics,
            "reviewStatus": review_summary.get("reviewStatus"),
            "reviewConclusion": review_summary.get("reviewConclusion"),
            "reviewFindings": review_summary.get("reviewFindings"),
            "reviewMode": "analysis_plus_showcase" if showcase_recheck_enabled else "analysis_only",
            "reviewMismatchCount": len(showcase_recheck.get("mismatches", []))
            if isinstance(showcase_recheck.get("mismatches"), list)
            else 0,
        },
        "exploration": exploration_cfg,
        "gateConfig": gate_cfg,
        "targetHosts": target_hosts,
        "gateViolations": gate_violations,
        "resume": {
            "startedFromStepId": started_from_step_id,
            "startedFromStepIndex": start_index,
            "source": resume_source,
            "sourceRunId": resume_from_run_id,
        },
        "stability": {
            "maxStepRetriesDefault": max_step_retries,
            "retryWaitMs": retry_wait_ms,
            "retriedStepCount": len(retried_steps),
            "retriesUsedTotal": retries_used_total,
            "analysisAutoScreenshot": analysis_auto_screenshot,
            "showcaseAutoScreenshot": showcase_auto_screenshot,
            "healthCheckMode": health_mode,
            "traceStartMode": trace_start_mode,
            "traceDeferred": defer_trace_start,
            "traceStartedAtStep": trace_started_at_step,
            "traceStartRetryUsed": trace_start_retry_used,
            "showcaseRecheck": {
                "enabled": showcase_recheck_enabled,
                "continueOnFailure": showcase_continue_on_failure,
                "maxStepRetries": showcase_max_step_retries,
                "retryWaitMs": showcase_retry_wait_ms,
                "timeBudgetMs": showcase_time_budget_ms,
                "status": showcase_recheck.get("status"),
            },
            "visualMode": visual_cfg,
            "scenarioPolicy": scenario_policy,
            "scenarioSelector": scenario_selector,
            "orphanProcessCleanup": orphan_cleanup,
        },
        "recheck": showcase_recheck,
        "steps": steps_out,
        "evidence": {
            "consoleCount": len(console_out),
            "networkCount": len(network_out),
            "tracePath": str(trace_path) if trace_path.exists() else None,
            "stepTraceMapPath": str(step_trace_map_path),
            "screenshotsDir": str(screenshots_dir),
            "healthChecksPath": str(artifact_dir / "health_checks.json"),
            "healthCheckCount": len(health_checks),
        },
        "warnings": warnings,
        "startedAt": started_at,
        "finishedAt": now_iso(),
    }

    fix_plan = build_fix_plan(
        run_id=run_id,
        failed_steps=failed_steps,
        gate_violations=gate_violations,
        console_entries=console_out,
        network_entries=network_out,
        trace_path=str(trace_path) if trace_path.exists() else None,
    )

    next_window_prompt = build_next_window_prompt(
        fix_plan=fix_plan,
        artifact_dir=artifact_dir,
        report_dir=report_dir,
    )
    standby_prompt = build_standby_prompt()

    report_json_path = report_dir / "report.json"
    report_html_path = report_dir / "report.html"
    fix_plan_path = report_dir / "fix_plan.json"
    next_prompt_path = report_dir / "next_window_prompt.md"
    standby_path = report_dir / "standby_prompt.txt"

    report["evidence"]["reportScreenshotPath"] = None
    report["evidence"]["reportScreenshotCompatPath"] = None
    report["notifications"] = {"requested": False}

    write_json(report_json_path, report)
    write_text(report_html_path, build_report_html(report))
    write_json(fix_plan_path, fix_plan)
    write_text(next_prompt_path, next_window_prompt)
    write_text(standby_path, standby_prompt)

    report_screenshot_path: Optional[str] = None
    report_screenshot_compat_path: Optional[str] = None
    try:
        report_screenshot_path = capture_report_fullpage_screenshot(
            browser=browser,
            report_html_path=report_html_path,
            report_dir=report_dir,
        )
        if report_screenshot_path:
            compat = report_dir / "report_screenshot.png"
            if compat.exists():
                report_screenshot_compat_path = str(compat)
    except Exception as exc:
        warnings.append(f"report screenshot failed: {exc}")

    notify_channel_raw = str(args.notify_channel).strip().lower() if isinstance(args.notify_channel, str) else ""
    notify_target_raw = str(args.notify_target).strip() if isinstance(args.notify_target, str) else ""
    notify_auto_current = bool(args.notify_auto_current_channel)
    notify_requested = bool(notify_channel_raw) or bool(notify_target_raw) or notify_auto_current
    notify_result: Dict[str, Any] = {
        "requested": notify_requested,
        "mode": "auto-current" if notify_auto_current else "explicit",
    }

    notify_channel: Optional[str] = None
    notify_target: Optional[str] = None
    target_source = "arg"
    if notify_channel_raw and notify_channel_raw not in {"auto", "current"}:
        notify_channel = notify_channel_raw
        if notify_target_raw:
            notify_target = notify_target_raw
            target_source = "arg"
        else:
            try:
                route = infer_notify_route_from_status(
                    command_prefix=command_prefix,
                    preferred_channel=notify_channel,
                    max_session_age_ms=None,
                )
                if route:
                    notify_target = str(route.get("target") or "")
                    notify_result["targetFromSessionKey"] = route.get("key")
                    notify_result["targetSessionAgeMs"] = route.get("ageMs")
                    target_source = "status.recent.channel"
            except Exception as exc:
                warnings.append(f"notify target infer failed: {exc}")
    elif notify_target_raw and not notify_channel_raw:
        warnings.append("notify target provided without channel; skip notification")
        notify_result.update(
            {
                "sent": False,
                "error": "notify_channel_missing",
            }
        )
    elif notify_requested:
        try:
            route = infer_notify_route_from_status(
                command_prefix=command_prefix,
                preferred_channel=None,
                max_session_age_ms=max(0, safe_int(args.notify_max_session_age_ms, 1800000)),
            )
            if route:
                notify_channel = str(route.get("channel") or "")
                notify_target = str(route.get("target") or "")
                notify_result["targetFromSessionKey"] = route.get("key")
                notify_result["targetSessionAgeMs"] = route.get("ageMs")
                target_source = "status.recent.auto"
        except Exception as exc:
            warnings.append(f"notify auto route infer failed: {exc}")

    if notify_channel and notify_target:
        notify_message = (
            str(args.notify_message).strip()
            if isinstance(args.notify_message, str) and args.notify_message.strip()
            else (
                f"AutoQA run {run_id} 完成。结论：{go_no_go} / "
                f"{release.get('releaseDecision')}，风险：{release.get('riskLevel')}。"
            )
        )
        try:
            send_result = send_report_notification(
                command_prefix=command_prefix,
                channel=notify_channel,
                target=notify_target,
                message=notify_message,
                media_path=report_screenshot_path,
                account_id=args.notify_account,
            )
            notify_result.update(
                {
                    "requested": True,
                    "sent": True,
                    "channel": notify_channel,
                    "target": notify_target,
                    "targetSource": target_source,
                    "message": notify_message,
                    "result": send_result,
                }
            )
        except Exception as exc:
            warnings.append(f"notify send failed: {exc}")
            notify_result.update(
                {
                    "requested": True,
                    "sent": False,
                    "channel": notify_channel,
                    "target": notify_target,
                    "targetSource": target_source,
                    "error": str(exc),
                }
            )
    elif notify_requested and "sent" not in notify_result:
        warnings.append("notify requested but route resolution failed")
        notify_result.update(
            {
                "sent": False,
                "channel": notify_channel,
                "target": notify_target,
                "targetSource": target_source,
                "error": "target_resolution_failed",
            }
        )

    report["evidence"]["reportScreenshotPath"] = report_screenshot_path
    report["evidence"]["reportScreenshotCompatPath"] = report_screenshot_compat_path
    report["notifications"] = notify_result
    report["warnings"] = warnings
    write_json(report_json_path, report)
    write_text(report_html_path, build_report_html(report))

    print(json.dumps(
        {
            "ok": True,
            "runId": run_id,
            "goNoGo": go_no_go,
            "releaseDecision": release.get("releaseDecision"),
            "riskLevel": release.get("riskLevel"),
            "reviewConclusion": review_summary.get("reviewConclusion"),
            "reviewStatus": review_summary.get("reviewStatus"),
            "reviewMismatchCount": report.get("summary", {}).get("reviewMismatchCount"),
            "recheckStatus": report.get("recheck", {}).get("status"),
            "stepCoverageRate": report.get("summary", {}).get("coverage", {}).get("stepCoverageRate"),
            "returnEdgePassRate": report.get("summary", {}).get("coverage", {}).get("returnEdgePassRate"),
            "browserCommandPrefix": command_prefix,
            "resume": report.get("resume"),
            "failureBreakdown": report.get("summary", {}).get("failureBreakdown"),
            "gateViolations": report.get("summary", {}).get("gateViolations"),
            "artifactDir": str(artifact_dir),
            "reportDir": str(report_dir),
            "report": str(report_json_path),
            "reportHtml": str(report_html_path),
            "reportScreenshot": report_screenshot_path,
            "notification": notify_result,
            "fixPlan": str(fix_plan_path),
            "nextPrompt": str(next_prompt_path),
            "standbyPrompt": str(standby_path),
        },
        ensure_ascii=False,
        indent=2,
    ))

    return 0 if not failed_steps else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OpenClaw AutoQA MVP flow: execute scenario, collect evidence, generate reports."
    )
    parser.add_argument(
        "--scenario-id",
        help="Scenario id from registry (default registry: demo/scenarios/registry.json)",
    )
    parser.add_argument(
        "--scenario",
        help="Direct scenario path (locked by default; requires --allow-direct-scenario-path)",
    )
    parser.add_argument(
        "--scenario-registry",
        help="Path to scenario registry JSON (default: demo/scenarios/registry.json)",
    )
    parser.add_argument(
        "--scenario-var",
        action="append",
        default=[],
        help="Scenario variable override in key=value format; can be repeated",
    )
    parser.add_argument(
        "--allow-direct-scenario-path",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Allow direct --scenario path request (default: false; fallback to registry default unless forced)",
    )
    parser.add_argument(
        "--force-direct-scenario-path",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Force execute direct --scenario path (debug only; bypass default-id fallback)",
    )
    parser.add_argument("--run-id", help="Run id (default: UTC timestamp)")
    parser.add_argument("--browser-bin", default=DEFAULT_BROWSER_BIN, help="OpenClaw executable name")
    parser.add_argument(
        "--browser-cmd",
        help="Full browser command prefix (e.g. 'pnpm --dir src openclaw')",
    )
    parser.add_argument("--browser-profile", default="openclaw", help="Browser profile name")
    parser.add_argument("--output-root", default="demo", help="Output root directory")
    parser.add_argument(
        "--allow-external-scenario",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Allow scenario path outside repo demo/scenarios (default: false, prevent wrong-script runs)",
    )
    parser.add_argument(
        "--allow-legacy-scenario",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Allow scenario.meta.legacy=true files to run (default: false)",
    )
    parser.add_argument(
        "--cleanup-orphan-openclaw-processes",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Before run, auto-clean extra OpenClaw browser Chrome processes (default: true)",
    )
    parser.add_argument("--auto-start-browser", action="store_true", help="Call 'openclaw browser start' before run")
    parser.add_argument("--max-step-retries", type=int, default=1, help="Default retry count per step")
    parser.add_argument("--retry-wait-ms", type=int, default=800, help="Wait between retries (ms)")
    parser.add_argument(
        "--showcase-recheck",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run a second visual recheck pass and compare with main execution (default: true)",
    )
    parser.add_argument(
        "--showcase-continue-on-failure",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="During showcase recheck, continue after mismatched/failed steps (default: true)",
    )
    parser.add_argument(
        "--showcase-max-step-retries",
        type=int,
        default=0,
        help="Default retries for showcase recheck steps (default: 0)",
    )
    parser.add_argument(
        "--showcase-retry-wait-ms",
        type=int,
        default=500,
        help="Wait between showcase recheck retries (ms)",
    )
    parser.add_argument(
        "--showcase-time-budget-ms",
        type=int,
        default=90000,
        help="Soft time budget for showcase recheck; stop early when reached (default: 90000)",
    )
    parser.add_argument("--resume-from-step-id", help="Resume execution from the given step id")
    parser.add_argument("--resume-from-run-id", help="Resume from first failed step in this historical run id")
    parser.add_argument(
        "--resume-last-failed",
        action="store_true",
        help="Resume from latest failed run of the same scenario path",
    )
    parser.add_argument(
        "--health-check-interval",
        default="on-failure",
        choices=["off", "on-failure", "each-step"],
        help="Run browser health checks off/on-failure/each-step",
    )
    parser.add_argument(
        "--trace-start-mode",
        default="auto",
        choices=["auto", "immediate", "after-first-step"],
        help="Trace start timing strategy (auto avoids pre-step about:blank when first step is open/navigate)",
    )
    parser.add_argument("--no-trace", action="store_true", help="Disable trace start/stop")
    parser.add_argument(
        "--notify-channel",
        help="Send report screenshot notification via openclaw message send (discord/.../auto/current)",
    )
    parser.add_argument("--notify-target", help="Notification target (if empty, auto-detect from latest session)")
    parser.add_argument("--notify-account", help="Optional channel account id for notification")
    parser.add_argument("--notify-message", help="Optional message text for notification")
    parser.add_argument(
        "--notify-auto-current-channel",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-send report to latest active chat session when channel/target is not explicitly set",
    )
    parser.add_argument(
        "--notify-max-session-age-ms",
        type=int,
        default=1800000,
        help="Max recent session age for auto notify route detection (default: 30m)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logs to stderr")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(run_autoqa(parse_args()))
    except Exception as exc:
        print(f"[auto-qa] failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
