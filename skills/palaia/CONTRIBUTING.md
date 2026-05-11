# Contributing to Palaia

Thanks for your interest in contributing to Palaia!

## Reporting Bugs

Open a [GitHub Issue](https://github.com/iret77/palaia/issues) using the bug report template. Include:

- Python version (`python --version`)
- Palaia version (`palaia --version`)
- Steps to reproduce
- Expected vs actual behavior

## Submitting Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`: `git checkout -b feat/my-feature`
3. **Write tests** for new functionality
4. **Run the test suite**: `pytest tests/ -v`
5. **Lint your code**: `ruff check palaia/ tests/`
6. **Commit** with a clear message (e.g., `feat: add memory compression`)
7. **Open a PR** against `main`

### PR Requirements

- All tests must pass
- New features need tests
- No force pushes to `main`
- Follow existing code style

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting. Configuration is in `pyproject.toml`.

```bash
# Check
ruff check palaia/ tests/

# Auto-fix
ruff check --fix palaia/ tests/
```

## Architecture Decisions

Significant changes should be proposed as an ADR (Architecture Decision Record) in `docs/adr/`. See existing ADRs for the format.

## Development Setup

```bash
git clone https://github.com/iret77/palaia.git
cd palaia
pip install -e ".[dev]"
pytest tests/ -v
```

## Zero Dependencies Policy

Palaia's core runs on Python stdlib only. Think twice before adding a dependency. If you need one, discuss it in an issue first.
