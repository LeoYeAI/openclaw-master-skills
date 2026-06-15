"""移除日程参与者

用法: python scripts/remove_event_attendee.py "<用户unionId>" "<eventId>" "<参与者unionId1,unionId2,...>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    if len(sys.argv) < 4:
        output({
            "success": False,
            "error": {
                "code": "INVALID_ARGS",
                "message": "用法: python scripts/remove_event_attendee.py \"<用户unionId>\" \"<eventId>\" \"<参与者unionId1,unionId2,...>\"",
            }
        })
        sys.exit(1)

    union_id = sys.argv[1]
    event_id = sys.argv[2]
    attendee_ids = sys.argv[3].split(",")

    try:
        token = get_access_token()
        print("正在移除参与者...", file=sys.stderr)

        body = {
            "attendeesToRemove": [{"id": aid} for aid in attendee_ids],
        }
        api_request(
            "POST",
            f"/calendar/users/{union_id}/calendars/primary/events/{event_id}/attendees/batchRemove",
            token,
            json_body=body,
        )
        output({
            "success": True,
            "eventId": event_id,
            "removedCount": len(attendee_ids),
            "message": f"已移除 {len(attendee_ids)} 位参与者",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
