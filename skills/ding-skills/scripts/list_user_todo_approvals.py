"""查询用户待审批的实例

用法: python scripts/list_user_todo_approvals.py "<userId>" [--maxResults 20] [--nextToken "xxx"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"user_id": None, "max_results": 20, "next_token": None}
    i = 1
    while i < len(argv):
        if argv[i] == "--maxResults" and i + 1 < len(argv):
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
            "message": "用法: python scripts/list_user_todo_approvals.py \"<userId>\" [--maxResults 20] [--nextToken \"xxx\"]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在查询用户待审批实例...", file=sys.stderr)

        body = {"userId": args["user_id"], "maxResults": args["max_results"]}
        if args["next_token"]:
            body["nextToken"] = args["next_token"]

        result = api_request("POST", "/workflow/processInstances/userTodo", token, json_body=body)
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
