#!/usr/bin/env python3
"""Manage C2C active event state for heartbeat workflows."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STATE_PATH = Path("~/.c2c/active_event.json").expanduser()


@dataclass
class EventState:
    event_id: str
    expires_at: int
    checked_in_at: str
    event_goal: str | None = None
    intro_constraints: str | None = None
    outreach_mode: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventState":
        return cls(
            event_id=data["eventId"],
            expires_at=int(data["expiresAt"]),
            checked_in_at=data.get("checkedInAt")
            or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            event_goal=data.get("eventGoal"),
            intro_constraints=data.get("introConstraints"),
            outreach_mode=data.get("outreachMode"),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "eventId": self.event_id,
            "expiresAt": self.expires_at,
            "checkedInAt": self.checked_in_at,
        }
        if self.event_goal:
            payload["eventGoal"] = self.event_goal
        if self.intro_constraints:
            payload["introConstraints"] = self.intro_constraints
        if self.outreach_mode:
            payload["outreachMode"] = self.outreach_mode
        return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=str(DEFAULT_STATE_PATH), help="State file path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    set_cmd = subparsers.add_parser("set", help="Persist active event state")
    set_cmd.add_argument("--event-id", required=True, help="Event ID")
    set_cmd.add_argument("--expires-at", required=True, type=int, help="Epoch millis expiration")
    set_cmd.add_argument("--checked-in-at", help="ISO timestamp, defaults to now")
    set_cmd.add_argument("--event-goal", help="Short summary of what the human wants from the event")
    set_cmd.add_argument("--intro-constraints", help="Hard nos or logistics for event intros")
    set_cmd.add_argument(
        "--outreach-mode",
        choices=("suggest_only", "propose_for_me"),
        help="Whether the agent should only suggest matches or can proactively propose intros",
    )

    status_cmd = subparsers.add_parser("status", help="Read active event state")
    status_cmd.add_argument("--now-ms", type=int, help="Override current epoch millis")
    status_cmd.add_argument("--clear-expired", action="store_true", help="Delete file when expired")

    subparsers.add_parser("clear", help="Delete active event state")

    return parser.parse_args()


def get_now_ms(now_ms: int | None = None) -> int:
    if now_ms is not None:
        return now_ms
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def read_state(path: Path) -> EventState:
    data = json.loads(path.read_text(encoding="utf-8"))
    return EventState.from_dict(data)


def write_state(path: Path, state: EventState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2))


def run_set(args: argparse.Namespace, path: Path) -> None:
    checked_in_at = args.checked_in_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state = EventState(
        event_id=args.event_id,
        expires_at=args.expires_at,
        checked_in_at=checked_in_at,
        event_goal=args.event_goal,
        intro_constraints=args.intro_constraints,
        outreach_mode=args.outreach_mode,
    )
    write_state(path, state)
    print_json({"status": "ok", "path": str(path), "state": state.to_dict()})


def run_status(args: argparse.Namespace, path: Path) -> None:
    if not path.exists():
        print_json({"active": False, "reason": "missing_state_file", "path": str(path)})
        return

    state = read_state(path)
    now_ms = get_now_ms(args.now_ms)
    expired = state.expires_at <= now_ms

    if expired and args.clear_expired:
        path.unlink(missing_ok=True)

    print_json(
        {
            "active": not expired,
            "expired": expired,
            "path": str(path),
            "nowMs": now_ms,
            "state": state.to_dict(),
            "action": "cleared" if expired and args.clear_expired else "none",
        }
    )


def run_clear(path: Path) -> None:
    existed = path.exists()
    path.unlink(missing_ok=True)
    print_json({"status": "ok", "path": str(path), "deleted": existed})


def main() -> None:
    args = parse_args()
    path = Path(args.path).expanduser()

    if args.command == "set":
        run_set(args, path)
    elif args.command == "status":
        run_status(args, path)
    elif args.command == "clear":
        run_clear(path)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
