#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

WORK_SKILLS = Path('/home/parallels/.openclaw/workspace/skills')


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


def main():
    ap = argparse.ArgumentParser(description='Check whether a to-be-downloaded skill overlaps with existing organized skills')
    ap.add_argument('skill_name')
    args = ap.parse_args()
    target_family = family_key(args.skill_name)
    matches = []
    for d in sorted(WORK_SKILLS.iterdir()):
        if d.is_dir() and family_key(d.name) == target_family:
            matches.append(d.name)
    if matches:
        print('overlap-found')
        for m in matches:
            print(m)
    else:
        print('no-overlap-found')

if __name__ == '__main__':
    main()
