import { describe, it, expect } from "vitest";
import { McpRegistry } from "./McpRegistry.js";

describe("McpRegistry", () => {
  it("should initialize with default URL", () => {
    const registry = new McpRegistry();
    expect(registry).toBeDefined();
  });

  it("should resolve known mock skill", async () => {
    const registry = new McpRegistry();
    const skill = await registry.resolve("mcp/filesystem");
    
    expect(skill).toBeDefined();
    expect(skill?.id).toBe("mcp/filesystem");
    expect(skill?.adapterType).toBe("mcp");
    expect(skill?.entrypoint).toContain("server-filesystem");
  });

  it("should return null for unknown skill", async () => {
    const registry = new McpRegistry();
    const skill = await registry.resolve("mcp/unknown");
    expect(skill).toBeNull();
  });

  it("should return null for non-mcp prefix", async () => {
    const registry = new McpRegistry();
    const skill = await registry.resolve("http/something");
    expect(skill).toBeNull();
  });

  it("should search and return results (mock)", async () => {
    const registry = new McpRegistry();
    const skills = await registry.search("query");
    expect(skills).toEqual([]); // Current mock returns empty array
  });
});
