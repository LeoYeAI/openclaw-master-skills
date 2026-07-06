#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from run_browser_action import handle_callback, open_root
from send_plan import build_message_payload
from file_browser_state import default_workspace_root
import browser_dispatcher
from browser_dispatcher import run_action

ROOT = str(default_workspace_root())


def assert_valid(plan: dict) -> None:
    result = build_message_payload(plan)
    assert result["ok"], result
    payload = result["payload"]
    assert isinstance(payload["buttons"], list)
    assert all(isinstance(row, list) for row in payload["buttons"])


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = str(Path(tmpdir) / "state.json")

        root_plan = open_root(state_path, ROOT)
        assert root_plan["viewType"] == "directory"
        assert_valid(root_plan)

        next_plan = handle_callback(state_path, "tfb_root_v1_page_next")
        assert next_plan["viewType"] == "directory"
        assert_valid(next_plan)

        root_again = open_root(state_path, ROOT)
        first_dir_callback = root_again["buttons"][0][0]["callback_data"]
        dir_plan = handle_callback(state_path, first_dir_callback)
        assert dir_plan["viewType"] == "directory"
        assert_valid(dir_plan)

        root_again = open_root(state_path, ROOT)
        file_callback = None
        for row in root_again["buttons"]:
            button = row[0]
            if button["text"].startswith("📄 "):
                file_callback = button["callback_data"]
                break
        assert file_callback, "expected at least one file on root page"

        file_actions = handle_callback(state_path, file_callback)
        assert file_actions["viewType"] == "file-actions"
        assert_valid(file_actions)

        broken = json.loads(json.dumps(root_plan))
        broken["buttons"] = [[button for row in root_plan["buttons"] for button in row]]
        broken_result = build_message_payload(broken)
        assert not broken_result["ok"], broken_result

        browser_dispatcher.STATE_PATH = state_path
        browser_dispatcher.WORKSPACE_ROOT = ROOT

        dispatcher_root = run_action("open-root")
        assert dispatcher_root["ok"], dispatcher_root
        assert dispatcher_root["messageToolCall"]["action"] == "send"
        assert dispatcher_root["messageToolCall"]["message"] == dispatcher_root["message"]
        assert dispatcher_root["messageToolCall"]["buttons"] == dispatcher_root["buttons"]
        assert isinstance(dispatcher_root["messageToolCall"]["buttons"], list)
        assert all(isinstance(row, list) for row in dispatcher_root["messageToolCall"]["buttons"])

        preview_callback = f"tfb_preview_v{file_actions['state']['menuVersion']}_{file_actions['state']['selectedFileId']}"
        preview_dispatch = run_action("handle-callback", preview_callback)
        assert preview_dispatch["ok"], preview_dispatch
        assert preview_dispatch["messageToolCall"]["action"] == "send"
        assert isinstance(preview_dispatch["messageToolCall"]["message"], str)
        assert preview_dispatch["messageToolCall"]["message"]
        assert "buttons" not in preview_dispatch["messageToolCall"]

        print(json.dumps({
            "ok": True,
            "tested": [
                "root",
                "page-next",
                "open-dir",
                "file-actions",
                "flattened-buttons-rejected",
                "dispatcher-message-tool-call",
                "dispatcher-text-send-without-buttons"
            ]
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
