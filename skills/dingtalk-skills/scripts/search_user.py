"""搜索用户

用法: python scripts/search_user.py "<搜索关键词>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    if len(sys.argv) < 2:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/search_user.py \"<搜索关键词>\""}})
        sys.exit(1)

    keyword = sys.argv[1]

    try:
        token = get_access_token()
        print("正在搜索用户...", file=sys.stderr)
        result = api_request("POST", "/contact/users/search", token, json_body={
            "queryWord": keyword, "offset": 0, "size": 20,
        })
        output({
            "success": True,
            "keyword": keyword,
            "totalCount": result.get("totalCount", 0),
            "hasMore": result.get("hasMore", False),
            "userIds": result.get("list", []),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
