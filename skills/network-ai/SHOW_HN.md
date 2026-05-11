# Show HN: Network-AI — Multi-Agent Race Condition Prevention for TypeScript

**Post title:**
> Show HN: Network-AI – plug-and-play orchestrator that prevents race conditions when AI agents share state

---

## Body

I built Network-AI because I kept hitting the same problem: run two AI agents in parallel, they write to the same resource at the same time, and one of them silently overwrites the other. No error. No warning. Just wrong output.

Most agent frameworks give you parallelism. None of them give you coordination safety.

**The classic failure:**

```
Agent A reads balance:  $10,000
Agent B reads balance:  $10,000       ← same moment
Agent A writes balance: $3,000        ← deducts $7,000
Agent B writes balance: $4,000        ← deducts $6,000, ignoring Agent A's write
```

Both agents believed they had $10,000. Both spent from it. You now have a $3,000 error with no trace of what happened.

This is a split-brain problem, and it happens any time two LLM agents hit a shared database, file, or API concurrently. It's not theoretical — I've seen it in production pipelines.

---

**What Network-AI does:**

- **Atomic blackboard** — `propose → validate → commit` with file-system mutex. No two agents can write to the same key simultaneously.
- **Priority preemption** — if two agents conflict, the higher-priority write wins deterministically (not "last write wins" chaos)
- **FSM governance** — agents can only act when the workflow is in the right state
- **FederatedBudget** — per-agent token ceilings with hard cut-off. One runaway agent cannot exhaust your OpenAI bill.
- **ComplianceMonitor** — detects TOOL_ABUSE, turn-taking violations, response timeouts, journey timeouts in real time
- **12 framework adapters** — LangChain, AutoGen, CrewAI, OpenAI Assistants, LlamaIndex, Semantic Kernel, Haystack, DSPy, Agno, MCP, OpenClaw, and a CustomAdapter for anything else

---

**You can see the whole thing in 2 seconds with no API key:**

```bash
git clone https://github.com/jovanSAPFIONEER/Network-AI
cd Network-AI
npm install
npm run demo -- --08
```

This runs the control-plane stress demo: atomic commits, priority preemption, FSM timeout, and 17 live compliance violations — all in ~2 seconds, no LLM calls.

---

**Or the full AI showcase** (needs `OPENAI_API_KEY`):

```bash
npm run demo -- --07
```

8-agent pipeline that builds a Payment Processing Service with FSM gating, scoped auth tokens, per-agent budget ceilings, AI quality gates, automated code fixing, and deterministic 10/10 scoring. Writes a cryptographically signed audit trail to disk on every run.

---

**Stack:** TypeScript, Node.js 18+. Zero required external services. Works on-prem, air-gapped, or cloud.

**Repo:** https://github.com/jovanSAPFIONEER/Network-AI  
**npm:** `npm install network-ai`  
**MCP server:** `npx network-ai-server --port 3001`

Happy to answer questions about the coordination model, the FSM design, or how the atomic commits work.

---

## Timing notes

- Post on a **Tuesday or Wednesday between 9–11am ET** — peak HN traffic window
- Tag: `Show HN`
- Do not post the same week as a major AI framework release (it will get buried)
- Have the demo commands ready to paste in the comments — someone will ask immediately

## Expected comment threads to prepare for

1. "How is this different from LangGraph / LangChain?" → answer: Network-AI is the coordination layer, not the agent logic. It works *with* LangChain (there's an adapter).
2. "Does this work with Python?" → Python scripts are included (`scripts/`), TypeScript is the orchestration layer
3. "What's the performance overhead of the file-system mutex?" → microseconds for local; designed for workloads where LLM latency (100ms–10s) dominates
4. "Is this production-ready?" → MIT, 1,200+ tests, CodeQL + OpenSSF Scorecard on CI, 2,500+ weekly npm downloads at 24 days old
