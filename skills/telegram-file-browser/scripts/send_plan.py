#!/usr/bin/env python3
import argparse
import json
from typing import Any, Dict, Optional


def _fail(error: str) -> Dict[str, Any]:
    return {"ok": False, "error": error}


def validate_buttons(buttons: Any, view_type: Optional[str] = None) -> Dict[str, Any]:
    if buttons is None:
        return _fail("buttons is required for send plans")
    if isinstance(buttons, str):
        return _fail("buttons must be a real 2D array, not a JSON string")
    if not isinstance(buttons, list):
        return _fail("buttons must be a list of rows")
    if not buttons:
        return _fail("buttons must not be empty")

    for row_index, row in enumerate(buttons, start=1):
        if not isinstance(row, list):
            return _fail(f"row {row_index} must be a list")
        if not row:
            return _fail(f"row {row_index} must not be empty")
        for button_index, button in enumerate(row, start=1):
            if not isinstance(button, dict):
                return _fail(f"row {row_index} button {button_index} must be an object")
            if not button.get("text"):
                return _fail(f"row {row_index} button {button_index} is missing text")
            if not button.get("callback_data"):
                return _fail(f"row {row_index} button {button_index} is missing callback_data")
            if isinstance(button["callback_data"], str) and "/" in button["callback_data"]:
                return _fail(f"row {row_index} button {button_index} callback_data must stay opaque and must not contain raw paths")

    if view_type == "directory":
        for row_index, row in enumerate(buttons, start=1):
            first = row[0]
            callback = str(first.get("callback_data", ""))
            is_item_row = not ("_page_" in callback or callback.startswith("tfb_back_") or callback.startswith("tfb_close_"))
            if is_item_row and len(row) != 1:
                return _fail(f"viewType={view_type} requires one item per row; row {row_index} has {len(row)} buttons")

    if view_type == "file-actions":
        for row_index, row in enumerate(buttons, start=1):
            if len(row) != 1:
                return _fail(f"viewType={view_type} requires one action per row; row {row_index} has {len(row)} buttons")

    return {"ok": True, "rows": len(buttons)}


def build_message_payload(plan: Dict[str, Any]) -> Dict[str, Any]:
    tool_action = plan.get("toolAction")
    if tool_action != "send":
        return _fail(f"send_plan only supports toolAction=send, got {tool_action!r}")

    message = plan.get("message")
    if not isinstance(message, str) or not message:
        return _fail("message must be a non-empty string")

    view_type = plan.get("viewType")
    validation = validate_buttons(plan.get("buttons"), view_type=view_type)
    if not validation.get("ok"):
        return validation

    payload: Dict[str, Any] = {
        "action": "send",
        "message": message,
        "buttons": plan["buttons"],
    }
    if plan.get("replyTo") is not None:
        payload["replyTo"] = plan["replyTo"]

    return {
        "ok": True,
        "payload": payload,
        "meta": {
            "viewType": view_type,
            "rows": validation["rows"],
        }
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_json", help="JSON string for a run_browser_action.py plan")
    args = ap.parse_args()

    plan = json.loads(args.plan_json)
    print(json.dumps(build_message_payload(plan), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
