import { SkillCreator } from "./SkillCreator.js";
import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { tmpdir } from "node:os";
import SwaggerParser from "@apidevtools/swagger-parser";

// Mock SwaggerParser
vi.mock("@apidevtools/swagger-parser", () => ({
  default: {
    validate: vi.fn(),
  },
}));

describe("SkillCreator", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(tmpdir(), "skill-creator-test-"));
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
    vi.clearAllMocks();
  });

  it("should create http_request skill skeleton", async () => {
    const result = await SkillCreator.create({
      name: "test-http-skill",
      template: "http_request",
      outputDir: tmpDir,
    });

    expect(result.files).toHaveLength(3);
    expect(fs.existsSync(path.join(tmpDir, "test-http-skill", "skill.json"))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, "test-http-skill", "adapter.config.json"))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, "test-http-skill", "tests", "basic.eval.json"))).toBe(true);

    const skillJson = JSON.parse(fs.readFileSync(path.join(tmpDir, "test-http-skill", "skill.json"), "utf-8"));
    expect(skillJson.adapterType).toBe("http");
  });

  it("should create python_script skill skeleton", async () => {
    const result = await SkillCreator.create({
      name: "test-py-skill",
      template: "python_script",
      outputDir: tmpDir,
    });

    expect(result.files).toHaveLength(4); // + skill.py
    expect(fs.existsSync(path.join(tmpDir, "test-py-skill", "skill.py"))).toBe(true);
    
    const skillJson = JSON.parse(fs.readFileSync(path.join(tmpDir, "test-py-skill", "skill.json"), "utf-8"));
    expect(skillJson.adapterType).toBe("subprocess");
  });

  it("should create skill from openapi spec", async () => {
    const mockApi = {
      info: { version: "1.0.0", title: "Test API" },
      paths: {
        "/test": {
          post: {
            operationId: "testOp",
            summary: "Test Op",
            requestBody: {
                content: {
                    "application/json": {
                        schema: { type: "object", properties: { foo: { type: "string" } } }
                    }
                }
            },
            responses: {
                "200": {
                    content: {
                        "application/json": {
                            schema: { type: "object", properties: { bar: { type: "string" } } }
                        }
                    }
                }
            }
          },
        },
      },
      servers: [{ url: "http://api.example.com" }],
    };

    (SwaggerParser.validate as any).mockResolvedValue(mockApi);

    const result = await SkillCreator.createFromOpenAPI("api-skill", "spec.json", tmpDir);

    expect(fs.existsSync(path.join(tmpDir, "api-skill", "skill.json"))).toBe(true);
    
    const skillJson = JSON.parse(fs.readFileSync(path.join(tmpDir, "api-skill", "skill.json"), "utf-8"));
    expect(skillJson.adapterType).toBe("http");
    expect(skillJson.entrypoint).toBe("http://api.example.com/test");
    // Check extracted schemas
    expect(skillJson.inputSchema).toEqual({ type: "object", properties: { foo: { type: "string" } } });
    expect(skillJson.outputSchema).toEqual({ type: "object", properties: { bar: { type: "string" } } });
  });
});
