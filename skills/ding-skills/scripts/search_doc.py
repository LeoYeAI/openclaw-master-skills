"""根据文档名搜索知识库文档，返回文档链接

用法: python scripts/search_doc.py "<操作人unionId>" "<文档名关键词>" ["<workspaceId>"]
如果不指定 workspaceId，会搜索所有知识库
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def search_nodes(token, parent_node_id, operator_id, keyword):
    """递归搜索节点，按名称模糊匹配"""
    matched = []
    next_token = None
    while True:
        params = {"parentNodeId": parent_node_id, "operatorId": operator_id, "maxResults": 50}
        if next_token:
            params["nextToken"] = next_token
        result = api_request("GET", "/wiki/nodes", token, params=params, api_version="v2.0")
        node = result.get("node")
        if node:
            nodes = node if isinstance(node, list) else [node]
            for n in nodes:
                name = n.get("name", "")
                if keyword.lower() in name.lower():
                    matched.append(n)
                if n.get("hasChildren"):
                    matched.extend(search_nodes(token, n["nodeId"], operator_id, keyword))
        next_token = result.get("nextToken")
        if not next_token:
            break
    return matched


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 2:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/search_doc.py \"<操作人unionId>\" \"<文档名关键词>\" [\"<workspaceId>\"]"}})
        sys.exit(1)

    operator_id = args[0]
    keyword = args[1]
    workspace_id = args[2] if len(args) >= 3 else None

    try:
        token = get_access_token()
        print(f"正在搜索文档: {keyword}...", file=sys.stderr)

        root_nodes = []
        if workspace_id:
            params = {"operatorId": operator_id, "maxResults": 30}
            result = api_request("GET", "/wiki/workspaces", token, params=params, api_version="v2.0")
            ws = result.get("workspace")
            if ws:
                ws_list = ws if isinstance(ws, list) else [ws]
                for w in ws_list:
                    if w.get("workspaceId") == workspace_id:
                        root_nodes.append((w.get("rootNodeId"), w.get("name")))
                        break
            if not root_nodes:
                root_nodes.append((None, None))
        else:
            next_token = None
            while True:
                params = {"operatorId": operator_id, "maxResults": 30}
                if next_token:
                    params["nextToken"] = next_token
                result = api_request("GET", "/wiki/workspaces", token, params=params, api_version="v2.0")
                ws = result.get("workspace")
                if ws:
                    ws_list = ws if isinstance(ws, list) else [ws]
                    for w in ws_list:
                        root_nodes.append((w.get("rootNodeId"), w.get("name")))
                next_token = result.get("nextToken")
                if not next_token:
                    break

        all_matched = []
        for root_node_id, ws_name in root_nodes:
            if root_node_id:
                matched = search_nodes(token, root_node_id, operator_id, keyword)
                for m in matched:
                    m["workspaceName"] = ws_name
                all_matched.extend(matched)

        output({
            "success": True,
            "keyword": keyword,
            "totalCount": len(all_matched),
            "documents": [{
                "name": d.get("name"),
                "nodeId": d.get("nodeId"),
                "url": d.get("url"),
                "category": d.get("category"),
                "workspaceName": d.get("workspaceName"),
                "creatorId": d.get("creatorId"),
                "modifiedTime": d.get("modifiedTime"),
            } for d in all_matched],
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
