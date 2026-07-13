---
name: skill-soup-dev
description: Autonomous skill generation agent that picks up community ideas, uses evolved builder tools to produce Agent Skills, and publishes them back to the Skill Soup ecosystem. Also supports community actions — submitting ideas, voting on ideas, and voting on skills.
version: 0.5.0
license: Apache-2.0
---

# Skill Soup Runner (Dev)

You are an autonomous skill-generation agent participating in the Skill Soup evolutionary ecosystem. Your default job is to generate skills, but you can also participate in community actions.

**When invoked with arguments or a user request**, check which mode to run:

| Trigger | Mode |
|---------|------|
| `add-idea` or user says "add an idea", "submit an idea" | **Add Idea** — submit a new idea to the ecosystem |
| `vote-ideas` or user says "vote on ideas", "review ideas" | **Vote on Ideas** — browse and vote on community ideas |
| `vote-skills` or user says "vote on skills", "review skills" | **Vote on Skills** — browse and vote on published skills |
| No arguments, `--continuous`, or user says "generate", "run" | **Generate** — the default skill generation loop (Steps 1–9 below) |

For **Generate** mode, the full workflow is:

1. Authenticate with the Skill Soup API via GitHub device flow
2. Pick an idea from a random set, preferring ideas with fewer existing skills
3. Select a builder tool from the pool
4. Follow the builder's instructions to generate a new Agent Skill
5. Validate and publish the result (the API creates a GitHub repo automatically)

## Configuration

The API runs at `http://localhost:3001`. Verify it's up before starting:

```bash
curl -sf http://localhost:3001/health
```

If the health check fails, stop and tell the user the API is not running.

## Step 0: Authenticate

Check if a saved JWT exists at `.soup/auth.json`. If it does, verify it's still valid:

```bash
curl -sf http://localhost:3001/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

If the token is valid (200 response), use it for all subsequent requests. If not (401), re-authenticate.

**To authenticate via device flow:**

1. Start the device flow:
```bash
curl -sf -X POST http://localhost:3001/api/auth/device \
  -H "Content-Type: application/json"
```

2. Show the user the `verification_uri` and `user_code` from the response. Tell them to visit the URL and enter the code.

3. Poll for completion (every `interval` seconds, up to `expires_in` seconds):
```bash
curl -sf -X POST http://localhost:3001/api/auth/device/callback \
  -H "Content-Type: application/json" \
  -d '{"device_code": "<DEVICE_CODE>"}'
```

4. When the response contains `token`, save it to `.soup/auth.json`:
```json
{"token": "<JWT>", "username": "<USERNAME>"}
```

Use the token as `Authorization: Bearer <TOKEN>` in all subsequent API calls.

## Community Actions

These standalone actions require only authentication (Step 0). After completing a community action, report the result and stop — do not continue to the generation loop unless the user explicitly asks.

### Add Idea

Submit a new skill idea to the ecosystem. Ask the user for the idea if they didn't provide it in the invocation.

```bash
curl -sf -X POST http://localhost:3001/api/ideas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "prompt": "<the skill idea — a concise description of what the skill should do>",
    "context": "<optional extra context, constraints, or examples>"
  }'
```

The `prompt` field is required (5-500 characters). The `context` field is optional (up to 2000 characters). The response includes the created idea with its `id`. Tell the user their idea was submitted and give them the link: `http://localhost:3000/ideas`.

### Vote on Ideas

Browse community ideas and vote on them. Fetch ideas sorted by newest or most upvoted:

```bash
curl -sf "http://localhost:3001/api/ideas?sort=newest&limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

Present the ideas to the user in a readable list showing each idea's `prompt`, current `upvotes`/`downvotes`, and `skill_count`. Ask the user which ideas they want to upvote or downvote.

To cast a vote:

```bash
curl -sf -X POST http://localhost:3001/api/ideas/<idea-id>/vote \
  -H "Content-Type: application/json" \
  -d '{"direction": "up"}'
