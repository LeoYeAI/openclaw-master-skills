---
name: openclaw-feishu-reasoning-ux
description: Improve OpenClaw's Feishu reply experience by customizing streaming cards, raw reasoning visibility, card 2.0 layouts, collapsible panels, titles, colors, and fallback send paths. Use this whenever a user wants a better Feishu reply UX for OpenClaw, especially when raw reasoning disappeared, only Thinking shows, titles/styles regressed, cards feel too black-box, or the user wants Feishu replies to become more observable, layered, and customizable.
---

# OpenClaw Feishu Reasoning UX

Use this skill when the task is specifically about how OpenClaw messages appear inside Feishu.

This skill is for:
- card 2.0 styling
- streaming card behavior
- raw reasoning visibility
- collapsible reasoning panels
- title/template/color behavior
- fallback send paths
- regressions after restart, update, or session rollover

This skill is not for generic Feishu app setup, permissions, or bot connectivity unless those directly block card delivery.

## Read this first

Before making any change, read:

- [references/proven-case-and-pitfalls.md](./references/proven-case-and-pitfalls.md)

Do not skip it.

That document contains:
- the real successful practice this skill came from
- the real failure patterns we actually hit
- the specific traps that repeatedly caused false fixes or broken environments

Only after reading it should you decide whether the current case is:
- close enough to a proven pattern to continue
- only safe for low-risk card changes
- or outside the proven cases and should be explained to the user first

## Core operating principles

This is not a "silently fix everything" skill.

Treat it as:
- a diagnosis-first skill
- a user-consent-first customization skill
- a backup-and-rollback-first skill

The user keeps control of the risky steps.

That means:
- if the current environment differs from the proven cases, do not silently push ahead
- explain the difference, the likely risk, the expected benefit, and the rollback path first
- let the user decide whether to continue

When in doubt:
- prefer stopping with a clear explanation
- prefer low-risk card-layer improvements
- avoid self-authorized runtime/session/provider surgery

## Real-world reference case

This skill was validated on a specific real deployment shape, but do not treat every detail of that environment as a hard prerequisite.

Proven reference case:
- a specific OpenClaw build/runtime path
- OpenClaw's built-in Feishu channel
- `minimax-cn/MiniMax-M2.7`
- not `minimax-portal/*`

Use this case as a comparison point, not as a rigid gate.

The details that matter most are usually:
- whether the channel is the built-in OpenClaw Feishu channel
- whether the current path emits usable live reasoning signals
- whether the installed build still exposes the runtime hooks this customization depends on
- provider/model path
- loaded runtime path (`src/` vs `dist/`)
- session/service state

Treat OpenClaw version/build as a compatibility factor, not a rigid gate by itself.
The question is not "is the version identical to the reference case?"
The question is "does this installed build still expose compatible runtime contracts?"

Do not overfocus on WSL vs non-WSL unless logs show environment differences are actually relevant.

## Interaction style for end users

Assume many users do not know Feishu card internals, provider runtime details, or OpenClaw file layout.

So when using this skill:
- explain findings in plain language first
- translate technical diagnosis into user-facing choices
- proactively offer the next reasonable options instead of stopping at analysis
- ask short, concrete preference questions when appearance or behavior depends on taste

Good examples:
- `我检测到当前模型不支持可见 raw reasoning，但我们还能把回复卡片做成 2.0 风格、带颜色标题和折叠面板。你想先改这个吗？`
- `我检测到现在标题已经能改。你想让标题显示什么文案？直接告诉我文字就行。`
- `当前模型只能流正式回答，不能流 raw 思考。我可以帮你切到支持的模型，或者保留当前模型只优化卡片样式。你想走哪条？`

Do not dump only low-level findings if the user clearly wants a working outcome.

## What success looks like

A correct Feishu customization usually has to satisfy all of these:
- Feishu messages still send reliably
- normal answer streaming still works
- raw reasoning, if enabled, shows in the intended form
- final answer still closes correctly
- new sessions do not silently lose the behavior
- changes are documented so they can be rebuilt later

Do not optimize appearance first if delivery or runtime lane selection is broken.

## Safe rollout strategy

Default to phased customization, not all-at-once modification.

The safest order is:

