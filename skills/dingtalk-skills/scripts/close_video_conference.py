"""关闭视频会议

用法: python scripts/close_video_conference.py "<conferenceId>" "<操作人unionId>"
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
                "message": "用法: python scripts/close_video_conference.py \"<conferenceId>\" \"<操作人unionId>\"",
            }
        })
        sys.exit(1)

    conference_id = sys.argv[1]
    union_id = sys.argv[2]

    try:
        token = get_access_token()
        print("正在关闭视频会议...", file=sys.stderr)

        body = {"unionId": union_id}
        api_request("DELETE", f"/conference/videoConferences/{conference_id}", token, json_body=body)
        output({
            "success": True,
            "conferenceId": conference_id,
            "message": "视频会议已关闭",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
