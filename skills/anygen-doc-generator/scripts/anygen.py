#!/usr/bin/env python3

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from auth import load_config, save_config, get_api_key, CONFIG_FILE, ENV_API_KEY
from io import BytesIO
from fileutil import read_file_bytes, read_json, write_json, write_bytes

try:
    import requests
except ImportError:
    print("[ERROR] requests library not found. Install with: pip3 install requests")
    sys.exit(1)


API_BASE = "https://www.anygen.io"
POLL_INTERVAL = 3  # seconds
MAX_POLL_TIME = 1200  # 20 minutes
OPENCLAW_WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILL_NAME = "doc-generator"



def log_info(msg):
    print(f"[INFO] {msg}")


def log_success(msg):
    print(f"[SUCCESS] {msg}")


def log_error(msg):
    print(f"[ERROR] {msg}")


def log_progress(status, progress):
    print(f"[PROGRESS] Status: {status}, Progress: {progress}%")


def format_timestamp(ts):
    """Convert Unix timestamp to readable datetime."""
    if not ts:
        return "N/A"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def log_request_id(response):
    request_id = response.headers.get("x-request-id", "")
    if request_id:
        print(f"x-request-id: {request_id}")


def parse_headers(header_list):
    """Parse header list from command line into dict."""
    if not header_list:
        return None
    headers = {}
    for h in header_list:
        if ":" in h:
            key, value = h.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers if headers else None


def make_auth_token(api_key):
    """Build Bearer auth token from API key."""
    return api_key if api_key.startswith("Bearer ") else f"Bearer {api_key}"



# ============ Upload Command ============

def upload_file(api_key, file_path, extra_headers=None):
    """Upload a file via multipart/form-data, returns file_token."""
    try:
        filename, content, size = read_file_bytes(file_path)
    except ValueError as e:
        log_error(str(e))
        return None

    auth_token = make_auth_token(api_key)
    log_info(f"Uploading file: {filename} ({size} bytes)")

    headers = {"Authorization": auth_token}
    if extra_headers:
        headers.update(extra_headers)

    try:
        files = {"file": (filename, BytesIO(content))}
        data = {"filename": filename}
        response = requests.post(
            f"{API_BASE}/v1/openapi/files/upload",
            files=files,
            data=data,
            headers=headers,
            timeout=60,
            allow_redirects=False,
        )

        log_request_id(response)
        log_info(f"Response status: {response.status_code}")
        if response.status_code != 200:
            log_error(f"HTTP error: {response.status_code}")
            log_error(f"Response: {response.text[:500]}")
            return None

        result = response.json()
    except requests.RequestException as e:
        log_error(f"Upload failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text[:500]}")
        return None

    if result.get("success"):
        file_token = result.get("file_token")
        log_success(f"File uploaded! file_token={file_token}")
        print(f"File Token: {file_token}")
        print(f"Filename: {result.get('filename')}")
        print(f"Size: {result.get('file_size')} bytes")
        return file_token
    else:
        log_error(f"Upload failed: {result.get('error', 'Unknown error')}")
        return None


# ============ Prepare Command ============

def prepare_task(api_key, messages, file_tokens=None, prepare_session_id=None,
                 base_suggested_task_params=None, extra_headers=None):
    """Call the prepare API for multi-turn requirement analysis."""
    auth_token = make_auth_token(api_key)

    body = {
        "auth_token": auth_token,
        "messages": messages,
    }
    if file_tokens:
        body["file_tokens"] = file_tokens
    if prepare_session_id:
        body["prepare_session_id"] = prepare_session_id
    if base_suggested_task_params:
        body["base_suggested_task_params"] = base_suggested_task_params

    # Add extra for tracking
    body["extra"] = {"create_from": "skill", "skill_name": SKILL_NAME}

    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    try:
        log_info("Calling prepare API...")
        response = requests.post(
            f"{API_BASE}/v1/openapi/tasks/prepare",
            json=body,
            headers=headers,
            timeout=120,
            allow_redirects=False,
        )

        log_request_id(response)
        if response.status_code != 200:
            log_error(f"HTTP error: {response.status_code}")
            log_error(f"Response: {response.text[:500]}")
            return None

        result = response.json()
    except requests.RequestException as e:
        log_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text[:500]}")
        return None

    if not result.get("success"):
        log_error(f"Prepare failed: {result.get('error', 'Unknown error')}")
        return None

    return result


