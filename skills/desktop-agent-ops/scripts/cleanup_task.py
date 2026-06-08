#!/usr/bin/env python3
import argparse
import json
import shutil

from task_paths import resolve_task_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task-id', required=True)
    args = ap.parse_args()
    target = resolve_task_dir(args.task_id)
    existed = target.exists()
    if existed:
        shutil.rmtree(target, ignore_errors=True)
    print(json.dumps({'ok': True, 'task_id': args.task_id, 'removed': existed}, ensure_ascii=False))


if __name__ == '__main__':
    main()
