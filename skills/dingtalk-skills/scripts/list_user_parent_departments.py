"""获取用户所属部门的父部门链

用法: python scripts/list_user_parent_departments.py "<userId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_user_parent_departments.py \"<userId>\""}})
        sys.exit(1)

    user_id = args[0]

    try:
        token = get_access_token()
        print("正在获取用户所属部门父部门链...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/department/listparentbyuser", token, json_body={"userid": user_id})
        output({"success": True, "userId": user_id, "parentIdList": result.get("result", {}).get("parent_list", [])})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
