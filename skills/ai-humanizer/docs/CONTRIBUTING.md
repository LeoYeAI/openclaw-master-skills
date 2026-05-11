# Contributing to humanizer

Thanks for your interest in improving AI writing detection.

## Getting started

```bash
git clone https://github.com/brandonwise/humanizer.git
cd humanizer
npm install
npm test
```

## What to work on

- **New patterns** — Found an AI writing pattern not covered? Add it
- **Better detection** — Improve regex accuracy, reduce false positives
- **More vocabulary** — Expand the AI word/phrase lists
- **Test cases** — Add fixtures that expose detection gaps
- **Documentation** — Improve examples, add before/after pairs

## Adding a new pattern

1. Add the pattern definition to `src/patterns.js` (see `docs/PATTERNS.md` for the format)
2. Write tests in `tests/analyzer.test.js`
3. Add documentation to `references/patterns.md`
4. Run `npm test` — everything must pass

## Improving detection

The main source of false positives is overly broad regex. When tightening patterns:

- Add word boundary markers (`\b`)
- Use context-aware matching (surrounding words matter)
- Test against both AI samples and human samples
- Check that human text doesn't get flagged unfairly

## Code style

- Pure Node.js, no external runtime dependencies
- CommonJS modules (`require`/`module.exports`)
- No build step — the code runs directly
- Comments explain *why*, not *what*
- Functions are small and single-purpose

## Tests

- All tests use vitest
- Run with `npm test`
- Test each pattern detector individually
- Include both positive matches (should detect) and negative cases (should not detect)
- Test fixtures go in `tests/fixtures/`

## Pull request process

1. Fork the repo and create a branch (`git checkout -b add-pattern-25`)
2. Make your changes
3. Run `npm test` — all tests must pass
4. Open a PR with a clear description of what changed and why
5. Include before/after examples for any new patterns

## Reporting issues

Found a false positive? A missed pattern? Open an issue with:

- The text that was incorrectly flagged (or missed)
- Which pattern is involved
- What you expected to happen
- What actually happened
