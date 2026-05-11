#!/usr/bin/env python3
"""
Medo Platform API CLI Client

Usage:
    python medo_api.py --api-key <token> [--base-url <url>] <command> [options]

Environment variables:
    MEDO_API_KEY    - Bearer token (alternative to --api-key)
    MEDO_BASE_URL   - Platform base URL (alternative to --base-url)
"""

import argparse
import json
import os
import sys
import time
import uuid
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' package not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

DEFAULT_BASE_URL = "https://cwk7oh9oyc.execute-api.us-west-2.amazonaws.com"
VERSION = "1.0.0"
CLIENT = "clawhub"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def auth_headers(api_key: str) -> dict:
    """Return HTTP headers with Bearer token authentication, JSON content type, and custom User-Agent."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": f"medo-app-builder/{CLIENT}-{VERSION}",
    }


def raise_for_api_error(resp: "requests.Response"):
    """Raise RuntimeError if the HTTP response or the API-level status indicates an error.

    Checks both the HTTP status code (via raise_for_status) and the JSON body's
    ``status`` field.  Returns the parsed body on success.
    """
    resp.raise_for_status()
    body = resp.json()
    if body.get("status") != 0:
        msg = body.get("msg") or body.get("message") or json.dumps(body)
        raise RuntimeError(f"API error (status={body.get('status')}): {msg}")
    return body


# ---------------------------------------------------------------------------
# 1. List Apps (应用基本信息)
# ---------------------------------------------------------------------------

_LIST_APPS_STRIP = {"avatar", "mobileCover", "hasAppHost", "hasBackend"}
_LIST_APPS_BRIEF_KEEP = {"appId", "name", "type", "appFocus", "host", "updatedAt"}

def list_apps(
    base_url: str,
    api_key: str,
    name: str = "",
    page: int = 1,
    size: int = 12,
    brief: bool = False,
) -> dict:
    """POST /api/v1/app/list — paginated app list."""
    url = f"{base_url.rstrip('/')}/api/v1/app/list"
    payload = {
        "name": name,
        "page": page,
        "size": size,
        "sort": {"direction": "desc", "property": "updatedAt"},
    }
    resp = requests.post(url, json=payload, headers=auth_headers(api_key), timeout=30)
    result = raise_for_api_error(resp)
    data = result.get("data", {})
    # Accommodate both "items" and "list" response keys (API may vary)
    items = data.get("items", data.get("list", []))
    if brief:
        items = [
            {k: v for k, v in item.items() if k in _LIST_APPS_BRIEF_KEEP}
            for item in items
        ]
    else:
        for item in items:
            for key in _LIST_APPS_STRIP:
                item.pop(key, None)
    if "items" in data:
        data["items"] = items
    elif "list" in data:
        data["list"] = items
    return result


# ---------------------------------------------------------------------------
# 2. App Detail (应用详情)
# ---------------------------------------------------------------------------

def get_app_detail(
    base_url: str,
    api_key: str,
    app_id: str,
) -> dict:
    """GET /api/v1/app/bootstrap/{app_id} — app detail."""
    url = f"{base_url.rstrip('/')}/api/v1/app/bootstrap/{app_id}"
    resp = requests.get(url, headers=auth_headers(api_key), timeout=30)
    result = raise_for_api_error(resp)
    data = result.get("data", {})
    for key in ("hasBackend", "hasAppHost", "sandboxUrl"):
        data.pop(key, None)
    return result


# ---------------------------------------------------------------------------
# 3. Chat (two-step: POST chat → SSE trajectory)
# ---------------------------------------------------------------------------

def _build_chat_payload(
    text: str,
    context_id: str = "",
    app_id: Optional[str] = None,
    query_mode: str = "deep_mode",
    input_field_type: str = "web",
    lang: str = "zh",
    user_confirmation: Optional[dict] = None,
) -> dict:
    """Build a JSON-RPC 2.0 ``message/send`` payload for the chat endpoint.

    When ``user_confirmation`` is provided it replaces ``inputFieldType`` in the
    request metadata, which is used to send confirmation actions such as
    ``{"type": "generateApp"}``.  Leave ``context_id`` empty to create a new app;
    pass the existing ``conversationId`` to continue an existing conversation.
    """
    params_metadata: dict = {
        "defaultAgent": "AdaPro",
        "agentConfig": {},
        "runtime": "miaoda",
        "queryMode": query_mode,
    }
    if user_confirmation is not None:
        params_metadata["userConfirmation"] = user_confirmation
    else:
        params_metadata["inputFieldType"] = input_field_type

    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": str(uuid.uuid4()),
        "params": {
            "message": {
                "parts": [{"kind": "text", "text": text}],
                "kind": "message",
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "contextId": context_id,
                "metadata": {},
                "taskId": "",
                "lang": lang,
            },
            "metadata": params_metadata,
        },
    }
    if app_id:
        payload["params"]["metadata"]["appId"] = app_id
    return payload


def _check_chat_response_for_error(chat_result: dict) -> None:
    """Raise RuntimeError if the chat POST response already indicates a terminal failure.

    When the platform rejects the request immediately (e.g. insufficient balance),
    it returns a ``state=failed`` or ``final=true`` JSON-RPC response directly in
    the POST body rather than via the trajectory stream.  Detecting this early
    avoids a pointless trajectory poll and surfaces the error message clearly.
    """
    result = chat_result.get("result", {})
    state = result.get("status", {}).get("state", "")
    is_final = result.get("final", False)
    if state == "failed" or is_final:
        # Extract the human-readable error text from message parts if available
        parts = result.get("status", {}).get("message", {}).get("parts", [])
        text_parts = [p.get("text", "") for p in parts if p.get("kind") == "text"]
        error_text = " ".join(text_parts).strip() or json.dumps(chat_result, ensure_ascii=False)
        print(json.dumps(chat_result, ensure_ascii=False), flush=True)
        raise RuntimeError(f"Chat request failed: {error_text}")


def _extract_ids_from_chat_response(
    chat_result: dict, fallback_app_id: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Extract (appId, conversationId) from the chat POST response.

    Response path: result.status.message.metadata.{appId, conversationId}
    For a new app (contextId=""), both values are freshly assigned by the server.
    """
    try:
        metadata = (
            chat_result
            .get("result", {})
            .get("status", {})
            .get("message", {})
            .get("metadata", {})
        )
        app_id = metadata.get("appId") or fallback_app_id
        conversation_id = metadata.get("conversationId")
        return app_id, conversation_id
    except (AttributeError, TypeError):
        return fallback_app_id, None


