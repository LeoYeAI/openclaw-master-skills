"""执行审批任务（同意/拒绝）

用法: python scripts/execute_approval_task.py "<instanceId>" "<userId>" "<agree|refuse>" [--taskId "xxx"] [--remark "审批意见"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def parse_args(argv):
    args = {"instance_id": None, "user_id": None, "result": None, "task_id": None, "remark": None}
    positional = []
    i = 1
    while i < len(argv):
        if argv[i] == "--taskId" and i + 1 < len(argv):
            args["task_id"] = argv[i + 1]
            i += 2
        elif argv[i] == "--remark" and i + 1 < len(argv):
            args["remark"] = argv[i + 1]
            i += 2
        elif argv[i] == "--debug":
            i += 1
        elif not argv[i].startswith("--"):
            positional.append(argv[i])
            i += 1
        else:
            i += 1
    if len(positional) >= 1:
        args["instance_id"] = positional[0]
    if len(positional) >= 2:
        args["user_id"] = positional[1]
    if len(positional) >= 3:
        args["result"] = positional[2]
    return args


def main():
    args = parse_args(sys.argv)
    if not all([args["instance_id"], args["user_id"], args["result"]]):
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/execute_approval_task.py \"<instanceId>\" \"<userId>\" \"<agree|refuse>\" [--taskId \"xxx\"] [--remark \"审批意见\"]"}})
        sys.exit(1)

    if args["result"] not in ("agree", "refuse"):
        output({"success": False, "error": {"code": "INVALID_RESULT", "message": "审批结果必须是 agree（同意）或 refuse（拒绝）"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在执行审批任务...", file=sys.stderr)

        body = {
            "processInstanceId": args["instance_id"],
            "actionerUserId": args["user_id"],
            "result": args["result"],
            "remark": args["remark"] or "",
        }
        if args["task_id"]:
            body["taskId"] = args["task_id"]

        result = api_request("POST", "/workflow/processInstances/tasks/execute", token, json_body=body)
        output({
            "success": result.get("result", {}).get("success", False),
            "instanceId": args["instance_id"],
            "userId": args["user_id"],
            "action": args["result"],
            "message": "已同意审批" if args["result"] == "agree" else "已拒绝审批",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
