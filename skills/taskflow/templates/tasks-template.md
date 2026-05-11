# {{Project Name}} — Tasks

<!-- ============================================================
  TASK FILE FORMAT
  ============================================================

  File name:   tasks/<slug>-tasks.md
  One file per project. Slug matches the ## heading in PROJECTS.md.

  TASK LINE FORMAT:
    - [x| ] (task:<slug>-NNN) [<priority>] [<owner>] <title>

  FIELDS:
    [ ] / [x]   Open / completed. The sync engine drives status
                from the section header, not this checkbox.
                Use [x] for Done (and optionally Pending Validation).

    (task:<id>) Task ID. Format: <slug>-NNN (zero-padded, sequential).
                Custom prefixes are allowed but tooling assumes this pattern.

    [<priority>] REQUIRED. Must come BEFORE the owner tag.
                Defaults: P0 (critical) | P1 (high) | P2 (normal) | P3 (low) | P9 (someday)

    [<owner>]   Optional. Agent or model tag (e.g., codex, sonnet, claude).

    <title>     Human-readable task title.

  NOTES (optional, immediately below task line):
    - note: <text>
    ⚠️  Notes are one-way in v1: removing a note in markdown does
        not clear it in the DB. This is a known limitation.

  SECTION HEADERS (fixed — do not rename):
    ## In Progress        → DB status: in_progress
    ## Pending Validation → DB status: pending_validation
    ## Backlog            → DB status: backlog
    ## Blocked            → DB status: blocked
    ## Done               → DB status: done

  TAG ORDER RULE:
    Priority tag MUST come before owner tag. The parser is positional.
    ✅  - [ ] (task:myproject-007) [P1] [codex] Implement search
    ❌  - [ ] (task:myproject-007) [codex] [P1] Implement search
  ============================================================ -->

## In Progress

## Pending Validation

## Backlog

<!-- Example task — replace with your own and assign the next sequential ID -->
- [ ] (task:{{slug}}-001) [P2] First task for this project

## Blocked

## Done
