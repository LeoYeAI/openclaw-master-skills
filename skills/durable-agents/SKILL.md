---
name: durable-agents
description: Build autonomous multi-agent pipelines with Mastra (agents only) and Trigger.dev (all workflows and tasks). Use when creating AI agents, designing multi-stage pipelines, defining permissioned tools, structuring agent handoffs, storing agentic outputs to a database, or building durable task chains with retries and fan-out.
---

> **FIRST INSTALL:** Read and follow `setupSKILL.md` before using this skill.
> After setup is complete and verified (health check + example pipeline + smoke tests pass),
> delete this block.

---

# Durable Agents — Multi-Agent Pipeline Development Guide

Mastra (AI agent framework) + Trigger.dev (durable task execution with retries, timeouts, fan-out). Build autonomous multi-agent pipelines where each agent owns a single stage, hands off structured output to the next stage through Trigger.dev, and never holds the full context of a pipeline it doesn't own.

---

## Core Principles

1. **All intelligence lives in `AGENT.md`, not in code.** The `.ts` file is boilerplate wiring. Writing logic in the agent's TypeScript file is wrong.
2. **One agent, one job.** Each agent has a single clear responsibility. If an agent does two unrelated things, split it into two agents in a pipeline.
3. **Tasks handle durability, agents handle reasoning.** Trigger.dev tasks wrap agent calls with retries and timeouts. The agent receives input and produces output.
4. **Tools return errors, never throw.** Every tool returns `{ success, errorMessage? }` on failure. Throwing inside a tool crashes the task. Returning an error lets the agent reason about it.
5. **Type everything.** Input schemas, output schemas, tool schemas — all Zod. If it crosses a boundary (tool input, task payload, pipeline stage), it has a schema.
6. **Agents are autonomous, not scripted.** Give agents an outcome and a quality bar. Don't wire their steps in code.
7. **Pipelines break context, not logic.** Split a pipeline at the point where a different capability is needed — not to artificially divide one agent's work.
8. **All agentic I/O persists to the database.** Agent inputs, outputs, and intermediate results are stored as records. The database is the source of truth, not in-memory state.
9. **Every tool that touches a real system is permission-gated.** If a tool can post, publish, delete, charge, or trigger anything external, it must confirm intent before executing.

---

## How to Create an Agent

### 1. Create the directory

```
src/agents/{name}/
  AGENT.md
  {name}.ts
```

### 2. Write the `AGENT.md`

```markdown
# AGENT: {Name}

## Role
Who this agent is. One sentence.

## Tools
What tools it has and when to use each one. Be explicit — "Use `sqlQuery` to
check if a table exists before referencing it" not just "Has sqlQuery tool."

## Inputs
What payload it receives. Describe the shape and what each field means.

## Goal
What it must achieve. Describe the outcome, not the steps. The agent decides
how to get there. "Produce a deployment plan for the given architecture" not
"First read the architecture, then list the services, then..."

## Output Contract
Exact shape it must return. If structured output is needed, specify the JSON
schema here. Example:
  { "plan": string, "steps": string[], "risks": string[] }

## Quality Standards
What makes output good vs bad. Be specific. "Each step must be independently
executable" not "Steps should be good."

## Guardrails
What it must NOT do. "Never modify database schema directly." "Never assume
the API is authenticated unless payload says so."

## Self-Validation
Checklist the agent must verify before returning:
- Does output match the Output Contract?
- Are all required fields present?
- Does it satisfy the Quality Standards?
```

### 3. Create the agent `.ts` file

Pure boilerplate. No logic here.

```ts
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { Agent } from "@mastra/core/agent";
import { model } from "../../config/model.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const instructions = fs.readFileSync(path.join(__dirname, "AGENT.md"), "utf8");

export const myAgent = new Agent({
    id: "my-agent",
    name: "My Agent",
    instructions,
    model,
});
```

To give the agent tools:

```ts
import { myTool } from "../../tools/myTool.js";

export const myAgent = new Agent({
    id: "my-agent",
    name: "My Agent",
    instructions,
    model,
    tools: { myTool },
});
```

### 4. Register the agent

In `src/mastra/index.ts`:

```ts
import { myAgent } from "../agents/my-agent/my-agent.js";

export const mastra = new Mastra({
    agents: { plannerAgent, reviewerAgent, myAgent },
});
```

---

## How to Create a Tool

### Structure

