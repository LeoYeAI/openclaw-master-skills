#!/usr/bin/env python3
"""
fix-openclaw-session.py — Repair corrupted OpenClaw session transcripts.

Fixes the "unexpected tool_use_id found in tool_result blocks" error that occurs
when an assistant response is aborted mid-tool_use, leaving orphaned tool_results
that the Anthropic API rejects on every subsequent turn.

Root cause: When stopReason is "error" or "aborted" and a tool_use block has
partialJson, the built-in transcript repair inserts synthetic toolResults, but
the API still rejects them because the original tool_use is structurally broken.

Usage:
    python3 fix-openclaw-session.py [--fix] [--verbose] [--all-agents] [session_dir]

    --fix        Apply the fix (default is dry-run)
    --verbose    Show detailed output
    --all-agents Scan all agents, not just main
    session_dir  Override session directory (default: ~/.openclaw/agents/main/sessions)
"""

import json
import os
import re
import sys
import shutil
from datetime import datetime
from pathlib import Path

DEFAULT_SESSION_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")


def find_active_session(session_dir):
    """Find the active session ID from sessions.json."""
    sessions_json = os.path.join(session_dir, "sessions.json")
    if not os.path.exists(sessions_json):
        return None
    with open(sessions_json) as f:
        data = json.load(f)
    for key, val in data.items():
        if isinstance(val, dict) and "sessionId" in val:
            return val["sessionId"]
    return None


def is_corrupted_error(msg):
    """Check if a message is a stopReason=error with tool_use_id rejection."""
    if msg.get("type") != "message":
        return False
    inner = msg.get("message", {})
    stop = inner.get("stopReason", "")
    err = inner.get("errorMessage", "")
    if stop == "error" and "unexpected `tool_use_id` found in `tool_result` blocks" in err:
        return True
    return False


def is_aborted_with_partial(msg):
    """Check if a message is an aborted/errored assistant with partialJson tool calls."""
    if msg.get("type") != "message":
        return False
    inner = msg.get("message", {})
    if inner.get("role") != "assistant":
        return False
    stop = inner.get("stopReason", "")
    if stop not in ("error", "aborted"):
        return False
    for block in inner.get("content", []):
        if block.get("type") == "toolCall" and "partialJson" in block:
            return True
    return False


def is_synthetic_tool_result(msg):
    """Check if a message is a synthetic toolResult inserted by openclaw repair."""
    if msg.get("type") != "message":
        return False
    inner = msg.get("message", {})
    if inner.get("role") != "toolResult":
        return False
    for block in inner.get("content", []):
        if isinstance(block, dict) and "synthetic error result for transcript repair" in block.get("text", ""):
            return True
    return False


def scan_session(filepath, verbose=False):
    """Scan a session file for corruption. Returns (remove_ids, reparent_map, details)."""
    with open(filepath) as f:
        lines = f.readlines()

    remove_ids = set()
    reparent_map = {}  # child_id -> new_parent_id
    details = []
    id_to_line = {}
    id_to_parent = {}
    id_to_obj = {}

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg_id = obj.get("id", "")
        parent_id = obj.get("parentId", "")
        if msg_id:
            id_to_line[msg_id] = i + 1
            id_to_parent[msg_id] = parent_id
            id_to_obj[msg_id] = obj

    # Pass 1: Find broken assistant messages with partialJson
    for msg_id, obj in id_to_obj.items():
        if is_aborted_with_partial(obj):
            remove_ids.add(msg_id)
            details.append(f"BROKEN ASSISTANT (partialJson): id={msg_id} line={id_to_line[msg_id]}")

            # Collect tool_use IDs from this broken message
            broken_tool_ids = set()
            for block in obj.get("message", {}).get("content", []):
                if block.get("type") == "toolCall":
                    broken_tool_ids.add(block.get("id", ""))

            if verbose:
                details.append(f"  Tool IDs in broken message: {broken_tool_ids}")

    # Pass 2: Find synthetic toolResults whose parent is a removed message
    for msg_id, obj in id_to_obj.items():
        parent = id_to_parent.get(msg_id, "")
        if parent in remove_ids and is_synthetic_tool_result(obj):
            remove_ids.add(msg_id)
            details.append(f"SYNTHETIC TOOL_RESULT: id={msg_id} line={id_to_line[msg_id]} parent={parent}")

    # Pass 3: Find cascading error responses
    for msg_id, obj in id_to_obj.items():
        if is_corrupted_error(obj):
            remove_ids.add(msg_id)
            details.append(f"ERROR RESPONSE (400): id={msg_id} line={id_to_line[msg_id]}")

    # Pass 4: Compute reparenting — any message whose parent was removed
    # Walk up the chain to find the nearest surviving ancestor
    seen = set()  # Cycle guard

    def find_surviving_ancestor(msg_id):
        visited = set()
        current = msg_id
        while current in remove_ids:
            if current in visited:
                return None  # Cycle detected
            visited.add(current)
            current = id_to_parent.get(current, "")
            if not current:
                return None
        return current

    for msg_id, obj in id_to_obj.items():
        if msg_id in remove_ids:
            continue
        parent = id_to_parent.get(msg_id, "")
        if parent in remove_ids:
            new_parent = find_surviving_ancestor(parent)
            if new_parent:
                reparent_map[msg_id] = new_parent
                details.append(f"REPARENT: id={msg_id} line={id_to_line[msg_id]} {parent} -> {new_parent}")

    return remove_ids, reparent_map, details, len(lines)


