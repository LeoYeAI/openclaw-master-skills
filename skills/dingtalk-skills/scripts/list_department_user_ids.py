"""获取部门用户 ID 列表

用法: python scripts/list_department_user_ids.py "<deptId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_department_user_ids.py \"<deptId>\""}})
        sys.exit(1)

    dept_id = int(args[0])

    try:
        token = get_access_token()
        print("正在获取部门用户ID列表...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/user/listid", token, json_body={"dept_id": dept_id})
        output({"success": True, "deptId": dept_id, "userIds": result.get("result", {}).get("userid_list", [])})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