1. **Low-risk card appearance changes**
- titles
- colors
- card 2.0 layout
- collapsible containers
- rich text / container structure

2. **Normal answer streaming behavior**
- confirm ordinary streaming still works
- keep reasoning disabled for now if needed

3. **Raw reasoning capability check**
- verify whether the current model/provider/runtime truly supports readable live reasoning

4. **Raw reasoning runtime/session wiring**
- only after capability is proven
- only after ordinary card sending and answer streaming are stable

5. **Persistence fixes**
- only after the behavior is correct
- patch new-session defaults or shared runtime logic so it survives restart and `/new`

If the user only wants a better Feishu card experience, stop after phase 1 or phase 2.
Do not pull them into high-risk reasoning/runtime changes unnecessarily.

### How to explain phased rollout to the user

Prefer language like:

- `我们先做风险最小的部分：标题、颜色和卡片 2.0 容器。`
- `普通回复流式先确认稳定，再决定要不要动 raw reasoning。`
- `raw reasoning 这层要先看模型支不支持，支持再继续。`

Do not jump straight into runtime surgery unless the user clearly wants visible raw reasoning.

## Backup and rollback are mandatory

Before any non-trivial Feishu customization, create a recovery trail first.

This is not optional.

Always do all three before risky changes:

1. **Create a written change note**
- summarize what is about to be changed
- record the current model/provider/session assumptions
- record the target files

2. **Create a file backup**
- back up every file that will be modified
- use a clearly named backup directory with date/time context
- do this before the first edit, not after

3. **Prepare a user-facing rollback guide**
- tell the user exactly how to restore the prior state
- include file paths
- include whether a gateway restart is needed after restore

If the user environment is fragile, prefer incremental backup points instead of one large backup.

### Minimum rollback instructions to provide

Before claiming a risky change is ready to test, the agent must be able to tell the user:

- which files were changed
- where the backups were saved
- how to restore the backups
- whether restoring requires a gateway restart
- how to verify that rollback succeeded

If you cannot explain rollback clearly, the change is not ready.

## Necessary conditions vs compatibility factors

Separate hard requirements from things that only increase risk.
Do not treat every difference from the reference case as a blocker.

### Necessary conditions for raw reasoning customization

These are the conditions that actually have to be true before you try to modify the raw reasoning lane:

1. The current Feishu path is truly the intended channel implementation.
- Verify whether the user is on:
  - OpenClaw's built-in Feishu channel
  - or Feishu's own official plugin / another integration path
- Do not treat those as interchangeable.

2. The current session is truly running on the intended provider/model path.
- Verify the active session transcript, not just the global default.
- Do not trust the agent saying it already switched.

3. The current runtime path is actually producing usable reasoning signals.
- Check `~/.openclaw/logs/raw-stream.jsonl`.
- For MiniMax CN, look for `assistant_thinking_stream`.
- If the current request produces no usable reasoning signal, card changes cannot create true raw reasoning.

4. The installed OpenClaw build still exposes compatible runtime hooks.
- Examples:
  - `reasoningMode = "stream"` is honored
  - `onReasoningStream` / `onReasoningEnd` can reach the final `replyOptions`
  - the dispatcher contract still matches the patch strategy
- A different version is acceptable if these contracts are still compatible.

5. A rollback path is ready before risky edits.
- If you cannot explain backup and rollback clearly, do not patch runtime/session/provider layers.

### Compatibility factors that can change the implementation

These are important to inspect, but they are not automatic reasons to stop:

- exact OpenClaw version/build
- loaded runtime path (`src/` vs `dist/`)
- gateway service environment vs shell environment
- session initialization behavior
- local model registry / alias table
- WSL vs non-WSL

They matter because they may change how you implement the fix.
They do not automatically mean the fix is impossible.

### What to verify first

0. The running OpenClaw version/build is known.
- Verify the actual installed OpenClaw version before assuming the same fix path applies.
- Use this to compare contracts, not as a rigid stop condition by itself.

1.5. The current Feishu path is truly the intended channel implementation.
- If the user is not on the built-in OpenClaw Feishu channel, say that explicitly before continuing.

2. The gateway service environment matches the shell path that was proven to work.
- Proxy-related env differences can make shell tests succeed while live Feishu traffic fails.
- If raw reasoning only works in local CLI tests, compare gateway service env before touching cards.

