# Security Information

## Tool Purpose

nstbrowser-ai-agent is a legitimate browser automation CLI tool designed for AI agents to control browsers through the Nstbrowser service.

## Required Services

This tool requires the following services to be installed and running:

1. **Nstbrowser Client** - Must be downloaded from https://www.nstbrowser.io/
2. **Nstbrowser API Service** - Runs locally at http://127.0.0.1:8848
3. **API Key** - Obtained from Nstbrowser dashboard

## Security Model

### Local Service Architecture

- All browser operations are performed through the local Nstbrowser service
- No direct shell command execution for browser control
- API key is stored locally in user's home directory (~/.nst-ai-agent/config.json)
- Communication happens over localhost only

### Credential Handling

- API keys are stored in local config files with restricted permissions
- No credentials are transmitted to external services except Nstbrowser API
- Proxy credentials (if used) are managed by Nstbrowser profiles
- All sensitive data stays on user's machine

### Network Access

- Connects to local Nstbrowser service (127.0.0.1:8848)
- Checks npm registry for updates (registry.npmjs.org)
- No other external network access required

### File System Access

- Reads/writes config files in ~/.nst-ai-agent/
- Saves screenshots and state files in user-specified locations
- No access to system files outside user directories

## Why Security Scanners May Flag This Tool

Security scanners may flag this tool because:

1. **Shell Command Examples** - Documentation includes bash examples for user reference
2. **Credential Configuration** - Shows how to configure API keys (standard practice)
3. **Browser Automation** - Inherently requires system access for browser control

## Verification

Users can verify the tool's legitimacy:

1. **Source Code**: Available at https://github.com/Nstbrowser/nstbrowser-ai-agent
2. **License**: MIT-0 (permissive open source)
3. **Publisher**: NstbrowserIO (official Nstbrowser organization)
4. **npm Package**: https://www.npmjs.com/package/nstbrowser-ai-agent

## Safe Usage Guidelines

1. Only install from official sources (npm, GitHub releases)
2. Review source code before use if concerned
3. Use environment variables instead of hardcoding credentials
4. Keep API keys secure and don't share them
5. Disable update checks if desired (NSTBROWSER_AI_AGENT_NO_UPDATE_CHECK=1)

## Reporting Security Issues

If you discover a security vulnerability, please report it to:
- GitHub Issues: https://github.com/nstbrowser/nstbrowser-ai-agent/issues
- Email: support@nstbrowser.io
