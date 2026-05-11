# Changelog

All notable changes to the CC_GodMode Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.11.3] - 2026-02-16

### Changed
- Resolved remaining ClawHub scan ambiguity by aligning runtime declarations with actual workflow instructions.
- Updated `SKILL.md` note to distinguish **docs-only package** from **runtime agent actions**.

### Runtime/Permission Transparency
- Declared runtime expectations for full workflow usage:
  - `requires_binaries: true`
  - `requires_credentials: true`
  - `requires_network: true`
- Added explicit `runtime_binaries` (required/optional) and `runtime_credentials` (optional) sections.
- Clarified security semantics:
  - No install-time executable payload
  - Agent runtime may execute shell/network operations when user invokes workflows.

## [5.11.2] - 2026-02-16

### Changed
- Added `clawdis.yaml` with explicit runtime/security declarations to reduce scanner ambiguity.
- Clarified `SKILL.md` metadata (`author`, `repository`, tags) and bumped version to `5.11.2`.
- Added top-level disclaimer: skill is documentation-only (no bundled executables, no credentials required).

### Security/Transparency
- Declared `type: orchestration-docs`.
- Declared `runtime.requires_binaries: false` and `runtime.requires_credentials: false`.
- Added explicit notes that model names are examples and depend on user OpenClaw configuration.

## [5.11.1] - 2026-02-04

### Added
- Initial OpenClaw Skill release
- Complete SKILL.md with all 8 agent specifications
- Collapsible `<details>` sections for detailed agent docs
- Quick Start section for immediate usage
- Dual Quality Gates documentation
- Workflow diagrams in ASCII art
- ClawHub publishing workflow

### Features from CC_GodMode v5.11.1
- **@tester Fail-Safe Reporting**
  - Graceful degradation chain: Full → Partial → Failure Report
  - Structured error output (JSON) for programmatic handling
  - Screenshot-on-failure best practice
  - MCP Health Check (Pre-Test) instructions

- **@researcher Timeout & Graceful Degradation**
  - Hard timeout: 30 seconds MAX per task
  - Partial results format for incomplete research
  - Memory usage guidelines

- **8 Specialized Agents**
  - @researcher (haiku) - Knowledge Discovery
  - @architect (opus) - System Design
  - @api-guardian (sonnet) - API Lifecycle
  - @builder (sonnet) - Implementation
  - @validator (sonnet) - Code Quality
  - @tester (sonnet) - UX Quality
  - @scribe (sonnet) - Documentation
  - @github-manager (haiku) - GitHub Operations

- **Dual Quality Gates**
  - 40% faster validation with parallel execution
  - @validator (Code) + @tester (UX) run simultaneously
  - Decision matrix for result coordination

- **7 Standard Workflows**
  - New Feature
  - Bug Fix
  - API Change
  - Refactoring
  - Release
  - Process Issue
  - Research Task

### Technical Details
- YAML frontmatter for ClawHub metadata
- Version 1:1 mapping with CC_GodMode versions
- Self-contained documentation (no external dependencies)
- Context-window optimized with collapsible sections

## [Unreleased]

### Planned
- Extended workflow customization
- Domain pack integration
- Custom agent model selection
