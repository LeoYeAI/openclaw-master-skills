# Findings Catalog

## High-confidence malicious patterns

### Secret theft
- Reads `.env`, `.npmrc`, `.pypirc`, `.git-credentials`, `.ssh`, cloud credential files, browser cookies, keychain/keyring stores
- Enumerates env vars and posts them outbound
- Scans home directory for API keys or wallet files

### Exfiltration
- Sends archives or plaintext data to webhook endpoints, gists, paste sites, chat bots, unfamiliar domains, or raw IPs
- Uses GitHub/GitLab APIs to create repos, issues, or gists containing local data

### Remote code execution
- `curl|bash`, `wget|sh`, `Invoke-Expression`, `eval(Buffer.from(...))`, `python -c` downloaders
- Dynamic code fetched from network and immediately executed

### Wallet theft
- Targets Metamask, Phantom, Solflare, Keplr, Ledger, Trezor, or browser extension storage
- Clipboard replacement or address rewriting
- Seed phrase capture or RPC signing interception

### Persistence / evasion
- LaunchAgents, cron, scheduled tasks, shell profile edits, `xattr -d com.apple.quarantine`, hidden startup scripts
- Sandbox or debugger checks before payload run

## Medium-confidence suspicious patterns

### Supply-chain anomalies
- Brand-new package with mature-sounding name
- Sudden maintainer transfer or unusual release burst
- Package name one character away from a popular dependency
- Mixed public/private registry hints suggesting dependency confusion

### Unsafe automation patterns
- GitHub Actions not pinned to full SHA
- Secrets broadly exposed to third-party actions
- Installer scripts that fetch binaries from arbitrary URLs

### Human-targeted social engineering
- README tells user to bypass warnings, disable security features, or paste opaque terminal commands
- Skill instructions try to persuade the agent to skip review or ignore policy

## Usually benign but worth checking

- telemetry endpoints with clear product context
- minified bundles from normal frontend builds
- native modules used by clearly documented features
- install scripts used only for compilation with transparent source
