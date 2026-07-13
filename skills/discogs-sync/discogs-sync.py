"""Entry-point script for running discogs-sync without pip install.

On first run, automatically creates a local venv and installs dependencies.
Works on macOS (Homebrew), Linux, and Windows without manual pip invocation.
"""

import os
import subprocess
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_VENV_DIR = os.path.join(_SCRIPT_DIR, ".deps")
_REQUIREMENTS = os.path.join(_SCRIPT_DIR, "requirements.txt")

# Determine venv python path (Windows uses Scripts/, Unix uses bin/)
if sys.platform == "win32":
    _VENV_PYTHON = os.path.join(_VENV_DIR, "Scripts", "python.exe")
else:
    _VENV_PYTHON = os.path.join(_VENV_DIR, "bin", "python3")


def _bootstrap_venv():
    """Create a local venv and install requirements."""
    print("First run: installing dependencies...", file=sys.stderr)

    # Create venv
    subprocess.check_call(
        [sys.executable, "-m", "venv", _VENV_DIR],
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    # Install requirements into the venv
    pip_cmd = [_VENV_PYTHON, "-m", "pip", "install", "-q", "-r", _REQUIREMENTS]
    subprocess.check_call(pip_cmd, stdout=sys.stderr, stderr=sys.stderr)

    print("Dependencies installed.", file=sys.stderr)


def _reexec_in_venv():
    """Re-execute this script using the venv's Python."""
    os.execv(_VENV_PYTHON, [_VENV_PYTHON, __file__] + sys.argv[1:])


# If we're not already running inside the venv, bootstrap and re-exec.
if os.path.isfile(_VENV_PYTHON):
    # Venv exists — if we're not in it, switch to it.
    if os.path.abspath(sys.executable) != os.path.abspath(_VENV_PYTHON):
        _reexec_in_venv()
else:
    # No venv yet — create it, then re-exec.
    _bootstrap_venv()
    _reexec_in_venv()

# At this point we're running inside the venv.
sys.path.insert(0, os.path.join(_SCRIPT_DIR, "src"))

from discogs_sync.cli import main

main()