def run_prepare_interactive(api_key, initial_message, file_tokens=None,
                             input_file=None, save_file=None, extra_headers=None):
    """Run prepare in interactive or single-shot mode."""
    messages = []
    loaded_file_tokens = set()
    prepare_session_id = None
    base_suggested_task_params = None

    # Load existing conversation from file
    if input_file:
        try:
            input_path = Path(input_file)
            save_path = Path(save_file) if save_file else None
            same_input_output = (
                save_path is not None and
                input_path.expanduser().resolve(strict=False) == save_path.expanduser().resolve(strict=False)
            )

            if not input_path.exists() and same_input_output:
                input_path.parent.mkdir(parents=True, exist_ok=True)
                write_json(input_path, {"messages": []})
                log_info(f"Input file not found, initialized a new conversation file: {input_path}")

            data = read_json(input_path)
            messages = data.get("messages", [])
            loaded_file_tokens = set(data.get("file_tokens", []))
            prepare_session_id = data.get("prepare_session_id")
            base_suggested_task_params = data.get("suggested_task_params")
            if loaded_file_tokens:
                file_tokens = (file_tokens or []) + list(loaded_file_tokens)
            log_info(f"Loaded conversation history: {len(messages)} messages")
        except (json.JSONDecodeError, IOError) as e:
            log_error(f"Failed to load conversation file: {e}")
            return None

    # Add user message with new file tokens embedded in content
    if initial_message:
        content = [{"type": "text", "text": initial_message}]
        for ft in (file_tokens or []):
            if ft not in loaded_file_tokens:
                content.append({"type": "file", "file_token": ft})
        messages.append({
            "role": "user",
            "content": content
        })

    if not messages:
        log_error("No messages. Use --message or --input to load conversation history")
        return None

    result = prepare_task(
        api_key=api_key,
        messages=messages,
        file_tokens=file_tokens,
        prepare_session_id=prepare_session_id,
        base_suggested_task_params=base_suggested_task_params,
        extra_headers=extra_headers,
    )
    if not result:
        return None

    # Display response
    response_msg = result.get("reply", "")
    status = result.get("status", "collecting")
    is_ready = status == "ready"
    suggested = result.get("suggested_task_params")
    updated_messages = result.get("messages", messages)
    prepare_session_id = result.get("prepare_session_id") or prepare_session_id
    base_suggested_task_params = suggested or base_suggested_task_params

    print()
    print("=" * 60)
    print(f"AnyGen: {response_msg}")
    print("=" * 60)
    print(f"Status: {status}")

    if is_ready and suggested:
        print()
        log_success("Requirement analysis complete! Suggested task params:")
        print(f"  Operation: {suggested.get('operation', 'N/A')}")
        print(f"  Prompt:")
        print(suggested.get('prompt', ''))
        if suggested.get("file_tokens"):
            print(f"  File Tokens: {', '.join(suggested['file_tokens'])}")
    else:
        print()
        log_info("Conversation in progress. Continue with the prepare command:")
        print("  Use --save to save conversation state, then --input to continue")

    # Save conversation state
    if save_file:
        save_data = {
            "messages": updated_messages,
            "file_tokens": file_tokens or [],
            "prepare_session_id": prepare_session_id,
            "status": status,
            "suggested_task_params": base_suggested_task_params,
        }
        try:
            write_json(save_file, save_data)
            log_info(f"Conversation saved to: {save_file}")
        except IOError as e:
            log_error(f"Failed to save conversation: {e}")

    return result


# ============ Create Task ============