```ts
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

export const myTool = createTool({
    id: "my-tool",
    description: "What it does and WHEN to use it",
    inputSchema: z.object({
        query: z.string().describe("The search query"),
    }),
    outputSchema: z.object({
        success: z.boolean(),
        data: z.any().optional(),
        errorMessage: z.string().optional(),
    }),
    execute: async ({ query }) => {
        try {
            const result = await doSomething(query);
            return { success: true, data: result };
        } catch (error: any) {
            return { success: false, errorMessage: error.message };
        }
    },
});
```

### Tool Rules

- **Always define `outputSchema`.** The agent uses it to understand what the tool returns.
- **Never throw from `execute`.** Return `{ success: false, errorMessage }` instead. Throwing crashes the Trigger.dev task.
- **Description is for the agent.** Write it as instructions: "Use this to check if a database table exists. Pass the table name. Returns true/false."
- **One tool does one thing.** "Query the database" not "Query the database and format the results and send an email."
- **Use `.describe()` on Zod fields** to tell the agent what to pass.
- **No side effects unless necessary.** If a tool writes, document it clearly in the description and in the agent's `AGENT.md` guardrails.

### Where to put tools

- Shared tools: `src/tools/{name}.ts`
- Agent-specific tools: `src/agents/{agentName}/tools/{name}.ts`

Register shared tools in `src/mastra/index.ts`. Agent-specific tools import directly in the agent file.

---

## Permissioned Tools for Destructive or External Actions

Any tool that touches a real system — posting to an API, publishing content, sending a message, charging a user, deleting data, triggering a webhook — must be permission-gated. Agents must not be able to fire these actions without explicit intent confirmation.

**Before building a tool that has real-world side effects, ask the user:**
- What exact action does this tool take?
- Should the agent be able to trigger this autonomously, or does a human need to approve it first?
- What are the consequences of it misfiring?
- Should this be rate-limited or scoped to specific records?

Build the answer into the tool's permission layer, not just the agent's `AGENT.md` guardrails. Guardrails are instructions; permission layers are enforcement.

### Pattern: Confirm Before Execute

For any action that can't be undone or that has cost/visibility consequences, the tool must receive an explicit `confirmed: true` in its input before it proceeds. The agent must call a read/preview tool first, then call the action tool only when it has verified the result and received `confirmed: true` from the calling context.

```ts
export const publishPostTool = createTool({
    id: "publish-post",
    description: "Publishes a post to the platform. Only call this after previewing with `previewPostTool` and receiving confirmed: true from the task payload.",
    inputSchema: z.object({
        postId: z.string().describe("ID of the post record to publish"),
        confirmed: z.boolean().describe("Must be true. Do not set this yourself — it must come from the task payload."),
    }),
    outputSchema: z.object({
        success: z.boolean(),
        publishedUrl: z.string().optional(),
        errorMessage: z.string().optional(),
    }),
    execute: async ({ postId, confirmed }) => {
        if (!confirmed) {
            return { success: false, errorMessage: "Publish requires confirmed: true in payload." };
        }
        try {
            const url = await publishPost(postId);
            return { success: true, publishedUrl: url };
        } catch (error: any) {
            return { success: false, errorMessage: error.message };
        }
    },
});
```

### Pattern: Scope to Records

Destructive or write tools must operate on a specific record ID — never on a query, a filter, or an implicit "current item." The agent must always pass the exact ID of the record it's acting on. This prevents the tool from accidentally operating on the wrong item.

```ts
inputSchema: z.object({
    recordId: z.string().describe("Exact DB ID of the record to act on. Do not pass a search query."),
})
```

### What belongs in `AGENT.md` Guardrails vs in the tool

| Concern | Where it lives |
|---|---|
| "Don't publish unless quality score > 0.8" | `AGENT.md` Guardrails |
| "Don't call this without confirmed: true" | Tool input schema + execute guard |
| "Only act on records in status: draft" | Tool execute guard (check DB before acting) |
| "Never delete more than one record per run" | Tool execute guard (enforce the count) |

---

## How to Create a Pipeline

Pipelines chain Trigger.dev tasks. Each task calls one agent and passes its output to the next. No single agent holds the full pipeline context — each stage receives only what it needs.

### 1. Create task files in `src/pipelines/tasks/`

```ts
import { task, logger } from "@trigger.dev/sdk/v3";
import { mastra } from "../../mastra/index.js";

export const planTask = task({
    id: "plan-task",
    retry: { maxAttempts: 3, minTimeoutInMs: 1000, factor: 2 },
    run: async (payload: { prompt: string }) => {
        logger.info("Running planner", { promptLength: payload.prompt.length });
        const agent = mastra.getAgent("plannerAgent");
        const response = await agent.generate(JSON.stringify(payload));
        return response.text;
    },
});
```

