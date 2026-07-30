# CHANGELOG - Proactive Tasks

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-02-12

### Added - Phase 2: Production Ready Architecture

#### WAL Protocol (Write-Ahead Logging)
- New `log_to_wal()` function logs critical changes before data modification
- Prevents data loss on context cutoff
- Creates `memory/WAL-YYYY-MM-DD.log` files automatically
- Integrated into mark-progress, log-time, mark-blocked, health-check commands
- Logs event types: PROGRESS_CHANGE, TIME_LOG, STATUS_CHANGE, HEALTH_CHECK

#### SESSION-STATE.md - Active Working Memory
- Auto-updated on every task operation
- Captures: Current task, progress, time logged, blockers, next action
- Serves as active working memory for current session
- Updated on: progress changes, time logs, status changes
- Includes velocity calculations (faster/slower than estimate)

#### Working Buffer - Danger Zone Capture
- `working-buffer.md` template captures updates during context-cutoff risk periods
- Auto-appends all task updates (PROGRESS, TIME_LOG, STATUS_CHANGE)
- Flushes to daily memory file (`memory/YYYY-MM-DD.md`) on compaction
- `flush-buffer` command triggers manual flush
- Prevents info loss when context gets truncated mid-session

#### Self-Healing Health Check
- New `health-check` command detects and fixes broken task states
- Detects 5 categories of issues:
  1. Orphaned recurring tasks (no parent goal)
  2. Impossible states (completed but progress < 100)
  3. Missing completion timestamps
  4. Corrupted times (actual >> estimate)
  5. Future-dated completed tasks
- Auto-fixes 4 safe categories, flags time anomalies for human review
- Run with: `python3 scripts/task_manager.py health-check`

#### Autonomous Operation Architecture
- Two-mode system: Interactive (systemEvent) vs Autonomous (isolated agentTurn)
- Documentation: `HEARTBEAT-CONFIG.md` with complete guidance
- Key principle: Don't use systemEvent for background work
- Includes heartbeat polling pattern (recommended for most work)
- Includes isolated cron patterns (velocity reports, cleanup)
- Anti-patterns documented to avoid

#### Evolution Guardrails
- `EVOLUTION.md` with VFM/ADL scoring frameworks for new features
- VFM Protocol: Value Frequency Multiplier (3x HF, 3x FR, 2x UB, 2x SC)
- ADL Protocol: Architecture Design Ladder (Stability > Explainability > Reusability > Scalability > Novelty)
- Pass threshold: >= 60 VFM points AND ADL PASS
- Prevents feature creep, maintains production stability

#### New Commands
- `mark-progress <task_id> <percent>` - Set task progress with WAL logging
- `log-time <task_id> <minutes>` - Log time spent with velocity calculation
- `mark-blocked <task_id> <reason>` - Mark task blocked with reason
- `health-check` - Detect and auto-fix broken states
- `flush-buffer` - Manually flush working buffer to daily memory

### Changed
- Main script now integrated: `scripts/task_manager.py` includes all Phase 1 + Phase 2 commands
- All task updates now create WAL entries automatically
- SESSION-STATE.md updated on every task change
- Working buffer auto-captures all updates
- SKILL.md updated with Autonomous Operation section and Evolution reference
- README now describes v1.2.0 Phase 2 features

### Documentation
- New: `HEARTBEAT-CONFIG.md` - Complete autonomous operation guide
- New: `EVOLUTION.md` - VFM/ADL scoring frameworks
- Updated: `SKILL.md` - Added Autonomous Operation and Evolution sections
- Reference: Phase 2 Plan in `PHASE2-PLAN.md`

### Testing
- Full workflow test: create goal → task → progress → log time → velocity
- Verified: SESSION-STATE updates on each operation
- Verified: WAL logs created for all critical events
- Verified: Working buffer captures and flushes correctly
- Verified: Health-check detects and fixes broken states
- Verified: All Phase 2 commands integrated and working

### Technical Details
- No breaking changes to Phase 1 API
- All Phase 1 commands continue to work as before
- Phase 2 commands are additive (new functionality)
- Data format unchanged (backward compatible)
- New files: SESSION-STATE.md, WAL logs, working buffer template

---

## [1.1.0] - 2026-02-12

### Added
- Recurring task support with next_due_at tracking
- time_variance_percent calculation for velocity tracking
- Blocked state reason tracking (blocked_reason field)
- Update task command for flexible modifications

### Fixed
- Task status transitions more robust
- Better error messages for missing tasks/goals

---

## [1.0.0] - 2026-02-05

### Initial Release
- Core task/goal management
- Priority and status tracking
- Task dependencies and blocking
- Time estimates and tracking
- Heartbeat integration ready
- CLI commands for all operations

---

## Version History Summary

| Version | Date | Focus | Status |
|---------|------|-------|--------|
| 1.0.0 | 2026-02-05 | Core features | Released |
| 1.1.0 | 2026-02-12 | Velocity tracking | Released |
| 1.2.0 | 2026-02-12 | Production resilience | Released |

---

## Roadmap

### Planned for v1.3.0
- Goal-level velocity dashboards
- Recurring task templates
- Batch task operations
- Performance optimization for 1000+ tasks

### Possible for v2.0.0
- Multi-agent goal coordination
- Distributed task processing
- Advanced analytics and ML-based predictions
- Web UI for goal/task management

---

**Built by Toki with production resilience patterns from Proactive Agent v3.1.0** 🚀
