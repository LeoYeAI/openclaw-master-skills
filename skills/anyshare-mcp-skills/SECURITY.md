# Security

## Treat this skill as operational guidance, not executable trust

- Review `SKILL.md` and scripts before use in production. Third-party or
  registry-installed skills should be audited like any other automation.
- **Never** commit or paste real cookies, OAuth tokens, or Bearer strings into
  Git, ClawHub descriptions, or chat logs.

## Secrets and configuration

- **MCP service URL** defaults to `https://anyshare.aishu.cn/mcp` in the skill template; override in `~/.mcporter/mcporter.json` (`asmcp.url`) for private deployments. Values are **environment-specific**.
  Do not commit internal-only URLs to public repos if they expose your network topology.
- Authentication uses **agent-browser** session state under
  `~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json` — protect this file on disk.

## Data handling

- The skill may access enterprise documents only as permitted by your AnyShare
  account and MCP server policy. Follow your organization’s data-classification rules.

## Reporting

- For vulnerabilities in **this skill’s documentation or packaging**, open an
  issue in the repository that maintains this skill. For product security issues
  in AnyShare itself, follow AISHU’s official disclosure channels.
