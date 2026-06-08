# Memory Positioning and Boundary Design

## Scope

This design tightens the repository messaging around what this project is and is not.

The update is intentionally documentation-only:

- Clarify that this repository is a local-first memory workflow, not a hosted memory platform.
- Make the file-layer boundaries easier to understand at a glance.
- Introduce lightweight concepts for stable profile, active context, and optional project scope.
- Reframe OpenViking and similar systems as optional recall backends or adapters.

This iteration does not add new commands, new storage formats, or automatic extraction behavior.

## Goals

- Preserve the repository's current local-file workflow as the core product.
- Explain the difference between recovery state, distilled memory, raw notes, and archive material.
- Make room for future semantic recall integrations without turning them into hard dependencies.
- Incorporate lessons from memory-platform products without changing this repository into one.

## Non-Goals

- Build a hosted memory API.
- Add connector infrastructure, sync daemons, or MCP services.
- Introduce automatic profile extraction, conflict resolution, or forgetting logic.
- Replace the current templates or script contract.

## Current Problem

The current README documents the workflow correctly, but the product positioning is still easy to misread:

- `MEMORY.md`, `memory/`, Obsidian, and optional semantic search are described, but their boundaries are spread across multiple sections.
- OpenViking is marked optional, but the broader concept of "optional recall backend" is not explicit.
- The repository does not clearly say that it is a workflow guide and file contract rather than an online memory product.

## Options Considered

### Option 1: Keep the current README structure and only mention more optional tools

Pros:

- Smallest edit.

Cons:

- Does not clarify the product boundary.
- Leaves memory-layer concepts implicit.

### Option 2: Add explicit memory-layer and backend-boundary sections

Pros:

- Matches the repository's actual value.
- Makes external references such as Supermemory easier to position correctly.
- Improves onboarding without changing runtime behavior.

Cons:

- Requires moderate README restructuring across languages.

### Option 3: Expand into a larger architecture document and defer README cleanup

Pros:

- More detailed.

Cons:

- Adds documentation weight before fixing the main entry points.

## Recommended Design

Adopt Option 2.

### README messaging changes

Add explicit language that this repository is:

- A local-first Agent memory workflow
- Based on durable files and manual distillation
- Compatible with optional semantic recall backends
- Not a hosted or API-first memory platform

### Memory boundary section

Add a compact section that explains:

- `SESSION-STATE.md`: active recovery state for the interrupted task
- `working-buffer.md`: rough scratchpad and write-ahead notes
- `MEMORY.md`: distilled stable profile, preferences, decisions, and recurring pitfalls
- `memory/`: daily notes and project-scoped raw history
- Obsidian or external search backends: deeper archive and optional recall

### Stable profile and active context

Add guidance that `MEMORY.md` should emphasize:

- Stable profile: lasting preferences, conventions, recurring decisions
- Active context: only the small amount of ongoing context that should survive startup

Daily notes remain the place for volatile execution history.

### Project scope concept

Add a lightweight recommendation that entries may include a project or repo reference when one workspace serves multiple efforts.

This stays a convention, not a new required schema.

### Optional backend positioning

Broaden OpenViking messaging so it still remains optional, while making clear that:

- OpenViking is one example of an optional semantic recall backend
- Other tools or services can fill the same role later
- The local recovery layer remains authoritative

## Files Expected To Change

- `README.md`
- `README_EN.md`
- `README_CN.md`
- `INSTALL.md`

## Acceptance Criteria

- The main README entry points clearly describe the repository as a local-first workflow.
- The documentation distinguishes recovery state, distilled memory, raw notes, and archive/search layers.
- OpenViking remains explicitly optional and not required for the core workflow.
- The documentation allows optional external backends without implying a platform pivot.