def chat_no_stream(
    base_url: str,
    api_key: str,
    text: str,
    context_id: str = "",
    app_id: Optional[str] = None,
    query_mode: str = "deep_mode",
    input_field_type: str = "web",
    user_confirmation: Optional[dict] = None,
) -> dict:
    """POST /api/v1/conversation/chat — returns raw JSON-RPC response without streaming."""
    url = f"{base_url.rstrip('/')}/api/v1/conversation/chat"
    payload = _build_chat_payload(
        text, context_id, app_id, query_mode, input_field_type,
        user_confirmation=user_confirmation,
    )
    resp = requests.post(url, json=payload, headers=auth_headers(api_key), timeout=60)
    resp.raise_for_status()
    chat_result = resp.json()
    _check_chat_response_for_error(chat_result)
    return chat_result


def chat_stream(
    base_url: str,
    api_key: str,
    text: str,
    context_id: str = "",
    app_id: Optional[str] = None,
    query_mode: str = "deep_mode",
    input_field_type: str = "web",
    prompt_generate: bool = False,
    poll_interval: float = 2.0,
    fetch_timeout: int = 10,
):
    """
    Two-step chat flow:
      1. POST /api/v1/conversation/chat
      2. Poll GET /api/v1/conversation/trajectory?stream=false until terminal state

    When context_id="" a new app is created. Prints a header line:
      {"appId": "...", "conversationId": "..."}
    then polls trajectory events and prints each as a JSON line.

    If prompt_generate=True and the trajectory returns immediately generated text,
    prompts the user interactively whether to submit the app (generate-app confirmation).
    """
    # Guard: --app-id without a valid --context-id silently creates a NEW app every time.
    # Also catches bash jq -r returning the literal string "null" for a missing field.
    _INVALID_CONTEXT = {"", "null", "undefined", "none"}
    if app_id and context_id.strip().lower() in _INVALID_CONTEXT:
        raise RuntimeError(
            f"--app-id ({app_id}) was provided but --context-id is missing or invalid "
            f"(got: {context_id!r}).\n"
            "The platform will NOT modify the existing app — it will create a brand-new one.\n"
            "To continue/modify an existing app:  --app-id <appId> --context-id <conversationId>\n"
            "To create a new app from scratch:    omit both --app-id and --context-id\n"
            "To recover a lost conversationId:    python scripts/medo_api.py get-context-id --app-id <appId>"
        )

    # Step 1: submit chat
    chat_url = f"{base_url.rstrip('/')}/api/v1/conversation/chat"
    payload = _build_chat_payload(text, context_id, app_id, query_mode, input_field_type)

    resp = requests.post(chat_url, json=payload, headers=auth_headers(api_key), timeout=60)
    resp.raise_for_status()
    chat_result = resp.json()
    _check_chat_response_for_error(chat_result)

    # Step 2: resolve appId and conversationId
    resolved_app_id, resolved_conversation_id = _extract_ids_from_chat_response(chat_result, app_id)
    if not resolved_app_id:
        raise RuntimeError(
            "Could not extract appId from chat response. "
            "Check that context-id / app-id is correct, or leave context-id empty to create a new app."
        )

    # Print resolved IDs so the caller can store them for follow-up requests
    print(
        json.dumps(
            {"appId": resolved_app_id, "conversationId": resolved_conversation_id},
            ensure_ascii=False,
        ),
        flush=True,
    )

    text_output = poll_trajectory(
        base_url, api_key, resolved_app_id,
        poll_interval=poll_interval,
        fetch_timeout=fetch_timeout,
    )

    # If the trajectory returned immediately generated text, optionally prompt the user
    if prompt_generate and text_output.strip():
        print(
            "\n[提示] 上游已返回生成的文本，是否提交应用？(y/n): ",
            end="",
            flush=True,
        )
        answer = input().strip().lower()
        if answer in ("y", "yes", "是"):
            print("\n[提交应用]", flush=True)
            generate_app_confirmation(
                base_url, api_key,
                context_id=resolved_conversation_id or context_id,
                app_id=resolved_app_id,
                query_mode=query_mode,
                watch=True,
                poll_interval=poll_interval,
                fetch_timeout=fetch_timeout,
            )


