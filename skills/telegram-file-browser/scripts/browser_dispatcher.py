#!/usr/bin/env python3
"""
One-click browser dispatcher: generates plan, validates, returns exact payload.

Usage:
    python3 browser_dispatcher.py open-root
    python3 browser_dispatcher.py handle-callback <callback_data>

Note: Back and Close are handled via callback_data through handle-callback.
"""
import json
import sys
import os

# Add scripts dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from run_browser_action import open_root, handle_callback
from send_plan import build_message_payload
from file_browser_state import default_runtime_state_path, default_workspace_root, load_state, save_state, set_live_message_id


STATE_PATH = str(default_runtime_state_path())
WORKSPACE_ROOT = str(default_workspace_root())


def run_action(action: str, callback_data: str = None):
    """Execute action and return a message-tool-ready payload."""

    if action == "open-root":
        plan = open_root(STATE_PATH, WORKSPACE_ROOT)
    elif action == "handle-callback":
        if not callback_data:
            return {"ok": False, "error": "callback_data required for handle-callback"}
        plan = handle_callback(STATE_PATH, callback_data)
    elif action == "update-message-id":
        # Update liveMessageId after successfully sending a menu
        # NOTE: Do NOT bump version here - that happens when menu content changes
        if not callback_data:
            return {"ok": False, "error": "message_id required for update-message-id"}
        state = load_state(STATE_PATH)
        set_live_message_id(state, callback_data)
        save_state(STATE_PATH, state)
        return {
            "ok": True,
            "toolAction": "noop",
            "message": f"Updated liveMessageId to {callback_data}, version now {state['menuVersion']}"
        }
    else:
        return {"ok": False, "error": f"Unknown action: {action}. Use 'open-root', 'handle-callback', or 'update-message-id'"}

    tool_action = plan.get("toolAction")

    if tool_action == "noop":
        return {
            "ok": True,
            "toolAction": "noop",
            "messageToolCall": None,
        }

    if tool_action == "delete":
        message_tool_call = {
            "action": "delete",
            "messageId": plan.get("messageId")
        }
        return {
            "ok": True,
            "toolAction": "delete",
            "messageToolCall": message_tool_call,
            "messageId": plan.get("messageId")
        }

    if tool_action == "send-file":
        message_tool_call = {
            "action": "send",
            "path": plan.get("path"),
            "caption": plan.get("caption"),
        }
        if plan.get("replyTo") is not None:
            message_tool_call["replyTo"] = plan.get("replyTo")
        if plan.get("filename") is not None:
            message_tool_call["filename"] = plan.get("filename")
        return {
            "ok": True,
            "toolAction": "send-file",
            "messageToolCall": message_tool_call,
            "path": plan.get("path"),
            "caption": plan.get("caption"),
            "replyTo": plan.get("replyTo")
        }

    if tool_action != "send":
        return {"ok": False, "error": f"Unsupported toolAction: {tool_action}"}

    if plan.get("buttons") is not None:
        validated = build_message_payload(plan)
        if not validated.get("ok"):
            return {"ok": False, "error": validated.get("error")}
        message_tool_call = dict(validated["payload"])
    else:
        message = plan.get("message")
        if not isinstance(message, str) or not message:
            return {"ok": False, "error": "message must be a non-empty string"}
        message_tool_call = {
            "action": "send",
            "message": message,
        }
        if plan.get("replyTo") is not None:
            message_tool_call["replyTo"] = plan.get("replyTo")

    post_send = {
        "updateLiveMessageId": bool(plan.get("replaceLiveMessage") or plan.get("liveMessageId") is None) and plan.get("buttons") is not None,
        "cleanupPreviousMessage": bool(plan.get("cleanupPreviousMessage")),
        "previousMessageId": plan.get("previousMessageId"),
    }

    return {
        "ok": True,
        "toolAction": "send",
        "messageToolCall": message_tool_call,
        "postSend": post_send,
        # Backward-compatible fields
        "message": message_tool_call["message"],
        "buttons": message_tool_call.get("buttons"),
        "replyTo": message_tool_call.get("replyTo"),
        "liveMessageId": plan.get("liveMessageId"),
        "previousMessageId": plan.get("previousMessageId"),
        "replaceLiveMessage": plan.get("replaceLiveMessage"),
        "cleanupPreviousMessage": plan.get("cleanupPreviousMessage")
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: browser_dispatcher.py <action> [callback_data]"}))
        sys.exit(1)
    
    action = sys.argv[1]
    callback_data = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = run_action(action, callback_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
