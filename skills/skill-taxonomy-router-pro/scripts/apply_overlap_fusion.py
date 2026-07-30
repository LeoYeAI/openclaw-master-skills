#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('/home/parallels/.openclaw/workspace/skills/skill-router')
INDEX = ROOT / 'references' / 'skill-index.md'
MAP = ROOT / 'references' / 'skill-overlap-map.json'
OUT = ROOT / 'references' / 'skill-fusion-view.md'


def parse_index():
    rows = []
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or line.startswith('|---') or 'skill | domain' in line:
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if len(parts) < 7:
            continue
        skill, domain, sub, risk, tags, status, notes = parts[:7]
        rows.append({'skill': skill, 'domain': domain, 'sub': sub, 'risk': risk, 'tags': tags, 'status': status, 'notes': notes})
    return rows


def main():
    rows = parse_index()
    overlap = json.loads(MAP.read_text(encoding='utf-8')) if MAP.exists() else {}
    variant_to_canonical = {}
    for canonical, info in overlap.items():
        for v in info.get('variants', []):
            variant_to_canonical[v] = canonical

    lines = ['# Skill fusion view\n', 'Canonical-first routing/index view. Variants are retained on disk but de-prioritized for routing unless needed.\n']
    lines.append('| skill | canonical_skill | fusion_status | notes |')
    lines.append('|---|---|---|---|')
    for row in rows:
        skill = row['skill']
        if skill in variant_to_canonical:
            canonical = variant_to_canonical[skill]
            fusion_status = 'variant-deprioritized'
            note = f'Prefer {canonical} by default; ask user if conflict matters.'
        elif skill in overlap:
            canonical = skill
            fusion_status = 'canonical'
            note = 'Primary representative for its overlap family.'
        else:
            canonical = skill
            fusion_status = 'standalone'
            note = ''
        lines.append(f"| {skill} | {canonical} | {fusion_status} | {note} |")

    lines.append('\n## Rule\n')
    lines.append('- Safe automatic fusion means canonical-first routing and index de-duplication, not destructive file merging.')
    lines.append('- If two overlapping skills differ materially in instructions, scripts, or intended outcomes, ask before content-level merge.')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT}')

if __name__ == '__main__':
    main()
