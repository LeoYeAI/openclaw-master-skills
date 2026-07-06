#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Optional


def load_state(path: Path) -> dict:
    return json.loads(path.read_text())


def find_item(state: dict, item_id: str) -> Optional[dict]:
    for view in state.get("views", {}).values():
        for item in view.get("items", []):
            if item.get("id") == item_id:
                return item
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("state_path")
    ap.add_argument("callback")
    args = ap.parse_args()

    state = load_state(Path(args.state_path))
    callback = args.callback.strip()
    state_version = int(state.get("menuVersion", 1))

    # Extract item_id from callback regardless of version.
    # Current formats:
    #   tfb_root_v{version}_{item_id}
    #   tfb_dir_{prefix}_v{version}_{item_id}
    item_id = None
    m = re.match(r"^tfb_root_v\d+_(w\d+)$", callback)
    if m:
        item_id = m.group(1)
    else:
        m = re.match(r"^tfb_dir_[^_]+_v\d+_([a-z\d]+)$", callback)
        if m:
            item_id = m.group(1)
    
    if item_id is not None:
        item = find_item(state, item_id)
        if item is not None:
            action = "open-dir" if item.get("type") == "dir" else "open-file-actions"
            print(json.dumps({"action": action, "item": item, "note": "processed despite version mismatch"}, ensure_ascii=False, indent=2))
            return

    # Check for navigation actions (back, close, page)
    # These need version match - if stale, just return stale
    simple_vm = re.match(r"^(tfb_(?:back|close))_v(\d+)$", callback)
    if simple_vm:
        base = simple_vm.group(1)
        cb_version = int(simple_vm.group(2))
        if cb_version != state_version:
            print(json.dumps({"action": "stale", "callback": callback, "stateVersion": state_version, "callbackVersion": cb_version}, ensure_ascii=False, indent=2))
            return
        callback = base
    else:
        vm = re.match(r"^(.*)_v(\d+)_(.+)$", callback)
        if vm:
            base = vm.group(1)
            cb_version = int(vm.group(2))
            suffix = vm.group(3)
            if cb_version != state_version:
                print(json.dumps({"action": "stale", "callback": callback, "stateVersion": state_version, "callbackVersion": cb_version}, ensure_ascii=False, indent=2))
                return
            callback = f"{base}_{suffix}"

    if callback == "tfb_back":
        print(json.dumps({"action": "back"}, ensure_ascii=False, indent=2))
        return
    if callback == "tfb_close":
        print(json.dumps({"action": "close"}, ensure_ascii=False, indent=2))
        return

    m = re.match(r"^(tfb_(?:root|dir_[^_]+))_page_(prev|next)$", callback)
    if m:
        print(json.dumps({"action": "page", "scope": m.group(1), "direction": m.group(2)}, ensure_ascii=False, indent=2))
        return

    m = re.match(r"^tfb_preview_(.+)$", callback)
    if m:
        item = find_item(state, m.group(1))
        print(json.dumps({"action": "preview", "item": item}, ensure_ascii=False, indent=2))
        return

    m = re.match(r"^tfb_path_(.+)$", callback)
    if m:
        item = find_item(state, m.group(1))
        print(json.dumps({"action": "path", "item": item}, ensure_ascii=False, indent=2))
        return

    m = re.match(r"^tfb_download_(.+)$", callback)
    if m:
        item = find_item(state, m.group(1))
        print(json.dumps({"action": "download", "item": item}, ensure_ascii=False, indent=2))
        return

    print(json.dumps({"action": "unknown", "callback": callback}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
