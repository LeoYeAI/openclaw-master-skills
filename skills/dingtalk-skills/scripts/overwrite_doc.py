"""覆写知识库文档内容（全量替换）

用法: python scripts/overwrite_doc.py "<workspaceId>" "<nodeId>" "<操作人unionId>" "<内容>"
注意：此操作会完全替换文档原有内容
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 4:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/overwrite_doc.py \"<workspaceId>\" \"<nodeId>\" \"<操作人unionId>\" \"<内容>\""}})
        sys.exit(1)

    workspace_id = args[0]
    node_id = args[1]
    operator_id = args[2]
    content = args[3]

    try:
        token = get_access_token()
        print("正在覆写文档内容...", file=sys.stderr)
        result = api_request("PUT", f"/doc/workspaces/{workspace_id}/docs/{node_id}/contents", token, json_body={
            "operatorId": operator_id,
            "content": content,
        })
        output({
            "success": True,
            "workspaceId": workspace_id,
            "nodeId": node_id,
            "message": "文档内容已覆写",
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
