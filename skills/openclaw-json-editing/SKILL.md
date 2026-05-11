---
name: openclaw-json-editing
description: Advanced JSON editing for OpenClaw configuration files, tools, and data structures. Handles JSON5 configs, schema validation, merge patching, env var substitution, and type-safe modifications.
metadata:
  openclaw:
    emoji: "📝"
    requires:
      bins: ["jq"]
---

# OpenClaw JSON Editing

Expert guidance for editing JSON in the OpenClaw ecosystem. OpenClaw uses **JSON5** for configuration (allows comments, trailing commas), has sophisticated config merging, and validates with **Zod schemas**.

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| Validate config | `openclaw config validate` |
| Apply config patch | `openclaw config patch <file.json>` |
| Safe JSON parse | Use `safeParseJson()` wrapper |
| Check config location | `openclaw config path` |
| Pretty print | `JSON.stringify(data, null, 2)` |

## OpenClaw JSON5 Config

OpenClaw config files use **JSON5** (not strict JSON):

```json5
{
  // Single-line comments are allowed
  "gateway": {
    "mode": "http",  // Trailing commas are allowed
  },
  /* Multi-line comments
     are also supported */
  "agents": {
    "main": {
      "model": "anthropic/claude-opus-4-6",
    },
  },
}
```

### Key Differences from JSON

- **Comments**: Single-line (`//`) and multi-line (`/* */`)
- **Trailing commas**: Allowed in arrays and objects
- **Unquoted keys**: `{ key: "value" }` is valid
- **Single quotes**: `'string'` is valid

### Config File Locations

| Type | Path |
|------|------|
| User config | `~/.openclaw/config.json` |
| Project config | `./openclaw.config.json` |
| Agent config | `~/.openclaw/agents/<id>/config.json` |
| Session store | `~/.openclaw/sessions/` |
| State dir | `~/.openclaw/` (or `$OPENCLAW_STATE_DIR`) |

## Safe JSON Operations

### Reading Config Files

OpenClaw uses `JSON5.parse()` for configs and safe wrappers:

```typescript
// OpenClaw's safeParseJson pattern
function safeParseJson<T>(raw: string): T | null {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

// For OpenClaw configs, use JSON5
import JSON5 from "json5";

function loadConfigFile(path: string): unknown {
  try {
    const raw = fs.readFileSync(path, "utf8");
    return JSON5.parse(raw);  // Allows comments, trailing commas
  } catch {
    return undefined;
  }
}
```

### Writing Config Files

OpenClaw writes with specific formatting and permissions:

```typescript
function saveJsonFile(pathname: string, data: unknown) {
  const dir = path.dirname(pathname);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  }
  // 2-space indentation, trailing newline
  fs.writeFileSync(pathname, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.chmodSync(pathname, 0o600);  // User read/write only
}
```

### Type Guards

Always validate before assuming structure:

```typescript
// OpenClaw's isPlainObject (strictest)
function isPlainObject(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    Object.prototype.toString.call(value) === "[object Object]"
  );
}

// Less strict version
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
```

## Config Merging & Patching

### Merge Patch (RFC 7386)

OpenClaw uses merge patching for config updates:

```typescript
// Apply a merge patch to base config
function applyMergePatch(base: unknown, patch: unknown): unknown {
  if (!isPlainObject(patch)) {
    return patch;
  }

  const result: Record<string, unknown> = isPlainObject(base) ? { ...base } : {};

  for (const [key, value] of Object.entries(patch)) {
    if (value === null) {
      delete result[key];  // null = delete key
      continue;
    }
    if (isPlainObject(value)) {
      const baseValue = result[key];
      result[key] = applyMergePatch(
        isPlainObject(baseValue) ? baseValue : {},
        value
      );
      continue;
    }
    result[key] = value;
  }

  return result;
}
```

### Usage Examples