def create_task(api_key, operation, prompt, export_format=None,
                file_tokens=None, extra_headers=None):
    """Create an async generation task."""
    log_info("Creating task...")

    auth_token = make_auth_token(api_key)

    # Build request body
    body = {
        "auth_token": auth_token,
        "operation": operation,
        "prompt": prompt
    }

    if export_format:
        body["export_format"] = export_format

    # File tokens from upload API
    if file_tokens:
        body["file_tokens"] = file_tokens
        log_info(f"Added {len(file_tokens)} file token(s)")

    # Add extra for tracking
    body["extra"] = {"create_from": "skill", "skill_name": SKILL_NAME}

    # Build headers
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    # Send request
    try:
        log_info(f"Request URL: {API_BASE}/v1/openapi/tasks")
        response = requests.post(
            f"{API_BASE}/v1/openapi/tasks",
            json=body,
            headers=headers,
            timeout=30,
            allow_redirects=False,
        )
        log_request_id(response)
        log_info(f"Response status: {response.status_code}")
        log_info(f"Response body: {response.text[:500] if response.text else 'Empty'}")
        if response.status_code != 200:
            log_error(f"HTTP error: {response.status_code}")
            return None
        result = response.json()
    except requests.RequestException as e:
        log_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text[:500] if response.text else 'Empty'}")
        return None

    if result.get("success"):
        task_id = result.get("task_id")
        log_success("Task created successfully!")
        print(f"Task ID: {task_id}")
        if result.get("task_url"):
            print(f"Task URL: {result['task_url']}")
        return task_id
    else:
        log_error(f"Task creation failed: {result.get('error', 'Unknown error')}")
        return None


def query_task(api_key, task_id, extra_headers=None):
    """Query task status."""
    auth_token = make_auth_token(api_key)

    headers = {"Authorization": auth_token}
    if extra_headers:
        headers.update(extra_headers)

    try:
        response = requests.get(
            f"{API_BASE}/v1/openapi/tasks/{task_id}",
            headers=headers,
            timeout=30,
            allow_redirects=False,
        )
        log_request_id(response)
        return response.json()
    except requests.RequestException as e:
        log_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text}")
        return None


def _download_to_local(file_url, file_name, output_dir):
    """Download file from URL to local directory. Returns local file path or None."""
    if not file_url:
        return None

    log_info("Downloading file...")

    try:
        response = requests.get(file_url, timeout=120, allow_redirects=False)
        response.raise_for_status()
    except requests.RequestException as e:
        log_error(f"Download failed: {e}")
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / (file_name or "output")
    # Avoid overwriting existing files from other tasks
    if file_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while file_path.exists():
            file_path = output_path / f"{stem}_{counter}{suffix}"
            counter += 1
    write_bytes(file_path, response.content)

    log_success(f"File saved: {file_path}")
    return str(file_path)


def poll_task(api_key, task_id, max_time=MAX_POLL_TIME, extra_headers=None, output_dir=None):
    """Poll task until completion or failure. Auto-downloads file if output_dir is provided."""
    log_info(f"Polling task status: {task_id}")

    start_time = time.time()
    last_progress = -1
    last_heartbeat = start_time

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_time:
            log_error(f"Polling timeout ({max_time}s)")
            return None

        task = query_task(api_key, task_id, extra_headers)
        if not task:
            time.sleep(POLL_INTERVAL)
            continue

        status = task.get("status")
        progress = task.get("progress", 0)

        if progress != last_progress:
            log_progress(status, progress)
            last_progress = progress

        now = time.time()
        if now - last_heartbeat >= 30:
            ts = datetime.now().strftime("%H:%M:%S")
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            print(f"[HEARTBEAT] {ts} | elapsed {mins}m{secs:02d}s | status: {status} | progress: {progress}%", flush=True)
            last_heartbeat = now

        if status == "completed":
            output = task.get("output", {})
            task_url = output.get("task_url", f"{API_BASE}/task/{task_id}")
            log_success("Task completed!")
            if output.get("slide_count"):
                print(f"Slide count: {output.get('slide_count')}")
            if output.get("word_count"):
                print(f"Word count: {output.get('word_count')}")

            # Auto-download file only if output_dir is specified
            file_url = output.get("file_url")
            if file_url and output_dir:
                local_path = _download_to_local(file_url, output.get("file_name"), output_dir)
                if local_path:
                    print(f"[RESULT] Local file: {local_path}")

            if output.get("thumbnail_url"):
                print(f"[RESULT] Thumbnail URL: {output['thumbnail_url']}")

            print(f"[RESULT] Task URL: {task_url}")
            return task

        elif status == "failed":
            log_error("Task failed!")
            print(f"Error: {task.get('error', 'Unknown error')}")
            return task

        time.sleep(POLL_INTERVAL)


