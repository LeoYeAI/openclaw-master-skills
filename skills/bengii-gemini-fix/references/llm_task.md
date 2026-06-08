# LLM Task — JSON-Only LLM Step

LLM Task is a plugin that provides a JSON-only LLM tool for structured workflow output. It calls a model and returns only JSON — no code fences, no commentary. Designed for use in Lobster pipelines and other automation where structured data is needed.

## Enable the Plugin

1. Enable the plugin in config:

```json5
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  }
}
```

2. Allowlist the tool (registered with `optional: true`):

```json5
{
  "agents": {
    "list": [
      { "id": "main", "tools": { "allow": ["llm-task"] } }
    ]
  }
}
```

## Config (Optional)

```json5
{
  "plugins": {
    "entries": {
      "llm-task": {
        "enabled": true,
        "config": {
          "defaultProvider": "openai-codex",
          "defaultModel": "gpt-5.2",
          "defaultAuthProfileId": "main",
          "allowedModels": ["openai-codex/gpt-5.3-codex"],
          "maxTokens": 800,
          "timeoutMs": 30000
        }
      }
    }
  }
}
```

`allowedModels` uses `provider/model` format.

## Tool Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | ✅ | The prompt to send to the model |
| `input` | any | ❌ | Input data to include with the prompt |
| `schema` | object | ❌ | JSON Schema for output validation |
| `provider` | string | ❌ | Override default provider |
| `model` | string | ❌ | Override default model |
| `authProfileId` | string | ❌ | Override auth profile |
| `temperature` | number | ❌ | Model temperature |
| `maxTokens` | number | ❌ | Max output tokens |
| `timeoutMs` | number | ❌ | Request timeout |

## Output

- Response is available in `details.json`.
- If `schema` is provided, the output is validated against it.

## Example: Lobster Workflow Step

```
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

## Safety Notes

- The tool is **JSON-only** and instructs the model to output only JSON (no code fences, no commentary).
- **No tools** are exposed to the model for this run.
- Treat output as **untrusted** unless you validate with `schema`.
- Put **approvals before any side-effecting step** (send, post, exec).

## Learn More

- [Lobster](lobster.md) — workflow runtime that uses LLM Task
- [Exec Tool](exec.md) — exec tool reference
