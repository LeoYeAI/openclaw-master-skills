---
name: template-skill
description: Starting point for writing a new skill. Use when creating a skill from scratch and you want the expected SKILL.md structure, frontmatter fields, and description conventions to copy from.
---

# Template skill

A skeleton to copy when starting a new skill. Copy this directory, rename it,
and replace each section below.

## Frontmatter

Two fields are required, and both are validated before release:

- `name` — the directory name. Lowercase, hyphen-separated, no spaces.
- `description` — one or two sentences covering *what* the skill does and *when*
  it should be used. This is the only text shown in the index and it is what
  gets matched against a user's request, so lead with the capability and include
  the trigger conditions ("Use when ...").

Anything containing `': '` must be quoted, or the YAML will not parse.

## Body

Write the instructions an agent should follow. What works well:

- Numbered steps when order matters.
- Concrete commands and file paths over descriptions of them.
- The failure cases and what to do about them.
- Any prerequisite: required env vars, installed tools, credentials.

Never hardcode credentials. Read them from the environment and exit with a clear
message when unset.

## Bundled files

Reference extra files by relative path (`scripts/run.py`, `references/api.md`)
and make sure anything referenced actually exists in the directory.
