"""查询用户抄送的审批实例

用法: python scripts/list_user_cc_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20] [--nextToken "xxx"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"user_id": None, "start_time": None, "end_time": None, "max_results": 20, "next_token": None}
    i = 1
    while i < len(argv):
        if argv[i] == "--startTime" and i + 1 < len(argv):
            args["start_time"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--endTime" and i + 1 < len(argv):
            args["end_time"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--maxResults" and i + 1 < len(argv):
            args["max_results"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--nextToken" and i + 1 < len(argv):
            args["next_token"] = argv[i + 1]
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--") and args["user_id"] is None:
            args["user_id"] = argv[i]
            i += 1
        else:
            i += 1
    return args


def main():
    args = parse_args(sys.argv)
    if not args["user_id"]:
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/list_user_cc_approvals.py \"<userId>\" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在查询用户抄送的审批...", file=sys.stderr)

        body = {"userId": args["user_id"], "maxResults": args["max_results"]}
        if args["start_time"]:
            body["startTime"] = args["start_time"]
        if args["end_time"]:
            body["endTime"] = args["end_time"]
        if args["next_token"]:
            body["nextToken"] = args["next_token"]

        result = api_request("POST", "/workflow/processInstances/userCc", token, json_body=body)
        instances = result.get("result", {}).get("list", [])
        output({
            "success": True,
            "userId": args["user_id"],
            "instances": instances,
            "totalCount": len(instances),
            "hasMore": bool(result.get("result", {}).get("nextToken")),
            "nextToken": result.get("result", {}).get("nextToken"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
