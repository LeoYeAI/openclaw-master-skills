"""获取未登录钉钉的员工列表

用法: python scripts/list_inactive_users.py "<queryDate>" [--deptIds "id1,id2,..."] [--offset 0] [--size 100]
queryDate 格式: yyyyMMdd
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def parse_args(argv):
    args = {"query_date": None, "dept_ids": [], "offset": 0, "size": 100}
    i = 1
    while i < len(argv):
        if argv[i] == "--deptIds" and i + 1 < len(argv):
            args["dept_ids"] = [int(x.strip()) for x in argv[i + 1].split(",") if x.strip()]
            i += 2
        elif argv[i] == "--offset" and i + 1 < len(argv):
            args["offset"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--size" and i + 1 < len(argv):
            args["size"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--") and args["query_date"] is None:
            args["query_date"] = argv[i]
            i += 1
        else:
            i += 1
    return args


def main():
    args = parse_args(sys.argv)
    if not args["query_date"]:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_inactive_users.py \"<queryDate>\" [--deptIds \"id1,id2\"] [--offset 0] [--size 100]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在获取未登录用户列表...", file=sys.stderr)

        body = {"is_active": False, "query_date": args["query_date"], "offset": args["offset"], "size": args["size"]}
        if args["dept_ids"]:
            body["dept_ids"] = args["dept_ids"]

        result = top_api_request("POST", "/topapi/inactive/user/v2/get", token, json_body=body)
        r = result.get("result", {})
        output({
            "success": True,
            "queryDate": args["query_date"],
            "userIds": r.get("list", []),
            "hasMore": r.get("has_more", False),
            "nextOffset": (args["offset"] + args["size"]) if r.get("has_more") else None,
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
