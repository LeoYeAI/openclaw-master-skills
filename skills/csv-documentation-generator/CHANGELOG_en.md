# Changelog - CSV Documentation Generator

All notable version updates are documented here.

## [1.6.4] - 2026-03-20

### Fixed

#### System Prompt Integration Documentation Clarification
- Emphasized that System Prompt integration is a **manual configuration** step, not automatic
- Explained that OpenClaw skills only execute when active, cannot persist instructions across skill switches

### Changed

#### Documentation Enhancements
- SKILL.md: Added --auto-add examples, --verbose option, AI Agent usage examples
- README.md/README_en.md: AI Agent usage examples, --verbose option

## [1.6.1] - 2026-03-20

### Fixed

#### CLI Error Handling Improvement
- **EOFError handling**: When running in non-interactive mode (e.g., AI agent usage), automatically falls back to autonomous mode
- No longer throws EOFError, instead switches mode and continues execution

#### UX Improvements
- **--verbose flag**: New `-v/--verbose` parameter to show detailed generation progress
- **Auto compliance check**: After `generate all`, automatically checks requirements.json and displays compliance issues
- **Agent Mode documentation**: Added Agent Mode section in README

## [1.6.0] - 2026-03-19

### Added

#### Smart Bilingual Mode
- **--language parameter**: New `--language` parameter to select content language ('zh' or 'en')
- **Intelligent bilingual processing**: `process_markdown_table_bilingual()` function that intelligently processes output based on `--bilingual` and `--language`

#### Cross-Skill Code Annotation Coordination
- **STANDARDS.md**: New standards documentation with System Prompt integration instructions
- **standards/code-annotations.json**: Central code annotation registry supporting 15 programming languages
- **scripts/standards_reader.py**: Standards reader tool for use by other skills

#### CLI Improvements
- **--auto-add/--yes flag**: New `--auto-add` and `--yes` flags for `cli.py parse` command for non-interactive use

### Changed

#### Bilingual Behavior
- `--bilingual true` (default): Headers remain bilingual, content follows `--language`
- `--bilingual false`: Pure single-language output, determined by `--language`
- Users and AI agents now have full control over document language output

#### Gitignore Updates
- Added `ses_*.json` and `session-*.md` to .gitignore

## [1.5.0] - 2026-03-19

### Changed

#### Skill Design Philosophy Refactoring
- **SKILL.md simplification**: Reduced from 1034 to ~785 lines, moved prompt content to prompts.md
- **Semantic Action Graph**: New explicit semantic action graph definition showing document generation dependencies
- **prompts.md created**: Critical Thinking Constraints, triggering conditions, and fill prompts moved to separate file
- **SemanticActions class**: New class in generate.py encapsulating dynamically callable capability nodes for AI agents

#### Architecture Changes
- **Skill = Tool Semantic Encapsulation + Trigger Conditions**: Refactored to better align with this design philosophy
- **SKILL.md**: Now contains only Skill Definition + Semantic Action Graph + Execution Interface
- **prompts.md**: Contains all prompt templates and thinking constraints
- **generate.py**: Acts as Execution Engine exposing SemanticActions interface

## [1.4.0] - 2026-03-19

### Added

#### GAMP 5 Second Edition Compliance
- **M12 Critical Thinking**: Added critical thinking constraints (M12.1~M12.5) guiding AI through systematic risk thinking during validation
- **Document Generation Triggering Conditions**: New trigger condition library defining pre-fill data for VP/URS/FS/RA/IQ-OQ-PQ/VSR
- **Content Fill Prompt Library**: New URS/FS/RA fill prompt templates
- **Data Flow Definitions**: New inter-document data flow rules (VP→RA→FS→Test→VSR automatic traceability)

#### Example Files
- **templates/examples/urs-example.md**: Complete CTMS URS example
- **templates/examples/fs-example.md**: FS traceability example
- **templates/examples/ra-example.md**: Hierarchical risk assessment example
- **templates/examples/iq-example.md**: IQ check items example

## [1.3.4] - 2026-03-19

### Changed

#### Documentation Updates
- **Standard Modules Table**: Removed "URS Section" column (was inconsistent with dynamic numbering)
- Added note: Section numbers are dynamically assigned based on existing sections in template