```javascript
// Add/update nested field
const patch = {
  agents: {
    main: {
      model: "anthropic/claude-opus-4-6"
    }
  }
};

// Delete a field (set to null)
const deletePatch = {
  agents: {
    main: {
      temperature: null  // Removes temperature
    }
  }
};

// Replace entire section
const replacePatch = {
  channels: {
    telegram: null,  // Delete old
    discord: { token: "new-token" }  // Add new
  }
};
```

## Environment Variable Substitution

OpenClaw configs support `${VAR}` and `${VAR:-default}` syntax:

```json5
{
  "auth": {
    "profiles": {
      "openai": {
        "apiKey": "${OPENAI_API_KEY}"  // Substituted at load time
      },
      "anthropic": {
        "apiKey": "${ANTHROPIC_API_KEY:-fallback-key}"
      }
    }
  }
}
```

### Handling in Code

```typescript
// Check if string contains env var reference
function containsEnvVarReference(value: string): boolean {
  return /\$\{[^}]+\}/.test(value);
}

// Collect all env var paths in an object
function collectEnvRefPaths(
  value: unknown,
  path: string,
  output: Map<string, string>
): void {
  if (typeof value === "string") {
    if (containsEnvVarReference(value)) {
      output.set(path, value);
    }
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      collectEnvRefPaths(item, `${path}[${index}]`, output);
    });
    return;
  }
  if (isPlainObject(value)) {
    for (const [key, child] of Object.entries(value)) {
      const childPath = path ? `${path}.${key}` : key;
      collectEnvRefPaths(child, childPath, output);
    }
  }
}
```

## Schema Validation

### Zod Schema Pattern

OpenClaw uses Zod for runtime validation:

```typescript
import { z } from "zod";

// Define schema
const AgentConfigSchema = z.object({
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().positive().optional(),
  enabled: z.boolean().default(true),
});

// Validate
type AgentConfig = z.infer<typeof AgentConfigSchema>;

function validateConfig(data: unknown): AgentConfig {
  return AgentConfigSchema.parse(data);
}

// Safe validation
function safeValidateConfig(data: unknown): AgentConfig | null {
  const result = AgentConfigSchema.safeParse(data);
  return result.success ? result.data : null;
}
```

### Common OpenClaw Schema Types

```typescript
// Model reference: "provider/model-name"
const ModelRefSchema = z.string().regex(/^[a-z0-9-]+\/[a-z0-9-]+$/i);

// Channel ID
const ChannelIdSchema = z.enum([
  "telegram", "discord", "slack", "whatsapp",
  "signal", "imessage", "irc", "web"
]);

// Duration string: "30s", "5m", "1h"
const DurationSchema = z.string().regex(/^\d+[smhd]$/);
```

## Config Includes

OpenClaw supports config file includes:

```json5
{
  "include": [
    "./base-config.json",
    "~/.openclaw/shared-channels.json"
  ],
  "agents": {
    // Local overrides
  }
}
```

### Processing Order

1. Load included files (recursive, depth-limited)
2. Merge in order (later files override earlier)
3. Apply env var substitution
4. Validate against schema
5. Apply runtime overrides

## jq Patterns for OpenClaw

### Common Operations

```bash
# Pretty print OpenClaw config
jq . ~/.openclaw/config.json

# Get gateway mode
jq '.gateway.mode' ~/.openclaw/config.json

# List all agent IDs
jq '.agents | keys[]' ~/.openclaw/config.json

# Find agent using specific model
jq '.agents | to_entries[] | select(.value.model == "anthropic/claude-opus-4-6") | .key' ~/.openclaw/config.json

# Get all channel types
jq '.channels | keys[]' ~/.openclaw/config.json

# Check if Telegram is configured
jq '.channels.telegram != null' ~/.openclaw/config.json

# Extract all model references
jq '.. | objects | select(has("model")) | .model' ~/.openclaw/config.json

# Merge patch using jq
jq '.agents.main.model = "anthropic/claude-opus-4-6"' ~/.openclaw/config.json > tmp.json \
  && mv tmp.json ~/.openclaw/config.json
```

