# OpenProse — Structured Multi-Agent Programs

OpenProse is a declarative program format (`.prose` files) for orchestrating multi-agent research, synthesis, and approval-safe workflows. Programs are reusable across supported agent runtimes.

## What It Can Do

- Multi-agent research + synthesis with explicit parallelism.
- Repeatable approval-safe workflows (code review, incident triage, content pipelines).
- Reusable `.prose` programs you can run across supported agent runtimes.

## Install + Enable

```bash
openclaw plugins enable open-prose
```

Or install from local path:

```bash
openclaw plugins install ./extensions/open-prose
```

See [Plugins](plugins.md), [Plugin manifest](plugin_manifest.md).

## Slash Command

```
/prose help
/prose run <file.prose>
/prose run <handle/slug>
/prose run <https://example.com/file.prose>
/prose compile <file.prose>
/prose examples
/prose update
```

## Example: A Simple .prose File

```
# Research + synthesis with two agents running in parallel.

input topic: "What should we research?"

agent researcher:
  model: sonnet
  prompt: "You research thoroughly and cite sources."

agent writer:
  model: opus
  prompt: "You write a concise summary."

parallel:
  findings = session: researcher
    prompt: "Research {topic}."
  draft = session: writer
    prompt: "Summarize {topic}."

session "Merge the findings + draft into a final answer."
  context: { findings, draft }
```

## File Locations

```
.prose/
├── .env
├── runs/
│   └── {YYYYMMDD}-{HHMMSS}-{random}/
│       ├── program.prose
│       ├── state.md
│       ├── bindings/
│       └── agents/
└── agents/
```

Global agents directory: `~/.prose/agents/`

## State Modes

| Mode | Description |
|---|---|
| `filesystem` (default) | `.prose/runs/...` |
| `in-context` | Transient, for small programs |
| `sqlite` (experimental) | Requires `sqlite3` binary |
| `postgres` (experimental) | Requires `psql` and connection string |

Notes:
- sqlite/postgres are opt-in and experimental.
- postgres credentials flow into subagent logs; use a dedicated, least-privileged DB.

## Remote Programs

```
/prose run <handle/slug>
```

Fetches from `https://p.prose.md/<handle>/<slug>`. Uses `web_fetch` and `exec` tools.

## OpenClaw Runtime Mapping

OpenProse maps to OpenClaw tools:

| Prose concept | OpenClaw tool |
|---|---|
| `session` | `sessions_spawn` |
| File I/O | `read`, `write` |
| Web fetch | `web_fetch` |

See [Skills config](skills.md) for integration details.

## Security + Approvals

`.prose` programs respect OpenClaw's approval model.

See [Lobster](lobster.md) for approval flow details.
