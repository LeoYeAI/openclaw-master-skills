# Proven Case and Pitfalls

This document exists for one reason:

- before changing anything, read the real successful case and the real failure patterns first

Do not start from theory alone.
Start from what actually worked, what actually failed, and what actually caused those failures.

## 1. Real successful practice

This skill was derived from a real OpenClaw + Feishu deployment that was repaired end-to-end and verified live.

The proven successful case was:

- OpenClaw using its built-in Feishu channel
- a compatible installed OpenClaw build/runtime path
- a model/provider/runtime path that actually emitted usable live reasoning signals
- card 2.0 layout with:
  - a dedicated reasoning lane
  - a dedicated answer lane
  - a collapsible reasoning panel
  - unified titles/templates/colors

Important:

- the model name alone was never the reason it worked
- the actual success criterion was that the current path emitted usable live reasoning signals and the installed build still exposed compatible runtime hooks

Treat the successful case as a comparison target, not a magic template.

## 2. The most important mindset

Most failures looked like "Feishu card issues" on the surface, but were actually caused by lower layers.

So the correct order is:

1. verify the current path
2. verify the current signals
3. verify the current build/runtime contract
4. only then adjust the Feishu card layer

Do not start by assuming the card template is the main problem.

## 3. Real pitfalls we actually hit

### Pitfall 1: The channel path was not the same path

OpenClaw's built-in Feishu channel is not the same thing as:

- Feishu's own official plugin
- another Feishu integration path
- a browser-side Feishu automation path

If the user is not on the built-in OpenClaw Feishu channel, do not assume the same patch strategy applies.

### Pitfall 2: The model name looked right, but the signal shape was wrong

We repeatedly saw cases where:

- the model name looked like the "same model"
- but the current runtime path did not emit usable live reasoning signals

So:

- do not conclude "this should work" only because the model name matches a known-good case
- inspect what the current path actually emits

### Pitfall 3: OpenClaw version/build was treated either as irrelevant or as a hard blocker

Both extremes are wrong.

Version/build matters because this customization depends on runtime contracts such as:

- reasoning stream mode
- callback wiring
- reply options shape
- session initialization behavior

But a different version/build is not an automatic blocker.

The real question is:

- does the installed build still expose compatible runtime hooks?

### Pitfall 4: `src/` was edited while the live runtime loaded `dist/`

This is one of the easiest ways to create a "worked yesterday, gone after restart" failure.

If you only change source files but the live runtime is still loading compiled `dist/`, your changes may never actually be active.

Always verify the real loaded runtime path.

### Pitfall 5: Shell tests and gateway service behavior were not the same

We hit cases where:

- local shell tests looked correct
- but live Feishu traffic still failed

The cause was environment mismatch, especially:

- proxy env
- service env
- user service vs shell session differences

Do not assume a local success means the gateway service path is also correct.

### Pitfall 6: The session was not actually on the intended model/provider

We also hit cases where the assistant said it switched models, but the session transcript showed it did not.

So:

- verify the actual session transcript
- do not trust a conversational confirmation

### Pitfall 7: The session lost reasoning defaults after `/new` or the next day

A fix that works only in the current session is not a durable fix.

If raw reasoning disappears after:

- `/new`
- a restart
- the next day

then session initialization or default state inheritance is still incomplete.

### Pitfall 8: `onReasoningStream` was wired to the wrong layer

This was a real root cause.

Reasoning callbacks were previously attached to an intermediate dispatcher options layer instead of the final `replyOptions` that the runtime actually used.

Result:

- the provider emitted live reasoning
- but Feishu never received it
- the UI stayed on `Thinking...`

### Pitfall 9: `reasoningMode = "on"` was mistaken for true live reasoning

That is not enough.

For live reasoning callbacks, the runtime had to actually be in:

- `reasoningMode = "stream"`

Otherwise the system could preserve thinking in transcripts without emitting live reasoning callbacks.

### Pitfall 10: Snapshot reasoning was treated as delta reasoning

This caused:

- duplicated reasoning
- repeated prefixes
- repeated earlier fragments

The fix was to normalize and compare snapshots before updating the card.

### Pitfall 11: Upstream wrappers were shown raw

We hit reasoning snapshots wrapped like:

- `Reasoning:\n`
- outer italics

If not normalized first, the user sees repeated wrapper noise instead of clean reasoning flow.

### Pitfall 12: Mutable queue state caused cross-frame corruption

If queued updates read mutable shared text later, a later frame can pollute an earlier queued update.

Freeze the queued text before the async update is enqueued.

### Pitfall 13: Final answers existed, but users still could not see them

This happened when:

- commentary-style suppression rules hid real final answers
- streaming close/update failed
- reply API failed while direct send would have worked

Always confirm whether the final answer exists in the session transcript before blaming the model.

### Pitfall 14: Feishu reply failed while direct send still worked

We hit reply/send API instability, including 5xx behavior on reply paths.

Do not assume "no visible answer" means "no generated answer".
Inspect the delivery path separately from generation.

### Pitfall 15: Placeholder text was placed in the wrong lane

If a placeholder is put into the answer lane instead of the reasoning lane, it can become a fake permanent reply stub.

Reasoning placeholders belong to the reasoning lane.

### Pitfall 16: The reasoning panel collapsed at the wrong time

If the panel collapses immediately at reasoning end, but more reasoning frames still arrive, the panel can flicker or re-expand.

The safer behavior is:

- mark reasoning as ready to collapse
- actually collapse once answer streaming begins

### Pitfall 17: Legacy send paths still used old titles/templates

Even after the main streaming path looked correct, some fallback/direct send paths still leaked old card titles or templates.

If titles are meant to be unified, inspect:

- streaming path
- direct send path
- fallback path
- media/image path

## 4. What to verify before you change anything

Before editing files, verify these in order:

1. Is this really the built-in OpenClaw Feishu channel?
2. What does the current runtime path actually emit?
3. Does the installed build still expose compatible runtime hooks?
4. Is the current session truly on the intended provider/model?
5. Is shell behavior the same as gateway service behavior?
6. Is the change low-risk card work or high-risk runtime/session/provider work?

If you cannot answer those, stop and explain the uncertainty first.

## 5. How this doc should be used

The correct workflow is:

1. read this document first
2. compare the user's environment to the proven case
3. identify which pitfall pattern is closest
4. only then decide whether to:
   - stop at diagnosis
   - do low-risk card changes
   - or continue into higher-risk runtime/session/provider changes

If the current situation does not match a proven pattern, say so clearly to the user before continuing.
