# Changelog

All notable changes to the ClawSec Scanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2026-03-10

### Changed

- Replaced simulated DAST checks with real OpenClaw hook execution harness testing
- Updated DAST semantics so high-severity findings are emitted for actual hook execution failures/timeouts, not static payload pattern matches
- Reclassified DAST harness capability limitations (for example missing TypeScript compiler for `.ts` hooks) to `info` coverage findings instead of high severity
- Added DAST harness mode guard to prevent recursive scanner execution when hook handlers are tested in isolation

### Added

- New DAST helper executor script for isolated per-hook execution and timeout enforcement
- DAST harness regression tests covering no-false-positive baseline and malicious-input crash detection

## [0.0.1] - 2026-02-27

### Added

- Initial release of ClawSec Scanner skill
- Automated vulnerability scanning for OpenClaw skill installations
- Integration with advisory feed for real-time security alerts
- Support for scanning skill dependencies and detecting known CVEs
- Configurable scan policies and risk thresholds
- Detailed vulnerability reporting with remediation guidance