4. The dispatcher is in true reasoning stream mode.
- OpenClaw only emits live reasoning callbacks when the runtime is in `reasoningMode = "stream"`.
- `thinkingLevel = low` alone is not enough.

5. `onReasoningStream` / `onReasoningEnd` are attached to the final `replyOptions`.
- Attaching them only to intermediate dispatcher options is not sufficient.
- If provider logs show live thinking but Feishu still only shows `Thinking...`, check this first.

6. New Feishu direct sessions inherit reasoning defaults.
- A manual session patch is not enough.
- If `/new` or next-day sessions lose raw reasoning, fix session initialization so new Feishu direct sessions default to:
  - `reasoningLevel = "stream"`
  - `thinkingLevel = "low"`

7. The model is actually registered in the local model table.
- `minimax-cn/MiniMax-M2.7` is a known trap: the provider may support it while the local model registry still silently falls back to `M2.5`.
- Verify the local model table before claiming that "M2.7 does not work".

If the necessary conditions are not met, do not attempt raw reasoning customization.
If only compatibility factors differ, adapt the implementation instead of stopping by reflex.

## First pass: identify the real layer

Before editing anything, classify the issue into one of these layers:

1. Provider/runtime layer
- Model does not emit live reasoning events
- Reasoning is encrypted or only present in final transcript
- Provider silently falls back to a different model

2. Session/state layer
- New session lost `reasoningLevel=stream`
- Current session is using the wrong provider/model override
- Gateway service environment differs from shell environment

3. Feishu dispatcher layer
- `onReasoningStream` is wired incorrectly
- answer lane and reasoning lane are mixed
- snapshot reasoning is treated as delta and duplicates text
- final answer is suppressed or never overrides placeholder content

4. Card rendering layer
- wrong title/template/color
- panel folds at the wrong time
- placeholder is rendered in the wrong lane
- layout regresses from card 2.0 to plain markdown

5. Delivery layer
- streaming start fails
- reply API fails but direct send fallback works
- media/image sending path differs from text sending path

Do not assume a visual symptom is a card-layer problem. A "Thinking..." only state is often a runtime or session-state problem.
Also do not assume all "Feishu plugins" are the same execution path.

## Stop conditions for risky changes

Do not modify high-risk layers if any of these are still unclear:

- whether the user is on the built-in OpenClaw Feishu channel
- actual provider/model path
- whether live reasoning signals truly exist
- whether the installed build still exposes compatible runtime hooks
- how to roll back the exact files you are about to edit

If any of those are unknown, stop at one of these safe outcomes:

1. diagnostic conclusion only
2. low-risk card 2.0 appearance changes only
3. ordinary answer streaming fixes only

Do not continue into:
- provider registration changes
- session initialization changes
- runtime callback wiring changes
- `dist/` patching

unless the above preconditions are verified.

Do not stop only because the installed OpenClaw version/build differs from the reference case.
Stop only when the build's actual runtime contracts are unknown or incompatible.

## What to do when the situation is not covered by this skill yet

If the current failure mode, runtime behavior, or channel behavior is not covered by the documented patterns in this skill, do not improvise silently.

In that case:

1. Explain clearly to the user that this is outside the known proven cases.
2. State what is known, what is unknown, and which assumption would have to be made.
3. Explain the risk level of the next possible change.
4. Explain the rollback path before making any risky edit.
5. Prefer stopping at diagnosis or low-risk card-layer changes unless the user explicitly wants to continue.

Required style in those cases:
- do not say "this should be safe" unless it is proven
- do not present a guess as a confirmed root cause
- do not continue directly into runtime/provider/session patching without warning the user

If the user still wants to continue, proceed incrementally and verify after each step.

## Files to inspect first

Locate the installed OpenClaw package root first. In many environments it will be something like:

```bash
npm root -g
```

Then inspect these Feishu files first:
- `extensions/feishu/src/reply-dispatcher.ts`
- `extensions/feishu/src/streaming-card.ts`
- `extensions/feishu/src/send.ts`
- `extensions/feishu/src/outbound.ts`
- `extensions/feishu/src/channel.ts`
- `extensions/feishu/src/config-schema.ts`

