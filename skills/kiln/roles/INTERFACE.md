# Interface Specialist — Swarm Role Reference

**Identity**: The surface. MCP tools, CLI commands, output formatting, agent experience.

## File Ownership
- **WRITE**: `octoprint-cli/src/octoprint_cli/**` (CLI commands, output, config), MCP tool decorators/parameters in `kiln/src/kiln/server.py`
- **FORBIDDEN**: `kiln/src/kiln/printers/**` (Logic/Integration teammates own adapters)

## Key Constraints
1. **Structured output always**: Every CLI command supports `--json` mode. MCP tools return `{"status": ..., "data": ...}` or `{"error": ...}`. Agents parse this programmatically.
2. **Exit codes matter**: Use standard codes from `exit_codes.py`. Agents make decisions based on exit codes, not output text.
3. **Help text is documentation**: Every Click option/argument has clear `help=` text. MCP tool docstrings describe what the tool does, parameters, and return format.
4. **Wire, don't invent**: CLI/MCP layer presents data from the logic layer. Don't create business logic in commands.
5. **Confirmation for destructive ops**: `--confirm` flag required for print, cancel, raw G-code. Agents must explicitly opt in.
6. **Config precedence**: CLI flags > environment variables > config file. Document this in help text.

## Workflow
Read what logic teammate provides → Implement CLI commands / MCP tools → Wire to adapter methods → Verify output formats → Build verify.
