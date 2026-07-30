#!/usr/bin/env python3
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

WORK = Path(__file__).resolve().parents[3]
SKILLS = WORK / 'skills'
INDEX = SKILLS / 'skill-router' / 'references' / 'skill-index.md'
OUT = SKILLS / 'skill-router' / 'references' / 'new-skill-review.md'

KEYWORDS = {
    'A/A1': ['message', 'chat', 'telegram', 'whatsapp', 'discord', 'sms', 'imessage'],
    'A/A2': ['email', 'mail', 'inbox'],
    'A/A3': ['doc', 'document'],
    'B/B1': ['search', 'web search', 'google', 'tavily', 'exa', 'perplexity'],
    'B/B2': ['fetch', 'scrape', 'transcript', 'extract', 'crawl'],
    'B/B4': ['markdown', 'notes search', 'knowledge base', 'rag'],
    'C/C3': ['browser', 'playwright', 'automation', 'click', 'form fill'],
    'C/C4': ['agent', 'sub-agent', 'orchestration', 'delegate'],
    'D/D5': ['deploy', 'cloud', 'docker', 'kubernetes', 'infrastructure', 'server'],
    'E/E2': ['crm', 'pipeline', 'salesforce', 'hubspot', 'attio'],
    'F/F1': ['calendar', 'schedule'],
    'F/F2': ['todo', 'task', 'reminder'],
    'F/F3': ['notes', 'obsidian', 'notion', 'draft'],
    'G/G2': ['smart home', 'device', 'thermostat', 'vacuum'],
    'I/I2': ['crypto', 'wallet', 'trading', 'exchange', 'token'],
    'Z/Z2': ['password', 'vault', 'secret', 'credential'],
}


def parse_index_backlog():
    rows = []
    if not INDEX.exists():
        return rows
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or line.startswith('|---') or 'skill | domain' in line:
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if len(parts) < 7:
            continue
        skill, domain, sub, risk, tags, status, notes = parts[:7]
        if status == 'backlog':
            rows.append({'skill': skill, 'notes': notes})
    return rows


def infer_candidates(text):
    t = text.lower()
    hits = []
    for bucket, kws in KEYWORDS.items():
        score = 0
        for kw in kws:
            if kw in t:
                score += 1
        if score:
            hits.append((bucket, score))
    hits.sort(key=lambda x: (-x[1], x[0]))
    return hits[:3]


def main():
    backlog = parse_index_backlog()
    counter = Counter()
    examples = defaultdict(list)
    unmatched = []
    for row in backlog:
        text = f"{row['skill']} {row['notes']}"
        cands = infer_candidates(text)
        if cands:
            top = cands[0][0]
            counter[top] += 1
            if len(examples[top]) < 8:
                examples[top].append(row['skill'])
        else:
            unmatched.append(row['skill'])

    lines = []
    lines.append('# New skill review\n')
    lines.append('This report scans backlog skills and estimates whether existing subdomains still fit them.\n')
    lines.append('## High-signal backlog clusters\n')
    for bucket, count in counter.most_common(20):
        lines.append(f'- {bucket}: {count} candidates (examples: {", ".join(examples[bucket])})')
    lines.append('\n## Potential taxonomy expansion signals\n')
    if unmatched:
        lines.append(f'- Unmatched backlog skills: {len(unmatched)}')
        lines.append(f'- Examples: {", ".join(unmatched[:30])}')
        lines.append('- If unmatched examples keep sharing a domain not captured by current subdomains, add a new subdomain.')
    else:
        lines.append('- No obvious unmatched backlog skills in this pass.')

    lines.append('\n## Suggested rule\n')
    lines.append('- When a newly added batch shows repeated unmatched patterns or repeated low-confidence fits, create or split a subdomain instead of forcing them into Z/Z4 forever.')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT}')

if __name__ == '__main__':
    main()
