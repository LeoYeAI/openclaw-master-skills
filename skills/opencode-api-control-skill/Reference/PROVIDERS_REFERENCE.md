# Providers & Models Reference

## Overview

This skill maintains a cache of **connected providers only** in `./providers.json`. The cache includes:
- OpenCode free provider (always available)
- Providers you've authenticated with API keys
- Their available models

## Updating Provider Cache
```bash
bash ./scripts/update_providers.sh
```

**When to update**:
- At workflow start
- After connecting new provider
- When selecting provider not in cache

**What it does**:
1. Queries OpenCode API for all providers
2. Filters to connected + OpenCode free
3. Extracts provider IDs, names, and models
4. Saves to `./providers.json`

## Cache File Structure
```json
{
  "connected": ["opencode", "anthropic", "openai"],
  "providers": [
    {
      "id": "opencode",
      "name": "OpenCode Zen",
      "models": [
        "gpt-5.1-codex",
        "gpt-5-nano"
      ]
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "models": [
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-haiku-4-5"
      ]
    }
  ]
}
```

## Selecting Provider

### Automatic (Default)

Uses values from `config.json`:
```bash
bash ./scripts/send_message.sh "Create app"
# Uses default_provider and default_model from config
```

### User Specifies

When user mentions provider in request:
```bash
# User says: "Create dashboard using Claude Sonnet"

# Search for provider and model
RESULT=$(bash ./scripts/select_provider.sh "claude" "sonnet")
PROVIDER_ID=$(echo "$RESULT" | cut -d' ' -f1)
MODEL_ID=$(echo "$RESULT" | cut -d' ' -f2)

# Use selected provider
bash ./scripts/send_message.sh "Create dashboard" "$PROVIDER_ID" "$MODEL_ID"
```

### Manual Selection
```bash
# Find provider
bash ./scripts/select_provider.sh "gemini" "pro"
# Output: gemini gemini-3-pro

# Parse and use
IFS=' ' read -r PROVIDER MODEL <<< $(bash ./scripts/select_provider.sh "gemini" "pro")
bash ./scripts/send_message.sh "Task" "$PROVIDER" "$MODEL"
```

## Provider Search Patterns

The `select_provider.sh` script searches by:
- Provider ID (exact or partial)
- Provider name (case-insensitive)
- Model name (partial match)

**Examples**:
```bash
# By provider ID
select_provider.sh "anthropic"          # → anthropic claude-opus-4-5
select_provider.sh "openai"             # → openai gpt-5

# By provider name
select_provider.sh "claude"             # → anthropic claude-opus-4-5
select_provider.sh "gemini"             # → gemini gemini-3-pro

# With model filter
select_provider.sh "anthropic" "sonnet" # → anthropic claude-sonnet-4-5
select_provider.sh "openai" "4"         # → openai gpt-4
select_provider.sh "gemini" "flash"     # → gemini gemini-2-flash
```

## Common Providers

### OpenCode Zen (Free)

**Always available** - no authentication needed.
```json
{
  "id": "opencode",
  "name": "OpenCode Zen",
  "models": [
    "kimi-k2.5-free",  // reasoning, Best for coding
    "gpt-5-nano"      // reasoning, Fast, smaller tasks
    "minimax-m2.5-free" // reasoning, Best for coding
    "big-pickle" // reasoning, Fastest, smaller tasks
  ]
}
```

**Best for**:
- Testing workflows
- Simple tasks
- Learning OpenCode

### Anthropic

Requires API key in OpenCode config.

**Best models**:
- `claude-opus-4-6` - Most capable, complex reasoning
- `claude-opus-4-5` - Most capable, complex reasoning
- `claude-sonnet-4-5` - Balanced, great for code
- `claude-haiku-4-5` - Fastest, simple tasks

**Best for**:
- Complex coding projects
- Following detailed instructions
- Large context (200K+ tokens)

### OpenAI

Requires API key in OpenCode config.

**Best models**:
- `gpt-5.3-codex` - Latest, most capable best for coding
- `gpt-5.2-codex` - Stable, reliable good for coding
- `gpt-5-nano` - Fast, smaller tasks

**Best for**:
- General development
- Fast responses
- Wide task variety

### Google Gemini

Requires API key in OpenCode config.

**Best models**:
- `gemini-3-pro-preview` - Latest pro model best for coding
- `gemini-3-flash-preview` - Fast, smaller tasks
- `gemini-2.5-flash-lite` - Previous generation, Fastest, simple tasks

**Best for**:
- Huge context (2M tokens)
- Large codebases
- Cost-effective processing

