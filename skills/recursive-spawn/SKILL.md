---
name: openclaw-spawner
description: >
  Enables an Openclaw agent to spawn sub-agents (child Openclaw instances) when a task is too
  large, complex, or parallel to handle alone. Use this skill whenever an Openclaw agent needs
  to delegate work to another Openclaw agent, break a large task into concurrent sub-tasks,
  or hand off a portion of work mid-execution. Triggers include: task requires parallel execution,
  a sub-task is clearly separable from the main task, the agent detects it cannot complete the
  work alone within time/context limits, or the user asks to "spawn", "delegate", "parallelize",
  or "split" work across agents. Always use this skill — not ad-hoc improvisation — when spawning
  is needed.
env: >
  Provider API key env var — which one depends on the model= argument passed at call time.
  Common ones: ANTHROPIC_API_KEY (Anthropic), OPENAI_API_KEY (OpenAI), GEMINI_API_KEY (Gemini),
  GROQ_API_KEY (Groq), MISTRAL_API_KEY (Mistral). Ollama requires no key.
  Full list: https://docs.litellm.ai/docs/providers
security: >
  CREDENTIAL: Set the provider-specific API key env var for your chosen model. Never embed keys in payloads or snapshots.
  FILESYSTEM: Passing file-access tools to children grants them read/write access to arbitrary paths — only pass tools you trust.
  DATA EXPOSURE: progress_so_far is sent to the provider API and visible to the child agent — sanitize snapshots and strip secrets before spawning.
  TOOLS: Tools must be in OpenAI function-call format — LiteLLM translates them per provider automatically.
---

# Openclaw Spawner

Allows an Openclaw agent to spawn child Openclaw agents, passing them exactly the context they
need to carry out their piece of work and report results back.

**Helper script:** `scripts/spawn_openclaw.py` — copy this into your project and import from it.
It contains `spawn_openclaw()`, `spawn_openclaw_async()`, `is_error()`, and `read_result()`.

