---
name: til
description: >
  Capture and manage TIL (Today I Learned) entries on OpenTIL.
  Use /til <content> to capture, /til to extract insights from conversation,
  or /til list|publish|edit|search|delete|status|sync|tags|categories|batch to
  manage entries -- all without leaving the CLI.
homepage: https://opentil.ai
license: MIT
metadata:
  author: opentil
  version: "1.11.0"
  primaryEnv: OPENTIL_TOKEN
---

# til

Capture and manage "Today I Learned" entries on OpenTIL -- from drafting to publishing, all within the CLI.

## Setup

1. Go to https://opentil.ai/dashboard/settings/tokens and create a Personal Access Token with `read:entries`, `write:entries`, and `delete:entries` scopes
2. Copy the token (starts with `til_`)
3. Set the environment variable:

```bash
export OPENTIL_TOKEN="til_xxx"
```

### Token Resolution

Token resolution order:
1. `$OPENTIL_TOKEN` environment variable (overrides all profiles)
2. `~/.til/credentials` file — active profile's token (created by `/til auth`)

If neither is set, entries are saved locally to `~/.til/drafts/`.

### Credential File Format

`~/.til/credentials` stores named profiles in YAML:

```yaml
active: personal
profiles:
  personal:
    token: til_abc...
    nickname: hong
    site_url: https://opentil.ai/@hong
    host: https://opentil.ai
  work:
    token: til_xyz...
    nickname: hong-corp
    site_url: https://opentil.ai/@hong-corp
    host: https://opentil.ai
```

- `active`: name of the currently active profile
- `profiles`: map of profile name → credentials
- Each profile stores: `token`, `nickname` (from API), `site_url`, `host`

**Backward compatibility**: If `~/.til/credentials` contains a plain text token (old format), silently migrate it to a `default` profile in YAML format and write back.

## Subcommand Routing

The first word after `/til` determines the action. Reserved words route to management subcommands; anything else is treated as content to capture.

| Invocation | Action |
|------------|--------|
| `/til list [drafts\|published\|all]` | List entries (default: drafts) |
| `/til publish [<id> \| last]` | Publish an entry |
| `/til unpublish <id>` | Unpublish (revert to draft) |
| `/til edit <id> [instructions]` | AI-assisted edit |
| `/til search <keyword>` | Search entries by title |
| `/til delete <id>` | Delete entry (with confirmation) |
| `/til status` | Show site status and connection info |
| `/til sync` | Sync local drafts to OpenTIL |
| `/til tags` | List site tags with usage counts |
| `/til categories` | List site categories |
| `/til batch <topics>` | Batch-capture multiple TIL entries |
| `/til auth` | Connect OpenTIL account (browser auth) |
| `/til auth switch [name]` | Switch active profile (by profile name or @nickname) |
| `/til auth list` | List all profiles |
| `/til auth remove <name>` | Remove a profile |
| `/til auth rename <old> <new>` | Rename a profile |
| `/til <anything else>` | Capture content as a new TIL |
| `/til` | Extract insights from conversation (multi-candidate) |

Reserved words: `list`, `publish`, `unpublish`, `edit`, `search`, `delete`, `status`, `sync`, `tags`, `categories`, `batch`, `auth`.

## Reference Loading

⚠️ DO NOT read reference files unless specified below. SKILL.md contains enough inline context for most operations.

### On subcommand dispatch (load before execution):

| Subcommand | References to load |
|------------|--------------------|
| `/til <content>` | none |
| `/til` (extract from conversation) | none |
| `/til list\|status\|tags\|categories` | [references/management.md](references/management.md) |
| `/til publish\|unpublish\|edit\|search\|delete\|batch` | [references/management.md](references/management.md) |
| `/til sync` | [references/management.md](references/management.md), [references/local-drafts.md](references/local-drafts.md) |
| `/til auth` | [references/management.md](references/management.md), [references/api.md](references/api.md) |
| `/til auth switch\|list\|remove\|rename` | [references/management.md](references/management.md) |

### On-demand (load only when the situation arises):

| Trigger | Reference to load |
|---------|-------------------|
| API returns non-2xx after inline error handling is insufficient | [references/api.md](references/api.md) |
| Auto-detection context (proactive TIL suggestion) | [references/auto-detection.md](references/auto-detection.md) |
| No token found (first-run local fallback) | [references/local-drafts.md](references/local-drafts.md) |

