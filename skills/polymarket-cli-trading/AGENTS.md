# AGENTS.md

## Repository

- **Source:** https://github.com/lacymorrow/openclaw-polymarket-trading-skill
- **ClawHub slug:** `polymarket-trading`
- **Current version:** See `_meta.json`

## Publishing to ClawHub

After making changes, publish the updated skill:

```bash
# Bump version in _meta.json first, then:
clawhub publish ~/clawd/skills/polymarket-trading \
  --slug polymarket-trading \
  --name "Polymarket Trading" \
  --version <NEW_VERSION> \
  --changelog "Description of changes"
```

## Pushing to GitHub

```bash
cd ~/clawd/skills/polymarket-trading
git add -A
git commit -m "describe changes"
git push origin main
```

## Workflow

1. Make changes to skill files
2. Bump version in `_meta.json`
3. Commit & push to GitHub
4. Publish to ClawHub with `clawhub publish`
