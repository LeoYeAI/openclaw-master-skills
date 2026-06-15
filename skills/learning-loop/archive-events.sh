#!/bin/bash
# Learning Loop - Event Archiver
# Moves events older than N days to dated archive files.
# Keeps recent events in the hot path, archives old ones.
# Usage: bash archive-events.sh [workspace-dir] [days-to-keep]
# Default: keep last 30 days in events.jsonl, archive the rest

set -o pipefail

WORKSPACE="${1:-$(pwd)}"
DAYS_KEEP="${2:-30}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
ARCHIVE_DIR="$LEARNING_DIR/archive"

mkdir -p "$ARCHIVE_DIR"

python3 - "$EVENTS_FILE" "$ARCHIVE_DIR" "$DAYS_KEEP" << 'PYTHON'
import json, sys, os
from datetime import datetime, timedelta

events_file = sys.argv[1]
archive_dir = sys.argv[2]
days_keep = int(sys.argv[3])

cutoff = (datetime.now() - timedelta(days=days_keep)).isoformat()

try:
    with open(events_file) as f:
        events = [json.loads(l.strip()) for l in f if l.strip()]
except FileNotFoundError:
    print("No events file found.")
    sys.exit(0)

keep = []
archive = []

for e in events:
    ts = e.get('ts', '')
    if ts < cutoff:
        archive.append(e)
    else:
        keep.append(e)

if not archive:
    print(f"No events older than {days_keep} days. Nothing to archive.")
    print(f"Total events: {len(events)}, all within retention window.")
    sys.exit(0)

# Group archived events by month
by_month = {}
for e in archive:
    ts = e.get('ts', '')[:7]  # YYYY-MM
    if ts not in by_month:
        by_month[ts] = []
    by_month[ts].append(e)

# Write archive files
for month, month_events in by_month.items():
    archive_file = os.path.join(archive_dir, f"events-{month}.jsonl")
    # Append to existing archive for that month
    with open(archive_file, 'a') as f:
        for e in month_events:
            f.write(json.dumps(e) + '\n')
    print(f"Archived {len(month_events)} events to {archive_file}")

# Rewrite hot events file with only recent events
with open(events_file, 'w') as f:
    for e in keep:
        f.write(json.dumps(e) + '\n')

print(f"\nArchived: {len(archive)} events")
print(f"Retained: {len(keep)} events (last {days_keep} days)")
print(f"Events file: {os.path.getsize(events_file)} bytes")

PYTHON
