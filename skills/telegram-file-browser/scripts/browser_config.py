#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict

DEFAULT_CONFIG = {
    "displayMode": "edit-message"
}


def load_config(path: str) -> Dict[str, str]:
    p = Path(path)
    if not p.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(p.read_text())
    except Exception:
        return dict(DEFAULT_CONFIG)
    merged = dict(DEFAULT_CONFIG)
    merged.update({k: v for k, v in data.items() if isinstance(v, str)})
    return merged


def save_config(path: str, config: Dict[str, str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(config, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get")
    p_get.add_argument("config_path")

    p_set = sub.add_parser("set-mode")
    p_set.add_argument("config_path")
    p_set.add_argument("mode", choices=["edit-message", "new-message"])

    args = ap.parse_args()

    if args.command == "get":
        print(json.dumps(load_config(args.config_path), ensure_ascii=False, indent=2))
        return

    if args.command == "set-mode":
        cfg = load_config(args.config_path)
        cfg["displayMode"] = args.mode
        save_config(args.config_path, cfg)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