## API Quick Reference

**Create and publish an entry:**

```bash
curl -X POST "https://opentil.ai/api/v1/entries" \
  -H "Authorization: Bearer $OPENTIL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": {
      "title": "Go interfaces are satisfied implicitly",
      "content": "In Go, a type implements an interface...",
      "summary": "Go types implement interfaces implicitly by implementing their methods, with no explicit declaration needed.",
      "tag_names": ["go", "interfaces"],
      "published": true,
      "lang": "en"
    }
  }'
```

**Key create parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | yes | Markdown body (max 100,000 chars) |
| `title` | string | no | Entry title (max 200 chars). Auto-generates slug. |
| `tag_names` | array | no | 1-3 lowercase tags, e.g. `["go", "concurrency"]` |
| `published` | boolean | no | `false` for draft (default), `true` to publish immediately |
| `lang` | string | no | Language code: `en`, `zh-CN`, `zh-TW`, `ja`, `ko`, etc. |
| `slug` | string | no | Custom URL slug. Auto-generated from title if omitted. |
| `visibility` | string | no | `public` (default), `unlisted`, or `private` |
| `summary` | string | no | AI-generated summary for listing pages (max 500 chars) |

**Management endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/entries?status=draft&q=keyword` | GET | List/search entries |
| `/entries/:id` | GET | Get a single entry |
| `/entries/:id` | PATCH | Update entry fields |
| `/entries/:id` | DELETE | Permanently delete entry |
| `/entries/:id/publish` | POST | Publish a draft |
| `/entries/:id/unpublish` | POST | Revert to draft |
| `/site` | GET | Site info (username, entry counts, etc.) |
| `/tags?sort=popular` | GET | List tags with usage counts |
| `/categories` | GET | List categories with entry counts |

> Full parameter list, response format, and error handling: see references/api.md

## Execution Flow

Every `/til` invocation follows this flow:

1. **Generate** -- craft the TIL entry (title, body, summary, tags, lang)
2. **Check token** -- resolve token (env var → active profile in `~/.til/credentials`)
   - If `~/.til/credentials` exists in old plain-text format, migrate to YAML `default` profile first
   - **Found** -> POST to API with `published: true` -> show published URL
   - **Not found** -> save to `~/.til/drafts/` -> show first-run guide with connect prompt
   - **401 response** -> save locally -> inline re-authentication (see Error Handling):
     - Token from `~/.til/credentials` (active profile) or no prior token: prompt to reconnect via device flow → on success, update the active profile's token and auto-retry the original operation
     - Token from `$OPENTIL_TOKEN` env var: cannot auto-fix — guide user to update/unset the variable
3. **Show identity** -- when ≥2 profiles are configured, include `Account: @nickname (profile_name)` in result messages so the user always knows which account was used
4. **Never lose content** -- the entry is always persisted somewhere
5. **On API failure** -> save locally as draft (fallback unchanged)

## `/til <content>` -- Explicit Capture

The user's input is **raw material** -- a seed, not the final entry. Generate a complete TIL from it:

- Short input (a sentence or phrase) -> expand into a full entry with context and examples
- Long input (a paragraph or more) -> refine and structure, but preserve the user's intent

**Steps:**

1. Treat the user's input as a seed -- craft a complete title + body from it
2. Generate a concise title (5-15 words) in the same language as the content
3. Write a self-contained Markdown body (see Content Guidelines below)
4. Generate a summary (see Summary Guidelines below)
5. Infer 1-3 lowercase tags from technical domain (e.g. `rails`, `postgresql`, `go`)
6. Detect language -> set `lang` (`en`, `zh-CN`, `zh-TW`, `ja`, `ko`, `es`, `fr`, `de`, `pt-BR`, `pt`, `ru`, `ar`, `bs`, `da`, `nb`, `pl`, `th`, `tr`, `it`)
7. Follow Execution Flow above (check token -> POST or save locally)

No confirmation needed -- the user explicitly asked to capture. Execute directly.

## `/til` -- Extract from Conversation

When `/til` is used without arguments, analyze the current conversation for learnable insights.

**Steps:**

1. Scan the conversation for knowledge worth preserving -- surprising facts, useful techniques, debugging breakthroughs, "aha" moments
2. Identify **all** TIL-worthy insights (not just one), up to 5
3. Branch based on count:

**0 insights:**
```
No clear TIL insights found in this conversation.
```

**1 insight:** Generate the full draft (title, body, tags), show it, ask for confirmation. On confirmation -> follow Execution Flow.

**2+ insights:** Show a numbered list (max 5), let the user choose:
```
Found 3 TIL-worthy insights:

  1. Go interfaces are satisfied implicitly
  2. PostgreSQL JSONB arrays don't support GIN @>
  3. CSS :has() enables parent selection

