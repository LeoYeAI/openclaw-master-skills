# Publishing Guide

This document explains how to publish new versions of this skill to Clawhub.

## Automated Publishing (Recommended)

The repository includes a GitHub Actions workflow that automatically publishes to Clawhub when you create a new release.

### Quick Release

```bash
# 1. Update version
npm version patch  # or minor, major

# 2. Push with tags
git push --follow-tags

# 3. Create GitHub release
gh release create v$(node -p "require('./package.json').version") \
  --title "Release v$(node -p "require('./package.json').version")" \
  --generate-notes
```

The GitHub Action (`.github/workflows/publish.yml`) will automatically:
- ✅ Validate package.json and openclaw configuration
- ✅ Run tests
- ✅ Publish to npm (if `NPM_TOKEN` secret is configured)
- ✅ Notify Clawhub (if webhook configured)

### Setup GitHub Secrets

Configure these secrets in your repository settings (`Settings` > `Secrets and variables` > `Actions`):

#### Option 1: npm Publishing (if Clawhub syncs from npm)

```
NPM_TOKEN=npm_xxxxxxxxxxxx
```

To get an npm token:
1. Create account at https://npmjs.com
2. Go to Account > Access Tokens
3. Generate new "Automation" token
4. Add to GitHub secrets

#### Option 2: Clawhub Direct Publishing (Optional)

**Required secret:**
```
CLAWHUB_TOKEN=clawhub_xxxxxxxxxxxx
```

The workflow will attempt to:
1. Install Clawhub CLI (`npm install -g clawhub`)
2. Login using your CLAWHUB_TOKEN
3. Publish your skill using `npx clawhub publish .`

**Note**: If CLI publish fails, the workflow gracefully handles the failure and relies on GitHub auto-sync instead.

**You only need CLAWHUB_TOKEN** for the CLI attempt, but GitHub auto-sync works without it!

## Manual Publishing

### Method 1: Using npm

If Clawhub syncs from npm registry:

```bash
# Login to npm
npm login

# Publish
npm publish --access public
```

### Method 2: Using Clawhub CLI

The Clawhub CLI can be used to publish:

```bash
# Install Clawhub CLI
npm install -g clawhub

# Login with your token
echo "YOUR_CLAWHUB_TOKEN" | npx clawhub login --token
# or interactive login
npx clawhub login

# Publish your skill (from the skill directory)
npx clawhub publish .
```

**Note**: If the CLI publish fails, use Method 3 (GitHub integration) instead - it's more reliable!

### Method 3: GitHub Integration (Recommended)

Clawhub auto-syncs from GitHub releases - this is the most reliable method:

1. Ensure your repository is connected to Clawhub (one-time setup)
2. Create a GitHub release with proper version tag
3. Clawhub automatically detects and syncs your skill

**This is the recommended approach** as it avoids CLI bugs and works reliably!

## Version Management

### Semantic Versioning

Follow [semver](https://semver.org/) principles:

- **Patch** (1.0.0 → 1.0.1): Bug fixes, documentation updates
  ```bash
  npm version patch
  ```

- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
  ```bash
  npm version minor
  ```

- **Major** (1.0.0 → 2.0.0): Breaking changes
  ```bash
  npm version major
  ```

### Pre-release Versions

For testing before official release:

```bash
# Create alpha version
npm version prerelease --preid=alpha
# 1.0.0 → 1.0.1-alpha.0

# Create beta version
npm version prerelease --preid=beta
# 1.0.1-alpha.0 → 1.0.1-beta.0
```

## Pre-publish Checklist

Before publishing a new version:

- [ ] All tests pass: `npm test`
- [ ] Documentation is updated:
  - [ ] README.md
  - [ ] SKILL.md
  - [ ] CLAUDE.md
  - [ ] CHANGELOG.md (if you maintain one)
- [ ] Version number is appropriate (patch/minor/major)
- [ ] `package.json` metadata is correct:
  - [ ] Repository URLs
  - [ ] Author information
  - [ ] Keywords
  - [ ] openclaw configuration
- [ ] Examples are working
- [ ] Scripts are tested:
  - [ ] `./scripts/setup.sh`
  - [ ] `./scripts/validate-intent.sh`
  - [ ] `./scripts/report.sh`

## Verifying Publication

After publishing, verify:

1. **Clawhub Page**: Visit https://clawhub.ai/nishantapatil3/self-improving-intent-security-agent
   - [ ] New version appears
   - [ ] GitHub link is visible
   - [ ] Documentation link works

2. **Installation**: Test the skill can be installed
   ```bash
   npx skills add nishantapatil3/self-improving-intent-security-agent
   ```

3. **GitHub Release**: Check https://github.com/nishantapatil3/self-improving-intent-security-agent/releases
   - [ ] Release notes are clear
   - [ ] Tags match version

## Troubleshooting

### GitHub Action Fails

Check the workflow run at:
https://github.com/nishantapatil3/self-improving-intent-security-agent/actions

Common issues:
- Missing secrets (NPM_TOKEN, CLAWHUB_TOKEN)
- Invalid package.json
- Failed tests
- Permission issues

### Clawhub Not Syncing

If Clawhub doesn't show new version:

1. **Check sync delay**: May take a few minutes to hours
2. **Verify package.json**: Ensure repository URL is correct
3. **Check GitHub release**: Must be a proper release, not just a tag
4. **Contact Clawhub support**: They may need to manually trigger sync

### npm Publish Errors

```bash
# Check if package name is available
npm view self-improving-intent-security-agent

# Check if you're logged in
npm whoami

# Verify package.json
npm pack --dry-run
```

## Rollback

If you need to unpublish or rollback:

### npm
```bash
# Deprecate a version (recommended over unpublish)
npm deprecate self-improving-intent-security-agent@1.0.1 "Version deprecated, use 1.0.2"

# Unpublish (only within 72 hours)
npm unpublish self-improving-intent-security-agent@1.0.1
```

### Clawhub
Check Clawhub documentation for version management and deprecation.

## Automation Tips

### Automatic Version Bumping

Add to `.github/workflows/publish.yml` to auto-increment versions:

```yaml
- name: Bump version
  run: npm version patch --no-git-tag-version
```

### Release Drafter

Use [Release Drafter](https://github.com/release-drafter/release-drafter) to automatically generate release notes from PRs.

### Conventional Commits

Use [conventional commits](https://www.conventionalcommits.org/) to automatically determine version bumps:

```bash
# Install
npm install -g standard-version

# Create release
standard-version

# Push
git push --follow-tags
```

## Support

For publishing issues:
- **GitHub Issues**: https://github.com/nishantapatil3/self-improving-intent-security-agent/issues
- **npm Support**: https://npmjs.com/support
- **Clawhub Support**: Check Clawhub documentation/contact

---

**Next Steps**: Set up your `NPM_TOKEN` or `CLAWHUB_TOKEN` secret in GitHub to enable automated publishing!
