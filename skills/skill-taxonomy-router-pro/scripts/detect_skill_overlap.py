#!/usr/bin/env python3
import re
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path('/home/parallels/.openclaw/workspace/skills/skill-router')
SKILLS = ROOT.parent.parent
OUT = ROOT / 'references' / 'skill-overlap-report.md'
MAP = ROOT / 'references' / 'skill-overlap-map.json'

BACKUP_HINTS = ['-bak-', 'backup', '-copy', ' copy', 'clone', '-1-0-0', '-1-0-', '-v2', '-v3']


def read_desc(skill_dir: Path) -> str:
    p = skill_dir / 'SKILL.md'
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8', errors='ignore')[:5000]
    m = re.search(r'^description:\s*(.*)$', text, re.M)
    return m.group(1).strip().strip('"\'') if m else ''


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


def score_variant(name: str, desc: str) -> int:
    s = 0
    low = f"{name} {desc}".lower()
    for hint in BACKUP_HINTS:
        if hint in low:
            s += 2
    if 'fork' in low or 'unofficial' in low:
        s += 1
    return s


def main():
    skills = []
    for d in sorted(SKILLS.iterdir()):
        if d.is_dir():
            if d.name == 'skill-router':
                continue
            desc = read_desc(d)
            skills.append({'name': d.name, 'desc': desc, 'family': family_key(d.name), 'variant_score': score_variant(d.name, desc)})

    families = defaultdict(list)
    for s in skills:
        families[s['family']].append(s)

    overlap_map = {}
    lines = ['# Skill overlap report\n', 'Potential duplicate / variant families for routing-layer and index-layer fusion.\n']
    for fam, items in sorted(families.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(items) < 2:
            continue
        ranked = sorted(items, key=lambda x: (x['variant_score'], len(x['name'])))
        canonical = ranked[0]['name']
        variants = [x['name'] for x in ranked[1:]]
        overlap_map[canonical] = {
            'family': fam,
            'variants': variants,
            'status': 'auto-canonical' if all(x['variant_score'] >= 0 for x in ranked[1:]) else 'review',
        }
        lines.append(f'## {fam}')
        lines.append(f'- canonical: {canonical}')
        lines.append(f'- variants: {", ".join(variants)}')
        if any(x['variant_score'] > 0 for x in ranked[1:]):
            lines.append('- reason: naming/backup/version signals suggest redundant or derivative variants.')
        else:
            lines.append('- reason: same normalized family name; review if semantics diverge.')
        lines.append('')

    OUT.write_text('\n'.join(lines), encoding='utf-8')
    MAP.write_text(json.dumps(overlap_map, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {OUT}')
    print(f'wrote {MAP}')

if __name__ == '__main__':
    main()
