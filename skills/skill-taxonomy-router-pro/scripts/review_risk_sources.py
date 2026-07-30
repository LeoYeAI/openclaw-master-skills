#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent.parent
OUT = ROOT / 'references' / 'risk-source-review.md'

HIGH_RISK_KWS = ['password', 'vault', 'credential', 'trading', 'wallet', 'proxy', 'cron', 'service', 'deploy', 'system', 'config', 'ssh', 'root', 'gateway']


def read_frontmatter(skill_dir: Path):
    p = skill_dir / 'SKILL.md'
    if not p.exists():
        return '', ''
    text = p.read_text(encoding='utf-8', errors='ignore')[:5000]
    nm = re.search(r'^name:\s*(.*)$', text, re.M)
    dm = re.search(r'^description:\s*(.*)$', text, re.M)
    return (nm.group(1).strip() if nm else skill_dir.name, dm.group(1).strip().strip('"\'') if dm else '')


def main():
    lines = ['# Risk/source review\n', 'Use this report to review skills from non-ClawHub channels or skills with suspicious/high-risk signals.\n']
    lines.append('## Review priorities\n')
    for d in sorted(SKILLS.iterdir()):
        if not d.is_dir() or d.name == 'skill-router':
            continue
        name, desc = read_frontmatter(d)
        text = f'{d.name} {name} {desc}'.lower()
        score = sum(1 for kw in HIGH_RISK_KWS if kw in text)
        non_clawhub_signal = any(x in d.name for x in ['bak', 'copy', 'clone', 'test'])
        if score or non_clawhub_signal:
            why = []
            if score:
                why.append(f'high-risk-keywords={score}')
            if non_clawhub_signal:
                why.append('nonstandard-name-signal')
            lines.append(f'- {d.name}: {", ".join(why)}')
    lines.append('\n## Rule\n')
    lines.append('- When ClawHub pages or metadata expose security/risk labels, incorporate them into the review decision to speed up screening.')
    lines.append('- For non-ClawHub or manually copied skills, do proactive screening before allowing routing priority or any risky execution path.')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT}')

if __name__ == '__main__':
    main()