### Advanced jq

```bash
# Deep search for all API keys (for audit)
jq '.. | objects | .apiKey? // .token? // .password? | select(.)' ~/.openclaw/config.json

# Collect all environment variable references
jq -r '.. | strings | select(contains("${"))' ~/.openclaw/config.json

# Validate JSON structure (returns true/false)
jq 'if has("gateway") and has("agents") then true else false end' ~/.openclaw/config.json

# Create minimal config from full config
jq '{ gateway: .gateway, agents: { main: .agents.main } }' ~/.openclaw/config.json
```

## Common Config Patterns

### Gateway Configuration

```json5
{
  "gateway": {
    "mode": "http",  // "http", "disabled", "process"
    "http": {
      "bind": "127.0.0.1",
      "port": 3000,
    },
    "auth": {
      "token": "${OPENCLAW_GATEWAY_TOKEN}",
    },
  },
}
```

### Agent Configuration

```json5
{
  "agents": {
    "main": {
      "model": "anthropic/claude-opus-4-6",
      "temperature": 0.7,
      "maxTokens": 4096,
      // System prompt or reference to file
      "systemPrompt": "You are a helpful assistant.",
      "systemPromptFile": "~/.openclaw/agents/main/prompt.md",
    },
    "coder": {
      "model": "anthropic/claude-sonnet-4-5",
      "temperature": 0.2,
      // Inherit from main with overrides
      "inherits": "main",
    },
  },
}
```

### Channel Configuration

```json5
{
  "channels": {
    "telegram": {
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "allowFrom": ["@username"],
    },
    "discord": {
      "botToken": "${DISCORD_BOT_TOKEN}",
      "applicationId": "123456789",
    },
    "slack": {
      "botToken": "${SLACK_BOT_TOKEN}",
      "appToken": "${SLACK_APP_TOKEN}",
    },
  },
}
```

### Tools Configuration

```json5
{
  "tools": {
    "alsoAllow": ["web_search", "browser"],
    "deny": ["exec"],
    "config": {
      "web_search": {
        "provider": "brave",
        "apiKey": "${BRAVE_API_KEY}",
      },
    },
  },
}
```

## Validation & Error Handling

### Common Validation Errors

```typescript
// Schema validation errors provide detailed paths
const result = schema.safeParse(data);
if (!result.success) {
  for (const error of result.error.errors) {
    console.log(`${error.path.join('.')}: ${error.message}`);
    // e.g., "agents.main.temperature: Number must be less than or equal to 2"
  }
}
```

### Config File Recovery

```bash
# If config is corrupted, OpenClaw keeps backups
ls -la ~/.openclaw/config.json.*

# Restore from backup
cp ~/.openclaw/config.json.2024-01-15T10-30-00.bak ~/.openclaw/config.json

# Or use OpenClaw's built-in rotation
openclaw config restore
```

## Best Practices

### 1. Always Validate After Edit

```bash
# Validate config syntax and schema
openclaw config validate

# Test config loading
openclaw config get
```

### 2. Backup Before Changes

```bash
# Create timestamped backup
cp ~/.openclaw/config.json ~/.openclaw/config.json.$(date +%Y%m%d_%H%M%S).bak
```

### 3. Use Type Guards

```typescript
// Never assume structure - always validate
if (!isPlainObject(config.agents)) {
  throw new Error("Invalid agents configuration");
}
```

### 4. Handle Env Vars Carefully

```typescript
// Preserve env var references when editing
const originalValue = "${API_KEY}";
const newValue = process.env.API_KEY || originalValue;
```

### 5. Use Structured Clone for Deep Copies

```typescript
// Preferred for deep cloning
deepCopy = structuredClone(original);

// Fallback for older environments
deepCopy = JSON.parse(JSON.stringify(original));
```

### 6. Atomic Writes

```typescript
// Write to temp file, then rename
fs.writeFileSync(tempPath, data);
fs.renameSync(tempPath, finalPath);
```

