import { HttpAdapter } from "./HttpAdapter.js";
import type { Skill } from "../types/index.js";
import { describe, it, expect, vi, afterEach } from "vitest";

// Mock fetch global
const fetchMock = vi.fn();
global.fetch = fetchMock;

const mockSkill: Skill = {
  id: "http-skill",
  name: "HTTP Skill",
  version: "1.0",
  description: "desc",
  tags: [],
  adapterType: "http",
  entrypoint: "http://example.com/api",
  inputSchema: {},
  outputSchema: {},
  metadata: {},
};

describe("HttpAdapter", () => {
  const adapter = new HttpAdapter();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should make POST request with correct body", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ result: "success" }),
    });

    const input = { foo: "bar" };
    const response = await adapter.invoke(mockSkill, input);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://example.com/api",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          skillId: mockSkill.id,
          version: mockSkill.version,
          input,
        }),
      })
    );

    expect(response.success).toBe(true);
    expect(response.output).toEqual({ result: "success" });
  });

  it("should handle non-200 response", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => ({ error: "some error" }),
      text: async () => "Error message",
    });

    const response = await adapter.invoke(mockSkill, {});

    expect(response.success).toBe(false);
    expect(response.error).toContain("HTTP 500");
  });

  it("should handle fetch error", async () => {
    fetchMock.mockRejectedValue(new Error("Network error"));

    const response = await adapter.invoke(mockSkill, {});

    expect(response.success).toBe(false);
    expect(response.error).toBe("Network error");
  });
});