Which to capture? (1/2/3/all/none)
```

- Single number -> generate draft for that insight, show confirmation, proceed
- Comma-separated list (e.g. `1,3`) -> generate drafts for selected, show all for confirmation, POST sequentially
- `all` -> generate drafts for each, show all for confirmation, POST sequentially
- `none` -> cancel

4. For each selected insight, generate a standalone TIL entry following Content Guidelines
5. **Show the generated entry to the user and ask for confirmation before proceeding**
6. On confirmation -> follow Execution Flow above (check token -> POST or save locally)

## Auto-Detection

When working alongside a user, proactively detect moments worth capturing as TIL entries.

### When to Suggest

Suggest when the conversation produces a genuine "aha" moment — something surprising, non-obvious, or worth remembering. Examples:

- Debugging uncovered a non-obvious root cause
- A language/framework behavior contradicted common assumptions
- Refactoring revealed a clearly superior pattern
- Performance optimization yielded measurable improvement
- An obscure but useful tool flag or API parameter was discovered
- Two technologies interacting produced unexpected behavior

Do NOT suggest for: standard tool usage, documented behavior, typo-caused bugs, or widely known best practices.

### Rate Limiting

1. **Once per session** — after suggesting once (accepted or declined), never suggest again
2. **Natural pauses only** — suggest at resolution points or task boundaries, never mid-problem-solving
3. **Respect rejection** — if declined, move on without persuasion

### Suggestion Format

Append at the end of your normal response. Never interrupt workflow.

**Template:**
```
💡 TIL: [concise title of the insight]
   Tags: [tag1, tag2] · Capture? (yes/no)
```

**Example** (at the end of a debugging response):
```
...so the fix is to close the channel before the goroutine exits.

💡 TIL: Unclosed Go channels in goroutines cause silent memory leaks
   Tags: go, concurrency · Capture? (yes/no)
