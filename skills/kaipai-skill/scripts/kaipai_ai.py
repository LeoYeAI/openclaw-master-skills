#!/usr/bin/env python3
"""
Kaipai skill CLI — single entry for agents:
preflight, install-deps, run-task, query-task, spawn-run-task,
last-task, history, resolve-input.
Run from anywhere: python3 /path/to/scripts/kaipai_ai.py <command> ...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_BASE_DIR = SCRIPTS_DIR.parent

import config as skill_config

STATE_DIR = Path.home() / ".openclaw" / "workspace" / "openclaw-kaipai-ai"
LAST_TASK_FILE = STATE_DIR / "last_task.json"
HISTORY_DIR = STATE_DIR / "history"

VIDEO_TASKS = frozenset({"videoscreenclear", "hdvideoallinone"})

CONNECT_TIMEOUT = 15
READ_TIMEOUT = 60

PLACEHOLDER_AK = "your_access_key_here"
PLACEHOLDER_SK = "your_secret_key_here"

DEFAULT_PARAMS = {"parameter": {"rsp_media_type": "url"}}

# OpenClaw sessions_spawn default; video tasks may poll up to ~1h extended schedule
SPAWN_DEFAULT_TIMEOUT_SECONDS = 3600

_HTTPS_URL_RE = re.compile(r"https://[^\s\])}>\"',]+", re.IGNORECASE)


def _https_urls_from_text(text: str) -> list[str]:
    """Extract https URLs from API msg / detail (e.g. consume.json meta.msg)."""
    if not isinstance(text, str) or not text.strip():
        return []
    out: list[str] = []
    for u in _HTTPS_URL_RE.findall(text):
        u = u.rstrip(".,;)]}>\"'")
        if u and u not in out:
            out.append(u)
    return out


def _pick_pricing_url(urls: list[str]) -> str | None:
    if not urls:
        return None
    for u in urls:
        if "pricing" in u.lower():
            return u
    return urls[0]


def _read_ak_sk_from_env_file() -> tuple[str, str]:
    ak = os.environ.get("MT_AK", "").strip()
    sk = os.environ.get("MT_SK", "").strip()
    env_path = SCRIPTS_DIR / ".env"
    if not env_path.exists():
        return ak, sk
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip().strip("\"'")
                if key == "MT_AK" and not ak:
                    ak = value
                elif key == "MT_SK" and not sk:
                    sk = value
    except OSError:
        pass
    return ak, sk


def _success_envelope(task_name: str, result: dict, *, resume: bool = False) -> dict:
    urls = result.get("output_urls")
    if not isinstance(urls, list):
        urls = []
    primary = urls[0] if urls else None
    if resume:
        instruction = (
            "Polling resumed successfully. Use primary_result_url for Step 4 or the next "
            "stage --input. Do not re-run run-task for this task_id. "
            "Next stage: new job (video: new spawn-run-task per stage). "
            "Details: SKILL.md Step 3 and Multi-stage pipelines."
        )
    else:
        instruction = (
            "Task completed. Do not re-run run-task for this task_id; use query-task only "
            "to resume. Next pipeline stage: new run-task with next --task and "
            "--input=primary_result_url (each video stage: its own spawn-run-task). "
            "Step 4: primary_result_url. Empty output_urls: check data/meta. "
            "Full rules: SKILL.md."
        )
    return {
        **result,
        "skill_status": "completed",
        "task_name": task_name,
        "primary_result_url": primary,
        "agent_instruction": instruction,
    }


def _is_failed_cli_result(result: dict) -> bool:
    if result.get("skill_status") == "failed":
        return True
    err = result.get("error")
    if err in (
        "poll_timeout",
        "poll_aborted",
        "task_failed",
        "invalid_result",
        "membership_required",
        "credit_required",
        "consume_param_error",
    ):
        return True
    return False


def _envelope_consume_denied(e, task_name: str) -> dict:
    """Structured stdout for POST /skill/consume.json failures (see docs/errors-and-polling.md)."""
    api_code = e.code
    detail = e.msg
    if api_code == 60001:
        err = "membership_required"
        agent_instruction = (
            "MANDATORY (user-visible): Quota consume failed — membership or eligible subscription "
            "is required (api_code 60001). You must tell the user clearly, following the server "
            "**detail** (API msg). If this JSON has **pricing_url**, include that link in your reply; "
            "if not, quote or paste the full **detail** so any links in the server message reach the user. "
            "Do not retry run-task expecting success by only changing --task or --params."
        )
    elif api_code == 60002:
        err = "credit_required"
        agent_instruction = (
            "MANDATORY (user-visible): Quota consume failed — insufficient credits (api_code 60002). "
            "You must tell the user they need more credits or a subscription before this API can run, "
            "using the server **detail** (API msg) as the source of truth. If this JSON has **pricing_url**, "
            "include that link; if not, quote or paste the full **detail** so links from the API are visible. "
            "Do not retry run-task or only tweak --task/--params expecting this to clear; do not treat as success."
        )
    else:
        err = "consume_param_error"
        agent_instruction = (
            f"Quota consume failed (api_code={api_code}, see detail). "
            "Treat as a parameter or invocation issue: verify --task, --input, and --params "
            "against SKILL.md and remote config, then fix and retry. Do not tell the user to "
            "recharge unless api_code is 60002."
        )
    out: dict = {
        "error": err,
        "skill_status": "failed",
        "failure_stage": "consume_quota",
        "api_code": api_code,
        "detail": detail,
        "task_name": task_name,
        "agent_instruction": agent_instruction,
    }
    if api_code in (60001, 60002):
        pu = _pick_pricing_url(_https_urls_from_text(detail))
        if pu:
            out["pricing_url"] = pu
    return out


def _merge_pipeline_trace(
    result: dict,
    client,
    *,
    success: bool,
) -> dict:
    """Attach upload/download/quota/submit steps for stdout JSON (stderr has [kaipai-ai] lines)."""
    if not isinstance(result, dict):
        return result
    trace = list(getattr(client, "_pipeline_trace", None) or [])
    if success:
        urls = result.get("output_urls")
        n = len(urls) if isinstance(urls, list) else 0
        p = result.get("primary_result_url")
        prev = None
        if isinstance(p, str):
            prev = p if len(p) <= 72 else p[:69] + "..."
        trace = trace + [
            {
                "step": "result_download",
                "description": "Download outputs with HTTP GET on primary_result_url or each output_urls item",
                "output_count": n,
                "primary_result_url_preview": prev,
            }
        ]
    result["pipeline_trace"] = trace
    return result


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False), flush=True)


def _is_video_task(task: str) -> bool:
    return (task or "").strip() in VIDEO_TASKS


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _task_record_from_result(
    task_name: str,
    input_src: str,
    result: dict | None,
    *,
    error_message: str | None = None,
) -> dict:
    rec: dict = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "task_name": task_name,
        "input": input_src,
    }
    if result and isinstance(result, dict):
        rec["skill_status"] = result.get("skill_status", "unknown")
        tid = result.get("task_id")
        if not tid and isinstance(result.get("data"), dict):
            r = result["data"].get("result")
            if isinstance(r, dict):
                tid = r.get("id")
        if tid:
            rec["task_id"] = tid
        if result.get("primary_result_url"):
            rec["primary_result_url"] = result["primary_result_url"]
        if result.get("output_urls"):
            rec["output_urls"] = result["output_urls"]
        if result.get("error"):
            rec["error"] = result["error"]
    if error_message:
        rec["skill_status"] = "failed"
        rec["error"] = error_message
    return rec


def _save_submitted_checkpoint(task_name: str, input_src: str, task_id: str) -> None:
    """
    Persist task_id to last_task.json as soon as the async job is accepted (before polling).
    Lets agents recover with query-task if the host kills the process mid-poll.
    """
    tid = (task_id or "").strip()
    if not tid:
        return
    rec = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "task_name": task_name,
        "input": input_src,
        "task_id": tid,
        "skill_status": "polling",
        "agent_instruction": (
            "Async job submitted; polling in progress. If this process stops before "
            "final JSON on stdout (host timeout, SIGKILL, OOM), use "
            "`kaipai_ai.py query-task --task-id` with the task_id above — do not "
            "run-task again for this job. See SKILL.md §3c and docs/errors-and-polling.md."
        ),
    }
    _ensure_state_dir()
    with open(LAST_TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)


def _save_task_record(record: dict) -> None:
    _ensure_state_dir()
    with open(LAST_TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    hist_path = HISTORY_DIR / f"task_{ts}.json"
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    history_files = sorted(HISTORY_DIR.glob("task_*.json"))
    if len(history_files) > 50:
        for old in history_files[:-50]:
            old.unlink(missing_ok=True)


def _run_task_command_argv(task: str, input_src: str, params_json: str) -> list[str]:
    argv = [
        "python3",
        str((SCRIPTS_DIR / "kaipai_ai.py").resolve()),
        "run-task",
        "--task",
        task,
        "--input",
        input_src,
    ]
    if params_json:
        argv.extend(["--params", params_json])
    return argv


def _run_task_command_shell(task: str, input_src: str, params_json: str) -> str:
    parts = _run_task_command_argv(task, input_src, params_json)
    return " ".join(shlex.quote(p) for p in parts)


def build_spawn_run_task(
    task: str,
    input_src: str,
    params_json: str,
    deliver_to: str | None,
    deliver_channel: str | None,
    run_timeout_seconds: int,
) -> dict:
    """Build sessions_spawn payload for async Kaipai run-task (same as Medeo spawn-task pattern)."""
    script_path = str((SCRIPTS_DIR / "kaipai_ai.py").resolve())
    deliver_to_str = deliver_to or "<deliver_to>"
    deliver_channel_str = (deliver_channel or "feishu").lower()
    base_dir = str(SKILL_BASE_DIR)
    cmd = _run_task_command_shell(task, input_src, params_json)
    is_video = _is_video_task(task)

    if deliver_channel_str == "feishu":
        if is_video:
            delivery_instructions = (
                "  2. **Feishu (video):** download then send (credentials: ~/.openclaw/openclaw.json):\n"
                "     ```\n"
                "     curl -sL -o /tmp/kaipai_result.mp4 \"<primary_result_url_or_output_urls[0]>\"\n"
                f"     python3 {base_dir}/scripts/feishu_send_video.py \\\n"
                f"       --video /tmp/kaipai_result.mp4 --to \"{deliver_to_str}\" \\\n"
                "       --video-url \"<primary_result_url_or_output_urls[0]>\" \\\n"
                "       [--cover-url \"<optional_thumb_url>\"] [--duration <ms_if_known>]\n"
                "     ```\n"
                "     `--video-url` → second text with download link; optional cover/duration (ms). "
                "Edge cases: docs/feishu-send-video.md.\n"
            )
        else:
            delivery_instructions = (
                "  2. **Feishu (image):**\n"
                "     ```\n"
                f"     python3 {base_dir}/scripts/feishu_send_image.py "
                f'--image "<result_url>" --to "{deliver_to_str}"\n'
                "     ```\n"
            )
    elif deliver_channel_str == "telegram":
        if is_video:
            delivery_instructions = (
                "  2. **Deliver via Telegram (video task):** download then sendVideo:\n"
                "     ```\n"
                "     curl -sL -o /tmp/kaipai_result.mp4 \"<primary_result_url_or_output_urls[0]>\"\n"
                f"     TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN python3 {base_dir}/scripts/telegram_send_video.py \\\n"
                f"       --video /tmp/kaipai_result.mp4 --to \"{deliver_to_str}\" \\\n"
                "       --video-url \"<primary_result_url_or_output_urls[0]>\" \\\n"
                '       [--cover-url "<optional_thumb_url>"] [--duration <seconds>] --caption "✅ Done"\n'
                "     ```\n"
                "     `--video-url` always sends a second text message with the download link "
                "(even if sendVideo succeeds). Max ~50 MB via Bot API; larger files rely on the link."
            )
        else:
            delivery_instructions = (
                "  2. **Deliver via Telegram (image task):**\n"
                "     ```\n"
                f"     TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN python3 {base_dir}/scripts/telegram_send_image.py \\\n"
                f'       --image "<result_url>" --to "{deliver_to_str}" --caption "✅ Done"\n'
                "     ```\n"
            )
    elif deliver_channel_str == "discord":
        ext_hint = "mp4" if is_video else "jpg"
        delivery_instructions = (
            "  2. **Deliver via Discord:**\n"
            "     Download then use the message tool:\n"
            "     ```\n"
            f"     curl -sL -o /tmp/kaipai_result.{ext_hint} \"<result_url>\"\n"
            "     ```\n"
            f"     `message(action=\"send\", channel=\"discord\", target=\"{deliver_to_str}\", "
            f'filePath="/tmp/kaipai_result.{ext_hint}")`\n'
            "     (~25 MB limit — otherwise send the URL as text.)"
        )
    else:
        delivery_instructions = (
            f"  2. **Deliver** to \"{deliver_to_str}\" using the host `message` tool "
            "with media or a link to result_url."
        )

    timeout_hint = (
        f"Keep `runTimeoutSeconds` at least the payload default ({SPAWN_DEFAULT_TIMEOUT_SECONDS}s); "
        "do not shrink without accepting timeout risk. "
        "SIGKILL / no final JSON, host turn limits, `query-task` / `last-task` / `history`: "
        "see the skill file `docs/errors-and-polling.md` and SKILL.md §3c–§3d.\n\n"
    )
    task_text = (
        "You are a Kaipai AI worker. Run the following command and complete delivery.\n\n"
        "BILLING (MANDATORY): This API consumes paid quota for the MT_AK tenant. Never tell the "
        "user the tool is free, costs nothing, or uses no credits; do not invent prices or plans. "
        "Use neutral success copy only. On credit/membership errors, follow stdout **detail** and "
        "**pricing_url** when present (same as SKILL.md Step 3 quota failures).\n"
        "SUBMISSION (MANDATORY): Run only the embedded command below — do not replace it with "
        "hand-crafted curl/HTTP to wapi or AIGC invoke (that skips /skill/consume.json). "
        "For status on an existing task_id only, use query-task per SKILL.md.\n\n"
        "Command:\n"
        "```\n"
        f"{cmd}\n"
        "```\n\n"
        "Run install-deps first if this environment never installed requirements:\n"
        f"`python3 {shlex.quote(script_path)} install-deps`\n\n"
        + timeout_hint
        + "The command blocks until the algorithm finishes (wall time varies; "
        "do NOT background it).\n\n"
        "When the command finishes:\n"
        '- If exit code is 0 and stdout JSON contains "skill_status": "completed":\n'
        "  1. Use output_urls[0] or primary_result_url as the result link.\n"
        f"{delivery_instructions}\n"
        "  3. Reply with a short success summary.\n"
        '- If stdout JSON has "skill_status": "failed" or top-level "error" '
        "(e.g. poll_timeout, poll_aborted, task_failed), or exit code non-zero: explain "
        "to the user; check MT_AK/MT_SK, network; timeouts: larger runTimeoutSeconds if needed.\n"
        "  - If **error** is **credit_required** (api_code 60002) or **failure_stage** is "
        "**consume_quota** with that error: follow stdout **detail** (server msg). Include JSON "
        "**pricing_url** in your reply when present (parsed from the API message); otherwise paste "
        "or quote the full **detail** so the user sees any links the server sent.\n"
        "  - If **error** is **membership_required** (api_code 60001): same — **pricing_url** if "
        "present, else full **detail**.\n"
        "  - If **error** is **consume_param_error**: fix invocation per agent_instruction; "
        "do not blame credits.\n"
        "- If you have **task_id** and the job may still be running, resume polling only:\n"
        f"  `python3 {shlex.quote(script_path)} query-task --task-id \"<task_id>\"`\n"
    )

    label = f"{task}: {input_src}"
    if len(label) > 72:
        label = label[:69] + "..."

    return {
        "sessions_spawn_args": {
            "task": task_text,
            "label": "kaipai: " + label,
            "runTimeoutSeconds": run_timeout_seconds,
        },
        "command": cmd,
    }


def cmd_preflight(_args: argparse.Namespace) -> int:
    ak, sk = _read_ak_sk_from_env_file()
    ok = (
        bool(ak)
        and bool(sk)
        and ak != PLACEHOLDER_AK
        and sk != PLACEHOLDER_SK
    )
    print("ok" if ok else "missing")
    return 0


def cmd_install_deps(_args: argparse.Namespace) -> int:
    req = SCRIPTS_DIR / "requirements.txt"
    if not req.exists():
        print(json.dumps({"error": "requirements.txt not found", "path": str(req)}))
        return 1
    try:
        import requests  # noqa: F401
        import alibabacloud_oss_v2  # noqa: F401
    except ImportError:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
            cwd=str(SCRIPTS_DIR),
        )
        return r.returncode
    return 0


def cmd_run_task(args: argparse.Namespace) -> int:
    # Ensure imports resolve (client, ai, sign_sdk live alongside this file)
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    from client import ConsumeDeniedError, SkillClient

    params = DEFAULT_PARAMS
    if args.params_json:
        try:
            params = json.loads(args.params_json)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": "invalid --params JSON", "detail": str(e)}))
            return 1

    client = None
    try:
        client = SkillClient()

        def _on_async_submitted(tid: str) -> None:
            _save_submitted_checkpoint(args.task, args.input, tid)

        result = client.run_task(
            args.task, args.input, params, on_async_submitted=_on_async_submitted
        )
        if not isinstance(result, dict):
            fail = {
                "error": "invalid_result",
                "skill_status": "failed",
                "detail": repr(result),
                "agent_instruction": (
                    "Unexpected non-object result from the SDK. Treat as failure; "
                    "check logs and retry."
                ),
            }
            _print_json(_merge_pipeline_trace(fail, client, success=False))
            _save_task_record(_task_record_from_result(args.task, args.input, fail))
            return 1
        if _is_failed_cli_result(result):
            _print_json(_merge_pipeline_trace(result, client, success=False))
            _save_task_record(_task_record_from_result(args.task, args.input, result))
            return 1
        out = _success_envelope(args.task, result)
        _print_json(_merge_pipeline_trace(out, client, success=True))
        _save_task_record(_task_record_from_result(args.task, args.input, out))
    except ConsumeDeniedError as e:
        fail = _envelope_consume_denied(e, args.task)
        if client is not None:
            _merge_pipeline_trace(fail, client, success=False)
        _print_json(fail)
        _save_task_record(_task_record_from_result(args.task, args.input, fail))
        return 1
    except Exception as e:
        err: dict = {"error": str(e), "skill_status": "failed"}
        if client is not None:
            _merge_pipeline_trace(err, client, success=False)
        _print_json(err)
        _save_task_record(
            _task_record_from_result(
                args.task, args.input, None, error_message=str(e)
            )
        )
        return 1
    return 0


def cmd_query_task(args: argparse.Namespace) -> int:
    """Resume polling by task_id (no upload, no consume)."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    from client import SkillClient

    task_label = (args.task or "").strip() or "query_task"
    client = None
    try:
        client = SkillClient()
        result = client.poll_task_status(args.task_id)
        if not isinstance(result, dict):
            fail = {
                "error": "invalid_result",
                "skill_status": "failed",
                "detail": repr(result),
                "agent_instruction": (
                    "Unexpected non-object result from poll_task_status. Treat as failure."
                ),
            }
            _print_json(_merge_pipeline_trace(fail, client, success=False))
            _save_task_record(_task_record_from_result(task_label, "", fail))
            return 1
        if _is_failed_cli_result(result):
            _print_json(_merge_pipeline_trace(result, client, success=False))
            _save_task_record(
                _task_record_from_result(task_label, "", result)
            )
            return 1
        out = _success_envelope(task_label, result, resume=True)
        _print_json(_merge_pipeline_trace(out, client, success=True))
        _save_task_record(_task_record_from_result(task_label, "", out))
    except Exception as e:
        err = {"error": str(e), "skill_status": "failed"}
        if client is not None:
            _merge_pipeline_trace(err, client, success=False)
        _print_json(err)
        _save_task_record(
            _task_record_from_result(task_label, "", None, error_message=str(e))
        )
        return 1
    return 0


