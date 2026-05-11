# Instagram Carousel Skill

Skill for generating Instagram carousel HTML with:

- fresh data
- safe slide layout
- simple language
- consistent color systems

## What This Skill Enforces

1. Mandatory kickoff questions:
   palette direction and tone of voice
2. Fresh data only:
   current year or previous year, unless explicitly marked as latest available
3. Safe layout:
   top copy must stay visible, bottom content must stay above the progress bar
4. Clear language:
   simple Russian, short sentences, no slang, minimal jargon

## Core Composition Patterns

- `Hero`
  opening hook + subtitle + one strong stat
- `Problem`
  heading + short intro + 1-2 proof blocks
- `Solution`
  heading + compact feature list
- `Entity Showcase`
  one ETF, company, tool, or category per slide
- `Overview / Verdict`
  shortlist, comparison, or selection logic
- `CTA`
  final call to action without swipe arrow

## Dense Slide Rule

On dense slides, split content into:

- `top-safe-copy`
  label + heading + short intro
- `support-stack`
  proof cards, stats, comparisons

If the slide becomes too tall:

1. remove the last optional block
2. tighten support spacing
3. shorten supporting copy

Never let visible content sit behind the progress bar.

## File Map

- `SKILL.md`
  main operating rules
- `references/components.md`
  layout and component patterns
- `agents/openai.yaml`
  optional OpenAI/Codex UI metadata
- `skill.json`
  generic metadata for non-OpenAI environments

## Compatibility Note

The real source of truth is `SKILL.md`.

- OpenAI/Codex can use `agents/openai.yaml`
- Claude, OpenClaw, or other agents can ignore `agents/openai.yaml` and use `SKILL.md` plus `skill.json`

## Recommended Prompt

Use this skill to create an Instagram carousel with fresh data, simple language, and a safe export-ready layout.
