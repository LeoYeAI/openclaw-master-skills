# MCP Server Troubleshooting

## "npx: command not found"

Node.js is not installed or not on PATH.

**Fix:**
1. Install Node.js from https://nodejs.org (LTS recommended)
2. Verify: `node --version && npx --version`
3. If installed but not found, check PATH: `which node`

## "uvx: command not found"

The uv Python package manager is not installed.

**Fix:**
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Restart your terminal or run: `source ~/.zshrc`
3. Verify: `uvx --version`

## "Server failed to start"

The MCP server process exits immediately or doesn't respond.

**Common causes:**
- Required environment variables not set
- Wrong package name
- Package not compatible with current Node/Python version

**Fix:**
1. Check env vars are set: `echo $VAR_NAME` for each required variable
2. Test the server manually:
   - npx: `npx -y @package/name --help`
   - uvx: `uvx package-name --help`
3. Check for error output in the terminal
4. Verify the package exists: `npm view @package/name` or `pip show package-name`

## "Permission denied"

File permission issues with config files or npm global installs.

**Fix for config files:**
```bash
chmod 644 .mcp.json
```

**Fix for npm global install:**
```bash
# Option 1: Use npx instead (no global install needed)
# Option 2: Fix npm permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

## "Connection refused" (HTTP servers)

The remote MCP server URL is unreachable.

**Fix:**
1. Verify the URL is correct and the service is running
2. Test with curl: `curl -X POST https://your-url/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'`
3. Check auth token is valid and not expired
4. Check if the service requires a VPN or specific network access

## "Environment variable not set"

A required environment variable is missing or empty.

**Fix:**
1. Check current value: `echo $VAR_NAME`
2. Set it for current session: `export VAR_NAME=your-value`
3. For persistence, add to shell profile:
   ```bash
   echo 'export VAR_NAME=your-value' >> ~/.zshrc
   source ~/.zshrc
   ```
4. Verify it persists: open a new terminal and run `echo $VAR_NAME`

## "Config not picked up after install"

OpenClaw doesn't see the new MCP server after adding it to `.mcp.json`.

**Fix:**
1. Verify `.mcp.json` is valid JSON: `python3 -c "import json; json.load(open('.mcp.json')); print('OK')"`
2. Verify the file is in the project root directory
3. Restart OpenClaw to reload the configuration
4. Check that the server entry is inside the `"mcpServers"` key

## "Package not found" during install

The npm/PyPI package name may have changed or been deprecated.

**Fix:**
1. Search npm: `npm search mcp-server-<name>`
2. Search PyPI: `pip search` or check https://pypi.org
3. Check the server's GitHub repository for updated install instructions
4. The official MCP servers list: https://github.com/modelcontextprotocol/servers

## "Health check timed out"

The server process started but did not respond to the initialize request within the timeout period.

**Fix:**
1. The server may need environment variables set before it can respond — check all required vars are exported
2. Check if the server requires a database connection or external service to be running
3. Try increasing the timeout: `python3 scripts/health_check.py --server-id "<id>" --timeout 30`
4. Test the server manually by running its command directly in the terminal

## "Health check: connection refused" (HTTP servers)

The HTTP MCP server URL is not reachable during health check.

**Fix:**
1. Verify the URL is correct in your config file
2. Check if the service requires authentication — ensure your token env var is set
3. Test with curl: `curl -X POST <url> -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'`
4. Check if the service is behind a VPN or firewall

## "Health check: tools/list returned empty"

The server initialized successfully but reported no tools.

**Fix:**
1. This may be normal for servers that require configuration before exposing tools
2. Check if additional environment variables or arguments are needed
3. Some servers only expose tools after specific setup steps (e.g., connecting to a database)

## "Config not found for Claude Desktop"

The Claude Desktop config file was not found at the expected path.

**Fix:**
1. macOS: Check `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Windows: Check `%APPDATA%/Claude/claude_desktop_config.json`
3. Linux: Check `~/.config/claude/claude_desktop_config.json`
4. If Claude Desktop hasn't been configured before, create the file manually with `{"mcpServers": {}}`

## "Config not found for Cursor"

The Cursor MCP config file was not found.

**Fix:**
1. Check `.cursor/mcp.json` in your project root
2. Create the `.cursor` directory if it doesn't exist: `mkdir -p .cursor`
3. Create the config file: `echo '{"mcpServers": {}}' > .cursor/mcp.json`
4. Ensure Cursor is configured to use MCP servers
