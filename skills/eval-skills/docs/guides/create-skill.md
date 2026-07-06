# Creating a Custom Skill

This guide covers how to create a Skill that works with eval-skills.

## Skill Structure

Every Skill needs a `skill.json` metadata file:

```json
{
  "id": "my_skill",
  "name": "My Custom Skill",
  "version": "1.0.0",
  "description": "What this skill does",
  "tags": ["category1", "category2"],
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" }
    },
    "required": ["query"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "result": { "type": "string" }
    }
  },
  "adapterType": "subprocess",
  "entrypoint": "python3 skill.py",
  "metadata": {
    "author": "Your Name",
    "license": "MIT"
  }
}
```

## Adapter Types

### Subprocess (JSON-RPC 2.0)

The simplest way to create a Skill. Your script reads JSON-RPC from stdin and writes to stdout.

**Protocol:**
```
stdin:  {"jsonrpc": "2.0", "method": "invoke", "params": {...}, "id": 1}
stdout: {"jsonrpc": "2.0", "result": {...}, "id": 1}
```

**Python Template:**
```python
#!/usr/bin/env python3
import json
import sys

def invoke(params):
    query = params.get("query", "")
    # Your logic here
    return {"result": f"Processed: {query}"}

def healthcheck(params):
    return {"status": "healthy"}

def main():
    raw = sys.stdin.read()
    request = json.loads(raw)

    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    handlers = {"invoke": invoke, "healthcheck": healthcheck}
    handler = handlers.get(method)

    if handler:
        result = handler(params)
        response = {"jsonrpc": "2.0", "result": result, "id": req_id}
    else:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
            "id": req_id,
        }

    print(json.dumps(response))

if __name__ == "__main__":
    main()
```

### HTTP

For Skills exposed as HTTP services.

**skill.json:**
```json
{
  "adapterType": "http",
  "entrypoint": "http://localhost:3000/api/invoke"
}
```

**adapter.config.json:**
```json
{
  "type": "http",
  "baseUrl": "http://localhost:3000",
  "authType": "bearer",
  "authTokenEnvKey": "MY_SKILL_API_KEY",
  "timeoutMs": 15000
}
```

The HTTP adapter sends:
```
POST /api/invoke
Content-Type: application/json

{
  "skillId": "my_skill",
  "version": "1.0.0",
  "input": { "query": "hello" }
}
```

## Using Templates

Generate a skeleton with:

```bash
# Python subprocess skill
eval-skills create --name my_skill --from-template python_script

# HTTP skill
eval-skills create --name my_api --from-template http_request

# MCP tool skill
eval-skills create --name my_mcp --from-template mcp_tool
```

## Testing Your Skill

1. Create evaluation tasks in `tests/basic.eval.json`:

```json
[
  {
    "id": "test_001",
    "description": "Basic test",
    "inputData": { "query": "hello" },
    "expectedOutput": { "type": "contains", "keywords": ["hello"] },
    "evaluator": { "type": "contains" },
    "timeoutMs": 10000
  }
]
```

2. Run evaluation:

```bash
eval-skills eval --skills ./skills/my_skill/ --tasks ./skills/my_skill/tests/basic.eval.json
```

## Best Practices

1. **Always define input/output schemas** — helps with validation and documentation
2. **Add meaningful tags** — makes your Skill discoverable
3. **Handle errors gracefully** — return structured error responses
4. **Keep latency low** — aim for P95 < 5 seconds
5. **Write comprehensive evaluation tasks** — cover edge cases
6. **Version your Skill** — use semver for tracking changes
