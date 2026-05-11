# Configuration Templates

These are the config changes the cost-optimizer applies during setup (with user permission).

## Free Model Registration

Add to models.providers.openrouter.models array:

{"id":"deepseek/deepseek-chat-v3-0324:free","name":"DeepSeek V3 (Free)","contextWindow":164000,"maxTokens":2048}
{"id":"meta-llama/llama-4-scout-17b-16e-instruct:free","name":"Llama 4 Scout (Free)","contextWindow":512000,"maxTokens":2048}
{"id":"qwen/qwen3-235b-a22b:free","name":"Qwen 3 235B (Free)","contextWindow":40000,"maxTokens":2048}
{"id":"google/gemma-3-27b-it:free","name":"Gemma 3 27B (Free)","contextWindow":96000,"maxTokens":2048}
{"id":"mistral/mistral-small-3.1-24b-instruct:free","name":"Mistral Small 3.1 (Free)","contextWindow":96000,"maxTokens":2048}

Note: maxTokens set to 2048 to prevent runaway output costs.

## Model Aliases

Add to agents.defaults.models:

"openrouter/deepseek/deepseek-chat-v3-0324:free":{"alias":"deepseek-free"}
"openrouter/meta-llama/llama-4-scout-17b-16e-instruct:free":{"alias":"llama-free"}
"openrouter/qwen/qwen3-235b-a22b:free":{"alias":"qwen-free"}
"openrouter/google/gemma-3-27b-it:free":{"alias":"gemma-free"}
"openrouter/mistral/mistral-small-3.1-24b-instruct:free":{"alias":"mistral-free"}

## Paid Model Aliases (verify these exist)

"openrouter/minimax/minimax-m2.5":{"alias":"minimax"}
"openrouter/deepseek/deepseek-v3.2":{"alias":"deepseek"}
"openrouter/moonshotai/kimi-k2.5":{"alias":"kimi"}
"openrouter/z-ai/glm-5":{"alias":"glm"}
"openrouter/anthropic/claude-haiku-4-5":{"alias":"haiku"}
"openrouter/anthropic/claude-sonnet-4-6":{"alias":"sonnet"}
"openrouter/anthropic/claude-opus-4-6":{"alias":"opus"}
"openrouter/google/gemini-2.5-flash-lite":{"alias":"flashlite"}
"openrouter/google/gemini-2.5-flash":{"alias":"flash"}
"openrouter/openai/gpt-5-mini":{"alias":"gpt"}
"openrouter/openai/gpt-5-nano":{"alias":"nano"}

## Primary Model

model.primary: openrouter/minimax/minimax-m2.5
fallbacks: ["openrouter/anthropic/claude-haiku-4-5", "openrouter/google/gemini-2.5-flash"]

## Heartbeat (Zero Cost)

heartbeat.every: "55m"
heartbeat.model: "openrouter/deepseek/deepseek-chat-v3-0324:free"
heartbeat.target: "last"

## Memory Flush

compaction.memoryFlush.enabled: true
compaction.memoryFlush.softThresholdTokens: 3000

## Concurrency (Cost Reduction)

maxConcurrent: 2
subagents.maxConcurrent: 2