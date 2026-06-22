"""获取部门用户详细信息（分页）

用法: python scripts/list_department_user_details.py "<deptId>" [--cursor 0] [--size 100]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def parse_args(argv):
    args = {"dept_id": None, "cursor": 0, "size": 100}
    i = 1
    while i < len(argv):
        if argv[i] == "--cursor" and i + 1 < len(argv):
            args["cursor"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--size" and i + 1 < len(argv):
            args["size"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--") and args["dept_id"] is None:
            args["dept_id"] = int(argv[i])
            i += 1
        else:
            i += 1
    return args


def main():
    args = parse_args(sys.argv)
    if args["dept_id"] is None:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_department_user_details.py \"<deptId>\" [--cursor 0] [--size 100]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在获取部门用户详情...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/user/list", token, json_body={
            "dept_id": args["dept_id"], "cursor": args["cursor"], "size": args["size"],
        })
        r = result.get("result", {})
        output({
            "success": True,
            "deptId": args["dept_id"],
            "users": r.get("list", []),
            "hasMore": r.get("has_more", False),
            "nextCursor": r.get("next_cursor"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
