# Changelog — task-runner

All notable changes to this skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.1.0] — 2026-02-18

### Changed
- **INTAKE now immediately triggers DISPATCHER in the same turn** — tasks start executing
  the moment they are queued, not on the next heartbeat cycle. Zero wait time for new tasks.
- Heartbeat/cron dispatcher demoted to backup role: handles retries, completion checks,
  and recovery only. Not the primary execution path.
- INTAKE confirmation messages updated: removed "Dispatcher will pick these up on the next
  heartbeat" — replaced with "Starting now..."
- Mode table and A7 success criteria updated to reflect immediate dispatch requirement.

---

## [2.0.3] — 2026-02-18

### Fixed
- Display name corrected to "Task Queue" (was incorrectly "Skill Release Task Runner")

---

## [2.0.2] — 2026-02-18

### Fixed
- Added `permissions` block to `skill.yml` declaring all system-level actions explicitly:
  filesystem access, cron registration, subagent spawning, exec (mkdir only).
  Resolves OpenClaw security scanner "Suspicious" flag for undeclared permissions.

---

## [2.0.1] — 2026-02-18

### Added
- **Step 0: First Run Auto-Setup** — on first INTAKE invocation (queue file absent), the agent
  automatically creates the task directory, initializes the queue file, appends the dispatcher
  entry to HEARTBEAT.md, and registers the backup cron job (every 15 min). No manual setup needed.
- Idempotency check: HEARTBEAT.md entry and cron job are never duplicated on re-initialization.
- Manual recovery path documented: delete queue file to re-trigger Step 0.
- Updated A6 section to reflect that heartbeat/cron setup is now automatic.
- Updated Edge Cases table with first-run and manually-deleted queue scenarios.

---

## [2.0.0] — 2026-02-17

### Added
- Initial release of the task-runner skill
- Multi-task intake: parse natural-language task lists into structured JSON objects
- Task types: info-lookup, file-creation, code-execution, agent-delegation, reminder-scheduling, messaging, unknown
- Execution loop with retry logic (configurable max retries, default 3)
- Per-task verification using type-appropriate checks (references/verification-guide.md)
- Per-task user notification on done/blocked/skipped
- Final summary table after all tasks reach terminal state
- Blocked task handling with `user_action_required` instructions
- Parallel execution support for independent info-lookup and file-creation tasks
- Configurable `TASK_RUNNER_DIR` (TOOLS.md) and `TASK_RUNNER_MAX_RETRIES` (env var)
- Persisted task state to `YYYY-MM-DD-tasks.json` with merge support
- Edge case handling: ambiguous tasks, tool unavailability, task dependencies, 20+ task batching
- Full test suite in `tests/`
- References: `task-types.md`, `verification-guide.md`
