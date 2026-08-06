# credit-guardian

> Stop burning through AI credits. A lightweight token budget enforcer for any AI agent workflow.

## When to use this skill

Trigger when the user or agent:
- Mentions running out of API credits, tokens, coins, or points (Cursor, OpenAI, Anthropic, Grok, Copilot, etc.)
- Asks to "save tokens", "reduce API costs", or "stop overspending"
- Wants to set a per-session or per-task token budget
- Is running a long agentic loop and needs a hard-stop before credits run out
- Wants to route cheap tasks to free/local models and expensive tasks to frontier models

## What this skill does

1. **Pre-estimates** token cost for each planned step (before executing it)
2. **Enforces a session budget** — stops execution if cumulative tokens would exceed the cap
3. **Routes by complexity** — haiku/phi/local for simple steps, frontier models only for complex ones
4. **Reports burn rate** after each major step
5. **Gates expensive loops** — asks for human confirmation before entering loops that may consume >X tokens

## Core patterns

### Pattern 1: Session budget enforcement
```
BUDGET = 50,000 tokens (or user-specified)
session_used = 0

Before each LLM call:
  estimated_cost = estimate_tokens(prompt)
  if session_used + estimated_cost > BUDGET:
    STOP → "Token budget reached. Confirm to continue or adjust budget."
  session_used += actual_tokens_used
```

### Pattern 2: Complexity-based model routing
```
Task complexity tiers:
  FAST   → haiku / phi-4 / llama-3.1-8B / local models
           (JSON formatting, simple Q&A, yes/no decisions, templating)
  
  STANDARD → sonnet / gpt-4o-mini / claude-3-5-haiku
             (standard analysis, code review, summarization)
  
  DEEP     → opus / gpt-4o / claude-opus / frontier
             (multi-document synthesis, complex reasoning, security audits)

Routing rules:
  - Is the output a simple boolean/number? → FAST
  - Is the context < 2K tokens with a clear format? → FAST  
  - Does the task require multi-step reasoning? → STANDARD
  - Does the task involve cross-document conflict detection? → DEEP
  - Is this a security/legal/compliance audit? → DEEP
```

### Pattern 3: Context compression before expensive calls
```
Before sending to a DEEP model:
1. Summarize long context with a FAST model first
2. Send only the summary + key facts to the expensive model
3. Savings: 60-80% input token reduction on long-context tasks
```

### Pattern 4: Caching repeated prompts
```
Cache key = hash(system_prompt + user_input)
If cache hit → return cached result (0 tokens consumed)
Cache TTL = 1 hour (or per user config)
```

## Platform-specific guidance

| Platform | Credit type | Best approach |
|----------|-------------|---------------|
| Cursor | "fast" vs "slow" requests | Use "fast" for autocomplete; route file-level analysis to slow only when needed |
| OpenAI | Token credits | LiteLLM proxy + per-session budget; route to gpt-4o-mini by default |
| Anthropic | Token credits | Route to haiku by default; opus only for audits/complex synthesis |
| GitHub Copilot | Completions per month | Disable for non-code files; use inline-only mode |
| Grok/xAI | API tokens | Same routing as OpenAI; use grok-3-mini for speed/cost |

## Recommended integrations

- **LiteLLM** (`litellm-ai/litellm`) — universal proxy; add `budget_manager` callback for hard-stop on spend
- **ruvnet/ruflo** — agent orchestration with built-in WASM token optimizer (30-50% reduction)
- **tiktoken** — OpenAI token estimator; use before every call to pre-check cost
- **litellm.token_counter()** — cross-model token counting without API calls

## Example: LiteLLM budget wrapper
```python
import litellm
from litellm import BudgetManager

budget_manager = BudgetManager(project_name="nexus-agent", client_type="local")
budget_manager.create_budget(total_budget=5.00, user="session-1", duration="daily")

def guarded_completion(messages, model="claude-haiku-4-5"):
    if not budget_manager.is_valid_user("session-1"):
        raise Exception("Daily budget exhausted. Try again tomorrow.")
    
    response = litellm.completion(model=model, messages=messages)
    budget_manager.update_cost(completion_obj=response, user="session-1")
    return response
```

## Example: NEXUS-style TypeScript router
```typescript
// Route by complexity tier
function selectModel(tier: 'fast' | 'standard' | 'deep'): string {
  const map = {
    fast:     process.env.MODEL_FAST     ?? 'claude-haiku-4-5',
    standard: process.env.MODEL_STANDARD ?? 'claude-sonnet-4-5',
    deep:     process.env.MODEL_DEEP     ?? 'claude-opus-4-5',
  };
  return map[tier];
}

// Hard-stop on budget
let sessionTokens = 0;
const BUDGET = parseInt(process.env.TOKEN_BUDGET ?? '50000', 10);

function checkBudget(estimated: number): void {
  if (sessionTokens + estimated > BUDGET) {
    throw new Error(`Token budget would be exceeded (${sessionTokens + estimated} > ${BUDGET})`);
  }
}
```

## Token savings benchmarks (real-world estimates)

| Technique | Savings |
|-----------|---------|
| Haiku for simple tasks (was opus) | 70-85% per call |
| Context compression before deep calls | 60-80% input tokens |
| Response caching (repeated prompts) | 100% on cache hits |
| Sonnet vs Opus for standard analysis | 40-60% |
| Hard-stop enforcement | Prevents runaway loops (∞ savings) |
| Combined (routing + compression + cache) | **65-80% overall** |

## Output format

After implementing this skill, report to user:
```
💰 Token Guardian Report
  Session budget:    50,000 tokens
  Used this session: 12,847 tokens  
  Remaining:         37,153 tokens
  
  Breakdown:
    Deep calls (opus):     3 × avg 2,100 tokens = 6,300
    Standard calls:        5 × avg 800 tokens   = 4,000
    Fast calls (haiku):   12 × avg 212 tokens   = 2,547
  
  Savings vs all-opus:  ~73% (47,153 tokens saved)
```