Also inspect current runtime/session state:
- `~/.openclaw/openclaw.json`
- `~/.openclaw/agents/main/sessions/sessions.json`
- `~/.openclaw/logs/raw-stream.jsonl`

If symptoms do not match source edits, inspect the actual loaded runtime too:
- OpenClaw may be executing compiled `dist/` files, not `src/`

## Mandatory debugging workflow

Follow this order.

### 1. Confirm the active model path

Check all three, not just one:
- global default model in config
- current session provider/model override
- actual model/provider recorded in the current session transcript

Do not trust the agent saying "I switched models". Verify it in session files.

### 2. Confirm whether live reasoning exists at all

Look for evidence in:
- provider/runtime event logs
- `raw-stream.jsonl`
- current session transcript

Distinguish these cases:
- live reasoning event exists and is readable
- reasoning exists only in final transcript
- reasoning exists but is encrypted
- no reasoning exists at all

If the model does not produce readable live reasoning, Feishu cannot truly display raw reasoning no matter how good the card layer is.

#### Mandatory model capability check

Do not assume the current model supports visible raw reasoning.

Explicitly determine which of these four cases you are in:

1. **Readable live reasoning**
- runtime emits live reasoning text
- Feishu can display true raw reasoning if wired correctly

2. **Readable reasoning only in final transcript**
- no live reasoning events
- transcript contains thinking after completion
- Feishu cannot show true live raw reasoning without a shim/replay design

3. **Encrypted or opaque reasoning**
- reasoning exists only as encrypted/opaque payload
- Feishu cannot display raw reasoning directly

4. **No reasoning exposed**
- neither live events nor readable transcript thinking are available

For every model under investigation, verify all three:
- what the current session actually ran
- whether `raw-stream.jsonl` shows live thinking events
- whether the saved session transcript contains readable `thinking`

Only after this check may you decide whether the task is:
- a Feishu card implementation problem
- a session/runtime routing problem
- or a provider/model capability limit

Important:
- do not collapse all non-live cases into "the model does not support reasoning"
- distinguish:
  - supports true live raw reasoning
  - supports only snapshot/transcript reasoning
  - exposes encrypted/opaque reasoning
  - exposes no readable reasoning at all

A snapshot-only result means:
- the model may still support reasoning
- but not true live raw reasoning through the current path
- the correct user-facing explanation is not simply "unsupported"

#### How to explain the result to the user

After capability detection, always convert the result into one of these user-facing outcomes:

1. **Model supports raw reasoning**
- Say that raw reasoning can be implemented or repaired on the current model.
- Proceed to fix the Feishu card/runtime path.

2. **Model does not support readable raw reasoning, but supports normal streaming**
- Say that true raw reasoning is not available on the current model.
- Offer alternatives:
  - keep current model and improve card 2.0 appearance
  - switch to a model/provider path that supports raw reasoning

2.5. **Model supports only snapshot/transcript reasoning**
- Say that the current path can retain reasoning after completion, but not stream true live raw reasoning.
- Do not describe this as "no reasoning support" without qualification.
- Offer alternatives:
  - keep the current model and improve card 2.0 / ordinary answer streaming
  - switch to a path that exposes live raw reasoning
  - if appropriate, design a replay/summary experience instead of pretending it is live raw reasoning

3. **Model/provider state is unclear**
- Say that the current route is not trustworthy yet.
- First fix routing/session state before making UI promises.

Do not just say "not supported" and stop. Turn it into the next actionable user choice.

### 3. Confirm session state

For Feishu direct sessions that should show raw reasoning, check:
- `reasoningLevel = stream`
- `thinkingLevel = low` or intended level

If new sessions keep dropping reasoning visibility, fix session initialization, not just the current session entry.

Also verify that the failure is not just a stale or wrong model override:
- `providerOverride`
- `modelOverride`
- `authProfileOverride`
- actual provider/model recorded in the latest assistant turn

### 4. Confirm dispatcher wiring

For raw reasoning to display, the Feishu dispatcher must receive reasoning callbacks through the final reply options that runtime actually uses.

Do not attach `onReasoningStream` to the wrong layer.

If provider logs show thinking stream but Feishu only shows a static placeholder, inspect how `onReasoningStream` and `onReasoningEnd` are passed into the runtime.