def download_file(api_key, task_id, output_dir, extra_headers=None):
    """Download the generated file. Returns local file path or False."""
    task = query_task(api_key, task_id, extra_headers)
    if not task:
        return False

    if task.get("status") != "completed":
        log_error(f"Task not completed, current status: {task.get('status')}")
        return False

    output = task.get("output", {})
    file_url = output.get("file_url")
    file_name = output.get("file_name")
    task_url = output.get("task_url", f"{API_BASE}/task/{task_id}")

    if not file_url:
        log_error("Unable to get download URL")
        return False

    local_path = _download_to_local(file_url, file_name, output_dir)
    if local_path:
        print(f"[RESULT] Local file: {local_path}")
        if output.get("thumbnail_url"):
            print(f"[RESULT] Thumbnail URL: {output['thumbnail_url']}")
        print(f"[RESULT] Task URL: {task_url}")
        return local_path
    return False


def download_thumbnail(api_key, task_id, output_dir, extra_headers=None):
    """Download only the thumbnail image. Returns local file path or False."""
    task = query_task(api_key, task_id, extra_headers)
    if not task:
        return False

    if task.get("status") != "completed":
        log_error(f"Task not completed, current status: {task.get('status')}")
        return False

    output = task.get("output", {})
    thumbnail_url = output.get("thumbnail_url")
    if not thumbnail_url:
        log_error("No thumbnail available for this task")
        return False

    local_path = _download_to_local(thumbnail_url, f"thumbnail_{task_id}.png", output_dir)
    if local_path:
        print(f"[RESULT] Thumbnail file: {local_path}")
        return local_path
    return False


# ============ Multi-turn Conversation ============

def send_message(api_key, task_id, content, files=None, extra_headers=None):
    """Send a message to an existing task. Returns immediately."""
    auth_token = make_auth_token(api_key)

    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    body = {"auth_token": auth_token, "content": content}
    if files:
        body["files"] = files

    # Add extra for tracking
    body["extra"] = {"create_from": "skill", "skill_name": SKILL_NAME}

    try:
        log_info(f"Sending message to task: {task_id}")
        response = requests.post(
            f"{API_BASE}/v1/openapi/tasks/{task_id}/messages",
            json=body,
            headers=headers,
            timeout=30,
            allow_redirects=False,
        )
        log_request_id(response)
        if response.status_code != 200:
            log_error(f"HTTP error: {response.status_code}")
            log_error(f"Response: {response.text[:500]}")
            return None

        result = response.json()
    except requests.RequestException as e:
        log_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text[:500]}")
        return None

    msg = result.get("message", {})
    status = result.get("status", "unknown")
    log_success(f"Message sent! id={msg.get('id')}, status={status}")
    print(f"Message ID: {msg.get('id')}")
    print(f"Status: {status}")
    return result


def get_messages(api_key, task_id, limit=10, cursor=None, extra_headers=None):
    """Get messages for a task. Supports polling and pagination."""
    auth_token = make_auth_token(api_key)

    headers = {"Authorization": auth_token}
    if extra_headers:
        headers.update(extra_headers)

    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor

    try:
        response = requests.get(
            f"{API_BASE}/v1/openapi/tasks/{task_id}/messages",
            headers=headers,
            params=params,
            timeout=30,
            allow_redirects=False,
        )
        log_request_id(response)
        if response.status_code != 200:
            log_error(f"HTTP error: {response.status_code}")
            log_error(f"Response: {response.text[:500]}")
            return None

        result = response.json()
    except requests.RequestException as e:
        log_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        log_error(f"Response parse failed: {response.text[:500]}")
        return None

    return result


