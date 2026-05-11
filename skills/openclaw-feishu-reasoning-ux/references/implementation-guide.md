# OpenClaw Feishu Card Customization Reference

This reference captures a proven debugging and implementation approach for OpenClaw Feishu card customization, especially when the desired UX includes:

- card 2.0 containerized layouts
- streaming answers
- raw reasoning visibility
- collapsible reasoning panels
- unified titles/colors across all message paths

## 0. Real deployment this guide was proven on

This guide is not abstract. It was derived from a real deployment that was debugged end-to-end and eventually restored successfully.

Proven reference case:
- a specific OpenClaw build/runtime path
- OpenClaw's built-in Feishu channel
- `minimax-cn/MiniMax-M2.7`
- not `minimax-portal/*`

Use this as the first comparison target when another user says "my setup is basically the same".

The highest-priority comparison factors are:
- built-in OpenClaw Feishu channel vs other Feishu integrations
- whether the current path emits usable reasoning signals
- whether the installed build still exposes compatible runtime hooks
- `minimax-cn` vs `minimax-portal`
- loaded runtime path (`src/` vs `dist/`)
- shell test path vs gateway service path

Do not overfocus on WSL vs non-WSL unless logs show environment differences are actually relevant.
Do not treat an OpenClaw version difference as a blocker by itself; treat it as a compatibility question.

## 1. The most important lesson

When a Feishu card regression appears, do not start by tweaking the visual template.

First determine which of these is broken:
- provider did not emit readable live reasoning
- current session lost reasoning state
- runtime callback wiring is wrong
- card streaming lane logic is wrong
- Feishu send/reply/update API path failed

Visual symptoms often come from lower layers.

## 2. Proven root-cause patterns

### Pattern A: Only shows `Thinking...`

Possible causes:
- no live reasoning events exist
- session lost `reasoningLevel=stream`
- `onReasoningStream` is attached to the wrong layer

What to check:
- current session file
- raw stream log
- runtime logs for `onReasoningStream`

### Pattern B: Raw reasoning repeats itself

Possible causes:
- runtime emits cumulative snapshots
- wrapper text like `Reasoning:` and outer italics are not normalized
- async queue uses mutable shared text and replays later content

Fix strategy:
- normalize snapshot
- compute delta against prior snapshot
- freeze queued text before async update

### Pattern C: Final answer exists but user cannot see it

Possible causes:
- final answer is suppressed by commentary filters
- streaming close/update failure prevents fallback send
- reply API path fails while direct send path would work

Fix strategy:
- confirm final answer exists in session transcript
- inspect reply/send API failures
- add fallback from reply to direct send where appropriate

### Pattern D: Works until a new session starts

Possible causes:
- session init does not preserve reasoning state
- only current session entry was patched manually

Fix strategy:
- patch session initialization defaults for the intended Feishu scope

## 2.3 Unknown-case handling

This guide cannot cover every future OpenClaw build, provider path, or Feishu integration shape.

When a new case does not match the documented patterns:

- do not pretend it is already explained by an existing pattern
- separate confirmed facts from working assumptions
- tell the user explicitly that this is outside the proven cases
- explain the risk of the next edit before making it
- keep the first intervention low-risk whenever possible

If the next step would require editing runtime/session/provider layers without a known-good pattern, prepare backup and rollback first and warn the user clearly.

## 2.1 Recommended modification order

For other users' environments, do not start with the hardest layer first.

Use this rollout order:

1. **Card appearance only**
- title wording
- color strategy
- container layout
- collapsible panels
- rich text structure

2. **Ordinary answer streaming**
- make sure final answer streaming is reliable before touching reasoning

3. **Reasoning capability detection**
- prove whether the current model path can expose readable live reasoning

4. **Reasoning integration**
- only if phase 3 passes

5. **Persistence / session initialization**
- only after the behavior is correct in one live session

This order minimizes blast radius.
Even if work stops early, the user still keeps a better Feishu card experience instead of a broken channel.

## 2.2 Backup-before-edit protocol

For real user environments, especially when touching runtime/session/provider layers, use this protocol:

1. Write down the planned scope
- what behavior is broken
- what is going to be changed
- which files are in scope

2. Create backups first
- copy every target file before editing
- keep backups in a clearly named folder
- include enough naming context that the user can identify the rollback point later

3. Explain rollback before testing
- the user should know how to go back before the first risky test

Recommended rollback explanation format:

- `Backups are here: ...`
- `Changed files are: ...`
- `To roll back, restore these files from backup.`
- `After restore, restart gateway if needed.`
- `Then verify with one minimal Feishu test message.`

This matters because the most expensive failure mode is not "the card still looks wrong".
It is "the user no longer trusts the environment and does not know how to recover it".

## 3. Card 2.0 structure that works well

Recommended high-level structure:

- card header
- reasoning `collapsible_panel`
  - element id for reasoning content
- answer content element

Reasoning panel states:
- expanded while raw reasoning streams
- collapsed once answer streaming begins

Header and template strategy:
- use one shared title/template selection path
- do not let fallback sends use a different legacy title

## 4. Necessary conditions vs compatibility factors

### Necessary conditions

For raw reasoning to actually appear, these conditions must be true:

- the current path emits readable or otherwise usable live reasoning signals
- the current session is in reasoning stream mode
- the Feishu dispatcher is wired to actual runtime reply options
- the installed build still exposes compatible runtime hooks
- the card has a visible reasoning lane