**Multi-provider:** Uses [LiteLLM](https://docs.litellm.ai/docs/providers) — pass any supported
model string via the `model=` argument. Default is `"anthropic/claude-opus-4-6"`.

**Requires:** `litellm` Python package (`pip install litellm`) and the API key env var for
your chosen provider (e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).

**Tool format:** OpenAI function-call format. LiteLLM translates to each provider's native
format automatically.

---

## Security Notes

> **Credential:** `spawn_openclaw.py` uses LiteLLM to call your chosen provider.
> Set the matching API key env var (e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
> Never put keys in a payload or snapshot.

> **Tool format:** Tools must be in OpenAI function-call format. LiteLLM translates
> them to each provider's native format automatically.

> **Filesystem access:** Passing `tools=` to a child agent grants that child whatever
> capabilities those tools carry. File-access tools allow children to read and write arbitrary
> paths. Only supply tools you would trust the parent to use directly. When in doubt, omit
> `tools=` — the child will return results in its summary text.

> **Snapshot sanitization:** `progress_so_far` is sent to the Anthropic API and injected
> into the child's context. Before spawning, review snapshots and strip any secrets,
> credentials, personal data, or other sensitive information.

---

## When to Spawn

Spawn a child agent when **any** of these are true:

- The remaining task has a clearly separable sub-task that can run independently.
- Two or more subtasks can proceed in parallel, saving wall-clock time.
- The current agent's context window is approaching its limit and a fresh context would help.
- A sub-task requires different tools, permissions, or specialization.
- The user explicitly asks to spawn / delegate / parallelize.

**Do not** spawn for trivial one-step tasks; keep it in the current agent.

---

## Spawn Depth Limit

`MAX_DEPTH = 3` (configurable in `scripts/spawn_openclaw.py`).

| Depth | Role |
|---|---|
| 0 | Root / parent agent |
| 1 | Direct child (default spawn) |
| 2 | Grandchild (only if child's `sub_task` explicitly permits spawning) |
| 3+ | **Blocked** — raises `ValueError` |

Always pass `depth=<current_depth + 1>` when calling `spawn_openclaw()` from inside a child.

---

## Spawn Payload Schema

Every spawn call must include these three fields:

```json
{
  "main_task_title": "<short human-readable title of the overall parent task>",
  "progress_so_far": "<markdown summary of what has already been done, decisions made, artefacts produced, and anything the sub-agent must know to avoid redoing work>",
  "sub_task": "<clear, self-contained description of exactly what this child agent must do, including expected output format and where/how to return results>"
}
```

### Field Guidelines

| Field | Rules |
|---|---|
| `main_task_title` | ≤ 10 words. Stable across all children of the same parent. |
| `progress_so_far` | Include: steps completed, key decisions, files written, variables/state the child needs. Exclude: raw data the child doesn't need. Keep it dense but readable. |
| `sub_task` | Must be self-contained. Assume the child has zero memory of the parent conversation. Include: what to do, inputs, expected output format, where to put results (file path, return value, etc.). |

---

## Step-by-Step Spawning Protocol

### 1 — Decide to Spawn

Confirm the sub-task is genuinely separable. If in doubt, handle it yourself.

### 2 — Freeze Parent State

Before spawning, write a progress snapshot. This becomes `progress_so_far` for the child
**and** serves as the parent's own checkpoint in case it needs to resume.

> **Sanitize before spawning.** `progress_so_far` is sent to the Anthropic API and
> injected into the child's context. Remove any secrets, API keys, passwords, tokens,
> or personal data before including them in the snapshot.

```
## Progress Snapshot — <main_task_title>
**Completed:**
- <step 1>
- <step 2>

**Artifacts produced:**
- <file or output name>: <one-line description>

**Decisions made:**
- <decision>: <rationale>

**Pending (what the child will handle):**
- <sub-task description>
```

### 3 — Build the Spawn Payload

Fill in the three required fields from the snapshot above.

### 4 — Spawn the Openclaw Sub-Instance

Import from `scripts/spawn_openclaw.py`:

> **Important:** Without `tools=`, the child is a pure language model — it can reason and
> produce text but **cannot read or write files**. If the sub_task requires file I/O, pass the
> appropriate tool definitions (e.g. Anthropic computer-use tools, custom file tools).
> When tools are omitted, collect the child's result from the `summary` string directly
> rather than calling `read_result()`.

```python
from spawn_openclaw import spawn_openclaw, is_error, read_result

# my_tools = [...]  # OpenAI function-call format tools if the child needs file I/O

payload = {
    "main_task_title": "Refactor authentication module",
    "progress_so_far": (
        "## Progress Snapshot\n"
        "**Completed:**\n- Audited existing auth flow\n- Identified 3 outdated JWT helpers\n\n"
        "**Artifacts produced:**\n- `/tmp/audit_report.md`: full list of issues\n\n"
        "**Decisions made:**\n- Use PyJWT 2.x API; drop legacy HS256 fallback\n\n"
        "**Pending (child handles):**\n- Rewrite auth/jwt_helpers.py per audit report"
    ),
    "sub_task": (
        "Rewrite `/src/auth/jwt_helpers.py` using PyJWT 2.x. "
        "Read `/tmp/audit_report.md` for issues to fix. "
        "Write the rewritten file to `/tmp/jwt_helpers_new.py` and a "
        "one-paragraph summary to `/tmp/jwt_helpers_changes.md`."
    ),
}

try:
    # Swap model= to use any LiteLLM-supported provider:
    # "openai/gpt-4o", "gemini/gemini-2.0-flash", "groq/llama-3.3-70b-versatile", etc.
    summary = spawn_openclaw(payload, depth=1, model="anthropic/claude-opus-4-6", tools=my_tools)
except (ValueError, FileNotFoundError) as exc:
    raise  # bad depth, missing payload key, or SKILL.md not found — fix the call

if is_error(summary):
    print("Child failed:", summary)
else:
    result = read_result("/tmp/jwt_helpers_changes.md")
    if result is None:
        print("WARNING: child did not write expected result file.")
```

If `SKILL.md` is not adjacent to `spawn_openclaw.py`, pass the path explicitly:

```python
import pathlib
summary = spawn_openclaw(payload, depth=1, skill_path=pathlib.Path("/your/path/to/SKILL.md"))
```

### 5 — Await and Integrate Results

1. Check `is_error(summary)` — handle failures before reading files.
2. Use `read_result(path)` to safely read child output; treat `None` as child failure.
3. Merge into parent progress snapshot.
4. Continue with the next step of the parent task — or spawn another child if needed.

---

## Spawning Strategies

| Strategy | When to use | Parent blocks? |
|---|---|---|
| **Sequential** | Child output is needed for next parent step | Yes, until child done |
| **Parallel-gather** | Multiple independent children; parent needs all before continuing | Yes, until all done |
| **Fire-and-forget** | Child works on a separable track; parent has its own work now | No — merge later |

---

### Strategy A — Sequential

Use `spawn_openclaw(payload, depth=1)` as shown in Step 4. Read result, check for errors, continue.

---

### Strategy B — Parallel Gather

```python
import asyncio
from spawn_openclaw import spawn_openclaw_async, is_error, read_result

async def main():
    payloads = [
        {
            "main_task_title": "Generate market research report",
            "progress_so_far": "Outline approved. Three sections assigned in parallel.",
            "sub_task": "Write 'Competitive Landscape' (600 words). Save to /tmp/section_competitive.md."
        },
        {
            "main_task_title": "Generate market research report",
            "progress_so_far": "Outline approved. Three sections assigned in parallel.",
            "sub_task": "Write 'Customer Segments' (600 words). Save to /tmp/section_customers.md."
        },
        {
            "main_task_title": "Generate market research report",
            "progress_so_far": "Outline approved. Three sections assigned in parallel.",
            "sub_task": "Write 'Market Trends' (600 words). Save to /tmp/section_trends.md."
        },
    ]

    summaries = await asyncio.gather(
        *[spawn_openclaw_async(p, depth=1, model="openai/gpt-4o", tools=my_tools) for p in payloads],
        return_exceptions=True,
    )

    result_paths = [
        "/tmp/section_competitive.md",
        "/tmp/section_customers.md",
        "/tmp/section_trends.md",
    ]

    for summary, path in zip(summaries, result_paths):
        if isinstance(summary, BaseException):
            print(f"Child raised exception for {path}: {summary}")
            continue
        if is_error(summary):
            print(f"Child failed for {path}:", summary)
            continue
        content = read_result(path)
        if content is None:
            print(f"WARNING: no result file at {path}")
        else:
            print(f"Merging {path} ({len(content)} chars)")
            # merge content into parent output ...
```

---

### Strategy C — Fire-and-Forget

The parent delegates a sub-task and **immediately continues its own work**.
The child writes results to a known file path. The parent checks at a planned **merge point**.

```
Parent:  ──[spawn child]──────────────────────────[merge point]──▶ continue
Child:            └──[work independently]──[write result file]──▶ done
```

```python
import asyncio
from spawn_openclaw import spawn_openclaw_async, is_error, read_result

async def main():
    child_result_path = "/tmp/child_analysis.md"
    payload = {
        "main_task_title": "Refactor authentication module",
        "progress_so_far": (
            "Audit complete. Parent is now rewriting core auth logic. "
            "Child is assigned to analyse test coverage gaps in parallel."
        ),
        "sub_task": (
            f"Read `/tmp/audit_report.md`. Identify which functions lack test coverage. "
            f"Write a markdown report of gaps to `{child_result_path}`. "
            f"Include function name, file, and suggested test cases for each gap."
        ),
    }

    # Spawn — returns immediately, child runs in background
    child_task = asyncio.create_task(
        spawn_openclaw_async(payload, depth=1, model="anthropic/claude-opus-4-6", tools=my_tools)
    )

    # Parent does its OWN work right now
    await do_parent_work()

    # Merge point — collect child
    try:
        summary = await child_task
    except (ValueError, FileNotFoundError) as exc:
        print("Child raised configuration error:", exc)
        return
    if is_error(summary):
        print("Child failed:", summary)
    else:
        content = read_result(child_result_path)
        if content is None:
            print("WARNING: child did not write expected result file.")
        else:
            await integrate_child_output(content)


async def do_parent_work():
    pass  # replace with actual parent steps

async def integrate_child_output(text: str):
    print(f"Merging {len(text)} chars from child...")
```

#### Rules for fire-and-forget

1. **Always specify `result_path` in `sub_task`** — it is the only rendezvous.
2. **Plan your merge point before spawning** — know exactly when the parent will need the child's output.
3. **Use `read_result()`** — returns `None` safely on any filesystem error (missing file, permission denied, etc.).
4. **One result file per child** — if a child produces multiple artefacts, have it write a manifest JSON listing them all.
5. **Don't fire-and-forget if parent needs the result immediately** — use Sequential instead.

---

## Error Handling

**What raises vs. what returns an error string:**

| Situation | Behaviour |
|---|---|
| Anthropic API error (network, rate limit, etc.) | Returns JSON error string — never raises |
| Empty or non-text API response | Returns JSON error string — never raises |
| `depth >= MAX_DEPTH` | **Raises `ValueError`** — programmer error, fix your call |
| Missing required payload key (`main_task_title`, `progress_so_far`, `sub_task`) | **Raises `ValueError`** — fix your payload |
| Non-JSON-serializable value in payload | **Raises `ValueError`** — fix your payload |
| SKILL.md not found | **Raises `FileNotFoundError`** — fix your path config |

Always check with `is_error()` after a successful call. Wrap the call itself in try/except if you need to handle the two programmer-error exceptions gracefully:

```python
try:
    summary = spawn_openclaw(payload, depth=1)
except (ValueError, FileNotFoundError) as exc:
    print("Configuration error:", exc)
    raise  # or handle

if is_error(summary):
    import json
    err = json.loads(summary)
    print("Runtime error:", err["error"])
    print("Partial results at:", err.get("partial_results"))  # may be None
    # decide: retry, fallback, abort parent
else:
    # success — read result files
    result = read_result("/tmp/some_output.md")
    if result is not None:
        # merge result ...
        pass
    else:
        print("WARNING: child did not write expected result file.")
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Sending the full conversation history as `progress_so_far` | Wastes tokens; child gets confused | Summarize: only what the child needs |
| Including secrets in `progress_so_far` | Snapshot is sent to Anthropic API and visible to child | Strip API keys, passwords, tokens, and personal data before spawning |
| Passing overly-permissive tools to children | Children gain filesystem or network access beyond what their sub_task needs | Scope tools to minimum required capability; omit tools= if the task only needs text output |
| Vague `sub_task` like "handle the rest" | Child doesn't know what to do | Be explicit: inputs, steps, output location |
| Spawning for a 2-line task | Overhead > benefit | Do it in the parent |
| Not writing a progress snapshot before spawning | Parent loses state if it crashes | Always freeze state first |
| Omitting `tools=` when sub_task requires file I/O | Child is a pure LM — it cannot read or write files; `read_result()` always returns `None` | Pass tool definitions or collect results from the summary string instead |
| Ignoring `is_error()` on child summary | Silent failures; parent merges nothing | Always check before reading result files |
| Fire-and-forget with no result file | No rendezvous; parent can't collect output | Always specify `result_path` in `sub_task` |
| Awaiting fire-and-forget child immediately after spawn | Defeats the purpose | Put `await child_task` at the merge point |
| Omitting `depth=` when spawning from inside a child | Depth check never triggers; runaway trees | Always pass `depth=current_depth + 1` |
| Child spawning further children without explicit permission | Runaway tree; hard to debug | Only spawn if `sub_task` explicitly says so |

---

## Quick Reference Card

```
SPAWN CHECKLIST
───────────────────────────────────────────
[ ] Sub-task is genuinely separable?
[ ] depth= will stay within MAX_DEPTH (default 3)?
[ ] Progress snapshot written (parent state frozen)?
[ ] main_task_title: ≤ 10 words, stable
[ ] progress_so_far: dense summary, no raw dumps
[ ] sub_task: self-contained, explicit result_path

STRATEGY SELECTION
[ ] Parent needs result before next step?        → Sequential (A)
[ ] Multiple children, all needed before merge?  → Parallel-gather (B)
[ ] Parent has its own work to do right now?     → Fire-and-forget (C)

AFTER EVERY SPAWN
[ ] is_error(summary) checked?
[ ] read_result(path) used (handles missing files safely)?
[ ] None result handled — don't merge silently?

FIRE-AND-FORGET EXTRAS
[ ] result_path agreed before spawning?
[ ] merge point placed after parent's own work?
```
