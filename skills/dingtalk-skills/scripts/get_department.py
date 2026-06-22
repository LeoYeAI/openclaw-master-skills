"""获取部门详情

用法: python scripts/get_department.py "<deptId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_department.py \"<deptId>\""}})
        sys.exit(1)

    dept_id = int(args[0])

    try:
        token = get_access_token()
        print("正在获取部门详情...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/department/get", token, json_body={"dept_id": dept_id})
        output({"success": True, "department": result.get("result", {})})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
