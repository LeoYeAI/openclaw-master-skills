#!/usr/bin/env python3
import argparse
from pathlib import Path

INDEX = Path('/home/parallels/.openclaw/workspace/skills/skill-router/references/skill-index.md')


def parse_rows():
    rows = []
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or line.startswith('|---') or 'skill | domain' in line:
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if len(parts) < 7:
            continue
        rows.append({
            'skill': parts[0],
            'domain': parts[1],
            'subdomain': parts[2],
            'risk': parts[3],
            'tags': parts[4],
            'status': parts[5],
            'notes': parts[6],
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description='Query skill-router skill-index without reading the full file into chat')
    ap.add_argument('--skill')
    ap.add_argument('--domain')
    ap.add_argument('--status')
    ap.add_argument('--limit', type=int, default=20)
    args = ap.parse_args()

    rows = parse_rows()
    if args.skill:
        rows = [r for r in rows if args.skill.lower() in r['skill'].lower()]
    if args.domain:
        rows = [r for r in rows if r['domain'] == args.domain]
    if args.status:
        rows = [r for r in rows if r['status'] == args.status]
    rows = rows[:args.limit]
    for r in rows:
        print(f"{r['skill']}\t{r['domain']}/{r['subdomain']}\t{r['risk']}\t{r['status']}\t{r['tags']}")

if __name__ == '__main__':
    main()
