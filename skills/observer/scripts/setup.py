#!/usr/bin/env python3
"""
Clawsight UXR Observer — First-run setup

Creates ~/.uxr-observer/ directory structure, generates anonymous participant ID,
initializes config.json. Idempotent — safe to run multiple times.
"""

import os
import json
import sys
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

def generate_participant_id():
    """Generate a random anonymous participant hash (not user's real name)."""
    random_bytes = secrets.token_bytes(16)
    return hashlib.sha256(random_bytes).hexdigest()[:16]

def setup_directories(base_path):
    """Create directory structure."""
    directories = [
        base_path,
        base_path / "sessions",
        base_path / "reports",
    ]
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {d}")

def create_config(base_path):
    """Create or update config.json."""
    config_path = base_path / "config.json"
    
    # If config exists, don't overwrite it
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        print(f"✓ Config exists (no changes)")
        return config
    
    # Create new config
    config = {
        "study_active": True,
        "study_start_date": datetime.now().isoformat(),
        "survey_frequency": "after_each_task",
        "survey_style": "brief",
        "opted_out_topics": [],
        "participant_id": generate_participant_id()
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created config.json (participant_id: {config['participant_id'][:8]}...)")
    return config

def create_today_session_dirs(base_path):
    """Create today's session directory if it doesn't exist."""
    today = datetime.now().strftime("%Y-%m-%d")
    session_dir = base_path / "sessions" / today
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Create empty JSONL files if they don't exist
    observations_file = session_dir / "observations.jsonl"
    surveys_file = session_dir / "surveys.jsonl"
    
    for f in [observations_file, surveys_file]:
        if not f.exists():
            f.touch()
    
    print(f"✓ Session directory: {session_dir}")

def main():
    base_path = Path.home() / ".uxr-observer"
    
    print("=== Clawsight UXR Observer — Setup ===\n")
    
    try:
        setup_directories(base_path)
        config = create_config(base_path)
        create_today_session_dirs(base_path)
        
        print(f"\n✓ Setup complete!")
        print(f"  Data directory: {base_path}")
        print(f"  Study active: {config['study_active']}")
        print(f"  Participant ID: {config['participant_id']}")
        print(f"\nClawsight is ready. Start using OpenClaw normally.")
        print(f"Observation logging begins on first interaction.\n")
        
        return 0
    except Exception as e:
        print(f"\n✗ Setup failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