```

### Capture Flow

Auto-detected TILs bypass the extract flow. The suggestion itself is the candidate.

1. User replies `yes` / `y` / `ok` / `sure` → agent generates full entry (title, body, tags, lang) from the suggested insight → follows Execution Flow (POST or save locally)
2. User replies `no` / ignores / continues other topic → move on, do not ask again

Non-affirmative responses (continuing the conversation about something else) are treated as implicit decline.

> Detailed trigger examples, state machine, and anti-patterns: see references/auto-detection.md

## Management Subcommands

Management subcommands require a token. There is no local fallback -- management operations need the API.

### `/til list [drafts|published|all]`

List entries. Default filter: `drafts`.

- API: `GET /entries?status=<filter>&per_page=10`
- Display as a compact table with short IDs (last 8 chars, prefixed with `...`)
- Show pagination info at the bottom

### `/til publish [<id> | last]`

Publish a draft entry.

- `last` resolves to the most recently created entry in this session (tracked via `last_created_entry_id` set on every successful POST)
- Fetch the entry first, show title/tags, ask for confirmation
- On success, display the published URL
- If already published, show informational message (not an error)

### `/til unpublish <id>`

Revert a published entry to draft.

- Fetch the entry first, confirm before unpublishing
- If already a draft, show informational message

### `/til edit <id> [instructions]`

AI-assisted editing of an existing entry.

- Fetch the full entry via `GET /entries/:id`
- Apply changes based on instructions (or ask what to change if none given)
- Show a diff preview of proposed changes
- On confirmation, `PATCH /entries/:id` with only the changed fields

### `/til search <keyword>`

Search entries by title.

- API: `GET /entries?q=<keyword>&per_page=10`
- Same compact table format as `list`

### `/til delete <id>`

Permanently delete an entry.

- Fetch the entry, show title and status
- Double-confirm: "This cannot be undone. Type 'delete' to confirm."
- On confirmation, `DELETE /entries/:id`

### `/til status`

Show site status and connection info. **Works without a token** (degraded display).

- With token: `GET /site` -> show username, entry breakdown (total/published/drafts), token status, local draft count, dashboard link
- Without token: show "not connected", local draft count, setup link

### `/til sync`

Explicitly sync local drafts from `~/.til/drafts/` to OpenTIL. Requires token.

- List pending drafts, POST each one, delete local file on success
- Show summary with success/failure per draft

### `/til tags`

List site tags sorted by usage count (top 20). Requires token.

- API: `GET /tags?sort=popular&per_page=20&with_entries=true`
- Show as compact table with tag name and entry count

### `/til categories`

List site categories. Requires token.

- API: `GET /categories`
- Show as compact table with name, entry count, and description

### `/til batch <topics>`

Batch-capture multiple TIL entries in one invocation. Requires explicit topic list.

- User lists topics separated by newlines, semicolons, or markdown list items (`-` / `1.`)
- Generate a draft for each -> show all drafts for confirmation -> POST sequentially
- On partial failure, show per-entry success/failure (same format as `/til sync`)

### ID Resolution

- In listings, show IDs in short form: `...` + last 8 characters
- Accept both short and full IDs as input
- Resolve short IDs by suffix match against the current listing
- If ambiguous (multiple matches), ask for clarification

### Session State

Track the following session state (not persisted across sessions):
- `last_created_entry_id` -- set on every successful `POST /entries` (201). Used by `/til publish last`.
- `active_profile` -- the profile name resolved at first token access. Reflects the `active` field from `~/.til/credentials` (or `$OPENTIL_TOKEN` override). Used for identity display and draft attribution.

> Detailed subcommand flows, display formats, and error handling: see references/management.md

## Agent Identity

Three layers of attribution signal distinguish human-initiated from agent-initiated TILs.

### Layer 1: HTTP Headers

Include these headers on every API call:

```
X-OpenTIL-Source: human | agent
X-OpenTIL-Agent: <your agent display name>
X-OpenTIL-Model: <human-readable model name>
```

- Source: `/til <content>` and `/til` -> `human`; Auto-detected -> `agent`
- Agent: use your tool's display name (e.g. `Claude Code`, `Cursor`, `GitHub Copilot`). Do not use a slug.
- Model: use a human-readable model name (e.g. `Claude Opus 4.6`, `GPT-4o`, `Gemini 2.5 Pro`). Do not use a model ID.
- Agent and Model are optional -- omit them if you are unsure.

### Layer 2: Tag Convention

- Auto-detected TILs: automatically add `agent-assisted` to the tag list
- `/til <content>` and `/til`: do **not** add the tag (unless the Agent substantially rewrote the content)

### Layer 3: Attribution Rendering (Backend)

Agent-initiated TILs are visually marked on OpenTIL automatically based on the
`source` field. No content modification needed -- the backend renders attribution
in the display layer.

- Public page: shows `✨ via {agent_name}`, or `✨ AI` when agent_name is absent
- Tooltip (hover): shows `{agent_name} · {model}` when both are present
- Dashboard: shows ✨ badge + agent_name, or "Agent" when agent_name is absent

Do NOT append any footer or attribution text to the content body.

### Summary

| Dimension | `/til <content>` | `/til` | Auto-detected |
|-----------|-----------------|--------|---------------|
| Trigger | User explicit | User command | Agent proactive |
| Confirmations | 0 (direct publish) | 1 (review before publish) | 1 (suggest → capture) |
| Source header | `human` | `human` | `agent` |
| Agent header | Yes | Yes | Yes |
| Model header | Yes | Yes | Yes |
| `agent-assisted` tag | No | No | Yes |
| Attribution | Automatic (backend) | Automatic (backend) | Automatic (backend) |

## Content Guidelines

Every TIL entry must follow these rules:

- **Self-contained**: The reader must understand the entry without any conversation context. Never write "as we discussed", "the above error", "this project's config", etc.
- **Desensitized**: Remove project names, company details, colleague names, internal URLs, and proprietary business logic. Generalize specifics: "our User model" -> "a model", "the production server" -> "a production environment", "the Acme payment service" -> "a payment gateway".
- **Universally valuable**: Write to StackOverflow-answer standards. A stranger searching for this topic should find the entry immediately useful. Content only useful to the author belongs in private notes, not TIL.
- **Factual tone**: State facts, show examples, explain why. Avoid first-person narrative ("I was debugging...", "I discovered..."). Exception: brief situational context is fine ("When upgrading Rails from 7.2 to 8.0...").
- **One insight per entry**: Each TIL teaches exactly ONE thing. If there are multiple insights, create separate entries.
- **Concrete examples**: Include code snippets, commands, or specific data whenever relevant. Avoid vague descriptions.
- **Title**: 5-15 words. Descriptive, same language as content. No "TIL:" prefix.
- **Content**: Use the most efficient format for the knowledge — tables for comparisons, code blocks for examples, lists for enumerations, math (`$inline$` / `$$display$$`) for formulas with fractions/subscripts/superscripts/greek letters, Mermaid diagrams (` ```mermaid `) for flows/states/sequences that text cannot clearly express. Simple expressions like `O(n)` stay as inline code; use math only when notation complexity warrants it. Only use prose when explaining causation or context. Never pad content; if one sentence suffices, don't write a paragraph.
- **Tags**: 1-3 lowercase tags from the technical domain (`go`, `rails`, `postgresql`, `css`, `linux`). No generic tags like `programming` or `til`.
- **Lang**: Detect from content. Chinese -> `zh-CN`, Traditional Chinese -> `zh-TW`, English -> `en`, Japanese -> `ja`, Korean -> `ko`.
- **Category**: Do not auto-infer `category_name` -- only include it if the user explicitly specifies a category/topic.
- **Summary**: 1-2 sentences, plain text (no markdown). Max 500 chars and must be shorter than the content body. Same language as content. Self-contained: the reader should understand the core takeaway from the summary alone. Be specific about what the reader will learn, not meta ("this article discusses..."). No first person, no meta-descriptions. Omit if the content is already very short (under ~200 chars) -- the excerpt fallback is sufficient.