Also verify that the runtime path is really in reasoning stream mode.
If the runtime is only in plain "thinking enabled" mode, Feishu may still get final transcript thinking without ever receiving live reasoning callbacks.

### 5. Confirm card lane behavior

Keep reasoning and answer as separate lanes.

Typical correct structure:
- reasoning lane for thinking/raw reasoning
- answer lane for final answer

Do not keep placeholder text in the answer lane.

## Design rules for Feishu card customization

### Rule 1: Separate reasoning lane and answer lane

Raw reasoning and final answer should not share the same mutable text buffer.

Maintain separate state for:
- reasoning snapshot/current text
- answer snapshot/current text

This avoids:
- repeated reasoning
- reasoning leaking into answer
- final answer failing to replace the placeholder

### Rule 2: Treat reasoning snapshots carefully

Many runtimes emit cumulative reasoning snapshots, not pure deltas.

If each new reasoning frame includes all prior text, normalize it before streaming:
- detect whether the new text starts with the previous snapshot
- if so, only stream the appended suffix
- otherwise treat it as a replacement snapshot

Also normalize provider-added wrappers before diffing:
- leading `Reasoning:\n`
- outer `_..._`

### Rule 3: Use collapsible panels for reasoning, not for the main answer

For card 2.0 reasoning UX:
- put reasoning inside a `collapsible_panel`
- keep answer in a separate content element
- panel can start expanded
- collapse after reasoning ends and answer begins

Do not collapse immediately on `onReasoningEnd` if more reasoning or late answer frames may still arrive. Prefer delaying collapse until answer streaming actually begins.

### Rule 4: Keep the card title system unified

All message paths should share the same title/header strategy:
- normal card sends
- streaming card start
- streaming final close
- fallback direct sends
- image/media fallback card paths

If titles regress in only one path, inspect `outbound.ts` and fallback card builders.

## Known-good path vs. lookalikes

Do not treat these as equivalent without evidence:

- `official Feishu channel`
- `same minimax-cn provider`
- `same model name on screen`

These can still differ in the real failure points:
- session override drift
- model table fallback
- gateway service env drift
- runtime callback wiring drift

Always prove the real path with logs and transcripts.

## Anti-patterns

Do not let the agent do any of these:

- assume "same provider + same channel" means same runtime path
- patch only the current session and claim the issue is solved
- modify only `src/` files when runtime behavior suggests the loaded code is from `dist/`
- promise raw reasoning on a model before checking whether readable live reasoning exists
- silently restart the gateway
- apply provider/session/runtime changes before low-risk card-layer changes are verified
- change provider model tables just because a model name "should" work
- patch session initialization before proving the current-session behavior is correct
- patch runtime callback wiring before proving the current path really emits live reasoning

### Rule 5: Fix the system, not a single task

If cron, new sessions, or fallback sends lose the behavior, repair the shared runtime/session/delivery logic.
Do not hardcode per-task fixes.

### Rule 6: Ask for text/style preferences when the problem is solved enough

Once delivery and runtime behavior are stable, invite the user to customize:
- title text
- panel title text
- color style
- whether reasoning should fold automatically
- whether group chats should differ from direct chats

Keep those questions simple and direct. For example:
- `主标题你想显示什么？`
- `思考面板标题你想写成“烟花在想”还是别的？`
- `颜色你想随机，还是固定一组偏好色？`

### Rule 7: Never restart the gateway silently

Do not restart `openclaw-gateway` on your own without telling the user.

If a restart is required:
- first explain why
- then either ask the user to run it
- or ask for confirmation before doing it

Use language like:
- `这个改动需要重启 gateway 才会生效。你来执行，还是我在你确认后替你执行？`

This rule exists because Feishu session behavior, active runs, and user expectations can all be disrupted by an unexpected restart.

## Current proven implementation pattern

When implementing raw reasoning plus card 2.0 behavior, use this architecture:

1. Keep normal Feishu streaming enabled
2. Add an explicit Feishu-level `reasoningStream` config gate
3. In the dispatcher:
- wire `onReasoningStream`
- wire `onReasoningEnd`
- keep a separate answer streaming path
4. In the streaming card:
- create a `collapsible_panel` for reasoning
- keep a separate answer element
- collapse the panel when answer streaming starts
5. Preserve reliable fallback sending if reply/update APIs fail
6. Ensure new Feishu direct sessions default to the intended reasoning state if the product requires it

