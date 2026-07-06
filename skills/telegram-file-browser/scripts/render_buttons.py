#!/usr/bin/env python3
import argparse
import json
from typing import Any, Dict, List, Optional


def make_button(text: str, callback_data: str, style: Optional[str] = None) -> Dict[str, Any]:
    button: Dict[str, Any] = {"text": text, "callback_data": callback_data}
    if style:
        button["style"] = style
    return button


def render_directory_buttons(view: Dict[str, Any], callback_prefix: str, include_back: bool = False, version: int = 1) -> List[List[Dict[str, Any]]]:
    rows: List[List[Dict[str, Any]]] = []
    for item in view.get("items", []):
        icon = "📁" if item.get("type") == "dir" else "📄"
        style = "primary" if item.get("type") == "dir" else None
        rows.append([make_button(f"{icon} {item.get('name')}", f"{callback_prefix}_v{version}_{item.get('id')}", style)])

    nav_row: List[Dict[str, Any]] = []
    if view.get("hasPrev"):
        nav_row.append(make_button("⬅️ 上一页", f"{callback_prefix}_v{version}_page_prev", "primary"))
    if view.get("hasNext"):
        nav_row.append(make_button("➡️ 下一页", f"{callback_prefix}_v{version}_page_next", "primary"))
    if nav_row:
        rows.append(nav_row)

    control_row: List[Dict[str, Any]] = []
    if include_back:
        control_row.append(make_button("⬅️ 返回上级", f"tfb_back_v{version}", "primary"))
    control_row.append(make_button("❌ 关闭", f"tfb_close_v{version}", "danger"))
    rows.append(control_row)
    return rows


def render_file_action_buttons(file_id: str, version: int = 1) -> List[List[Dict[str, Any]]]:
    return [
        [make_button("👁 预览", f"tfb_preview_v{version}_{file_id}", "primary")],
        [make_button("📋 路径", f"tfb_path_v{version}_{file_id}")],
        [make_button("⬇️ 下载", f"tfb_download_v{version}_{file_id}", "primary")],
        [make_button("⬅️ 返回", f"tfb_back_v{version}", "primary")],
        [make_button("❌ 关闭", f"tfb_close_v{version}", "danger")]
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["directory", "file-actions"])
    ap.add_argument("input")
    ap.add_argument("--callback-prefix", default="tfb")
    ap.add_argument("--include-back", action="store_true")
    ap.add_argument("--file-id")
    args = ap.parse_args()

    if args.mode == "directory":
        view = json.loads(args.input)
        print(json.dumps(render_directory_buttons(view, args.callback_prefix, args.include_back), ensure_ascii=False, indent=2))
        return

    if args.mode == "file-actions":
        if not args.file_id:
            raise SystemExit("--file-id is required for file-actions mode")
        print(json.dumps(render_file_action_buttons(args.file_id), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
