#!/usr/bin/env python3
"""
Universal runner for NotebookLM skill scripts
Ensures all scripts run with the correct virtual environment
"""

import hashlib
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


AGENT_PROCESS_HINTS = ("codex", "claude", "claude-code", "claude_code")
IGNORED_PROCESS_NAMES = {
    # Unix shells
    "bash",
    "dash",
    "fish",
    "sh",
    "zsh",
    # Windows shells
    "cmd",
    "cmd.exe",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
    # Interpreters
    "python",
    "python3",
    "python.exe",
    "node",
    "node.exe",
    "npm",
    "npm.cmd",
}

# Scripts that skip auth pre-check
SKIP_AUTH_CHECK = {
    "auth_manager.py",      # Handles its own auth
    "cleanup_manager.py",   # Cleanup doesn't need auth
    "setup_environment.py", # Setup script
    "init_platform.py",     # Platform initialization
}

# Timeouts for long-running operations (in seconds)
TIMEOUT_VENV_SETUP = 600      # 10 minutes
TIMEOUT_PIP_INSTALL = 600     # 10 minutes
TIMEOUT_NPM_INSTALL = 600     # 10 minutes
TIMEOUT_AUTH_SETUP = 600      # 10 minutes (user interaction)


def _get_process_info(pid: int):
    """Return (ppid, command) for a PID, or None on failure."""
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid=,ppid=,command="],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    line = result.stdout.strip()
    if not line:
        return None

    parts = line.split(None, 2)
    if len(parts) < 2:
        return None

    try:
        ppid = int(parts[1])
    except ValueError:
        return None

    command = parts[2] if len(parts) > 2 else ""
    return ppid, command


def _looks_like_agent(command: str) -> bool:
    lower = command.lower()
    return any(hint in lower for hint in AGENT_PROCESS_HINTS)


def _is_ignored_command(command: str) -> bool:
    if not command:
        return True
    base = Path(command.split()[0]).name.lower()
    return base in IGNORED_PROCESS_NAMES


def _detect_owner_pid():
    """Best-effort owner PID detection for CLI agents."""
    if os.name == "nt":
        return os.getppid()

    pid = os.getppid()
    fallback_pid = None
    seen = set()

    for _ in range(20):
        if pid <= 1 or pid in seen:
            break
        seen.add(pid)

        info = _get_process_info(pid)
        if not info:
            break

        ppid, command = info
        if _looks_like_agent(command):
            return pid
        if fallback_pid is None and not _is_ignored_command(command):
            fallback_pid = pid

        if not ppid or ppid == pid:
            break
        pid = ppid

    return fallback_pid


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"

    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"

    return venv_python


def ensure_venv():
    """Ensure virtual environment exists"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    setup_script = skill_dir / "scripts" / "setup_environment.py"

    # Check if venv exists
    if not venv_dir.exists():
        print("🔧 First-time setup: Creating virtual environment...")
        print("   This may take a minute...")

        # Run setup with system Python
        try:
            result = subprocess.run(
                [sys.executable, str(setup_script)],
                timeout=TIMEOUT_VENV_SETUP
            )
        except subprocess.TimeoutExpired:
            print(f"❌ Venv setup timed out after {TIMEOUT_VENV_SETUP}s")
            sys.exit(1)

        if result.returncode != 0:
            print("❌ Failed to set up environment")
            sys.exit(1)

        print("✅ Environment ready!")

    return get_venv_python()


def _get_requirements_hash(requirements_file: Path) -> str:
    """Compute SHA256 hash of requirements.txt"""
    if not requirements_file.exists():
        return ""
    content = requirements_file.read_bytes()
    return hashlib.sha256(content).hexdigest()


def ensure_pip_deps():
    """Ensure pip dependencies are installed and up-to-date"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    requirements_file = skill_dir / "requirements.txt"
    hash_file = venv_dir / ".requirements.hash"

    if not requirements_file.exists():
        return  # No requirements file

    current_hash = _get_requirements_hash(requirements_file)

    # Check if hash matches
    if hash_file.exists():
        stored_hash = hash_file.read_text().strip()
        if stored_hash == current_hash:
            return  # Dependencies up-to-date

    # Install/update dependencies
    print("📦 Installing Python dependencies...")
    venv_python = get_venv_python()
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file), "--quiet"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PIP_INSTALL
        )
    except subprocess.TimeoutExpired:
        print(f"⚠️ pip install timed out after {TIMEOUT_PIP_INSTALL}s")
        print("   Try running manually: pip install -r requirements.txt")
        return

    if result.returncode != 0:
        print(f"⚠️ pip install failed: {result.stderr}")
        print("   Try running: pip install -r requirements.txt")
    else:
        # Save hash on success
        hash_file.write_text(current_hash)
        print("✅ Python dependencies installed")
        # Install Patchright browser if patchright was installed
        _ensure_patchright_browser(venv_python)


