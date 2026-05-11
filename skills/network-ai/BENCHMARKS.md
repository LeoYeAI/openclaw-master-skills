# Benchmarks & Performance

> Performance data for Network-AI deployments. Your swarm is only as fast as the backend it calls — this page helps you choose the right setup.

## BlackboardValidator Throughput

Layer 1 validation (rule-based, zero LLM calls) measured on Node.js 20, Apple M2, single-thread:

| Input size | Ops/sec | Latency |
|---|---|---|
| Small entry (~100 chars) | ~1,000,000 | < 1 µs |
| Medium entry (~1 KB) | ~500,000 | ~2 µs |
| Large entry (~10 KB) | ~159,000 | ~6 µs |

Layer 2 (QualityGateAgent) adds LLM latency and is async — intended for high-value writes, not every write.

---

## Cloud Provider Performance

Not all cloud APIs perform the same. Model size, inference infrastructure, and tier all affect how fast each agent gets a response — and that directly multiplies across every agent in your swarm.

| Provider / Model | Avg response (5-agent swarm) | RPM limit (free/tier-1) | Notes |
|---|---|---|---|
| **OpenAI gpt-5.2** | 6–10s per call | 3–6 RPM | Flagship model, high latency, strict RPM |
| **OpenAI gpt-4o-mini** | 2–4s per call | 500 RPM | Fast, cheap, good for reviewer agents |
| **OpenAI gpt-4o** | 4–7s per call | 60–500 RPM | Balanced quality/speed |
| **Anthropic Claude 3.5 Haiku** | 2–3s per call | 50 RPM | Fastest Claude, great for parallel agents |
| **Anthropic Claude 3.7 Sonnet** | 4–8s per call | 50 RPM | Stronger reasoning, higher latency |
| **Google Gemini 2.0 Flash** | 1–3s per call | 15 RPM (free) | Very fast inference, low RPM on free tier |
| **Groq (Llama 3.3 70B)** | 0.5–2s per call | 30 RPM | Fastest cloud inference available |
| **Together AI / Fireworks** | 1–3s per call | Varies by plan | Good for parallel workloads |

**Key insight:** A 5-agent swarm using `gpt-4o-mini` at 500 RPM can fire all 5 agents truly in parallel and finish in ~4s total. The same swarm on `gpt-5.2` at 6 RPM must go sequential and takes 60s. **The model tier matters more than the orchestration framework.**

### Choosing a Model for Swarm Agents

- **Speed over depth** (many agents, real-time) → `gpt-4o-mini`, `claude-3.5-haiku`, `gemini-2.0-flash`, `groq/llama-3.3-70b`
- **Depth over speed** (few agents, high-stakes) → `gpt-4o`, `claude-3.7-sonnet`
- **Free / no-cost testing** → Groq free tier, Gemini free tier, or Ollama locally
- **Production with budget** → multiple keys across providers, route agents to different models

---

## Rate Limit Patterns

When you run a 5-agent swarm sharing one API key and hit the RPM ceiling, the API silently returns empty responses — not a 429 error, just blank content. Network-AI's swarm demos handle this automatically with **sequential dispatch** and **adaptive header-based pacing** (reads `x-ratelimit-reset-requests` to wait exactly as long as needed).

| You have | What to expect |
|---|---|
| One cloud API key | Sequential dispatch, 40–70s per 5-agent swarm — handled automatically |
| Multiple cloud keys | Near-parallel, 10–15s — one key per adapter instance |
| Local GPU (Ollama, vLLM) | True parallel, 5–20s depending on hardware |
| Home GPU + cloud mix | Local agents never block — cloud agents rate-paced independently |

### Multiple Keys = True Parallel

```typescript
import { CustomAdapter, AdapterRegistry } from 'network-ai';

const registry = new AdapterRegistry();

for (const reviewer of REVIEWERS) {
  const adapter = new CustomAdapter();
  const client  = new OpenAI({ apiKey: process.env[`OPENAI_KEY_${reviewer.id.toUpperCase()}`] });

  adapter.registerHandler(reviewer.id, async (payload) => {
    const resp = await client.chat.completions.create({ /* ... */ });
    return { findings: extractContent(resp) };
  });

  registry.register(reviewer.id, adapter);
}

// All 5 dispatch in parallel via Promise.all — ~8–12s instead of ~60s
```

### Local GPU = Zero Rate Limits

```typescript
const localClient = new OpenAI({
  apiKey : 'not-needed',
  baseURL: 'http://localhost:11434/v1',   // Ollama, vLLM, llama.cpp
});

adapter.registerHandler('reviewer', async (payload) => {
  const resp = await localClient.chat.completions.create({
    model   : 'llama3.2',
    messages: [/* ... */],
  });
  return { findings: extractContent(resp) };
});
```

---

## Cloud GPU Instances (Self-Hosted)

Running your own model on AWS / GCP / Azure sits between managed APIs and local hardware:

| Setup | Speed vs managed API | RPM |
|---|---|---|
| A100 (80GB) + vLLM, Llama 3.3 70B | Faster — 0.5–2s/call | None |
| H100 + vLLM, Mixtral 8x7B | Faster — 0.3–1s/call | None |
| T4 / V100 + Ollama, Llama 3.2 8B | Comparable | None |

Cost: $1–5/hr for GPU VMs. For high-volume production swarms or teams that want no external API dependency, it is the fastest architecture available. The connection is identical to local Ollama — just point `baseURL` at your VM's IP.

---

## `max_completion_tokens` — The Silent Truncation Trap

One of the most common failure modes in agentic output tasks. When a model hits the `max_completion_tokens` ceiling it stops mid-output and returns whatever it has — no error, no warning. The API call succeeds with `finish_reason: "length"` instead of `"stop"`.

**This is especially dangerous for code-rewrite agents** where the output is a full file.

```
# Real numbers (gpt-5-mini, order-service.ts rewrite):
  Blockers section:  ~120 tokens
  Fixed code:        ~2,800 tokens  (213 lines with // FIX: comments)
  Total needed:      ~3,000 tokens  ← hits the cap exactly → empty output
  Fix: set to 16,000 → full rewrite delivered in one shot
```

### Rule of Thumb by Task

| Task | Recommended cap |
|---|---|
| Short classification / sentiment | 200–500 |
| Code review findings (one reviewer) | 400–800 |
| Blocker summary (coordinator) | 500–1,000 |
| Full file rewrite (≤300 lines) | 12,000–16,000 |
| Full file rewrite (≤1,000 lines) | 32,000–64,000 |
| Document / design revision | 16,000–32,000 |

All GPT-5 variants support **128,000 max output tokens** — the ceiling is never the model, it is always the cap you set.

### Lessons from Building the Code-Review Swarm

| Issue | Root cause | Fix |
|---|---|---|
| Fixed code output was empty | `max_completion_tokens: 3000` too low | Raise to `16000`+ for any code-output agent |
| `finish_reason: "length"` silently discards | Model hits cap, partial response, no error | Always check `choices[0].finish_reason` and alert on `"length"` |
| Flagship model slow + expensive for reviewers | High latency + $14/1M output tokens | Use `gpt-5-mini` ($2/1M, same RPM) for reviewer/fixer agents |
| Coordinator + fixer as two calls | Second call hits rate limit window, +60s | Merge into one structured two-section call |
