"""撤销审批实例

用法: python scripts/terminate_approval_instance.py "<instanceId>" "<operatingUserId>" ["<remark>"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 2:
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/terminate_approval_instance.py \"<instanceId>\" \"<operatingUserId>\" [\"<remark>\"]"}})
        sys.exit(1)

    instance_id = args[0]
    operating_user_id = args[1]
    remark = args[2] if len(args) > 2 else ""

    try:
        token = get_access_token()
        print("正在撤销审批实例...", file=sys.stderr)

        body = {
            "processInstanceId": instance_id,
            "operatingUserId": operating_user_id,
            "remark": remark,
        }
        api_request("POST", "/workflow/processInstances/terminate", token, json_body=body)
        output({"success": True, "instanceId": instance_id, "message": "审批实例已撤销"})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
