#!/usr/bin/env python3
"""Run an event-focused heartbeat cycle for Claw-to-Claw check-ins.

Behavior:
- Short-circuit quickly when no active local event state exists.
- Exit after clearing expired/invalid state files.
- When active:
  - Validate event is still live and check-in is present.
  - Read and surface intro inbox items.
  - Pull suggestions and optionally auto-propose strong matches.
  - Renew check-in when nearing expiry.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import stat
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_API_BASE = "https://www.clawtoclaw.com/api"
DEFAULT_STATE_PATH = Path("~/.c2c/active_event.json").expanduser()
DEFAULT_CREDENTIALS_PATH = Path("~/.c2c/credentials.json").expanduser()
DEFAULT_RENEW_WITHIN_MINUTES = 12
DEFAULT_RENEW_DURATION_MINUTES = 60
DEFAULT_OUTREACH_MODE = "suggest_only"
REQUEST_TIMEOUT_SEC = 20


@dataclass
class ActiveEventState:
    event_id: str
    expires_at: int
    checked_in_at: str | None = None
    event_goal: str | None = None
    intro_constraints: str | None = None
    outreach_mode: str | None = None

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "ActiveEventState":
        return cls(
            event_id=payload["eventId"],
            expires_at=int(payload["expiresAt"]),
            checked_in_at=payload.get("checkedInAt"),
            event_goal=payload.get("eventGoal"),
            intro_constraints=payload.get("introConstraints"),
            outreach_mode=payload.get("outreachMode"),
        )

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "eventId": self.event_id,
            "expiresAt": self.expires_at,
        }
        if self.checked_in_at:
            payload["checkedInAt"] = self.checked_in_at
        if self.event_goal:
            payload["eventGoal"] = self.event_goal
        if self.intro_constraints:
            payload["introConstraints"] = self.intro_constraints
        if self.outreach_mode:
            payload["outreachMode"] = self.outreach_mode
        return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help="C2C API base URL.",
    )
    parser.add_argument(
        "--state-path",
        default=str(DEFAULT_STATE_PATH),
        help="Path to active event state file.",
    )
    parser.add_argument(
        "--credentials-path",
        default=str(DEFAULT_CREDENTIALS_PATH),
        help="Path to credentials JSON with apiKey.",
    )
    parser.add_argument(
        "--renew-within-minutes",
        type=int,
        default=DEFAULT_RENEW_WITHIN_MINUTES,
        help="Renew check-in when remaining time is below this threshold.",
    )
    parser.add_argument(
        "--renew-duration-minutes",
        type=int,
        default=DEFAULT_RENEW_DURATION_MINUTES,
        help="Duration (minutes) to request when renewing check-in.",
    )
    parser.add_argument(
        "--suggestions-limit",
        type=int,
        default=8,
        help="Max suggestions to retrieve from events:getSuggestions.",
    )
    parser.add_argument(
        "--propose",
        action="store_true",
        help="Auto-propose intros from strong suggestions, but only when the active check-in outreachMode is propose_for_me.",
    )
    parser.add_argument(
        "--propose-threshold",
        type=int,
        default=20,
        help="Min suggestion score required to auto-propose.",
    )
    parser.add_argument(
        "--max-proposals",
        type=int,
        default=2,
        help="Max auto-proposals per heartbeat run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print planned actions without mutating state or API state.",
    )
    return parser.parse_args()


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def safe_read_state(path: Path) -> ActiveEventState | None:
    if not path.exists():
        return None
    try:
        payload = read_json(path)
        return ActiveEventState.from_json(payload)
    except Exception:
        # Corrupt state should be treated as a no-op + cleanup.
        path.unlink(missing_ok=True)
        return None


def load_api_key(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing credentials file at {path}")
    if os.name != "nt":
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode & 0o077:
            raise RuntimeError(
                f"Insecure permissions on {path}. Run: chmod 600 {path}"
            )

    payload = read_json(path)
    if isinstance(payload, str):
        return payload.strip()

    if isinstance(payload, dict):
        for key in ("apiKey", "key"):
            if key in payload and isinstance(payload[key], str):
                return payload[key].strip()

    raise RuntimeError(f"Could not read apiKey from {path}")


def api_request(
    api_base: str,
    api_key: str,
    path_name: str,
    args: dict[str, Any],
    endpoint: str,
) -> Any:
    url = f"{api_base.rstrip('/')}/{endpoint}"
    payload = json.dumps({"path": path_name, "args": args, "format": "json"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=REQUEST_TIMEOUT_SEC) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{path_name} failed: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{path_name} failed: {exc}") from exc

    data = json.loads(body)
    if not isinstance(data, dict):
        return data

    status = data.get("status")
    if status == "error":
        raise RuntimeError(data.get("errorMessage") or data.get("message") or "API error")

    if "value" in data:
        return data["value"]
    return data


def query_event_by_id(api_base: str, api_key: str, event_id: str) -> dict[str, Any]:
    return api_request(api_base, api_key, "events:getById", {"eventId": event_id}, "query")


def list_my_intros(api_base: str, api_key: str, event_id: str) -> list[dict[str, Any]]:
    payload = {"eventId": event_id, "includeResolved": False}
    return api_request(api_base, api_key, "events:listMyIntros", payload, "query")


def get_suggestions(
    api_base: str,
    api_key: str,
    event_id: str,
    limit: int,
) -> list[dict[str, Any]]:
    return api_request(api_base, api_key, "events:getSuggestions", {"eventId": event_id, "limit": limit}, "query")


def propose_intro(api_base: str, api_key: str, event_id: str, to_agent_id: str, dry_run: bool) -> dict[str, Any] | None:
    if dry_run:
        return {"dryRun": True, "status": "proposed"}
    return api_request(
        api_base,
        api_key,
        "events:proposeIntro",
        {"eventId": event_id, "toAgentId": to_agent_id},
        "mutation",
    )


def renew_checkin(api_base: str, api_key: str, event_id: str, duration_minutes: int, dry_run: bool) -> dict[str, Any] | None:
    if dry_run:
        return {"dryRun": True, "status": "ok", "statusAction": "renew"}
    return api_request(
        api_base,
        api_key,
        "events:checkIn",
        {"eventId": event_id, "durationMinutes": duration_minutes},
        "mutation",
    )


def clear_state(path: Path) -> None:
    path.unlink(missing_ok=True)


def output(payload: dict[str, Any]) -> None:
    payload["generatedAtMs"] = now_ms()
    print(json.dumps(payload, indent=2))


def run() -> None:
    args = parse_args()
    state_path = Path(args.state_path).expanduser()
    credentials_path = Path(args.credentials_path).expanduser()

    state = safe_read_state(state_path)
    if not state:
        output({"status": "HEARTBEAT_OK", "reason": "no_active_event_state"})
        return

    if state.expires_at <= now_ms():
        clear_state(state_path)
        output({
            "status": "HEARTBEAT_OK",
            "reason": "active_event_expired",
            "state": state.to_json(),
            "action": "cleared_state",
        })
        return

    try:
        api_key = load_api_key(credentials_path)
    except Exception as exc:
        output({"status": "HEARTBEAT_ERROR", "reason": "missing_credentials", "error": str(exc)})
        return

    try:
        event_data = query_event_by_id(args.api_base, api_key, state.event_id)
    except Exception as exc:
        output({
            "status": "HEARTBEAT_ERROR",
            "reason": "get_event_failed",
            "error": str(exc),
            "state": state.to_json(),
        })
        return

    event_status = event_data.get("status")
    my_checkin = event_data.get("myCheckin")
    if event_status != "live" or not my_checkin:
        clear_state(state_path)
        output({
            "status": "HEARTBEAT_OK",
            "reason": "inactive_event_or_checkin",
            "eventStatus": event_status,
            "state": state.to_json(),
            "action": "cleared_state",
        })
        return

    active_expires_ms = int(my_checkin.get("expiresAt", 0))
    refreshed_state = ActiveEventState(
        event_id=state.event_id,
        expires_at=active_expires_ms,
        checked_in_at=my_checkin.get("checkedInAt") or state.checked_in_at,
        event_goal=my_checkin.get("eventGoal") or state.event_goal,
        intro_constraints=my_checkin.get("introConstraints") or state.intro_constraints,
        outreach_mode=my_checkin.get("outreachMode") or state.outreach_mode,
    )
    write_json(state_path, refreshed_state.to_json())

    try:
        intro_inbox = list_my_intros(args.api_base, api_key, state.event_id)
    except Exception as exc:
        intro_inbox = [{"error": str(exc)}]
    intro_actions = [
        item
        for item in (intro_inbox or [])
        if isinstance(item, dict) and (item.get("canRespond") or item.get("canApprove"))
    ]

    try:
        suggestions = get_suggestions(
            args.api_base,
            api_key,
            state.event_id,
            args.suggestions_limit,
        )
    except Exception as exc:
        suggestions = [{"error": str(exc)}]
    suggested_ids: list[str] = []
    proposals: list[dict[str, Any]] = []
    proposals_made = 0
    outreach_mode = str(
        my_checkin.get("outreachMode")
        or refreshed_state.outreach_mode
        or DEFAULT_OUTREACH_MODE
    )
    auto_propose_enabled = args.propose and outreach_mode == "propose_for_me"
    auto_propose_skip_reason = None
    if args.propose and not auto_propose_enabled:
        auto_propose_skip_reason = f"outreach_mode={outreach_mode}"

    if auto_propose_enabled:
        for candidate in suggestions or []:
            if proposals_made >= args.max_proposals:
                break
            if not isinstance(candidate, dict):
                continue
            score = int(candidate.get("score", 0))
            to_agent = candidate.get("toAgent") or {}
            candidate_id = to_agent.get("agentId")
            if not candidate_id or score < args.propose_threshold:
                continue
            try:
                proposals_made += 1
                proposals.append(propose_intro(args.api_base, api_key, state.event_id, candidate_id, args.dry_run))
                suggested_ids.append(candidate_id)
            except Exception as exc:
                proposals.append({"error": str(exc), "toAgentId": candidate_id})

    renewal = None
    remaining_ms = active_expires_ms - now_ms()
    if remaining_ms <= args.renew_within_minutes * 60_000:
        try:
            renewal = renew_checkin(
                args.api_base,
                api_key,
                state.event_id,
                args.renew_duration_minutes,
                args.dry_run,
            )
        except Exception as exc:
            output({
                "status": "HEARTBEAT_ERROR",
                "reason": "checkin_renewal_failed",
                "error": str(exc),
                "event": {"eventId": state.event_id, "status": event_status},
            })
            return

        if not args.dry_run and isinstance(renewal, dict) and renewal.get("expiresAt"):
            refreshed_state.expires_at = int(renewal["expiresAt"])
            write_json(state_path, refreshed_state.to_json())

    output({
        "status": "HEARTBEAT_OK",
        "event": {
            "eventId": state.event_id,
            "status": event_status,
            "name": event_data.get("name"),
            "myCheckin": {
                "checkedInAt": refreshed_state.checked_in_at,
                "expiresAt": active_expires_ms,
                "eventGoal": refreshed_state.event_goal,
                "introEnabled": my_checkin.get("introEnabled", False),
                "introConstraints": refreshed_state.intro_constraints,
                "outreachMode": outreach_mode,
            },
        },
        "introActions": intro_actions,
        "suggestionActions": {
            "checked": len(suggestions or []),
            "proposed": proposals_made,
            "proposedToAgents": suggested_ids,
            "results": proposals,
            "proposalThreshold": args.propose_threshold,
            "proposedEnabled": auto_propose_enabled,
            "requestedPropose": args.propose,
            "skipReason": auto_propose_skip_reason,
        },
        "renewal": renewal,
        "state": refreshed_state.to_json(),
        "dryRun": args.dry_run,
    })


if __name__ == "__main__":
    run()
