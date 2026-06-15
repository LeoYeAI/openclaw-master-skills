#!/usr/bin/env python3
"""
WAL Protocol - Write-Ahead Logging for Proactive Agent

Captures corrections, decisions, proper nouns, preferences, and specific values
to SESSION-STATE.md before responding to the human.

Usage:
    python wal_protocol.py "Human message here" "Agent response here"
    
Or import as module:
    from wal_protocol import capture_wal_entry
    capture_wal_entry(human_msg, agent_response)
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import re

# Session state file location
SESSION_STATE_FILE = Path("D:/OpenClaw/workspace/SESSION-STATE.md")

# Patterns that trigger WAL capture
WAL_TRIGGERS = {
    'correction': [
        r'\b(not|instead of|rather than|actually|no, i meant|it\'s x, not y)\b',
        r'\b(correct|wrong|mistake|error|should be)\b'
    ],
    'proper_noun': [
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Capitalized names
        r'\b(?:Inc|LLC|Ltd|Corp|Co)\.\b',  # Company suffixes
        r'\b[A-Z]{2,}\b'  # Acronyms
    ],
    'preference': [
        r'\b(i (prefer|like|love|hate|dislike|want|need))\b',
        r'\b(preferred|favorite|favourite|best|worst)\b'
    ],
    'decision': [
        r'\b(let\'s|let us|go with|choose|select|use|decided to)\b',
        r'\b(okay|ok|agreed|sounds good|perfect)\b'
    ],
    'specific_value': [
        r'\b\d{4}-\d{2}-\d{2}\b',  # Dates
        r'\bhttps?://\S+\b',  # URLs
        r'\b\d+\b',  # Numbers
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Emails
    ]
}


def detect_wal_triggers(text: str) -> list:
    """Detect which WAL triggers are present in the text."""
    detected = []
    for category, patterns in WAL_TRIGGERS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(category)
                break
    return list(set(detected))


def extract_key_details(text: str) -> dict:
    """Extract key details from text for WAL entry."""
    details = {
        'dates': re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text),
        'urls': re.findall(r'\bhttps?://\S+\b', text),
        'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        'numbers': re.findall(r'\b\d+\b', text),
        'capitalized': re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
    }
    # Filter out empty lists
    return {k: v for k, v in details.items() if v}


def capture_wal_entry(human_message: str, agent_response: str = None, 
                      session_state_path: str = None) -> dict:
    """
    Capture a WAL entry from a human-agent exchange.
    
    Args:
        human_message: The human's message
        agent_response: Optional agent response
        session_state_path: Optional custom path to SESSION-STATE.md
        
    Returns:
        dict with capture results
    """
    if session_state_path:
        state_file = Path(session_state_path)
    else:
        state_file = SESSION_STATE_FILE
    
    # Detect triggers
    triggers = detect_wal_triggers(human_message)
    
    if not triggers:
        return {
            'captured': False,
            'reason': 'No WAL triggers detected',
            'triggers': []
        }
    
    # Extract details
    details = extract_key_details(human_message)
    
    # Create WAL entry
    timestamp = datetime.now().isoformat()
    entry = {
        'timestamp': timestamp,
        'type': 'wal_entry',
        'triggers': triggers,
        'human_message': human_message[:200],  # Truncate for brevity
        'extracted_details': details
    }
    
    # Ensure directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing state or create new
    if state_file.exists():
        content = state_file.read_text(encoding='utf-8')
    else:
        content = "# SESSION-STATE.md - Active Working Memory\n\n"
    
    # Append WAL entry
    wal_section = f"\n## WAL Entry [{timestamp}]\n"
    wal_section += f"**Triggers:** {', '.join(triggers)}\n"
    wal_section += f"**Human:** {human_message[:150]}{'...' if len(human_message) > 150 else ''}\n"
    
    if details:
        wal_section += "**Extracted:**\n"
        for key, values in details.items():
            wal_section += f"- {key}: {', '.join(values[:5])}\n"
    
    wal_section += "\n---\n"
    
    # Write updated state
    new_content = content + wal_section
    state_file.write_text(new_content, encoding='utf-8')
    
    return {
        'captured': True,
        'triggers': triggers,
        'details': details,
        'entry_file': str(state_file)
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python wal_protocol.py <human_message> [agent_response]")
        print("       python wal_protocol.py --test")
        sys.exit(1)
    
    if sys.argv[1] == '--test':
        # Run self-test
        test_messages = [
            "Use the blue theme, not red",
            "My name is John Smith and I work at Acme Inc.",
            "I prefer dark mode and hate bright colors",
            "Let's go with option 3, the meeting is on 2024-03-22",
            "Contact me at john@example.com or visit https://example.com"
        ]
        
        print("WAL Protocol Self-Test\n")
        for msg in test_messages:
            result = capture_wal_entry(msg)
            print(f"Message: {msg}")
            print(f"Result: {result}\n")
        
        return
    
    # Normal operation
    human_msg = sys.argv[1]
    agent_resp = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = capture_wal_entry(human_msg, agent_resp)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
