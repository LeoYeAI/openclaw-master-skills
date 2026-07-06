#!/usr/bin/env python3
"""my-first-skill — JSON-RPC subprocess skill"""
import json
import sys

def invoke(params):
    """Handle invoke method. Override this with your logic."""
    query = params.get("query", "")
    return {"result": f"Processed: {query}"}

def healthcheck(params):
    return {"status": "healthy"}

def main():
    raw = sys.stdin.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}))
        return

    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    handlers = {"invoke": invoke, "healthcheck": healthcheck}
    handler = handlers.get(method)

    if handler is None:
        response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {method}"}, "id": req_id}
    else:
        try:
            result = handler(params)
            response = {"jsonrpc": "2.0", "result": result, "id": req_id}
        except Exception as e:
            response = {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}, "id": req_id}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