### 2. Create the pipeline orchestrator

In `src/pipelines/{name}.ts`, chain tasks using `triggerAndWait`:

```ts
import { planTask } from "./tasks/plan-task.js";
import { reviewTask } from "./tasks/review-task.js";

export async function runMyPipeline(input: string) {
    const planResult = await planTask.triggerAndWait({ prompt: input });
    if (!planResult.ok) throw new Error("Plan task failed");

    const reviewResult = await reviewTask.triggerAndWait({ plan: planResult.output });
    if (!reviewResult.ok) throw new Error("Review task failed");

    return { plan: planResult.output, review: reviewResult.output };
}
```

### 3. Export tasks for the worker

In `src/trigger/index.ts`:

```ts
export * from "../pipelines/tasks/plan-task.js";
export * from "../pipelines/tasks/review-task.js";
```

Every task must be exported here or the Trigger.dev worker won't discover it.

### 4. Add an API endpoint

In `src/app/index.ts`:

```ts
app.post("/my-pipeline", async (req, res) => {
    const { input } = req.body;
    const result = await runMyPipeline(input);
    res.json({ success: true, ...result });
});
```

---

## Pipeline Design: Agents vs Scripts

Not every pipeline stage needs an agent. Use agents where judgment is required. Use scripts (plain TypeScript functions or Trigger.dev tasks with no agent) where the action is deterministic.

### Example: Content Production Pipeline

```
[Director Agent]         — generates ideas, writes scripts, validates against criteria
        ↓
[Media Selector Agent]   — selects or processes media assets based on the script
        ↓
[Overlay Task]           — no agent; deterministic script that composites text onto video and stores result
```

The overlay stage has no reasoning to do. It receives exact inputs, executes a fixed operation, and stores the output. Putting an agent here adds latency and cost for no benefit.

### When to use an agent in a pipeline stage

Use an agent when the stage requires:
- Judgment or evaluation (does this meet a quality bar?)
- Selection from ambiguous options (which asset fits this script best?)
- Generation from a goal (write a script for this topic)
- Iterative refinement based on feedback

Use a plain task (no agent) when the stage is:
- A deterministic transformation (resize, encode, composite)
- A storage write (save output to DB or file system)
- A notification or webhook trigger
- A lookup with no interpretation needed

### Splitting pipeline stages

Split at the boundary where a different capability is needed — not to artificially divide one agent's work. A director agent that generates ideas, writes a script, and validates it against criteria is doing one coherent job. That's one agent, one task. The media selection is a different capability — that's the split.

---

## Pipeline Patterns

### Fan-Out (Parallel Sub-tasks)

```ts
import { tasks } from "@trigger.dev/sdk/v3";

const handles = await tasks.batchTrigger("process-item",
    items.map(item => ({ payload: { item } }))
);
```

Each sub-task runs independently with its own retries.

### Review Checkpoint

Insert a review stage between pipeline steps. Three modes:

| Mode | Behavior |
|---|---|
| `"none"` | Auto-approve. Trigger next stage immediately. |
| `"agent"` | Call a reviewer agent. If approved, continue. If rejected, feed feedback back to the previous stage for revision. |
| `"human"` | Set a status in the DB to `pending`. Return. A human reviews externally. Resume the pipeline via an API callback. |

### Retry Configuration

Every task must have explicit retry config. LLM calls are flaky — the default (no retries) means one transient API error kills the pipeline.

```ts
retry: {
    maxAttempts: 3,
    minTimeoutInMs: 1000,
    factor: 2,
}
```

---

## Database as the Agentic Record Layer

Every agent input, output, and intermediate result must be persisted to the database before the next stage runs. This is not optional. Agents operate on DB records — they do not pass raw data through in-memory pipelines.

### Why

- **Deduplication.** Check if an equivalent job has already run before triggering a new one. Compare by content hash, source ID, or a natural key.
- **Verification.** The next stage reads from the DB, not from the previous task's return value. If a record isn't in the DB, the stage doesn't proceed.
- **Record keeping.** Every generated asset, decision, and status transition is a row. You can audit, replay, and debug any run.
- **Resume on failure.** If a task retries, it checks the DB first. If the output already exists, it skips regeneration and continues.

### Pattern: Write Before Passing

Every task writes its output to the DB and returns the record ID. The next task receives the ID, reads from the DB, and operates on the record.

