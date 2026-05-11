#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC = timezone.utc


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def read_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def cleanup(rows):
    now = datetime.now(UTC)
    changed = 0
    for r in rows:
        if r.get('status') == 'active':
            exp = parse_iso(r['expires_at'])
            if exp <= now:
                r['status'] = 'expired'
                r['expired_at'] = now_iso()
                changed += 1
    return changed


def cmd_cleanup(args):
    path = Path(args.file)
    rows = read_jsonl(path)
    changed = cleanup(rows)
    write_jsonl(path, rows)
    print(json.dumps({'ok': True, 'changed': changed, 'total': len(rows)}, ensure_ascii=False))


def cmd_add(args):
    path = Path(args.file)
    rows = read_jsonl(path)
    cleanup(rows)

    now = datetime.now(UTC)
    expires = now + timedelta(hours=args.hold_hours)

    # close previous active holds for same client
    replaced = 0
    for r in rows:
        if r.get('status') == 'active' and r.get('client_contact') == args.client_contact:
            r['status'] = 'replaced'
            r['replaced_at'] = now_iso()
            replaced += 1

    rec = {
        'hold_id': f"HLD-{int(now.timestamp())}",
        'created_at': now.isoformat(),
        'expires_at': expires.isoformat(),
        'status': 'active',
        'client_name': args.client_name,
        'client_contact': args.client_contact,
        'room': args.room,
        'checkin': args.checkin,
        'checkout': args.checkout,
        'guests': args.guests,
        'notes': args.notes or '',
    }
    rows.append(rec)
    write_jsonl(path, rows)

    warn = (
        'Я могу удерживать номер только 24 часа. '
        'После этого заявка автоматически удаляется, и при повторном обращении оформляем заново.'
    )

    print(json.dumps({'ok': True, 'hold': rec, 'replaced': replaced, 'client_warning': warn}, ensure_ascii=False))


def cmd_list(args):
    path = Path(args.file)
    rows = read_jsonl(path)
    cleanup(rows)
    write_jsonl(path, rows)
    out = rows
    if args.active_only:
        out = [r for r in rows if r.get('status') == 'active']
    print(json.dumps({'ok': True, 'items': out}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description='Manage 24h room hold requests (jsonl).')
    p.add_argument('--file', default=str(Path(__file__).resolve().parent.parent / 'data' / 'holds.jsonl'))

    sub = p.add_subparsers(dest='cmd', required=True)

    c1 = sub.add_parser('cleanup')
    c1.set_defaults(func=cmd_cleanup)

    c2 = sub.add_parser('add')
    c2.add_argument('--client-name', required=True)
    c2.add_argument('--client-contact', required=True)
    c2.add_argument('--room', required=True)
    c2.add_argument('--checkin', required=True)
    c2.add_argument('--checkout', required=True)
    c2.add_argument('--guests', type=int, required=True)
    c2.add_argument('--notes', default='')
    c2.add_argument('--hold-hours', type=int, default=24)
    c2.set_defaults(func=cmd_add)

    c3 = sub.add_parser('list')
    c3.add_argument('--active-only', action='store_true')
    c3.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
