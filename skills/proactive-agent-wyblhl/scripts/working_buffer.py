#!/usr/bin/env python3
"""
Working Buffer Protocol - Danger Zone Log for Proactive Agent

Captures EVERY exchange when context exceeds 60% threshold.
Survives compaction and enables recovery.

Usage:
    python working_buffer.py --append --human "message"
    python working_buffer.py --append --agent "summary"
    python working_buffer.py --read
    python working_buffer.py --check-context
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import re

# Working buffer file location
WORKING_BUFFER_FILE = Path("D:/OpenClaw/workspace/memory/working-buffer.md")

# Context threshold (percentage)
CONTEXT_THRESHOLD = 60


def get_context_percentage() -> float:
    """
    Get current context usage percentage.
    In production, this would query the session status API.
    For now, returns a placeholder that can be overridden.
    """
    # TODO: Integrate with OpenClaw session_status tool
    # For now, return 0 (caller should override based on actual context)
    return 0.0


def check_context_threshold() -> bool:
    """Check if context has exceeded the danger zone threshold."""
    percentage = get_context_percentage()
    return percentage >= CONTEXT_THRESHOLD


def init_buffer() -> str:
    """Initialize or reset the working buffer."""
    timestamp = datetime.now().isoformat()
    header = f"""# Working Buffer (Danger Zone Log)
**Status:** ACTIVE
**Started:** {timestamp}
**Context Threshold:** {CONTEXT_THRESHOLD}%

---

"""
    WORKING_BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
    WORKING_BUFFER_FILE.write_text(header, encoding='utf-8')
    return header


def append_human_message(message: str, timestamp: str = None) -> str:
    """Append a human message to the working buffer."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not WORKING_BUFFER_FILE.exists():
        init_buffer()
    
    entry = f"## [{timestamp}] Human\n{message}\n\n"
    
    with open(WORKING_BUFFER_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    return entry


def append_agent_summary(summary: str, timestamp: str = None) -> str:
    """Append an agent response summary to the working buffer."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not WORKING_BUFFER_FILE.exists():
        init_buffer()
    
    entry = f"## [{timestamp}] Agent (summary)\n{summary}\n\n"
    
    with open(WORKING_BUFFER_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    return entry


def append_exchange(human_msg: str, agent_summary: str = None, 
                    human_ts: str = None, agent_ts: str = None) -> dict:
    """Append a complete human-agent exchange to the buffer."""
    human_entry = append_human_message(human_msg, human_ts)
    agent_entry = None
    
    if agent_summary:
        agent_entry = append_agent_summary(agent_summary, agent_ts)
    
    return {
        'success': True,
        'human_entry': len(human_entry),
        'agent_entry': len(agent_entry) if agent_entry else 0,
        'buffer_file': str(WORKING_BUFFER_FILE)
    }


def read_buffer() -> str:
    """Read the entire working buffer."""
    if not WORKING_BUFFER_FILE.exists():
        return ""
    
    return WORKING_BUFFER_FILE.read_text(encoding='utf-8')


def extract_from_buffer(query: str = None) -> list:
    """
    Extract relevant context from the working buffer.
    If query provided, filter entries; otherwise return all.
    """
    if not WORKING_BUFFER_FILE.exists():
        return []
    
    content = WORKING_BUFFER_FILE.read_text(encoding='utf-8')
    
    # Parse entries
    entries = []
    current_entry = None
    
    for line in content.split('\n'):
        if line.startswith('## ['):
            if current_entry:
                entries.append(current_entry)
            current_entry = {'header': line, 'content': []}
        elif current_entry:
            current_entry['content'].append(line)
    
    if current_entry:
        entries.append(current_entry)
    
    # Filter by query if provided
    if query:
        filtered = []
        for entry in entries:
            full_text = entry['header'] + '\n'.join(entry['content'])
            if query.lower() in full_text.lower():
                filtered.append(entry)
        entries = filtered
    
    return entries


def clear_buffer():
    """Clear the working buffer (after successful compaction recovery)."""
    if WORKING_BUFFER_FILE.exists():
        timestamp = datetime.now().isoformat()
        footer = f"\n---\n**Cleared:** {timestamp}\n"
        with open(WORKING_BUFFER_FILE, 'a', encoding='utf-8') as f:
            f.write(footer)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Working Buffer Protocol')
    parser.add_argument('--append', action='store_true', help='Append to buffer')
    parser.add_argument('--read', action='store_true', help='Read buffer')
    parser.add_argument('--extract', type=str, help='Extract matching entries')
    parser.add_argument('--clear', action='store_true', help='Clear buffer')
    parser.add_argument('--check', action='store_true', help='Check context threshold')
    parser.add_argument('--human', type=str, help='Human message to append')
    parser.add_argument('--agent', type=str, help='Agent summary to append')
    
    args = parser.parse_args()
    
    if args.check:
        threshold_exceeded = check_context_threshold()
        result = {
            'context_percentage': get_context_percentage(),
            'threshold': CONTEXT_THRESHOLD,
            'danger_zone': threshold_exceeded
        }
        print(json.dumps(result, indent=2))
        return
    
    if args.read:
        content = read_buffer()
        print(content if content else "Buffer is empty")
        return
    
    if args.extract:
        entries = extract_from_buffer(args.extract)
        for entry in entries:
            print(entry['header'])
            print('\n'.join(entry['content']))
            print()
        return
    
    if args.clear:
        clear_buffer()
        print("Buffer cleared")
        return
    
    if args.append:
        if args.human:
            result = append_human_message(args.human)
            print(f"Appended human message: {len(result)} bytes")
        if args.agent:
            result = append_agent_summary(args.agent)
            print(f"Appended agent summary: {len(result)} bytes")
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