def poll_messages(api_key, task_id, since_message_id, limit=10,
                  max_time=MAX_POLL_TIME, extra_headers=None):
    """Poll messages until an assistant reply is completed after since_message_id."""
    log_info(f"Waiting for AI reply on task: {task_id}")

    start_time = time.time()
    last_heartbeat = start_time

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_time:
            log_error(f"Polling timeout ({max_time}s)")
            return None

        result = get_messages(api_key, task_id, limit=limit, extra_headers=extra_headers)
        if not result:
            time.sleep(POLL_INTERVAL)
            continue

        messages = result.get("messages", [])
        task_snapshot = result.get("task_snapshot", {})

        # Find the latest assistant message newer than since_message_id
        for msg in messages:
            if (msg.get("role") == "assistant"
                    and msg.get("id", 0) > since_message_id
                    and msg.get("status") == "completed"):
                log_success("AI reply received!")
                print(f"[REPLY] {msg.get('content', '')}")
                if task_snapshot:
                    snap_status = task_snapshot.get("status", "")
                    can_export = task_snapshot.get("can_export", False)
                    print(f"[SNAPSHOT] status={snap_status}, can_export={can_export}")
                return result

        now = time.time()
        if now - last_heartbeat >= 30:
            ts = datetime.now().strftime("%H:%M:%S")
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            snap_status = task_snapshot.get("status", "unknown")
            print(f"[HEARTBEAT] {ts} | elapsed {mins}m{secs:02d}s | task_status: {snap_status}", flush=True)
            last_heartbeat = now

        time.sleep(POLL_INTERVAL)


