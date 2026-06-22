"""获取用户待审批数量

用法: python scripts/get_user_todo_count.py "<userId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_user_todo_count.py \"<userId>\""}})
        sys.exit(1)

    user_id = args[0]

    try:
        token = get_access_token()
        print("正在查询用户待审批数量...", file=sys.stderr)
        result = api_request("GET", "/workflow/processes/todoTasks/numbers", token, params={"userId": user_id})
        output({"success": True, "userId": user_id, "count": result.get("result", {}).get("count", 0)})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
