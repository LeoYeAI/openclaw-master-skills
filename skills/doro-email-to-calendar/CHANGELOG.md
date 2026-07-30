# Changelog

## [1.13.1] - 2026-02-05

### Fixed
- **Complete Shell Quoting Fix**: Fixed remaining `eval ... $ARGS` patterns missed in v1.13.0
  - Affected scripts: `calendar_delete.sh`, `email_read.sh`, `email_send.sh`, `undo.sh`, `process_calendar_replies.sh`
  - Converted string-based argument building to bash arrays with `"${ARGS[@]}"` expansion
  - All shell scripts now use safe array-based argument passing

## [1.13.0] - 2026-02-05

### Fixed
- **Critical Shell Quoting Bug**: Fixed `eval ... $ARGS` pattern in all shell scripts that caused arguments with embedded quotes to fail silently
  - Affected scripts: `disposition_email.sh`, `email_modify.sh`, `email_search.sh`, `calendar_search.sh`, `create_event.sh`, `check_duplicate.sh`
  - Now uses proper bash array expansion `"${ARGS[@]}"` for safe argument passing
  - This was causing email disposition (mark read, archive) to fail after event creation
  - This was causing event tracking to `events.json` to fail

- **Duplicate Detection Logic**: Fixed flawed duplicate detection for short titles
  - Previously: Single-word titles like "Fastelavn" matched ANY event containing that word on the same date
  - Now: Short titles (1-2 keywords) require ALL keywords to match; longer titles require 50% match
  - Prevents false-positive duplicates and missed actual duplicates

### Added
- **Add Pending Invite Function**: New `add_pending_invite()` function in `pending_ops.py`
  - Records pending invites when events are presented to user (was missing entirely)
  - Enables heartbeat reminders to work correctly
  - Prevents `pending_invites.json` from staying empty

- **add_pending.sh**: New shell wrapper script for adding pending invites
  - Usage: `add_pending.sh --email-id <id> --email-subject <subject> --events-json <json>`
  - Uses proper array-based argument passing

- **Unit Tests**: 4 new tests for `add_pending_invite()` function
  - `test_add_new_invite`
  - `test_add_updates_existing_invite`
  - `test_add_multiple_events`
  - `test_add_creates_file_if_missing`

### Changed
- **SKILL.md**: Updated workflow documentation to use `add_pending.sh` for recording pending invites

## [1.12.1] - 2026-02-04

### Added
- **Agent Attribution**: Event descriptions now include "Created by [agent_name] (AI assistant)" footer
  - Configurable via `agent_name` in config.json (default: "Ripurapu")

### Changed
- **SKILL.md Critical Rules**: Added prominent warnings about using scripts vs direct `gog` calls
  - Rule 1 now explicitly forbids direct `gog` usage
  - Rule 2 warns to ignore calendar notification emails (from `calendar-notification@google.com`)
  - Added large warning block with WRONG/RIGHT examples
- **BOOT.md**: Complete rewrite with critical operating rules
  - Added "Critical Operating Rules" section listing all wrapper scripts
  - Added explicit warning to ignore calendar notification emails
  - Updated heartbeat section templates with calendar notification exclusion
  - Added configuration reference section
- **create_event.sh**: Auto-appends agent attribution to all event descriptions
- **CONTRIBUTING.md**: Updated test count to 154

## [1.12.0] - 2026-02-04

### Added
- **Automatic Email Disposition**: Emails are now automatically marked read and archived after event creation
  - New `scripts/utils/disposition_ops.py`: Core disposition logic with `get_disposition_settings()` and `disposition_email()`
  - New `scripts/disposition_email.sh`: Shell wrapper for manual disposition
  - New `scripts/process_calendar_replies.sh`: Process calendar reply emails (accepts, declines, tentatives)
- **Calendar Reply Auto-Processing**: Automatically disposition unread calendar notifications from Google Calendar
  - Matches patterns: Accepted, Declined, Tentative, Updated invitation, Cancelled
  - Run manually with `process_calendar_replies.sh` or `process_calendar_replies.sh --dry-run`
