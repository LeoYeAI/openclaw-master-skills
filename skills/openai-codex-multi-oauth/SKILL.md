---
name: openai-codex-multi-oauth
description: Manage and debug multiple OpenAI Codex OAuth profiles inside OpenClaw, including native multi-profile auth stores and external-router setups where one active slot is backed by a repository of multiple OAuth identities. Use when fixing Codex profile switching, session `authProfileOverride` sync, `/status` or usage mismatches, auth.order behavior, active-slot routing, broken-token recovery, or same-email different-account/workspace selection bugs.
---

# OpenAI Codex Multi OAuth

Support and debug more than one `openai-codex` OAuth login inside OpenClaw.

## Start here

1. Run `python3 scripts/summarize_codex_profiles.py`.
2. Classify the bug before patching anything.
3. Change the smallest wrong layer.
4. Re-test after every change.

If the target setup includes a local helper command or router script, reproduce through that real entrypoint at least once. Synthetic env-injected tests can miss session-sync bugs.

## Mental model

Treat these as separate layers:

- **stored preference** — any saved local pointer such as `codex_profile_id`
- **auth order** — `order.openai-codex` in the auth store
- **session override** — `authProfileOverride` for the current chat/session
- **effective runtime profile** — the profile that actually handled the request after selection or failover
- **usage source** — the token/accountId used by usage-fetch logic
- **display metadata** — the label shown to the user, such as email/workspace
- **optional external profile repo** — a separate file or store that keeps multiple Codex OAuth identities while runtime uses one active slot

Do not assume these layers always match.

## Common architectures

### A. Native auth-store setup

OpenClaw stores multiple `openai-codex:*` profiles directly in `auth-profiles.json`, and runtime resolves selection from auth order plus session override.

### B. External-router setup

A local repo of Codex OAuth identities exists outside normal runtime selection, and a helper/router copies one selected profile into an active slot such as `openai-codex:default`.

In that design, verify all of these separately:
- repo profile selected by the router
- active slot content after routing
- current session `authProfileOverride`
- `/status` oauth label
- `/status` usage source

## Decision tree

### 1) The wrong account is selected

Check in this order:
1. stored preference or helper-selected profile
2. `order.openai-codex`
3. session `authProfileOverride`
4. effective runtime profile
5. whether failover is expected or a bug

### 2) `/codex_profile`-style helper switches profile, but `/status` does not follow

Check:
1. whether the helper changed only the active slot or also the current session override
2. whether the current chat/session was correctly identified
3. whether the environment that invokes the helper is missing chat/session metadata
4. whether the platform keeps companion session entries that also need syncing

If the helper is real, re-test through the real command path, not only manual edits.

### 3) `/status` oauth changes, but usage does not

Check:
1. current session `authProfileOverride`
2. the effective runtime profile for the current chat
3. whether the usage loader resolves auth from generic provider order instead of the current session profile
4. whether the UI is mixing preferred-profile and effective-profile semantics

### 4) A profile works sometimes but not always

Check:
1. cooldown / last-good logic
2. token expiry
3. soft-pin vs hard-pin semantics
4. whether failover is expected behavior or a bug

### 5) A token or profile entry is broken

Check:
1. whether the same `accountId` exists in another store or backup
2. whether only one profile entry can be restored surgically
3. whether local token parsing fails before request dispatch

### 6) `/status`, display labels, and runtime truth disagree

Decide which semantic each surface should represent:
- preferred profile
- effective runtime profile
- usage source profile
- display metadata label

Then verify every layer against that semantic before patching.

## Stable design rules

- Prefer profile identity by `accountId` before email when possible.
- Preserve different workspaces/accounts as separate profiles even when email matches.
- Keep profile ids stable, for example:
  - `openai-codex:default`
  - `openai-codex:secondary`
  - `openai-codex:tertiary`
  - `openai-codex:account-N`
- Do not blur preferred profile, effective runtime profile, and usage source profile.
- If an external repo exists, treat it as a separate layer instead of silently merging it into runtime state.

## Validation checklist

After each change, verify all of these:

1. stored preference or helper-selected profile is what you expect
2. auth order is what you expect
3. current session `authProfileOverride` is what you expect
4. runtime actually uses the intended profile
5. `/status` shows the intended semantic
6. usage matches the intended semantic, or the difference is explicitly understood
7. any helper command resolves the same profile id the runtime is using

## Bundled resources

- Read `references/runtime-files.md` for the file families that usually matter.
- Read `references/workflows.md` for concrete repair workflows and rollback points.
- Run `scripts/summarize_codex_profiles.py` before and after changes.

## Guardrails

- Back up auth files or runtime bundles before editing them.
- Prefer surgical patches over broad rewrites.
- Keep version-specific assumptions explicit.
- Do not restart the gateway unless the user asked.
- Commit workspace skill changes after edits.
