"""删除日程

用法: python scripts/delete_event.py "<用户unionId>" "<eventId>" [--push-notification]
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
                "message": "用法: python scripts/delete_event.py \"<用户unionId>\" \"<eventId>\" [--push-notification]",
            }
        })
        sys.exit(1)

    union_id = sys.argv[1]
    event_id = sys.argv[2]
    push_notification = "--push-notification" in sys.argv

    try:
        token = get_access_token()
        print("正在删除日程...", file=sys.stderr)

        params = {}
        if push_notification:
            params["pushNotification"] = "true"

        api_request(
            "DELETE",
            f"/calendar/users/{union_id}/calendars/primary/events/{event_id}",
            token,
            params=params,
        )
        output({
            "success": True,
            "eventId": event_id,
            "message": "日程已删除",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