## [1.3.3] - 2026-03-19

### Fixed

#### GxP Compliance Fix
- **Dynamic Section Numbering**: Removed hardcoded `STANDARD_MODULES` number mapping, now uses `_get_next_section_number()` to dynamically calculate next available 4.X number in template
- Ensures custom modules (e.g., `pm_query`, `multi_lock`) get unique, non-conflicting section numbers
- Added SKILL.md documentation explaining section numbering behavior

## [1.3.2] - 2026-03-19

### Fixed

#### Bug Fixes
- **Sync Module Section Fix**: `sync_bidirectional()` `to-template` branch now correctly groups requirements by module and creates corresponding section headers (`### 4.X Module Name`) instead of simply appending table rows
- Fixed issue where custom modules (e.g., `pm_query`, `multi_lock`) couldn't create sections

## [1.3.1] - 2026-03-19

### Fixed

#### Bug Fixes
- **Sync Path Fix**: `sync_bidirectional()` now writes to project directory instead of skill directory
- **RTM Filename Fix**: RTM filename now correctly includes project name, format `RTM_{project}.xlsx`

## [1.3.0] - 2026-03-19

### Added

#### Phase 2 (P1) Features
- **P1.1 Git Hooks**: `scripts/git-hooks/post-commit` and `install.sh` for post-commit compliance checks
- **P1.2 Compliance Checker**: `generate.py check` command with coverage, high-risk module, and test coverage checks
- **P1.3 Incremental Update**: `--diff-only` parameter with SHA256 hash-based smart rebuild

#### Phase 3 (P2) Features
- **P2.1 Bidirectional Sync**: `--sync --sync-direction {to-json|to-template|both}` with conflict detection
- **P2.2 Monorepo Support**: `--project-root` parameter, auto-detects `apps/`, `packages/` structures
- **P2.3 CI/CD Templates**: `templates/ci/github-actions.yml` and `gitlab-ci.yml`
- **P2.4 Template Versioning**: Automatic migration and compatibility checking

## [1.1.2] - 2026-03-18

### Fixed

#### ID Format Unification
- **Unified ID prefix**: Changed all `UR-xxx` to `URS-xxx` to comply with GAMP 5 standard
- templates/urs.md: UR-001~055 → URS-001~055
- templates/vsr.md: UR-001~002 → URS-001~002

## [1.1.1] - 2026-03-18

### Added

#### SKILL.md Standardization
- **Frontmatter enhancement**: Added complete YAML frontmatter structure
- **Extended triggers**: Added GxP, 21 CFR Part 11, electronic signature, electronic record, EDC, CTMS, eTMF, LIMS, medical device triggers
- **inputSchema definition**: Standardized input parameter structure
- **outputSchema definition**: Standardized output document format
- **Metadata completion**: version, author, createdAt, validationStatus fields
- **requiredTools declaration**: Explicit exec tool permission requirement
- **Path fix**: Use `<SKILL_DIR>` placeholder instead of hardcoded paths

## [1.1.0] - 2026-03-18

### Added

#### Requirements Traceability System
- **Data model enhancement**: Requirement class added module, fs_ref, ts_ref, test_cases fields
- **Module grouping**: Support for 8 standard modules (user_mgmt, audit_trail, data_mgmt, business_func, reporting, integration, security, compliance)
- **AI comment parsing**: Support for `@URS[module]` format comment markers, enabling automatic traceability when AI agents generate code
- **Template sync feature**: `--sync` option automatically syncs requirements from requirements.json to template sections
- **RTM auto-generation**: Generate 14-column traceability matrix Excel from requirements.json
- **Test result linking**: Automatically link test results to requirements and update status

#### SKILL.md Updates
- Added Requirements Traceability section
- Code comment standards (AI agents must follow)
- Standard modules definition table
- Test Case ID format specification
- Auto-Sync feature usage instructions

## [1.0.1] - 2026-03-18

### Fixed

