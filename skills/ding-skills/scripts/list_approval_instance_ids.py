"""获取审批实例 ID 列表

用法: python scripts/list_approval_instance_ids.py "<processCode>" --startTime <timestamp> --endTime <timestamp> [--size 20] [--nextToken "xxx"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"process_code": None, "start_time": 0, "end_time": 0, "size": 20, "next_token": None}
    i = 1
    while i < len(argv):
        if argv[i] == "--startTime" and i + 1 < len(argv):
            args["start_time"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--endTime" and i + 1 < len(argv):
            args["end_time"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--size" and i + 1 < len(argv):
            args["size"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--nextToken" and i + 1 < len(argv):
            args["next_token"] = argv[i + 1]
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--") and args["process_code"] is None:
            args["process_code"] = argv[i]
            i += 1
        else:
            i += 1
    return args


def main():
    args = parse_args(sys.argv)
    if not args["process_code"] or not args["start_time"] or not args["end_time"]:
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/list_approval_instance_ids.py \"<processCode>\" --startTime <timestamp> --endTime <timestamp> [--size 20] [--nextToken \"xxx\"]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在查询审批实例ID列表...", file=sys.stderr)

        body = {
            "processCode": args["process_code"],
            "startTime": args["start_time"],
            "endTime": args["end_time"],
            "size": args["size"],
        }
        if args["next_token"]:
            body["nextToken"] = args["next_token"]

        result = api_request("POST", "/workflow/processInstances/ids", token, json_body=body)
        r = result.get("result", {})
        instance_ids = r.get("list", [])
        output({
            "success": True,
            "processCode": args["process_code"],
            "instanceIds": instance_ids,
            "totalCount": len(instance_ids),
            "hasMore": bool(r.get("nextToken")),
            "nextToken": r.get("nextToken"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
