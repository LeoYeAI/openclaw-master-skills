#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

WORK = Path('/home/parallels/.openclaw/workspace')
WORK_SKILLS = WORK / 'skills'
INBOX = Path('/home/parallels/Desktop/skills-inbox')
STATE = INBOX / 'intake-state.json'


def ensure_dirs():
    INBOX.mkdir(parents=True, exist_ok=True)


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {'items': {}, 'updated_at': None}


def save_state(state):
    state['updated_at'] = datetime.now(timezone.utc).isoformat()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[-_]+', ' ', s)
    s = re.sub(r'\b(skill|cli|api|tool|tools)\b', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def family_key(name: str) -> str:
    n = normalize(name)
    n = re.sub(r'\bbak\b.*$', '', n).strip()
    n = re.sub(r'\b\d+(?: \d+)*\b', '', n).strip()
    n = re.sub(r'\bcopy\b.*$', '', n).strip()
    return n


def overlap_matches(skill_name: str):
    target = family_key(skill_name)
    matches = []
    for d in sorted(WORK_SKILLS.iterdir()):
        if d.is_dir() and family_key(d.name) == target:
            matches.append(d.name)
    return matches


def main():
    ap = argparse.ArgumentParser(description='High-automation skill intake: check overlap, download to inbox, record intake state')
    ap.add_argument('skill_name')
    ap.add_argument('--source', default='clawhub')
    ap.add_argument('--force-download', action='store_true')
    args = ap.parse_args()

    ensure_dirs()
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()

    existing = overlap_matches(args.skill_name)
    inbox_skill = INBOX / 'skills' / args.skill_name
    record = state['items'].get(args.skill_name, {})
    result = {
        'skill_name': args.skill_name,
        'source': args.source,
        'timestamp': now,
        'overlap_matches': existing,
        'inbox_path': str(inbox_skill),
        'downloaded': False,
        'status': 'pending-review',
        'note': '',
    }

    if existing and not args.force_download:
        result['note'] = 'Existing organized/classified overlap found; download skipped pending review.'
        result['status'] = 'overlap-skip'
    elif inbox_skill.exists() and not args.force_download:
        result['note'] = 'Already present in inbox; download skipped.'
        result['status'] = 'already-in-inbox'
    else:
        cmd = ['clawhub', 'install', args.skill_name, '--workdir', str(INBOX), '--force']
        proc = subprocess.run(cmd, text=True, capture_output=True)
        result['downloaded'] = proc.returncode == 0
        result['status'] = 'downloaded-to-inbox' if proc.returncode == 0 else 'download-failed'
        result['note'] = (proc.stdout + '\n' + proc.stderr).strip()[:4000]

    state['items'][args.skill_name] = result
    save_state(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