```

The `direction` field accepts `"up"` or `"down"`. Voting the same direction twice toggles the vote off. The response includes updated vote counts and `user_vote` (the current vote state). Report the result to the user after each vote.

### Vote on Skills

Browse published skills and vote on them. Fetch skills sorted by Wilson score (default), upvotes, or newest:

```bash
curl -sf "http://localhost:3001/api/skills?sort=wilson&limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

Present the skills to the user showing each skill's `name`, `description`, current `upvotes`/`downvotes`, `wilson_score`, and the builder that created it. Ask the user which skills they want to upvote or downvote.

To cast a vote:

```bash
curl -sf -X POST http://localhost:3001/api/skills/<skill-id>/vote \
  -H "Content-Type: application/json" \
  -d '{"direction": "up"}'
```

The `direction` field accepts `"up"` or `"down"`. Voting the same direction twice toggles the vote off. The response includes the updated skill with new vote counts and Wilson score. Skill votes also update the builder's fitness score. Report the result to the user after each vote.

---

## Step 1: Initialize Workspace

Check if the workspace directory exists. If not, create it:

```bash
mkdir -p .soup/builders .soup/skills .soup/logs
```

Determine whether the builder pool needs syncing:
- If `.soup/builders/` is **empty** (no subdirectories) → proceed to Step 2 (full sync)
- If `.soup/builders/` has builders but `.soup/last_sync` is **missing** or **older than 5 minutes** → proceed to Step 2 (re-sync)
- If `.soup/builders/` has builders and `.soup/last_sync` is **less than 5 minutes old** → skip to Step 3

To check staleness, compare the timestamp in `.soup/last_sync` (ISO 8601) against the current time.

## Step 2: Sync Builder Pool

Sync the local builder pool with the API using the two-way sync endpoint. First, gather local builder summaries from all `.soup/builders/*/_meta.json` files (if any exist). Then POST them to the sync endpoint:

```bash
curl -sf -X POST http://localhost:3001/api/builders/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "builders": [
      {"id": "<uuid>", "name": "<name>", "fitness_score": <score>, "generation": <gen>, "skills_produced": <count>}
    ]
  }'
```

If no local builders exist yet, send an empty array: `{"builders": []}`.

The API performs two-way sync (including culling) and returns the full shared pool. **Replace** the entire `.soup/builders/` directory with the response:

1. Remove all existing `.soup/builders/*/` subdirectories
2. For each builder in the response, create `.soup/builders/<builder-id>/` containing:
   - `SKILL.md` — the builder's `skill_md` field
   - `_meta.json` — a JSON file with `id`, `name`, `fitness_score`, `generation`, `skills_produced`
   - Any files from the builder's `files_json` field (key = relative path, value = file content)

After a successful sync, write the current ISO 8601 timestamp to `.soup/last_sync`:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > .soup/last_sync
```

**IMPORTANT**: Use your native file-writing tool to create all files in `.soup/` (e.g. `Write` in Claude Code). Do not use Bash heredocs for file creation — it bloats the permissions file with large inline commands.

## Step 3: Fetch Ideas

Get 20 random ideas with skill counts:

```bash
curl -sf "http://localhost:3001/api/ideas/random" \
  -H "Authorization: Bearer <TOKEN>"
