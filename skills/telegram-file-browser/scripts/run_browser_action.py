#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from file_browser_state import is_duplicate_callback, load_state, path_label, remember_callback, save_state
from browser_config import load_config

SCRIPT_DIR = Path(__file__).resolve().parent
CONTROLLER = SCRIPT_DIR / 'browser_controller.py'
RESOLVER = SCRIPT_DIR / 'resolve_callback.py'
PREVIEW = SCRIPT_DIR / 'preview_file.py'
DEFAULT_CONFIG_PATH = SCRIPT_DIR.parent / 'config.json'


def run_json(cmd: list[str]) -> Dict[str, Any]:
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def open_root(state_path: str, root: str, page_size: int = 12, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Open the root directory and return a plan dict (Python object, not JSON string).
    Can be imported and used directly without JSON parsing.
    """
    if config_path is None:
        config_path = str(DEFAULT_CONFIG_PATH)
    
    state_path = str(Path(state_path).resolve())
    config = load_config(config_path)
    
    result = run_json([
        'python3', str(CONTROLLER), 'open-root', state_path,
        '--root', root,
        '--page-size', str(page_size)
    ])
    
    plan = build_send(result)
    plan['displayMode'] = config.get('displayMode', 'edit-message')
    return plan


def handle_callback(state_path: str, callback: str, page_size: int = 12, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle a callback and return a plan dict (Python object, not JSON string).
    Can be imported and used directly without JSON parsing.
    """
    if config_path is None:
        config_path = str(DEFAULT_CONFIG_PATH)
    
    state_path = str(Path(state_path).resolve())
    config = load_config(config_path)
    
    state = load_state(state_path)
    if is_duplicate_callback(state, callback):
        return {
            'toolAction': 'noop',
            'message': f'duplicate callback ignored: {callback}',
            'state': state
        }

    resolution = run_json(['python3', str(RESOLVER), state_path, callback])
    action = resolution.get('action')

    if action == 'stale':
        remember_and_save(state_path, state, callback)
        return {
            'toolAction': 'noop',
            'message': f"stale callback ignored: {callback}",
            'state': state
        }

    if action == 'close':
        state = load_state(state_path) if Path(state_path).exists() else {}
        remember_and_save(state_path, state, callback)
        return {
            'toolAction': 'delete',
            'messageId': state.get('liveMessageId'),
            'state': state
        }

    state = load_state(state_path)
    live_message_id = state.get('liveMessageId')
    remember_and_save(state_path, state, callback)

    if action == 'back':
        result = run_json(['python3', str(CONTROLLER), 'back', state_path, '--page-size', str(page_size)])
        return build_navigation_plan(live_message_id, result, config.get('displayMode', 'edit-message'))

    if action == 'open-dir':
        item = resolution['item']
        result = run_json([
            'python3', str(CONTROLLER), 'open-dir', state_path,
            '--item-id', item['id'],
            '--page-size', str(page_size)
        ])
        return build_navigation_plan(live_message_id, result, config.get('displayMode', 'edit-message'))

    if action == 'open-file-actions':
        item = resolution['item']
        result = run_json([
            'python3', str(CONTROLLER), 'open-file-actions', state_path,
            '--item-id', item['id']
        ])
        return build_navigation_plan(live_message_id, result, config.get('displayMode', 'edit-message'))

    if action == 'preview':
        item = resolution.get('item')
        if not item:
            return {'toolAction': 'noop', 'message': 'preview target not found', 'state': state}
        preview = run_json(['python3', str(PREVIEW), item['path']])
        item_path_label = path_label(item['path'])
        if preview.get('kind') == 'text':
            body = preview.get('preview', '')
            if preview.get('truncated'):
                body += '\n\n（已截断）'
        else:
            body = preview.get('message', '无法预览该文件')
        return {
            'toolAction': 'send',
            'message': f"📄 `{item_path_label}`\n\n```\n{body}\n```",
            'replyTo': str(live_message_id),
            'state': load_state(state_path)
        }

    if action == 'path':
        item = resolution.get('item')
        if not item:
            return {'toolAction': 'noop', 'message': 'path target not found', 'state': state}
        return {
            'toolAction': 'send',
            'message': path_label(item['path']),
            'replyTo': str(live_message_id),
            'state': load_state(state_path)
        }

    if action == 'download':
        item = resolution.get('item')
        if not item:
            return {'toolAction': 'noop', 'message': 'download target not found', 'state': state}
        path = Path(item['path'])
        if not path.exists() or path.is_dir():
            return {
                'toolAction': 'send',
                'message': f"⚠️ 无法下载：目标不存在或是目录\n{path_label(item['path'])}",
                'replyTo': str(live_message_id),
                'state': load_state(state_path)
            }
        return {
            'toolAction': 'send-file',
            'path': str(path),
            'filename': path.name,
            'caption': f"⬇️ {path_label(item['path'])}",
            'replyTo': str(live_message_id),
            'state': load_state(state_path)
        }

    if action == 'page':
        result = run_json([
            'python3', str(CONTROLLER), 'page', state_path,
            '--direction', resolution['direction'],
            '--page-size', str(page_size)
        ])
        return build_navigation_plan(live_message_id, result, config.get('displayMode', 'edit-message'))

    return {
        'toolAction': 'noop',
        'message': f'Unknown callback: {callback}',
        'state': load_state(state_path)
    }


def build_send(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'toolAction': 'send',
        'message': result['text'],
        'buttons': result.get('buttons'),
        'viewType': result.get('kind'),
        'state': result.get('state', {})
    }


def build_navigation_plan(message_id: str, result: Dict[str, Any], display_mode: str) -> Dict[str, Any]:
    plan = {
        'toolAction': 'send',
        'message': result['text'],
        'buttons': result.get('buttons'),
        'viewType': result.get('kind'),
        'state': result.get('state', {}),
        'displayMode': display_mode,
        'replaceLiveMessage': True,
        'previousMessageId': str(message_id) if message_id is not None else None
    }
    if display_mode == 'edit-message':
        plan['cleanupPreviousMessage'] = True
        plan['cleanupMode'] = 'delete-after-send'
    return plan


def remember_and_save(state_path: str, state: Dict[str, Any], callback: str) -> Dict[str, Any]:
    remember_callback(state, callback)
    save_state(state_path, state)
    return state


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)

    p_open = sub.add_parser('open-root')
    p_open.add_argument('state_path')
    p_open.add_argument('--root', required=True)
    p_open.add_argument('--page-size', type=int, default=12)
    p_open.add_argument('--config-path', default=str(DEFAULT_CONFIG_PATH))

    p_cb = sub.add_parser('handle-callback')
    p_cb.add_argument('state_path')
    p_cb.add_argument('callback')
    p_cb.add_argument('--page-size', type=int, default=12)
    p_cb.add_argument('--config-path', default=str(DEFAULT_CONFIG_PATH))

    args = ap.parse_args()

    if args.command == 'open-root':
        plan = open_root(
            args.state_path,
            args.root,
            args.page_size,
            args.config_path
        )
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    # handle-callback
    plan = handle_callback(
        args.state_path,
        args.callback,
        args.page_size,
        args.config_path
    )
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
