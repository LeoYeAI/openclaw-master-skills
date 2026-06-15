"""查询离职记录列表

用法: python scripts/list_resigned_users.py "<startTime>" ["<endTime>"] [--nextToken "xxx"] [--maxResults 100]
startTime/endTime 格式: ISO8601 (如 2024-01-15T00:00:00+08:00)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"start_time": None, "end_time": None, "next_token": None, "max_results": 100}
    positional = []
    i = 1
    while i < len(argv):
        if argv[i] == "--nextToken" and i + 1 < len(argv):
            args["next_token"] = argv[i + 1]
            i += 2
        elif argv[i] == "--maxResults" and i + 1 < len(argv):
            args["max_results"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--"):
            positional.append(argv[i])
            i += 1
        else:
            i += 1
    if len(positional) >= 1:
        args["start_time"] = positional[0]
    if len(positional) >= 2:
        args["end_time"] = positional[1]
    return args


def main():
    args = parse_args(sys.argv)
    if not args["start_time"]:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_resigned_users.py \"<startTime>\" [\"<endTime>\"] [--nextToken \"xxx\"] [--maxResults 100]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在查询离职记录...", file=sys.stderr)

        params = {"startTime": args["start_time"], "maxResults": str(args["max_results"])}
        if args["end_time"]:
            params["endTime"] = args["end_time"]
        if args["next_token"]:
            params["nextToken"] = args["next_token"]

        result = api_request("GET", "/contact/empLeaveRecords", token, params=params)
        output({
            "success": True,
            "startTime": args["start_time"],
            "endTime": args["end_time"],
            "records": result.get("records", []),
            "nextToken": result.get("nextToken"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
