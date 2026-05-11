<div align="right">
<a href="./README.md">简体中文</a> | English
</div>

# OpenClaw Feishu Reasoning UX

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Status](https://img.shields.io/badge/status-beta-orange)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Feishu%20UX-0ea5e9)
![Skill](https://img.shields.io/badge/type-skill-8b5cf6)

Make OpenClaw show reasoning in Feishu in a Telegram-like real-time streaming way, avoid long black-box waits, and pair it with better-looking colorful 2.0 cards that support multi-component containers and rich text.

This is a skill for OpenClaw, designed to improve OpenClaw's reply experience in Feishu, especially around:

- visible reasoning / reply dual lanes
- collapsible reasoning panels
- card 2.0 layouts
- unified titles, colors, and templates
- model capability detection and troubleshooting

## Before you use it

What actually has to be true:

- you are customizing the Feishu reply path that OpenClaw itself controls
- the current model/provider/runtime path emits usable reasoning signals
- the current build still exposes the runtime hooks that this customization depends on

What may affect compatibility, but should not be treated as an automatic blocker:

- exact OpenClaw version/build
- provider route
- loaded runtime path (`src/` vs `dist/`)
- shell vs gateway service environment
- session state

In other words:

- if the current model path does not expose readable live reasoning, this skill will not magically create it
- whether live reasoning is feasible depends on what the current path actually emits, not just on the model name
- version differences matter only when they change the runtime contracts this customization relies on
- if those contracts are still compatible, the skill should continue instead of stopping only because the version is different

## Screenshots

### Initial thinking state

![Initial thinking state](./assets/01-thinking-start.jpg)

### Expanded reasoning content

![Expanded reasoning content](./assets/02-reasoning-expanded.jpg)

### Collapsed reasoning with final reply

![Collapsed reasoning with final reply](./assets/03-reasoning-collapsed-reply.jpg)

## What this is

A skill for improving OpenClaw's Feishu-channel reply experience.

Its goal is to:

- make Feishu replies more visible and more layered
- show real raw reasoning when the current model path supports it
- still improve card and streaming UX when raw reasoning is not available

## How this differs from ordinary Feishu streaming

OpenClaw's built-in Feishu channel, as well as the ordinary official Feishu-side streaming behavior, usually only stream the final reply text. They do not stream the model's reasoning in real time.

This skill aims to:

- display reasoning and answer separately
- place reasoning inside a collapsible panel
- continue streaming the answer in a dedicated answer area

That makes it much closer to a Telegram-style reasoning-stream experience than a single updating body block.

## Default preset flow

The default preset works like this:

1. send a card first
2. show a placeholder inside the reasoning panel
3. stream raw reasoning into the collapsible panel in real time
4. collapse the reasoning panel when the final answer starts streaming
5. continue streaming the final answer in the answer lane

## Not every model can show raw reasoning

This skill does not default to template text pretending to be reasoning.

It first checks:

- whether the current model/provider/runtime truly exposes live reasoning

Then it decides:

- whether raw reasoning can be shown
- or whether only ordinary answer streaming and card UX improvements are possible

That means:

- the skill should first detect what kind of reasoning signal the current path exposes
- only then decide whether true live raw reasoning is feasible
- otherwise stop at diagnosis or continue only with safer card and streaming UX improvements

This also means:

- do not treat a model name as the reason something works
- do not treat a version difference as the reason something must fail
- the real criteria are the emitted reasoning signals and the runtime hooks available in the installed build

## Who this is for

Use this if you:

- use OpenClaw with Feishu
- want a more visible reply process
- want better card 2.0 layouts, collapsible panels, titles, and colors
- have seen issues like `Thinking...`, missing raw reasoning, or title/style regressions

## Installation

Recommended path:

- give this GitHub repository URL directly to OpenClaw
- let it read the repository as a skill source

Repository URL:

- `https://github.com/doashoi/openclaw-feishu-reasoning-ux`

## Minimal trigger examples

- `Help me make OpenClaw replies in Feishu feel more layered`
- `Why does Feishu only show Thinking... now?`
- `I want visible reasoning and better-looking Feishu cards`
- `Help me unify the title, colors, and collapsible reasoning panel`

## FAQ

### Why is raw reasoning sometimes Chinese and sometimes English?

That is a common outcome and does not automatically mean the card implementation is broken.

The reason is usually model/provider-side:

- the model may internally reason in mixed Chinese and English
- the runtime may pass upstream reasoning snapshots through to the UI with minimal transformation
- different prompts may result in different reasoning languages

If what is shown is truly raw reasoning, language consistency is not guaranteed.

### Why do some models stream raw reasoning while others only show Thinking...?

Because different models/providers expose reasoning in different forms.

Common cases:

- readable live reasoning events
- thinking only in the final transcript
- encrypted/opaque reasoning payloads
- no exposed reasoning at all

So this is not only a Feishu card-layer issue. It also depends on the current model path itself.

One important nuance:

- some model paths are not "completely unsupported"
- they may only support snapshot/transcript-only thinking
- in those cases, the model can still preserve reasoning after completion, but it cannot provide true live raw reasoning
- another case is when the model name looks the same as a successful reference case, but the current runtime path still does not emit live reasoning signals
- so the real criterion is what the path outputs, not just what the model is called

So the more accurate statement is often:
- `does not support true live raw reasoning on the current path`
rather than simply:
- `the model does not support reasoning`

### Can everything be forced into Chinese?

You can add a presentation-layer rewrite, but then it stops being strictly raw reasoning.

By default, this skill prioritizes preserving the authenticity of reasoning rather than silently translating or rewriting it.

## References

### Official Feishu docs

- Feishu Card JSON 2.0 structure  
  https://open.feishu.cn/document/feishu-cards/card-json-v2-structure
- `collapsible_panel`  
  https://open.feishu.cn/document/feishu-cards/card-json-v2-components/containers/collapsible-panel
- Feishu card update guide  
  https://open.feishu.cn/document/feishu-cards/update-feishu-card
- PATCH updates for sent message cards  
  https://open.feishu.cn/document/server-docs/im-v1/message-card/patch

### OpenClaw / Telegram references

- OpenClaw Telegram channel docs  
  https://openclawlab.com/en/docs/channels/telegram/
- OpenClaw upstream repository  
  https://github.com/openclaw/openclaw

### Repository-local references

- [SKILL.md](./SKILL.md)
- [references/proven-case-and-pitfalls.md](./references/proven-case-and-pitfalls.md)
- [references/implementation-guide.md](./references/implementation-guide.md)
