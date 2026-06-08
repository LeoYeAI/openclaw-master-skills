# Workflow Patterns

## 1. Linear Pipeline

Steps chained via `depends_on`:

```json
{
  "steps": [
    {
      "id": "fetch",
      "action": "http.get",
      "params": { "url": "${{inputs.url}}" }
    },
    {
      "id": "hash",
      "action": "crypto.hash",
      "depends_on": ["fetch"],
      "params": {
        "data": "${{steps.fetch.output.body}}",
        "algorithm": "sha256"
      }
    },
    {
      "id": "save",
      "action": "fs.write",
      "depends_on": ["hash"],
      "params": {
        "path": "/tmp/result.txt",
        "content": "${{steps.hash.output.hash}}"
      }
    }
  ]
}
```

## 2. Conditional Branching

Route based on CEL expression:

```json
{
  "steps": [
    {
      "id": "route",
      "type": "condition",
      "config": {
        "expression": "inputs.env",
        "branches": {
          "prod": [
            {
              "id": "deploy",
              "action": "shell.exec",
              "params": { "command": "deploy.sh", "args": ["prod"] }
            }
          ],
          "staging": [
            {
              "id": "test",
              "action": "shell.exec",
              "params": { "command": "test.sh" }
            }
          ]
        },
        "default": [
          {
            "id": "dry-run",
            "action": "shell.exec",
            "params": { "command": "echo", "args": ["dry run"] }
          }
        ]
      }
    }
  ]
}
```

## 3. For-Each Loop

Iterate over a collection:

```json
{
  "steps": [
    {
      "id": "process-items",
      "type": "loop",
      "config": {
        "mode": "for_each",
        "over": "[\"alpha\",\"beta\",\"gamma\"]",
        "max_iter": 100,
        "body": [
          {
            "id": "hash",
            "action": "crypto.hash",
            "params": { "data": "${{loop.item}}", "algorithm": "sha256" }
          }
        ]
      }
    }
  ]
}
```

## 4. Parallel Fan-Out

Execute branches concurrently:

```json
{
  "steps": [
    {
      "id": "health-checks",
      "type": "parallel",
      "config": {
        "mode": "all",
        "branches": [
          [
            {
              "id": "check-api",
              "action": "http.get",
              "params": { "url": "${{inputs.api_url}}/health" }
            }
          ],
          [
            {
              "id": "check-db",
              "action": "shell.exec",
              "params": { "command": "pg_isready" }
            }
          ],
          [
            {
              "id": "check-cache",
              "action": "http.get",
              "params": { "url": "${{inputs.cache_url}}/ping" }
            }
          ]
        ]
      }
    }
  ]
}
```

Use `"mode": "race"` to complete when the first branch finishes.

## 5. Human-in-the-Loop Approval

Reasoning node for agent decision:

```json
{
  "steps": [
    {
      "id": "analyze",
      "action": "http.get",
      "params": { "url": "${{inputs.target_url}}" }
    },
    {
      "id": "approve",
      "type": "reasoning",
      "depends_on": ["analyze"],
      "config": {
        "prompt_context": "Review analysis results and decide whether to proceed with deployment",
        "data_inject": { "analysis": "steps.analyze.output" },
        "options": [
          { "id": "approve", "description": "Proceed with deployment" },
          { "id": "reject", "description": "Cancel deployment" },
          { "id": "modify", "description": "Modify parameters and retry" }
        ],
        "timeout": "1h",
        "fallback": "reject"
      }
    },
    {
      "id": "deploy",
      "action": "shell.exec",
      "depends_on": ["approve"],
      "condition": "steps.approve.output.choice == 'approve'",
      "params": { "command": "deploy.sh" }
    }
  ]
}
```

## 6. Error Recovery with Fallback

Retry + fallback step for graceful degradation:

```json
{
  "steps": [
    {
      "id": "primary",
      "action": "http.get",
      "params": { "url": "${{inputs.primary_url}}" },
      "retry": { "max": 2, "backoff": "exponential", "delay": "1s" },
      "on_error": { "strategy": "fallback_step", "fallback_step": "backup" }
    },
    {
      "id": "backup",
      "action": "http.get",
      "params": { "url": "${{inputs.backup_url}}" }
    }
  ]
}
```

## 7. Sub-Workflow Composition

Parent workflow calls a child template:

```json
{
  "steps": [
    {
      "id": "prepare",
      "action": "crypto.uuid",
      "params": {}
    },
    {
      "id": "run-pipeline",
      "action": "workflow.run",
      "depends_on": ["prepare"],
      "params": {
        "template_name": "data-pipeline",
        "version": "v1",
        "params": {
          "source": "${{inputs.data_source}}",
          "run_id": "${{steps.prepare.output.uuid}}"
        }
      }
    }
  ]
}
```

## 8. Nested Flow Control

Parallel branches containing loops:

```json
{
  "steps": [
    {
      "id": "parallel-process",
      "type": "parallel",
      "config": {
        "mode": "all",
        "branches": [
          [
            {
              "id": "batch-a",
              "type": "loop",
              "config": {
                "mode": "for_each",
                "over": "[\"x\",\"y\",\"z\"]",
                "max_iter": 10,
                "body": [
                  {
                    "id": "hash",
                    "action": "crypto.hash",
                    "params": { "data": "${{loop.item}}" }
                  }
                ]
              }
            }
          ],
          [{ "id": "generate-id", "action": "crypto.uuid", "params": {} }]
        ]
      }
    }
  ]
}
```

