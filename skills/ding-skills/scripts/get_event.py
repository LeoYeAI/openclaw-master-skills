"""查询日程详情

用法: python scripts/get_event.py "<用户unionId>" "<eventId>"
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
                "message": "用法: python scripts/get_event.py \"<用户unionId>\" \"<eventId>\"",
            }
        })
        sys.exit(1)

    union_id = sys.argv[1]
    event_id = sys.argv[2]

    try:
        token = get_access_token()
        print("正在查询日程详情...", file=sys.stderr)

        result = api_request(
            "GET",
            f"/calendar/users/{union_id}/calendars/primary/events/{event_id}",
            token,
        )

        output({
            "success": True,
            "event": {
                "id": result.get("id"),
                "summary": result.get("summary"),
                "description": result.get("description"),
                "start": result.get("start"),
                "end": result.get("end"),
                "status": result.get("status"),
                "isAllDay": result.get("isAllDay"),
                "location": result.get("location"),
                "organizer": result.get("organizer"),
                "attendees": result.get("attendees"),
                "onlineMeetingInfo": result.get("onlineMeetingInfo"),
                "recurrence": result.get("recurrence"),
                "createTime": result.get("createTime"),
                "updateTime": result.get("updateTime"),
            },
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