def cmd_spawn_run_task(args: argparse.Namespace) -> int:
    task = (args.task or "").strip()
    if not _is_video_task(task):
        _print_json(
            {
                "error": "spawn_video_tasks_only",
                "skill_status": "failed",
                "detail": (
                    "spawn-run-task accepts only video task_name: "
                    f"{sorted(VIDEO_TASKS)}. For eraser_watermark and image_restoration, "
                    "use run-task in the main session (SKILL.md §3a)."
                ),
                "task_name": task,
                "agent_instruction": (
                    "Use run-task (blocking) for image tasks; spawn-run-task is only for "
                    "videoscreenclear and hdvideoallinone."
                ),
            }
        )
        return 1
    payload = build_spawn_run_task(
        task=task,
        input_src=args.input,
        params_json=getattr(args, "params_json", "") or "",
        deliver_to=getattr(args, "deliver_to", None),
        deliver_channel=getattr(args, "deliver_channel", None),
        run_timeout_seconds=args.run_timeout_seconds,
    )
    _print_json(payload)
    return 0


def cmd_last_task(_args: argparse.Namespace) -> int:
    if not LAST_TASK_FILE.is_file():
        _print_json({"message": "No saved task yet.", "record": None})
        return 0
    try:
        with open(LAST_TASK_FILE, encoding="utf-8") as f:
            record = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _print_json({"error": "failed to read last_task.json", "detail": str(e)})
        return 1
    _print_json(record)
    return 0