#### Word Generator Bug Fixes
- **Fixed table rendering bug**: `_process_content` method was exiting loop after first table, now processes all tables correctly (24 tables rendered)
- **Fixed header cell text loss bug**: `_style_header_cell` method now receives text as explicit parameter instead of relying on cell.text after `para.clear()`
- **Improved color contrast**: Header color changed from #4682B4 (Steel Blue, 3.2:1) to #2563EB (Royal Blue, 4.6:1) to meet WCAG 4.5:1 requirement
- **Unified fonts**: Chinese text uses SimSun (宋体), English text uses Arial

#### Documentation Fixes
- **Fixed dependency installation**: Use `pip install -r requirements.txt` instead of installing packages individually

## [1.0.0] - 2026-03-18

### Added

#### Core Features
- **9 Validation Document Templates** (VP, URS, FS, TS, RA, IQ, OQ, PQ, VSR)
- **Professional GMP-Style Word Generator**
  - Header color: Steel blue (#4682B4) + white text
  - Priority markers: `[必须]`, `[应该]`, `[Pass]`, `[Fail]`
  - Cover page + approval signature table
  - Alternating row colors
- **Bilingual Chinese/English Support**

#### AI Agent Intelligent Requirements Tracking System
- **Agent Mode Detection** (`scripts/agent.py`)
  - Auto-detect OpenClaw/OpenCode/Codex agent types
  - Support `interactive` (semi-auto) and `autonomous` (full-auto) modes
  - Environment variable priority: `CSV_DOCS_MODE` > Agent env vars > Git config > Project config

- **Requirements Parser** (`scripts/requirements/parser.py`)
  - Parse requirements from code comments: `@req`, `@requirement`, `# URS-001`
  - Auto-detect electronic signature requirements (21 CFR Part 11)
  - Keywords: 签名, 审核, 审批, sign, approve, etc.

- **Risk Analyzer** (`scripts/requirements/risk_analyzer.py`)
  - RPN/FMEA methodology
  - Auto severity/likelihood/detectability assessment
  - GAMP Category-based risk calculation
  - Standard mitigation suggestions

- **Git Linker** (`scripts/requirements/linker.py`)
  - Auto-parse requirement IDs from commit messages
  - Requirements ↔ Commit traceability matrix

- **Test Results Parser** (`scripts/tests/parser.py`)
  - Support JUnit XML, pytest JSON, NUnit XML formats
  - Auto-link requirements to test status
  - Test coverage statistics

- **Document Auto-Filler** (`scripts/fill/filler.py`)
  - Auto-fill template variables from requirements database
  - Document completeness validation

- **Audit Log** (`scripts/audit/log.py`)
  - Complete record of all operations
  - Export to PDF (text format)
  - Filter by operation type and mode

#### CLI Unified Entry Point (`scripts/cli.py`)

```bash
csv-docs init              # Initialize project config
csv-docs agent             # Detect agent mode
csv-docs agent --set autonomous  # Set to autonomous mode
csv-docs parse ./src       # Parse code for requirements
csv-docs status            # Show status
csv-docs add "description" # Add requirement
csv-docs risk              # Run risk analysis
csv-docs test --results ./ # Parse test results
csv-docs generate vp       # Generate document
csv-docs audit            # Show audit log
```

#### Compliance Support
- **GAMP 5 Second Edition** validation lifecycle
- **21 CFR Part 11** Electronic Records and Signatures
- **EU Annex 11** Computerized Systems
- **ALCOA+** Data Integrity Principles

### Configuration

#### Project Config (`.csv-docs-config.json`)
```json
{
  "agent": {
    "default_mode": "interactive",
    "auto_detect": true
  },
  "autonomous": {
    "on_duplicate": "overwrite"
  },
  "compliance": {
    "gamp_category": null,
    "auto_esig_detection": true,
    "auto_ra": true,
    "esig_keywords": ["签名", "审核", "审批", "sign", "approve"]
  }
}
```

#### Requirements Database (`requirements.json`)
- Stores all requirements, risks, test results, commit links

#### Audit Log (`audit-log.json`)
- Complete audit trail of all operations

---

## [0.1.0] - Initial Version

### Added
- Basic document templates
- Word generator
- Excel generator
- GAMP 5 reference documents
- 21 CFR Part 11 reference documents
- EU Annex 11 reference documents
- Data integrity reference documents

---

## Version Format

Version format follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible new features
- **PATCH**: Backward-compatible bug fixes
