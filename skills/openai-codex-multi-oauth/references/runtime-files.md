# Runtime files and inspection points

These are the file families that usually matter when debugging multiple Codex OAuth profiles in OpenClaw.

## Core state files

- saved local profile pointer, if the setup keeps one:
  - `~/.openclaw/codex_profile_id`
- auth profile store for agent `main`:
  - `~/.openclaw/agents/main/agent/auth-profiles.json`
- session registry for agent `main`:
  - `~/.openclaw/agents/main/sessions/sessions.json`
- session transcript for a specific chat:
  - `~/.openclaw/agents/main/sessions/<session-id>.jsonl`

For non-`main` agents, replace `main` in the path.

## Optional external-router files

Some setups keep a separate repository of Codex OAuth identities and route one selected profile into an active runtime slot.

Common examples:

- external profile repo:
  - `~/.openclaw/codex-oauth-profiles.json`
- local helper command:
  - `~/.openclaw/codex_profile`
- local router script:
  - `<workspace>/scripts/codex_oauth_router.py`

Treat these as optional. Not every install has them.

## What each layer usually controls

### `auth-profiles.json`
- profile records
- `order.openai-codex`
- `usageStats`
- `lastGood`
- active-slot content in external-router designs

### `sessions.json`
- per-session model/provider state
- `authProfileOverride`
- the OAuth id that `/status` should show for the current chat

### external profile repo, if present
- the canonical list of multiple Codex OAuth identities
- metadata used for display labels
- the profile the router/helper believes is selected

### local helper command, if present
- user-facing switching flow
- session-sync behavior when the selected profile should also update current-chat state
- a common source of bugs when command invocation lacks the expected chat/session env

## Runtime bundles that often matter

- OpenClaw bundled status / auth / usage logic:
  - `~/.npm-global/lib/node_modules/openclaw/dist/model-selection-*.js`
  - `~/.npm-global/lib/node_modules/openclaw/dist/plugin-sdk/thread-bindings-*.js`
  - `~/.npm-global/lib/node_modules/openclaw/dist/auth-profiles-*.js`
- Codex provider transport:
  - `~/.npm-global/lib/node_modules/openclaw/node_modules/@mariozechner/pi-ai/dist/providers/openai-codex-responses.js`

Adjust paths if OpenClaw is installed elsewhere.

## Fast inspection checklist

1. inspect stored preference or helper-selected profile state
2. inspect `order.openai-codex`
3. inspect current session `authProfileOverride`
4. inspect the effective runtime profile or active slot if the setup has one
5. if usage is wrong, inspect the runtime usage loader path, not only router state
6. if a helper command exists, reproduce through that real path at least once
7. if requests fail before remote auth handling, inspect `openai-codex-responses.js`

## Portability note

Exact dist bundle filenames and routing conventions change across OpenClaw versions and local installations. Confirm the target version and actual file layout before reusing a patch literally.
