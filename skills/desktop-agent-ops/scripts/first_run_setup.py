#!/usr/bin/env python3
"""
Unified first-run setup for desktop-agent-ops.

This script is the SINGLE entry point that agents call on first use.
It is fully idempotent: each stage checks whether it already passed
and skips if so. Run with --force to redo everything.

Pipeline:
  1. Platform detection
  2. System dependencies (brew install cliclick tesseract on macOS)
  3. Python venv + pip dependencies (via uv)
  4. OS permission bootstrap (Screen Recording, Accessibility, Automation)
  5. Smoke test verification

Usage:
  python3 first_run_setup.py           # normal first-run
  python3 first_run_setup.py --check   # just report readiness (no changes)
  python3 first_run_setup.py --force   # redo all stages
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent

DEFAULT_HOME = Path(
    os.environ.get(
        "OPENCLAW_DESKTOP_AGENT_OPS_HOME",
        Path.home() / ".openclaw-desktop-agent-ops",
    )
).expanduser().resolve()

STATE_FILE = DEFAULT_HOME / "setup_state.json"
PERMISSION_FILE = DEFAULT_HOME / "permissions.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def jprint(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def run_cmd(cmd, timeout=120):
    """Run a command and return structured result."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "stdout": "", "stderr": "timeout"}
    except FileNotFoundError:
        return {"ok": False, "code": -1, "stdout": "", "stderr": f"command not found: {cmd[0]}"}


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def stage_done(state, stage_name):
    stage = state.get("stages", {}).get(stage_name, {})
    return stage.get("ok") is True


# ---------------------------------------------------------------------------
# Stage 1: Platform detection
# ---------------------------------------------------------------------------

def stage_platform(state, force):
    if not force and stage_done(state, "platform"):
        return state["stages"]["platform"]

    system = platform.system().lower()
    mac_ver = None
    linux_session = None

    if system == "darwin":
        try:
            mac_ver = platform.mac_ver()[0]
        except Exception:
            pass
    elif system == "linux":
        if os.environ.get("WAYLAND_DISPLAY"):
            linux_session = "wayland"
        elif os.environ.get("DISPLAY"):
            linux_session = "x11"

    return {
        "ok": True,
        "system": system,
        "mac_version": mac_ver,
        "linux_session": linux_session,
    }


# ---------------------------------------------------------------------------
# Stage 2: System dependencies (macOS: brew install cliclick tesseract)
# ---------------------------------------------------------------------------

MACOS_BREW_DEPS = ["cliclick", "tesseract"]

# Mapping of macOS/system locale prefixes to tesseract language codes
LOCALE_TO_TESS_LANG = {
    "zh-Hans": "chi_sim",      # Simplified Chinese
    "zh-Hant": "chi_tra",      # Traditional Chinese
    "zh": "chi_sim",           # Chinese fallback
    "ja": "jpn",               # Japanese
    "ko": "kor",               # Korean
    "ar": "ara",               # Arabic
    "hi": "hin",               # Hindi
    "th": "tha",               # Thai
    "vi": "vie",               # Vietnamese
    "ru": "rus",               # Russian
    "de": "deu",               # German
    "fr": "fra",               # French
    "es": "spa",               # Spanish
    "pt": "por",               # Portuguese
    "it": "ita",               # Italian
}


def stage_system_deps(state, force, system):
    if not force and stage_done(state, "system_deps"):
        return state["stages"]["system_deps"]

    if system != "darwin":
        # On Linux/Windows, system deps are handled differently; skip for now
        return {"ok": True, "skipped": True, "reason": f"no auto-install for {system}"}

    # Check if brew is available
    brew = shutil.which("brew")
    if not brew:
        return {
            "ok": False,
            "error": "homebrew_not_found",
            "hint": "Install Homebrew first: https://brew.sh",
        }

    results = {}
    all_ok = True
    for dep in MACOS_BREW_DEPS:
        # Check if already installed
        if shutil.which(dep):
            results[dep] = {"ok": True, "already_installed": True}
            continue

        # Install via brew
        install = run_cmd([brew, "install", dep], timeout=300)
        results[dep] = install
        if not install["ok"]:
            all_ok = False

    return {
        "ok": all_ok,
        "brew": brew,
        "deps": results,
    }