## Security Considerations

- **File permissions**: Config files should be `0o600` (user read/write only)
- **No secrets in JSON**: Use `${ENV_VAR}` substitution
- **Validate inputs**: Always schema-validate external JSON
- **Sanitize paths**: Use `path.resolve()` and check traversal
- **Audit logging**: OpenClaw logs config changes to `config-audit.jsonl`

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Unexpected token /` | Comments in JSON | Use JSON5 parser |
| `Trailing comma` | Trailing comma in array | Use JSON5 parser |
| `Env var not substituted` | Missing env var | Check `${VAR:-default}` |
| `Validation failed` | Schema mismatch | Run `openclaw config validate` |
| `Permission denied` | Wrong file permissions | `chmod 600 config.json` |

### Debug Commands

```bash
# Check raw config (before env substitution)
cat ~/.openclaw/config.json

# Check effective config (after all processing)
openclaw config get --json

# List all env var references
openclaw config env-refs

# Trace config loading
OPENCLAW_DEBUG=config openclaw config get
```

## Editing Providers & Model Configuration

When adding or updating AI providers in `openclaw.config.json`, you must **discover actual model names from the provider's API** and handle **reasoning model variants** correctly.

### Model Discovery Workflow

```bash
# 1. Fetch available models from provider API
# xAI example - requires XAI_API_KEY
XAI_API_KEY="your-key"
curl -s -H "Authorization: Bearer $XAI_API_KEY" \
  https://api.x.ai/v1/models | jq '.data[] | {id: .id, name: .object}'

# OpenAI example
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | jq '.data[] | select(.id | contains("gpt")) | .id'

# Together AI example
curl -s -H "Authorization: Bearer $TOGETHER_API_KEY" \
  https://api.together.xyz/v1/models | jq '.[] | {id: .id, name: .display_name}'
```

### Provider Configuration Schema

OpenClaw uses `ModelProviderConfig` schema:

```typescript
type ModelProviderConfig = {
  baseUrl: string;           // API endpoint base URL
  apiKey?: string;           // Optional: API key (prefer env vars)
  auth?: "api-key" | "aws-sdk" | "oauth" | "token";
  api?: "openai-completions" | "openai-responses" | 
        "anthropic-messages" | "google-generative-ai" |
        "github-copilot" | "bedrock-converse-stream" | "ollama";
  headers?: Record<string, string>;  // Custom headers
  models: ModelDefinitionConfig[];   // Model definitions
};

