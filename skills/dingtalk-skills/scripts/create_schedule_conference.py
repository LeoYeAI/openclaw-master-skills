"""创建预约会议（通过日历 API 创建带视频会议的日程）

用法: python scripts/create_schedule_conference.py "<会议主题>" "<创建人unionId>" "<开始时间>" "<结束时间>" "[参会人unionId1,unionId2,...]" "[会议地点]"

时间格式: "2026-03-16 14:00" 或 ISO 8601
"""

import sys
import os
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output

CST = timezone(timedelta(hours=8))


def parse_time(time_str):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(time_str, fmt)
            dt = dt.replace(tzinfo=CST)
            return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        except ValueError:
            continue
    return time_str


def main():
    if len(sys.argv) < 5:
        output({
            "success": False,
            "error": {
                "code": "INVALID_ARGS",
                "message": "用法: python scripts/create_schedule_conference.py \"<主题>\" \"<创建人unionId>\" \"<开始时间>\" \"<结束时间>\" \"[参会人unionId1,unionId2,...]\" \"[会议地点]\"",
            }
        })
        sys.exit(1)

    title = sys.argv[1]
    creator_union_id = sys.argv[2]
    start_time = parse_time(sys.argv[3])
    end_time = parse_time(sys.argv[4])
    invite_union_ids = sys.argv[5].split(",") if len(sys.argv) > 5 else []
    location = sys.argv[6] if len(sys.argv) > 6 else ""

    try:
        token = get_access_token()
        print("正在创建预约会议...", file=sys.stderr)

        attendees = [{"id": uid, "isOptional": False} for uid in invite_union_ids]
        body = {
            "summary": title,
            "start": {"dateTime": start_time, "timeZone": "Asia/Shanghai"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Shanghai"},
            "isAllDay": False,
            "onlineMeetingInfo": {"type": "dingtalk"},
            "attendees": attendees,
        }
        if location:
            body["location"] = {"displayName": location}

        result = api_request(
            "POST",
            f"/calendar/users/{creator_union_id}/calendars/primary/events",
            token,
            json_body=body,
        )

        online_info = result.get("onlineMeetingInfo", {})
        resp_data = {
            "success": True,
            "title": title,
            "eventId": result.get("id"),
            "onlineMeetingUrl": online_info.get("extraInfo", {}).get("url", ""),
            "conferenceId": online_info.get("conferenceId", ""),
            "startTime": start_time,
            "endTime": end_time,
            "attendeeCount": len(invite_union_ids),
        }
        if location:
            resp_data["location"] = location
        output(resp_data)
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
