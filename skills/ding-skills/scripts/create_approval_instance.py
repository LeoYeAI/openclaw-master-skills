"""发起审批实例

用法: python scripts/create_approval_instance.py "<processCode>" "<originatorUserId>" "<deptId>" '<formValuesJson>' [--ccList "user1,user2"]

formValuesJson 示例: '[{"name":"标题","value":"请假申请"}]'
"""

import sys
import os
import json as json_mod
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"process_code": None, "originator_user_id": None, "dept_id": None, "form_values_json": None, "cc_list": None}
    positional = []
    i = 1
    while i < len(argv):
        if argv[i] == "--ccList" and i + 1 < len(argv):
            args["cc_list"] = argv[i + 1]
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--"):
            positional.append(argv[i])
            i += 1
        else:
            i += 1
    if len(positional) >= 1:
        args["process_code"] = positional[0]
    if len(positional) >= 2:
        args["originator_user_id"] = positional[1]
    if len(positional) >= 3:
        args["dept_id"] = positional[2]
    if len(positional) >= 4:
        args["form_values_json"] = positional[3]
    return args


def main():
    args = parse_args(sys.argv)
    if not all([args["process_code"], args["originator_user_id"], args["dept_id"], args["form_values_json"]]):
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/create_approval_instance.py \"<processCode>\" \"<originatorUserId>\" \"<deptId>\" '<formValuesJson>' [--ccList \"user1,user2\"]"}})
        sys.exit(1)

    try:
        form_values = json_mod.loads(args["form_values_json"])
    except json_mod.JSONDecodeError:
        output({"success": False, "error": {"code": "INVALID_JSON", "message": "formValuesJson 参数不是有效的 JSON 字符串"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在发起审批实例...", file=sys.stderr)

        body = {
            "processCode": args["process_code"],
            "originatorUserId": args["originator_user_id"],
            "deptId": args["dept_id"],
            "formComponentValues": form_values,
        }
        if args["cc_list"]:
            body["ccList"] = args["cc_list"]

        result = api_request("POST", "/workflow/processInstances", token, json_body=body)
        output({
            "success": True,
            "processCode": args["process_code"],
            "originatorUserId": args["originator_user_id"],
            "instanceId": result.get("result", {}).get("processInstanceId", ""),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