- **New Config Option**: `email_handling.auto_dispose_calendar_replies` (default: true)
- **Unit Tests**: 19 new tests for disposition operations in `test_disposition_ops.py`

### Changed
- **create_event.sh**: Now automatically dispositions source email after successful event creation
- **Default Config**: `archive` now defaults to `true` (was `false`) for cleaner inbox management
- **SKILL.md Section 6**: Replaced manual email handling instructions with automatic disposition documentation

### Documentation
- `SETUP.md`: Added `auto_dispose_calendar_replies` config option
- Updated all example configs to include the new option and use `archive: true` default

## [1.11.0] - 2026-02-03

### Added
- **Provider Abstraction Layer**: All email and calendar operations now go through wrapper scripts
  - New `scripts/utils/email_ops.py`: Provider-agnostic email operations (read, search, modify, send)
  - New `scripts/utils/calendar_ops.py`: Provider-agnostic calendar operations (search, create, update, delete)
  - New shell wrappers: `email_read.sh`, `email_search.sh`, `email_modify.sh`, `email_send.sh`
  - New shell wrappers: `calendar_search.sh`, `calendar_delete.sh`
- **Provider Configuration**: New `provider` field in config.json (default: "gog")
- **`--provider` Parameter**: All scripts now accept optional `--provider` override

### Changed
- **create_event.sh**: Now uses `calendar_ops.py` instead of direct `gog` calls
- **undo.sh**: Now uses `calendar_ops.py` for all calendar operations
- **check_duplicate.sh**: Now uses `calendar_search.sh` wrapper
- **event_tracking.py**: Validation now uses `calendar_ops.search_events()` instead of subprocess
- **SKILL.md**: All `gog` command examples replaced with wrapper script calls
  - LLM should NEVER call `gog` directly - always use scripts for proper tracking

### Documentation
- `SETUP.md`: Added `provider` configuration option documentation
- Updated all example configs to include `provider` field

### Future Extension
To add a new provider (e.g., Outlook):
1. Add implementation in `email_ops.py` and `calendar_ops.py`
2. Set `"provider": "outlook"` in config
3. No script changes needed

## [1.10.0] - 2026-02-03

### Added
- **Deadline Detection**: Automatically detects RSVP, registration, and ticket deadlines from emails
  - Scans for patterns like "RSVP by [date]", "Register by [date]", "Tickets available until [date]"
  - Extracts deadline_date, deadline_action, and deadline_url fields
- **Deadline Reminder Events**: Creates separate calendar events for action-required deadlines
  - Title format: `DEADLINE: [Action] for [Event Name]`
  - Set at 9:00 AM on the deadline date (30 min duration)
  - Includes email reminder 1 day before + popup reminder 1 hour before
- **Action Required Warnings**: Main events with deadlines include prominent capital letter warnings
  - Format: `*** ACTION REQUIRED: [ACTION] BY [DATE] ***`
  - Warning placed at the beginning of event description
- **Email Notifications**: Optional email alerts for events requiring user action
  - New config: `deadline_notifications.enabled` and `deadline_notifications.email_recipient`
  - Uses `gog gmail send` command
  - Includes event details, deadline, action required, and link
- **Improved URL Extraction**: URLs now placed at the beginning of event descriptions
  - Format: `Event Link: [URL]` appears right after any deadline warning
  - Makes action links more visible and accessible

### Changed
- **Event Description Format**: Structured format with clear sections
  1. Action warning (if deadline exists)
  2. Event link (if URL found)
  3. Event details from email

### Documentation
- `references/gog-commands.md`: Added `gog gmail send` command documentation
- `SETUP.md`: Added `deadline_notifications` configuration section with examples

## [1.9.1] - 2026-02-02

