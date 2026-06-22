"""查询用户详情

用法: python scripts/get_user.py "<userId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    if len(sys.argv) < 2:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_user.py \"<userId>\""}})
        sys.exit(1)

    user_id = sys.argv[1]

    try:
        token = get_access_token()
        print("正在查询用户详情...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/user/get", token, json_body={
            "userid": user_id, "language": "zh_CN",
        })
        output({"success": True, "user": result.get("result", {})})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
