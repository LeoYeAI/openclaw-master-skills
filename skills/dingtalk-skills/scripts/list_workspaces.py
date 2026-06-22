"""获取知识库列表

用法: python scripts/list_workspaces.py "<操作人unionId>"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 1:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/list_workspaces.py \"<操作人unionId>\""}})
        sys.exit(1)

    operator_id = args[0]

    try:
        token = get_access_token()
        print("正在获取知识库列表...", file=sys.stderr)
        workspaces = []
        next_token = None
        while True:
            params = {"operatorId": operator_id, "maxResults": 30}
            if next_token:
                params["nextToken"] = next_token
            result = api_request("GET", "/wiki/workspaces", token, params=params, api_version="v2.0")
            ws = result.get("workspace")
            if ws:
                if isinstance(ws, list):
                    workspaces.extend(ws)
                else:
                    workspaces.append(ws)
            next_token = result.get("nextToken")
            if not next_token:
                break
        output({
            "success": True,
            "totalCount": len(workspaces),
            "workspaces": [{"workspaceId": w.get("workspaceId"), "name": w.get("name"), "type": w.get("type"), "url": w.get("url"), "rootNodeId": w.get("rootNodeId")} for w in workspaces],
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