### Added
- **Comprehensive Test Suite**: 135 unit tests for all Python utility modules
  - `tests/test_common.py`: Tests for shared utility functions
  - `tests/test_date_parser.py`: Tests for date/time parsing
  - `tests/test_json_store.py`: Tests for JSON file operations
  - `tests/test_event_tracking.py`: Tests for event tracking operations
  - `tests/test_pending_ops.py`: Tests for pending invites operations
  - `tests/test_activity_ops.py`: Tests for activity logging
  - `tests/test_changelog_ops.py`: Tests for changelog operations
  - `tests/test_invite_ops.py`: Tests for invite status updates
  - `tests/test_undo_ops.py`: Tests for undo operations
- **Test Runner**: `scripts/run_tests.sh` for easy test execution
- **Zero-Dependency Testing**: All tests use Python's built-in `unittest` module (no pip install required)

### Changed
- `utils/__init__.py`: Added package init file for proper module imports

## [1.8.0] - 2026-02-02

### Changed
- **Major Refactoring**: Extracted embedded Python to shared utility modules
  - `utils/json_store.py`: Common JSON file operations (load_json, save_json, ensure_dir)
  - `utils/common.py`: Shared utilities (get_day_of_week, format_timestamp, generate_id, time_ago)
  - `utils/changelog_ops.py`: Changelog logic extracted from changelog.sh
  - `utils/activity_ops.py`: Activity log logic extracted from activity_log.sh
  - `utils/pending_ops.py`: Pending invites logic extracted from list_pending.sh
  - `utils/event_tracking.py`: Event tracking logic consolidated from multiple scripts
  - `utils/invite_ops.py`: Invite status updates extracted from update_invite_status.sh
  - `utils/undo_ops.py`: Undo helper functions extracted from undo.sh
- **Streamlined SKILL.md**: Reduced from 41KB to 10KB (75% reduction)
  - Removed redundant setup section (now references SETUP.md)
  - Moved detailed CLI reference to references/gog-commands.md
  - Consolidated repetitive examples
- **Refactored Scripts**: Shell scripts now thin wrappers delegating to Python utilities
  - changelog.sh: 436 → 111 lines
  - activity_log.sh: 282 → 84 lines
  - list_pending.sh: 235 → 36 lines
  - Fixed duplicate get_day_of_week() function in list_pending.sh

### Added
- **references/gog-commands.md**: Detailed gog CLI reference with recurrence patterns, flags, and advanced syntax

## [1.7.0] - 2026-02-02

### Added
- **Shared Date Parser**: Extracted date/time parsing to `scripts/utils/date_parser.py` to reduce code duplication (~70 lines removed)
- **Capability Requirements**: Skill now declares semantic capabilities (`read_email`, `create_calendar_event`, `update_calendar_event`) instead of just binary requirements
- **Email Scanning Heartbeat**: BOOT.md now includes email scanning section for automatic email checks during heartbeat cycles
- **Capability Verification**: On first activation, skill verifies agent has required email/calendar capabilities

### Changed
- **Tool Flexibility**: SKILL.md and SETUP.md now note that `gog` commands are reference examples; agents with alternative tools (MCP servers, other CLIs) can use those instead
- **package.json**: `requires.capabilities` added alongside `requires.bins`
- **create_event.sh**: Now uses shared `date_parser.py` instead of inline Python
- **check_duplicate.sh**: Now uses shared `date_parser.py` instead of inline Python

## [1.6.0] - 2026-02-02

