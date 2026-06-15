# Contributing to china-mirror-resolver

Thank you for your interest in contributing! This skill helps developers in
mainland China resolve slow package downloads by maintaining a self-healing
mirror source resolver.

## How to Contribute

### Report a Dead Mirror Source

1. Open an issue with the title: `[Dead Source] <tool> - <provider>`
2. Include: the URL, when it stopped working, the error message
3. If you know a replacement, suggest it in the issue

### Add a New Mirror Source

1. Verify the source is from a known institution (university, cloud vendor, or well-known OSS org)
2. Test it with the validation scripts: `bash scripts/validate.sh <tool>`
3. Submit a PR updating:
   - `SKILL.md` Section 2 (Baseline Sources table)
   - `scripts/validate.sh` and `scripts/validate.ps1` (add the new URL)
   - `references/config-templates.md` (if config format differs)

### Add Support for a New Tool

1. Add the tool to Section 1 (Diagnostic Table) with error keywords and detect command
2. Add baseline sources to Section 2
3. Add validation method to Section 4.2
4. Add config template to `references/config-templates.md`
5. Add restore command to Section 6
6. Add search query to Section 3.1
7. Update both validation scripts

### Fix a Bug or Improve Documentation

PRs are welcome. Please describe what you changed and why.

## Guidelines

- **Test before submitting**: Run `bash scripts/validate.sh` (or `.ps1`) to verify your changes
- **Keep SKILL.md concise**: Detailed templates go in `references/config-templates.md`
- **Bilingual**: Section headers should have English titles. Chinese annotations are welcome in tables and notes
- **No personal mirrors**: Only add sources from recognized institutions
- **Update CHANGELOG.md**: Add your changes under an `[Unreleased]` section

## Code of Conduct

Be respectful and constructive. We're all here to help each other build better tools.
