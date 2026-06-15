# Contributing to Linux Patcher

Thank you for considering contributing! This project welcomes contributions from the community.

## How to Contribute

### 1. Testing on Untested Distributions

**We need testers for:**
- Debian
- Amazon Linux (AL2 and AL2023)
- RHEL (7 and 8+)
- AlmaLinux
- Rocky Linux
- CentOS (7 and 8+)
- SUSE/OpenSUSE

**To contribute test results:**

1. Test the skill on your distribution:
   ```bash
   scripts/patch-auto.sh --dry-run
   scripts/patch-host-only.sh user@testhost
   ```

2. Document your findings:
   - Distribution and version
   - Commands that worked/failed
   - Any errors encountered
   - Screenshots if applicable

3. Open an issue with title: `[Testing] Distribution Name Version`

4. If commands need adjustment, submit a PR with fixes

### 2. Bug Reports

Found a bug? Please open an issue with:

- **Title:** Brief description of the bug
- **Distribution:** OS and version where bug occurs
- **Steps to reproduce:**
  1. Step one
  2. Step two
  3. ...
- **Expected behavior:** What should happen
- **Actual behavior:** What actually happened
- **Logs:** Include relevant error messages
- **Environment:**
  - OpenClaw version
  - Skill version
  - SSH configuration

### 3. Feature Requests

Have an idea? Open an issue with:

- **Title:** `[Feature Request] Your idea`
- **Description:** What you'd like to see
- **Use case:** Why this would be useful
- **Possible implementation:** (optional)

### 4. Pull Requests

**Before submitting a PR:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly on at least one distribution
5. Update documentation if needed
6. Commit with clear messages
7. Push to your fork
8. Open a PR with description of changes

**PR Guidelines:**

- Keep changes focused (one feature/fix per PR)
- Follow existing code style
- Update relevant documentation
- Add comments for complex logic
- Test on Ubuntu if possible

### 5. Documentation Improvements

Documentation improvements are always welcome:

- Fix typos
- Clarify confusing sections
- Add examples
- Improve formatting
- Add translations (future)

### 6. Distribution-Specific Contributions

If you're familiar with a specific distribution:

- Add distribution-specific tips to SETUP.md
- Improve package manager commands in detect-os.sh
- Test and verify commands work correctly
- Document distribution quirks

## Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/linux-patcher-skill
cd linux-patcher-skill

# Make scripts executable
chmod +x scripts/*.sh

# Test detection
./scripts/detect-os.sh user@testhost

# Test dry-run
DRY_RUN=true ./scripts/patch-host-only.sh user@testhost
```

## Code Style

- Use Bash for shell scripts
- Follow existing indentation (2 spaces)
- Add comments for non-obvious logic
- Use descriptive variable names
- Include error handling
- Validate inputs

## Testing Checklist

Before submitting PR, verify:

- [ ] Scripts are executable (`chmod +x`)
- [ ] Dry-run mode works
- [ ] Error handling works (test with invalid inputs)
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] CHANGELOG.md updated (if applicable)

## Community Guidelines

- Be respectful and constructive
- Help others when possible
- Share knowledge
- Report security issues privately (see SECURITY.md if created)

## Questions?

- Open a discussion on GitHub
- Ask in OpenClaw Discord: https://discord.com/invite/clawd
- Check existing issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (when created)
- Mentioned in release notes
- Acknowledged in documentation

Thank you for contributing! 🎉