type ModelDefinitionConfig = {
  id: string;                // Model ID (e.g., "grok-4")
  name: string;              // Display name (e.g., "Grok 4")
  api?: ModelApi;            // Override API type per model
  reasoning: boolean;        // Whether model supports reasoning/thinking
  input: Array<"text" | "image">;  // Supported input types
  cost: {
    input: number;           // Cost per 1M input tokens
    output: number;          // Cost per 1M output tokens
    cacheRead: number;       // Cost per 1M cached tokens read
    cacheWrite: number;      // Cost per 1M cached tokens written
  };
  contextWindow: number;     // Max context window size
  maxTokens: number;         // Max output tokens
  headers?: Record<string, string>;
  compat?: ModelCompatConfig;
};
```

### Reasoning Model Families

**CRITICAL**: Some models have **reasoning variants** handled specially by OpenClaw. For example, xAI's `grok-4-1-fast` has three variants:

| Model ID | Type | Notes |
|----------|------|-------|
| `grok-4-1-fast` | Base | The "family" identifier |
| `grok-4-1-fast-reasoning` | Reasoning | Full reasoning capabilities |
| `grok-4-1-fast-non-reasoning` | Non-reasoning | Faster, no reasoning |

**In OpenClaw, you typically configure ONLY the base model** (`grok-4-1-fast`). The system automatically switches between reasoning/non-reasoning variants based on the `thinking` directive or configuration.

```json5
{
  "models": {
    "providers": {
      "xai": {
        "baseUrl": "https://api.x.ai/v1",
        "api": "openai-completions",
        "apiKey": "${XAI_API_KEY}",
        "models": [
          {
            "id": "grok-4-1-fast",
            "name": "Grok 4.1 Fast",
            "reasoning": false,  // Base model is non-reasoning
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 128000,
            "maxTokens": 8192
          }
          // NOTE: Do NOT add -reasoning or -non-reasoning variants separately
          // OpenClaw handles these automatically via model family resolution
        ]
      }
    }
  }
}
```

### Model Family Resolution

OpenClaw internally defines **reasoning model families** in `src/agents/model-families.ts`:

```typescript
const REASONING_MODEL_FAMILIES = [
  {
    provider: "xai",
    members: [
      "grok-4-1-fast",
      "grok-4-1-fast-reasoning",
      "grok-4-1-fast-non-reasoning"
    ],
    reasoningModel: "grok-4-1-fast-reasoning",
    nonReasoningModel: "grok-4-1-fast-non-reasoning",
  },
];
```

When a user requests a model with `thinking: "on"` or `thinking: "off"`, OpenClaw:

1. Looks up if the requested model is in a reasoning family
2. If `thinking: "on"` → uses `reasoningModel` variant
3. If `thinking: "off"` → uses `nonReasoningModel` variant
4. If no thinking directive → uses the base model as-is

### Complete Provider Configuration Example

```json5
{
  "models": {
    "mode": "merge",  // "merge" or "replace"
    "providers": {
      // xAI - Grok models with reasoning variants
      "xai": {
        "baseUrl": "https://api.x.ai/v1",
        "api": "openai-completions",
        "apiKey": "${XAI_API_KEY}",
        "models": [
          {
            "id": "grok-4-1-fast",
            "name": "Grok 4.1 Fast",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 128000,
            "maxTokens": 8192
          },
          {
            "id": "grok-4",
            "name": "Grok 4",
            "reasoning": false,
            "input": ["text", "image"],  // Vision-capable
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 128000,
            "maxTokens": 8192,
            "compat": {
              "supportsReasoningEffort": false,
              "maxTokensField": "max_completion_tokens"
            }
          }
        ]
      },
      
      // OpenAI - with response API and reasoning
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "api": "openai-responses",
        "apiKey": "${OPENAI_API_KEY}",
        "models": [
          {
            "id": "gpt-5.2",
            "name": "GPT-5.2",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 2.5, "output": 10, "cacheRead": 0.5, "cacheWrite": 1.25 },
            "contextWindow": 200000,
            "maxTokens": 16384,
            "compat": {
              "supportsReasoningEffort": true,
              "thinkingFormat": "openai"
            }
          },
          {
            "id": "o3-mini",
            "name": "o3 Mini",
            "reasoning": true,  // Built-in reasoning model
            "input": ["text", "image"],
            "cost": { "input": 1.1, "output": 4.4, "cacheRead": 0.275, "cacheWrite": 0.55 },
            "contextWindow": 200000,
            "maxTokens": 100000,
            "compat": {
              "supportsReasoningEffort": true,
              "requiresAssistantAfterToolResult": true
            }
          }
        ]
      },
      
      // Anthropic - Messages API
      "anthropic": {
        "baseUrl": "https://api.anthropic.com",
        "api": "anthropic-messages",
        "apiKey": "${ANTHROPIC_API_KEY}",
        "models": [
          {
            "id": "claude-opus-4-6",
            "name": "Claude Opus 4.6",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 15, "output": 75, "cacheRead": 1.88, "cacheWrite": 7.5 },
            "contextWindow": 200000,
            "maxTokens": 8192,
            "compat": {
              "supportsStore": false,
              "supportsDeveloperRole": false
            }
          }
        ]
      },
      
      // Google Gemini
      "google": {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
        "api": "google-generative-ai",
        "apiKey": "${GEMINI_API_KEY}",
        "models": [
          {
            "id": "gemini-3-pro-preview",
            "name": "Gemini 3 Pro Preview",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 1.25, "output": 10, "cacheRead": 0.31, "cacheWrite": 1.25 },
            "contextWindow": 1000000,
            "maxTokens": 8192,
            "compat": {
              "thinkingFormat": "qwen"
            }
          }
        ]
      },
      
      // Ollama - local models (auto-discovered)
      "ollama": {
        "baseUrl": "http://localhost:11434/v1",
        "api": "ollama",
        "models": []  // Auto-populated from /api/tags
      }
    }
  }
}
```

### Model Compatibility Flags

```typescript
type ModelCompatConfig = {
  // OpenAI-specific features
  supportsStore?: boolean;                    // Use 'store' parameter
  supportsDeveloperRole?: boolean;            // Use 'developer' vs 'system' role
  supportsReasoningEffort?: boolean;          // Support reasoning_effort param
  supportsUsageInStreaming?: boolean;         // Usage in streaming responses
  supportsStrictMode?: boolean;               // Strict tool mode
  
  // Token handling
  maxTokensField?: "max_completion_tokens" | "max_tokens";
  
  // Thinking/reasoning format
  thinkingFormat?: "openai" | "zai" | "qwen";
  
  // Tool calling quirks
  requiresToolResultName?: boolean;           // Must include tool result name
  requiresAssistantAfterToolResult?: boolean; // Assistant message after tool
  requiresThinkingAsText?: boolean;           // Thinking blocks as text
  requiresMistralToolIds?: boolean;           // Mistral-style tool IDs
};
```

### Validating Provider Configuration

```bash
# Validate the full config including models
openclaw config validate