def fix_session(filepath, remove_ids, reparent_map, verbose=False):
    """Apply fixes to a session file."""
    with open(filepath) as f:
        lines = f.readlines()

    output_lines = []
    removed = 0
    reparented = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            output_lines.append(stripped)
            continue

        msg_id = obj.get("id", "")

        if msg_id in remove_ids:
            removed += 1
            continue

        if msg_id in reparent_map:
            obj["parentId"] = reparent_map[msg_id]
            reparented += 1

        output_lines.append(json.dumps(obj, ensure_ascii=False))

    with open(filepath, "w") as f:
        for line in output_lines:
            f.write(line + "\n")

    return removed, reparented, len(output_lines)


def verify_session(filepath, verbose=False):
    """Post-fix verification: check no orphaned parents remain."""
    with open(filepath) as f:
        lines = f.readlines()

    all_ids = set()
    orphans = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
            msg_id = obj.get("id", "")
            if msg_id:
                all_ids.add(msg_id)
        except:
            pass

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
            parent = obj.get("parentId", "")
            msg_id = obj.get("id", "")
            if parent and parent not in all_ids:
                orphans.append((msg_id, parent))
        except:
            pass

    return orphans


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix corrupted OpenClaw session transcripts")
    parser.add_argument("session_dir", nargs="?", default=DEFAULT_SESSION_DIR,
                        help="Session directory (default: ~/.openclaw/agents/main/sessions)")
    parser.add_argument("--fix", action="store_true", help="Apply the fix (default is dry-run)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all-agents", action="store_true", help="Scan all agents")
    parser.add_argument("--session-id", help="Target a specific session ID")
    args = parser.parse_args()

    session_dir = args.session_dir

    if args.all_agents:
        agents_dir = os.path.expanduser("~/.openclaw/agents")
        dirs = []
        for agent in os.listdir(agents_dir):
            sdir = os.path.join(agents_dir, agent, "sessions")
            if os.path.isdir(sdir):
                dirs.append(sdir)
    else:
        dirs = [session_dir]

    for sdir in dirs:
        print(f"\n{'='*60}")
        print(f"Scanning: {sdir}")
        print(f"{'='*60}")

        if args.session_id:
            files = [os.path.join(sdir, f"{args.session_id}.jsonl")]
        else:
            # Find active session
            active = find_active_session(sdir)
            if active:
                files = [os.path.join(sdir, f"{active}.jsonl")]
                print(f"Active session: {active}")
            else:
                files = sorted(Path(sdir).glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
                files = [str(f) for f in files[:5]]  # Check 5 most recent
                print(f"No active session found, checking {len(files)} most recent files")

        for filepath in files:
            if not os.path.exists(filepath):
                print(f"  File not found: {filepath}")
                continue

            print(f"\n  File: {os.path.basename(filepath)}")
            try:
                remove_ids, reparent_map, details, total_lines = scan_session(filepath, args.verbose)
            except Exception as e:
                print(f"  ERROR scanning: {e}")
                continue

            if not remove_ids:
                print(f"  Status: CLEAN ({total_lines} lines)")
                continue

            print(f"  Status: CORRUPTED")
            print(f"  Lines to remove: {len(remove_ids)}")
            print(f"  References to reparent: {len(reparent_map)}")
            for d in details:
                print(f"    {d}")

            if args.fix:
                # Backup
                backup = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(filepath, backup)
                print(f"\n  Backup: {backup}")

                # Fix
                removed, reparented, final_lines = fix_session(filepath, remove_ids, reparent_map, args.verbose)
                print(f"  Fixed: removed {removed} lines, reparented {reparented} references")
                print(f"  Lines: {total_lines} -> {final_lines}")

                # Verify
                orphans = verify_session(filepath, args.verbose)
                if orphans:
                    print(f"  WARNING: {len(orphans)} orphaned parent references remain!")
                    for mid, pid in orphans[:5]:
                        print(f"    id={mid} -> missing parent {pid}")
                else:
                    print(f"  Verification: CLEAN")
            else:
                print(f"\n  Dry run — use --fix to apply")


if __name__ == "__main__":
    main()
