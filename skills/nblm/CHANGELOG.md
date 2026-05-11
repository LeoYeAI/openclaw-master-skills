# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2026-01-24

### Changed
- **BREAKING**: Replaced notebooklm-kit (TypeScript) with notebooklm-py (Python) for all NotebookLM API operations
- Migrated source_manager.py and ask_question.py to async
- API-first approach: queries and uploads use notebooklm-py, browser fallback on failure

### Added
- `NotebookLMWrapper` class - thin async wrapper over notebooklm-py
- Token extraction during auth setup (csrf_token, session_id)
- Silent token refresh on auth errors
- Browser fallback for file uploads using agent-browser upload command
- `AGENTS.md` - mirror of CLAUDE.md for all AI agents

### Removed
- `notebooklm_kit_bridge.mjs` - Node.js bridge no longer needed
- `notebooklm_kit_client.py` - replaced by notebooklm_wrapper.py
- `notebooklm-kit` npm dependency

### Added
- NotebookLM kit bridge and client for NotebookLM uploads
- NotebookLM auth token/cookie persistence in `data/auth/google.json`
- Agent-browser helpers for cookie collection and page evaluation
- API fallback for `ask_question.py` via notebooklm-kit when daemon is unavailable
- Environment variable support for `NOTEBOOKLM_AUTH_TOKEN` and `NOTEBOOKLM_COOKIES`
- HTTP-first refresh for NotebookLM auth tokens using stored cookies with a 10-day staleness policy
- Upload progress tracking that waits for NotebookLM source processing to complete
- Text upload fallback when browser automation is unavailable (set `NOTEBOOKLM_UPLOAD_MODE=text`)
- PDF text extraction fallback via `pypdf`

### Fixed
- Z-Library direct download (`/dl/`) links wait for downloads before navigation
- Z-Library auth detection recognizes login/logout indicators
- NotebookLM auth extraction restores saved browser state and persists tokens after setup
- File uploads now use browser automation so the actual file contents are uploaded

## [2.0.0] - 2026-01-18

### Added
- agent-browser CLI integration for faster, token-efficient automation
- Node.js dependency management via `npm install`

### Changed
- Authentication and query flow now use agent-browser sessions
- Python wrapper updated to drive CLI commands with `--session`

### Removed
- Patchright/Playwright-specific browser helpers and state files

## [1.3.0] - 2025-11-21

### Added
- **Modular Architecture** - Refactored codebase for better maintainability
  - New `config.py` - Centralized configuration (paths, selectors, timeouts)
  - New `browser_utils.py` - BrowserFactory and StealthUtils classes
  - Cleaner separation of concerns across all scripts

### Changed
- **Timeout increased to 120 seconds** - Long queries no longer timeout prematurely
  - `ask_question.py`: 30s → 120s
  - `browser_session.py`: 30s → 120s
  - Resolves Issue #4

### Fixed
- **Thinking Message Detection** - Fixed incomplete answers showing placeholder text
  - Now waits for `div.thinking-message` element to disappear before reading answer
  - Answers like "Reviewing the content..." or "Looking for answers..." no longer returned prematurely
  - Works reliably across all languages and NotebookLM UI changes

- **Correct CSS Selectors** - Updated to match current NotebookLM UI
  - Changed from `.response-content, .message-content` to `.to-user-container .message-text-content`
  - Consistent selectors across all scripts

- **Stability Detection** - Improved answer completeness check
  - Now requires 3 consecutive stable polls instead of 1 second wait
  - Prevents truncated responses during streaming

## [1.2.0] - 2025-10-28

### Added
- Initial public release
- NotebookLM integration via browser automation
- Session-based conversations with Gemini 2.5
- Notebook library management
- Knowledge base preparation tools
- Google authentication with persistent sessions