# ---------------------------------------------------------------------------
# Stage 2b: OCR language packs (auto-detect system locale)
# ---------------------------------------------------------------------------

def _detect_system_languages():
    """Detect system languages and return required tesseract language codes."""
    needed = set()
    system = platform.system().lower()

    if system == "darwin":
        # Read macOS preferred languages
        try:
            p = subprocess.run(
                ["defaults", "read", "-g", "AppleLanguages"],
                capture_output=True, text=True, timeout=5,
            )
            if p.returncode == 0:
                # Parse the plist-like output: ("zh-Hans-CN", "en-US", ...)
                import re
                langs = re.findall(r'"([^"]+)"', p.stdout)
                for lang in langs:
                    for prefix, tess_code in LOCALE_TO_TESS_LANG.items():
                        if lang.startswith(prefix):
                            needed.add(tess_code)
                            break
        except Exception:
            pass
    elif system == "windows":
        # Windows: use locale.getdefaultlocale() for system locale
        try:
            import locale
            def_locale = locale.getdefaultlocale()
            if def_locale and def_locale[0]:
                loc = def_locale[0]
                for prefix, tess_code in LOCALE_TO_TESS_LANG.items():
                    if loc.startswith(prefix):
                        needed.add(tess_code)
                # Also check underscore-based prefixes
                _UNDERSCORE_LOCALE = {
                    "zh_CN": "chi_sim", "zh_TW": "chi_tra",
                    "ja_JP": "jpn", "ko_KR": "kor",
                }
                for prefix, tess_code in _UNDERSCORE_LOCALE.items():
                    if loc.startswith(prefix):
                        needed.add(tess_code)
        except Exception:
            pass
    else:
        # Linux: check LANG/LANGUAGE env vars
        _UNDERSCORE_LOCALE = {
            "zh_CN": "chi_sim", "zh_TW": "chi_tra",
            "ja_JP": "jpn", "ko_KR": "kor",
        }
        for env_var in ["LANG", "LANGUAGE", "LC_ALL"]:
            val = os.environ.get(env_var, "")
            for prefix, tess_code in LOCALE_TO_TESS_LANG.items():
                if val.startswith(prefix):
                    needed.add(tess_code)
            for prefix, tess_code in _UNDERSCORE_LOCALE.items():
                if val.startswith(prefix):
                    needed.add(tess_code)

    return list(needed)


def _get_installed_tess_langs():
    """Get list of currently installed tesseract language codes."""
    try:
        p = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True, text=True, timeout=5,
        )
        if p.returncode == 0:
            # First line is path header, rest are lang codes
            lines = p.stderr.strip().splitlines() + p.stdout.strip().splitlines()
            langs = set()
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("List of") and "/" not in stripped:
                    langs.add(stripped)
            return langs
    except Exception:
        pass
    return set()


