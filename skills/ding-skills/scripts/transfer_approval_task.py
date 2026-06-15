"""转交审批任务

用法: python scripts/transfer_approval_task.py "<instanceId>" "<userId>" "<transferToUserId>" [--taskId "xxx"] [--remark "转交原因"]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, top_api_request, handle_error, output


def parse_args(argv):
    args = {"instance_id": None, "user_id": None, "transfer_to": None, "task_id": None, "remark": None}
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
        args["transfer_to"] = positional[2]
    return args


def main():
    args = parse_args(sys.argv)
    if not all([args["instance_id"], args["user_id"], args["transfer_to"]]):
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/transfer_approval_task.py \"<instanceId>\" \"<userId>\" \"<transferToUserId>\" [--taskId \"xxx\"] [--remark \"转交原因\"]"}})
        sys.exit(1)

    try:
        token = get_access_token()
        print("正在转交审批任务...", file=sys.stderr)

        body = {
            "process_instance_id": args["instance_id"],
            "userid": args["user_id"],
            "transfer_to_userid": args["transfer_to"],
            "remark": args["remark"] or "转交审批任务",
        }
        if args["task_id"]:
            body["task_id"] = args["task_id"]

        top_api_request("POST", "/topapi/process/workrecord/task/transfer", token, json_body=body)
        output({
            "success": True,
            "instanceId": args["instance_id"],
            "userId": args["user_id"],
            "transferToUserId": args["transfer_to"],
            "message": "审批任务已转交",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
