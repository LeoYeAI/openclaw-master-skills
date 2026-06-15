# Contributing to MinerU CLI Skill

This skill wraps the `mineru-open-api` CLI. Determine where the problem lies before reporting issues.

## Issue Reporting Guide

### Open an issue in this repository if

- The skill documentation is unclear or missing
- Examples in SKILL.md do not work as described
- You need help using the CLI with this skill wrapper
- The skill is missing a command or flag that the CLI supports

### Open an issue at the mineru-open-cli repository if

- The CLI crashes or throws errors
- Commands do not behave as documented
- You found a bug in document extraction or web crawling
- You need a new feature in the CLI itself

## Before Opening an Issue

1. Install the latest version:

   ```bash
   npm install -g mineru-open-api@latest
   ```

2. Test the command in your terminal to isolate the issue:

   ```bash
   mineru-open-api auth --verify
   mineru-open-api extract test.pdf
   ```

3. Check your authentication:

   ```bash
   mineru-open-api auth --show
   ```

## Issue Report Template

```
**Command:** mineru-open-api extract report.pdf -o ./out/
**Expected:** Markdown output saved to ./out/report.md
**Actual:** [describe what happened]
**OS:** [e.g. macOS 14, Ubuntu 22.04]
```

## Adding New Commands to the Skill

Update SKILL.md when the upstream CLI adds new commands or flags:

- Keep the Installation and Authentication sections current
- Add new commands in the correct category (extract/crawl/auth/status)
- Include usage examples for every new flag
- Update the exit codes table if new codes are added
