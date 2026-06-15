"""根据手机号查询用户

用法: python scripts/get_user_by_mobile.py "<手机号>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    if len(sys.argv) < 2:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_user_by_mobile.py \"<手机号>\""}})
        sys.exit(1)

    mobile = sys.argv[1]

    try:
        token = get_access_token()
        print("正在根据手机号查询用户...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/user/getbymobile", token, json_body={"mobile": mobile})
        output({"success": True, "mobile": mobile, "userId": result.get("result", {}).get("userid")})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
