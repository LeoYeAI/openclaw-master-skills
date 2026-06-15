"""获取子部门列表

用法: python scripts/list_sub_departments.py "<deptId>"
根部门 deptId = 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_sub_departments.py \"<deptId>\"，根部门为 1"}})
        sys.exit(1)

    dept_id = int(args[0])

    try:
        token = get_access_token()
        print("正在获取子部门列表...", file=sys.stderr)
        result = top_api_request("POST", "/topapi/v2/department/listsub", token, json_body={"dept_id": dept_id})
        sub_ids = [d.get("dept_id") for d in (result.get("result") or [])]
        output({"success": True, "deptId": dept_id, "subDepartmentIds": sub_ids})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
