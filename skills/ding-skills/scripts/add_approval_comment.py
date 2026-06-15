"""添加审批评论

用法: python scripts/add_approval_comment.py "<instanceId>" "<commentUserId>" "<评论内容>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 3:
        output({"success": False, "error": {"code": "INVALID_ARGS",
            "message": "用法: python scripts/add_approval_comment.py \"<instanceId>\" \"<commentUserId>\" \"<评论内容>\""}})
        sys.exit(1)

    instance_id = args[0]
    comment_user_id = args[1]
    text = args[2]

    try:
        token = get_access_token()
        print("正在添加审批评论...", file=sys.stderr)
        api_request("POST", "/workflow/processInstances/comments", token, json_body={
            "processInstanceId": instance_id,
            "commentUserId": comment_user_id,
            "text": text,
        })
        output({"success": True, "instanceId": instance_id, "userId": comment_user_id, "message": "评论已添加"})
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