def generate_app_confirmation(
    base_url: str,
    api_key: str,
    context_id: str = "",
    app_id: Optional[str] = None,
    query_mode: str = "deep_mode",
    watch: bool = False,
    poll_interval: float = 2.0,
    fetch_timeout: int = 10,
) -> dict:
    """POST /api/v1/conversation/chat with userConfirmation: {type: "generateApp"}.

    Submits the app-generation confirmation and returns immediately with the
    server's ``state=submitted`` response.  The resolved ``appId`` and
    ``conversationId`` are printed as a JSON line so callers can capture them.

    When ``watch=True`` the function additionally calls ``poll_trajectory`` to
    block until the generation reaches a terminal state.  For long-running
    generations prefer leaving ``watch=False`` and checking status separately
    with ``fetch_trajectory_once`` (or the ``fetch-trajectory`` CLI command).
    """
    _INVALID_CONTEXT = {"", "null", "undefined", "none"}
    if app_id and context_id.strip().lower() in _INVALID_CONTEXT:
        raise RuntimeError(
            f"--app-id ({app_id}) was provided but --context-id is missing or invalid "
            f"(got: {context_id!r}).\n"
            "The platform will NOT modify the existing app — it will create a brand-new one.\n"
            "Provide --context-id <conversationId> to confirm generation for the correct app."
        )

    chat_url = f"{base_url.rstrip('/')}/api/v1/conversation/chat"
    payload = _build_chat_payload(
        text="生成应用",
        context_id=context_id,
        app_id=app_id,
        query_mode=query_mode,
        user_confirmation={"type": "generateApp"},
    )
    resp = requests.post(chat_url, json=payload, headers=auth_headers(api_key), timeout=60)
    resp.raise_for_status()
    result = resp.json()
    _check_chat_response_for_error(result)

    resolved_app_id, resolved_conversation_id = _extract_ids_from_chat_response(result, app_id)
    print(
        json.dumps(
            {"appId": resolved_app_id, "conversationId": resolved_conversation_id},
            ensure_ascii=False,
        ),
        flush=True,
    )

    if watch and resolved_app_id:
        poll_trajectory(
            base_url, api_key, resolved_app_id,
            poll_interval=poll_interval,
            fetch_timeout=fetch_timeout,
        )

    return result


