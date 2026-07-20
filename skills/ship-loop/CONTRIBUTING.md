# Contributing to Ship Loop

Thanks for your interest in Ship Loop! Here's how to get involved.

## Quick Setup

```bash
git clone https://github.com/fernando-fernandez3/ship-loop.git
cd ship-loop
pip install -e ".[dev]"
python -m pytest tests/ -x
```

## Development

Ship Loop is a Python CLI. The main code lives in `shiploop/`:

```
shiploop/
├── cli.py              # CLI entry point (argparse)
├── config.py           # SHIPLOOP.yml parsing (Pydantic v2)
├── orchestrator.py     # State machine + DAG scheduler
├── agent.py            # Agent runner with timeout enforcement
├── loops/
│   ├── ship.py         # Loop 1: code → preflight → ship → verify
│   ├── repair.py       # Loop 2: auto-repair on failure
│   ├── meta.py         # Loop 3: meta-analysis + experiments
│   └── optimize.py     # Post-ship optimization
├── preflight.py        # Build/lint/test runner
├── git_ops.py          # Git operations + security scan
├── deploy.py           # Deploy verification plugin loader
├── budget.py           # Token/cost tracking
├── learnings.py        # Failure → lesson engine
├── reporting.py        # Status output + reports
└── providers/
    ├── base.py         # Abstract DeployVerifier
    ├── vercel.py       # Vercel verification
    ├── netlify.py      # Netlify verification
    └── custom.py       # Custom script provider
```

## Running Tests

```bash
python -m pytest tests/ -x          # Stop on first failure
python -m pytest tests/ -v          # Verbose output
python -m pytest tests/ -k "budget" # Run specific tests
```

All 125 tests should pass. If they don't, something's broken and that's worth a bug report.

## Submitting Changes

1. Fork the repo
2. Create a branch: `git checkout -b my-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/ -x`
5. Commit with a clear message
6. Open a PR against `main`

## What We're Looking For

Check [open issues](https://github.com/fernando-fernandez3/ship-loop/issues) for things to work on. Some areas where contributions are especially welcome:

- **New deploy providers** (AWS Amplify, Cloudflare Pages, Railway, Fly.io). Subclass `DeployVerifier` in `shiploop/providers/`.
- **New agent presets** in `config.py` (`AGENT_PRESETS` dict).
- **Framework detection** in `cli.py` (`_detect_framework` and `_default_preflight`).
- **Better error messages** when things fail.
- **Documentation** improvements.

## Adding a Deploy Provider

1. Create `shiploop/providers/your_provider.py`
2. Subclass `DeployVerifier` from `shiploop/providers/base.py`
3. Implement the `verify()` method
4. Register it in `shiploop/deploy.py`
5. Add tests in `tests/`

## Code Style

- Python 3.10+ (use `|` union syntax, not `Union`)
- Type hints everywhere
- Pydantic v2 for data models
- `asyncio` for I/O operations
- No external dependencies beyond `pyyaml` and `pydantic` (keep it light)

## Reporting Bugs

Open an issue with:
- What you expected
- What happened
- Your `shiploop --version`
- Your `SHIPLOOP.yml` (redact any secrets)
- The full error output

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