def run_full_workflow(api_key, operation, prompt, output_dir, extra_headers=None,
                      file_tokens=None, export_format=None):
    """Run the full workflow: create -> poll -> download."""
    task_id = create_task(api_key, operation, prompt, extra_headers=extra_headers,
                          file_tokens=file_tokens, export_format=export_format)
    if not task_id:
        return False

    task = poll_task(api_key, task_id, extra_headers=extra_headers)
    if not task or task.get("status") != "completed":
        return False

    if output_dir:
        return download_file(api_key, task_id, output_dir, extra_headers=extra_headers)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="AnyGen OpenAPI Client",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    def add_common_args(p):
        p.add_argument("--api-key", "-k",
                        help="AnyGen API Key (sk-xxx). Also: env ANYGEN_API_KEY or config file")
        p.add_argument("--header", "-H", action="append", dest="headers",
                        help="Extra HTTP header (format: 'Key:Value')")

    # ---- upload command ----
    upload_parser = subparsers.add_parser("upload", help="Upload a file and get file_token")
    add_common_args(upload_parser)
    upload_parser.add_argument("--file", required=True, help="File path to upload")

    # ---- prepare command ----
    prepare_parser = subparsers.add_parser("prepare",
        help="Multi-turn requirement analysis before creating a task")
    add_common_args(prepare_parser)
    prepare_parser.add_argument("--message", "-m", help="User message text")
    prepare_parser.add_argument("--file-token", action="append", dest="file_tokens",
                                 help="File token (from upload). Can be repeated")
    prepare_parser.add_argument("--input", dest="input_file",
                                 help="Load conversation history from JSON file")
    prepare_parser.add_argument("--save", dest="save_file",
                                 help="Save conversation state to JSON file")
    prepare_parser.add_argument("--stdin", action="store_true",
                                 help="Read message from stdin")

    # ---- create command ----
    create_parser = subparsers.add_parser("create", help="Create a generation task")
    add_common_args(create_parser)
    create_parser.add_argument("--operation", "-o", required=True,
                               choices=["slide", "doc", "smart_draw", "storybook", "data_analysis", "website", "finance", "deep_research", "ai_designer"],
                               help="Operation type")
    create_parser.add_argument("--prompt", "-p", required=True, help="Content prompt")
    create_parser.add_argument("--export-format", "-f", help="Export format (smart_draw: drawio/excalidraw)")
    create_parser.add_argument("--file-token", action="append", dest="file_tokens",
                               help="File token from upload (can be repeated)")

    # ---- poll command ----
    poll_parser = subparsers.add_parser("poll", help="Poll task status until completion and auto-download")
    add_common_args(poll_parser)
    poll_parser.add_argument("--task-id", required=True, help="Task ID to poll")
    poll_parser.add_argument("--output", help="Output directory for auto-download (omit to skip download)")

    # ---- download command ----
    download_parser = subparsers.add_parser("download", help="Download generated file")
    add_common_args(download_parser)
    download_parser.add_argument("--task-id", required=True, help="Task ID")
    download_parser.add_argument("--output", required=True, help="Output directory")

    # ---- thumbnail command ----
    thumbnail_parser = subparsers.add_parser("thumbnail", help="Download thumbnail image only")
    add_common_args(thumbnail_parser)
    thumbnail_parser.add_argument("--task-id", required=True, help="Task ID")
    thumbnail_parser.add_argument("--output", required=True, help="Output directory")


    # ---- send-message command ----
    send_msg_parser = subparsers.add_parser("send-message",
        help="Send a message to an existing task (multi-turn conversation)")
    add_common_args(send_msg_parser)
    send_msg_parser.add_argument("--task-id", required=True, help="Task ID")
    send_msg_parser.add_argument("--message", "-m", required=True, help="Message content")
    send_msg_parser.add_argument("--file", action="append", dest="files",
                                  help="File path to upload and attach (can be repeated)")
    send_msg_parser.add_argument("--file-token", action="append", dest="file_tokens",
                                  help="File token from upload (can be repeated)")

    # ---- get-messages command ----
    get_msgs_parser = subparsers.add_parser("get-messages",
        help="Get messages for a task (supports polling and pagination)")
    add_common_args(get_msgs_parser)
    get_msgs_parser.add_argument("--task-id", required=True, help="Task ID")
    get_msgs_parser.add_argument("--limit", type=int, default=10,
                                  help="Number of messages to return (default: 10, max: 100)")
    get_msgs_parser.add_argument("--cursor", help="Pagination cursor")
    get_msgs_parser.add_argument("--wait", action="store_true",
                                  help="Block and poll until a new assistant reply is completed")
    get_msgs_parser.add_argument("--since-id", type=int, default=0,
                                  help="Wait for assistant reply with id greater than this (used with --wait)")

    # ---- run command ----
    run_parser = subparsers.add_parser("run", help="Full workflow: create -> poll -> download")
    add_common_args(run_parser)
    run_parser.add_argument("--operation", "-o", required=True,
                           choices=["slide", "doc", "smart_draw", "storybook", "data_analysis", "website", "finance", "deep_research", "ai_designer"],
                           help="Operation type")
    run_parser.add_argument("--prompt", "-p", required=True, help="Content prompt")
    run_parser.add_argument("--export-format", "-f", help="Export format (smart_draw: drawio/excalidraw)")
    run_parser.add_argument("--file-token", action="append", dest="file_tokens",
                           help="File token from upload (can be repeated)")
    run_parser.add_argument("--output", help="Output directory (optional)")

    # ---- config command ----
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_action", help="Config actions")

    config_set_parser = config_subparsers.add_parser("set", help="Set a config value")
    config_set_parser.add_argument("key", choices=["api_key", "default_language", "suite_recommended"], help="Config key")
    config_set_parser.add_argument("value", help="Config value")

    config_get_parser = config_subparsers.add_parser("get", help="Get a config value")
    config_get_parser.add_argument("key", nargs="?", help="Config key (omit to show all)")

    config_delete_parser = config_subparsers.add_parser("delete", help="Delete a config value")
    config_delete_parser.add_argument("key", help="Config key to delete")

    config_subparsers.add_parser("path", help="Show config file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle config command (no API key needed)
    if args.command == "config":
        if not args.config_action:
            config_parser.print_help()
            sys.exit(1)

        if args.config_action == "path":
            print(f"Config file: {CONFIG_FILE}")
            sys.exit(0)

        elif args.config_action == "set":
            config = load_config()
            config[args.key] = args.value
            save_config(config)
            # Mask API key in output
            display_value = args.value[:10] + "..." if args.key == "api_key" and len(args.value) > 10 else args.value
            log_success(f"Set {args.key} = {display_value}")
            sys.exit(0)

        elif args.config_action == "get":
            config = load_config()
            if args.key:
                value = config.get(args.key)
                if value:
                    # Mask API key
                    if args.key == "api_key" and len(value) > 10:
                        value = value[:10] + "..."
                    print(f"{args.key} = {value}")
                else:
                    print(f"{args.key} is not set")
            else:
                if config:
                    for k, v in config.items():
                        # Mask API key
                        if k == "api_key" and len(v) > 10:
                            v = v[:10] + "..."
                        print(f"{k} = {v}")
                else:
                    print("No config set")
            sys.exit(0)

        elif args.config_action == "delete":
            config = load_config()
            if args.key in config:
                del config[args.key]
                save_config(config)
                log_success(f"Deleted {args.key}")
            else:
                log_error(f"{args.key} not found in config")
            sys.exit(0)

    # Resolve API key for all other commands
    api_key = get_api_key(getattr(args, 'api_key', None))
    if not api_key:
        log_error("API Key not found. Provide one via:")
        print("  1. Command line: --api-key sk-xxx")
        print(f"  2. Environment variable: export {ENV_API_KEY}=sk-xxx")
        print(f"  3. Config file: python3 anygen.py config set api_key sk-xxx")
        sys.exit(1)

    extra_headers = parse_headers(args.headers) if hasattr(args, 'headers') else None

    if args.command == "upload":
        token = upload_file(api_key, args.file, extra_headers=extra_headers)
        sys.exit(0 if token else 1)

    elif args.command == "prepare":
        message = args.message
        if args.stdin:
            message = sys.stdin.read().strip()

        result = run_prepare_interactive(
            api_key=api_key,
            initial_message=message,
            file_tokens=args.file_tokens,
            input_file=args.input_file,
            save_file=args.save_file,
            extra_headers=extra_headers
        )
        sys.exit(0 if result else 1)

    elif args.command == "create":
        task_id = create_task(
            api_key=api_key,
            operation=args.operation,
            prompt=args.prompt,
            export_format=args.export_format,
            file_tokens=args.file_tokens,
            extra_headers=extra_headers,
        )
        sys.exit(0 if task_id else 1)

    elif args.command == "poll":
        output_dir = getattr(args, 'output', None)
        task = poll_task(api_key, args.task_id, extra_headers=extra_headers, output_dir=output_dir)
        if task and task.get("status") == "completed":
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.command == "download":
        success = download_file(api_key, args.task_id, args.output, extra_headers=extra_headers)
        sys.exit(0 if success else 1)

    elif args.command == "thumbnail":
        success = download_thumbnail(api_key, args.task_id, args.output, extra_headers=extra_headers)
        sys.exit(0 if success else 1)

    elif args.command == "send-message":
        # Upload files if provided and build file references
        files_payload = []
        if args.file_tokens:
            for ft in args.file_tokens:
                files_payload.append({"file_token": ft})
        if args.files:
            for file_path in args.files:
                log_info(f"Uploading file: {file_path}")
                token = upload_file(api_key, file_path, extra_headers=extra_headers)
                if token:
                    files_payload.append({"file_token": token})
                else:
                    log_error(f"File upload failed, skipping: {file_path}")

        result = send_message(
            api_key=api_key,
            task_id=args.task_id,
            content=args.message,
            files=files_payload if files_payload else None,
            extra_headers=extra_headers,
        )
        sys.exit(0 if result else 1)

    elif args.command == "get-messages":
        if args.wait:
            result = poll_messages(
                api_key=api_key,
                task_id=args.task_id,
                since_message_id=args.since_id,
                limit=args.limit,
                extra_headers=extra_headers,
            )
            sys.exit(0 if result else 1)
        else:
            result = get_messages(
                api_key=api_key,
                task_id=args.task_id,
                limit=args.limit,
                cursor=args.cursor,
                extra_headers=extra_headers,
            )
            if result:
                messages = result.get("messages", [])
                task_snapshot = result.get("task_snapshot", {})
                has_more = result.get("has_more", False)

                print(f"\n{'=' * 60}")
                print(f"Messages ({len(messages)}):")
                print(f"{'=' * 60}")
                for msg in messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    msg_id = msg.get("id", "?")
                    status = msg.get("status", "?")
                    print(f"  [{role}] (id={msg_id}, status={status}): {content[:200]}")

                if task_snapshot:
                    print(f"\nTask Snapshot:")
                    print(f"  status={task_snapshot.get('status')}")
                    print(f"  content_version={task_snapshot.get('content_version')}")
                    print(f"  can_export={task_snapshot.get('can_export')}")

                if has_more:
                    next_cursor = result.get("cursor", "")
                    print(f"\nMore messages available. Use --cursor {next_cursor}")

                sys.exit(0)
            else:
                sys.exit(1)

    elif args.command == "run":
        success = run_full_workflow(
            api_key=api_key,
            operation=args.operation,
            prompt=args.prompt,
            output_dir=args.output,
            extra_headers=extra_headers,
            file_tokens=args.file_tokens,
            export_format=args.export_format,
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
