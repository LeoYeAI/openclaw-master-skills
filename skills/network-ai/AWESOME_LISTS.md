# Awesome List PR Submissions

Ready-to-use PR titles, one-liners, and context for each list.
Submit these as pull requests to the respective repositories.

---

## 1. awesome-mcp-servers
**Repo:** https://github.com/punkpeye/awesome-mcp-servers

**PR title:**
> Add network-ai — multi-agent orchestration MCP server with blackboard, FSM, and compliance tools

**One-liner to add to the list:**
```markdown
- [network-ai](https://github.com/jovanSAPFIONEER/Network-AI) - Multi-agent orchestration MCP server. 20+ MCP tools: blackboard read/write, agent spawn/stop, FSM transitions, budget tracking, token management, audit log query. `npx network-ai-server --port 3001`. TypeScript/Node.js.
```

**Where to add it:** Under the orchestration or multi-agent section.

**PR body:**
> network-ai ships a production-ready MCP server (`network-ai-server` binary) that exposes the full orchestration control plane over HTTP/SSE + JSON-RPC 2.0. It includes 20+ tools across 4 groups: blackboard coordination (read/write/lock), agent control (spawn/stop/list), FSM governance (transition/state), and observability (budget status, audit trail, token lifecycle). Zero config — `npx network-ai-server` starts immediately.

---

## 2. awesome-ai-agents
**Repo:** https://github.com/e2b-dev/awesome-ai-agents

**PR title:**
> Add network-ai — TypeScript orchestration framework with concurrency safety for multi-agent systems

**One-liner to add to the list:**
```markdown
- [network-ai](https://github.com/jovanSAPFIONEER/Network-AI) - Plug-and-play multi-agent orchestration for TypeScript/Node.js. Connects 12 frameworks (LangChain, AutoGen, CrewAI, OpenAI Assistants, LlamaIndex, MCP, and more) with atomic shared state, FSM governance, per-agent budget enforcement, and cryptographic audit trails. Solves race conditions and split-brain writes in concurrent agent systems.
```

**PR body:**
> network-ai fills a gap that most agent frameworks leave open: safe coordination when agents share state. It wraps any agent framework via adapters (12 supported) and adds atomic blackboard writes, FSM state gating, per-agent token budget ceilings, and a ComplianceMonitor for behavioral governance. MIT licensed, 1,200+ tests, CodeQL + OpenSSF Scorecard.

---

## 3. awesome-langchain
**Repo:** https://github.com/kyrolabs/awesome-langchain

**PR title:**
> Add network-ai — orchestration layer with LangChain adapter for multi-agent coordination safety

**One-liner to add to the list:**
```markdown
- [network-ai](https://github.com/jovanSAPFIONEER/Network-AI) - Multi-agent orchestration framework with a first-class LangChain adapter. Wraps LangChain Runnables, chains, and agents with atomic shared state, permission gating, budget enforcement, and FSM governance. Prevents race conditions when multiple LangChain agents write to shared resources concurrently.
```

**Where to add it:** Under Tools / Agent frameworks / Orchestration.

---

## 4. awesome-llamaindex
**Repo:** https://github.com/emptycrown/awesome-llamaindex (or the official one)

**PR title:**
> Add network-ai — orchestration layer with LlamaIndex adapter

**One-liner to add to the list:**
```markdown
- [network-ai](https://github.com/jovanSAPFIONEER/Network-AI) - Orchestration framework with a LlamaIndex adapter supporting query engines, chat engines, and agent runners. Adds atomic shared state, FSM governance, and per-agent budget ceilings to LlamaIndex-based pipelines.
```

---

## 5. awesome-mcp (or MCP-related lists)
**Search:** github.com/topics/model-context-protocol

**PR title:**
> Add network-ai — MCP server + client transport for multi-agent orchestration

**One-liner:**
```markdown
- [network-ai](https://github.com/jovanSAPFIONEER/Network-AI) - MCP server (`network-ai-server`) and transport (`McpSseTransport`) for multi-agent orchestration. Exposes blackboard, FSM, budget, token, and audit tools over SSE/JSON-RPC 2.0. Also includes an MCP adapter so MCP tool handlers can be registered as governed agents.
```

---

## Submission checklist

Before each PR:
- [ ] Fork the target repo
- [ ] Add the one-liner in alphabetical order by tool name within its section
- [ ] PR title follows the repo's existing convention (check other recent PRs)
- [ ] Verify the repo's README or CONTRIBUTING.md for any format requirements
- [ ] Star the repo before submitting (improves PR acceptance rate)

## Other lists to check

- https://github.com/jim-schwoebel/awesome-ai-frameworks
- https://github.com/AgentOps-AI/agentops (list of frameworks)
- https://github.com/topics/ai-agents (GitHub topic — add `ai-agents` to repo if not there)
- Product Hunt — "AI Developer Tools" category launch
