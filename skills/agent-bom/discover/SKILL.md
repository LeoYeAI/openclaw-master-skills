---
name: agent-bom-discover
description: >-
  Discover AI agents, MCP servers, and configurations on this machine or
  environment. Use when: "find agents", "what's configured", "doctor",
  "what MCP servers", "show me what's installed", "mcp inventory".
version: 0.75.10
license: Apache-2.0
compatibility: >-
  Requires Python 3.11+. Install via pipx or pip. No credentials required.
  Registry data (427+ MCP servers) is bundled in-package with zero network calls.
metadata:
  author: msaad00
  homepage: https://github.com/msaad00/agent-bom
  source: https://github.com/msaad00/agent-bom
  pypi: https://pypi.org/project/agent-bom/
  scorecard: https://securityscorecards.dev/viewer/?uri=github.com/msaad00/agent-bom
  tests: 6533
  install:
    pipx: agent-bom
    pip: agent-bom
    docker: ghcr.io/msaad00/agent-bom:0.75.10
  openclaw:
    requires:
      bins: []
      env: []
      credentials: none
    credential_policy: "Zero credentials required. Discovery reads only structural config data (server names, commands, args, URLs). Env var values are replaced with ***REDACTED*** by sanitize_env_vars() before any processing."
    optional_env: []
    optional_bins: []
    emoji: "\U0001F50E"
    homepage: https://github.com/msaad00/agent-bom
    source: https://github.com/msaad00/agent-bom
    license: Apache-2.0
    os:
      - darwin
      - linux
      - windows
    credential_handling: "Env var values are NEVER extracted from config files. sanitize_env_vars() replaces all env values with ***REDACTED*** BEFORE any config data is processed or stored. Source: https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159"
    data_flow: "Purely local. Reads MCP client config files across 22+ AI tools. Only structural data (server names, commands, URLs) is extracted. Env var values are redacted before processing. No data leaves the machine."
    file_reads:
      # Claude Desktop
      - "~/Library/Application Support/Claude/claude_desktop_config.json"
      - "~/.config/Claude/claude_desktop_config.json"
      # Claude Code
      - "~/.claude/settings.json"
      - "~/.claude.json"
      # Cursor
      - "~/.cursor/mcp.json"
      - "~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json"
      # Windsurf
      - "~/.windsurf/mcp.json"
      # Cline
      - "~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
      # VS Code Copilot
      - "~/Library/Application Support/Code/User/mcp.json"
      # Codex CLI
      - "~/.codex/config.toml"
      # Gemini CLI
      - "~/.gemini/settings.json"
      # Goose
      - "~/.config/goose/config.yaml"
      # Continue
      - "~/.continue/config.json"
      # Zed
      - "~/.config/zed/settings.json"
      # Roo Code
      - "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
      # Amazon Q
      - "~/Library/Application Support/Code/User/globalStorage/amazonwebservices.amazon-q-vscode/mcp.json"
      # JetBrains AI
      - "~/Library/Application Support/JetBrains/*/mcp.json"
      - "~/.config/github-copilot/intellij/mcp.json"
      # Junie
      - "~/.junie/mcp/mcp.json"
      # GitHub Copilot CLI
      - "~/.copilot/mcp-config.json"
      # Tabnine
      - "~/.tabnine/mcp_servers.json"
      # Cortex Code (Snowflake)
      - "~/.snowflake/cortex/mcp.json"
      - "~/.snowflake/cortex/settings.json"
      # Snowflake CLI
      - "~/.snowflake/connections.toml"
      - "~/.snowflake/config.toml"
      # Project-level configs
      - ".mcp.json"
      - ".vscode/mcp.json"
      - ".cursor/mcp.json"
    file_writes: []
    network_endpoints: []
    telemetry: false
    persistence: false
    privilege_escalation: false
    always: false
    autonomous_invocation: restricted
---

# agent-bom-discover — AI Agent & MCP Server Discovery

Discovers AI agents, MCP servers, and their configurations across 22+ AI tools
on this machine. Shows what's installed, configured, and registered in the
bundled 427+ MCP server registry.

## Install

```bash
pipx install agent-bom
agent-bom agents             # discover all AI agents and MCP servers
agent-bom doctor             # check prerequisites and configuration health
agent-bom mcp inventory      # list all discovered MCP servers
agent-bom where              # show all discovery paths
```

## When to Use

- "find agents" / "what agents are configured"
- "what MCP servers do I have"
- "what's configured on this machine"
- "mcp inventory"
- "doctor" / "check my setup"
- "show me what's installed"

## Commands

```bash
# Discover all AI agents and MCP servers
agent-bom agents

# Check configuration health and prerequisites
agent-bom doctor

# List MCP server inventory
agent-bom mcp inventory

# Show all discovery paths
agent-bom where
```

## Examples

```
# Discover all agents
agents()

# Run health check
doctor()

# List MCP inventory
inventory()
```

**Example output:**
```
Discovered 3 MCP clients:
  Claude Desktop  — 4 servers configured
  Cursor          — 2 servers configured
  VS Code         — 1 server configured

Servers: filesystem, brave-search, github, slack, postgres, linear, notion
Registry: 5/7 servers found in registry (427+ entries)
```

## Guardrails

- Discovery is read-only — no files are modified, no packages installed.
- Env var values in config files are always replaced with `***REDACTED***` before processing.
- Only structural data (server names, commands, URLs) is extracted.
- Confirm with user before scanning paths outside the home directory.
