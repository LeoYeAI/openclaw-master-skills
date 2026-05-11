/**
 * stdio.ts — MCP Stdio Transport Entry Point
 *
 * Allows agent-comm-hub to run as a stdio MCP server (command-based),
 * in addition to the existing HTTP Streamable HTTP transport.
 *
 * Usage: HUB_AUTH_TOKEN=<token> node dist/stdio.js
 *
 * Auth: Reads HUB_AUTH_TOKEN env var, verifies against auth_tokens table.
 * Logging: All logs go to stderr (stdout is reserved for JSON-RPC).
 */
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools } from "./tools.js";
import { verifyToken } from "./security.js";

async function main(): Promise<void> {
  const token = process.env.HUB_AUTH_TOKEN;
  if (!token) {
    console.error("[stdio] ERROR: HUB_AUTH_TOKEN environment variable is required");
    process.exit(1);
  }

  // Authenticate (importing security.js triggers db.js initialization)
  const authContext = verifyToken(token);
  if (!authContext) {
    console.error(`[stdio] ERROR: Token authentication failed`);
    process.exit(1);
  }
  console.error(`[stdio] Authenticated as ${authContext.agentId} (role: ${authContext.role})`);

  // Create MCP server — same config as HTTP transport
  const server = new McpServer({
    name: "agent-comm-hub",
    version: "2.4.0",
  });
  registerTools(server, authContext);

  // Connect stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`[stdio] Hub stdio mode started (agent: ${authContext.agentId})`);
}

main().catch((err) => {
  console.error(`[stdio] Fatal error:`, err);
  process.exit(1);
});
