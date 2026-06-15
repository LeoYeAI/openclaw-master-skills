# Security Model

## Architecture: Local-First, User-Scoped

ContextUI is a **local desktop application**. All tools in this skill execute on the user's machine, under the user's OS permissions. There is no remote code execution, no cloud relay, and no network-accessible API surface exposed to the internet.

This is architecturally equivalent to an IDE (VS Code, IntelliJ) or terminal emulator — it provides development tools that operate within the user's existing permission boundary.

## Honest Capability Scope

This skill grants an agent broad local development capabilities. Here's exactly what it can and cannot do:

### What the agent CAN do
- **Read/write workflow files** — React TSX source files within the ContextUI workflows directory, using absolute paths
- **Start Python servers** — from existing local scripts via `python_start_server`. Servers bind to `127.0.0.1` (localhost)
- **Create virtual environments and install pip packages** — the ServerLauncher pattern creates venvs and installs packages from PyPI. This involves network downloads
- **Read local directories** — including `~/.cache/huggingface` for model cache monitoring in ML workflows (documented in `references/cache-monitoring.md`)
- **UI automation** — click, type, screenshot within ContextUI's Electron webview (scoped to the app window, not the broader OS)
- **Exchange operations** — upload/download workflows via the ContextUI Exchange (requires optional `CONTEXTUI_API_KEY`)
- **Connect MCP servers** — stdio or HTTP, persisted in config and visible in the ContextUI UI

### What the agent CANNOT do
- **Access other OS applications** — UI automation is scoped to ContextUI's Electron window
- **Gain elevated privileges** — no sudo, no admin. Everything runs as the current OS user
- **Bypass OS permissions** — filesystem access is limited to what the user account can already reach
- **Act invisibly** — MCP connections, running servers, and open workflows are all visible in the ContextUI UI

## Runtime Network Access

This skill is local-first but **not offline-only**. Network I/O occurs for:
- **pip package installs** — downloads from PyPI when creating/updating venvs
- **Model downloads** — HuggingFace model files if a workflow requires them
- **Exchange operations** — uploading/downloading marketplace workflows (requires API key)

These are standard operations for any ML/AI development environment.

## Credentials

| Variable | Required | Scope | Purpose |
|----------|----------|-------|---------|
| `CONTEXTUI_API_KEY` | No | Exchange only | Publishing and downloading marketplace workflows |

No other credentials are required. The skill operates on local filesystem paths and localhost servers.

## Trust Model

This skill assumes the **agent is trusted by the user** to perform development tasks on their machine — the same trust model as giving an agent access to a terminal, IDE, or code editor. The user installs ContextUI locally and explicitly configures the MCP connection to grant their agent access.

### Recommendations for untrusted environments
- Run ContextUI in an isolated environment (VM, container, dedicated user account)
- Only provide `CONTEXTUI_API_KEY` if Exchange features are needed
- Review `scripts/exchange.sh` for upload sanitization logic
- Monitor venv creation and package installs if running untrusted workflows

## No Elevated Privileges

No tool in this skill requires or requests elevated permissions (sudo, admin). All operations run as the current OS user with no privilege escalation.
