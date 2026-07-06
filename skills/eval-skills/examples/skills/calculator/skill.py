#!/usr/bin/env python3
"""Calculator — JSON-RPC subprocess skill for eval-skills"""
import json
import sys
import math

def invoke(params):
    """Evaluate a math expression."""
    expression = params.get("expression", "")
    
    # Handle special operations
    if params.get("operation") == "reverse":
        return {"result": params.get("input", "")[::-1]}
    if params.get("operation") == "is_palindrome":
        s = params.get("input", "")
        return {"result": str(s == s[::-1]).lower()}
    
    # Handle factorial
    if expression.endswith("!"):
        try:
            n = int(expression[:-1])
            return {"result": str(math.factorial(n))}
        except ValueError:
            return {"result": "error: invalid factorial input"}
    
    # Evaluate math expression
    try:
        # Safe subset of operations
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expression):
            result = eval(expression)
            return {"result": str(result)}
        else:
            return {"result": "error: invalid characters in expression"}
    except Exception as e:
        return {"result": f"error: {e}"}

def healthcheck(params):
    return {"status": "healthy"}

def main():
    raw = sys.stdin.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }))
        return

    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    handlers = {"invoke": invoke, "healthcheck": healthcheck}
    handler = handlers.get(method)

    if handler is None:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
            "id": req_id
        }
    else:
        try:
            result = handler(params)
            response = {"jsonrpc": "2.0", "result": result, "id": req_id}
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": req_id
            }

    print(json.dumps(response))

if __name__ == "__main__":
    main()
