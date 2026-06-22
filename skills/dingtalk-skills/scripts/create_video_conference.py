"""创建即时视频会议

用法: python scripts/create_video_conference.py "<会议主题>" "<发起人unionId>" "[邀请人unionId1,unionId2,...]"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    if len(sys.argv) < 3:
        output({
            "success": False,
            "error": {
                "code": "INVALID_ARGS",
                "message": "用法: python scripts/create_video_conference.py \"<会议主题>\" \"<发起人unionId>\" \"[邀请人unionId1,unionId2,...]\"",
            }
        })
        sys.exit(1)

    conf_title = sys.argv[1]
    user_id = sys.argv[2]
    invite_user_ids = sys.argv[3].split(",") if len(sys.argv) > 3 else []

    try:
        token = get_access_token()
        print("正在创建视频会议...", file=sys.stderr)

        body = {
            "userId": user_id,
            "confTitle": conf_title,
            "inviteCaller": True,
            "inviteUserIds": invite_user_ids,
        }

        result = api_request("POST", "/conference/videoConferences", token, json_body=body)
        output({
            "success": True,
            "title": conf_title,
            "conferenceId": result.get("conferenceId"),
            "conferencePassword": result.get("conferencePassword"),
            "hostPassword": result.get("hostPassword"),
            "phoneNumbers": result.get("phoneNumbers"),
            "externalLinkUrl": result.get("externalLinkUrl"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
