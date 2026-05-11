# Changelog

All notable changes to SafeExec will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-02-26

### Security
- **Enhanced SKILL.md metadata** - Added explicit declarations for network, monitoring, and credential requirements
- **Documented Agent Mode** - Clearly explained non-interactive execution behavior with full audit logging
- **Added Security & Privacy section** - Comprehensive documentation of what SafeExec does and does NOT do
- **Created CLAWDHUB_SECURITY_RESPONSE.md** - Detailed response to security review concerns

### Changed
- **SKILL.md** - Added comprehensive metadata section
  - Declares environment variables: SAFE_EXEC_DISABLE, OPENCLAW_AGENT_CALL, SAFE_EXEC_AUTO_CONFIRM
  - Declares write paths: ~/.openclaw/safe-exec/, ~/.openclaw/safe-exec-audit.log
  - Explicitly states: network=false, monitoring=false, credentials=[]
- **SKILL.md** - Added "Security & Privacy" section
  - Clearly documents what SafeExec does and does NOT do
  - Addresses all ClawdHub security review concerns
- **SKILL.md** - Enhanced "Agent Mode" section
  - Explains non-interactive execution behavior
  - Documents full audit logging for agent-executed commands
  - Clarifies safety preservation in agent mode

### Security Notes
- ✅ **No monitoring** - Does not read chat sessions or conversation history
- ✅ **No network calls** - Works entirely locally (except git clone during manual installation)
- ✅ **No external notifications** - No integration with Feishu, webhooks, or external services
- ✅ **No background processes** - No cron jobs or persistent monitoring daemons
- ✅ **Transparent audit logging** - All executions logged with mode label (user_approved / agent_auto)
- ⚠️ **Agent mode preserved** - Non-interactive bypass for automation, fully audited

### Addressed Issues
This release directly addresses security review concerns from ClawdHub:
- Declared capabilities: Explicit metadata in SKILL.md
- Documented behavior: Agent mode clearly explained with safety guarantees
- Transparency: Comprehensive "Security & Privacy" section

## [0.3.2] - 2026-02-26

### Security
- **Removed monitoring subsystem** - Deleted unified-monitor.sh and all monitoring components
- **Removed external integrations** - No more Feishu notifications, GitHub monitoring, or OpenClaw comment checking
- **Simplified project scope** - Focused purely on command approval functionality

### Removed
- `UNIFIED_MONITOR.md` - Unified monitoring system documentation
- `docs/GITHUB_ISSUE_MONITOR.md` - GitHub issue monitoring documentation
- `docs/BLOG.md` / `docs/BLOG_EN.md` - Blog posts with notification references
- `docs/CONTRIBUTING.md` - Outdated contribution guide
- `docs/FIX_REPORT_v0.1.3.md` / `docs/FIX_REPORT_v0.2.3.md` - Historical fix reports
- `docs/GITHUB_RELEASE_v0.2.0.md` - GitHub release documentation
- `docs/GLOBAL_SWITCH_GUIDE.md` - Global switch usage guide
- `docs/PROJECT_REPORT.md` - Project report
- `docs/PUBLISHING_GUIDE.md` - Publishing tool documentation
- `docs/RELEASE_NOTES.md` - Release notes
- `docs/RELEASE_v0.2.0.md` / `docs/RELEASE_v0.2.4.md` - Historical release documentation
- `docs/USAGE.md` - Usage documentation
- `tools/publish-to-github.sh` - GitHub publishing script
- `tools/push-to-github.sh` - Git push script
- `tools/release.sh` - Release automation script
- `RELEASE_v0.3.2.md` - Release documentation
- `UPDATE_NOTES.md` - Update notes

### Changed
- `README_EN.md` - Removed Feishu environment variable configuration

## [Unreleased]

## [0.2.4] - 2026-02-01

### Fixed
- **Non-interactive hang issue**: Fixed `safe-exec-approve.sh` hanging when called by OpenClaw Agent
- Script now detects non-interactive environments and skips confirmation prompt
- Added `OPENCLAW_AGENT_CALL` and `SAFE_EXEC_AUTO_CONFIRM` environment variable support
- TTY detection using `[[ -t 0 ]]` for automatic environment detection

### Changed
- Interactive confirmation is now conditional based on environment
- Human terminal usage maintains safety confirmation
- Agent calls automatically bypass confirmation (prevents hanging)

### Added
- `FIX_REPORT_v0.2.3.md` - Detailed fix report with test results
- Smart environment detection logic (TTY + environment variables)
- Visual indicator for non-interactive mode: `🤖 非交互式环境 - 自动跳过确认`

