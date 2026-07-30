#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict

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
    rows = parse_rows()
    by_domain = Counter(r['domain'] for r in rows)
    by_status = Counter(r['status'] for r in rows)
    by_domain_status = defaultdict(Counter)
    for r in rows:
        by_domain_status[r['domain']][r['status']] += 1

    print('# skill pool summary')
    print('total_skills', len(rows))
    print('status_counts', dict(by_status))
    print('domain_counts')
    for d, n in sorted(by_domain.items()):
        print(f'{d}\t{n}\tclassified={by_domain_status[d].get("classified",0)}\tbacklog={by_domain_status[d].get("backlog",0)}')

if __name__ == '__main__':
    main()
