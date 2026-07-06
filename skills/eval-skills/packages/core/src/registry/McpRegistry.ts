import { Skill } from "../types/index.js";

interface McpRegistryItem {
  name: string;
  description: string;
  url: string; // SSE endpoint or repo URL
  type: "sse" | "stdio";
}

/**
 * Registry for MCP Servers
 * Allows fetching skills from modelcontextprotocol.io or other registries.
 */
export class McpRegistry {
  private registryUrl: string;

  constructor(registryUrl = "https://registry.modelcontextprotocol.io/v1") {
    this.registryUrl = registryUrl;
  }

  /**
   * Search for MCP servers in the registry
   * (Mock implementation as actual API spec might vary)
   */
  async search(query: string): Promise<Skill[]> {
    // TODO: Implement actual registry API call
    // For now, return mock data or fetch from a known list
    
    // Simulating fetch
    const results: McpRegistryItem[] = [
      // Mock data
    ];

    return results.map(item => this.convertToSkill(item));
  }

  /**
   * Convert registry item to Skill object
   */
  private convertToSkill(item: McpRegistryItem): Skill {
    return {
      id: `mcp/${item.name}`,
      name: item.name,
      version: "1.0.0", // Registry might provide version
      description: item.description,
      adapterType: "mcp",
      entrypoint: item.url,
      tags: [],
      inputSchema: {}, // Default empty schema, should be fetched from tool definition
      outputSchema: {},
      metadata: {
        transport: item.type
      }
    };
  }
  
  /**
   * Resolves a skill by ID from the registry
   * e.g. "mcp/filesystem"
   */
  async resolve(skillId: string): Promise<Skill | null> {
      if (!skillId.startsWith("mcp/")) return null;
      
      const name = skillId.replace("mcp/", "");
      // Fetch details for `name`
      
      // Mock resolution
      if (name === "filesystem") {
          return {
              id: "mcp/filesystem",
              name: "filesystem",
              version: "0.1.0",
              description: "Filesystem access via MCP",
              adapterType: "mcp",
              entrypoint: "npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/dir",
              tags: ["filesystem", "mcp"],
              inputSchema: {},
              outputSchema: {},
              metadata: {
                  transport: "stdio"
              }
          };
      }
      
      return null;
  }
}
