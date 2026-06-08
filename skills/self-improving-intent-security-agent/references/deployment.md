# Deployment Guide

How to publish and deploy the self-improving-intent-security-agent skill to clawhub.

## Prerequisites

- Node.js >= 18.0.0
- clawhub CLI installed
- GitHub account (>= 1 week old)
- Repository set up on GitHub

## Installation

### Install clawhub CLI

```bash
# npm
npm install -g clawhub

# pnpm
pnpm add -g clawhub

# yarn
yarn global add clawhub
```

### Verify Installation

```bash
clawhub --version
```

## Prepare for Publishing

### 1. Review File Structure

Ensure you have the required structure:

```
self-improving-intent-security-agent/
├── SKILL.md                    # Required
├── README.md                   # Recommended
├── package.json                # Recommended
├── assets/                     # Templates
├── examples/                   # Usage examples
├── hooks/                      # Optional (user-created)
├── references/                 # Documentation
└── scripts/                    # Helper utilities
```

### 2. Validate SKILL.md

Ensure SKILL.md has proper frontmatter:

```yaml
---
name: self-improving-intent-security-agent
description: "Autonomous agent that learns from experience while maintaining strict intent alignment and security boundaries"
---
```

### 3. Update Version

Edit `package.json`:

```json
{
  "version": "1.0.0"
}
```

Follow semantic versioning:
- `1.0.0` - Initial release
- `1.1.0` - New features (backward compatible)
- `1.0.1` - Bug fixes
- `2.0.0` - Breaking changes

### 4. Test Locally

```bash
# Run setup script
./scripts/setup.sh

# Validate intent templates
./scripts/validate-intent.sh assets/INTENT-TEMPLATE.md

# Generate test report
./scripts/report.sh .agent
```

### 5. Create Git Tag

```bash
# Commit all changes
git add .
git commit -m "Prepare v1.0.0 release"

# Create version tag
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

## Publishing to Clawhub

### 1. Authenticate

```bash
# Browser-based login
clawhub login

# Or token-based (CI/CD)
export CLAWHUB_TOKEN="your-token"
clawhub login --token $CLAWHUB_TOKEN
```

### 2. Validate Skill

```bash
# Check if skill structure is valid
clawhub validate

# Dry run (see what would be published)
clawhub publish --dry-run
```

### 3. Publish

```bash
# Publish skill
clawhub publish \
  --slug self-improving-intent-security-agent \
  --name "Self-Improving Intent Security Agent" \
  --version 1.0.0 \
  --changelog "Initial release with intent validation, security monitoring, and self-improvement" \
  --tags latest,stable
```

**Parameters**:
- `--slug`: Unique identifier (must match package name)
- `--name`: Display name
- `--version`: Semver version
- `--changelog`: Description of changes
- `--tags`: Comma-separated tags (e.g., `latest`, `stable`, `beta`)

### 4. Verify Publication

```bash
# Check skill info
clawhub info self-improving-intent-security-agent

# Search for your skill
clawhub search "intent security"
```

## User Installation

After publishing, users can install your skill:

```bash
# Install via clawhub
clawhub install self-improving-intent-security-agent

# Or via npm/npx
npx skills add nishantapatil3/self-improving-intent-security-agent
```

## Updating Published Skill

### Patch Release (Bug Fixes)

```bash
# Update version
npm version patch  # 1.0.0 → 1.0.1

# Publish
clawhub publish \
  --version 1.0.1 \
  --changelog "Fix: Corrected validation logic for constraints" \
  --bump patch
```

### Minor Release (New Features)

```bash
# Update version
npm version minor  # 1.0.1 → 1.1.0

# Publish
clawhub publish \
  --version 1.1.0 \
  --changelog "Added: Transfer learning across domains" \
  --bump minor
```

### Major Release (Breaking Changes)

```bash
# Update version
npm version major  # 1.1.0 → 2.0.0

# Publish
clawhub publish \
  --version 2.0.0 \
  --changelog "Breaking: New intent specification format, requires migration" \
  --bump major
```

## Sync Multiple Skills

If you maintain multiple skills:

```bash
# Auto-detect and publish all skills
clawhub sync --all

# Dry run to see what would be published
clawhub sync --all --dry-run

# Auto-bump versions
clawhub sync --all --bump patch

# With changelog
clawhub sync --all --changelog "Maintenance update" --bump minor
```

## Environment Configuration

### Clawhub Environment Variables

```bash
# Site URL (default: https://clawhub.ai)
export CLAWHUB_SITE=https://clawhub.ai

# API URL (default: https://api.clawhub.ai)
export CLAWHUB_REGISTRY=https://api.clawhub.ai

