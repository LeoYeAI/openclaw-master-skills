# Changelog

All notable changes to this skill will be documented in this file.

## [2.1] - 2026-03-08

### Added
- **CONTRIBUTING.md**: contribution guidelines for the open source community
- **references/config-templates.md**: detailed config templates extracted from SKILL.md (progressive disclosure)
- **Docker daemon.json merge logic**: safe merge scripts (bash + PowerShell) that preserve existing config fields
- **Gradle Kotlin DSL** (`build.gradle.kts`) config template alongside Groovy DSL
- **Bilingual search queries**: Section 3.1 now provides both Chinese and English query templates
- **Security warnings**: explicit notes on `trusted-host` SSL bypass risk and malicious mirror danger
- **JSON output mode**: `--json` flag for validate.sh and `-Json` flag for validate.ps1
- **Homebrew section** in validate.ps1 (was missing, now symmetric with validate.sh)
- **Cursor .mdc and Windsurf .md** complete format examples in Section 9
- **ARM architecture note** in Section 7
- **WSL 1 vs WSL 2 difference** note in Section 7
- **Multi-version environment** note (pyenv, nvm, conda envs) in Section 7

### Changed
- **Execution flow rewritten**: step 3 now tests ALL baseline sources with speed thresholds (< 3s/10s), picks fastest; step 4 has explicit "search failed" branch; step 5 has "all candidates fail" branch
- **validate.sh**: replaced `set -euo pipefail` with `set -uo pipefail` to fix `((0++))` exit trap; replaced `date +%s%N` with portable `_now_ms()` function (GNU date → perl → python3 → second-level fallback) for macOS compatibility; replaced `((PASS++))` with `PASS=$((PASS+1))`
- **SKILL.md size reduced**: detailed config templates moved to `references/config-templates.md`, SKILL.md now contains quick reference only
- **Section headers**: simplified to English-only for cleaner Agent parsing (Chinese retained in descriptions and notes)
- **yarn/pnpm**: separate diagnostic entries and config commands (yarn v1 vs v2+ distinction)

### Fixed
- validate.sh crashes on macOS due to `date +%s%N` not supported
- validate.sh exits prematurely when PASS=0 due to `set -e` + `((0++))` bash trap
- Docker config template could overwrite existing daemon.json fields (log-driver, etc.)
- Step 3 accepted slow sources (8s+) as "reachable" without speed check
- Search failure had no handling branch (flow diagram dead end)
- validate.ps1 missing homebrew test section (asymmetric with validate.sh)

## [2.0] - 2026-03-08

### Added
- **Agent Skills open standard compliance**: `license`, `compatibility`, `allowed-tools`, `metadata` frontmatter fields
- **Cross-agent adaptation guide** (Section 9): Cursor (.mdc), Windsurf (.md), Gemini, generic LLM
- **Graceful degradation**: agents without web search can still use baseline sources
- **Capability requirements table**: declares terminal, file, search, fetch dependencies
- **New tools**: yum/dnf (CentOS/RHEL/Fedora), yarn, pnpm
- **New baseline sources**: Tencent (pip), Huawei (npm/Maven), RsProxy.cn (Rust), USTC (Homebrew)
- **Validation scripts**: `scripts/validate.sh` (bash) and `scripts/validate.ps1` (PowerShell)
- **README.md**: bilingual (English + Chinese) with installation and usage guide
- **LICENSE**: MIT
- **CHANGELOG.md**: this file
- **Bilingual SKILL.md**: section headers in English + Chinese for international accessibility
- **Known unstable sources** section with verification dates
- **Docker macOS path** added to config templates

### Changed
- Rewrote execution flow to include capability gate (search optional, not required)
- Search strategy now uses abstract "agent's available search mechanism" instead of hardcoded tool names
- Validation acceptance criteria refined (3s/10s thresholds)
- All config templates now cover Windows + macOS + Linux paths explicitly

### Removed
- Hardcoded dependency on specific search tool names (WebSearch)
- Douban pip source (confirmed dead)
- ghproxy.cc (confirmed dead, SSL error)

## [1.0] - 2026-03-08

### Added
- Initial release
- Self-healing workflow: diagnose → baseline → search → validate → configure
- Baseline source table for 12 tool categories
- Search query templates with credibility ranking
- HTTP + tool-specific validation methods
- Config templates for all supported tools
- Restore official sources table