## Provider Selection Strategy

### By Task Type

**Planning/Analysis**:
```bash
# Use fast models
select_provider.sh "opencode"  # Free
select_provider.sh "gemini" "flash"  # Fast + cheap
```

**Implementation**:
```bash
# Use capable models
select_provider.sh "anthropic" "sonnet"  # Great code
select_provider.sh "openai" "gpt-5"  # Latest
```

**Complex/Critical**:
```bash
# Use best models
select_provider.sh "anthropic" "opus"  # Most capable
```

### By User Request

Extract from natural language:
```bash
USER_REQUEST="Create dashboard with Gemini Pro"

if echo "$USER_REQUEST" | grep -qi "gemini"; then
  bash ./scripts/select_provider.sh "gemini" "pro"
elif echo "$USER_REQUEST" | grep -qi "claude\|anthropic\|sonnet"; then
  bash ./scripts/select_provider.sh "anthropic" "sonnet"
elif echo "$USER_REQUEST" | grep -qi "gpt\|openai"; then
  bash ./scripts/select_provider.sh "openai"
else
  # Use default
  PROVIDER=$(jq -r '.default_provider' ./config.json)
  MODEL=$(jq -r '.default_model' ./config.json)
fi
```

## Checking Provider Availability

### Is provider connected?
```bash
PROVIDER="anthropic"
if jq -e --arg p "$PROVIDER" '.providers[] | select(.id==$p)' ./providers.json >/dev/null; then
  echo "Available"
else
  echo "Not connected"
fi
```

### List available providers
```bash
jq -r '.providers[] | "\(.id): \(.name)"' ./providers.json
```

**Output**:
```
opencode: OpenCode Zen
anthropic: Anthropic
openai: OpenAI
gemini: Google Gemini
```

### List models for provider
```bash
PROVIDER="anthropic"
jq -r --arg p "$PROVIDER" \
  '.providers[] | select(.id==$p) | .models[]' \
  ./providers.json
```

## Fallback Behavior

If requested provider not found:
```bash
REQUESTED="my-provider"
RESULT=$(bash ./scripts/select_provider.sh "$REQUESTED" 2>&1)

if [ $? -ne 0 ]; then
  # Provider not found - use default
  PROVIDER=$(jq -r '.default_provider' ./config.json)
  MODEL=$(jq -r '.default_model' ./config.json)
  echo "Using default: $PROVIDER/$MODEL"
else
  PROVIDER=$(echo "$RESULT" | cut -d' ' -f1)
  MODEL=$(echo "$RESULT" | cut -d' ' -f2)
fi
```

## Updating Default Provider

Change in `config.json`:
```json
{
  "default_provider": "anthropic",
  "default_model": "claude-sonnet-4-5"
}
```

Then all commands without explicit provider use this default.

## Provider Authentication

Providers are connected in OpenCode, not in this skill:

1. **Via OpenCode CLI**:
```bash
   opencode config set providers.anthropic.apiKey "sk-..."
```

2. **Via OpenCode Web UI**:
   - Settings → Providers → Add API Key

3. **Via Environment**:
```bash
   export ANTHROPIC_API_KEY="sk-..."
   export OPENAI_API_KEY="sk-..."
```

After adding keys, update cache:
```bash
bash ./scripts/update_providers.sh
```

## Troubleshooting

### "Provider not found"

**Cause**: Not connected or cache outdated

**Solution**:
```bash
# Update cache
bash ./scripts/update_providers.sh

# Check available
jq -r '.providers[].id' ./providers.json

# If still missing, connect in OpenCode first
```

### Cache is empty

**Cause**: OpenCode server issue or wrong directory

**Solution**:
```bash
# Verify server
curl -s http://127.0.0.1:4099/global/health

# Try update with explicit project
bash ./scripts/update_providers.sh /path/to/any/project
```

### Wrong model selected

**Cause**: Multiple models match search

**Solution**:
```bash
# Be more specific
select_provider.sh "anthropic" "sonnet"  # Not just "claude"
select_provider.sh "gemini" "3-pro"      # Not just "pro"
```

## Best Practices

✅ Update cache at workflow start
✅ Use specific model names when critical
✅ Provide fallback to default
✅ Check provider availability before complex workflows
✅ Keep cache updated after connecting new providers

❌ Don't hardcode provider IDs
❌ Don't assume all providers available
❌ Don't use outdated cache
❌ Don't forget OpenCode free option
---
**Author:** [Malek RSH](https://github.com/malek262) | **Repository:** [OpenCode-CLI-Controller](https://github.com/malek262/opencode-api-control-skill)
