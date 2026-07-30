#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

INBOX = Path('/home/parallels/Desktop/skills-inbox')


def main():
    ap = argparse.ArgumentParser(description='Delete the download inbox folder after all skills are organized')
    ap.add_argument('--yes', action='store_true', help='confirm deletion')
    args = ap.parse_args()
    if not args.yes:
        raise SystemExit('pass --yes to delete the inbox folder')
    if INBOX.exists():
        shutil.rmtree(INBOX)
        print(f'deleted {INBOX}')
    else:
        print(f'not found: {INBOX}')

if __name__ == '__main__':
    main()
