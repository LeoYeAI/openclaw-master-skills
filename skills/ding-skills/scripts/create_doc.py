"""在知识库中创建文档

用法: python scripts/create_doc.py "<workspaceId>" "<文档名>" "<操作人unionId>" ["<docType>"]
docType 默认为 alidoc（钉钉文档），可选：alidoc, alinote, alisheet
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 3:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/create_doc.py \"<workspaceId>\" \"<文档名>\" \"<操作人unionId>\" [\"<docType>\"]"}})
        sys.exit(1)

    workspace_id = args[0]
    doc_name = args[1]
    operator_id = args[2]
    doc_type = args[3] if len(args) >= 4 else "alidoc"

    try:
        token = get_access_token()
        print(f"正在创建文档: {doc_name}...", file=sys.stderr)
        result = api_request("POST", f"/doc/workspaces/{workspace_id}/docs", token, json_body={
            "name": doc_name,
            "docType": doc_type,
            "operatorId": operator_id,
        })
        output({
            "success": True,
            "name": doc_name,
            "docType": doc_type,
            "workspaceId": result.get("workspaceId", workspace_id),
            "nodeId": result.get("nodeId"),
            "docKey": result.get("docKey"),
            "url": result.get("url"),
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
