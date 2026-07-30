#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path


def load_json(path: str) -> object:
    if path == "-":
        try:
            return json.load(sys.stdin)
        except JSONDecodeError as exc:
            raise SystemExit(
                f"invalid JSON on stdin: {exc.msg} at line {exc.lineno} column {exc.colno}"
            ) from exc

    text = Path(path).read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"invalid JSON in {path}: file is empty")
    try:
        return json.loads(text)
    except JSONDecodeError as exc:
        raise SystemExit(
            f"invalid JSON in {path}: {exc.msg} at line {exc.lineno} column {exc.colno}"
        ) from exc


def write_text_atomic(path: str, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(output_path)


def emit_json(data: object, output_path: str | None = None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output_path:
        write_text_atomic(output_path, text)
        return
    sys.stdout.write(text)


def parse_events(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("events", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise SystemExit("input must be a JSON array or an object with `events`/`items`")


def parse_candidates(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        value = payload.get("candidates")
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    raise SystemExit("input must be a candidate array or an object with `candidates`")


def location_text(event: dict) -> str | None:
    location = event.get("location")
    if isinstance(location, str) and location.strip():
        return location.strip()
    if isinstance(location, dict):
        parts = []
        for key in ("name", "address"):
            value = location.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
        if parts:
            return " / ".join(parts)
    return None


def room_id_from_attendee(attendee: dict) -> str | None:
    for key in ("room_id", "attendee_id", "id"):
        value = attendee.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def room_name_from_attendee(attendee: dict, room_id: str) -> str:
    for key in ("name", "display_name", "resource_custom_name", "room_name", "title"):
        value = attendee.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return room_id


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_now(value: str | None) -> datetime:
    if value:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt.astimezone()
    return datetime.now().astimezone()


def format_dt(value: datetime) -> str:
    return value.astimezone().isoformat(timespec="seconds")


def load_state(path: str) -> dict | None:
    try:
        payload = load_json(path)
    except FileNotFoundError:
        return None
    if not isinstance(payload, dict):
        raise SystemExit("state file is not a JSON object")
    return payload


def choose_default_city(
    *,
    explicit_default_city: str | None,
    state_path: str,
    merged_payload: dict,
) -> str:
    if explicit_default_city and explicit_default_city.strip():
        return explicit_default_city.strip()

    state = load_state(state_path)
    if state:
        existing_default_city = state.get("default_city")
        if isinstance(existing_default_city, str) and existing_default_city.strip():
            return existing_default_city.strip()

    default_city_hint = merged_payload.get("default_city_hint")
    if isinstance(default_city_hint, str) and default_city_hint.strip():
        return default_city_hint.strip()

    location_hints = merged_payload.get("location_hints")
    if isinstance(location_hints, list):
        for item in location_hints:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()

    candidates = parse_candidates(merged_payload)
    for candidate in candidates:
        hints = candidate.get("location_hints")
        if not isinstance(hints, list):
            continue
        for hint in hints:
            if isinstance(hint, str) and hint.strip():
                return hint.strip()

    raise SystemExit("unable to choose default_city from state or candidate hints")


def build_candidate_result(
    *,
    event_count: int,
    rooms: dict[str, dict],
    all_locations: Counter[str],
) -> dict:
    candidates = []
    for room in rooms.values():
        names = room.pop("_names")
        locations = room.pop("_locations")
        display_name = names.most_common(1)[0][0] if names else room["room_id"]
        candidates.append(
            {
                "room_id": room["room_id"],
                "display_name": display_name,
                "score": room["score"],
                "last_seen_at": room["last_seen_at"],
                "location_hints": [name for name, _ in locations.most_common(5)],
            }
        )

    candidates.sort(
        key=lambda item: (
            int(item.get("score") or 0),
            item.get("last_seen_at") or "",
            item.get("display_name") or "",
        ),
        reverse=True,
    )

    default_city_hint = None
    if all_locations:
        default_city_hint = all_locations.most_common(1)[0][0]
    elif candidates:
        hints = candidates[0].get("location_hints")
        if isinstance(hints, list):
            for hint in hints:
                if isinstance(hint, str) and hint.strip():
                    default_city_hint = hint.strip()
                    break

    result = {
        "generated_at": iso_now(),
        "event_count": event_count,
        "candidate_count": len(candidates),
        "default_city_hint": default_city_hint,
        "location_hints": [
            {"name": name, "count": count}
            for name, count in all_locations.most_common(10)
        ],
        "default_order_room_ids": [item["room_id"] for item in candidates],
        "default_priority_preview": [
            {
                "rank": index,
                "room_id": item["room_id"],
                "display_name": item.get("display_name") or item["room_id"],
                "score": item.get("score", 0),
            }
            for index, item in enumerate(candidates, start=1)
        ],
        "candidates": candidates,
    }
    return result


def merge_candidate_payloads(payloads: list[object]) -> dict:
    merged_rooms: dict[str, dict] = {}
    merged_locations: Counter[str] = Counter()
    total_event_count = 0

    for payload in payloads:
        if not isinstance(payload, dict):
            raise SystemExit("merged inputs must be JSON objects")

        event_count = payload.get("event_count")
        if isinstance(event_count, int):
            total_event_count += event_count

        location_hints = payload.get("location_hints")
        if isinstance(location_hints, list):
            for item in location_hints:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                count = item.get("count")
                if isinstance(name, str) and name.strip():
                    merged_locations[name.strip()] += int(count or 0)

        for item in parse_candidates(payload):
            room_id = item.get("room_id")
            if not isinstance(room_id, str) or not room_id.strip():
                continue
            room_id = room_id.strip()
            entry = merged_rooms.setdefault(
                room_id,
                {
                    "room_id": room_id,
                    "score": 0,
                    "last_seen_at": None,
                    "_names": Counter(),
                    "_locations": Counter(),
                },
            )
            score = int(item.get("score") or 0)
            entry["score"] += score

            display_name = item.get("display_name")
            if isinstance(display_name, str) and display_name.strip():
                entry["_names"][display_name.strip()] += max(score, 1)

            hints = item.get("location_hints")
            if isinstance(hints, list):
                for hint in hints:
                    if isinstance(hint, str) and hint.strip():
                        entry["_locations"][hint.strip()] += max(score, 1)

            last_seen_at = item.get("last_seen_at")
            if isinstance(last_seen_at, str) and last_seen_at.strip():
                if entry["last_seen_at"] is None or last_seen_at > entry["last_seen_at"]:
                    entry["last_seen_at"] = last_seen_at

    return build_candidate_result(
        event_count=total_event_count,
        rooms=merged_rooms,
        all_locations=merged_locations,
    )


def build_state_payload(
    *,
    candidates: list[dict],
    default_city: str,
    room_ids: list[str] | None,
    top: int | None,
) -> dict:
    by_room_id = {item.get("room_id"): item for item in candidates if item.get("room_id")}

    selected = []
    if room_ids:
        missing = [room_id for room_id in room_ids if room_id not in by_room_id]
        if missing:
            raise SystemExit(f"unknown room_id(s): {', '.join(missing)}")
        for room_id in room_ids:
            selected.append(by_room_id[room_id])
    else:
        selected = list(candidates)

    if top is not None:
        selected = selected[:top]

    if not selected:
        raise SystemExit("no rooms selected")

    return {
        "version": 1,
        "default_city": default_city,
        "updated_at": iso_now(),
        "rooms": [
            {
                "room_id": item["room_id"],
                "display_name": item.get("display_name") or item["room_id"],
                "rank": index,
                "score": item.get("score", 0),
                "last_seen_at": item.get("last_seen_at"),
                "location_hints": item.get("location_hints", []),
            }
            for index, item in enumerate(selected, start=1)
        ],
    }


def merge_room_hints(existing: object, incoming: object) -> list[str]:
    merged: list[str] = []
    for source in (existing, incoming):
        if not isinstance(source, list):
            continue
        for item in source:
            if not isinstance(item, str):
                continue
            value = item.strip()
            if value and value not in merged:
                merged.append(value)
    return merged


def merge_last_seen(existing: object, incoming: object) -> str | None:
    values = []
    for item in (existing, incoming):
        if isinstance(item, str) and item.strip():
            values.append(item.strip())
    if not values:
        return None
    return max(values)


def build_incremental_state_payload(
    *,
    existing_state: dict | None,
    candidates: list[dict],
    default_city: str,
    top: int | None,
) -> tuple[dict, list[str], list[str]]:
    existing_rooms = []
    if existing_state:
        rooms = existing_state.get("rooms")
        if isinstance(rooms, list):
            existing_rooms = [item for item in rooms if isinstance(item, dict)]

    candidate_by_room_id = {
        item["room_id"]: item
        for item in candidates
        if isinstance(item, dict) and isinstance(item.get("room_id"), str) and item["room_id"].strip()
    }

    merged_rooms: list[dict] = []
    kept_room_ids: list[str] = []
    added_room_ids: list[str] = []

    for room in existing_rooms:
        room_id = room.get("room_id")
        if not isinstance(room_id, str) or not room_id.strip():
            continue
        room_id = room_id.strip()
        incoming = candidate_by_room_id.pop(room_id, None)
        merged_rooms.append(
            {
                "room_id": room_id,
                "display_name": (
                    incoming.get("display_name")
                    if incoming and isinstance(incoming.get("display_name"), str) and incoming.get("display_name").strip()
                    else room.get("display_name") or room_id
                ),
                "score": max(int(room.get("score") or 0), int((incoming or {}).get("score") or 0)),
                "last_seen_at": merge_last_seen(room.get("last_seen_at"), (incoming or {}).get("last_seen_at")),
                "location_hints": merge_room_hints(room.get("location_hints"), (incoming or {}).get("location_hints")),
            }
        )
        kept_room_ids.append(room_id)

    for candidate in candidates:
        room_id = candidate.get("room_id")
        if not isinstance(room_id, str) or not room_id.strip():
            continue
        room_id = room_id.strip()
        if room_id not in candidate_by_room_id:
            continue
        merged_rooms.append(
            {
                "room_id": room_id,
                "display_name": candidate.get("display_name") or room_id,
                "score": int(candidate.get("score") or 0),
                "last_seen_at": candidate.get("last_seen_at"),
                "location_hints": merge_room_hints([], candidate.get("location_hints")),
            }
        )
        added_room_ids.append(room_id)
        candidate_by_room_id.pop(room_id, None)

    if top is not None:
        merged_rooms = merged_rooms[:top]

    if not merged_rooms:
        raise SystemExit("no rooms selected")

    state = {
        "version": 1,
        "default_city": default_city,
        "updated_at": iso_now(),
        "rooms": [
            {
                "room_id": item["room_id"],
                "display_name": item.get("display_name") or item["room_id"],
                "rank": index,
                "score": item.get("score", 0),
                "last_seen_at": item.get("last_seen_at"),
                "location_hints": item.get("location_hints", []),
            }
            for index, item in enumerate(merged_rooms, start=1)
        ],
    }
    return state, kept_room_ids, added_room_ids


def write_state(path: str, payload: dict) -> None:
    write_text_atomic(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def cmd_extract(args: argparse.Namespace) -> int:
    events = parse_events(load_json(args.input))
    rooms: dict[str, dict] = {}
    all_locations: Counter[str] = Counter()

    for event in events:
        event_start = event.get("start_time")
        if not isinstance(event_start, str):
            event_start = None
        hint = location_text(event)
        if hint:
            all_locations[hint] += 1

        attendees = event.get("attendees")
        if not isinstance(attendees, list):
            continue

        for attendee in attendees:
            if not isinstance(attendee, dict):
                continue
            if attendee.get("type") != "resource":
                continue

            rsvp_status = attendee.get("rsvp_status")
            if isinstance(rsvp_status, str) and rsvp_status not in {"accept", ""}:
                continue

            room_id = room_id_from_attendee(attendee)
            if not room_id:
                continue

            entry = rooms.setdefault(
                room_id,
                {
                    "room_id": room_id,
                    "score": 0,
                    "last_seen_at": None,
                    "_names": Counter(),
                    "_locations": Counter(),
                },
            )
            entry["score"] += 1
            entry["_names"][room_name_from_attendee(attendee, room_id)] += 1
            if hint:
                entry["_locations"][hint] += 1
            if event_start and (
                entry["last_seen_at"] is None or event_start > entry["last_seen_at"]
            ):
                entry["last_seen_at"] = event_start

    result = build_candidate_result(
        event_count=len(events),
        rooms=rooms,
        all_locations=all_locations,
    )
    emit_json(result, args.output)
    return 0


def cmd_plan_refresh(args: argparse.Namespace) -> int:
    now = resolve_now(args.now)
    if args.mode == "default_refresh":
        start = now - timedelta(days=1)
        end = now + timedelta(days=7)
    elif args.mode == "init":
        start = now - timedelta(days=7)
        end = now + timedelta(days=7)
    elif args.mode == "full_rebuild":
        start = now - timedelta(days=20)
        end = now + timedelta(days=20) - timedelta(minutes=1)
    else:
        raise SystemExit(f"unknown mode: {args.mode}")

    slices: list[tuple[datetime, datetime]] = []
    current = start
    slice_delta = timedelta(days=args.slice_days)
    while current < end:
        next_time = min(current + slice_delta, end)
        slices.append((current, next_time))
        current = next_time

    pad = max(2, len(str(len(slices))))
    emit_json(
        {
            "generated_at": iso_now(),
            "mode": args.mode,
            "slice_days": args.slice_days,
            "window_start": format_dt(start),
            "window_end": format_dt(end),
            "slices": [
                {
                    "index": index,
                    "start_time": format_dt(slice_start),
                    "end_time": format_dt(slice_end),
                    "event_file": f"tmp/meeting-room-events-{index:0{pad}d}.json",
                    "candidate_file": f"tmp/meeting-room-candidates-{index:0{pad}d}.json",
                }
                for index, (slice_start, slice_end) in enumerate(slices, start=1)
            ],
        },
        args.output,
    )
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    result = merge_candidate_payloads([load_json(input_path) for input_path in args.input])
    emit_json(result, args.output)
    return 0


def cmd_finalize_refresh(args: argparse.Namespace) -> int:
    merged_payload = merge_candidate_payloads([load_json(input_path) for input_path in args.input])
    candidates = parse_candidates(merged_payload)
    if not candidates:
        raise SystemExit("no candidate rooms extracted")

    default_city = choose_default_city(
        explicit_default_city=args.default_city,
        state_path=args.state,
        merged_payload=merged_payload,
    )
    existing_state = load_state(args.state)
    if args.mode == "default_refresh":
        state, kept_room_ids, added_room_ids = build_incremental_state_payload(
            existing_state=existing_state,
            candidates=candidates,
            default_city=default_city,
            top=args.top,
        )
    else:
        state = build_state_payload(
            candidates=candidates,
            default_city=default_city,
            room_ids=None,
            top=args.top,
        )
        kept_room_ids = []
        added_room_ids = [room["room_id"] for room in state["rooms"]]
    write_state(args.state, state)
    emit_json(
        {
            "saved": True,
            "mode": args.mode,
            "state_path": args.state,
            "default_city": default_city,
            "event_count": merged_payload.get("event_count", 0),
            "candidate_count": len(candidates),
            "state_room_count": len(state["rooms"]),
            "added_room_ids": added_room_ids,
            "preserved_room_ids": kept_room_ids,
            "default_priority_preview": merged_payload.get("default_priority_preview", []),
            "state": state,
        },
        args.output,
    )
    return 0


def cmd_save(args: argparse.Namespace) -> int:
    candidates = parse_candidates(load_json(args.input))
    state = build_state_payload(
        candidates=candidates,
        default_city=args.default_city,
        room_ids=args.room_id,
        top=args.top,
    )
    write_state(args.state, state)
    emit_json(state, args.output)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    state = load_json(args.state)
    if args.json:
        emit_json(state, args.output)
        return 0

    if not isinstance(state, dict):
        raise SystemExit("state file is not a JSON object")

    rooms = state.get("rooms")
    if not isinstance(rooms, list):
        raise SystemExit("state file does not contain a room list")

    print(f"default_city: {state.get('default_city', '')}")
    print(f"updated_at: {state.get('updated_at', '')}")
    for room in rooms:
        if not isinstance(room, dict):
            continue
        line = (
            f"{room.get('rank', '?')}. {room.get('display_name', room.get('room_id', ''))} "
            f"({room.get('room_id', '')}) score={room.get('score', 0)}"
        )
        if room.get("last_seen_at"):
            line += f" last_seen_at={room['last_seen_at']}"
        print(line)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meeting room preference helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="extract room candidates from calendar events")
    extract.add_argument("--input", default="-", help="JSON file path or - for stdin")
    extract.add_argument("--output", help="write JSON output atomically to this file")
    extract.set_defaults(func=cmd_extract)

    plan_refresh = subparsers.add_parser(
        "plan-refresh",
        help="build a deterministic refresh plan with scan windows and temp file names",
    )
    plan_refresh.add_argument(
        "--mode",
        choices=["default_refresh", "init", "full_rebuild"],
        required=True,
        help="refresh mode",
    )
    plan_refresh.add_argument(
        "--now",
        help="override the current time with an ISO 8601 timestamp",
    )
    plan_refresh.add_argument(
        "--slice-days",
        type=int,
        default=2,
        help="slice size in days",
    )
    plan_refresh.add_argument("--output", help="write JSON output atomically to this file")
    plan_refresh.set_defaults(func=cmd_plan_refresh)

    merge = subparsers.add_parser("merge", help="merge candidate files from multiple small scans")
    merge.add_argument(
        "--input",
        action="append",
        required=True,
        help="candidate JSON file path; pass multiple times in scan order",
    )
    merge.add_argument("--output", help="write JSON output atomically to this file")
    merge.set_defaults(func=cmd_merge)

    finalize_refresh = subparsers.add_parser(
        "finalize-refresh",
        help="merge candidates, choose default city, and write refreshed state",
    )
    finalize_refresh.add_argument(
        "--input",
        action="append",
        required=True,
        help="candidate JSON file path; pass multiple times in scan order",
    )
    finalize_refresh.add_argument(
        "--mode",
        choices=["default_refresh", "init", "full_rebuild"],
        default="default_refresh",
        help="default_refresh merges into the existing state; init/full_rebuild replace it",
    )
    finalize_refresh.add_argument("--state", required=True, help="state file path")
    finalize_refresh.add_argument(
        "--default-city",
        help="override the automatically chosen default city",
    )
    finalize_refresh.add_argument(
        "--top",
        type=int,
        help="keep only the first N rooms after merging",
    )
    finalize_refresh.add_argument("--output", help="write JSON output atomically to this file")
    finalize_refresh.set_defaults(func=cmd_finalize_refresh)

    save = subparsers.add_parser("save", help="save confirmed room preferences")
    save.add_argument("--input", required=True, help="candidate JSON file path")
    save.add_argument("--state", required=True, help="state file path")
    save.add_argument("--default-city", required=True, help="default city label")
    save.add_argument(
        "--room-id",
        action="append",
        help="room id to keep, in final rank order; omit to save the extracted default order",
    )
    save.add_argument("--top", type=int, help="keep only the first N selected rooms")
    save.add_argument("--output", help="write JSON output atomically to this file")
    save.set_defaults(func=cmd_save)

    show = subparsers.add_parser("show", help="show saved room preferences")
    show.add_argument("--state", required=True, help="state file path")
    show.add_argument("--json", action="store_true", help="print raw JSON")
    show.add_argument("--output", help="write JSON output atomically to this file when --json is set")
    show.set_defaults(func=cmd_show)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