```ts
// Stage 1: director agent writes its output
export const scriptTask = task({
    id: "script-task",
    retry: { maxAttempts: 3, minTimeoutInMs: 1000, factor: 2 },
    run: async (payload: { projectId: string }) => {
        const existing = await db.script.findFirst({ where: { projectId: payload.projectId } });
        if (existing) return { scriptId: existing.id }; // already done, skip

        const agent = mastra.getAgent("directorAgent");
        const response = await agent.generate(JSON.stringify(payload));
        const output = ScriptOutputSchema.parse(JSON.parse(response.text));

        const record = await db.script.create({
            data: { projectId: payload.projectId, content: output.script, status: "draft" },
        });
        return { scriptId: record.id };
    },
});

// Stage 2: next agent reads by ID
export const mediaTask = task({
    id: "media-task",
    retry: { maxAttempts: 3, minTimeoutInMs: 1000, factor: 2 },
    run: async (payload: { scriptId: string }) => {
        const script = await db.script.findUniqueOrThrow({ where: { id: payload.scriptId } });
        const agent = mastra.getAgent("mediaSelectorAgent");
        const response = await agent.generate(JSON.stringify({ script: script.content }));
        const output = MediaOutputSchema.parse(JSON.parse(response.text));

        const record = await db.mediaSelection.create({
            data: { scriptId: payload.scriptId, assetIds: output.assetIds, status: "selected" },
        });
        return { mediaSelectionId: record.id };
    },
});
```

### Pattern: Status Transitions as Pipeline Control

Store a `status` field on every record. Use it to gate pipeline stages and drive human review checkpoints.

| Status | Meaning |
|---|---|
| `pending` | Created, not yet processed |
| `processing` | Task is running |
| `draft` | Agent output produced, not reviewed |
| `approved` | Passed review (agent or human) |
| `rejected` | Failed review, needs revision |
| `published` | Final action taken |
| `failed` | Unrecoverable error |

```ts
await db.script.update({
    where: { id: scriptId },
    data: { status: "processing" },
});
// ... agent call ...
await db.script.update({
    where: { id: scriptId },
    data: { status: "draft", content: output.script },
});
```


## Keeping Agents Autonomous

Define the destination and the quality bar. Don't specify how to get there.

**Wrong — micromanaging the agent:**
```
1. Read the input
2. Extract the requirements
3. For each requirement, write a task
4. Format the tasks as a numbered list
5. Return the list
```

**Right — defining the outcome:**
```
## Goal
Produce a technical implementation plan for the given objective.

## Output Contract
{ "tasks": [{ "title": string, "description": string, "dependencies": string[] }] }

## Quality Standards
- Each task must be independently executable by a developer
- Dependencies must reference other tasks by title
- No task should take more than 4 hours of work
```

---

## Type Enforcement

### Task Payloads

Always type the `run` function parameter:

```ts
run: async (payload: { prompt: string; maxTokens?: number }) => {
```

### Structured Output from Agents

Define the exact schema in the `AGENT.md` Output Contract section, then validate with Zod on receipt:

```ts
const OutputSchema = z.object({
    tasks: z.array(z.object({
        title: z.string(),
        description: z.string(),
        dependencies: z.array(z.string()),
    })),
});

const response = await agent.generate(JSON.stringify(payload));
const parsed = OutputSchema.parse(JSON.parse(response.text));
```

If parsing fails, the task throws, Trigger.dev retries with the same input, and the agent produces output again.

### Tool Schemas

Always define both `inputSchema` and `outputSchema` on tools. The agent uses these to understand what arguments to pass and what it will receive back.

---

## Key Rules

1. All intelligence lives in `AGENT.md`, not in code
2. Agent `.ts` files are boilerplate wiring only — no logic
3. Tools return `{ success, errorMessage }` on failure — never throw
4. Task wrappers handle durability, agents handle reasoning
5. Self-validation checklist in `AGENT.md` is mandatory for structured output agents
6. Every Trigger.dev task has explicit `retry` config
7. Every task is exported from `src/trigger/index.ts`
8. One model config for all agents — `src/config/model.ts`
9. Pipeline stages use `triggerAndWait` for sequential, `batchTrigger` for parallel
10. Check `result.ok` after every `triggerAndWait` — don't assume success
11. Every agent output is written to the DB before the next stage runs — never pass raw data between tasks
12. Tasks that would duplicate work must check the DB first and skip if already done
13. Every tool that takes a real-world action requires `confirmed: true` in the input and must verify it before executing
14. Not every pipeline stage needs an agent — use plain tasks for deterministic operations