def _ensure_patchright_browser(venv_python: Path):
    """Ensure Patchright browser is installed for Google auth."""
    skill_dir = Path(__file__).parent.parent
    patchright_marker = skill_dir / ".venv" / ".patchright-browser-installed"

    # Skip if already installed
    if patchright_marker.exists():
        return

    # Check if patchright is installed
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "import patchright"],
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            return  # Patchright not installed, skip
    except Exception:
        return

    # Install Patchright browser
    print("📦 Installing Patchright browser for Google auth...")
    try:
        patchright_cmd = skill_dir / ".venv" / "bin" / "patchright"
        if os.name == 'nt':
            patchright_cmd = skill_dir / ".venv" / "Scripts" / "patchright.exe"

        result = subprocess.run(
            [str(patchright_cmd), "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for browser download
        )
        if result.returncode == 0:
            patchright_marker.write_text("installed")
            print("✅ Patchright browser installed")
        else:
            print(f"⚠️ Patchright browser install failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Patchright browser install timed out")
    except Exception as e:
        print(f"⚠️ Patchright browser install error: {e}")


def _get_npm_command():
    """Get the npm command for the current platform."""
    if os.name == 'nt':  # Windows
        return "npm.cmd"
    return "npm"


def ensure_node_deps():
    """Ensure Node.js dependencies are installed"""
    skill_dir = Path(__file__).parent.parent
    package_json = skill_dir / "package.json"
    node_modules = skill_dir / "node_modules"

    if not package_json.exists():
        return  # No Node.js dependencies needed

    if not node_modules.exists():
        print("📦 Installing agent-browser...")
        npm_cmd = _get_npm_command()
        try:
            result = subprocess.run(
                [npm_cmd, "install"],
                cwd=str(skill_dir),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_NPM_INSTALL
            )
        except subprocess.TimeoutExpired:
            print(f"⚠️ npm install timed out after {TIMEOUT_NPM_INSTALL}s")
            print("   Please run manually: npm install")
            return

        if result.returncode != 0:
            print(f"⚠️ npm install failed: {result.stderr}")
            print("   Please ensure Node.js and npm are installed")
        else:
            print("✅ agent-browser installed")


def _prompt_auth_setup():
    """Trigger interactive auth setup, return True on success."""
    print("🔐 Google authentication required. Opening browser...")
    print("   Please complete login in the browser window.")
    print(f"   (Timeout: {TIMEOUT_AUTH_SETUP // 60} minutes)")
    print()

    venv_python = get_venv_python()
    skill_dir = Path(__file__).parent.parent
    auth_script = skill_dir / "scripts" / "auth_manager.py"

    try:
        result = subprocess.run(
            [str(venv_python), str(auth_script), "setup", "--service", "google"],
            timeout=TIMEOUT_AUTH_SETUP
        )
    except subprocess.TimeoutExpired:
        print(f"❌ Authentication timed out after {TIMEOUT_AUTH_SETUP // 60} minutes.")
        print("   Please try again: python scripts/run.py auth_manager.py setup")
        sys.exit(1)

    if result.returncode != 0:
        print("❌ Authentication failed. Cannot proceed.")
        sys.exit(1)

    print()  # Blank line after auth success
    return True


def _prompt_auth_reauth():
    """Trigger interactive reauth for expired credentials, return True on success."""
    print("🔐 Re-authenticating expired Google session...")
    print("   Please complete login in the browser window.")
    print(f"   (Timeout: {TIMEOUT_AUTH_SETUP // 60} minutes)")
    print()

    venv_python = get_venv_python()
    skill_dir = Path(__file__).parent.parent
    auth_script = skill_dir / "scripts" / "auth_manager.py"

    try:
        result = subprocess.run(
            [str(venv_python), str(auth_script), "reauth", "--service", "google"],
            timeout=TIMEOUT_AUTH_SETUP
        )
    except subprocess.TimeoutExpired:
        print(f"❌ Re-authentication timed out after {TIMEOUT_AUTH_SETUP // 60} minutes.")
        print("   Please try again: python scripts/run.py auth_manager.py reauth")
        sys.exit(1)

    if result.returncode != 0:
        print("❌ Re-authentication failed. Cannot proceed.")
        sys.exit(1)

    print()  # Blank line after auth success
    return True


def ensure_google_auth():
    """Ensure Google authentication is valid and fresh, prompting setup if needed."""
    skill_dir = Path(__file__).parent.parent
    TTL_DAYS = 10

    # Multi-account structure: check google/index.json first
    index_file = skill_dir / "data" / "auth" / "google" / "index.json"
    legacy_auth_file = skill_dir / "data" / "auth" / "google.json"

    if index_file.exists():
        # Multi-account mode: find active account's auth file
        try:
            index_data = json.loads(index_file.read_text())
            active_index = index_data.get("active_account")
            if active_index:
                for acc in index_data.get("accounts", []):
                    if acc.get("index") == active_index:
                        auth_file = skill_dir / "data" / "auth" / "google" / acc.get("file", "")
                        break
                else:
                    auth_file = None
            else:
                auth_file = None
        except (json.JSONDecodeError, IOError):
            auth_file = None
    elif legacy_auth_file.exists():
        auth_file = legacy_auth_file
    else:
        auth_file = None

    # Check 1: File exists
    if not auth_file or not auth_file.exists():
        return _prompt_auth_setup()

    # Check 2: Valid structure
    try:
        payload = json.loads(auth_file.read_text())
    except (json.JSONDecodeError, IOError):
        return _prompt_auth_setup()

    if not payload.get("cookies") and not payload.get("origins"):
        return _prompt_auth_setup()

    # Check 3: Freshness (notebooklm_updated_at within TTL)
    updated_at = payload.get("notebooklm_updated_at")
    if updated_at:
        try:
            timestamp = datetime.fromisoformat(updated_at)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - timestamp
            if age > timedelta(days=TTL_DAYS):
                print(f"⚠️ Google auth expired ({age.days} days old)")
                return _prompt_auth_reauth()  # Reauth existing account, not fresh setup
        except ValueError:
            pass  # Invalid timestamp, but cookies exist - proceed

    # All checks passed - silent success
    return True


def should_skip_auth_check(script_name: str, script_args: list) -> bool:
    """Determine if this invocation should skip auth pre-check."""
    # Skip for help flags
    if "--help" in script_args or "-h" in script_args:
        return True

    # Skip for scripts that don't need auth
    if script_name in SKIP_AUTH_CHECK:
        return True

    return False


def ensure_owner_pid_env():
    """Ensure agent-browser owner PID is set for watchdog cleanup"""
    if not os.environ.get("AGENT_BROWSER_OWNER_PID"):
        owner_pid = _detect_owner_pid()
        if owner_pid is None:
            owner_pid = os.getppid()
        os.environ["AGENT_BROWSER_OWNER_PID"] = str(owner_pid)


def main():
    """Main runner"""
    # Handle init command for platform initialization
    if len(sys.argv) >= 2 and sys.argv[1] == "init":
        skill_dir = Path(__file__).parent.parent
        init_script = skill_dir / "scripts" / "init_platform.py"

        # Pass remaining args to init_platform.py
        init_args = sys.argv[2:]
        cmd = [sys.executable, str(init_script)] + init_args
        result = subprocess.run(cmd)
        sys.exit(result.returncode)

    # Handle --check-deps flag for pre-flight dependency check
    if len(sys.argv) >= 2 and sys.argv[1] == "--check-deps":
        print("🔍 Checking dependencies...")
        skill_dir = Path(__file__).parent.parent

        # Check Python venv
        venv_python = get_venv_python()
        if not venv_python.exists():
            print("📦 Setting up Python environment...")
            ensure_venv()
        else:
            print("✅ Python environment ready")

        # Check pip dependencies
        ensure_pip_deps()

        # Check Node.js deps
        node_modules = skill_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing Node.js dependencies...")
            ensure_node_deps()
        else:
            print("✅ Node.js dependencies ready")

        print("✅ All dependencies installed")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  ask_question.py    - Query NotebookLM")
        print("  notebook_manager.py - Manage notebook library")
        print("  session_manager.py  - Manage sessions")
        print("  auth_manager.py     - Handle authentication")
        print("  cleanup_manager.py  - Clean up skill data")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Handle both "scripts/script.py" and "script.py" formats
    if script_name.startswith('scripts/'):
        # Remove the scripts/ prefix if provided
        script_name = script_name[8:]  # len('scripts/') = 8

    # Ensure .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get script path
    skill_dir = Path(__file__).parent.parent
    script_path = skill_dir / "scripts" / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        print(f"   Working directory: {Path.cwd()}")
        print(f"   Skill directory: {skill_dir}")
        print(f"   Looked for: {script_path}")
        sys.exit(1)

    # Ensure venv exists and get Python executable
    venv_python = ensure_venv()
    ensure_pip_deps()
    ensure_node_deps()
    ensure_owner_pid_env()

    # Auth pre-check (unless skipped)
    if not should_skip_auth_check(script_name, script_args):
        ensure_google_auth()

    # Build command
    cmd = [str(venv_python), str(script_path)] + script_args

    # Run the script
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