# Check if models.json is correctly generated
openclaw models list

# Test a specific model provider
openclaw models test --provider xai --model grok-4-1-fast

# Debug model resolution
OPENCLAW_DEBUG=models openclaw models list
```

### Common Pitfalls

| Pitfall | Why It Happens | Solution |
|---------|---------------|----------|
| Adding `-reasoning` variants | Don't manually add reasoning variants | Only add base model (e.g., `grok-4-1-fast`) |
| Wrong `reasoning` boolean | Confusion about model capabilities | Set based on base model, not variants |
| Missing `api` field | Defaults may not match provider | Explicitly set `api` to correct value |
| Hardcoded API keys | Security risk | Always use `${ENV_VAR}` substitution |
| Wrong baseUrl | Provider-specific endpoints | Check provider documentation |
| Incorrect cost values | Tracking/budgeting issues | Verify per-provider pricing |

### Provider-Specific Notes

#### xAI (Grok)
- Uses `openai-completions` API
- Model families auto-resolve reasoning variants
- Vision support varies by model

#### OpenAI
- Use `openai-responses` for o-series and GPT-5
- Use `openai-completions` for legacy GPT-4
- Reasoning effort adjustable via `supportsReasoningEffort`

#### Anthropic
- Uses `anthropic-messages` API
- No separate reasoning models (all models can think)
- Distinct cost structure for prompt caching

#### Google (Gemini)
- Uses `google-generative-ai` API
- Very large context windows (1M tokens)
- Different content format than OpenAI/Anthropic

#### Ollama
- Set `api: "ollama"` for native discovery
- Models auto-discovered from `/api/tags`
- Local inference - no API key needed

### Model Aliases

Define aliases for common models in agent defaults:

```json5
{
  "agents": {
    "defaults": {
      "models": {
        "fast": { "alias": "Grok Fast", "id": "xai/grok-4-1-fast" },
        "smart": { "alias": "Claude Opus", "id": "anthropic/claude-opus-4-6" },
        "vision": { "alias": "GPT Vision", "id": "openai/gpt-5.2" }
      }
    }
  }
}
```

Use aliases in agent config:

```json5
{
  "agents": {
    "main": {
      "model": "fast"  // Resolves to xai/grok-4-1-fast
    }
  }
}
```