## 9. Complete MCP Lifecycle

Full define -> run -> status -> signal -> status flow:

### Step 1: Define template

```json
// opcode.define
{
  "name": "approval-flow",
  "agent_id": "my-agent",
  "definition": {
    "steps": [
      {
        "id": "check",
        "action": "http.get",
        "params": { "url": "${{inputs.url}}" }
      },
      {
        "id": "decide",
        "type": "reasoning",
        "depends_on": ["check"],
        "config": {
          "prompt_context": "Review data and approve",
          "options": [
            { "id": "approve", "description": "Approve" },
            { "id": "reject", "description": "Reject" }
          ],
          "timeout": "30m",
          "fallback": "reject"
        }
      }
    ]
  }
}
// Returns: { "name": "approval-flow", "version": "v1" }
```

### Step 2: Run workflow

```json
// opcode.run
{
  "template_name": "approval-flow",
  "agent_id": "my-agent",
  "params": { "url": "https://api.example.com/data" }
}
// Returns: { "status": "suspended", "workflow_id": "abc-123", ... }
```

### Step 3: Check status

```json
// opcode.status
{ "workflow_id": "abc-123" }
// Returns: { "status": "suspended", "steps": { "decide": { "status": "suspended" } } }
```

### Step 4: Resolve decision

```json
// opcode.signal
{
  "workflow_id": "abc-123",
  "signal_type": "decision",
  "step_id": "decide",
  "payload": { "choice": "approve" },
  "agent_id": "my-agent",
  "reasoning": "Data looks correct"
}
// Returns: { "ok": true }
```

### Step 5: Verify completion

```json
// opcode.status
{ "workflow_id": "abc-123" }
// Returns: { "status": "completed", "output": {...} }
```

## 10. Scripting with shell.exec

`shell.exec` supports any language. Scripts receive input via **stdin** and produce output via **stdout**. JSON stdout is **auto-parsed**.

**Convention**: stdin=JSON, stdout=JSON, stderr=errors, non-zero exit=failure. Use `stdout_raw` for unprocessed text.

| Language | Command   | Args                  | Boilerplate                                                 |
| -------- | --------- | --------------------- | ----------------------------------------------------------- |
| Bash     | `bash`    | `["script.sh"]`       | `set -euo pipefail; input=$(cat -)`                         |
| Python   | `python3` | `["script.py"]`       | `json.load(sys.stdin)` -> `json.dump(result, sys.stdout)`   |
| Node     | `node`    | `["script.js"]`       | Read stdin stream -> `JSON.parse` -> `JSON.stringify`       |
| Go       | `go`      | `["run","script.go"]` | `json.NewDecoder(os.Stdin)` -> `json.NewEncoder(os.Stdout)` |

Scripts that output JSON can chain with `${{steps.X.output.stdout.field}}`.

### Bash

```bash
#!/usr/bin/env bash
set -euo pipefail
input=$(cat -)
name=$(echo "$input" | jq -r '.name')
echo "{\"greeting\": \"hello ${name}\"}"
```

```json
{
  "id": "greet",
  "action": "shell.exec",
  "params": {
    "command": "bash",
    "args": ["scripts/greet.sh"],
    "stdin": "${{steps.fetch.output.body}}"
  }
}
```

### Python

```python
#!/usr/bin/env python3
import sys, json
data = json.load(sys.stdin)
result = {"total": sum(data["values"]), "count": len(data["values"])}
json.dump(result, sys.stdout)
```

```json
{
  "id": "summarize",
  "action": "shell.exec",
  "params": {
    "command": "python3",
    "args": ["scripts/summarize.py"],
    "stdin": "${{steps.fetch.output.body}}"
  }
}
```

### Node.js

```javascript
#!/usr/bin/env node
let input = "";
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const data = JSON.parse(input);
  const result = { ids: data.items.map((i) => i.id) };
  process.stdout.write(JSON.stringify(result));
});
```

```json
{
  "id": "extract-ids",
  "action": "shell.exec",
  "params": {
    "command": "node",
    "args": ["scripts/extract.js"],
    "stdin": "${{steps.fetch.output.body}}"
  }
}
```

### Go

```go
package main

import (
    "encoding/json"
    "os"
)

func main() {
    var data map[string]any
    json.NewDecoder(os.Stdin).Decode(&data)
    result := map[string]any{"processed": true, "source": data["name"]}
    json.NewEncoder(os.Stdout).Encode(result)
}
```

```json
{
  "id": "process",
  "action": "shell.exec",
  "params": {
    "command": "go",
    "args": ["run", "scripts/process.go"],
    "stdin": "${{steps.fetch.output.body}}"
  }
}
```

### Chaining script output

Since JSON stdout is auto-parsed, the next step accesses fields directly:

```json
{
  "id": "use-result",
  "action": "http.post",
  "depends_on": ["greet"],
  "params": {
    "url": "${{inputs.api_url}}",
    "body": { "message": "${{steps.greet.output.stdout.greeting}}" }
  }
}
```

Use `${{steps.X.output.stdout_raw}}` when you need the raw string (e.g., for non-JSON text or when preserving exact formatting).