def stage_ocr_langs(state, force, system):
    """Install tesseract language packs for detected system languages."""
    if not force and stage_done(state, "ocr_langs"):
        return state["stages"]["ocr_langs"]

    if not shutil.which("tesseract"):
        return {"ok": True, "skipped": True, "reason": "tesseract not installed yet"}

    needed = _detect_system_languages()
    if not needed:
        return {"ok": True, "needed": [], "installed": [], "note": "system uses English only"}

    installed = _get_installed_tess_langs()
    missing = [lang for lang in needed if lang not in installed]

    if not missing:
        return {"ok": True, "needed": needed, "already_installed": True}

    if system != "darwin":
        return {
            "ok": True,
            "needed": needed,
            "missing": missing,
            "hint": f"Install manually: sudo apt install {' '.join('tesseract-ocr-' + m for m in missing)}",
        }

    # macOS: install tesseract-lang (contains ALL languages) or individual traineddata
    brew = shutil.which("brew")
    if not brew:
        return {"ok": False, "error": "homebrew_not_found", "missing": missing}

    # Install tesseract-lang meta package (fastest, ~50MB, all languages)
    install = run_cmd([brew, "install", "tesseract-lang"], timeout=300)
    if install["ok"]:
        return {
            "ok": True,
            "needed": needed,
            "installed_via": "tesseract-lang",
        }

    # Fallback: try downloading individual traineddata files
    tessdata_dir = None
    try:
        p = subprocess.run(["brew", "--prefix", "tesseract"], capture_output=True, text=True, timeout=5)
        if p.returncode == 0:
            tessdata_dir = Path(p.stdout.strip()) / "share" / "tessdata"
    except Exception:
        pass

    if not tessdata_dir or not tessdata_dir.exists():
        tessdata_dir = Path("/opt/homebrew/share/tessdata")

    results = {}
    for lang in missing:
        url = f"https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
        dl = run_cmd(["curl", "-fsSL", "-o", str(tessdata_dir / f"{lang}.traineddata"), url], timeout=60)
        results[lang] = dl

    all_ok = all(r.get("ok") for r in results.values())
    return {
        "ok": all_ok,
        "needed": needed,
        "installed_individually": results,
    }

PYTHON_DEPS = [
    "pillow",
    "pyautogui",
    "pygetwindow",
    "pytesseract",
    "opencv-python",
    "numpy",
]


def stage_python_env(state, force, system):
    if not force and stage_done(state, "python_env"):
        prev = state["stages"]["python_env"]
        # Verify the python binary still exists
        py_path = prev.get("python")
        if py_path and Path(py_path).exists():
            return prev

    venv_dir = DEFAULT_HOME / "venv"

    # Try uv first, fall back to python3 -m venv + pip
    uv = shutil.which("uv")
    if uv:
        return _setup_with_uv(uv, venv_dir, system)
    else:
        return _setup_with_pip(venv_dir, system)


def _setup_with_uv(uv, venv_dir, system):
    # Create venv
    create = run_cmd([uv, "venv", str(venv_dir)], timeout=60)
    if not create["ok"] and "already exists" not in create.get("stderr", ""):
        return {"ok": False, "stage": "create_venv", "tool": "uv", **create}

    py = venv_dir / ("Scripts/python.exe" if system == "windows" else "bin/python")
    if not py.exists():
        return {"ok": False, "error": f"python not found at {py}", "tool": "uv"}

    # Install deps
    install = run_cmd([uv, "pip", "install", "--python", str(py), *PYTHON_DEPS], timeout=300)
    if not install["ok"]:
        return {"ok": False, "stage": "install_deps", "tool": "uv", **install}

    return {
        "ok": True,
        "tool": "uv",
        "venv": str(venv_dir),
        "python": str(py),
        "deps": PYTHON_DEPS,
    }


def _setup_with_pip(venv_dir, system):
    # Create venv with stdlib
    if not venv_dir.exists():
        create = run_cmd([sys.executable, "-m", "venv", str(venv_dir)], timeout=60)
        if not create["ok"]:
            return {"ok": False, "stage": "create_venv", "tool": "pip", **create}

    py = venv_dir / ("Scripts/python.exe" if system == "windows" else "bin/python")
    if not py.exists():
        return {"ok": False, "error": f"python not found at {py}", "tool": "pip"}

    # Install deps with pip
    install = run_cmd([str(py), "-m", "pip", "install", "--quiet", *PYTHON_DEPS], timeout=300)
    if not install["ok"]:
        return {"ok": False, "stage": "install_deps", "tool": "pip", **install}

    return {
        "ok": True,
        "tool": "pip",
        "venv": str(venv_dir),
        "python": str(py),
        "deps": PYTHON_DEPS,
    }


