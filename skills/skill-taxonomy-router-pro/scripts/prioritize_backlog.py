#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'references' / 'skill-index.md'
USAGE = ROOT / 'references' / 'usage-stats.json'
REVIEW = ROOT / 'references' / 'new-skill-review.md'
OUT = ROOT / 'references' / 'backlog-priority.md'

RISK_WEIGHT = {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4}


def parse_index():
    rows = []
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or line.startswith('|---') or 'skill | domain' in line:
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if len(parts) < 7:
            continue
        skill, domain, sub, risk, tags, status, notes = parts[:7]
        rows.append({
            'skill': skill,
            'domain': domain,
            'sub': sub,
            'risk': risk,
            'tags': tags,
            'status': status,
            'notes': notes,
        })
    return rows


def load_usage():
    if not USAGE.exists():
        return {}
    data = json.loads(USAGE.read_text(encoding='utf-8'))
    return {k: v.get('count', 0) for k, v in data.get('skills', {}).items()}


def score(row, usage):
    note = (row['skill'] + ' ' + row['notes']).lower()
    s = 0
    # If it is backlog, it is eligible.
    if row['status'] == 'backlog':
        s += 5
    # likely high-value buckets
    for kw in ['calendar','todo','task','notes','search','browser','cloud','docker','kubernetes','crm','email','youtube','transcript','security']:
        if kw in note:
            s += 2
    # riskier backlog deserves earlier review when action-capable
    s += RISK_WEIGHT.get(row['risk'], 0)
    # direct usage signal if this specific skill has been used
    s += usage.get(row['skill'], 0) * 10
    return s


def main():
    rows = parse_index()
    usage = load_usage()
    backlog = [r for r in rows if r['status'] == 'backlog']
    ranked = sorted(backlog, key=lambda r: (-score(r, usage), r['skill']))

    lines = []
    lines.append('# Backlog priority report\n')
    lines.append('Use this report to decide which backlog skills should be formally classified next.\n')
    lines.append('Scoring combines backlog status, task-value keywords, risk, and direct usage counts.\n')
    lines.append('\n## Top candidates\n')
    for row in ranked[:60]:
        lines.append(f"- {row['skill']} | score={score(row, usage)} | risk={row['risk']} | notes={row['notes']}")

    groups = defaultdict(list)
    for row in ranked[:120]:
        text = (row['skill'] + ' ' + row['notes']).lower()
        key = 'other'
        for label, kws in {
            'calendar-tasks-notes': ['calendar','todo','task','reminder','notes','obsidian','notion'],
            'search-retrieval': ['search','retrieve','transcript','crawl','scrape'],
            'browser-automation': ['browser','playwright','automation'],
            'infra-devops': ['cloud','docker','kubernetes','deploy','server'],
            'crm-growth': ['crm','sales','outreach','lead','linkedin'],
            'media-transcription': ['audio','video','transcript','whisper','tts'],
            'finance-crypto': ['finance','crypto','wallet','trading'],
        }.items():
            if any(kw in text for kw in kws):
                key = label
                break
        groups[key].append(row['skill'])

    lines.append('\n## Suggested next classification batches\n')
    for group, skills in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines.append(f'- {group}: {len(skills)} candidates (examples: {", ".join(skills[:12])})')

    lines.append('\n## Rule\n')
    lines.append('- Prefer formal classification for backlog skills that are used in practice, action-capable, or clustered in recurring task domains.')
    lines.append('- If a cluster stays large and awkward under existing subdomains, split the taxonomy instead of forcing weak fits.')

    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT}')

if __name__ == '__main__':
    main()
