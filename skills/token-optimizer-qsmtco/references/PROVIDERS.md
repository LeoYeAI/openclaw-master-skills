# Alternative AI Providers & Models

Cost-effective alternatives to reduce token spend while maintaining quality.

## Provider Comparison

### Anthropic (Direct)
- **Claude Opus 4**: $15/MTok (input), $75/MTok (output) — Best reasoning, use sparingly
- **Claude Sonnet 4.5**: $3/MTok (input), $15/MTok (output) — Balanced, recommended default
- **Claude Haiku 4**: $0.25/MTok (input), $1.25/MTok (output) — Fast, cheap, great for simple tasks

### OpenRouter (Unified API)
- **Gemini 2.0 Flash**: $0.075/MTok (both) — 40x cheaper than Sonnet, decent quality
- **Gemini 2.5 Flash Exp**: $0.0375/MTok (both) — 80x cheaper, good for bulk operations
- **Claude models**: Same pricing as direct, convenience of unified API
- **Multiple providers**: Automatic failover if one hits rate limit

Website: https://openrouter.ai

### OpenAI (Direct or via OpenRouter)
- **GPT-4o**: $2.50/MTok (input), $10/MTok (output) — Comparable to Sonnet
- **GPT-4o-mini**: $0.15/MTok (input), $0.60/MTok (output) — Good for simple tasks
- **o1/o3-mini**: Reasoning models, higher cost but excellent for complex logic

### Google AI Studio (Direct)
- **Gemini 2.0 Flash Exp**: FREE up to 10M tokens/day — Best for development/testing
- **Gemini 2.5 Flash**: $0.0375/MTok (both) — Production-ready, very cheap

Website: https://aistudio.google.com

### Together.ai
- **Llama 3.3 70B**: $0.18/MTok (input), $0.18/MTok (output) — Open model, fast
- **Qwen 2.5 72B**: $0.18/MTok (both) — Strong at code and reasoning
- **DeepSeek V3**: $0.07/MTok (both) — Extremely cheap, surprisingly capable

Website: https://together.ai

### Cloudflare Workers AI
- **Free tier**: 10,000 neurons/day (generous for small workloads)
- **Paid**: $0.01/1000 neurons — Very cheap at scale
- **Models**: Llama, Mistral, various open models
- **Limitation**: Smaller context windows

Website: https://workers.cloudflare.com

## Routing Strategy

### Task Classification

**Simple tasks** → Quick tier (Haiku or Gemini Flash)
- File reads, status checks, simple queries
- Straightforward edits with clear instructions
- Routine operations (list files, check logs)

**Medium complexity** → Standard tier (Sonnet or GPT-4o)
- Code writing, debugging
- Multi-step workflows
- Explanation and documentation
- Most user-facing interactions

**Complex reasoning** → Deep tier (Opus or o1/o3-mini)
- Architecture design, system planning
- Deep code analysis
- Complex debugging
- Strategic decision-making

### Cost-Optimized Stack

**Development/Testing:**
1. Gemini 2.0 Flash Exp (free up to 10M/day)
2. Quick-tier models (cheap fallback)
3. Standard-tier models (when quality matters)

**Production (Hosting):**
1. Quick-tier models for 60% of tasks
2. Gemini Flash via OpenRouter for bulk operations
3. Standard-tier models for user interactions
4. Deep-tier models for critical decisions only

**Rate-Limited:**
1. OpenRouter (multiple providers, auto-failover)
2. Together.ai (open models, no strict limits)
3. Local Ollama (offline, free, slower)

## Multi-Provider Setup

### OpenRouter Configuration
```json
{
  "provider": "openrouter",
  "apiKey": "sk-or-v1-...",
  "models": {
    "cheap": "google/gemini-2.5-flash",
    "balanced": "anthropic/claude-sonnet-4.5",
    "smart": "anthropic/claude-opus-4"
  }
}
```

### Fallback Chain
1. Primary: Anthropic (direct)
2. Fallback 1: OpenRouter (same models)
3. Fallback 2: Together.ai (open models)
4. Fallback 3: Local Ollama (offline)

## API Key Management

Store API keys in `~/.openclaw/openclaw.json` or environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."
```

OpenClaw supports multiple keys for same provider → automatic rotation when rate-limited.

## Cost Estimation

**Example workload** (100K tokens/day):
- **All Standard (Sonnet)**: 100K × $3/MTok = $0.30/day = $9/month
- **Smart routing** (60% Quick, 30% Standard, 10% Deep):
  - 60K × $0.25 = $0.015
  - 30K × $3 = $0.09
  - 10K × $15 = $0.15
  - Total: $0.255/day = $7.65/month (**15% savings**)
- **Aggressive routing** (80% Gemini, 15% Quick, 5% Standard):
  - 80K × $0.075 = $0.006
  - 15K × $0.25 = $0.00375
  - 5K × $3 = $0.015
  - Total: $0.025/day = $0.75/month (**92% savings**)

## When NOT to Optimize

Don't over-optimize at the expense of user experience:
- User-facing responses → prioritize quality over cost
- Critical decisions → use best model available
- Real-time interactions → avoid latency from model switching

Use cheaper models for:
- Background tasks
- Heartbeat checks
- Log parsing
- Routine operations
- Internal processes
