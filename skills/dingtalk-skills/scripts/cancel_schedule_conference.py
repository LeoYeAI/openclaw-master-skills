"""取消预约会议

用法: python scripts/cancel_schedule_conference.py "<scheduleConferenceId>" "<创建人unionId>"
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
                "message": "用法: python scripts/cancel_schedule_conference.py \"<scheduleConferenceId>\" \"<创建人unionId>\"",
            }
        })
        sys.exit(1)

    schedule_conference_id = sys.argv[1]
    creator_union_id = sys.argv[2]

    try:
        token = get_access_token()
        print("正在取消预约会议...", file=sys.stderr)

        body = {
            "scheduleConferenceId": schedule_conference_id,
            "creatorUnionId": creator_union_id,
        }
        api_request("POST", "/conference/scheduleConferences/cancel", token, json_body=body)
        output({
            "success": True,
            "scheduleConferenceId": schedule_conference_id,
            "message": "预约会议已取消",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