# ---------------------------------------------------------------------------
# Stage 4: Permission bootstrap
# ---------------------------------------------------------------------------

def stage_permissions(state, force, system, python_exec):
    if not force and stage_done(state, "permissions"):
        return state["stages"]["permissions"]

    bootstrap = ROOT / "permission_bootstrap.py"
    cmd = [python_exec, str(bootstrap), "--python", python_exec]
    if force:
        cmd.append("--force")
    # On macOS, also try to open settings to prompt the user
    if system == "darwin":
        cmd.append("--open-settings")

    # Pass the venv python via env so sub-scripts use it
    env = os.environ.copy()
    env["DESKTOP_AGENT_OPS_PYTHON"] = python_exec
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        result = {
            "ok": p.returncode == 0,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        result = {"ok": False, "stdout": "", "stderr": "timeout"}

    # Parse the JSON output
    parsed = None
    if result["stdout"]:
        try:
            parsed = json.loads(result["stdout"])
        except Exception:
            pass

    if parsed:
        return {
            "ok": parsed.get("completed", False),
            "completed": parsed.get("completed", False),
            "failed_steps": parsed.get("failed_steps", []),
            "hints": parsed.get("hints", []),
            "instructions": parsed.get("instructions", []),
        }

    return {
        "ok": False,
        "error": "permission_bootstrap_parse_failed",
        "raw": result,
    }


# ---------------------------------------------------------------------------
# Stage 5: Smoke test
# ---------------------------------------------------------------------------

def stage_smoke_test(state, force, python_exec):
    if not force and stage_done(state, "smoke_test"):
        return state["stages"]["smoke_test"]

    smoke = ROOT / "smoke_test.py"
    # Pass the venv python via env so smoke_test.py and its sub-scripts use it
    env = os.environ.copy()
    env["DESKTOP_AGENT_OPS_PYTHON"] = python_exec
    try:
        p = subprocess.run(
            [python_exec, str(smoke)],
            capture_output=True, text=True, timeout=30, env=env,
        )
        result = {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        result = {"ok": False, "stdout": "", "stderr": "timeout"}
    except FileNotFoundError:
        result = {"ok": False, "stdout": "", "stderr": f"python not found: {python_exec}"}

    parsed = None
    if result["stdout"]:
        try:
            parsed = json.loads(result["stdout"])
        except Exception:
            pass

    if parsed:
        return {
            "ok": parsed.get("ready", False),
            "ready": parsed.get("ready", False),
            "move_verified": parsed.get("move_verified", False),
            "move_details": parsed.get("move_details"),
        }

    return {
        "ok": False,
        "error": "smoke_test_parse_failed",
        "raw": result,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="First-run setup for desktop-agent-ops")
    ap.add_argument("--check", action="store_true",
                     help="Report readiness without making any changes")
    ap.add_argument("--force", action="store_true",
                     help="Redo all stages even if previously completed")
    args = ap.parse_args()

    state = load_state()

    # --- Check-only mode ---
    if args.check:
        all_done = all(
            stage_done(state, s)
            for s in ["platform", "system_deps", "ocr_langs", "python_env", "permissions", "smoke_test"]
        )
        python_exec = (state.get("stages", {}).get("python_env", {}).get("python")
                       or os.environ.get("DESKTOP_AGENT_OPS_PYTHON", "python3"))
        jprint({
            "ok": True,
            "ready": all_done,
            "state_file": str(STATE_FILE),
            "python": python_exec,
            "stages": {
                name: {"ok": stage_done(state, name)}
                for name in ["platform", "system_deps", "ocr_langs", "python_env", "permissions", "smoke_test"]
            },
            "env": {
                "OPENCLAW_DESKTOP_AGENT_OPS_HOME": str(DEFAULT_HOME),
                "DESKTOP_AGENT_OPS_PYTHON": python_exec,
            },
        })
        return

    force = args.force
    stages = state.get("stages", {})

    # --- Stage 1: Platform ---
    platform_result = stage_platform(state, force)
    stages["platform"] = platform_result
    system = platform_result.get("system", platform.system().lower())

    # --- Stage 2: System deps ---
    sys_deps_result = stage_system_deps(state, force, system)
    stages["system_deps"] = sys_deps_result

    # --- Stage 2b: OCR language packs ---
    ocr_langs_result = stage_ocr_langs(state, force, system)
    stages["ocr_langs"] = ocr_langs_result

    # --- Stage 3: Python env ---
    python_env_result = stage_python_env(state, force, system)
    stages["python_env"] = python_env_result

    # Determine which python to use for remaining stages
    python_exec = python_env_result.get("python", "python3")

    # --- Stage 4: Permissions ---
    perm_result = stage_permissions(state, force, system, python_exec)
    stages["permissions"] = perm_result

    # --- Stage 5: Smoke test (only if all previous stages passed) ---
    all_prev_ok = all(stages[s].get("ok") for s in ["platform", "system_deps", "ocr_langs", "python_env", "permissions"])
    if all_prev_ok:
        smoke_result = stage_smoke_test(state, force, python_exec)
    else:
        smoke_result = {"ok": False, "skipped": True, "reason": "previous stages not all passed"}
    stages["smoke_test"] = smoke_result

    # --- Save state ---
    all_ok = all(stages[s].get("ok") for s in stages)
    new_state = {
        "ready": all_ok,
        "timestamp": int(time.time()),
        "platform": system,
        "stages": stages,
        "env": {
            "OPENCLAW_DESKTOP_AGENT_OPS_HOME": str(DEFAULT_HOME),
            "DESKTOP_AGENT_OPS_PYTHON": python_exec,
        },
    }
    save_state(new_state)

    # --- Output ---
    failed_stages = [name for name, s in stages.items() if not s.get("ok")]
    jprint({
        "ok": all_ok,
        "ready": all_ok,
        "platform": system,
        "state_file": str(STATE_FILE),
        "python": python_exec,
        "stages": stages,
        "failed_stages": failed_stages,
        "env": {
            "OPENCLAW_DESKTOP_AGENT_OPS_HOME": str(DEFAULT_HOME),
            "DESKTOP_AGENT_OPS_PYTHON": python_exec,
        },
        "next_steps": (
            []
            if all_ok
            else _build_next_steps(stages, system)
        ),
    })


def _build_next_steps(stages, system):
    """Generate actionable next-step instructions for failed stages."""
    steps = []
    if not stages.get("system_deps", {}).get("ok"):
        if system == "darwin":
            steps.append("Install system deps: brew install cliclick tesseract")
        elif system == "windows":
            steps.append("Install system deps: choco install tesseract (via Chocolatey) or download from https://github.com/UB-Mannheim/tesseract/wiki")
        elif system == "linux":
            steps.append("Install system deps: sudo apt install xdotool wmctrl tesseract-ocr")
    if not stages.get("python_env", {}).get("ok"):
        steps.append("Install uv (curl -LsSf https://astral.sh/uv/install.sh | sh) then re-run")
    if not stages.get("permissions", {}).get("ok"):
        hints = stages.get("permissions", {}).get("hints", [])
        if "screen_recording_permission_required" in hints:
            steps.append("Grant Screen Recording permission in System Settings > Privacy & Security")
        if "automation_permission_required" in hints:
            steps.append("Grant Automation permission in System Settings > Privacy & Security")
        if not hints:
            steps.append("Grant Screen Recording, Accessibility, and Automation permissions")
    if not stages.get("smoke_test", {}).get("ok"):
        if stages.get("smoke_test", {}).get("skipped"):
            steps.append("Fix previous stage failures first, then smoke test will run automatically")
        else:
            steps.append("Smoke test failed; run scripts/doctor.py for diagnostics")
    return steps


if __name__ == "__main__":
    main()
