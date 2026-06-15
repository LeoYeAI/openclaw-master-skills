"""查询日程列表

用法: python scripts/list_events.py "<用户unionId>" [--time-min "2026-03-01 00:00"] [--time-max "2026-03-31 23:59"] [--max-results 50] [--next-token "xxx"]
"""

import sys
import os
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output

CST = timezone(timedelta(hours=8))


def parse_time_to_iso(time_str):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(time_str, fmt)
            dt = dt.replace(tzinfo=CST)
            return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        except ValueError:
            continue
    return time_str


def parse_args(argv):
    args = {"union_id": None, "time_min": None, "time_max": None, "max_results": None, "next_token": None}
    positional = []
    i = 1
    while i < len(argv):
        if argv[i] == "--time-min" and i + 1 < len(argv):
            args["time_min"] = parse_time_to_iso(argv[i + 1])
            i += 2
        elif argv[i] == "--time-max" and i + 1 < len(argv):
            args["time_max"] = parse_time_to_iso(argv[i + 1])
            i += 2
        elif argv[i] == "--max-results" and i + 1 < len(argv):
            args["max_results"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--next-token" and i + 1 < len(argv):
            args["next_token"] = argv[i + 1]
            i += 2
        else:
            positional.append(argv[i])
            i += 1
    if positional:
        args["union_id"] = positional[0]
    return args


def main():
    args = parse_args(sys.argv)
    if not args["union_id"]:
        output({
            "success": False,
            "error": {
                "code": "INVALID_ARGS",
                "message": "用法: python scripts/list_events.py \"<用户unionId>\" [--time-min \"...\"] [--time-max \"...\"] [--max-results 50]",
            }
        })
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在查询日程列表...", file=sys.stderr)

        params = {}
        if args["time_min"]:
            params["timeMin"] = args["time_min"]
        if args["time_max"]:
            params["timeMax"] = args["time_max"]
        if args["max_results"]:
            params["maxResults"] = args["max_results"]
        if args["next_token"]:
            params["nextToken"] = args["next_token"]

        result = api_request(
            "GET",
            f"/calendar/users/{args['union_id']}/calendars/primary/events",
            token,
            params=params,
        )

        events = result.get("events", [])
        output({
            "success": True,
            "totalCount": len(events),
            "nextToken": result.get("nextToken"),
            "events": [{
                "id": e.get("id"),
                "summary": e.get("summary"),
                "start": e.get("start"),
                "end": e.get("end"),
                "status": e.get("status"),
                "isAllDay": e.get("isAllDay"),
                "onlineMeetingInfo": e.get("onlineMeetingInfo"),
            } for e in events],
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
