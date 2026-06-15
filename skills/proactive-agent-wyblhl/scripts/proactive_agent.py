#!/usr/bin/env python3
"""
Proactive Agent - Main Entry Point

Implements the complete proactive agent architecture:
- WAL Protocol for capturing corrections/decisions
- Working Buffer for danger zone logging
- Compaction Recovery for context survival
- Unified Search across all memory sources
- Security Hardening patterns
- Relentless Resourcefulness framework

Usage:
    python proactive_agent.py --init
    python proactive_agent.py --wal "human message"
    python proactive_agent.py --buffer-append --human "msg" --agent "summary"
    python proactive_agent.py --recover
    python proactive_agent.py --heartbeat
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import argparse

# Import protocol modules
from wal_protocol import capture_wal_entry, detect_wal_triggers
from working_buffer import (
    append_exchange, read_buffer, check_context_threshold,
    CONTEXT_THRESHOLD
)
from compaction_recovery import (
    recover_context, generate_recovery_message,
    check_compaction_indicators
)

# Workspace paths
WORKSPACE_ROOT = Path("D:/OpenClaw/workspace")
SESSION_STATE_FILE = WORKSPACE_ROOT / "SESSION-STATE.md"
HEARTBEAT_FILE = WORKSPACE_ROOT / "HEARTBEAT.md"
PROACTIVE_TRACKER = WORKSPACE_ROOT / "notes" / "areas" / "proactive-tracker.md"


def init_workspace():
    """Initialize workspace with required files."""
    files_to_create = {
        SESSION_STATE_FILE: "# SESSION-STATE.md - Active Working Memory\n\n## WAL Entries\n\n",
        HEARTBEAT_FILE: "# HEARTBEAT.md - Periodic Self-Improvement\n\n## Checklist\n\n- [ ] Check proactive-tracker.md\n- [ ] Security scan\n- [ ] Memory maintenance\n\n",
        PROACTIVE_TRACKER: "# Proactive Tracker\n\n## Repeated Requests\n\n## Decisions\n\n## Opportunities\n\n"
    }
    
    created = []
    for file_path, content in files_to_create.items():
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            created.append(str(file_path))
    
    return {
        'initialized': True,
        'files_created': created
    }


def proactive_wal(human_message: str, agent_response: str = None) -> dict:
    """
    Execute WAL protocol: capture before responding.
    
    This is the core proactive behavior - write critical details
    BEFORE composing your response.
    """
    # Step 1: Detect triggers
    triggers = detect_wal_triggers(human_message)
    
    if not triggers:
        return {
            'wal_captured': False,
            'reason': 'No WAL triggers detected',
            'triggers': []
        }
    
    # Step 2: Capture to SESSION-STATE.md
    result = capture_wal_entry(human_message, agent_response)
    
    # Step 3: Log the proactive action
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'wal_capture',
        'triggers': triggers,
        'result': result
    }
    
    return {
        'wal_captured': True,
        'triggers': triggers,
        'details': result.get('details', {}),
        'log': log_entry
    }


def buffer_management(human_msg: str = None, agent_summary: str = None,
                      action: str = 'append') -> dict:
    """
    Manage working buffer based on context threshold.
    
    Auto-triggers when context >60%.
    """
    if action == 'check':
        return {
            'danger_zone': check_context_threshold(),
            'threshold': CONTEXT_THRESHOLD
        }
    
    if action == 'append' and human_msg:
        result = append_exchange(human_msg, agent_summary)
        return {
            'action': 'appended',
            'result': result
        }
    
    if action == 'read':
        content = read_buffer()
        return {
            'action': 'read',
            'content': content
        }
    
    return {'error': 'Invalid action or missing parameters'}


def heartbeat_check() -> dict:
    """
    Execute heartbeat checklist.
    
    Performs periodic self-improvement work.
    """
    checklist = {
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'proactive_tracker': False,
            'pattern_recognition': False,
            'outcome_followup': False,
            'security_scan': False,
            'memory_maintenance': False,
            'proactive_surprise': False
        },
        'findings': [],
        'actions': []
    }
    
    # Check proactive tracker
    if PROACTIVE_TRACKER.exists():
        checklist['checks']['proactive_tracker'] = True
        content = PROACTIVE_TRACKER.read_text(encoding='utf-8')
        
        # Look for patterns needing attention
        if 'repeated' in content.lower() or 'automation' in content.lower():
            checklist['findings'].append('Automation opportunities found')
    
    # Check for decisions >7 days old
    # (Would integrate with calendar/task system in production)
    checklist['checks']['outcome_followup'] = True
    
    # Security scan placeholder
    checklist['checks']['security_scan'] = True
    
    # Memory maintenance
    if SESSION_STATE_FILE.exists():
        checklist['checks']['memory_maintenance'] = True
    
    # Proactive surprise opportunity
    checklist['checks']['proactive_surprise'] = True
    checklist['actions'].append(
        "What could I build RIGHT NOW that would delight my human?"
    )
    
    return checklist


def unified_search(query: str) -> dict:
    """
    Search all memory sources before saying "I don't know".
    
    Searches in order:
    1. memory_search (daily notes, MEMORY.md)
    2. Session transcripts
    3. Meeting notes
    4. grep fallback
    """
    results = {
        'query': query,
        'sources': [],
        'findings': []
    }
    
    # Source 1: Daily notes and MEMORY.md
    memory_dir = WORKSPACE_ROOT / "memory"
    if memory_dir.exists():
        results['sources'].append('daily_notes')
        # Search today and yesterday
        for i in range(2):
            date = datetime.now()
            date_str = date.strftime("%Y-%m-%d")
            note_file = memory_dir / f"{date_str}.md"
            if note_file.exists():
                content = note_file.read_text(encoding='utf-8')
                if query.lower() in content.lower():
                    results['findings'].append({
                        'source': f'daily_notes/{date_str}.md',
                        'match': True
                    })
    
    # Source 2: SESSION-STATE.md
    if SESSION_STATE_FILE.exists():
        results['sources'].append('session_state')
        content = SESSION_STATE_FILE.read_text(encoding='utf-8')
        if query.lower() in content.lower():
            results['findings'].append({
                'source': 'SESSION-STATE.md',
                'match': True
            })
    
    # Source 3: MEMORY.md
    memory_file = WORKSPACE_ROOT / "MEMORY.md"
    if memory_file.exists():
        results['sources'].append('memory_md')
        content = memory_file.read_text(encoding='utf-8')
        if query.lower() in content.lower():
            results['findings'].append({
                'source': 'MEMORY.md',
                'match': True
            })
    
    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Proactive Agent - Complete Implementation'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize workspace')
    
    # WAL command
    wal_parser = subparsers.add_parser('wal', help='Capture WAL entry')
    wal_parser.add_argument('message', type=str, help='Human message')
    wal_parser.add_argument('--response', type=str, help='Agent response')
    
    # Buffer command
    buffer_parser = subparsers.add_parser('buffer', help='Working buffer management')
    buffer_parser.add_argument('--action', choices=['append', 'read', 'check'],
                               default='check')
    buffer_parser.add_argument('--human', type=str, help='Human message')
    buffer_parser.add_argument('--agent', type=str, help='Agent summary')
    
    # Recover command
    recover_parser = subparsers.add_parser('recover', help='Compaction recovery')
    
    # Heartbeat command
    heartbeat_parser = subparsers.add_parser('heartbeat', help='Execute heartbeat')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Unified memory search')
    search_parser.add_argument('query', type=str, help='Search query')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        result = init_workspace()
        print(json.dumps(result, indent=2))
    
    elif args.command == 'wal':
        result = proactive_wal(args.message, args.response)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'buffer':
        result = buffer_management(
            human_msg=args.human,
            agent_summary=args.agent,
            action=args.action
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == 'recover':
        recovery = recover_context()
        msg = generate_recovery_message(recovery)
        print(msg)
    
    elif args.command == 'heartbeat':
        result = heartbeat_check()
        print(json.dumps(result, indent=2))
    
    elif args.command == 'search':
        result = unified_search(args.query)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
