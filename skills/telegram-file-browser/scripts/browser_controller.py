#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from file_browser_state import bump_menu_version, init_state, load_state, path_label, pop_path, push_path, save_state, set_live_message_id
from build_view import normalize, list_entries, paginate, build_items, is_within_root
from render_buttons import render_directory_buttons, render_file_action_buttons


def make_dir_prefix(path: Path) -> str:
    return f"d{abs(hash(str(path))) % 1000}"


def build_view_dict(root: Path, current: Path, prefix: str, page: int, page_size: int) -> Dict[str, Any]:
    entries = list_entries(root, current)
    page_entries, safe_page, total_pages = paginate(entries, page, page_size)
    start_index = (safe_page - 1) * page_size + 1
    return {
        "root": str(root),
        "path": str(current),
        "page": safe_page,
        "pageSize": page_size,
        "totalItems": len(entries),
        "totalPages": total_pages,
        "hasPrev": safe_page > 1,
        "hasNext": safe_page < total_pages,
        "items": build_items(page_entries, prefix, start_index=start_index)
    }


def find_item(state: Dict[str, Any], item_id: str) -> Optional[Dict[str, Any]]:
    for view in state.get("views", {}).values():
        for item in view.get("items", []):
            if item.get("id") == item_id:
                return item
    return None


def current_page_for(state: Dict[str, Any], path: Path) -> int:
    view = state.get("views", {}).get(str(path), {})
    return int(view.get("page", 1))


def render_directory_result(state: Dict[str, Any], root: Path, current: Path, page_size: int, page: int) -> Dict[str, Any]:
    prefix = "w" if current == root else make_dir_prefix(current)
    view = build_view_dict(root, current, prefix, page, page_size)
    state.setdefault("views", {})[str(current)] = view
    state["current"] = str(current)
    callback_prefix = "tfb_root" if current == root else f"tfb_dir_{prefix}"
    version = int(state.get("menuVersion", 1))
    return {
        "kind": "directory",
        "text": f"📂 文件浏览器\n当前位置：`{path_label(str(current))}`\n\n点下面按钮直接浏览：",
        "buttons": render_directory_buttons(view, callback_prefix, include_back=(current != root), version=version),
        "view": view,
        "state": state
    }


def open_root(state: Dict[str, Any], root: Path, page_size: int = 12) -> Dict[str, Any]:
    state["current"] = str(root)
    state["stack"] = []
    return render_directory_result(state, root, root, page_size, page=1)


def open_directory(state: Dict[str, Any], item_id: str, page_size: int = 12) -> Dict[str, Any]:
    item = find_item(state, item_id)
    if not item or item.get("type") != "dir":
        raise ValueError(f"Directory item not found: {item_id}")
    root = normalize(state["root"])
    current = normalize(state["current"])
    newp = normalize(item["path"])
    if not is_within_root(root, newp):
        raise PermissionError(f"Path escapes root: {newp}")
    push_path(state, str(current), str(newp))
    bump_menu_version(state)
    return render_directory_result(state, root, newp, page_size, page=1)


def open_file_actions(state: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    item = find_item(state, item_id)
    if not item or item.get("type") != "file":
        raise ValueError(f"File item not found: {item_id}")
    state["selectedFileId"] = item_id
    state["selectedFilePath"] = item["path"]
    bump_menu_version(state)
    version = int(state.get("menuVersion", 1))
    return {
        "kind": "file-actions",
        "text": f"📄 文件操作\n目标：`{path_label(item['path'])}`\n\n选择你要的操作：",
        "buttons": render_file_action_buttons(item_id, version=version),
        "item": item,
        "state": state
    }


def go_back(state: Dict[str, Any], page_size: int = 12) -> Dict[str, Any]:
    prev = pop_path(state)
    root = normalize(state["root"])
    if not prev:
        bump_menu_version(state)
        return render_directory_result(state, root, root, page_size=page_size, page=1)
    prevp = normalize(prev)
    bump_menu_version(state)
    return render_directory_result(state, root, prevp, page_size, page=current_page_for(state, prevp))


def change_page(state: Dict[str, Any], direction: str, page_size: int = 12) -> Dict[str, Any]:
    root = normalize(state["root"])
    current = normalize(state["current"])
    current_page = current_page_for(state, current)
    target_page = current_page - 1 if direction == 'prev' else current_page + 1
    bump_menu_version(state)
    return render_directory_result(state, root, current, page_size, page=target_page)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["open-root", "open-dir", "open-file-actions", "back", "page", "set-live-message"])
    ap.add_argument("state_path")
    ap.add_argument("--root")
    ap.add_argument("--item-id")
    ap.add_argument("--message-id")
    ap.add_argument("--direction", choices=["prev", "next"])
    ap.add_argument("--page-size", type=int, default=12)
    args = ap.parse_args()

    state_file = Path(args.state_path)
    if args.command == "open-root":
        if not args.root:
            raise SystemExit("--root is required for open-root")
        root = normalize(args.root)
        # Load existing state if it exists, otherwise initialize new
        if state_file.exists():
            state = load_state(str(state_file))
            state["current"] = str(root)
            state["stack"] = []
        else:
            state = init_state(str(root))
        result = open_root(state, root, page_size=args.page_size)
        save_state(str(state_file), result["state"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    state = load_state(str(state_file))

    if args.command == "open-dir":
        if not args.item_id:
            raise SystemExit("--item-id is required for open-dir")
        result = open_directory(state, args.item_id, page_size=args.page_size)
    elif args.command == "open-file-actions":
        if not args.item_id:
            raise SystemExit("--item-id is required for open-file-actions")
        result = open_file_actions(state, args.item_id)
    elif args.command == "back":
        result = go_back(state, page_size=args.page_size)
    elif args.command == "page":
        if not args.direction:
            raise SystemExit("--direction is required for page")
        result = change_page(state, args.direction, page_size=args.page_size)
    elif args.command == "set-live-message":
        result = {"kind": "state-only", "state": set_live_message_id(state, args.message_id)}
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    save_state(str(state_file), result["state"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