## Result Messages

### API Success (token configured, 201)

```
Published to OpenTIL

  Title:  Go interfaces are satisfied implicitly
  Tags:   go, interfaces
  URL:    https://opentil.ai/@username/go-interfaces-are-satisfied-implicitly
```

When ≥2 profiles are configured, add an `Account` line:

```
Published to OpenTIL

  Account: @hong (personal)
  Title:   Go interfaces are satisfied implicitly
  Tags:    go, interfaces
  URL:     https://opentil.ai/@hong/go-interfaces-are-satisfied-implicitly
```

Single-profile users see no `Account` line — keep the output clean.

Extract the `url` field from the API response for the URL.

### Sync Local Drafts

After the first successful API call, check `~/.til/drafts/` for pending files. If any exist, offer to sync:

```
Draft saved to OpenTIL

  Title:  Go interfaces are satisfied implicitly
  Tags:   go, interfaces
  Review: https://opentil.ai/@username/go-interfaces-are-satisfied-implicitly

Found 3 local drafts from before. Sync them to OpenTIL?
```

On confirmation, POST each draft to the API. Delete the local file after each successful sync. Keep files that fail. Show summary:

```
Synced 3 local drafts to OpenTIL

  + Go defer runs in LIFO order
  + PostgreSQL JSONB indexes support GIN operators
  + CSS :has() selector enables parent selection
```

If the user declines, keep the local files and do not ask again in this session.

### First Run (no token)

Save the draft locally, then proactively offer to connect. This is NOT an error -- the user successfully captured a TIL.

```
TIL captured

  Title:  Go interfaces are satisfied implicitly
  Tags:   go, interfaces
  File:   ~/.til/drafts/20260210-143022-go-interfaces.md

Connect to OpenTIL to publish entries online.
Connect now? (y/n)
```

- `y` → run inline device flow (same as `/til auth`) → on success, sync the just-saved draft + any other pending drafts in `~/.til/drafts/`
- `n` → show manual setup instructions (see Manual Setup Instructions below)

Only show the connect prompt on the **first** local save in this session. On subsequent saves, use the short form (no prompt):

```
TIL captured

  Title:  Go interfaces are satisfied implicitly
  Tags:   go, interfaces
  File:   ~/.til/drafts/20260210-143022-go-interfaces.md
```

## Error Handling

**On ANY API failure, always save the draft locally first.** Never let user content be lost.