def cmd_history(_args: argparse.Namespace) -> int:
    _ensure_state_dir()
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(HISTORY_DIR.glob("task_*.json"))
    jobs: list = []
    for path in files[-50:]:
        try:
            with open(path, encoding="utf-8") as f:
                jobs.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    _print_json({"jobs": jobs, "count": len(jobs)})
    return 0


def cmd_resolve_input(args: argparse.Namespace) -> int:
    try:
        import requests
    except ImportError:
        _print_json(
            {
                "error": "requests not installed",
                "install_command": "pip install -r scripts/requirements.txt",
            }
        )
        return 1

    out_dir = Path(args.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    file_bytes: bytes | None = None
    filename = "input.bin"

    if getattr(args, "file", None):
        p = Path(args.file).expanduser()
        if not p.is_file():
            _print_json({"error": f"File not found: {args.file}"})
            return 1
        max_b = skill_config.url_download_max_bytes()
        if p.stat().st_size > max_b:
            _print_json(
                {"error": "File too large", "max_bytes": max_b}
            )
            return 1
        file_bytes = p.read_bytes()
        filename = p.name

    elif getattr(args, "url", None):
        url = args.url.strip()
        if not url.startswith(("http://", "https://")):
            _print_json({"error": "Only http:// and https:// URLs are allowed"})
            return 1
        url_to = skill_config.url_download_timeout_tuple()
        r = requests.get(
            url,
            stream=True,
            timeout=url_to,
            headers={
                "User-Agent": getattr(
                    skill_config, "USER_AGENT", "action-web-skill-v1.2.1"
                )
            },
        )
        if r.status_code != 200:
            _print_json({"error": f"Download failed: HTTP {r.status_code}"})
            return 1
        chunks: list[bytes] = []
        total = 0
        max_b = skill_config.url_download_max_bytes()
        for chunk in r.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > max_b:
                _print_json({"error": "Downloaded file too large", "max_bytes": max_b})
                return 1
            chunks.append(chunk)
        file_bytes = b"".join(chunks)
        url_path = url.split("?")[0]
        ext_from_url = (
            url_path.rsplit(".", 1)[-1].lower() if "." in url_path else ""
        )
        if ext_from_url in (
            "jpg",
            "jpeg",
            "png",
            "webp",
            "gif",
            "mp4",
            "mov",
            "webm",
        ):
            extension = "jpg" if ext_from_url == "jpeg" else ext_from_url
        else:
            ct = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            extension = {
                "image/jpeg": "jpg",
                "image/png": "png",
                "image/webp": "webp",
                "video/mp4": "mp4",
                "video/quicktime": "mov",
            }.get(ct, "bin")
        filename = f"download_{uuid.uuid4().hex[:8]}.{extension}"

    elif getattr(args, "telegram_file_id", None):
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            _print_json(
                {
                    "error": "TELEGRAM_BOT_TOKEN not set",
                    "hint": "Never pass bot tokens as CLI args (visible in ps).",
                }
            )
            return 1
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": args.telegram_file_id},
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            _print_json({"error": "Telegram getFile failed", "detail": data})
            return 1
        file_path = data["result"]["file_path"]
        ext_from_path = (
            file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "jpg"
        )
        extension = (
            ext_from_path
            if ext_from_path
            in ("jpg", "jpeg", "png", "webp", "gif", "mp4", "mov", "webm")
            else "jpg"
        )
        filename = f"tg_{uuid.uuid4().hex[:8]}.{extension}"
        dl_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        r2 = requests.get(
            dl_url,
            timeout=skill_config.url_download_timeout_tuple(),
            headers={
                "User-Agent": getattr(
                    skill_config, "USER_AGENT", "action-web-skill-v1.2.1"
                )
            },
        )
        r2.raise_for_status()
        file_bytes = r2.content
        max_b = skill_config.url_download_max_bytes()
        if len(file_bytes) > max_b:
            _print_json(
                {"error": "Telegram file too large", "max_bytes": max_b}
            )
            return 1

    elif getattr(args, "feishu_image_key", None):
        if not args.feishu_message_id:
            _print_json(
                {"error": "--feishu-message-id required with --feishu-image-key"}
            )
            return 1
        feishu_token = (
            args.feishu_app_token or os.environ.get("FEISHU_APP_TOKEN", "")
        ).strip()
        if not feishu_token:
            _print_json(
                {"error": "FEISHU_APP_TOKEN or --feishu-app-token required"}
            )
            return 1
        r = requests.get(
            f"https://open.feishu.cn/open-apis/im/v1/messages/"
            f"{args.feishu_message_id}/resources/{args.feishu_image_key}",
            params={"type": "image"},
            headers={"Authorization": f"Bearer {feishu_token}"},
            timeout=skill_config.url_download_timeout_tuple(),
        )
        if r.status_code != 200:
            _print_json(
                {"error": f"Feishu download failed: HTTP {r.status_code}"}
            )
            return 1
        file_bytes = r.content
        max_b = skill_config.url_download_max_bytes()
        if len(file_bytes) > max_b:
            _print_json(
                {"error": "Feishu resource too large", "max_bytes": max_b}
            )
            return 1
        extension = "jpg"
        ct = r.headers.get("Content-Type", "")
        if "png" in ct:
            extension = "png"
        elif "webp" in ct:
            extension = "webp"
        filename = f"feishu_{uuid.uuid4().hex[:8]}.{extension}"

    else:
        _print_json(
            {
                "error": "Provide one of: --file, --url, --telegram-file-id, "
                "--feishu-image-key (+ --feishu-message-id)",
            }
        )
        return 1

    dest = out_dir / f"kaipai_in_{uuid.uuid4().hex[:10]}_{filename}"
    dest.write_bytes(file_bytes)  # type: ignore[arg-type]
    _print_json(
        {
            "path": str(dest.resolve()),
            "filename": filename,
            "bytes": len(file_bytes),  # type: ignore[arg-type]
        }
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Kaipai skill CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("preflight", help="Print ok or missing (AK/SK)")
    p_pre.set_defaults(func=cmd_preflight)

    p_dep = sub.add_parser("install-deps", help="Install requirements if needed")
    p_dep.set_defaults(func=cmd_install_deps)

    p_run = sub.add_parser("run-task", help="Run algorithm task")
    p_run.add_argument("--task", required=True, help="task_name e.g. eraser_watermark")
    p_run.add_argument(
        "--input", required=True, help="Image or video URL or local path (must match --task modality)"
    )
    p_run.add_argument(
        "--params",
        dest="params_json",
        default="",
        help='Optional JSON object for invoke params (default: {"parameter":{"rsp_media_type":"url"}})',
    )
    p_run.set_defaults(func=cmd_run_task)

    p_query = sub.add_parser(
        "query-task",
        help="Resume async status polling by task_id (no re-upload; same AK/SK as submit)",
    )
    p_query.add_argument(
        "--task-id",
        required=True,
        dest="task_id",
        help="Full task id from a previous run-task / failure JSON (task_id or data.result.id)",
    )
    p_query.add_argument(
        "--task",
        default="",
        help="Optional label for task_name in success JSON (default: query_task)",
    )
    p_query.set_defaults(func=cmd_query_task)

    p_spawn = sub.add_parser(
        "spawn-run-task",
        help=(
            "Build sessions_spawn payload for video tasks only "
            "(videoscreenclear, hdvideoallinone); image tasks use run-task"
        ),
    )
    p_spawn.add_argument(
        "--task",
        required=True,
        help="Video task_name only: videoscreenclear or hdvideoallinone",
    )
    p_spawn.add_argument("--input", required=True, help="Video URL or local path")
    p_spawn.add_argument(
        "--params",
        dest="params_json",
        default="",
        help="Optional JSON for --params (same as run-task)",
    )
    p_spawn.add_argument(
        "--deliver-to",
        default=None,
        help="Feishu oc_/ou_, Telegram chat_id, Discord channel_id, etc.",
    )
    p_spawn.add_argument(
        "--deliver-channel",
        default=None,
        help="feishu, telegram, discord, or other",
    )
    p_spawn.add_argument(
        "--run-timeout-seconds",
        type=int,
        default=SPAWN_DEFAULT_TIMEOUT_SECONDS,
        help=(
            f"sessions_spawn runTimeoutSeconds (default {SPAWN_DEFAULT_TIMEOUT_SECONDS}; "
            "do not reduce without accepting timeout risk)"
        ),
    )
    p_spawn.set_defaults(func=cmd_spawn_run_task)

    p_last = sub.add_parser("last-task", help="Show last run-task/query-task record JSON")
    p_last.set_defaults(func=cmd_last_task)

    sub.add_parser("history", help="List recent task records (up to 50)").set_defaults(
        func=cmd_history
    )

    p_res = sub.add_parser(
        "resolve-input",
        help="Download IM attachment / URL to a local path for --input",
    )
    p_res.add_argument("--file", help="Local file path (copy into output dir with unique name)")
    p_res.add_argument("--url", help="HTTP(S) URL to download")
    p_res.add_argument(
        "--telegram-file-id",
        dest="telegram_file_id",
        help="Telegram file_id (requires TELEGRAM_BOT_TOKEN)",
    )
    p_res.add_argument(
        "--feishu-message-id",
        dest="feishu_message_id",
        default="",
        help="Feishu message id (with --feishu-image-key)",
    )
    p_res.add_argument(
        "--feishu-image-key",
        dest="feishu_image_key",
        help="Feishu image resource key",
    )
    p_res.add_argument(
        "--feishu-app-token",
        dest="feishu_app_token",
        default="",
        help="Feishu tenant token (or set FEISHU_APP_TOKEN)",
    )
    p_res.add_argument(
        "--output-dir",
        default="/tmp",
        help="Directory for downloaded file (default: /tmp)",
    )
    p_res.set_defaults(func=cmd_resolve_input)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
