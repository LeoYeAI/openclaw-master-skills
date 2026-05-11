# Model Tier Reference Card

Prices are approximate per-request costs including ~140K base overhead. Verify current pricing at openrouter.ai/models.

## Free Tier — $0.00/request

| Alias | Model ID | Context |
|-------|----------|---------|
| deepseek-free | deepseek/deepseek-chat-v3-0324:free | 164K |
| llama-free | meta-llama/llama-4-scout-17b-16e-instruct:free | 512K |
| qwen-free | qwen/qwen3-235b-a22b:free | 40K |
| mistral-free | mistral/mistral-small-3.1-24b-instruct:free | 96K |
| gemma-free | google/gemma-3-27b-it:free | 96K |

Free models have rate limits. If one is limited, try the next in the list.

## Budget Tier — $0.01-0.14/request

| Alias | Model ID | Blended $/M | Per Request |
|-------|----------|------------|------------|
| nano | openai/gpt-5-nano | $0.14 | ~$0.01 |
| flashlite | google/gemini-2.5-flash-lite | $0.18 | ~$0.01 |
| deepseek | deepseek/deepseek-v3.2 | $0.31 | ~$0.04 |
| minimax | minimax/minimax-m2.5 | $0.53 | ~$0.04 |
| kimi | moonshotai/kimi-k2.5 | $1.08 | ~$0.07 (drops to ~$0.02 with caching) |
| glm | z-ai/glm-5 | $1.35 | ~$0.14 |

## Quality Tier — $0.15-0.53/request

| Alias | Model ID | Blended $/M | Per Request |
|-------|----------|------------|------------|
| haiku | anthropic/claude-haiku-4-5 | $2.00 | ~$0.15 |
| sonnet | anthropic/claude-sonnet-4-6 | $6.00 | ~$0.53 |

## Premium Tier — $0.44-0.71/request

| Alias | Model ID | Blended $/M | Per Request |
|-------|----------|------------|------------|
| gpt5 | openai/gpt-5 | $3.44 | ~$0.44 |
| opus | anthropic/claude-opus-4-6 | $10.00 | ~$0.71 |

## Monthly Cost Estimates (50 questions/day)

| Strategy | Monthly Cost |
|----------|-------------|
| All Opus | ~$1,065 |
| All Sonnet | ~$645 |
| All MiniMax | ~$60 |
| MiniMax + free models for simple tasks | ~$15-30 |
| Mostly free + MiniMax fallback | ~$1-10 |
| All free models | ~$0 |

## Prompt Caching Notes

- Anthropic: 90% discount on cached system prompt tokens. Cache expires after ~1 hour.
- Kimi K2.5: Auto-caching drops input cost 75% after first request in session.
- Switching models mid-session kills the cache. Stay on one model when possible.