**422 -- Validation error:** Analyze the error response, fix the issue (e.g. truncate title to 200 chars, correct lang code), and retry. Only save locally if the retry also fails.

**401 -- Token invalid or expired (token from `~/.til/credentials` active profile):**

```
TIL captured (saved locally)

  File: ~/.til/drafts/20260210-143022-go-interfaces.md

Token expired for @hong (personal). Reconnect now? (y/n)
```

- `y` → run inline device flow (same as `/til auth`) → on success, update the active profile's token in `~/.til/credentials` and auto-retry the original POST (publish the just-saved draft, then delete the local file)
- `n` → show manual setup instructions (see Manual Setup Instructions below)

When only one profile exists, omit the `@nickname (profile)` from the message.

**401 -- Token invalid or expired (token from `$OPENTIL_TOKEN` env var):**

The env var takes priority over `~/.til/credentials`, so saving a new token via device flow would not help — the env var would still be used. Guide the user instead:

```
TIL captured (saved locally)

  File: ~/.til/drafts/20260210-143022-go-interfaces.md

Your $OPENTIL_TOKEN is expired or invalid. To fix:
  • Update the variable with a new token, or
  • unset OPENTIL_TOKEN, then run /til auth

Create a new token: https://opentil.ai/dashboard/settings/tokens
```

**Network failure or 5xx:**

```
TIL captured (saved locally -- API unavailable)

  File: ~/.til/drafts/20260210-143022-go-interfaces.md
```

> Full error codes, 422 auto-fix logic, and rate limit details: see references/api.md

### Re-authentication Safeguards

| Rule | Behavior |
|------|----------|
| No retry loops | If re-auth succeeds but the retry still returns 401 → stop and show the error. Do not re-authenticate again. |
| Batch-aware | During batch/sync operations, re-authenticate at most once. On success, continue processing remaining items with the new token. |
| Respect refusal | If the user declines re-authentication (`n`), do not prompt again for the rest of this session. Use the short local-save format silently. |
| Env var awareness | When the active token comes from `$OPENTIL_TOKEN`, never attempt device flow — it cannot override the env var. Always show the env var guidance instead. |
| Profile-aware re-auth | On successful re-authentication, update the corresponding profile's token in `~/.til/credentials`. Do not create a new profile. |

### Manual Setup Instructions

When the user declines inline authentication (answers `n`), show:

```
Or set up manually:
  1. Visit https://opentil.ai/dashboard/settings/tokens
  2. Create a token (select read + write + delete scopes)
  3. Add to shell profile:
     export OPENTIL_TOKEN="til_..."
```

## Local Draft Fallback

When the API is unavailable or no token is configured, drafts are saved locally to `~/.til/drafts/`.

**File format:** `YYYYMMDD-HHMMSS-<slug>.md`

```markdown
---
title: "Go interfaces are satisfied implicitly"
tags: [go, interfaces]
lang: en
summary: "Go types implement interfaces implicitly by implementing their methods, with no explicit declaration needed."
profile: personal
---

In Go, a type implements an interface...
```

The `profile` field records the active profile name at save time, ensuring sync uses the correct account's token. Omitted when no profiles are configured (backward-compatible).

> Full directory structure, metadata fields, and sync protocol: see references/local-drafts.md

## Notes

- **UI language adaptation**: All prompts, result messages, and error messages in this document are written in English as canonical examples. At runtime, adapt them to match the user's language in the current session (e.g. if the user writes in Chinese, display messages in Chinese). Entry content language (`lang` field) is independent -- it is always detected from the content itself.
- Entries are published immediately by default (`published: true`) -- use `/til unpublish <id>` to revert to draft
- The API auto-generates a URL slug from the title
- Tags are created automatically if they don't exist on the site
- Content is rendered to HTML server-side (GFM Markdown with syntax highlighting, KaTeX math, and Mermaid diagrams)
- Management subcommands (`list`, `publish`, `edit`, `search`, `delete`, `tags`, `categories`, `sync`, `batch`) require a token -- no local fallback. Exception: `status` and `auth` (including `auth switch`, `auth list`, `auth remove`, `auth rename`) work without a token.
- Scope errors map to specific scopes: `list`/`search`/`tags`/`categories` need `read:entries`, `publish`/`unpublish`/`edit`/`sync`/`batch` need `write:entries`, `delete` needs `delete:entries`. `status` uses `read:entries` when available but works without a token.
