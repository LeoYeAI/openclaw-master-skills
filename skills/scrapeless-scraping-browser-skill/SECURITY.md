# Security Policy

## Supported Versions

We actively support the following versions of scraping-browser-skill:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in scraping-browser-skill, please report it responsibly:

### How to Report

1. **Email**: Send details to security@scrapeless.com
2. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Regular Updates**: Every 7 days until resolved
- **Resolution Timeline**: Critical issues within 30 days

### Security Best Practices

When using scraping-browser-skill:

1. **API Key Security**:
   - Store API keys securely using config files with restricted permissions (0600)
   - Never commit API keys to version control
   - Use environment variables only when necessary

2. **Network Security**:
   - All communications with Scrapeless API use HTTPS
   - Proxy configurations should use secure protocols when possible

3. **Data Handling**:
   - Screenshots and extracted data are handled locally
   - No sensitive data is transmitted to third parties except Scrapeless API
   - Session recordings (if enabled) are stored on Scrapeless servers

4. **Access Control**:
   - Configuration files are created with user-only permissions
   - Session management prevents unauthorized access to browser instances

### Scope

This security policy covers:
- The scraping-browser-skill CLI tool
- Integration with Scrapeless API
- Local configuration and data handling
- Session management and authentication

### Out of Scope

- Scrapeless cloud infrastructure (report to Scrapeless directly)
- Third-party dependencies (report to respective maintainers)
- User-generated content or scripts

## Security Features

- **Secure Configuration**: Config files created with 0600 permissions
- **API Authentication**: Header-based authentication with Scrapeless API
- **Session Isolation**: Each session is isolated and automatically expires
- **No Local Browser**: Eliminates local browser security risks
- **Encrypted Communication**: All API communication over HTTPS

## Responsible Disclosure

We appreciate security researchers who:
- Give us reasonable time to fix issues before public disclosure
- Avoid accessing or modifying user data
- Don't perform testing on production systems without permission
- Follow coordinated disclosure practices

Thank you for helping keep scraping-browser-skill secure!