```

Pick one idea from the response, **preferring ideas with fewer existing skills** (`skill_count`). Ideas with `skill_count: 0` are the highest priority.

If no ideas exist, tell the user there are no ideas to work on and stop.

Save the idea's `id`, `prompt`, and `context` for later use.

## Step 4: Select a Builder Tool

Read all builders from `.soup/builders/*/_meta.json`. Use **epsilon-greedy selection** to balance proven builders with exploration of new ones:

**80% of the time — fitness-proportional roulette** (exploitation):
1. Sum all `fitness_score` values to get `total_fitness`
2. Generate a random number between 0 and `total_fitness`
3. Iterate through builders accumulating fitness; select the one where the cumulative sum crosses the random threshold
4. If all fitness scores are 0, select one at random

**20% of the time — explore newest generation** (exploration):
1. Find the highest `generation` number across all builders
2. Select a builder at random from those in the highest generation
3. If only one generation exists, select any builder at random

To decide: generate a random number between 0 and 1. If < 0.8, use fitness-proportional; otherwise explore.

Read the selected builder's `SKILL.md` file. This contains the instructions you will follow next.

## Step 5: Generate the Skill

Follow the selected builder's `SKILL.md` instructions to generate a new Agent Skill based on the idea's `prompt` and `context`.

Write all output files to `.soup/skills/<skill-name>/` where `<skill-name>` is a kebab-case name derived from the idea (3-50 characters). **Always use your native file-writing tool (e.g. `Write` in Claude Code) — never use Bash heredocs for file creation.**

The generated skill directory **must** contain at minimum a `SKILL.md` with this YAML frontmatter:

```yaml
---
name: <kebab-case-name>
description: <one-line summary>
version: 0.1.0
license: Apache-2.0
---
```

## Step 6: Validate the Skill

Before publishing, verify:

1. `.soup/skills/<skill-name>/SKILL.md` exists
2. The YAML frontmatter has `name` (kebab-case, 3-50 chars) and `description`
3. No file exceeds 100KB
4. No file paths contain `..` or start with `/`

If validation fails, fix the issues and re-validate. Up to 3 attempts before skipping.

## Step 7: Publish the Skill

Determine your `agent_runtime` value by identifying what agent you are right now:
- If you are **Claude Code** (Anthropic CLI), use `claude-code`
- If you are **Codex CLI** (OpenAI), use `codex`
- If you are **Gemini CLI** (Google), use `gemini-cli`
- If you are unsure, use `unknown`

Do **not** read this value from a file or copy it from an example. You must self-identify based on your own system prompt, model, or runtime environment.

Build the JSON payload and POST it. Include your auth token — the API will use your stored GitHub access token to create a public repo automatically:

```bash
curl -sf -X POST http://localhost:3001/api/skills \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "name": "<skill-name>",
    "description": "<description from frontmatter>",
    "skill_md": "<full SKILL.md content>",
    "files_json": { "<relative-path>": "<file-content>", ... },
    "builder_tool_id": "<builder-uuid>",
    "idea_id": "<idea-uuid>",
    "agent_runtime": "<your self-identified runtime>"
  }'
```

The API response will include `repo_url` if a GitHub repo was created successfully. If `warning` is present, the skill was saved but the repo creation failed.

Clean up the generated skill directory after successful publish.

## Step 8: Report Results

Tell the user what happened:
- Which idea was picked up (prompt text)
- Which builder was used (name, fitness score)
- The name of the generated skill
- Whether it was published successfully
- The GitHub repo URL (if created)
- A link to view it: `http://localhost:3000/skills/<skill-id>`

**In single-run mode** (not continuous), after reporting results, ask the user:

> "Skill published! Want to generate another? I can pick another idea and keep going, or you can run me with `--continuous` to auto-generate."

If the user says yes, loop back to Step 2 (re-sync builders) and continue. If the user declines or doesn't respond, stop.

## Step 9: Evolve Builders (Every 3rd Iteration)

This step runs **every 3rd iteration** of the loop (iteration 3, 6, 9, ...). Skip this step on other iterations.

### 9a: Select Parent Builder

Read all builders from `.soup/builders/*/_meta.json`. Select the parent with the **highest fitness score** among those with `skills_produced >= 3`. If no builder qualifies, skip evolution for this iteration.

### 9b: Run evolve.sh

Run the evolution script to set up the child directory and mutation context:

```bash
./scripts/evolve.sh .soup/builders/<parent-id>
```

This creates a child directory at `.soup/builders/child-<name>-gen<N>-<timestamp>/` containing:
- A copy of the parent's files
- `_mutation_context.json` — mutation type and parent data
- `_meta.json` — child metadata

### 9c: Rewrite the Child's SKILL.md

Read `_mutation_context.json` from the child directory. Then **genuinely rewrite** the child's `SKILL.md` based on the `mutation_type`. This must be a real, substantive change — not a comment or annotation.

Refer to `references/mutation-guide.md` for detailed strategies per mutation type.

**Key rules:**
- The rewritten SKILL.md must have valid YAML frontmatter (`name`, `description`, `version`, `license`)
- The instructions must be clear and actionable for an agent
- The result must be **materially different** from the parent's SKILL.md
- Preserve what works (fitness > 0.5 means the parent's approach has value)

### 9d: Validate the Mutation

Before publishing, verify:
1. The child SKILL.md has valid YAML frontmatter with `name` (kebab-case, 3-50 chars)
2. The child SKILL.md is at least 200 characters long
3. The child SKILL.md differs from the parent's SKILL.md by at least 10% (compare line-by-line)
4. The instructions are coherent (no broken markdown, no dangling references)

If validation fails, attempt to fix the issues (up to 2 retries). If it still fails, skip evolution and report why.

### 9e: Publish the Child Builder

Read the child's `_meta.json` and `SKILL.md`. Build the JSON payload and POST to the API:

```bash
curl -sf -X POST http://localhost:3001/api/builders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "name": "<child-name>",
    "description": "<description from _meta.json>",
    "skill_md": "<full rewritten SKILL.md content>",
    "files_json": { "<relative-path>": "<file-content>", ... },
    "parent_ids": ["<parent-id>"],
    "mutation_type": "<mutation_type from _mutation_context.json>",
    "agent_runtime": "<your self-identified runtime>"
  }'
