"""获取部门用户列表（简略信息，自动分页）

用法: python scripts/list_department_users.py "<deptId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_department_users.py \"<deptId>\""}})
        sys.exit(1)

    dept_id = int(args[0])

    try:
        token = get_access_token()
        print("正在获取部门用户列表...", file=sys.stderr)

        all_users = []
        cursor = 0
        has_more = True
        while has_more:
            result = top_api_request("POST", "/topapi/v2/user/list", token, json_body={
                "dept_id": dept_id, "cursor": cursor, "size": 100,
            })
            r = result.get("result", {})
            for u in (r.get("list") or []):
                all_users.append({"userId": u.get("userid"), "name": u.get("name")})
            has_more = r.get("has_more", False)
            if has_more:
                cursor = r.get("next_cursor", 0)

        output({"success": True, "deptId": dept_id, "users": all_users})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