# ---------------------------------------------------------------------------
# 4. Conversation Trajectory
# ---------------------------------------------------------------------------

def _extract_text_from_event(event: dict) -> str:
    """Return concatenated text from a trajectory event's message parts (empty if none)."""
    result = event.get("result", {})
    status = result.get("status", {})
    message = status.get("message")
    if not message:
        return ""
    parts = message.get("parts", [])
    return "".join(p.get("text", "") for p in parts if p.get("kind") == "text")


def _extract_event_id(event: dict) -> Optional[int]:
    """Return result.metadata.eventId from a trajectory event, or None if absent."""
    try:
        return event.get("result", {}).get("metadata", {}).get("eventId")
    except (AttributeError, TypeError):
        return None


def _is_terminal_event(event: dict) -> bool:
    """Return True if the event represents a terminal state (completed / failed / final)."""
    result_obj = event.get("result", {})
    state = result_obj.get("status", {}).get("state", "")
    return state in ("completed", "input-required", "failed") or bool(result_obj.get("final"))


def fetch_trajectory_once(
    base_url: str,
    api_key: str,
    app_id: str,
    last_event_id: int = -1,
    timeout: int = 10,
) -> tuple[list, int, bool]:
    """GET /api/v1/conversation/trajectory?stream=false — single non-SSE fetch.

    Fetches a batch of trajectory events starting after ``last_event_id``.
    Pass ``last_event_id=-1`` to retrieve all events from the beginning.

    Returns:
        events       - list of event dicts (JSON-RPC 2.0 objects)
        max_event_id - highest ``result.metadata.eventId`` seen in this batch,
                       or the original ``last_event_id`` if no events were returned
        is_terminal  - True if any event in the batch is a terminal state
    """
    url = f"{base_url.rstrip('/')}/api/v1/conversation/trajectory"
    params = {"appId": app_id, "lastEventId": last_event_id, "stream": "false"}

    resp = requests.get(url, params=params, headers=auth_headers(api_key), timeout=timeout)
    resp.raise_for_status()
    body = resp.json()

    # Normalise the response: the endpoint may return a list directly,
    # or wrap events in {"status": 0, "data": [...]} / {"status": 0, "data": {"events": [...]}}
    if isinstance(body, list):
        events = body
    elif isinstance(body, dict):
        data = body.get("data", body)
        if isinstance(data, list):
            events = data
        elif isinstance(data, dict):
            events = data.get("events", [data])
        else:
            events = [body]
    else:
        events = []

    max_event_id = last_event_id
    is_terminal = False
    for event in events:
        eid = _extract_event_id(event)
        if eid is not None and eid > max_event_id:
            max_event_id = eid
        if _is_terminal_event(event):
            is_terminal = True

    return events, max_event_id, is_terminal


def poll_trajectory(
    base_url: str,
    api_key: str,
    app_id: str,
    last_event_id: int = -1,
    poll_interval: float = 2.0,
    fetch_timeout: int = 10,
) -> str:
    """Poll GET /api/v1/conversation/trajectory?stream=false until a terminal state.

    Calls ``fetch_trajectory_once`` repeatedly, printing each event as a JSON
    line and advancing ``lastEventId`` with each batch.  Stops when the server
    returns a completed / failed / final event.

    Returns concatenated text from all text-part events (empty string if none).
    """
    text_output = ""
    current_last_id = last_event_id

    while True:
        events, max_event_id, is_terminal = fetch_trajectory_once(
            base_url, api_key, app_id, current_last_id, timeout=fetch_timeout,
        )
        for event in events:
            print(json.dumps(event, ensure_ascii=False), flush=True)
            text_output += _extract_text_from_event(event)

        current_last_id = max_event_id

        if is_terminal:
            break

        time.sleep(poll_interval)

    return text_output