If any one of these is false, the front-end card cannot compensate.

### Compatibility factors

These factors can change the repair method, but they are not automatic blockers:

- exact OpenClaw version/build
- loaded runtime path (`src/` vs `dist/`)
- gateway service vs shell environment
- session initialization behavior
- local model registry
- WSL vs non-WSL

Use them to choose the right patch strategy, not to reject the attempt too early.

## 5. Model/provider caveat

Different providers can expose reasoning differently:
- some provide readable live reasoning text
- some only provide final transcript thinking
- some provide encrypted reasoning blobs

Do not assume one successful provider path generalizes to another.

### Practical capability test

When checking a model for Feishu raw reasoning support, use this decision tree:

0. Verify the installed OpenClaw version/build first.
   - if behavior differs from expectations, compare the live installed build before assuming the same fix path applies
   - use this to verify compatible runtime contracts, not as a hard stop by itself
1. Verify the current Feishu path is really the intended implementation.
   - confirm whether the user is on OpenClaw's built-in Feishu channel
   - do not assume Feishu official plugin behavior is equivalent
2. Verify the current session truly ran on the intended provider/model.
3. Check `raw-stream.jsonl`.
   - If it shows live thinking text events, the model/runtime can support true raw reasoning.
4. Check the saved session transcript.
   - If transcript has readable `thinking` but no live events, the model supports post-hoc thinking but not true live raw reasoning through the current runtime path.
5. If transcript has only encrypted/opaque reasoning payloads, treat it as non-displayable raw reasoning.

This prevents a common mistake:
- blaming Feishu card code for a model/provider capability limit.

It also prevents another common mistake:
- rejecting a recoverable environment only because its OpenClaw version differs from the reference case

The right question is:
- does this installed build still expose the hooks required by the customization?

Not simply:
- is this exactly the same version as the proven case?

Another common mistake:
- calling a snapshot-only or transcript-only model path simply "unsupported"

That is too coarse.

Use this distinction instead:
- supports true live raw reasoning
- supports only post-hoc / snapshot reasoning
- supports only encrypted / opaque reasoning
- exposes no readable reasoning

This matters because the user-facing options are different in each case.

## 5.1 Turn technical diagnosis into user choices

When capability limits are found, do not stop at the technical conclusion.

Translate them into practical options:

- `Current model cannot expose raw reasoning, but we can still improve card 2.0 styling.`
- `Current model cannot expose raw reasoning. If you want raw reasoning, we should switch models.`
- `Current model path is unstable. We should first fix session/provider routing, then continue with card customization.`

This makes the skill usable by non-expert users.

## 6. Persistence caveat

If the behavior works only until restart or only in one current session, the fix is incomplete.

A stable solution must survive:
- gateway restart
- new direct Feishu session
- normal fallback send paths

## 6.1 Restart policy

Do not silently restart `openclaw-gateway`.

Even if restart is technically necessary, the agent should:
- explain why restart is needed
- ask the user to run it or confirm permission first

Unexpected restarts can disrupt:
- active Feishu chats
- session-specific reasoning state
- ongoing tasks

## 7. Practical file map

Most work lands in:
- `extensions/feishu/src/reply-dispatcher.ts`
- `extensions/feishu/src/streaming-card.ts`
- `extensions/feishu/src/send.ts`
- `extensions/feishu/src/outbound.ts`
- `extensions/feishu/src/channel.ts`
- `extensions/feishu/src/config-schema.ts`

If symptoms and source do not match, inspect the actual runtime-loaded code path, which may be compiled `dist/`.

## 8. Release-grade verification checklist

If this skill is being used on another user's machine, do not stop at "the setup looks similar".

Before concluding whether the skill worked, verify this exact checklist:

1. **Current session really runs on the intended provider/model**
- confirm in the latest session transcript
- do not trust only the global default or the agent's reply text

2. **Gateway service env matches the path that was proven to work**
- if local shell tests and live Feishu behavior differ, compare service env first
- proxy-related env drift is a common hidden cause

3. **Live reasoning events exist for the real Feishu request**
- inspect `~/.openclaw/logs/raw-stream.jsonl`
- if there is no live reasoning event there, card-layer changes cannot restore raw reasoning

4. **Runtime is in real reasoning stream mode**
- `reasoningMode = "stream"` is required for live reasoning callbacks
- plain thinking-enabled mode is not enough

5. **Reasoning callbacks are attached to final `replyOptions`**
- if `assistant_thinking_stream` exists in logs but Feishu still shows only `Thinking...`, this is the first place to inspect

6. **New Feishu direct sessions inherit reasoning defaults**
- if only the current session works, the fix is incomplete
- new sessions should preserve:
  - `reasoningLevel = "stream"`
  - `thinkingLevel = "low"`

7. **The target model is really registered in the local model table**
- especially for `minimax-cn/MiniMax-M2.7`
- a provider can support the model while local model selection still falls back to another model

## 9. Known traps

### Trap A: "Same official Feishu channel + same minimax-cn" still failed

This does not prove the skill is wrong.

It often means one of these differed:
- session override
- model table registration
- gateway service env
- runtime callback wiring
- loaded `dist/` vs edited `src/`

### Trap B: `/new` or the next day breaks raw reasoning again

This usually means the current session was patched, but session initialization was not.

### Trap C: Model looks correct on screen, but behavior matches another model

Check whether the local model registry silently falls back.
This is especially relevant for `minimax-cn/MiniMax-M2.7`.
