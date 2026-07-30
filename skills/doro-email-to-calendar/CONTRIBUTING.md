# Contributing to email-to-calendar

## Development Setup

The skill is located at `~/.openclaw/workspace/skills/email-to-calendar/` and source-controlled separately from the main server config repo.

## Definition of Done (DOD)

After completing any work on this skill, you must complete ALL of the following:

### 1. Run Tests
```bash
cd ~/.openclaw/workspace/skills/email-to-calendar/scripts
./run_tests.sh
```
All 154 tests must pass before proceeding.

### 2. Update CHANGELOG.md
Document what changed with today's date, following existing format.

### 3. Bump Version
Update version in both files:
- `package.json` - the `version` field
- `SKILL.md` - the frontmatter `version` field

Version format: `MAJOR.MINOR.PATCH`
- PATCH: Bug fixes, minor tweaks
- MINOR: New features, non-breaking changes
- MAJOR: Breaking changes to API or workflow

### 4. Commit Changes
```bash
cd ~/.openclaw/workspace/skills/email-to-calendar
git add -A
git status  # Review changes
git commit -m "Description of changes"
```

### 5. Push to Remote
```bash
git push origin master
```

### 6. Publish to ClawHub
```bash
export CLAWHUB_REGISTRY=https://auth.clawdhub.com
clawhub publish ~/.openclaw/workspace/skills/email-to-calendar --version X.Y.Z
```

The `--version` flag is required due to a CLI bug.

## File Structure

| Path | Purpose |
|------|---------|
| `SKILL.md` | Main skill instructions (read by agents) |
| `SETUP.md` | User configuration guide |
| `BOOT.md` | Self-bootstrapping instructions |
| `CHANGELOG.md` | Version history |
| `package.json` | Skill metadata |
| `scripts/` | Shell script wrappers |
| `scripts/utils/` | Python utility modules |
| `scripts/tests/` | Unit tests |
| `references/` | Reference documentation |

## Testing

Tests use Python's built-in `unittest` module (no pip install required).

```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test file
python3 -m pytest scripts/tests/test_date_parser.py

# Run with verbose output
python3 -m unittest discover -v scripts/tests/
```

## Code Style

- Shell scripts are thin wrappers that delegate to Python utilities
- Python utilities are in `scripts/utils/`
- Keep SKILL.md concise - move detailed docs to `references/`