def stream_trajectory(
    base_url: str,
    api_key: str,
    app_id: str,
    last_event_id: int = 0,
) -> str:
    """GET /api/v1/conversation/trajectory — SSE stream (legacy).

    Prints each event as a JSON line. Stops at [DONE], state==completed/failed,
    or final==true.  Returns concatenated text from all text-part events.
    Prefer ``poll_trajectory`` for more reliable long-running tasks.
    """
    url = f"{base_url.rstrip('/')}/api/v1/conversation/trajectory"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    params = {"appId": app_id, "lastEventId": last_event_id}

    resp = requests.get(url, params=params, headers=headers, stream=True, timeout=300)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    text_output = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("data:"):
            data_str = line[5:].strip()
            # Handle double-prefix edge case
            if data_str.startswith("data:"):
                data_str = data_str[5:].strip()
            if data_str in ("[DONE]", "[done]"):
                break
            try:
                event = json.loads(data_str)
                print(json.dumps(event, ensure_ascii=False), flush=True)
                text_output += _extract_text_from_event(event)
                if _is_terminal_event(event):
                    break
            except json.JSONDecodeError:
                continue
    return text_output


# ---------------------------------------------------------------------------
# 4b. Get Context ID / Conversation History
# ---------------------------------------------------------------------------

def get_context_id(
    base_url: str,
    api_key: str,
    app_id: str,
    fetch_timeout: int = 10,
) -> Optional[str]:
    """Extract the conversationId (contextId) for an existing app by reading its trajectory.

    Scans ALL trajectory events and returns the MOST RECENT (last) non-empty contextId
    found, checking two paths per event:
      1. result.contextId           — direct field present in some event types
      2. result.status.message.metadata.conversationId  — same path as chat POST response

    Returning the most recent value ensures multi-round modification gets the
    up-to-date contextId in case the platform rotates it across interactions.
    Returns ``None`` if no events exist or neither field is found in any event.
    """
    events, _, _ = fetch_trajectory_once(
        base_url, api_key, app_id, last_event_id=-1, timeout=fetch_timeout,
    )
    found: Optional[str] = None
    for event in events:
        result = event.get("result", {})
        # Path 1: result.contextId
        ctx = result.get("contextId")
        if ctx:
            found = ctx
            continue
        # Path 2: result.status.message.metadata.conversationId (same as chat response)
        ctx = (
            result.get("status", {})
            .get("message", {})
            .get("metadata", {})
            .get("conversationId")
        )
        if ctx:
            found = ctx
    return found


