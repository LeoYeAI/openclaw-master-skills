# Changelog

All notable changes to Tide Watch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.6] - 2026-03-01

### Fixed
- **Metadata: Declared OPENCLAW_SESSION_ID environment variable**
  - Added to `requires.env.optional` in SKILL.md frontmatter
  - Addresses ClawHub scan finding: UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID
  - Env var is optional (only for --current flag, v1.3.4+)
  - Not required for Directives-Only mode

### Changed
- **Security scan rating improvement**
  - v1.3.5: BENIGN/SUSPICIOUS (undeclared env var)
  - v1.3.6: Expected BENIGN/BENIGN (metadata corrected)

### Impact
- ClawHub automated eligibility checks now accurate
- User expectations aligned with actual dependencies
- No code changes - metadata fix only

---

## [1.3.5] - 2026-03-01

### Fixed
- **Terminology: Resume vs Restore** (Issue #37)
  - Changed `restorePromptCommand` → `resumePromptCommand` in code
  - "Resume" = session resumption prompts (context loading)
  - "Restore" = OpenClaw trigger word (loads from backup/archive)
  - Using "restore" in Tide Watch caused unintended OpenClaw behavior
  - Updated HEARTBEAT.md.template: "Backup Restoration" → "Loading Session Backups"
  - Updated SKILL.md: "Restore from Backup" → "Load Session from Backup"

### Added
- **Comprehensive CLI documentation** (Issue #37)
  - New CLI Reference section with all flags and options
  - Documented `--raw-size` flag (added in v1.3.2)
  - Documented `--current` flag (added in v1.3.4)
  - Documented enhanced `--session` (partial IDs, multiple sessions, added in v1.3.3)
  - Usage examples for all new features
  - Version tags on new features (v1.3.2+, v1.3.3+, v1.3.4+)

### Changed
- **Frontmatter metadata** (Issue #37)
  - Capability: "session-restoration" → "session-resumption"
  - Added capabilities: "multi-agent-support", "auto-detection"

### Impact
- Prevents OpenClaw restore trigger confusion
- Complete documentation for CLI flags added in v1.3.2-v1.3.4
- Clear examples for all new features
- Proper capability tagging

---

## [1.3.4] - 2026-03-01

### Added
- **Multi-agent aware session recommendations** (Fixes #35)
  - Dashboard recommendations now respect agent boundaries
  - Only suggests shifting work within same agent's sessions
  - Prevents inappropriate cross-agent recommendations
  - Example: Won't suggest shifting from Kintaro → Motoko
  - Shows agent name in recommendations for clarity
  
- **Session auto-detection for heartbeat monitoring** (Fixes #36)
  - Auto-detect current session via `OPENCLAW_SESSION_ID` environment variable
  - New `--current` flag: `tide-watch check --current`
  - Implicit auto-detection: `tide-watch check` (when env var set)
  - JSON output for heartbeat scripting: `tide-watch check --current --json`
  - Graceful fallback with helpful errors when env var not available

### Changed
- **Session shift recommendations (multi-agent improvement):**
  - Before: Suggested ANY low-capacity session (cross-agent)
  - After: Only suggests same-agent sessions
  - Single-agent setups: No change (backward compatible)
  - Multi-agent setups: Better recommendations aligned with agent roles

- **Check command behavior:**
  - Can now auto-detect current session (when `OPENCLAW_SESSION_ID` set)
  - Backward compatible: `--session <id>` still works as before
  - Clearer error messages when auto-detection unavailable

### Technical
- Updated `getRecommendations()` in `lib/capacity.js`
  - Group high-capacity sessions by agent
  - Filter low-capacity sessions by `agentId`
  - Only recommend same-agent shifts
  
- Updated `checkCommand()` in `bin/tide-watch.js`
  - Read `OPENCLAW_SESSION_ID` environment variable
  - Support `--current` flag
  - Use `getAllSessions()` for auto-detected sessions
  - Enhanced error messages with troubleshooting steps

### Impact
- **Multi-agent users:** Recommendations respect agent persona boundaries
- **Single-agent users:** No change (all sessions belong to same agent)
- **Heartbeat monitoring:** More efficient session capacity checks (when OpenClaw core adds env var support)
- **Backward compatibility:** All existing commands work unchanged

### Security
- Both changes assessed as BENIGN (high confidence)
- No new file access or external operations
- Read-only environment variable access (safe)
- Filtering logic improvements only

### Notes
- Session auto-detection pending OpenClaw core support
- Feature is implemented and ready when `OPENCLAW_SESSION_ID` is exported
- Users can manually set env var for testing

---

## [1.3.3] - 2026-02-28

### Added
- **Session-specific archiving** (Fixes #34)
  - Archive specific sessions by ID: `tide-watch archive --session abc123`
  - Archive multiple sessions: `tide-watch archive --session abc123 --session def456`
  - Partial ID matching: `--session 595765f8-c` matches full UUID
  - Works with labels: `--session "#navi-code-yatta"`
  - Works with channels: `--session discord`
  - Supports `--dry-run` for preview

### Changed
- **Archive command now supports two modes:**
  - Time-based: `--older-than <time>` (existing behavior)
  - Session-specific: `--session <id>` (new)
  - Mutually exclusive: cannot use both together
  - One is required: must specify either `--older-than` OR `--session`

### Technical
- Enhanced session resolution with partial UUID matching
- Validates conflicting flags (--session + --older-than)
- Multi-agent support for session-specific archiving
- Updated help text and examples

### Impact
- Selective archiving after saving specific sessions to memory
- Archive completed project sessions regardless of age
- More control over which sessions to archive

---

## [1.3.2] - 2026-02-28

### Added
- **Human-readable token sizing** (Fixes #33)
  - Default: Relative sizing (18.7k/128k, 20.6k/1M, 19.3k/2M)
  - Much easier to scan than comma-separated full numbers
  - Especially helpful for Gemini (1M-2M contexts)
  
- **Optional `--raw-size` flag**
  - Shows full precision with commas: `18,713/128,000`
  - Works for one-time output: `tide-watch dashboard --raw-size`
  - Works for live dashboard: `tide-watch dashboard --watch --raw-size`
  - NOT persisted (ephemeral, command-line only)

### Changed
- **Token display format:**
  - Default: `18.7k/128k` (clear, scannable)
  - Raw mode: `18,713/128,000` (exact, opt-in)
  - Formatting rules:
    - < 1k: raw number (850)
    - 1k-100k: k with decimal (18.7k)
    - 100k-1M: k without decimal (171k)
    - 1M+: M with decimal (1.0M, 2.0M)

### Technical
- New functions: `formatSize()`, `formatTokens()`
- Updated: `formatDashboard()`, `formatTable()`, `formatTableRow()`
- Added `--raw-size` CLI flag parsing
- Exported `formatTokens` for reuse

### Impact
- Faster visual scanning of capacity percentages
- Reduces cognitive load when viewing dashboard
- Precision available when needed via flag

---

## [1.3.1] - 2026-02-28

### Fixed
- Display name metadata (ClawHub publication)
  - Corrected display name to "Tide Watch" (was incorrectly inferred as "OpenClaw Tide Watch")
  - No code changes, metadata-only republication

---

## [1.3.0] - 2026-02-28

### Added
- **Dynamic context limit detection** (Fixes #32)
  - Three-tier fallback: OpenClaw CLI → Config file → Hardcoded defaults
  - Automatically detects context limits from `openclaw models list`
  - Falls back to `~/.openclaw/openclaw.json` models.providers
  - Enhanced hardcoded defaults for Gemini and Ollama models
  - Future-proof: automatically picks up new models from OpenClaw

### Changed
- **Accurate capacity percentages for all models:**
  - Gemini 2.5 Flash: Now shows 2.1% (was 10.3% - 5x improvement)
  - Gemini 3.1 Pro: Now shows ~1% (was ~10% - 10x improvement)
  - qwen2.5:14b: Now shows 14.6% (was 9.4% - now accurate)
  - Claude Sonnet: Uses actual 195k from OpenClaw (was hardcoded 200k)

### Technical
- New functions: `getContextFromCLI()`, `getContextFromConfig()`, `getContextFromDefaults()`
- Enhanced `getModelMaxTokens()` with dynamic detection
- Hardcoded defaults now include Gemini and Ollama variants
- Graceful degradation when OpenClaw CLI unavailable

### Impact
- Users with Gemini models see accurate capacity (not false warnings)
- Users with Ollama models see correct context limits per model
- Warnings trigger at correct thresholds for all models
- No more premature session resets for high-context models

---

## [1.2.1] - 2026-02-28

### Fixed
- Archive command crash with multi-agent sessions (Fixes #31)
  - Sessions now track their source directory (`session.sessionDir`)
  - Archive groups sessions by source directory
  - Each agent's sessions archived to correct agent directory
  - Handles multiple archive locations properly
- Missing `path` import in archive command output display
  - Added `const path = require('path');` to bin/tide-watch.js
  - Fixed crash after successful archiving

### Technical
- All 113 tests pass
- Verified with 19-session multi-agent archive test
- SECURITY-ASSESSMENT-v1.2.1.md: BENIGN

## [1.2.0] - 2026-02-28

### Added
- **Multi-agent session discovery** (Fixes #30)
  - Auto-discovers all configured agents from `~/.openclaw/openclaw.json`
  - Unified dashboard showing sessions from all agents
  - Agent column displays agent name/identity for each session
  - Per-agent summary with counts and average capacity
  - Zero configuration needed - auto-discovers from OpenClaw setup
  - Backward compatible - single-agent users see no change

- **Agent filtering and control**
  - `--all-agents` flag: Multi-agent mode (default)
  - `--single-agent-only` flag: Legacy single-agent mode (main agent only)
  - `--agent <id>` flag: Filter dashboard to specific agent
  - `--exclude-agent <id>` flag: Exclude specific agent (repeatable)

- **Enhanced dashboard formatting**
  - Agent column when multi-agent sessions detected
  - Per-agent summary section with stats
  - Automatic layout adjustment for multi-agent vs single-agent
  - Agent metadata display (name, identity)

### Changed
- `getAllSessions()` now auto-discovers multi-agent setups by default
- Dashboard adapts layout based on agent detection (backward compatible)
- Session directory resolution improved to handle multiple path conventions

### Fixed
- Session directory resolution for agents with `agentDir` ending in `/agent`
- Handles OpenClaw config path variations gracefully
- Graceful fallback to main agent if config doesn't exist

### Techincal
- New functions: `discoverAgents()`, `resolveSessionDir()`, `getSessionsFromDir()`
- Enhanced `formatDashboard()` with multi-agent layout
- Robust path resolution with multiple fallback locations
- All 113 tests pass
- Zero new dependencies

## [1.1.6] - 2026-02-28

### Added
- Hybrid configuration system (Fixes #29)
  - CLI flags for per-invocation overrides
  - Environment variables for session-specific settings
  - Config file (`~/.config/tide-watch/config.json`) for persistent preferences
  - Precedence: CLI flags > env vars > config file > defaults
- Configuration options:
  - `refreshInterval`: Dashboard watch refresh (default: 10s)
  - `gatewayInterval`: Gateway status check interval (default: 30s)
  - `gatewayTimeout`: Gateway command timeout (default: 3s)
- Input validation with clear error messages
- Secure file permissions (config dir: 0700, config file: 0600)
- Comprehensive configuration documentation in README.md

### Changed
- Dashboard watch mode now uses configurable refresh interval (was hardcoded 10s)
- Gateway status check uses configurable interval/timeout (were hardcoded 30s/3s)

### Security
- Config file created with user-only permissions (0600)
- All configuration inputs validated (type + range)
- Whitelist approach for config keys
- JSON data format (not executable)
- Graceful error handling with safe defaults

## [1.1.5] - 2026-02-28

### Fixed
- Gateway status timeout increased to 3000ms (Fixes #28)
  - v1.1.4 async check inherited 500ms timeout from v1.1.3 sync version
  - Gateway probe takes 1-2 seconds, was timing out
  - Increased to 3 seconds (async = no blocking)
  - Gateway status now displays correctly ("🟢 Online")

## [1.1.4] - 2026-02-28

### Changed
- Gateway status check now fully async - eliminates ALL blocking (Fixes #27)
  - Replaced execSync with exec (async callback-based)
  - Dashboard refresh always instant (0ms, never blocks)
  - First load shows "⏳ Checking..." then updates when complete
  - Background check updates cache without blocking
  - Reduced refresh interval from 60s to 30s

### Performance
- First load: instant (vs 500ms in v1.1.3)
- Cache expiry: instant (vs 500ms in v1.1.3)
- All dashboard refreshes: 0ms blocking (perfect smoothness)
- Gateway status updates every 30 seconds in background

## [1.1.3] - 2026-02-28

### Fixed
- Gateway status check no longer blocks live dashboard refresh (Fixes #26)
  - Cache gateway status for 60 seconds (instead of checking every 10s)
  - Reduced timeout from 5000ms to 500ms (fail fast)
  - Dashboard refresh now instant (no blocking on gateway check)
  - Graceful fallback to cached status on timeout/error

### Performance
- Live dashboard refresh: instant (< 100ms instead of 1-2.5s)
- Gateway status only checked once per minute
- Eliminates "blink out of existence" issue in Terminal.app

## [1.1.2] - 2026-02-28

### Fixed
- Live dashboard refresh UX - eliminated screen flashing (Fixes #25)
  - Replaced console.clear() with ANSI cursor positioning
  - Smooth in-place updates without visible flicker
  - 0.5-2.5 second gap eliminated

### Added
- Real-time change tracking and visual highlighting in live dashboard (Refs #25)
  - Color-coded trend indicators: 🔴 Red ↑ (increasing), 🟢 Green ↓ (decreasing), 🟡 Yellow (new)
  - Shows capacity delta percentage (+X.X% / -X.X%)
  - Track session state between refreshes
  - New Trend column in dashboard output
  - Makes live monitoring actually useful for tracking progress

### Changed
- Dashboard watch mode now professional-grade terminal UI
- ANSI escape sequences for smooth rendering
- Differential updates show only what changed

## [1.1.1] - 2026-02-28

### Fixed
- Metadata/documentation inconsistency flagged by ClawHub security scan (Fixes #24)
  - Removed `node` and `npm` from mandatory `requires.bins`
  - Added `anyBins: ["node"]` for optional CLI detection
  - Updated install spec label to clarify Node.js requirement
  - Added mode comparison table to SKILL.md
  - Clarified Directives-Only mode uses built-in tools (no CLI)
- Added deprecation notice to outdated SECURITY-ANALYSIS.md

### Changed
- Node.js is now truly optional (Directives-Only mode requires nothing)
- Documentation accurately reflects hybrid skill architecture
- Expected ClawHub scan result: BENIGN (high confidence)

## [1.1.0] - 2026-02-28

### Added
- Model display in session listings (Fixes #22)
  - Table format now shows model name for each session
  - Dashboard format includes model column (25 char width)
  - Helps track which sessions are using paid vs. free models
- Gateway status indicator (Fixes #23)
  - Dashboard now shows OpenClaw gateway online/offline status
  - Visual indicator: 🟢 Online / 🔴 Offline
  - Helps diagnose connection issues faster

### Changed
- Dashboard width increased from 95 to 120 characters to accommodate model column
- Table header updated to include Model column

## [1.0.7] - 2026-02-25

### Fixed
- Added `.js` extension to bin/tide-watch.js for ClawHub compatibility
- Added postinstall script to set executable permissions
- Achieved Benign/Benign security rating on ClawHub

## [1.0.0 - 1.0.6] - 2026-02-23 to 2026-02-25

### Added
- Initial release
- Session capacity monitoring
- Resumption prompt management
- Session archiving
- Dashboard and report views
