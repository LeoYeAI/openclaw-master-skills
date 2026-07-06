import { BaseAdapter } from "./BaseAdapter.js";
import type { AdapterType, Skill, AdapterResponse, HealthCheckResult, InvokeOptions } from "../types/index.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";

interface McpMetadata {
  transport?: "stdio" | "sse";
  toolName?: string;
}

/**
 * MCP Adapter
 * 
 * Supports calling MCP tools via stdio or SSE transport.
 * The entrypoint string determines the connection type:
 * - "http://..." or "https://..." -> SSE transport
 * - otherwise -> stdio transport (interpreted as command)
 * 
 * The skill.metadata can optionally contain "toolName" to specify which tool to call.
 * If not provided, it defaults to the skill.id.
 */
export class McpAdapter extends BaseAdapter {
  readonly type: AdapterType = "mcp";

  /**
   * Invoke an MCP tool
   */
  protected async doInvoke(
    skill: Skill,
    input: Record<string, unknown>,
    signal?: AbortSignal,
    options?: InvokeOptions
  ): Promise<AdapterResponse> {
    let client: Client | undefined;
    let transport: Transport | undefined;

    try {
      // 1. Determine transport and create client
      const { client: c, transport: t } = await this.createClient(skill);
      client = c;
      transport = t;

      // 2. Connect
      await client.connect(transport);

      // 3. Resolve tool name
      // Default to skill.id, or use metadata.toolName if available
      const meta = skill.metadata as unknown as McpMetadata;
      const toolName = meta.toolName || skill.id;

      // 4. Call tool
      const result = await client.callTool({
        name: toolName,
        arguments: input,
      });

      // 5. Process result
      // MCP result content is an array of Content (TextContent | ImageContent | EmbeddedResource)
      // We extract the text content for now as the primary output
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const content = result.content as any[];
      const textContent = content
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .filter((c: any) => c.type === "text")
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((c: any) => c.text)
        .join("\n");

      // Try to parse JSON from the text content if possible, as many skills output JSON
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let parsedOutput: any = textContent;
      try {
          parsedOutput = JSON.parse(textContent);
      } catch {
          // ignore, keep as string
      }

      return {
        success: true,
        output: parsedOutput,
        latencyMs: 0, // Calculated by BaseAdapter
        rawResponse: result, // Keep full raw result for advanced scorers
      };

    } catch (error) {
      return {
        success: false,
        error: (error as Error).message,
        latencyMs: 0,
      };
    } finally {
        // Close connection
        if (transport) {
            try {
                await transport.close();
            } catch {
                // Ignore close errors
            }
        }
    }
  }

  /**
   * Check if the tool exists in the MCP server
   */
  async healthCheck(skill: Skill): Promise<HealthCheckResult> {
    let client: Client | undefined;
    let transport: Transport | undefined;

    try {
      const { client: c, transport: t } = await this.createClient(skill);
      client = c;
      transport = t;

      await client.connect(transport);

      const tools = await client.listTools();
      const meta = skill.metadata as unknown as McpMetadata;
      const toolName = meta.toolName || skill.id;
      const exists = tools.tools.some(t => t.name === toolName);

      return {
        healthy: exists,
        message: exists ? "Tool found" : `Tool "${toolName}" not found in MCP server`,
        latencyMs: 0,
      };

    } catch (error) {
      return {
        healthy: false,
        message: (error as Error).message,
        latencyMs: 0,
      };
    } finally {
        if (transport) {
            try {
                await transport.close();
            } catch {
                // Ignore close errors
            }
        }
    }
  }

  /**
   * Create MCP Client and Transport based on skill entrypoint
   */
  private async createClient(skill: Skill): Promise<{ client: Client; transport: Transport }> {
    const entrypoint = skill.entrypoint;
    let transport: Transport;

    if (entrypoint.startsWith("http://") || entrypoint.startsWith("https://")) {
      // SSE Transport
      transport = new SSEClientTransport(new URL(entrypoint));
    } else {
      // Stdio Transport
      // Use regex to respect quoted arguments
      const parts = entrypoint.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
      const command = parts[0] ?? "";
      const args = parts.slice(1).map(arg => arg.replace(/^"|"$/g, ""));
      
      transport = new StdioClientTransport({
        command,
        args,
      });
    }

    const client = new Client(
      {
        name: "eval-skills-client",
        version: "0.1.0",
      },
      {
        capabilities: {},
      }
    );

    return { client, transport };
  }
}