def get_conversation_history(
    base_url: str,
    api_key: str,
    app_id: str,
    full: bool = False,
    limit: Optional[int] = None,
    fetch_timeout: int = 10,
) -> list[dict]:
    """Parse trajectory events into a human-readable conversation history.

    Returns a list of dicts, each representing one meaningful conversation turn:
      {"eventId": int, "role": str, "type": str, "content": str}

    Roles: "user", "agent", "system"
    Types: "message", "file", "status", "action"
    """
    events, _, _ = fetch_trajectory_once(
        base_url, api_key, app_id, last_event_id=-1, timeout=fetch_timeout,
    )

    history: list[dict] = []
    max_content = 200 if not full else 100_000

    for event in events:
        result = event.get("result", {})
        role = result.get("role", "")
        metadata = result.get("metadata", {})
        event_id = metadata.get("eventId")
        state = result.get("status", {}).get("state", "") if isinstance(result.get("status"), dict) else ""

        parts = result.get("parts", [])
        content_pieces: list[str] = []
        entry_type = "message"

        for p in parts:
            kind = p.get("kind", "")
            if kind == "text":
                text = p.get("text", "").strip()
                if text:
                    content_pieces.append(text[:max_content])
            elif kind == "data":
                data = p.get("data", {})
                dtype = data.get("type", "")
                if dtype == "filePart":
                    fname = data.get("filename", "")
                    ftext = data.get("text", "").strip()
                    entry_type = "file"
                    if full and ftext:
                        content_pieces.append(f"[file: {fname}] {ftext[:max_content]}")
                    else:
                        content_pieces.append(f"[file: {fname}]")
                elif dtype == "extension":
                    ext = data.get("extension", {})
                    content_pieces.append(f"[style: {ext.get('name', '')}]")
                elif dtype == "userConfirmation":
                    entry_type = "action"
                    content_pieces.append(f"[confirm: {data.get('type', '')}]")
                elif dtype == "file_edit_action":
                    entry_type = "action"
                    action = data.get("action_name", data.get("action", ""))
                    path = data.get("path", "")
                    content_pieces.append(f"[{action}: {path}]")
                elif dtype == "cmd_run_observation":
                    entry_type = "action"
                    content_pieces.append(f"[cmd: {data.get('observation', '')}]")

        content = " ".join(content_pieces).strip()

        if role in ("user", "agent"):
            if content:
                history.append({
                    "eventId": event_id,
                    "role": role,
                    "type": entry_type,
                    "content": content,
                })
        elif state and state != "working":
            history.append({
                "eventId": event_id,
                "role": "system",
                "type": "status",
                "content": f"state={state}",
            })

    if limit is not None and limit > 0:
        history = history[-limit:]

    return history


# ---------------------------------------------------------------------------
# 5. Publish App
# ---------------------------------------------------------------------------

def publish_app(
    base_url: str,
    api_key: str,
    app_id: str,
    app_env: str = "PRODUCE",
    enable_weapp_mini_program: bool = True,
    is_release_app_square: bool = False,
) -> dict:
    """POST /api/v1/app/release — triggers a release, returns releaseId."""
    url = f"{base_url.rstrip('/')}/api/v1/app/release"
    payload = {
        "appId": app_id,
        "appEnv": app_env,
        "enableWeappMiniProgram": enable_weapp_mini_program,
        "isReleaseAppSquare": is_release_app_square,
    }
    resp = requests.post(url, json=payload, headers=auth_headers(api_key), timeout=120)
    resp.raise_for_status()
    return resp.json()


def get_publish_status(
    base_url: str,
    api_key: str,
    release_id: str,
) -> dict:
    """GET /api/v1/app/release/status/{release_id}"""
    url = f"{base_url.rstrip('/')}/api/v1/app/release/status/{release_id}"
    resp = requests.get(url, headers=auth_headers(api_key), timeout=120)
    resp.raise_for_status()
    return resp.json()


