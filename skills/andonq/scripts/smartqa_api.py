"""
SmartQA API client — Tencent Cloud Andon smart customer service.

This module provides:
- Question encoding (URL encode → base64)
- Session management (create/reuse sessions)
- SSE stream chat with parse
- CLI with argparse (dry-run support)

Independent from andon_api.py — different protocol (Web API + SSE vs TC3 signing).
"""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import random
import socket
import ssl
import string
import sys
import urllib.parse
import uuid

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

CHAT_HOST = "andon.cloud.tencent.com"
CHAT_PATH = "/online-service/api/agent/chat"
SESSION_HOST = "cloud.tencent.com"
SESSION_PATH = "/online-service/api/agent/create/session"

DEFAULT_MODEL = "D-v3"
DEFAULT_CLIENT = "offical-smarty-v2"
DEFAULT_FROM = "AndonQ"
DEFAULT_LANG = "zh"
DEFAULT_INPUT_TYPE = 1
DEFAULT_RETURN_MANUAL = True

ACTION = "SmartQA"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60


# ──────────────────────────────────────────────
# Unified response builders
# ──────────────────────────────────────────────

def make_success(action: str, data: dict) -> dict:
    return {
        "success": True,
        "action": action,
        "data": data,
    }


def make_error(action: str, code: str, message: str) -> dict:
    return {
        "success": False,
        "action": action,
        "error": {
            "code": code,
            "message": message,
        },
    }


# ──────────────────────────────────────────────
# Question encoding
# ──────────────────────────────────────────────

def encode_question(text: str) -> str:
    """Encode question: raw text → URL encode → base64."""
    url_encoded = urllib.parse.quote(text, safe="")
    return base64.b64encode(url_encoded.encode("utf-8")).decode("utf-8")


# ──────────────────────────────────────────────
# Session management
# ──────────────────────────────────────────────

def generate_session_id() -> str:
    """Generate a session ID with 'AndonQ-' prefix and 12-char random suffix."""
    chars = string.ascii_uppercase + string.digits
    return "AndonQ-" + "".join(random.choices(chars, k=12))


def build_chat_payload(
    encoded_question: str,
    session_id: str,
    agent_session_id: str,
) -> dict:
    """Build the chat request payload. Question must be pre-encoded."""
    if not encoded_question:
        raise ValueError("Question must not be empty")
    return {
        "sessionId": session_id,
        "agentSessionId": agent_session_id,
        "uin": "",
        "skey": "",
        "client": DEFAULT_CLIENT,
        "from": DEFAULT_FROM,
        "source": "",
        "question": encoded_question,
        "inputType": DEFAULT_INPUT_TYPE,
        "returnManual": DEFAULT_RETURN_MANUAL,
        "model": DEFAULT_MODEL,
        "lang": DEFAULT_LANG,
    }


def create_session(session_id: str) -> dict:
    """Create a new chat session. Returns unified response with agentSessionId."""
    body = json.dumps({"sessionId": session_id, "source": ""})
    try:
        conn = http.client.HTTPSConnection(
            SESSION_HOST, timeout=CONNECT_TIMEOUT,
        )
        conn.request(
            "POST",
            SESSION_PATH,
            body=body.encode("utf-8"),
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "Accept": "application/json, text/plain, */*",
            },
        )
        resp = conn.getresponse()
        raw = json.loads(resp.read().decode("utf-8"))
        conn.close()
    except (socket.timeout, socket.error, OSError) as e:
        return make_error(ACTION, "NetworkError", str(e))
    except json.JSONDecodeError as e:
        return make_error(ACTION, "ParseError", str(e))

    # Extract agentSessionId (API returns it as "sessionId" in data)
    data = raw.get("data") if isinstance(raw, dict) else None
    if data is None:
        return make_error(ACTION, "SessionCreateFailed",
                          f"Missing data in response: {raw}")

    # API returns "sessionId" in data, which is the agentSessionId for chat
    agent_session_id = data.get("agentSessionId") or data.get("sessionId")
    if not agent_session_id:
        return make_error(ACTION, "SessionCreateFailed",
                          f"Missing agentSessionId/sessionId in response: {raw}")

    return make_success(ACTION, {
        "sessionId": session_id,
        "agentSessionId": str(agent_session_id),
    })


# ──────────────────────────────────────────────
# SSE stream parsing
# ──────────────────────────────────────────────

def parse_sse_stream(lines) -> dict:
    """
    Parse SSE event lines and extract the assistant's answer + metadata.

    Args:
        lines: iterable of SSE text lines (strings)

    Returns:
        Unified response dict with answer, intention, recommendQuestions.
    """
    answer_parts = []
    intention = None
    recommend_questions = None
    smart_tool = None       # fallback from smart_tools_event
    collecting = False
    finished = False

    for line in lines:
        line = line.rstrip("\r\n") if isinstance(line, str) else line.decode("utf-8").rstrip("\r\n")

        if not line.startswith("data:"):
            continue

        json_str = line[5:].strip()
        if not json_str:
            continue

        try:
            event = json.loads(json_str)
        except json.JSONDecodeError:
            continue

        event_type = event.get("Type")
        if not event_type:
            continue

        if event_type == "CUSTOM" and event.get("Name") == "meta_data_event":
            value = event.get("Value", {})
            intention = value.get("Intention")
            recommend_questions = value.get("RecommendQuestions")

        elif event_type == "CUSTOM" and event.get("Name") == "smart_tools_event":
            # Product-specific queries return a tool reference instead of text
            value = event.get("Value", {})
            smart_tool = value

        elif event_type == "TEXT_MESSAGE_START" and event.get("Role") == "assistant":
            collecting = True

        elif event_type == "TEXT_MESSAGE_CONTENT" and event.get("Role") == "assistant":
            delta = event.get("Delta", {})
            content = delta.get("Content", "")
            if content:
                answer_parts.append(content)

        elif event_type == "TEXT_MESSAGE_END":
            collecting = False

        elif event_type == "RUN_FINISHED":
            finished = True
            break

    answer = "".join(answer_parts)

    # Fallback: if no text answer but got smart_tools_event, use its answer
    if not answer and smart_tool:
        answer = smart_tool.get("answer", "")

    if not answer:
        return make_error(ACTION, "EmptyResponse", "No assistant content in SSE stream")

    data = {
        "answer": answer,
        "intention": intention,
        "recommendQuestions": recommend_questions,
    }

    if smart_tool:
        data["smartTool"] = smart_tool

    if not finished:
        data["partial"] = True

    return make_success(ACTION, data)


