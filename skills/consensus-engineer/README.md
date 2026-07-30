# consensus-engineer

AI solution architect for [consensus-tools](https://github.com/consensus-tools/consensus-tools) — the decision infrastructure for autonomous AI agents.

## What it does

`/consensus-engineer` is an interactive skill that walks you through integrating consensus-tools into your project:

1. **Analyzes your project** — detects your stack, framework, AI SDKs
2. **Discovers your use case** — maps your needs to guard domains + consensus policies
3. **Recommends architecture** — guards vs wrapper vs hybrid pattern
4. **Scaffolds setup** — installs packages, creates config, generates starter code
5. **Proves it works** — runs a live guard evaluation against sample input
6. **Extends** — LangChain tools, AI SDK middleware, custom templates

## Quick start

```bash
# In Claude Code:
/consensus-engineer
```

The skill guides you through everything. No prior knowledge of consensus-tools required.

## What's included

- **llms.txt** (2,200+ lines) — Complete system reference covering all 32 packages, 29 MCP tools, 9 consensus policies, 7 guard domains, schema types, examples, and integration patterns
- **SKILL.md** — Interactive 6-phase guided experience with AskUserQuestion gates
- **metadata.json** — Skill metadata for ClawHub/skills.sh publishing

## Consensus-tools packages

The skill helps you integrate these packages:

| Package | What it does |
|---------|-------------|
| `@consensus-tools/guards` | 7 guard domains + `createGuardTemplate()` for custom domains |
| `@consensus-tools/policies` | 9 consensus algorithms + `createPolicyTemplate()` for custom policies |
| `@consensus-tools/wrapper` | Runtime function gating + `createWrapperTemplate()` |
| `@consensus-tools/personas` | Persona packs, reputation engine, respawn logic |
| `@consensus-tools/langchain` | Guards as LangChain tools + LangSmith tracer |
| `@consensus-tools/ai-sdk` | Guarded generateText/streamText for Vercel AI SDK |
| `@consensus-tools/core` | Job engine, ledger, vote aggregation |
| `@consensus-tools/schemas` | Zod schemas + TypeScript types |
| `@consensus-tools/mcp` | 29 MCP tools for Claude integration |

## Integration patterns

The skill detects which pattern fits your project:

- **Guards** — API/workflow style: evaluate inputs before actions execute
- **Wrapper** — In-memory function gating: wrap functions with reviewer consensus
- **Hybrid** — Guard templates as wrapper reviewers: best of both worlds
- **MCP** — 29 Claude-native tools for AI-driven governance

## License

Skill: MIT | Engine: Apache-2.0