## What to avoid

Avoid these anti-patterns:
- monkey-patching core dispatcher creation globally if a local reply option path is available
- forcing reasoning through unrelated block paths without evidence
- storing placeholders in answer lane
- editing only `src/` when runtime actually loads `dist/`
- trusting visual behavior without checking session/runtime logs
- trusting card appearance while ignoring delivery failures

## Validation checklist

Before claiming success, verify all of these:

1. A new Feishu direct session uses the intended model
2. A new Feishu direct session has the intended reasoning state
3. Raw reasoning displays without repeated snapshot spam
4. Final answer still streams
5. Reasoning panel collapses at the right time
6. Titles/templates/colors are consistent across:
- streaming
- final answer
- fallback text send
- fallback media/image send
7. Restarting the gateway does not drop the behavior
8. Creating a new session does not drop the behavior
9. The tested model was confirmed to expose readable live reasoning, or the limitation was explicitly documented

## Documentation requirement

Every meaningful Feishu card customization must update the project’s Feishu card guide or create one if absent.

Document at minimum:
- the user-facing goal
- the actual root cause
- exact files changed
- required session/runtime conditions
- known model/provider limits
- how to verify after restart
- how to recover if the behavior drops again

## Suggested output when using this skill

When you finish, report in this order:

1. Root cause
2. What layer was fixed
3. What files changed
4. What was verified
5. What can still regress and how to check it

If the issue is only partially solvable because of model/provider limits, also include:
6. What still can be customized anyway
7. What user-facing choices are available next

## Examples of prompts that should trigger this skill

Example 1:
`帮我把 OpenClaw 的飞书回复卡片改得更像一个完整 UI，不要只有一块 markdown。`

Example 2:
`之前飞书里能流 raw reasoning，今天又只剩 Thinking... 了，你帮我恢复。`

Example 3:
`把飞书思考过程做成折叠面板，思考完自动折叠，再开始流正式回复。`

Example 4:
`为什么飞书里只有部分路径的标题还是旧的“烟花想法”，帮我统一掉。`

Example 5:
`帮我看看这个模型到底支不支持在飞书里流 raw reasoning，不要先默认是卡片代码的问题。`

## Example prompts and expected behaviors

Use these as practical calibration examples. They are not heavy formal evals; they exist to keep the skill usable and consistent.

### Example A: Raw reasoning disappeared

Prompt:
`昨天还能看到飞书里流 raw reasoning，今天又只剩 Thinking... 了，帮我查一下。`

Expected behavior:
- inspect model/session/runtime before changing card visuals
- verify whether the current session lost `reasoningLevel=stream`
- explain the root cause in plain language
- if the model cannot provide readable live reasoning, say so clearly and offer alternatives

### Example B: User wants style customization

Prompt:
`我想把飞书卡片标题改成别的文案，再加一点颜色。`

Expected behavior:
- avoid over-diagnosing if delivery/runtime is already healthy
- ask direct preference questions:
  - title text
  - reasoning panel title
  - random vs fixed color style
- implement styling in the correct Feishu card builder path
- keep fallback paths visually consistent

### Example C: Model does not support raw reasoning

Prompt:
`为什么这个模型只有回答流，没有 raw reasoning？还能做点什么？`

Expected behavior:
- explicitly classify the model as:
  - supports readable live reasoning
  - transcript-only thinking
  - encrypted/opaque reasoning
  - no reasoning exposed
- do not pretend Feishu alone can fix a provider limitation
- offer alternatives:
  - keep current model and improve card 2.0 appearance
  - switch to a model/path that supports raw reasoning

### Example D: Needs restart to take effect

Prompt:
`你直接帮我把飞书卡片改掉。`

Expected behavior:
- make the code/config changes
- if restart is required, do not restart silently
- tell the user what changed and say:
  - why restart is needed
  - whether the user should run it
  - or ask for confirmation before doing it

### Example E: New session keeps losing the behavior

Prompt:
`每次 /new 之后 raw reasoning 就没了。`

Expected behavior:
- do not patch only the current session
- inspect session initialization/default inheritance
- fix the shared session/runtime path so future sessions retain the intended state
