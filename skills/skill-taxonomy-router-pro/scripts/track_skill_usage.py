#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'references' / 'usage-stats.json'


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {
        'schema_version': 1,
        'skills': {},
        'updated_at': None,
    }


def save_state(state):
    state['updated_at'] = datetime.now(timezone.utc).isoformat()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def cmd_mark(skill_names):
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    for name in skill_names:
        rec = state['skills'].setdefault(name, {
            'count': 0,
            'first_used_at': now,
            'last_used_at': now,
        })
        rec['count'] += 1
        rec['last_used_at'] = now
    save_state(state)
    for name in skill_names:
        print(f'marked {name}: {state["skills"][name]["count"]}')


def cmd_report(limit):
    state = load_state()
    items = sorted(state['skills'].items(), key=lambda kv: (-kv[1]['count'], kv[0]))[:limit]
    print('# skill usage report')
    for name, rec in items:
        print(f"{name}\tcount={rec['count']}\tlast={rec['last_used_at']}")


def main():
    ap = argparse.ArgumentParser(description='Track skill-router usage frequency')
    sub = ap.add_subparsers(dest='cmd', required=True)

    ap_mark = sub.add_parser('mark')
    ap_mark.add_argument('skills', nargs='+')

    ap_report = sub.add_parser('report')
    ap_report.add_argument('--limit', type=int, default=30)

    args = ap.parse_args()
    if args.cmd == 'mark':
        cmd_mark(args.skills)
    elif args.cmd == 'report':
        cmd_report(args.limit)

if __name__ == '__main__':
    main()
