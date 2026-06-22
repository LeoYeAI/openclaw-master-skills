"""获取员工人数

用法: python scripts/get_user_count.py [--onlyActive]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    only_active = "--onlyActive" in sys.argv

    try:
        token = get_access_token()
        print("正在获取员工人数...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/user/count", token, json_body={"only_active": only_active})
        output({"success": True, "onlyActive": only_active, "count": result.get("result", {}).get("count", 0)})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