# ──────────────────────────────────────────────
# HTTP transport — send chat request
# ──────────────────────────────────────────────

def send_chat(payload: dict, verbose: bool = False) -> dict:
    """
    Send chat request and parse SSE stream response.

    Args:
        payload: chat request body dict

    Returns:
        Unified response dict with answer.
    """
    body = json.dumps(payload)
    try:
        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(
            CHAT_HOST, timeout=CONNECT_TIMEOUT, context=context,
        )
        conn.request(
            "POST",
            CHAT_PATH,
            body=body.encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "*/*, text/event-stream",
                "Origin": "https://cloud.tencent.com",
                "Referer": "https://cloud.tencent.com/",
                "Request-Id": str(uuid.uuid4()),
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            },
        )
        resp = conn.getresponse()
    except socket.timeout:
        return make_error(ACTION, "ConnectionTimeout", "Connection timed out")
    except (socket.error, OSError) as e:
        return make_error(ACTION, "NetworkError", str(e))

    if resp.status != 200:
        try:
            err_body = resp.read().decode("utf-8")
        except Exception:
            err_body = ""
        return make_error(ACTION, "HttpError", f"HTTP {resp.status}: {err_body}")

    # Read SSE stream — read full body then split into lines.
    # (readline() can fail on chunked-transfer SSE responses)
    try:
        raw_body = resp.read().decode("utf-8")
    except socket.timeout:
        raw_body = ""
    except Exception as e:
        return make_error(ACTION, "ReadTimeout", str(e))
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if verbose:
        print(f"\n[DEBUG] Raw SSE body ({len(raw_body)} chars):")
        print(raw_body[:3000])
        if len(raw_body) > 3000:
            print(f"... ({len(raw_body) - 3000} chars truncated)")
        print("[DEBUG] End of raw body")

    lines = raw_body.splitlines()
    return parse_sse_stream(lines)


# ──────────────────────────────────────────────
# High-level API — smart_qa
# ──────────────────────────────────────────────

def smart_qa(
    question: str,
    session_id: str = None,
    agent_session_id: str = None,
    verbose: bool = False,
) -> dict:
    """
    High-level smart Q&A: auto-create session if needed, ask question, return answer.

    Args:
        question: raw question text
        session_id: reuse existing session (optional)
        agent_session_id: reuse existing agent session (optional)

    Returns:
        Unified response dict.
    """
    if not question or not question.strip():
        return make_error(ACTION, "InvalidParameter", "Question must not be empty")

    # Create session if not provided
    if not session_id:
        session_id = generate_session_id()

    if not agent_session_id:
        session_result = create_session(session_id)
        if not session_result["success"]:
            return session_result
        agent_session_id = session_result["data"]["agentSessionId"]

    # Encode and build payload
    encoded_q = encode_question(question.strip())
    payload = build_chat_payload(encoded_q, session_id, agent_session_id)

    # Send and parse
    result = send_chat(payload, verbose=verbose)

    # Inject session info into successful response
    if result["success"]:
        result["data"]["sessionId"] = session_id
        result["data"]["agentSessionId"] = agent_session_id

    return result


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SmartQA CLI — Tencent Cloud Andon smart customer service",
    )
    parser.add_argument(
        "-q", "--question",
        required=True,
        help="Question to ask (plain text)",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Reuse an existing session ID",
    )
    parser.add_argument(
        "--agent-session-id",
        default=None,
        help="Reuse an existing agent session ID",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose request details",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Print request summary without sending",
    )
    return parser


def main(argv=None):
    """CLI entry point."""
    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    question = args.question.strip()
    if not question:
        print(json.dumps(make_error(ACTION, "InvalidParameter", "Question is empty"), indent=2))
        sys.exit(1)

    session_id = args.session_id or generate_session_id()
    encoded_q = encode_question(question)

    if args.verbose or args.dry_run:
        print("=" * 60)
        if args.dry_run:
            print("[DRY RUN] ", end="")
        print("Request Summary")
        print("=" * 60)
        print(f"Action:   SmartQA")
        print(f"Chat URL: https://{CHAT_HOST}{CHAT_PATH}")
        print(f"Session:  {session_id}")
        print(f"Question: {question}")
        print(f"Encoded:  {encoded_q}")
        print(f"Model:    {DEFAULT_MODEL}")

    if args.dry_run:
        payload = build_chat_payload(encoded_q, session_id, args.agent_session_id or "<pending>")
        print(f"\nPayload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("=" * 60)
        print("[DRY RUN] No HTTP request sent.")
        sys.exit(0)

    result = smart_qa(
        question,
        session_id=args.session_id,
        agent_session_id=args.agent_session_id,
        verbose=args.verbose,
    )

    if args.verbose:
        print(f"\nResponse:")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
