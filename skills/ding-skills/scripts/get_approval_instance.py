"""获取审批实例详情

用法: python scripts/get_approval_instance.py "<instanceId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_approval_instance.py \"<instanceId>\""}})
        sys.exit(1)

    instance_id = args[0]

    try:
        token = get_access_token()
        print("正在查询审批实例详情...", file=sys.stderr)
        result = api_request("GET", "/workflow/processInstances", token, params={"processInstanceId": instance_id})
        output({"success": True, "instanceId": instance_id, "instance": result.get("result", {})})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
