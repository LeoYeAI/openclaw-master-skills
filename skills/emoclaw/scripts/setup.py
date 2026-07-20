#!/usr/bin/env python3
"""First-time setup for the emoclaw skill.

Copies the bundled emotion_model engine to the project root,
creates a venv, installs it, and copies the config template.

Usage:
    python skills/emoclaw/scripts/setup.py
    python skills/emoclaw/scripts/setup.py --no-config  # skip config copy
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent

# Bundled engine lives inside the skill
BUNDLED_ENGINE = SKILL_DIR / "engine" / "emotion_model"
BUNDLED_PYPROJECT = SKILL_DIR / "engine" / "pyproject.toml"

# Destination at project root
PACKAGE_DIR = REPO_ROOT / "emotion_model"
VENV_DIR = PACKAGE_DIR / ".venv"
CONFIG_TEMPLATE = SKILL_DIR / "assets" / "emoclaw.yaml"
CONFIG_DEST = REPO_ROOT / "emoclaw.yaml"


def main() -> None:
    skip_config = "--no-config" in sys.argv

    print("Emoclaw Setup")
    print(f"  Skill dir:  {SKILL_DIR}")
    print(f"  Repo root:  {REPO_ROOT}")
    print()

    # --- Copy bundled engine to project root ---
    if PACKAGE_DIR.exists() and (PACKAGE_DIR / "config.py").exists():
        print(f"  Engine already exists at {PACKAGE_DIR.relative_to(REPO_ROOT)}")
    elif BUNDLED_ENGINE.exists():
        print(f"  Copying bundled engine to {PACKAGE_DIR.relative_to(REPO_ROOT)}...")
        shutil.copytree(BUNDLED_ENGINE, PACKAGE_DIR, dirs_exist_ok=True)
        # Copy pyproject.toml to repo root (above emotion_model/) — matching
        # the engine/ layout where setuptools finds the emotion_model package.
        if BUNDLED_PYPROJECT.exists():
            shutil.copy2(BUNDLED_PYPROJECT, REPO_ROOT / "pyproject.toml")
        print("  Engine installed.")
    else:
        print(
            "ERROR: No bundled engine found and no existing engine at project root.\n"
            "\n"
            "Expected bundled engine at:\n"
            f"  {BUNDLED_ENGINE}\n"
            "\n"
            "This may indicate a corrupted skill package.\n"
            "Re-install via: clawdhub install emoclaw"
        )
        sys.exit(1)

    # --- Create venv ---
    if VENV_DIR.exists():
        print(f"  Venv already exists at {VENV_DIR.relative_to(REPO_ROOT)}")
    else:
        print(f"  Creating venv at {VENV_DIR.relative_to(REPO_ROOT)}...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True,
        )
        print("  Venv created.")

    # --- Install package ---
    pip = VENV_DIR / "bin" / "pip"
    if not pip.exists():
        pip = VENV_DIR / "Scripts" / "pip.exe"  # Windows fallback

    print("  Installing emotion_model package (editable)...")
    result = subprocess.run(
        [str(pip), "install", "-e", str(REPO_ROOT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR: pip install failed:\n{result.stderr}")
        sys.exit(1)
    print("  Package installed.")

    # --- Install dev dependencies ---
    print("  Installing dev dependencies (pytest)...")
    subprocess.run(
        [str(pip), "install", "pytest"],
        capture_output=True,
        text=True,
    )

    # --- Copy config template ---
    if not skip_config:
        if CONFIG_DEST.exists():
            print(f"  Config already exists at {CONFIG_DEST.relative_to(REPO_ROOT)}")
        else:
            shutil.copy2(CONFIG_TEMPLATE, CONFIG_DEST)
            print(f"  Copied config template to {CONFIG_DEST.relative_to(REPO_ROOT)}")
    else:
        print("  Skipping config copy (--no-config)")

    # --- Done ---
    print()
    print("Setup complete!")
    print()
    print("Next steps:")
    print(f"  1. Edit {CONFIG_DEST.relative_to(REPO_ROOT)} to customize for your agent")
    print("  2. Run the bootstrap pipeline:")
    print("     python skills/emoclaw/scripts/bootstrap.py")
    print("  3. Or extract + label + train manually (see SKILL.md)")
    print("  4. Add emotional state refresh to your HEARTBEAT.md:")
    print("     - task: Refresh emotional state")
    print("       schedule: session_start")
    print("       run: python skills/emoclaw/scripts/inject_state.py")
    print()
    print("To activate the venv manually:")
    print(f"  source {VENV_DIR.relative_to(REPO_ROOT)}/bin/activate")


if __name__ == "__main__":
    main()
