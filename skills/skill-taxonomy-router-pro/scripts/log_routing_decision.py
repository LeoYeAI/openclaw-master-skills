#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
USAGE = ROOT / 'references' / 'usage-stats.json'
LOG = ROOT / 'references' / 'routing-decisions.jsonl'


def load_usage():
    if USAGE.exists():
        return json.loads(USAGE.read_text(encoding='utf-8'))
    return {'schema_version': 1, 'skills': {}, 'updated_at': None}


def save_usage(state):
    state['updated_at'] = datetime.now(timezone.utc).isoformat()
    USAGE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def mark_usage(skill_names):
    state = load_usage()
    now = datetime.now(timezone.utc).isoformat()
    for name in skill_names:
        rec = state['skills'].setdefault(name, {
            'count': 0,
            'first_used_at': now,
            'last_used_at': now,
        })
        rec['count'] += 1
        rec['last_used_at'] = now
    save_usage(state)


def append_log(entry):
    with LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser(description='Log skill-router routing decisions and mark skill usage')
    ap.add_argument('--intent', required=True)
    ap.add_argument('--domain', default='')
    ap.add_argument('--subdomain', default='')
    ap.add_argument('--risk', default='')
    ap.add_argument('--skills', nargs='+', required=True)
    ap.add_argument('--candidates', nargs='*', default=[])
    ap.add_argument('--reason', default='')
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).isoformat()
    mark_usage(args.skills)
    append_log({
        'timestamp': ts,
        'intent': args.intent,
        'domain': args.domain,
        'subdomain': args.subdomain,
        'risk': args.risk,
        'skills': args.skills,
        'candidates': args.candidates,
        'reason': args.reason,
    })
    print('logged routing decision for:', ', '.join(args.skills))

if __name__ == '__main__':
    main()
