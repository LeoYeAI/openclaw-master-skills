"""获取群内机器人列表

用法: python scripts/get_bot_list.py "<openConversationId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/get_bot_list.py \"<openConversationId>\""}})
        sys.exit(1)

    open_conversation_id = args[0]

    try:
        token = get_access_token()
        print("正在获取群内机器人列表...", file=sys.stderr)
        result = api_request("POST", "/robot/getBotListInGroup", token, json_body={
            "openConversationId": open_conversation_id,
        })
        output({
            "success": True,
            "openConversationId": open_conversation_id,
            "botList": result.get("chatbotInstanceVOList", []),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
