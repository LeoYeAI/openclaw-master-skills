# Lobster — Typed Workflow Runtime

Lobster is a typed workflow runtime for OpenClaw that lets agents run composable pipelines with built-in approval gates. One tool call replaces many, with resumable state and deterministic execution.

## Why Lobster

- **One call instead of many**: OpenClaw runs one Lobster tool call and gets a structured result.
- **Approvals built in**: Side effects (send email, post comment) halt the workflow until explicitly approved.
- **Resumable**: Halted workflows return a `resumeToken`; approve and resume without re-running everything.

## Why a DSL Instead of Plain Programs

- **Approve/resume built in**: Normal programs can't pause and resume with a durable token without custom runtime.
- **Determinism + auditability**: Pipelines are data — easy to log, diff, replay, and review.
- **Constrained surface for AI**: Tiny grammar + JSON piping reduces "creative" code paths.
- **Safety policy baked in**: Timeouts, output caps, sandbox checks, and allowlists enforced by runtime.
- **Still programmable**: Each step can call any CLI or script. Generate `.lobster` files from code if needed.

## How It Works

1. Agent calls `lobster` tool with `action: "run"` and a `pipeline` string (inline or `.lobster` file path).
2. Lobster CLI executes the pipeline.
3. If a step requires approval, the tool returns `status: "needs_approval"` with a `resumeToken`.
4. Agent presents the approval to the user and calls `action: "resume"` with the token.

## Install Lobster

1. Get the Lobster CLI from [Lobster repo](https://github.com/openclaw/lobster).
2. Ensure `lobster` is on `PATH`.

## Enable the Tool

Global:

```json5
{ "tools": { "alsoAllow": ["lobster"] } }
```

Per-agent:

```json5
{
  "agents": {
    "list": [
      { "id": "main", "tools": { "alsoAllow": ["lobster"] } }
    ]
  }
}
```

Note: `tools.allow: ["lobster"]` also works but replaces the default set.

## Workflow Files (.lobster)

`.lobster` files define named, reusable workflows with typed args and steps.

**Fields**:
- `name` — workflow name
- `args` — named arguments with optional defaults
- `steps` — ordered list of steps
- `env` — environment variables (optional)
- `condition` / `when` — gate steps on prior results
- `approval` — mark steps requiring human approval
- `pipeline` — inline pipeline string (alternative to steps)

**Example — inbox triage**:

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

**Piping**:
- `stdin: $step.stdout` and `stdin: $step.json` pass a prior step's output.
- `condition` (or `when`) can gate steps on `$step.approved`.

## Pattern: Small CLI + JSON Pipes + Approvals

Compose small CLIs that produce JSON, pipe them together, and gate side effects with `approve`:

```json5
// Inline pipeline
{
  "action": "run",
  "pipeline": "exec --json --shell 'inbox list --json' | exec --stdin json --shell 'inbox categorize --json' | exec --stdin json --shell 'inbox apply --json' | approve --preview-from-stdin --limit 5 --prompt 'Apply changes?'",
  "timeoutMs": 30000
}
```

Resume after approval:

```json5
{ "action": "resume", "token": "<resumeToken>", "approve": true }
```

Cross-tool piping example:

```
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## JSON-Only LLM Steps (llm-task)

Use `llm-task` plugin inside Lobster for structured LLM output:

1. Enable the plugin:

```json5
{
  "plugins": { "entries": { "llm-task": { "enabled": true } } },
  "agents": { "list": [{ "id": "main", "tools": { "allow": ["llm-task"] } }] }
}
```

2. Invoke inside a pipeline:

```
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

See [LLM Task](llm_task.md) for full parameter reference.

## Tool Parameters

### run

```json5
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

Run a `.lobster` file with args:

```json5
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### resume

```json5
{ "action": "resume", "token": "<resumeToken>", "approve": true }
```

### Optional Inputs

| Parameter | Default | Description |
|---|---|---|
| `cwd` | process cwd | Working directory (must stay within cwd) |
| `timeoutMs` | 20000 | Kill subprocess if exceeded |
| `maxStdoutBytes` | 512000 | Kill subprocess if stdout exceeds this |
| `argsJson` | — | JSON string passed to `lobster run --args-json` (workflow files only) |

## Output Envelope

| Status | Meaning |
|---|---|
| `ok` | Finished successfully |
| `needs_approval` | Paused; `requiresApproval.resumeToken` needed to resume |
| `cancelled` | Explicitly denied or cancelled |

Output fields: `content` (result data), `details` (metadata).

## Approvals

When a step returns `requiresApproval`:

- `approve: true` → resume and continue side effects
- `approve: false` → cancel and finalize the workflow

Use `approve --preview-from-stdin --limit N` to show a preview before approval.

## OpenProse Integration

The `/prose` slash command can compile to `lobster` pipelines. OpenProse programs that use `tools.subagents.tools` map to Lobster tool invocations.

See [OpenProse](openprose.md).

## Safety

- **Local subprocess only** — no network calls from the plugin itself.
- **No secrets** — Lobster doesn't manage OAuth; it calls OpenClaw tools that do.
- **Sandbox-aware** — disabled when the tool context is sandboxed.
- **Hardened** — fixed executable name (`lobster`) on `PATH`; timeouts and output caps enforced.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `lobster subprocess timed out` | Pipeline takes too long | Increase `timeoutMs` or split pipeline |
| `lobster output exceeded maxStdoutBytes` | Too much output | Raise `maxStdoutBytes` or reduce output |
| `lobster returned invalid JSON` | Pipeline prints non-JSON | Ensure tool mode; print only JSON |
| `lobster failed (code …)` | Step error | Run the pipeline in a terminal to inspect stderr |

## Example: Email Triage

Without Lobster (manual multi-step):
```
User: "Check my email and draft replies"
→ openclaw calls gmail.list → LLM summarizes
→ User: "draft replies to #2 and #5" → LLM drafts
→ User: "send #2" → openclaw calls gmail.send
(repeat daily, no memory of what was triaged)
```

With Lobster (single tool call):

```json5
{ "action": "run", "pipeline": "email.triage --limit 20", "timeoutMs": 30000 }
```

Returns:

```json5
{
  "ok": true,
  "status": "needs_approval",
  "output": [{ "summary": "5 need replies, 2 need action" }],
  "requiresApproval": {
    "type": "approval_request",
    "prompt": "Send 2 draft replies?",
    "items": [],
    "resumeToken": "..."
  }
}
```

Resume:

```json5
{ "action": "resume", "token": "<resumeToken>", "approve": true }
```

## Case Study: Community Workflows

Popular community workflow patterns: `weekly-review`, `inbox-triage`, `memory-consolidation`, `shared-task-sync`.

- Thread: https://x.com/plattenschieber/status/2014508656335770033
- Repo: https://github.com/bloomedai/brain-cli

## Learn More

- [Plugins](plugins.md)
- [LLM Task](llm_task.md)
- [OpenProse](openprose.md)
