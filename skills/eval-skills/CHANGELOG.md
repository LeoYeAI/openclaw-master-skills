# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Core**: Support for creating Skills from OpenAPI specs (`create --from-openapi`).
- **Core**: Configurable `passThreshold` for `LlmJudgeScorer`.
- **Core**: Token usage tracking in `HttpAdapter` and reports.
- **Core**: Incremental result persistence to SQLite.
- **CLI**: Global `--json` and `--verbose` flags.
- **CLI**: `csv` report format support.

### Changed
- **Core**: Refactored `SqliteStore` schema to include `run_id` in primary key.
- **Core**: Improved `LlmJudgeScorer` with OpenAI SDK, retries, and concurrency limits.
- **Core**: Enhanced `HtmlReporter` using `marked` for better Markdown rendering.
- **Core**: Fixed duplicate persistence in `EvaluationEngine`.
- **CLI**: Fixed `run` command skill path logic.

### Fixed
- **Core**: CSV escaping in `CsvReporter`.