def publish_and_wait(
    base_url: str,
    api_key: str,
    app_id: str,
    app_env: str = "PRODUCE",
    poll_interval: int = 3,
    max_wait: int = 300,
) -> dict:
    """Publish an app and poll until SUCCESS or FAILED."""
    result = publish_app(base_url, api_key, app_id, app_env)
    if result.get("status") != 0:
        raise RuntimeError(f"Publish failed: {result.get('msg')}")

    release_id = result.get("data", {}).get("releaseId")
    if not release_id:
        raise RuntimeError("No releaseId in publish response")

    print(json.dumps({"releaseId": release_id, "status": "PROCESSING"}, ensure_ascii=False), flush=True)

    start = time.time()
    while True:
        if time.time() - start > max_wait:
            raise TimeoutError(f"Publish timed out after {max_wait}s (releaseId={release_id})")

        status_result = get_publish_status(base_url, api_key, release_id)
        data = status_result.get("data", {})
        status = data.get("status", "UNKNOWN")

        print(json.dumps({"releaseId": release_id, "status": status}, ensure_ascii=False), flush=True)

        if status == "SUCCESS":
            return status_result
        if status == "FAILED":
            raise RuntimeError(f"Publish FAILED (releaseId={release_id})")

        time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="Medo Platform API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("MEDO_API_KEY"),
        help="Bearer token (or set MEDO_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",   
        default=os.environ.get("MEDO_BASE_URL", DEFAULT_BASE_URL),
        help=f"Platform host URL (default: {DEFAULT_BASE_URL})",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # list-apps
    p = sub.add_parser("list-apps", help="List apps with basic info (paginated)")
    p.add_argument("--name", default="", help="Filter by app name (substring)")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--size", type=int, default=12)
    p.add_argument(
        "--brief",
        action="store_true",
        help="Output only key fields: appId, name, type, appFocus, host, updatedAt (reduces token usage)",
    )

    # app-detail
    p = sub.add_parser("app-detail", help="Get app detail by ID (auto-injects conversationId by default)")
    p.add_argument("--app-id", required=True, help="Application ID")
    p.add_argument(
        "--no-context",
        action="store_true",
        help="Skip auto-fetching conversationId from trajectory (faster but no contextId in response)",
    )

    # chat
    p = sub.add_parser("chat", help="Send a chat message and stream the response")
    p.add_argument("--text", required=True, help="Message text (user query)")
    p.add_argument(
        "--context-id",
        default="",
        help="conversationId of an existing app. Leave empty to create a new app (default: '')",
    )
    p.add_argument("--app-id", default=None, help="App ID (optional, improves routing for existing apps)")
    p.add_argument(
        "--query-mode",
        default="deep_mode",
        help="Query mode (default: deep_mode)",
    )
    p.add_argument(
        "--input-field-type",
        default="web",
        help="Input field type (default: web)",
    )
    p.add_argument(
        "--no-stream",
        action="store_true",
        help="Return raw chat POST response without trajectory polling",
    )
    p.add_argument(
        "--prompt-generate",
        action="store_true",
        help="After polling, interactively ask whether to submit app generation if text was returned",
    )
    p.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds between trajectory polls (default: 2.0)",
    )
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Per-request timeout in seconds for each trajectory fetch (default: 10)",
    )

    # generate-app
    p = sub.add_parser(
        "generate-app",
        help="Submit app generation confirmation and return immediately with appId/conversationId",
    )
    p.add_argument("--context-id", default="", help="conversationId of the app to generate")
    p.add_argument("--app-id", default=None, help="App ID (optional)")
    p.add_argument("--query-mode", default="deep_mode", help="Query mode (default: deep_mode)")
    p.add_argument(
        "--watch",
        action="store_true",
        help="Block and poll trajectory until generation completes (default: return immediately)",
    )
    p.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds between polls when --watch is set (default: 2.0)",
    )
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Per-request timeout in seconds when --watch is set (default: 10)",
    )

    # trajectory  (polling, default)
    p = sub.add_parser(
        "trajectory",
        help="Poll trajectory until terminal state (non-SSE, default)",
    )
    p.add_argument("--app-id", required=True, help="Application ID")
    p.add_argument(
        "--last-event-id",
        type=int,
        default=-1,
        help="Start eventId: -1 = all events from beginning (default: -1)",
    )
    p.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds between polls (default: 2.0)",
    )
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Per-request timeout in seconds for each trajectory fetch (default: 10)",
    )
    p.add_argument(
        "--sse",
        action="store_true",
        help="Use legacy SSE streaming instead of polling",
    )

    # get-context-id
    p = sub.add_parser(
        "get-context-id",
        help="Retrieve the conversationId (contextId) for an existing app from its trajectory",
    )
    p.add_argument("--app-id", required=True, help="Application ID")
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    # conversation-history
    p = sub.add_parser(
        "conversation-history",
        help="Show human-readable conversation history for an app",
    )
    p.add_argument("--app-id", required=True, help="Application ID")
    p.add_argument(
        "--full",
        action="store_true",
        help="Show full content instead of truncated summaries (default: truncate at 200 chars)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only show the last N conversation turns",
    )
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    # fetch-trajectory  (single non-SSE fetch, no polling loop)
    p = sub.add_parser(
        "fetch-trajectory",
        help="Fetch one batch of trajectory events without polling (stream=false)",
    )
    p.add_argument("--app-id", required=True, help="Application ID")
    p.add_argument(
        "--last-event-id",
        type=int,
        default=-1,
        help="Fetch events after this eventId; -1 = all (default: -1)",
    )
    p.add_argument(
        "--fetch-timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    # publish
    p = sub.add_parser("publish", help="Publish an app")
    p.add_argument("--app-id", required=True, help="Application ID to publish")
    p.add_argument("--env", default="PRODUCE", help="Target environment (default: PRODUCE)")
    p.add_argument(
        "--wait",
        action="store_true",
        help="Poll publish status until SUCCESS or FAILED",
    )

    # publish-status
    p = sub.add_parser("publish-status", help="Get publish status by release ID")
    p.add_argument("--release-id", required=True, help="Release record ID from publish command")

    return parser


def main():
    """Parse CLI arguments and dispatch to the appropriate API function."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.api_key:
        print(
            "Error: API key required. Pass --api-key or set MEDO_API_KEY env var.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        if args.command == "list-apps":
            result = list_apps(
                args.base_url, args.api_key, args.name, args.page, args.size,
                brief=args.brief,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "app-detail":
            result = get_app_detail(args.base_url, args.api_key, args.app_id)
            if not args.no_context:
                try:
                    context_id = get_context_id(args.base_url, args.api_key, args.app_id)
                    if context_id:
                        result.setdefault("data", {})["conversationId"] = context_id
                except Exception:
                    pass  # non-fatal: app may have no conversation history yet
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "chat":
            if args.no_stream:
                result = chat_no_stream(
                    args.base_url, args.api_key, args.text,
                    args.context_id, args.app_id,
                    args.query_mode, args.input_field_type,
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                chat_stream(
                    args.base_url, args.api_key, args.text,
                    args.context_id, args.app_id,
                    args.query_mode, args.input_field_type,
                    prompt_generate=args.prompt_generate,
                    poll_interval=args.poll_interval,
                    fetch_timeout=args.fetch_timeout,
                )

        elif args.command == "generate-app":
            generate_app_confirmation(
                args.base_url, args.api_key,
                context_id=args.context_id,
                app_id=args.app_id,
                query_mode=args.query_mode,
                watch=args.watch,
                poll_interval=args.poll_interval,
                fetch_timeout=args.fetch_timeout,
            )

        elif args.command == "trajectory":
            if args.sse:
                stream_trajectory(
                    args.base_url, args.api_key, args.app_id, args.last_event_id,
                )
            else:
                poll_trajectory(
                    args.base_url, args.api_key, args.app_id,
                    last_event_id=args.last_event_id,
                    poll_interval=args.poll_interval,
                    fetch_timeout=args.fetch_timeout,
                )

        elif args.command == "get-context-id":
            context_id = get_context_id(
                args.base_url, args.api_key, args.app_id,
                fetch_timeout=args.fetch_timeout,
            )
            if context_id:
                print(json.dumps({"appId": args.app_id, "conversationId": context_id}, ensure_ascii=False))
            else:
                print(
                    f"Error: Could not find conversationId for app {args.app_id}. "
                    "The app may have no conversation history.",
                    file=sys.stderr,
                )
                sys.exit(1)

        elif args.command == "conversation-history":
            history = get_conversation_history(
                args.base_url, args.api_key, args.app_id,
                full=args.full,
                limit=args.limit,
                fetch_timeout=args.fetch_timeout,
            )
            for entry in history:
                print(json.dumps(entry, ensure_ascii=False))

        elif args.command == "fetch-trajectory":
            events, max_event_id, is_terminal = fetch_trajectory_once(
                args.base_url, args.api_key, args.app_id, args.last_event_id,
                timeout=args.fetch_timeout,
            )
            for event in events:
                print(json.dumps(event, ensure_ascii=False))
            print(
                json.dumps({"maxEventId": max_event_id, "isTerminal": is_terminal}, ensure_ascii=False),
                file=sys.stderr,
            )

        elif args.command == "publish":
            if args.wait:
                result = publish_and_wait(
                    args.base_url, args.api_key, args.app_id, args.env,
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                result = publish_app(
                    args.base_url, args.api_key, args.app_id, args.env,
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "publish-status":
            result = get_publish_status(
                args.base_url, args.api_key, args.release_id,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
