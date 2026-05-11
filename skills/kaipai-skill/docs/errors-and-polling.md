# Errors, polling, and environment tuning

This document expands on **Step 3** in [SKILL.md](../SKILL.md) for long-running Kaipai jobs.

**Operators (one line):** Video tasks → **`spawn-run-task`** + `sessions_spawn` (don’t block the main session on `run-task` for `videoscreenclear` / `hdvideoallinone`); if a run was cut off or the user asks for status → **`last-task`** / **`history`** then **`query-task --task-id`** — never duplicate **`run-task`** for the same job.

`kaipai_ai.py` flushes JSON lines to stdout after each `print`; you can also set **`PYTHONUNBUFFERED=1`** if your host buffers piped stdout unusually.

## Checklist: agent keeps re-submitting the “same” job

Use this when the model appears to loop on **`run-task`** or repeat **`spawn-run-task`** + **`sessions_spawn`** for the same user request (each new **`run-task`** is a **new** billable job; **`query-task`** is not).

1. **Final JSON on stdout?** If the tool or session ends with **no** closing JSON while the job was still running, the agent often retries. Check host **tool timeout**, **session / turn limits**, and **OOM**.
2. **Video path?** For **`videoscreenclear`** / **`hdvideoallinone`**, the main session should use **`spawn-run-task`** + **`sessions_spawn`**, not a blocking **`run-task`**, and **`runTimeoutSeconds`** should stay at the payload default (**3600**) unless you accept timeout risk.
3. **`task_id` in stderr?** Progress lines may include **`task_id=...`**. If present, **`query-task --task-id`** — do **not** submit **`run-task`** again for that id.
4. **`last-task` after async submit:** For async jobs, **`last_task.json`** is updated **as soon as the server returns a `task_id`** ( **`skill_status`: `"polling"`** ) and again when the run finishes. If polling is cut off, run **`last-task`** then **`query-task`** with that **`task_id`**.
5. **Quota errors (60001 / 60002)?** Fix membership or credits first; repeating **`run-task`** will not help.

## Video tasks and wall time

Tasks **`videoscreenclear`** and **`hdvideoallinone`** are asynchronous. The client polls until completion; wall time varies (often on the order of minutes to tens of minutes).

## Stderr progress (`[kaipai-ai]`)

While polling, `kaipai_ai.py` may print throttled **`[kaipai-ai]`** lines to **stderr** (`poll i/N`, `api_status`, `elapsed`). Hosts that merge stderr into the chat transcript will show progress.

- Progress lines are **sampled**: poll **1**, then every **3rd** poll (3, 6, 9, …), plus the last poll. Skipped indices still run, so **`elapsed` can jump** when each sleep step is large (e.g. 30s from **`MT_AI_POLL_EXTEND_STEP_MS`**).
- Set **`MT_AI_PROGRESS=0`** to silence those lines.

## Poll schedule extension

Server `token_policy` **`status_query.durations`** values are in **milliseconds** between polls.

- If their **sum is below 1 hour**, the client **extends** the schedule to **at least ~1 hour** of cumulative sleep before giving up.
- If the server sum is **already ≥ 1 hour**, that longer schedule is used unchanged.
- A finished task **returns as soon as** the status API says done (no need to wait the full hour).

Overrides:

| Variable | Meaning |
|----------|---------|
| **`MT_AI_POLL_MIN_TOTAL_MS`** | Minimum total poll sleep budget in ms; `0` or `false` = use server list only |
| **`MT_AI_POLL_EXTEND_STEP_MS`** | Default `30000` (ms), min `1000` — gap for each appended step when extending |
| **`MT_AI_POLL_MAX_CONSECUTIVE_ERRORS`** | Default `5` — stop after this many consecutive status-query errors (network / non-JSON / HTTP) |
| **`MT_AI_TASK_FAILURE_STATUSES`** | Default `3` — comma-separated ints; matching `data.status` = immediate failure; empty = disable |

## Failure JSON and exit codes

If polling exhausts, repeated query errors occur, or the API reports a terminal failure, stdout is JSON with **`skill_status`: `"failed"`** and an **`error`** field such as `poll_timeout`, `poll_aborted`, or `task_failed`. **`run-task` exits non-zero** (and on invalid stdout shape).

Status queries treat **`meta.code` ≠ 0** as failure unless **`MT_AI_IGNORE_META_CODE=1`** (escape hatch if your tenant sends non-zero codes while tasks are still running).

## Quota consume (`/skill/consume.json`) before `run-task`

After input upload, **`run-task`** calls **`POST /skill/consume.json`**. A **new** job must go through **`run-task`** so **consume and algorithm submit stay in order** — **do not** hand-craft HTTP to invoke/AIGC endpoints to skip consume. **`query-task`** resumes polling for an existing **`task_id`** only; it does **not** replace **`run-task`** for a new submission.

On consume failure, stdout JSON includes **`skill_status`: `"failed"`**, **`failure_stage`: `"consume_quota"`**, **`api_code`**, and **`agent_instruction`**. Map **`error`** as follows:

| `api_code` | `error` | Meaning for the agent |
|------------|---------|------------------------|
| **60001** | `membership_required` | User needs membership/subscription — not fixable by changing `--task` / **`--params`** alone. If the API **`detail`** / `msg` contains an `https` link, stdout may include **`pricing_url`** (parsed from that text); the agent **must** surface that link or the full **`detail`** to the user. |
| **60002** | `credit_required` | User needs more credits or a subscription. Same as 60001: follow server **`detail`**; use JSON **`pricing_url`** when present (extracted from **`detail`**), otherwise paste/quote **`detail`** so links in the API message are visible. |
| **Other** (including **-1** if the server sent a non-numeric code) | `consume_param_error` | Treat as invocation/parameters: check **`--task`**, **`--input`**, **`--params`** against SKILL.md and remote config. **Do not** instruct recharge unless **`api_code`** is 60002. |

## SIGKILL / host timeout

If the OS or host kills the process (**SIGKILL**, OOM, or a **shorter outer timeout** than the job), Python may not flush a final JSON line — the agent may see stderr progress only or truncated stdout. Use **`spawn-run-task`** with the payload’s **`runTimeoutSeconds`** (default **3600**) and **do not shorten** it when passing `sessions_spawn_args` to the tool.

## Shorter outer / session timeouts

Some stacks cap **how long one agent turn, tool call, or blocking shell** may run. That cap is separate from **`runTimeoutSeconds`** and from the client’s poll schedule. If it fires before the job finishes, you may see **no final JSON** on stdout while **stderr** can still show `[kaipai-ai]` lines and **`task_id=...`**.

**Recovery:** use **`last-task`** / **`history`**, read **`task_id`** from stderr or any partial JSON, then **`query-task`** — do **not** re-run **`run-task`** for the same id. Video tasks should use **`spawn-run-task`** in the main session so it is not blocked on polling. Host-side limits (config names vary) can be raised if appropriate; they do not replace **`spawn-run-task`** for video in the main session.

## Resuming without re-submitting

When you already have a full **`task_id`**, use **`query-task`** — do **not** run **`run-task`** again for that id. See SKILL.md **§3c**.
