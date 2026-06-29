#!/bin/bash
# recreate-venvs.sh — Recreate virtual environments from manifest after resurrection
# Part of proactive-amcp enforcer

set -euo pipefail

MANIFEST="${1:-$HOME/.openclaw/workspace/memory/venvs-manifest.json}"

if [[ ! -f "$MANIFEST" ]]; then
    echo "No venvs manifest found at $MANIFEST — skipping venv recreation"
    exit 0
fi

echo "=== Recreating venvs from manifest ==="

# Parse manifest and recreate each venv
python3 << EOF
import json
import subprocess
import os
from pathlib import Path

manifest_path = "$MANIFEST"

with open(manifest_path) as f:
    manifest = json.load(f)

for venv_config in manifest.get("venvs", []):
    base_path = Path(os.path.expanduser(venv_config["path"]))
    venv_path = base_path / ".venv"
    python_cmd = venv_config.get("python", "python3")
    
    print(f"\n--- {base_path} ---")
    
    # Check if venv exists and is functional
    pip_path = venv_path / "bin" / "pip"
    if pip_path.exists():
        print(f"  venv exists at {venv_path}")
        # Verify it works
        try:
            subprocess.run([str(pip_path), "--version"], check=True, capture_output=True)
            print("  venv is functional, skipping")
            continue
        except:
            print("  venv broken, recreating...")
    
    # Create venv
    print(f"  Creating venv with {python_cmd}...")
    subprocess.run([python_cmd, "-m", "venv", str(venv_path)], check=True)
    
    # Install packages
    pip_path = venv_path / "bin" / "pip"
    
    if "packages" in venv_config:
        packages = venv_config["packages"]
        print(f"  Installing packages: {packages}")
        subprocess.run([str(pip_path), "install", "-q"] + packages, check=True)
    
    elif "requirements" in venv_config:
        req_file = base_path / venv_config["requirements"]
        if req_file.exists():
            print(f"  Installing from {req_file}")
            subprocess.run([str(pip_path), "install", "-q", "-r", str(req_file)], check=True)
        else:
            print(f"  WARNING: requirements file not found: {req_file}")
    
    print(f"  ✓ venv ready")

print("\n=== Venv recreation complete ===")
EOF
