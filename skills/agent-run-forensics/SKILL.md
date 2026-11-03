---
name: agent-run-forensics
description: Answers questions about a coding agent's earlier run from its recording rather than from memory - which step changed a file, why a command ran, where the build broke - and replays or forks that run offline. Use when investigating what a previous agent session actually did, reproducing a failure someone else reported, turning a failed session into a regression test, or deciding whether a different model would have handled the same task better.
---

# Agent Run Forensics

## Overview

A recording is evidence. An agent's memory of its own session is not, and neither is a transcript: both are missing the tool results, the exit codes, and the files that changed without anyone mentioning them.

This skill enforces one rule: **when a question is about something that already happened, read the trace before answering.** Do not reconstruct it. If a recording exists, guessing is the wrong move even when the guess would have been right.

The software-engineering problem it addresses is specific. Agent-assisted changes arrive without the provenance a human commit has - no review thread, no reasoning trail that survives the session. When the change turns out wrong, the usual question ("why was this done?") has no artifact to answer it, so it gets answered by asking the agent, which answers from a summary of its own context window. That is how a confident, wrong explanation enters a codebase's history.

## Prerequisites

Recording happens out of process: the agent is launched as a child process with its model-provider origin redirected for that process only. Nothing is installed into the agent, so the run that is captured is the program as it really ran rather than an instrumented variant.

```bash
node --version                          # Node 20+
which orca || npm install -g orcareplay # exposes an MCP server; register it as `orca`
orca list                               # at least one run, or there is nothing to read
```

## Core Workflow

### 1. Find the run

`orca_list_runs` returns runs newest first and names the run each fork came from. Skip this only when the user clearly means the most recent run; every other tool defaults to `run: "last"`.

### 2. Narrow to the chain that produced the thing being asked about

Two tools answer two different questions:

| Question | Tool |
|---|---|
| *What happened?* | `orca_show_run` - the full timeline: model turns with token counts and stop reasons, tool calls with arguments and results, shell commands with exit codes, every file changed |
| *Why did this happen?* | `orca_graph` with `to: <event seq>` - **only** the causal chain that produced that one event |

Reach for `orca_graph` first on a "why" question. Reading a 200-event timeline and reasoning over it is slower, costs more context, and invites exactly the confident guess this skill exists to prevent.

### 3. Keep observed and derived facts apart

Every edge `orca_graph` returns carries a label:

- **`recorded`** - the recorder observed it happen and wrote it into the trace.
- **`inferred`** - derived at query time from a rule the edge names. The trace does not vouch for it.

These are different epistemic claims and must stay different in the answer:

- Correct: "The trace shows the `rm` at step 14 removed it."
- Correct: "This looks like the `rm` at step 14, going by timing - that edge is inferred, not recorded."
- Wrong: "Step 14 removed it." (when the edge was inferred)

Name the rule whenever an inferred edge carries the conclusion.

### 4. Reproduce before explaining

`orca_replay` re-runs the recording and reports what could not be reproduced.

```
info replaying exchanges=6 egress=blocked
info replay.done reused=6/6 exact=6 divergences=0 exit=0
```

`exact=6` means every request matched the recording byte for byte. Anything that drifted is reported with its size rather than quietly matched.

**Always pass `worktree: true`.** It replays into a scratch copy. Without it, replay restores the recorded filesystem over the working tree for the duration of the run - uncommitted work is absent in the meantime, and stays absent if the replay is interrupted.

**Read the recorded shell commands before the first replay, not after.** Model responses come from the trace and no provider is contacted, but the agent process runs again for real, so every command it issued runs again too. A run that only read files and edited the repository is free to replay; one that reached `/tmp`, Docker, a database, a package manager or another host is not, and needs explicit approval or a container.

**`reused=3/5` is usually not a partial failure.** Harnesses make calls for themselves - a quota probe, a session-naming request - and a replay does not repeat them.

### 5. Compare models only when asked

`orca_compare` forks one run onto several models from the same checkpoint: same files, same conversation prefix, so the model is the only variable. Pick the fork point with `orca_checkpoints` and grade with `verify`, a shell command whose exit code is the verdict.

Use something the repository already declares (`npm test`, `npm run typecheck`) or an explicitly local binary (`./node_modules/.bin/tsc --noEmit`). Never `npx <tool>`: with no local install, npx runs whatever the registry has under that name.

Three approvals are needed and they are not the same question:

1. **Disclosure** - each model named receives the run's files and conversation prefix, so whatever that run touched is sent to every provider behind those model ids.
2. **Side effects** - each fork is a live agent, not a replay: from the fork point on the model is really being asked and its shell commands execute for real.
3. **Cost** - models times forks, in real money.

## Examples

**Investigating an unexplained change**

> "Why does `tsconfig.json` no longer have `strict: true`?"

Walk the graph to the edit, and answer from it:

```
14  TOOL   file_editor   {"command":"str_replace","path":".../tsconfig.json"}
15  SHELL  npm run build  exit 2
16  FILE   tsconfig.json  modified +1 -1
```

> The edit at step 14 removed it, and the build at step 15 then exited 2 (recorded, not inferred).

**Turning a failure into a test**

> "Does the bug from yesterday's session still reproduce?"

Replay the recorded run with `worktree: true` after checking what re-executes, and report the verdict line rather than a narrative.

**Choosing between models**

> "Would Haiku have got this right?"

Fork from the checkpoint before the failing decision, grade with the repository's own test command, and report the exit codes.

## If there is no recording

Say so plainly and offer to start one. Do not fall back to reconstructing the session - that is the failure mode this skill exists to replace.

```bash
orca record claude          # or codex, opencode, openclaw, grok
orca record generic-openai -- python my_agent.py
```

A run started with its prompt in argv (`orca record claude -- -p "..."`) replays exactly. A session someone typed into replays approximately, because those prompts were never on the wire and are recovered from the harness's own transcript; the replay output says which is which.

## Anti-patterns

**Answering a "why did you..." question from memory when a recording exists.** A fluent reconstruction that happens to be right is still the wrong process; the next one will be wrong and will read identically.

**Presenting an inferred edge as recorded.** Merging the two into one confident sentence is the specific failure this skill prevents.

**Replaying without `worktree: true`, or without reading the recorded shell commands first.** A replay is not a dry run.

**Calling a matching replay a determinism result.** The model is not re-asked; its recorded answers are served back. Whether a *fresh* run would fail the same way is a different question that replay cannot answer.

**Describing replay as a sandbox.** `egress=blocked` means model-provider egress, not network isolation. Only a network-isolated container makes it a sandbox.

**Treating an empty trace as "nothing happened".** It means the harness was not captured - usually an agent that reads no base-URL variable and pins its own origin.

## Limitations

- It only sees what was recorded; unrecorded sessions are unrecoverable.
- A typed session replays approximately rather than exactly.
- `inferred` edges are a reading of the trace, not something the recorder witnessed.
- Replay reproduces the agent's side of the run against today's world: external state the run depended on is whatever it is now.
