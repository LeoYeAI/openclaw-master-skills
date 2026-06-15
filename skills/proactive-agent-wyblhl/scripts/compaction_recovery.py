#!/usr/bin/env python3
"""
Compaction Recovery Protocol - Recover from context truncation

Step-by-step recovery when context gets compacted or truncated.
Reads working buffer, session state, and memory files to reconstruct context.

Usage:
    python compaction_recovery.py --recover
    python compaction_recovery.py --status
    python compaction_recovery.py --extract-from-buffer
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

# File locations
WORKSPACE_ROOT = Path("D:/OpenClaw/workspace")
WORKING_BUFFER_FILE = WORKSPACE_ROOT / "memory" / "working-buffer.md"
SESSION_STATE_FILE = WORKSPACE_ROOT / "SESSION-STATE.md"
MEMORY_FILE = WORKSPACE_ROOT / "MEMORY.md"
MEMORY_DIR = WORKSPACE_ROOT / "memory"

# Recovery state file
RECOVERY_STATE_FILE = WORKSPACE_ROOT / "notes" / "compaction-state.json"


def check_compaction_indicators(transcript: str = None) -> dict:
    """
    Check for compaction/truncation indicators.
    
    Indicators:
    - Session starts with <summary> tag
    - Message contains "truncated", "context limits"
    - Human asks "where were we?", "continue"
    """
    indicators = {
        'summary_tag': False,
        'truncation_mentioned': False,
        'continuation_request': False,
        'missing_context': False
    }
    
    if not transcript:
        return indicators
    
    transcript_lower = transcript.lower()
    
    indicators['summary_tag'] = '<summary>' in transcript_lower
    indicators['truncation_mentioned'] = any([
        'truncated' in transcript_lower,
        'context limit' in transcript_lower,
        'compacted' in transcript_lower
    ])
    indicators['continuation_request'] = any([
        'where were we' in transcript_lower,
        'continue' in transcript_lower,
        'what were we doing' in transcript_lower,
        'what was i saying' in transcript_lower
    ])
    
    return indicators


def read_working_buffer() -> str:
    """Read the working buffer (danger zone log)."""
    if not WORKING_BUFFER_FILE.exists():
        return ""
    return WORKING_BUFFER_FILE.read_text(encoding='utf-8')


def read_session_state() -> str:
    """Read the session state file."""
    if not SESSION_STATE_FILE.exists():
        return ""
    return SESSION_STATE_FILE.read_text(encoding='utf-8')


def get_recent_daily_notes(days: int = 2) -> list:
    """Get daily notes from the last N days."""
    notes = []
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        note_file = MEMORY_DIR / f"{date_str}.md"
        
        if note_file.exists():
            notes.append({
                'date': date_str,
                'content': note_file.read_text(encoding='utf-8')
            })
    
    return notes


def extract_context_from_buffer(buffer_content: str) -> dict:
    """
    Extract important context from working buffer.
    Returns structured context for recovery.
    """
    if not buffer_content:
        return {}
    
    extracted = {
        'tasks': [],
        'decisions': [],
        'human_messages': [],
        'agent_summaries': []
    }
    
    # Parse buffer entries
    current_entry = None
    
    for line in buffer_content.split('\n'):
        if line.startswith('## ['):
            # Extract timestamp and type
            match = re.match(r'## \[(.*?)\] (Human|Agent \(summary\))', line)
            if match:
                timestamp = match.group(1)
                entry_type = match.group(2)
                current_entry = {
                    'timestamp': timestamp,
                    'type': entry_type,
                    'content': []
                }
        elif current_entry and line.strip():
            current_entry['content'].append(line)
            
            # Look for task indicators
            content_str = ' '.join(current_entry['content'])
            if any(kw in content_str.lower() for kw in ['task', 'todo', 'working on', 'implementing']):
                if current_entry['type'].startswith('Human'):
                    extracted['tasks'].append({
                        'timestamp': current_entry['timestamp'],
                        'description': content_str[:200]
                    })
            
            # Look for decisions
            if any(kw in content_str.lower() for kw in ['decided', 'let\'s', 'go with', 'agreed']):
                extracted['decisions'].append({
                    'timestamp': current_entry['timestamp'],
                    'decision': content_str[:200]
                })
    
    return extracted


def recover_context() -> dict:
    """
    Perform full compaction recovery.
    
    Returns structured context for the agent to continue.
    """
    recovery = {
        'timestamp': datetime.now().isoformat(),
        'sources_checked': [],
        'recovered_context': {},
        'last_task': None,
        'recommendations': []
    }
    
    # Step 1: Read working buffer FIRST
    buffer_content = read_working_buffer()
    if buffer_content:
        recovery['sources_checked'].append('working_buffer')
        recovery['recovered_context']['working_buffer'] = extract_context_from_buffer(buffer_content)
    
    # Step 2: Read session state
    session_state = read_session_state()
    if session_state:
        recovery['sources_checked'].append('session_state')
        recovery['recovered_context']['session_state'] = session_state[:2000]  # Truncate for brevity
    
    # Step 3: Read recent daily notes
    daily_notes = get_recent_daily_notes()
    if daily_notes:
        recovery['sources_checked'].append('daily_notes')
        recovery['recovered_context']['daily_notes'] = [
            {'date': note['date'], 'preview': note['content'][:500]}
            for note in daily_notes
        ]
    
    # Step 4: Read MEMORY.md if exists
    if MEMORY_FILE.exists():
        recovery['sources_checked'].append('memory_md')
        recovery['recovered_context']['memory_md'] = MEMORY_FILE.read_text(encoding='utf-8')[:2000]
    
    # Determine last task
    if recovery['recovered_context'].get('working_buffer', {}).get('tasks'):
        tasks = recovery['recovered_context']['working_buffer']['tasks']
        recovery['last_task'] = tasks[-1] if tasks else None
    elif recovery['recovered_context'].get('session_state'):
        # Extract from session state
        state = recovery['recovered_context']['session_state']
        if 'task' in state.lower():
            recovery['last_task'] = {'description': 'See SESSION-STATE.md for details'}
    
    # Generate recommendations
    if recovery['last_task']:
        recovery['recommendations'].append(
            f"Last task was: {recovery['last_task']['description'][:100]}..."
        )
        recovery['recommendations'].append("Continue with this task?")
    
    if recovery['recovered_context'].get('working_buffer', {}).get('decisions'):
        recovery['recommendations'].append(
            f"Found {len(recovery['recovered_context']['working_buffer']['decisions'])} recent decisions in buffer"
        )
    
    # Save recovery state
    RECOVERY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    RECOVERY_STATE_FILE.write_text(
        json.dumps(recovery, indent=2, default=str),
        encoding='utf-8'
    )
    
    return recovery


def generate_recovery_message(recovery: dict) -> str:
    """Generate a human-readable recovery message."""
    msg = "🔄 **Recovered from compaction**\n\n"
    
    msg += f"**Sources checked:** {', '.join(recovery['sources_checked'])}\n\n"
    
    if recovery['last_task']:
        msg += f"**Last task:** {recovery['last_task']['description'][:150]}{'...' if len(recovery['last_task']['description']) > 150 else ''}\n\n"
    
    if recovery['recommendations']:
        msg += "**Recommendations:**\n"
        for rec in recovery['recommendations']:
            msg += f"- {rec}\n"
    
    msg += "\nContinue where we left off?"
    
    return msg


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compaction Recovery Protocol')
    parser.add_argument('--recover', action='store_true', help='Perform full recovery')
    parser.add_argument('--status', action='store_true', help='Check recovery state')
    parser.add_argument('--buffer', action='store_true', help='Show working buffer')
    parser.add_argument('--state', action='store_true', help='Show session state')
    parser.add_argument('--check-transcript', type=str, help='Check transcript for compaction indicators')
    
    args = parser.parse_args()
    
    if args.check_transcript:
        indicators = check_compaction_indicators(args.check_transcript)
        print(json.dumps(indicators, indent=2))
        return
    
    if args.status:
        if RECOVERY_STATE_FILE.exists():
            state = json.loads(RECOVERY_STATE_FILE.read_text(encoding='utf-8'))
            print(json.dumps(state, indent=2, default=str))
        else:
            print("No recovery state found")
        return
    
    if args.buffer:
        content = read_working_buffer()
        print(content if content else "Working buffer is empty")
        return
    
    if args.state:
        content = read_session_state()
        print(content if content else "Session state file does not exist")
        return
    
    if args.recover:
        recovery = recover_context()
        msg = generate_recovery_message(recovery)
        print(msg)
        print("\n--- Full Recovery Data ---")
        print(json.dumps(recovery, indent=2, default=str))
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
