#!/usr/bin/env python3
import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path('/home/openclaw/.openclaw/workspace/skills/paradiz/data/db/sync.sqlite')


def main():
    p = argparse.ArgumentParser(description='Cleanup and health-check for sync.sqlite')
    p.add_argument('--days', type=int, default=90, help='Keep logs for last N days')
    p.add_argument('--warn-mb', type=float, default=50.0, help='Warn if DB exceeds this size in MB')
    args = p.parse_args()

    if not DB_PATH.exists():
        print(json.dumps({'ok': False, 'error': 'sync.sqlite not found', 'path': str(DB_PATH)}, ensure_ascii=False))
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    before_rows = cur.execute('SELECT COUNT(*) FROM log').fetchone()[0]
    cutoff = cur.execute("SELECT julianday('now', ?)", (f'-{args.days} days',)).fetchone()[0]

    cur.execute('DELETE FROM log WHERE creation < ?', (cutoff,))
    deleted = cur.rowcount if cur.rowcount is not None else 0
    conn.commit()

    cur.execute('VACUUM')
    conn.close()

    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    warn = size_mb > args.warn_mb

    # reopen only to read count after vacuum
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    after_rows = cur.execute('SELECT COUNT(*) FROM log').fetchone()[0]
    conn.close()

    print(json.dumps({
        'ok': True,
        'db': str(DB_PATH),
        'kept_days': args.days,
        'rows_before': before_rows,
        'rows_deleted': deleted,
        'rows_after': after_rows,
        'size_mb': round(size_mb, 3),
        'warn_threshold_mb': args.warn_mb,
        'size_warn': warn
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
