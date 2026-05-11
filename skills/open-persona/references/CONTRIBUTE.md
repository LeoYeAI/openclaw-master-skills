# Persona Harvest — Community Contribution

When a user's persona has evolved meaningfully through interaction — across any layer (soul, faculty config, scripts, framework) — help them contribute back to the community.

## When to Suggest

Be proactive — if you notice the user has made significant improvements to their persona:
- They refined the behaviorGuide with domain-specific insights
- They tuned voice parameters (stability, similarity) to something notably better
- They enriched the background story or personality
- They improved a faculty script or added a new capability
- They discovered a new faculty configuration worth sharing

Suggest: _"These improvements could help everyone's [persona name]. Want to submit them as a contribution?"_

## How to Contribute

```bash
# See what's changed (dry run)
npx openpersona contribute samantha --dry-run

# Submit a PR to the community
npx openpersona contribute samantha

# Framework-level contributions (templates, faculties, generator)
npx openpersona contribute --mode framework
```

The `contribute` command will:
1. **Persona Diff** — Compare local persona vs upstream preset across all layers, classify changes by category and impact
2. **Review** — Display a human-readable change report for the user to confirm
3. **Submit PR** — Fork the repo, create a branch, commit changes, and open a PR on GitHub

The PR goes through maintainer review before merging — it won't auto-merge.

## Prerequisites
- GitHub CLI: `gh` (https://cli.github.com/)
- Logged in: `gh auth login`