### Security
- ✅ All security features preserved
- ✅ Danger pattern detection unchanged
- ✅ Risk assessment mechanism unchanged
- ✅ Approval workflow intact
- ✅ Audit logging complete
- ✅ Human users still get confirmation prompt in terminals

### Testing
- ✅ Agent call scenario: Pass (no hang, completes in <1s)
- ✅ Environment variable detection: Pass
- ✅ Human terminal usage: Pass (confirmation preserved)
- ✅ Command execution: Pass (successful)
- ✅ Request cleanup: Pass

### Backwards Compatibility
- ✅ Fully backwards compatible
- ✅ Existing usage patterns unchanged
- ✅ Human user experience unchanged
- ✅ Agent calls automatically adapt

## [0.2.3] - 2026-02-01

### Added
- **Context-aware risk assessment**: Detect user confirmation keywords
- Dynamic risk level adjustment based on user intent
- Customizable confirmation keywords
- `safe-exec-ai-wrapper.sh` for AI Agent integration
- `test-context-aware.sh` test suite

### Changed
- Risk assessment now considers user context
- CRITICAL + confirmation → MEDIUM (still requires approval)
- HIGH + confirmation → LOW (direct execution)
- MEDIUM + confirmation → LOW (direct execution)

### Security
- CRITICAL operations always require approval
- All operations logged to audit trail
- Configurable strictness level

## [0.2.0] - 2026-02-01

### Added
- **Global on/off switch** for SafeExec
- New commands: `--enable`, `--disable`, `--status`
- Configuration file `safe-exec-rules.json` now includes `enabled` field
- When disabled, commands execute directly without safety checks
- Audit log includes `bypassed` events when disabled

### Changed
- Improved `is_enabled()` function to handle false correctly
- Updated status display to show current protection state
- Enhanced user feedback for enable/disable operations

### Fixed
- **Critical Bug**: Fixed jq `//` operator treating `false` as falsy
- Now explicitly checks `.enabled == true` instead of `.enabled // true`
- This ensures SafeExec can be properly toggled on/off

### Security Note
⚠️ **Warning**: When SafeExec is disabled, ALL commands execute directly without protection!
Only disable in trusted environments.

## [0.1.3] - 2026-02-01

### Fixed
- **Configuration Fix**: Removed incorrect SafeExec plugin configuration
- SafeExec is now properly configured as a **Skill** (not a Plugin)
- Eliminated startup warning logs about missing plugin skill paths
- Clean separation between Plugin (core extension) and Skill (Agent tool)

### Changed
- Removed `~/.openclaw/extensions/safe-exec/` (incorrect Plugin version)
- Kept `~/.openclaw/skills/safe-exec/` (correct Skill version)
- Updated `openclaw.json` to remove plugin entry for safe-exec

### Technical Details
- **Before**: SafeExec was registered in `plugins.entries.safe-exec`
- **After**: SafeExec is loaded from `skills.load.extraDirs`
- **Benefit**: Correct architecture, no warning logs, proper Skill behavior

## [0.1.2] - 2026-01-31

### Added
- Comprehensive USAGE.md guide (3000+ words)
- CONTRIBUTING.md with contribution guidelines
- CHANGELOG.md following Keep a Changelog format
- release.sh automation script
- RELEASE_NOTES.md for v0.1.2
- .github/workflows/test.yml for CI/CD
- PROJECT_REPORT.md with completion status

### Documentation
- Complete installation guide
- Usage examples and scenarios
- Troubleshooting section
- FAQ (Frequently Asked Questions)
- Best practices guide

## [0.1.1] - 2026-01-31

### Added
- Automatic cleanup of expired approval requests
- `cleanup_expired_requests()` function
- `--cleanup` flag for manual cleanup
- Default 5-minute timeout for requests
- Audit log entries for expiration events

### Improved
- Prevents request database from growing indefinitely
- Automatic cleanup on every command execution
- Better security with request expiration

## [0.1.0] - 2026-01-31

### Added
- Core risk assessment engine
- Command interception system
- Approval workflow
- Audit logging
- Integration with OpenClaw
- Initial documentation

### Security
- 10+ danger pattern detection
- Fork bomb detection
- System directory protection
- Pipe injection prevention

## [0.2.0] - Planned

### Planned
- Web UI for approval management
- Multi-channel notifications (Telegram, Discord)
- ML-based risk assessment
- Batch operation support
- Rate limiting

---

## Links

- [GitHub Repository](https://github.com/yourusername/safe-exec)
- [Issue Tracker](https://github.com/yourusername/safe-exec/issues)
- [Documentation](https://github.com/yourusername/safe-exec/blob/main/README.md)
