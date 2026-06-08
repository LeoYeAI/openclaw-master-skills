#!/usr/bin/env python3
import argparse
import json
import time

from task_paths import resolve_task_dir


def path_for(task_id):
    return resolve_task_dir(task_id)


def cmd_init(task_id):
    p = path_for(task_id)
    p.mkdir(parents=True, exist_ok=True)
    state = {
        'task_id': p.name,
        'started_at': int(time.time()),
        'last_action': None,
        'last_capture': None,
        'last_target': None,
    }
    (p / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(json.dumps({'ok': True, 'task_dir': str(p), 'state_file': str(p / 'state.json')}, ensure_ascii=False))


def cmd_show(task_id):
    p = path_for(task_id) / 'state.json'
    if not p.exists():
        print(json.dumps({'ok': False, 'error': 'state_not_found'}, ensure_ascii=False))
        return
    print(p.read_text())


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init', aliases=['create'])
    i.add_argument('--task-id', '--name', required=True, dest='task_id')
    s = sub.add_parser('show', aliases=['get'])
    s.add_argument('--task-id', '--name', required=True, dest='task_id')
    args = ap.parse_args()
    if args.cmd in ('init', 'create'):
        cmd_init(args.task_id)
    else:
        cmd_show(args.task_id)


if __name__ == '__main__':
    main()