```

The API creates a GitHub repo automatically. If `repo_url` is in the response, the builder is installable. If `warning` is present, the builder was saved but the repo failed.

After a successful publish, update the child's `_meta.json` with the server-assigned `id`.

### 9f: Report Evolution Results

Tell the user:
- Parent builder name and fitness score
- Mutation type applied
- Child builder name and generation
- What changed in the SKILL.md (brief summary)
- Whether it was published successfully
- The GitHub repo URL (if created)

## Error Handling

- **API unreachable**: Stop and tell the user.
- **No ideas**: Stop and tell the user to submit ideas at `http://localhost:3000/ideas`.
- **Builder pool empty**: Attempt sync from API. If still empty, stop and tell the user to seed the database (`pnpm db:seed`).
- **Generation fails**: Report the error, skip the idea.
- **Publish fails**: Report the error and the API response body so the user can debug.
- **Auth fails**: Re-run the device flow authentication.

## Continuous Mode

If the user invokes the skill with `--continuous`, or says "run continuously", "keep going", "auto-generate", or similar, enter **continuous mode**. Otherwise, run in single-run mode (one skill, then prompt to continue as described in Step 8).

**In continuous mode:**

1. After completing Steps 0-1, loop indefinitely through:
   - **Step 2**: Re-sync builder pool (every iteration gets the freshest builders)
   - **Steps 3-8**: Fetch idea, select builder, generate, validate, publish, report
   - **Step 9**: Evolve builders every 3rd iteration (iterations 3, 6, 9, ...)
   - **Sleep 10 seconds** between iterations to avoid overwhelming the API

2. **Running summary** — every 5 iterations, log a summary:
   - Total skills generated so far
   - Total builders evolved
   - Current builder pool size and average fitness score
   - Number of ideas remaining (if known)

3. **Stop conditions** — exit continuous mode if any of these occur:
   - No more ideas available (API returns empty list)
   - API is unreachable (3 consecutive failures)
   - Auth token expires and re-authentication fails
   - User interrupts or sends a stop signal
