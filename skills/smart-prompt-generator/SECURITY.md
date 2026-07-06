# Security Policy

## Supported Versions

We actively support the following versions of the AI Prompt Generator skill with security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.0.x   | :white_check_mark: | Active |
| < 1.0   | :x:                | Not supported |

## Reporting a Vulnerability

We take the security of AI Prompt Generator seriously. If you have discovered a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them using one of these methods:

1. **Email (Preferred)**: Send details to security@openclaw.ai
   - Subject line: "Security Vulnerability in prompt-generator"
   - Include detailed description
   - Steps to reproduce (if applicable)
   - Potential impact

2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature
   - Go to https://github.com/openclaw/skill-prompt-generator/security/advisories
   - Click "Report a vulnerability"

### What to Include

Please include the following information:

- **Type of issue**: e.g., data exposure, malicious prompt injection, etc.
- **Affected component**: Which part of the skill is affected
- **Reproduction steps**: How can we reproduce the issue?
- **Impact**: What's the potential impact?
- **Suggested fix**: If you have ideas for fixing it

### Response Timeline

- **Initial Response**: Within 24 hours
- **Vulnerability Confirmation**: Within 48 hours
- **Fix Development**: Depends on severity (1-7 days)
- **Security Advisory**: Published with the fix

### Disclosure Policy

- We follow **responsible disclosure**
- We'll work with you to understand and fix the issue
- We'll publish a security advisory after the fix is released
- We'll credit you in the advisory (unless you prefer to remain anonymous)

## Security Considerations

### Prompt Injection

While this skill generates prompts for AI tools, please be aware:

- ✅ **We sanitize templates** to prevent malicious content
- ✅ **We validate user inputs** before generating prompts
- ✅ **We review templates** before merging contributions
- ⚠️ **Users should review** generated prompts before using them with AI tools

### Data Privacy

- ❌ **No data collection**: This skill doesn't send data to external servers
- ❌ **No tracking**: We don't track how you use generated prompts
- ✅ **Local processing**: All prompt generation happens locally
- ✅ **Your prompts are yours**: Generated prompts are not stored or shared

### Safe Usage

To use this skill safely:

1. **Review Generated Prompts**: Always review prompts before using them
2. **Don't Share Sensitive Data**: Don't include sensitive information in prompts
3. **Validate Templates**: If using community templates, review them first
4. **Report Issues**: If you find suspicious content, report it immediately

## Security Best Practices for Users

### When Generating Prompts

```markdown
✅ DO:
- Review generated prompts before use
- Use placeholders for sensitive data
- Validate templates from community
- Keep your OpenClaw installation updated

❌ DON'T:
- Include passwords or API keys in prompts
- Use untrusted templates without review
- Share prompts with sensitive information
- Ignore security warnings
```

### When Contributing Templates

```markdown
✅ DO:
- Follow our template guidelines
- Submit clear, safe templates
- Document potential risks
- Allow community review

❌ DON'T:
- Include malicious code
- Add obfuscated content
- Submit untested templates
- Bypass security reviews
```

## Known Security Issues

### Current (as of 2026-03-10)

No known security vulnerabilities in version 1.0.0.

### Past Issues

None yet.

## Security Features

### Template Validation

- **Static Analysis**: All templates are analyzed for suspicious content
- **Community Review**: Templates are reviewed before merging
- **Automated Checks**: CI/CD pipeline includes security scans
- **Version Control**: All changes are tracked in Git

### User Protection

- **Input Sanitization**: User inputs are validated and sanitized
- **Output Validation**: Generated prompts are checked for safety
- **Error Handling**: Secure error handling prevents information leakage
- **Access Control**: Skill respects OpenClaw's permission system

## Security Architecture

```
┌─────────────────────────────────────────┐
│         User Input (Validated)          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Template Engine (Sandboxed)          │
│  - Input sanitization                   │
│  - Template validation                  │
│  - Safe rendering                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      Generated Prompt (Checked)         │
│  - Output validation                    │
│  - Content filtering                    │
│  - Safe to use                          │
└─────────────────────────────────────────┘
```

## Security Updates

We'll announce security updates through:

- **GitHub Security Advisories**
- **Release Notes**
- **Discord Announcements** (critical issues only)
- **Email** (if you've opted in)

### Subscribe to Security Updates

- Watch the repository on GitHub
- Join our Discord server
- Check the Security tab regularly

## Third-Party Dependencies

This skill has minimal dependencies:

| Dependency | Purpose | Security Status |
|------------|---------|-----------------|
| OpenClaw | Runtime | Maintained by OpenClaw team |
| None other | - | N/A |

## Security Audits

- **Internal Review**: Ongoing by maintainers
- **Community Review**: Open source allows anyone to review code
- **External Audit**: Not yet (planned for future)

## Contact

For security concerns:

- **Security Email**: security@openclaw.ai
- **GitHub**: https://github.com/openclaw/skill-prompt-generator/security
- **Discord**: #security channel (for non-sensitive discussions)

## Credits

We thank all security researchers who responsibly disclose vulnerabilities.

### Hall of Thanks

*Your name could be here! Report vulnerabilities responsibly.*

---

**Last Updated**: 2026-03-10  
**Next Review**: 2026-06-10

For general questions (not security issues), please use:
- GitHub Issues: https://github.com/openclaw/skill-prompt-generator/issues
- Discord: https://discord.com/invite/clawd
- Email: community@openclaw.ai
