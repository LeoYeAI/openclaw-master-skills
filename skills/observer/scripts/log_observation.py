#!/usr/bin/env python3
"""
Clawsight UXR Observer — Log observation or survey record

Appends a JSON observation or survey record to the appropriate day's JSONL file.

Usage:
    echo '{"_type": "observation", "timestamp": "...", ...}' | python3 log_observation.py
    python3 log_observation.py --record '{"_type": "survey", ...}'
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

def get_base_path():
    """Get the UXR observer base directory."""
    return Path.home() / ".uxr-observer"

def get_today_dir():
    """Get today's session directory, creating if needed."""
    base = get_base_path()
    today = datetime.now().strftime("%Y-%m-%d")
    session_dir = base / "sessions" / today
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def log_record(record):
    """Append a record (observation or survey) to the appropriate JSONL file."""
    if not isinstance(record, dict):
        raise ValueError("Record must be a JSON object")
    
    record_type = record.get("_type", "observation")
    
    if record_type not in ("observation", "survey"):
        raise ValueError(f"Invalid _type: {record_type}. Must be 'observation' or 'survey'")
    
    # Route to correct file
    if record_type == "observation":
        filename = "observations.jsonl"
    else:
        filename = "surveys.jsonl"
    
    session_dir = get_today_dir()
    file_path = session_dir / filename
    
    # Append to JSONL
    with open(file_path, 'a') as f:
        f.write(json.dumps(record) + '\n')
    
    return str(file_path)

def main():
    parser = argparse.ArgumentParser(
        description="Log observation or survey record to Clawsight JSONL"
    )
    parser.add_argument(
        "--record",
        type=str,
        help="JSON record as string (alternative to stdin)"
    )
    
    args = parser.parse_args()
    
    # Get record from stdin or --record argument
    if args.record:
        record_str = args.record
    else:
        record_str = sys.stdin.read()
    
    if not record_str.strip():
        print("Error: No record provided (use stdin or --record)", file=sys.stderr)
        return 1
    
    try:
        record = json.loads(record_str)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1
    
    try:
        file_path = log_record(record)
        print(f"✓ Logged to {file_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