# Config path (default: ~/.clawhub/config)
export CLAWHUB_CONFIG_PATH=~/.clawhub/config

# Working directory (default: current directory)
export CLAWHUB_WORKDIR=./my-workspace

# Disable telemetry
export CLAWHUB_DISABLE_TELEMETRY=1
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to Clawhub

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install clawhub CLI
        run: npm install -g clawhub

      - name: Authenticate
        env:
          CLAWHUB_TOKEN: ${{ secrets.CLAWHUB_TOKEN }}
        run: clawhub login --token $CLAWHUB_TOKEN

      - name: Publish skill
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          clawhub publish \
            --version $VERSION \
            --changelog "Release $VERSION" \
            --tags latest
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
publish:
  stage: deploy
  only:
    - tags
  script:
    - npm install -g clawhub
    - clawhub login --token $CLAWHUB_TOKEN
    - clawhub publish --version $CI_COMMIT_TAG --changelog "Release $CI_COMMIT_TAG"
  variables:
    CLAWHUB_TOKEN: $CLAWHUB_TOKEN
```

## Rollback

If a published version has issues:

```bash
# Tag previous version as latest
clawhub tag self-improving-intent-security-agent@1.0.1 latest

# Or unpublish problematic version (use with caution)
clawhub unpublish self-improving-intent-security-agent@1.0.2
```

## Distribution Channels

### GitHub Releases

Create releases on GitHub for visibility:

```bash
# Using GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "First stable release with intent security and self-improvement"
```

### npm Registry (Optional)

Publish to npm for broader reach:

```bash
# Login to npm
npm login

# Publish
npm publish
```

### Direct Installation from Git

Users can install directly from your repository:

```bash
npx skills add nishantapatil3/self-improving-intent-security-agent#main
```

## Monitoring

### Track Usage

Clawhub provides usage metrics:

```bash
# View skill statistics
clawhub stats self-improving-intent-security-agent

# Download metrics
clawhub stats self-improving-intent-security-agent --json > metrics.json
```

### User Feedback

Monitor for issues and feedback:

- GitHub Issues: Track bugs and feature requests
- Clawhub Reviews: Check user ratings and comments
- GitHub Discussions: Community Q&A

## Maintenance

### Regular Updates

Schedule regular maintenance:

- **Monthly**: Review issues, update dependencies
- **Quarterly**: Major feature releases
- **As Needed**: Security patches, critical bugs

### Deprecation

If you need to deprecate:

1. Mark as deprecated in SKILL.md
2. Provide migration guide
3. Maintain for 6 months minimum
4. Redirect to replacement skill

## Troubleshooting

### Common Issues

**Issue**: Authentication failed
```bash
# Clear token and re-authenticate
rm ~/.clawhub/config
clawhub login
```

**Issue**: Skill validation failed
```bash
# Check SKILL.md format
clawhub validate --verbose

# Ensure name matches directory name
```

**Issue**: Version already exists
```bash
# Bump version
npm version patch

# Or force overwrite (not recommended)
clawhub publish --force
```

### Getting Help

- Clawhub Docs: https://clawhub.ai/docs
- GitHub Issues: Your repository issues
- Clawhub Community: https://clawhub.ai/community

## Security Considerations

### Secrets Management

Never commit:
- API tokens (`CLAWHUB_TOKEN`)
- Private keys
- Credentials

Use environment variables or secrets management:

```bash
# GitHub Secrets
# Settings → Secrets → Actions → New repository secret

# GitLab CI/CD Variables
# Settings → CI/CD → Variables
```

### Verification

Clawhub automatically:
- Scans for secrets in published code
- Validates skill structure
- Checks for malicious patterns
- Requires account age (1+ week)

## Best Practices

1. **Semantic Versioning**: Follow semver strictly
2. **Changelog**: Always include meaningful changelogs
3. **Testing**: Test locally before publishing
4. **Documentation**: Keep README and examples up-to-date
5. **Tags**: Use appropriate tags (latest, stable, beta)
6. **Licensing**: Include clear license (MIT recommended)
7. **Security**: Never publish secrets or credentials
8. **Support**: Respond to issues and discussions promptly

## Checklist

Before publishing:

- [ ] SKILL.md has valid frontmatter
- [ ] README.md is clear and complete
- [ ] package.json version is correct
- [ ] Examples are tested and working
- [ ] Scripts are executable (`chmod +x`)
- [ ] No secrets or credentials in code
- [ ] Git tag matches version
- [ ] Changelog is meaningful
- [ ] Local validation passes
- [ ] GitHub repository is public (if applicable)

---

You're now ready to publish your intent security agent skill to clawhub! 🚀