### Added
- **Smart Onboarding**: Auto-detects Gmail accounts and calendars, presents all 9 settings with smart defaults. User can accept all with Enter or change specific items by number.
- **Silent Activity Log**: All processing activity logged to `activity.json`. Users can ask "what did you skip?" or "show me activity" to see what happened. New script `activity_log.sh`.
- **Event Changelog with Undo**: All calendar changes logged to `changelog.json`. Changes can be undone within 24 hours. New scripts `changelog.sh` and `undo.sh`.
- **Day-of-Week Display**: Events now show day of week for verification (e.g., "Feb 12, Wednesday").
- **LLM-Based Duplicate Matching**: Semantic matching for duplicates instead of simple keyword matching. Explains updates to user.
- **Recurring Event Detection**: Detects patterns like "Every Tuesday at 3pm" and creates appropriate RRULE.
- **Batched Reminders with Dismissal Tracking**: Pending invites are batched, track reminder_count, auto-dismiss after 3 ignored reminders.
- **Orphaned Event Cleanup**: `--validate` flag on `lookup_event.sh` checks if events still exist in calendar and removes orphaned tracking entries.

### Changed
- **Email Search Strategy**: Removed `newer_than:1d` filter to catch stale forwards (old emails forwarded today). Now processes all unread emails and relies on "already processed" check.
- **create_event.sh**: Now logs changes to changelog.json for undo support, captures before/after state for updates.
- **lookup_event.sh**: Added `--validate` flag for orphan cleanup on 404/410.
- **list_pending.sh**: Added `--update-reminded` and `--auto-dismiss` flags, shows day-of-week, tracks reminder_count.
- **SKILL.md**: Major rewrite with smart onboarding flow, activity logging, changelog/undo documentation, LLM matching guidance, recurring event detection.
- **SETUP.md**: Simplified to reflect smart defaults approach.

### Fixed
- Stale forward handling: Old emails forwarded today are now properly processed.
- Orphaned events: Events deleted in Google Calendar are now automatically removed from tracking.

## [1.5.0] - 2026-02-02

### Added
- **Pending Invites Reminder System**: Events that aren't actioned immediately are tracked and resurfaced during heartbeat cycles
- **pending_invites.json**: New tracking file for undispositioned events with status tracking (pending/created/dismissed/expired)
- **list_pending.sh**: Script to list all pending invites (JSON or human-readable summary)
- **update_invite_status.sh**: Script to update event status after user decisions
- **BOOT.md**: Self-bootstrapping instructions for ClawHub installations
- **HEARTBEAT.md integration**: Pending invites are checked during heartbeat cycles

### Changed
- **create_event.sh**: Now automatically updates pending_invites.json when creating events
- **SKILL.md**: Added Steps 5.1 and 5.2 for recording and updating pending invites

## [1.4.0] - 2026-02-02

### Added
- **Selective Selection**: Users can now cherry-pick events by number (e.g., '1, 2, 3'), 'all', or 'none' instead of binary yes/no confirmation
- **Self-Healing Tracking**: When updating an event that was deleted externally (404/410), automatically removes stale tracking entry and creates a new event

### Removed
- **extract_events.py**: Deleted Python extraction script - Agent now extracts events directly using natural language understanding (better accuracy for phrases like "next Tuesday, not this one")

### Changed
- Step 3 (Extract Events) now instructs Agent to extract directly instead of using regex-based script
- Step 5 (Present Items) uses numbered selection UI for better user control

## [1.3.0] - 2026-02-01

### Added
- Event tracking system with `events.json` for efficient updates/deletions
- Tracking scripts: `track_event.sh`, `lookup_event.sh`, `update_tracked_event.sh`, `delete_tracked_event.sh`
- `create_event.sh` now automatically tracks created events
- Email ID tracking to prevent duplicate processing

### Changed
- Duplicate detection now checks local tracking before calendar search

## [1.2.0] - 2026-01-31

### Added
- Direct inbox monitoring mode (scans all emails for events)
- Forwarded email mode (processes forwarded emails only)
- `--send-updates all` flag support for attendee notifications (tonimelisma fork)
- Email handling options (mark read, archive)

## [1.1.0] - 2026-01-30

### Added
- Auto-create and ignore patterns in config
- Multi-day event support with RRULE recurrence
- Attendee support with configurable email list

## [1.0.0] - 2026-01-29

### Added
- Initial release
- Email parsing and event extraction
- Google Calendar integration via gog CLI
- Duplicate detection
- Configuration wizard
