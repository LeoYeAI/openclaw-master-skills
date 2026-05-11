#!/usr/bin/env python3
"""
Run OpenAI Codex CLI in the background and notify the originating OpenClaw session when done.
Zero OpenClaw tokens while Codex works.

Usage:
  nohup python3 run-task.py -t "Build X" -p ~/projects/x -s "SESSION_KEY" > /tmp/codex-run.log 2>&1 &

Resume previous session:
  nohup python3 run-task.py -t "Continue with Y" -p ~/projects/x -s "SESSION_KEY" --resume <session-id> > /tmp/codex-run.log 2>&1 &

Features:
  - Session resumption: continue previous Codex conversations
  - Session registry: automatic tracking in ~/.openclaw/codex_sessions.json
  - Session labels: human-readable names for easier tracking
  - Heartbeat pings every 60s to the originating channel
  - Timeout with graceful kill + notification
  - PID file for tracking running tasks
  - Crash-safe: notify on any failure
  - Stale process cleanup
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

import requests
import uuid
import hashlib
from typing import Optional

# Import session registry
try:
    from session_registry import register_session, update_session
except ImportError:
    # Fallback if not in same directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "session_registry",
        Path(__file__).parent / "session_registry.py"
    )
    session_registry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(session_registry)
    register_session = session_registry.register_session
    update_session = session_registry.update_session

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
GW_URL = "http://localhost:18789"
# PID files stored next to this script (in pids/ subdirectory)
PID_DIR = Path(__file__).parent / "pids"
DEFAULT_TIMEOUT = 7200  # 2 hours


def fmt_duration(seconds: int) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    m = seconds // 60
    return f"{m}min"


def get_token():
    return json.loads(CONFIG_PATH.read_text())["gateway"]["auth"]["token"]


BG_PREFIX = "📡 "  # Visual marker for background (non-agent-waking) messages

# Notification overrides
# If not set, channel/target are auto-detected from session key and session metadata.
NOTIFY_CHANNEL_OVERRIDE = None
NOTIFY_TARGET_OVERRIDE = None


def extract_group_jid(session_key: str) -> Optional[str]:
    """Extract WhatsApp group JID from session key (e.g. agent:main:whatsapp:group:123@g.us)."""
    if not session_key:
        return None
    for part in session_key.split(":"):
        if "@g.us" in part:
            return part
    return None


def extract_thread_id(session_key: str) -> Optional[str]:
    """Extract Telegram thread ID from session key (e.g. agent:main:main:thread:369520)."""
    if not session_key:
        return None
    parts = session_key.split(":")
    for i, part in enumerate(parts):
        if part == "thread" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def detect_channel(session_key: str):
    """Return (channel, target) for notifications based on session key or CLI overrides."""
    # Explicit internally-resolved overrides take priority
    if NOTIFY_CHANNEL_OVERRIDE and NOTIFY_TARGET_OVERRIDE:
        return NOTIFY_CHANNEL_OVERRIDE, NOTIFY_TARGET_OVERRIDE
    # WhatsApp: extract JID from session key
    jid = extract_group_jid(session_key or "")
    if jid:
        return "whatsapp", jid
    # Default: no notification target known
    return None, None


def build_whatsapp_group_session_key(base_session_key: str, group_jid: str) -> Optional[str]:
    """Build whatsapp group session key preserving agent id from base session.

    Example:
      base:  agent:iris:main
      group: 120...@g.us
      ->     agent:iris:whatsapp:group:120...@g.us
    """
    if not base_session_key or not group_jid:
        return None
    parts = base_session_key.split(":")
    if len(parts) < 2:
        return None
    if parts[0] != "agent":
        return None
    agent_id = parts[1]
    return f"agent:{agent_id}:whatsapp:group:{group_jid}"


def _invoke_tool(token: str, tool: str, args: dict, timeout: int = 20) -> Optional[dict]:
    """Invoke OpenClaw tool via gateway; return parsed JSON or None."""
    try:
        resp = requests.post(
            f"{GW_URL}/tools/invoke",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"tool": tool, "args": args},
            timeout=timeout,
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def resolve_session_meta(token: str, session_key: str) -> Optional[dict]:
    """Resolve session metadata from sessions_list by exact session key.

    Returns: {"sessionId": str|None, "telegramTarget": str|None, "key": str}
    """
    if not token or not session_key:
        return None

    data = _invoke_tool(token, "sessions_list", {"limit": 200})
    if not data:
        return None

    try:
        # Tool responses are wrapped as text JSON in result.content[0].text
        txt = data.get("result", {}).get("content", [{}])[0].get("text", "")
        payload = json.loads(txt) if txt else {}
        for s in payload.get("sessions", []):
            if s.get("key") == session_key:
                dc = s.get("deliveryContext", {}) or {}
                to = dc.get("to") or s.get("displayName")
                tg_target = None
                if isinstance(to, str) and to.startswith("telegram:"):
                    tg_target = to.split(":", 1)[1]
                return {
                    "sessionId": s.get("sessionId"),
                    "telegramTarget": tg_target,
                    "key": s.get("key"),
                }
    except Exception:
        return None

    return None


def has_recent_thread_session(token: str, telegram_target: str, max_age_hours: int = 24) -> bool:
    """Return True if there is a recent thread session for this Telegram target.

    Used to prevent accidental non-thread launches when the user is actively using thread mode.
    Checks both sessions_list and local topic session files.
    """
    if not token or not telegram_target:
        return False
    data = _invoke_tool(token, "sessions_list", {"limit": 300})
    if not data:
        return False
    try:
        txt = data.get("result", {}).get("content", [{}])[0].get("text", "")
        payload = json.loads(txt) if txt else {}
        now_ms = int(time.time() * 1000)
        max_age_ms = max_age_hours * 3600 * 1000
        for s in payload.get("sessions", []):
            key = s.get("key", "")
            if ":thread:" not in key:
                continue
            dc = s.get("deliveryContext", {}) or {}
            to = dc.get("to", "")
            if to == f"telegram:{telegram_target}":
                updated = int(s.get("updatedAt", 0) or 0)
                if updated and (now_ms - updated) <= max_age_ms:
                    return True
    except Exception:
        pass

    # Fallback: local topic session files (handles cases where sessions_list only shows current session)
    try:
        base = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
        if base.exists():
            now = time.time()
            max_age_sec = max_age_hours * 3600
            files = sorted(base.glob("*-topic-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            for p in files[:200]:
                if (now - p.stat().st_mtime) > max_age_sec:
                    continue
                with p.open("r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i > 120:
                            break
                        obj = json.loads(line)
                        if obj.get("type") != "message":
                            continue
                        msg = (obj.get("message") or {})
                        if msg.get("role") != "user":
                            continue
                        for b in msg.get("content") or []:
                            txt = b.get("text", "") if isinstance(b, dict) else ""
                            if "sender_id" in txt:
                                start = txt.find("{")
                                end = txt.rfind("}")
                                if start != -1 and end != -1 and end > start:
                                    meta = json.loads(txt[start:end + 1])
                                    sid = str(meta.get("sender_id", ""))
                                    if sid and sid == str(telegram_target):
                                        return True
    except Exception:
        pass

    return False


def resolve_thread_meta_from_local_files(thread_id: str) -> Optional[dict]:
    """Resolve {sessionId, telegramTarget} from local session jsonl files.

    Useful when sessions_list doesn't return inactive thread sessions.
    Looks for newest: ~/.openclaw/agents/main/sessions/*-topic-<thread_id>.jsonl
    """
    if not thread_id:
        return None
    base = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
    if not base.exists():
        return None

    candidates = sorted(
        base.glob(f"*-topic-{thread_id}.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None

    p = candidates[0]
    session_id = p.name.rsplit("-topic-", 1)[0]
    telegram_target = None

    # Try to extract sender_id from early user envelope messages
    try:
        with p.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 150:
                    break
                obj = json.loads(line)
                if obj.get("type") != "message":
                    continue
                msg = (obj.get("message") or {})
                if msg.get("role") != "user":
                    continue
                blocks = msg.get("content") or []
                for b in blocks:
                    txt = b.get("text", "") if isinstance(b, dict) else ""
                    if "sender_id" in txt:
                        # Robust extraction: message may contain multiple JSON blocks,
                        # so wide {..} parsing can fail. Prefer direct regex first.
                        m = re.search(r'"sender_id"\s*:\s*"?(\d+)"?', txt)
                        if m:
                            telegram_target = m.group(1)
                            break
                        try:
                            # Fallback: envelope is embedded json in markdown fence
                            start = txt.find("{")
                            end = txt.rfind("}")
                            if start != -1 and end != -1 and end > start:
                                meta = json.loads(txt[start:end + 1])
                                sid = meta.get("sender_id")
                                if sid:
                                    telegram_target = str(sid)
                                    break
                        except Exception:
                            pass
                if telegram_target:
                    break
    except Exception:
        pass

    return {"sessionId": session_id, "telegramTarget": telegram_target, "key": f"agent:main:main:thread:{thread_id}"}


def get_telegram_bot_token() -> Optional[str]:
    """Read the Telegram bot token from openclaw.json config."""
    try:
        cfg_data = json.loads(CONFIG_PATH.read_text())
        tg = cfg_data.get("channels", {}).get("telegram", {})
        token = tg.get("botToken") or tg.get("token")
        if token:
            return token
        for acct in tg.get("accounts", {}).values():
            if isinstance(acct, dict) and acct.get("botToken"):
                return acct["botToken"]
    except Exception:
        pass
    return None


def send_telegram_direct(
    chat_id: str,
    text: str,
    thread_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    silent: bool = False,
    parse_mode: Optional[str] = None,
) -> bool:
    """Send a message directly via Telegram Bot API, bypassing the OpenClaw message tool.

    Required when sending to DM threads from outside a session context:
    the message tool's target resolver doesn't accept 'chatId:topic:threadId' format,
    but the Telegram API accepts message_thread_id directly.

    parse_mode: None (default) = plain text; "HTML" = HTML tags; avoid "Markdown" —
    the finish notification uses **text** (CommonMark) which Telegram MarkdownV1 rejects.

    Returns True on success, False on failure (logs warning to stderr).
    """
    bot_token = get_telegram_bot_token()
    if not bot_token:
        print("⚠ send_telegram_direct: no bot token found", file=sys.stderr)
        return False
    try:
        payload: dict = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": silent,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if thread_id:
            payload["message_thread_id"] = int(thread_id)
        if reply_to:
            payload["reply_to_message_id"] = int(reply_to)
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json=payload,
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"⚠ send_telegram_direct: HTTP {resp.status_code} — {resp.text[:200]}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"⚠ send_telegram_direct: exception — {e}", file=sys.stderr)
        return False


def send_channel(token: str, session_key: str, text: str, bg_prefix: bool = True, silent: bool = False, thread_id: Optional[str] = None, reply_to: Optional[str] = None):
    """Send a notification message to the appropriate channel.

    bg_prefix=True: prepend 📡 (background/informational messages)
    silent=True: Telegram silent mode (no notification sound) — heartbeats use this
    thread_id: Telegram thread ID (message_thread_id) — works for both Forum group topics
               and DM threads (e.g. Saved Messages threads).
    reply_to: Telegram message ID to reply to (reply_to_message_id for DM thread routing).
              Takes priority over thread_id for Telegram channel.
    """
    channel, target = detect_channel(session_key)
    if not channel or not target or not token:
        return
    try:
        msg = f"{BG_PREFIX}{text}" if bg_prefix else text
        args = {
            "action": "send",
            "channel": channel,
            "target": target,
            "message": msg,
        }
        # Telegram supports silent notifications; WhatsApp does not
        if silent and channel == "telegram":
            args["silent"] = True
        # Telegram DM thread routing:
        # - With thread_id: call Telegram Bot API directly (message tool doesn't accept chatId:topic:threadId format)
        # - With reply_to only: use message tool with replyTo arg (works without thread_id)
        if thread_id and channel == "telegram":
            # Bypass message tool — send directly via Bot API with message_thread_id
            send_telegram_direct(target, msg, thread_id=thread_id, reply_to=reply_to, silent=silent)
            return
        if reply_to and channel == "telegram":
            args["replyTo"] = str(reply_to)
        requests.post(
            f"{GW_URL}/tools/invoke",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"tool": "message", "args": args},
            timeout=15,
        )
    except Exception:
        pass


def trace_live(token: Optional[str], session_key: Optional[str], enabled: bool, tag: str, text: str,
               thread_id: Optional[str] = None, reply_to: Optional[str] = None):
    """Send live technical trace events to the same chat/thread."""
    if not enabled or not token or not session_key:
        return
    send_channel(token, session_key, f"[TRACE][TECH]{tag} {text}", bg_prefix=False, silent=True,
                 thread_id=thread_id, reply_to=reply_to)


def state_file_for_project(project_name: str) -> Path:
    """State file path for per-project wake dedupe."""
    h = hashlib.sha1(project_name.encode("utf-8")).hexdigest()[:12]
    return Path(f"/tmp/codex-orchestrator-state-{h}.json")


def load_state(path: Path) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return {}


def save_state(path: Path, state: dict):
    try:
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    except Exception:
        pass


def should_dispatch_wake(state_path: Optional[Path], output_file_path: str, wake_id: str) -> bool:
    """Return True if wake should be dispatched (dedupe repeated output/wake)."""
    if not state_path:
        return True
    st = load_state(state_path)
    if st.get("last_dispatched_wake_id") == wake_id:
        return False
    if st.get("last_dispatched_output") == output_file_path:
        return False
    st["last_dispatched_wake_id"] = wake_id
    st["last_dispatched_output"] = output_file_path
    st["last_dispatch_at"] = int(time.time())
    save_state(state_path, st)
    return True


def notify_session(token: str, session_key: str, group_jid: Optional[str], message: str,
                   thread_id: Optional[str] = None, notify_session_id: Optional[str] = None,
                   reply_to: Optional[str] = None, html_msg: Optional[str] = None,
                   completion_mode: str = "single",
                   exit_code: int = 0, project_name: str = "", output_file_path: str = "",
                   iter_budget: int = 1,
                   trace_enabled: bool = False,
                   run_id: str = "",
                   wake_id: str = "",
                   state_path: Optional[Path] = None):
    """Send Codex result to the appropriate channel and wake the agent.

    WhatsApp: sends to group + attempts sessions_send to wake agent.
    Telegram: sends direct message + uses `openclaw agent --deliver` to wake agent.
    Note: sessions_send is blocked in HTTP API deny list, so we use CLI for Telegram.

    thread_id: Telegram thread ID for Forum group topic notifications.
    notify_session_id: OpenClaw session UUID for precise agent wake in threads.
    reply_to: Telegram message ID to reply to (for DM thread routing).
    """
    channel, target = detect_channel(session_key)

    # Channel-specific delivery strategy:
    # - WhatsApp: send full result directly (human sees it) + sessions_send wakes agent
    # - Telegram: agent wakes and sends one clean response; skip raw dump to avoid double messages
    if channel == "whatsapp":
        # Send direct message (human sees result immediately)
        send_channel(token, session_key, message, bg_prefix=False, thread_id=thread_id, reply_to=reply_to)

    # Wake the agent based on channel
    if channel == "whatsapp" and session_key:
        # WhatsApp: sessions_send puts result in session queue.
        # If explicit notify target points to a different group than source session,
        # wake that group session directly to avoid cross-session NO_REPLY artifacts.
        wake_session_key = session_key
        if target:
            maybe_group_session = build_whatsapp_group_session_key(session_key, target)
            if maybe_group_session and maybe_group_session != session_key:
                wake_session_key = maybe_group_session

        trace_live(token, session_key, trace_enabled, "[WHATSAPP][WAKE]", "sending sessions_send wake", thread_id, reply_to)
        agent_msg = (
            f"[CODEX_RESULT]\n{message}\n\n"
            f"---\n"
            f"⚠️ INSTRUCTION: You received an OpenAI Codex result. "
            f"Process it, then send your response to the WhatsApp group using "
            f"message(action=send, channel=whatsapp, target={target or 'GROUP_JID'}, message=YOUR_SUMMARY). "
            f"Then reply NO_REPLY to avoid duplicate. Do NOT rely on announce step."
        )
        try:
            resp = requests.post(
                f"{GW_URL}/tools/invoke",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"tool": "sessions_send",
                      "args": {"sessionKey": wake_session_key, "message": agent_msg}},
                timeout=30,
            )
            if resp.status_code == 200:
                print(f"✓ Agent notified via sessions_send -> {wake_session_key}", file=sys.stderr)
            else:
                print(f"⚠ sessions_send returned {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"⚠ Session notify error: {e}", file=sys.stderr)

    elif channel == "telegram" and target:
        # For thread sessions: always send result directly to thread first so user always sees it.
        # Agent wake is an additional continuation step and is delivered to chat (--deliver).
        already_sent = False
        if thread_id or reply_to:
            if html_msg and thread_id:
                # HTML version available — use expandable blockquote formatting
                _, tgt = detect_channel(session_key)
                send_telegram_direct(tgt, html_msg, thread_id=thread_id,
                                     reply_to=reply_to, silent=True, parse_mode="HTML")
            else:
                send_channel(token, session_key, message, bg_prefix=False,
                             silent=True, thread_id=thread_id, reply_to=reply_to)
            already_sent = True

        # Wake the agent and deliver continuation response into chat.
        # Fallback: if agent wake fails AND we haven't already sent, send full result directly.
        # NOTE: target:topic:thread format is not supported by message tool for Telegram.
        tg_target = target
        # IMPORTANT: keep wake payload clean and non-leaky.
        # Do NOT include internal markers like [CODEX_RESULT] / ⚠️ INSTRUCTION,
        # because in failure modes they may surface to the user chat.
        # completion_mode governs post-run behavior:
        # - single: concise summary + stop
        # - iterate: gap-analysis + re-run if needed
        iterative_intent = (completion_mode == "iterate")

        # Compact one-liner wake signal. Full result already delivered to thread above.
        # Short enough not to be spammy if it appears visibly in Telegram.
        if iterative_intent:
            wake_text = (
                f"[CC:iterate] exit={exit_code} project={project_name} output={output_file_path} limit={iter_budget} run_id={run_id} wake_id={wake_id}\n\n"
                "Это системный wake-вызов после того, как OpenAI Codex прислал результат по твоему же последнему запуску. "
                "Считай это обычным продолжением того же диалога: та же личность агента, та же сессия, та же история.\n\n"
                "Ключевое правило continuity: ориентируйся на ИСХОДНУЮ пользовательскую цель, ради которой запускался OpenAI Codex, "
                "а не только на последний технический подшаг. Если текущий подшаг закрыт, но исходная цель ещё нет — продолжай движение к исходной цели.\n"
                "Если видишь, что это устаревший wake по уже закрытой более новой итерации — коротко пометь его как stale и ничего не запускай.\n\n"
                "Сделай естественное продолжение переписки. Для отладки в начале сообщения используй префикс: "
                "[TRACE][AGENT][WAKE_RECEIVED].\n"
                "ЖЁСТКОЕ ПРАВИЛО: silent launch запрещён. Сначала отправь отдельный видимый turn с анализом и решением ([TRACE][AGENT][DECISION]). "
                "Только ПОСЛЕ этого, отдельным следующим действием, запускай следующую итерацию при необходимости.\n"
                "1) коротко отреагируй на результат OpenAI Codex,\n"
                "2) сопоставь результат с исходной целью пользователя и проверь, закрыта ли она полностью,\n"
                "3) если исходная цель не закрыта — в явном виде сообщи решение continue и что именно докручиваешь, затем запусти ровно одну следующую итерацию,\n"
                "4) если исходная цель закрыта — в явном виде сообщи решение stop и остановись."
            )
        else:
            wake_text = (
                f"[CC:single] exit={exit_code} project={project_name} output={output_file_path} limit=1 run_id={run_id} wake_id={wake_id}\n\n"
                "Это системный wake-вызов после того, как OpenAI Codex прислал результат по твоему же последнему запуску. "
                "Считай это обычным продолжением того же диалога: та же личность агента, та же сессия, та же история.\n\n"
                "Ключевое правило continuity: ориентируйся на ИСХОДНУЮ пользовательскую цель, ради которой запускался OpenAI Codex, "
                "а не только на последний технический подшаг.\n"
                "Если видишь, что это устаревший wake по уже закрытой более новой итерации — коротко пометь его как stale и заверши без новых действий.\n\n"
                "Сделай естественное продолжение переписки. Для отладки в начале сообщения используй префикс: "
                "[TRACE][AGENT][WAKE_RECEIVED].\n"
                "ЖЁСТКОЕ ПРАВИЛО: silent launch запрещён. Дай отдельный видимый turn с анализом и явным решением ([TRACE][AGENT][DECISION]).\n"
                "1) коротко отреагируй на результат,\n"
                "2) оцени, закрыта ли исходная цель пользователя целиком,\n"
                "3) сообщи итог пользователю и остановись."
            )

        try:
            if notify_session_id:
                cmd = ["openclaw", "agent",
                       "--session-id", notify_session_id,
                       "--message", wake_text,
                       "--deliver",
                       "--timeout", "30"]
            else:
                cmd = ["openclaw", "agent",
                       "--channel", "telegram",
                       "--to", target,
                       "--message", wake_text,
                       "--deliver",
                       "--timeout", "30"]
            if not should_dispatch_wake(state_path, output_file_path, wake_id):
                trace_live(token, session_key, trace_enabled, "[TELEGRAM][WAKE][SKIP]",
                           f"duplicate/stale wake ignored (project={project_name}, output={output_file_path}, wake_id={wake_id})",
                           thread_id, reply_to)
                return
            trace_live(token, session_key, trace_enabled, "[TELEGRAM][WAKE]",
                       f"dispatching openclaw agent wake (project={project_name}, output={output_file_path}, wake_id={wake_id})",
                       thread_id, reply_to)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
            if result.returncode == 0:
                print(f"✓ Agent woken via openclaw agent", file=sys.stderr)
            else:
                print(f"⚠ Agent wake failed: {result.stderr[:100]}", file=sys.stderr)
                if not already_sent:
                    send_channel(token, session_key, message, bg_prefix=False, thread_id=thread_id, reply_to=reply_to)
        except Exception as e:
            print(f"⚠ Telegram agent wake error: {e}", file=sys.stderr)
            if not already_sent:
                send_channel(token, session_key, message, bg_prefix=False, thread_id=thread_id, reply_to=reply_to)


def cleanup_stale_pids():
    """Remove PID files for processes that no longer exist."""
    if not PID_DIR.exists():
        return
    for pid_file in PID_DIR.glob("*.pid"):
        try:
            pid = int(pid_file.read_text().strip().split("\n")[0])
            os.kill(pid, 0)  # Check if alive
        except (ProcessLookupError, ValueError):
            pid_file.unlink(missing_ok=True)
        except PermissionError:
            pass  # Process exists but we can't signal it


def write_pid_file(task_short: str) -> Path:
    """Write PID file for this task."""
    PID_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_stale_pids()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Sanitize task name for filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in task_short[:40])
    pid_file = PID_DIR / f"{ts}-{safe_name}.pid"
    pid_file.write_text(f"{os.getpid()}\n{task_short}\n{datetime.now().isoformat()}")
    return pid_file


def kill_process_graceful(proc: subprocess.Popen, timeout_grace: int = 10):
    """SIGTERM → wait → SIGKILL."""
    try:
        proc.terminate()
        try:
            proc.wait(timeout=timeout_grace)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    except Exception:
        pass


def format_tokens(n: int) -> str:
    """Format token count: 1234 → '1.2K', 12345 → '12K'."""
    if n < 1000:
        return str(n)
    elif n < 10000:
        return f"{n/1000:.1f}K"
    else:
        return f"{n//1000}K"


def parse_stream_line(line: str, state: dict):
    """Parse Codex experimental JSON events for activity tracking and session capture."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return

    event_type = data.get("type", "")
    if not event_type:
        return

    state["last_event_time"] = time.time()
    state["events_since_heartbeat"] += 1

    if event_type == "session.created":
        session_id = data.get("session_id")
        if session_id:
            state["session_id"] = session_id
        return

    if event_type == "token_count":
        info = data.get("info") or {}
        usage = info.get("total_token_usage") or info.get("last_token_usage") or {}
        total_tokens = usage.get("total_tokens") or usage.get("output_tokens") or 0
        if total_tokens:
            state["output_tokens"] = max(state["output_tokens"], int(total_tokens))
        return

    if not event_type.startswith("item."):
        return

    item = data.get("item") or {}
    item_type = item.get("item_type") or item.get("type") or ""
    item_id = item.get("id")
    status = item.get("status", "")

    if event_type == "item.started":
        if item_id:
            state["active_item_ids"].add(item_id)
        if item_type == "command_execution":
            state["tool_calls"] += 1
            cmd = (item.get("command") or "?").strip()
            state["last_activity"] = f"💻 {cmd[:60]}"
        elif item_type == "reasoning":
            state["last_activity"] = "🧠 Thinking..."
        elif item_type == "assistant_message":
            state["last_activity"] = "✍️ Responding..."
        else:
            state["last_activity"] = f"🔧 {item_type or 'working'}"
        return

    if item_id:
        state["active_item_ids"].discard(item_id)

    if item_type == "assistant_message":
        text = (item.get("text") or "").strip()
        if text:
            state["last_message"] = text
        state["last_activity"] = "✍️ Responding..."
        return

    if item_type == "reasoning":
        state["last_activity"] = "🧠 Thinking..."
        return

    if item_type == "command_execution":
        cmd = (item.get("command") or "?").strip()
        if status == "completed":
            exit_code = item.get("exit_code")
            if exit_code is None or exit_code == 0:
                state["last_activity"] = f"💻 {cmd[:60]}"
            else:
                state["last_activity"] = f"⚠️ {cmd[:50]} (exit {exit_code})"
        else:
            state["last_activity"] = f"💻 {cmd[:60]}"
        return

    if item_type == "file_change":
        changes = item.get("changes") or []
        for change in changes:
            path = change.get("path")
            if path:
                state["files_written"].append(Path(path).name)
        if changes:
            first = Path(changes[0].get("path") or "").name or "file"
            state["last_activity"] = f"📝 file: {first}"
        else:
            state["last_activity"] = "📝 file changes"
        return

    if "search" in item_type.lower():
        state["tool_calls"] += 1
        state["last_activity"] = "🔍 Web search"
        return

    state["last_activity"] = f"🔧 {item_type or 'working'}"


def main():
    parser = argparse.ArgumentParser(description="Run OpenAI Codex CLI task async")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--project", "-p", default="/tmp/codex-scratch", help="Project directory")
    parser.add_argument("--session", "-s", help="Session key to notify on completion")
    parser.add_argument("--output", "-o", help="Output file (default: /tmp/codex-<timestamp>.txt)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Max runtime in seconds (default: {DEFAULT_TIMEOUT}s = {DEFAULT_TIMEOUT//60}min)")
    parser.add_argument("--resume", help="Resume from previous Codex session ID")
    parser.add_argument("--session-label", help="Human-readable label for this session (e.g., 'Research on X')")
    parser.add_argument("--model", help="Optional Codex model override")
    parser.add_argument("--no-search", action="store_true", help="Disable Codex web search (enabled by default)")
    parser.add_argument("--full-auto", action="store_true",
                        help="Use Codex --full-auto instead of the default dangerous unattended mode")
    parser.add_argument("--danger-full-access", action="store_true",
                        help="Compatibility flag; dangerous unattended mode is already the default")
    parser.add_argument("--notify-channel", help="Channel for notifications override (telegram|whatsapp)")
    parser.add_argument("--notify-thread-id", help="Telegram thread ID for threaded mode (auto-detected from session key)")
    parser.add_argument("--notify-session-id", help="OpenClaw session UUID for precise agent wake in threads")
    parser.add_argument("--reply-to-message-id", help="Telegram message ID to reply to (for DM thread routing)")
    parser.add_argument("--validate-only", action="store_true", help="Resolve routing and exit (no Codex run)")
    parser.add_argument("--allow-main-telegram", action="store_true", help="Allow Telegram launch without :thread: session (for non-thread Telegram setups)")
    parser.add_argument("--telegram-routing-mode", choices=["auto", "thread-only", "allow-non-thread"], default="auto", help="Telegram routing policy (default: auto)")
    parser.add_argument("--completion-mode", choices=["single", "iterate"], default="single",
                        help="(Optional, legacy) Post-completion hint: single (default) or iterate")
    parser.add_argument("--max-iterations", type=int, default=5,
                        help="Max iterations budget for iterate mode (shown in notifications; single mode is always 1)")
    parser.add_argument("--trace-live", action="store_true",
                        help="Send live technical trace events to chat/thread for debugging")
    args = parser.parse_args()

    # Effective iteration budget for display/instructions
    iter_budget = 1 if args.completion_mode == "single" else max(1, int(args.max_iterations))

    # Set notification globals (channel hint; target must be resolved deterministically)
    global NOTIFY_CHANNEL_OVERRIDE, NOTIFY_TARGET_OVERRIDE
    if args.notify_channel:
        NOTIFY_CHANNEL_OVERRIDE = args.notify_channel

    # Resolve thread_id: explicit arg takes priority, otherwise auto-detect from session key
    thread_id = args.notify_thread_id or extract_thread_id(args.session or "")
    notify_session_id = args.notify_session_id  # Optional UUID for precise agent wake in threads
    reply_to_msg_id = args.reply_to_message_id  # Optional, for DM thread routing

    # Setup
    project = Path(args.project)
    project.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = args.output or f"/tmp/codex-{ts}.txt"
    run_id = str(uuid.uuid4())
    wake_id = str(uuid.uuid4())
    state_path = state_file_for_project(str(project))
    group_jid = extract_group_jid(args.session or "")  # WhatsApp JID if present
    token = None
    pid_file = None
    proc = None
    notify_script_path = None

    try:
        token = get_token() if args.session else None
    except Exception:
        pass

    # Strict Telegram thread routing: auto-resolve missing IDs and fail fast on mismatch.
    # Goal: make incorrect launches impossible when using thread sessions.
    session_meta = resolve_session_meta(token, args.session) if (token and args.session) else None
    if not session_meta and thread_id:
        # Fallback for inactive sessions not returned by sessions_list
        session_meta = resolve_thread_meta_from_local_files(thread_id)

    if thread_id:
        # Thread sessions must always use Telegram notifications
        if args.notify_channel and args.notify_channel != "telegram":
            print("❌ Invalid routing: thread session requires --notify-channel telegram", file=sys.stderr)
            sys.exit(2)

        # Resolve target from session delivery context (mandatory for deterministic thread routing)
        resolved_target = (session_meta or {}).get("telegramTarget")
        if resolved_target:
            NOTIFY_CHANNEL_OVERRIDE = "telegram"
            NOTIFY_TARGET_OVERRIDE = resolved_target

        # If notify-session-id omitted, auto-resolve exact UUID by session key
        resolved_session_id = (session_meta or {}).get("sessionId")
        resolved_target = (session_meta or {}).get("telegramTarget")
        if not notify_session_id and resolved_session_id:
            notify_session_id = resolved_session_id

        # If caller provided notify-session-id but it mismatches the actual session key, fail hard
        if notify_session_id and resolved_session_id and notify_session_id != resolved_session_id:
            print(
                "❌ Invalid routing: --notify-session-id does not match --session key\n"
                f"   session key: {args.session}\n"
                f"   provided:   {notify_session_id}\n"
                f"   expected:   {resolved_session_id}",
                file=sys.stderr,
            )
            sys.exit(2)

        # Hard requirements for thread sessions
        if not NOTIFY_TARGET_OVERRIDE:
            print("❌ Invalid routing: thread session requires resolvable telegram target (auto-resolve failed)", file=sys.stderr)
            print("   Tip: ensure session exists in sessions_list or local thread session files", file=sys.stderr)
            sys.exit(2)
        if not notify_session_id:
            print("❌ Invalid routing: thread session requires --notify-session-id (auto-resolve failed)", file=sys.stderr)
            print("   Tip: pass --notify-session-id <uuid> from sessions_list", file=sys.stderr)
            sys.exit(2)

        # Ensure override is active after auto-resolution
        NOTIFY_CHANNEL_OVERRIDE = "telegram"

    # Safety guard: Telegram launches without explicit thread are error-prone and can drift across threads.
    ch_now, tgt_now = detect_channel(args.session or "")
    is_telegram_route = (ch_now == "telegram") or (args.notify_channel == "telegram")
    if is_telegram_route and not thread_id:
        # Non-thread Telegram is allowed for users/chats that do not use thread mode,
        # but guarded in auto mode if we detect ambiguity.
        tg_target = NOTIFY_TARGET_OVERRIDE or (session_meta or {}).get("telegramTarget")
        user_scope_key = bool(args.session and args.session.startswith("agent:main:telegram:user:"))
        if not tg_target and user_scope_key:
            tg_target = args.session.split(":")[-1]

        if args.telegram_routing_mode == "thread-only":
            print("❌ Unsafe routing blocked: Telegram launch requires thread session (:thread:<id>)", file=sys.stderr)
            print("   Use --session agent:main:main:thread:<id>", file=sys.stderr)
            sys.exit(2)

        if args.telegram_routing_mode == "allow-non-thread":
            pass  # explicitly allowed
        else:
            # auto mode guard #1: synthesized/ambiguous user-scope key must be explicit
            if user_scope_key and not args.allow_main_telegram:
                print("❌ Unsafe routing blocked: session key is non-thread user scope (agent:main:telegram:user:...).", file=sys.stderr)
                print("   For thread chats use --session agent:main:main:thread:<id>.", file=sys.stderr)
                print("   For intentional non-thread Telegram, pass --allow-main-telegram or --telegram-routing-mode allow-non-thread.", file=sys.stderr)
                sys.exit(2)

            # auto mode guard #2: if this target has recent thread sessions, treat non-thread as likely mistake
            if tg_target and has_recent_thread_session(token, str(tg_target), max_age_hours=24):
                if not args.allow_main_telegram:
                    print("❌ Unsafe routing blocked: recent thread session detected for this Telegram target.", file=sys.stderr)
                    print("   Use thread session key (:thread:<id>) or pass --allow-main-telegram to force non-thread.", file=sys.stderr)
                    sys.exit(2)

    # Deterministic Telegram target resolution: no manual --notify-target allowed.
    # If Telegram routing is requested/detected and target cannot be resolved, fail fast.
    if is_telegram_route:
        resolved_tg = NOTIFY_TARGET_OVERRIDE or (session_meta or {}).get("telegramTarget")
        user_scope_key = bool(args.session and args.session.startswith("agent:main:telegram:user:"))
        if not resolved_tg and user_scope_key:
            resolved_tg = args.session.split(":")[-1]
        if not resolved_tg:
            print("❌ Invalid routing: Telegram target could not be resolved from session metadata", file=sys.stderr)
            print("   Provide a valid thread/user session key resolvable via sessions_list/local files.", file=sys.stderr)
            sys.exit(2)
        NOTIFY_CHANNEL_OVERRIDE = "telegram"
        NOTIFY_TARGET_OVERRIDE = str(resolved_tg)

    if args.validate_only:
        ch, tgt = detect_channel(args.session or "")
        print("✅ Routing validation")
        print(f"   session: {args.session}")
        print(f"   thread_id: {thread_id}")
        print(f"   channel: {ch}")
        print(f"   target: {tgt}")
        print(f"   notify_session_id: {notify_session_id}")
        print(f"   allow_main_telegram: {args.allow_main_telegram}")
        print(f"   completion_mode: {args.completion_mode}")
        print(f"   max_iterations: {iter_budget}")
        if session_meta:
            print(f"   resolved_session_id: {session_meta.get('sessionId')}")
            print(f"   resolved_telegram_target: {session_meta.get('telegramTarget')}")
        sys.exit(0)

    exit_code = -1  # default; updated after Codex run completes
    try:
        # Write PID file
        pid_file = write_pid_file(args.task[:60])

        # Codex should run inside a git repo; initialize one if needed.
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q"], cwd=str(project), capture_output=True)

        print(f"🔧 Starting OpenAI Codex...", file=sys.stderr)
        print(f"   Task: {args.task[:100]}", file=sys.stderr)
        print(f"   Project: {project}", file=sys.stderr)
        print(f"   Output: {output_file}", file=sys.stderr)
        print(f"   Timeout: {args.timeout}s ({args.timeout//60}min)", file=sys.stderr)
        if args.resume:
            print(f"   Resume: {args.resume}", file=sys.stderr)
        if args.session_label:
            print(f"   Label: {args.session_label}", file=sys.stderr)
        if args.model:
            print(f"   Model: {args.model}", file=sys.stderr)
        print(f"   Search: {'off' if args.no_search else 'on'}", file=sys.stderr)
        sandbox_mode = "full-auto" if args.full_auto else "danger-full-access"
        print(f"   Sandbox: {sandbox_mode}", file=sys.stderr)
        print(f"   PID: {os.getpid()}", file=sys.stderr)
        print(f"   Completion mode: {args.completion_mode}", file=sys.stderr)
        print(f"   Max iterations: {iter_budget}", file=sys.stderr)

        # Resume display in launch message: show session id for resumed runs, otherwise 'new'
        resume_display = args.resume if args.resume else "new"

        # Send launch info (informational)
        _ch, _tgt = detect_channel(args.session or "")
        trace_live(token, args.session, args.trace_live, "[RUN_TASK][START]",
                   f"project={project} mode={args.completion_mode} limit={iter_budget} run_id={run_id}", thread_id, reply_to_msg_id)
        if _tgt and token:
            launch_parts = [f"🚀 *OpenAI Codex started*"]
            if args.session_label:
                launch_parts.append(f"*Label:* {args.session_label}")
            launch_parts.append(f"*Project:* {project}")
            launch_parts.append(f"*Timeout:* {fmt_duration(args.timeout)}")
            launch_parts.append(f"*Mode:* {args.completion_mode}")
            launch_parts.append(f"*Iteration limit:* {iter_budget}")
            launch_parts.append(f"*Resume:* {resume_display}")
            launch_parts.append(f"*Search:* {'off' if args.no_search else 'on'}")
            launch_parts.append(f"*Sandbox:* {sandbox_mode}")
            launch_parts.append(f"*PID:* {os.getpid()}")
            # Build launch message: use HTML + expandable blockquote for prompt
            def _esc(s: str) -> str:
                return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            html_parts = ["🚀 <b>OpenAI Codex started</b>"]
            if args.session_label:
                html_parts.append(f"<b>Label:</b> {_esc(args.session_label)}")
            html_parts.append(f"<b>Project:</b> {_esc(str(project))}")
            html_parts.append(f"<b>Timeout:</b> {_esc(fmt_duration(args.timeout))}")
            html_parts.append(f"<b>Mode:</b> {_esc(args.completion_mode)}")
            html_parts.append(f"<b>Iteration limit:</b> {_esc(str(iter_budget))}")
            html_parts.append(f"<b>Resume:</b> {_esc(resume_display)}")
            html_parts.append(f"<b>Search:</b> {_esc('off' if args.no_search else 'on')}")
            html_parts.append(f"<b>Sandbox:</b> {_esc(sandbox_mode)}")
            html_parts.append(f"<b>PID:</b> {os.getpid()}")
            prompt_preview = args.task[:3500] + ("…" if len(args.task) > 3500 else "")
            html_parts.append(f"<b>Prompt:</b>\n<blockquote expandable>{_esc(prompt_preview)}</blockquote>")
            launch_html = "\n".join(html_parts)

            if thread_id and _ch == "telegram":
                # Use direct Bot API for thread routing + HTML parse mode
                send_telegram_direct(
                    _tgt, launch_html,
                    thread_id=thread_id, reply_to=reply_to_msg_id,
                    silent=True, parse_mode="HTML"
                )
            else:
                # Fallback: gateway message tool (non-thread sends, other channels)
                task_preview = args.task[:300] + ("…" if len(args.task) > 300 else "")
                launch_parts.append(f"Prompt: {task_preview}")
                send_channel(token, args.session or "", "\n".join(launch_parts),
                             silent=True, thread_id=thread_id, reply_to=reply_to_msg_id)

        # Build Codex command
        # Create a progress notification script on disk so Codex can send
        # mid-task updates without seeing the bot token in the prompt.
        notify_script_path = None
        if thread_id and _ch == "telegram" and _tgt:
            bot_token_for_script = get_telegram_bot_token()
            if bot_token_for_script:
                notify_script_path = f"/tmp/codex-notify-{os.getpid()}.py"
                with open(notify_script_path, "w") as _nf:
                    _nf.write(
                        "#!/usr/bin/env python3\n"
                        "import sys, json\n"
                        "try:\n"
                        "    import urllib.request\n"
                        f"    raw = sys.argv[1] if len(sys.argv) > 1 else 'Progress update'\n"
                        f"    prefix = '📡 🟢 Codex: '\n"
                        f"    msg = raw if raw.startswith(prefix) else (prefix + raw)\n"
                        f"    payload = json.dumps({{'chat_id': '{_tgt}', 'text': msg, "
                        f"'message_thread_id': {thread_id}, 'disable_notification': True}}).encode()\n"
                        f"    req = urllib.request.Request("
                        f"'https://api.telegram.org/bot{bot_token_for_script}/sendMessage', "
                        f"data=payload, headers={{'Content-Type': 'application/json'}})\n"
                        f"    urllib.request.urlopen(req, timeout=10)\n"
                        "except Exception as e:\n"
                        "    print(f'notify error: {e}', file=sys.stderr)\n"
                    )
                os.chmod(notify_script_path, 0o755)

        # Prepend system context about notification script (avoids prompt-injection warnings)
        task_prompt = args.task
        if notify_script_path:
            task_prompt = (
                f"[Automation context: a progress notification script is available at "
                f"{notify_script_path}. Run it with: "
                f"python3 {notify_script_path} 'your message text' — this sends a "
                f"message to the task owner. Use it once during the task to confirm progress.]\n\n"
                + args.task
            )

        codex_cmd = ["codex"]
        if args.model:
            codex_cmd.extend(["--model", args.model])
        if not args.no_search:
            codex_cmd.append("--search")
        codex_cmd.append("exec")
        codex_cmd.extend([
            "--experimental-json",
            "--output-last-message", output_file,
            "-C", str(project),
        ])
        if args.full_auto:
            codex_cmd.append("--full-auto")
        else:
            codex_cmd.append("--dangerously-bypass-approvals-and-sandbox")

        if args.resume:
            codex_cmd.extend(["resume", args.resume, task_prompt])
        else:
            codex_cmd.append(task_prompt)

        # Start Codex CLI
        proc = subprocess.Popen(
            codex_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Activity tracking state
        state = {
            "tool_calls": 0,
            "files_written": [],
            "last_activity": "",
            "session_id": None,
            "last_event_time": time.time(),
            "output_tokens": 0,
            "events_since_heartbeat": 0,
            "active_item_ids": set(),
            "last_message": "",
        }

        start = time.time()
        last_heartbeat = 0
        output_lines = []
        timed_out = False

        # Read stdout in background thread
        def reader():
            for line in proc.stdout:
                line = line.strip()
                if line:
                    output_lines.append(line)
                    parse_stream_line(line, state)

        read_thread = threading.Thread(target=reader, daemon=True)
        read_thread.start()

        # Main loop: poll process, send heartbeats, check timeout
        while proc.poll() is None:
            time.sleep(5)
            elapsed = int(time.time() - start)

            # Timeout check
            if elapsed >= args.timeout:
                timed_out = True
                print(f"⏰ Timeout ({args.timeout}s) reached, killing process...", file=sys.stderr)
                kill_process_graceful(proc)
                break

            # Heartbeat every 60s
            _hb_ch, _hb_tgt = detect_channel(args.session or "")
            if elapsed - last_heartbeat >= 60 and _hb_tgt and token:
                last_heartbeat = elapsed
                mins = elapsed // 60

                # Status emoji based on liveness
                idle_secs = time.time() - state["last_event_time"]
                if idle_secs < 30:
                    status = "🟢"
                elif idle_secs < 120:
                    status = "🟡"
                else:
                    status = "🔴"

                parts = [f"{status} Codex ({mins}min)"]
                if state["active_item_ids"]:
                    parts.append(f"ops:{len(state['active_item_ids'])}")
                if state["output_tokens"] > 0:
                    parts.append(f"{format_tokens(state['output_tokens'])} tok")
                if state["tool_calls"] > 0:
                    parts.append(f"{state['tool_calls']} calls")
                if idle_secs > 120:
                    parts.append(f"🧠 Thinking... ({int(idle_secs)}s)")
                elif idle_secs > 15 and state["events_since_heartbeat"] == 0:
                    parts.append(f"🧠 Thinking...")
                elif state["last_activity"]:
                    activity = state["last_activity"]
                    if state["events_since_heartbeat"] > 0:
                        activity += " ✍️"
                    parts.append(activity)

                state["events_since_heartbeat"] = 0
                send_channel(token, args.session or "", " | ".join(parts), silent=True, thread_id=thread_id, reply_to=reply_to_msg_id)

        read_thread.join(timeout=5)
        stderr_output = ""
        try:
            stderr_output = proc.stderr.read() or ""
        except Exception:
            pass

        # Check for obvious resume failure
        resume_failed = bool(args.resume and re.search(r"(not found|unable to resume|unknown session|invalid session)", stderr_output, re.IGNORECASE))
        if resume_failed:
            print(f"❌ Resume failed: session {args.resume} not found", file=sys.stderr)
            if args.session and token and group_jid:
                notify_session(token, args.session, group_jid,
                    f"❌ Codex resume failed\n\n"
                    f"Session ID `{args.resume}` not found or expired.\n\n"
                    f"**Suggestion:** Start a fresh session without --resume flag.",
                    thread_id=thread_id, notify_session_id=notify_session_id, reply_to=reply_to_msg_id, completion_mode=args.completion_mode,
                           exit_code=exit_code, project_name=str(project.name), output_file_path=output_file, iter_budget=iter_budget,
                           trace_enabled=args.trace_live, run_id=run_id, wake_id=wake_id, state_path=state_path)
                print("📨 Resume failure notified", file=sys.stderr)
            return  # Exit early, don't process output

        output = ""
        try:
            output = Path(output_file).read_text()
        except Exception:
            pass
        if not output:
            output = state.get("last_message", "") or stderr_output or "(no output captured)"
            Path(output_file).write_text(output)

        exit_code = proc.returncode if proc.returncode is not None else -1
        output_size = len(output)
        preview = output[:2000]
        elapsed_min = int((time.time() - start) / 60)

        status = "⏰ TIMEOUT" if timed_out else ("✅" if exit_code == 0 else "❌")
        print(f"{status} Done (exit {exit_code}, {output_size} chars, {elapsed_min}min)", file=sys.stderr)

        # Register session in registry
        if state.get("session_id"):
            try:
                session_status = "timeout" if timed_out else ("completed" if exit_code == 0 else "failed")
                update_fields = {
                    "task_summary": args.task[:200],
                    "project_dir": str(project),
                    "openclaw_session": args.session,
                    "output_file": output_file,
                    "status": session_status,
                }
                if args.session_label:
                    update_fields["label"] = args.session_label
                updated = update_session(state["session_id"], **update_fields)
                if not updated:
                    register_session(
                        session_id=state["session_id"],
                        label=args.session_label,
                        task=args.task,
                        project_dir=str(project),
                        openclaw_session=args.session,
                        output_file=output_file,
                        status=session_status
                    )
                print(f"📝 Session registered: {state['session_id']}", file=sys.stderr)
            except Exception as e:
                print(f"⚠️  Failed to register session: {e}", file=sys.stderr)

        # Notify session with result
        if args.session and token:
            trace_live(token, args.session, args.trace_live, "[RUN_TASK][COMPLETE]",
                       f"exit={exit_code} output={output_file} size={output_size} run_id={run_id} wake_id={wake_id}", thread_id, reply_to_msg_id)
            def _e(s: str) -> str:
                return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            if timed_out:
                elapsed = fmt_duration(int(time.time() - start))
                msg = (
                    f"⏰ OpenAI Codex timed out after {elapsed} "
                    f"(limit: {fmt_duration(args.timeout)})\n\n"
                    f"Task: {args.task[:200]}\n"
                    f"Project: {project}\n"
                    f"Tool calls: {state['tool_calls']}\n\n"
                    f"Partial result ({output_size} chars):\n\n{preview}\n\n"
                    f"Full output: {output_file}"
                )
                html_msg = (
                    f"⏰ <b>OpenAI Codex timed out</b> after {_e(elapsed)} "
                    f"(limit: {_e(fmt_duration(args.timeout))})\n\n"
                    f"<b>Task:</b> {_e(args.task[:200])}\n"
                    f"<b>Project:</b> {_e(str(project))}\n"
                    f"<b>Tool calls:</b> {state['tool_calls']}\n\n"
                    f"<b>Partial result</b> ({output_size} chars):\n"
                    f"<blockquote expandable>{_e(preview)}</blockquote>\n"
                    f"<b>Full output:</b> <code>{_e(str(output_file))}</code>"
                )
            elif exit_code == 0:
                trunc = "...(truncated)" if output_size > 2000 else ""
                msg = (
                    f"✅ OpenAI Codex task complete!\n\n"
                    f"Task: {args.task[:200]}\n"
                    f"Project: {project}\n"
                    f"Result ({output_size} chars):\n\n{preview}\n{trunc}\n"
                    f"Full output: {output_file}"
                )
                html_msg = (
                    f"✅ <b>OpenAI Codex task complete!</b>\n\n"
                    f"<b>Task:</b> {_e(args.task[:200])}\n"
                    f"<b>Project:</b> {_e(str(project))}\n"
                    f"<b>Result</b> ({output_size} chars):\n"
                    f"<blockquote expandable>{_e(preview)}</blockquote>\n"
                    f"{_e(trunc)}"
                    f"<b>Full output:</b> <code>{_e(str(output_file))}</code>"
                )
            else:
                msg = (
                    f"❌ OpenAI Codex error (exit {exit_code})\n\n"
                    f"Task: {args.task[:200]}\n"
                    f"Project: {project}\n\n{preview}"
                )
                html_msg = (
                    f"❌ <b>OpenAI Codex error</b> (exit {exit_code})\n\n"
                    f"<b>Task:</b> {_e(args.task[:200])}\n"
                    f"<b>Project:</b> {_e(str(project))}\n\n"
                    f"<blockquote expandable>{_e(preview)}</blockquote>"
                )

            notify_session(token, args.session, group_jid, msg,
                           thread_id=thread_id, notify_session_id=notify_session_id,
                           reply_to=reply_to_msg_id, html_msg=html_msg, completion_mode=args.completion_mode,
                           exit_code=exit_code, project_name=str(project.name), output_file_path=output_file, iter_budget=iter_budget,
                           trace_enabled=args.trace_live, run_id=run_id, wake_id=wake_id, state_path=state_path)
            print("📨 Session notified", file=sys.stderr)

    except Exception as e:
        # Crash-safe: always try to notify
        print(f"💥 Crash: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

        if proc and proc.poll() is None:
            kill_process_graceful(proc)

        if args.session and token:
            try:
                notify_session(token, args.session, group_jid,
                    f"💥 OpenAI Codex runner crashed!\n\n"
                    f"**Task:** {args.task[:200]}\n"
                    f"**Error:** {str(e)[:500]}",
                    thread_id=thread_id, notify_session_id=notify_session_id, reply_to=reply_to_msg_id, completion_mode=args.completion_mode,
                           exit_code=exit_code, project_name=str(project.name), output_file_path=output_file, iter_budget=iter_budget,
                           trace_enabled=args.trace_live, run_id=run_id, wake_id=wake_id, state_path=state_path)
            except Exception:
                pass

        # Fallback: direct channel notification
        _fb_ch, _fb_tgt = detect_channel(args.session or "")
        if _fb_tgt and token and not args.session:
            send_channel(token, args.session or "", f"💥 OpenAI Codex crash: {str(e)[:200]}", thread_id=thread_id, reply_to=reply_to_msg_id)

    finally:
        # Cleanup PID file
        if pid_file and pid_file.exists():
            pid_file.unlink(missing_ok=True)
        # Cleanup notification script
        if notify_script_path and Path(notify_script_path).exists():
            Path(notify_script_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
