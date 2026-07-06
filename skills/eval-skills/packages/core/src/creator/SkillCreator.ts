import * as fs from "node:fs";
import * as path from "node:path";
import SwaggerParser from "@apidevtools/swagger-parser";

export type TemplateType = "http_request" | "python_script" | "mcp_tool";

export interface CreateOptions {
  name: string;
  template: TemplateType;
  outputDir?: string;
  description?: string;
  openapiSpec?: string;
}

export interface CreateResult {
  skillDir: string;
  files: string[];
}

/**
 * Skill 骨架生成器
 */
export class SkillCreator {
  /**
   * 根据模板生成 Skill 骨架
   */
  static async create(options: CreateOptions): Promise<CreateResult> {
    const { name, template, outputDir = "./skills", description = "", openapiSpec } = options;
    const skillDir = path.resolve(outputDir, name);
    const files: string[] = [];

    // 创建目录
    fs.mkdirSync(path.join(skillDir, "tests"), { recursive: true });

    // 如果提供了 OpenAPI spec，则从 spec 生成
    if (openapiSpec) {
      return await SkillCreator.createFromOpenAPI(name, openapiSpec, outputDir);
    }

    // 生成 skill.json
    const skillJson = SkillCreator.generateSkillJson(name, template, description);
    const skillJsonPath = path.join(skillDir, "skill.json");
    fs.writeFileSync(skillJsonPath, JSON.stringify(skillJson, null, 2));
    files.push(skillJsonPath);

    // 生成 adapter.config.json
    const adapterConfig = SkillCreator.generateAdapterConfig(template);
    const adapterConfigPath = path.join(skillDir, "adapter.config.json");
    fs.writeFileSync(adapterConfigPath, JSON.stringify(adapterConfig, null, 2));
    files.push(adapterConfigPath);

    // 生成 tests/basic.eval.json
    const evalJson = SkillCreator.generateBasicEval(name);
    const evalJsonPath = path.join(skillDir, "tests", "basic.eval.json");
    fs.writeFileSync(evalJsonPath, JSON.stringify(evalJson, null, 2));
    files.push(evalJsonPath);

    // Python 模板额外生成 skill.py
    if (template === "python_script") {
      const skillPyPath = path.join(skillDir, "skill.py");
      fs.writeFileSync(skillPyPath, SkillCreator.generatePythonScript(name));
      files.push(skillPyPath);
    }

    return { skillDir, files };
  }

  /**
   * 从 OpenAPI Spec 生成 Skill
   */
  static async createFromOpenAPI(
    name: string,
    specPath: string,
    outputDir: string = "./skills",
  ): Promise<CreateResult> {
    const api = await SwaggerParser.validate(specPath);
    const skillDir = path.resolve(outputDir, name);
    const files: string[] = [];

    // 创建目录
    fs.mkdirSync(path.join(skillDir, "tests"), { recursive: true });

    // 提取第一个路径的第一个操作作为示例 (简化处理)
    // 实际应支持选择操作或生成多个 Skill
    const paths = api.paths || {};
    const firstPathKey = Object.keys(paths)[0];
    if (!firstPathKey) {
      throw new Error("No paths found in OpenAPI spec");
    }

    const pathItem = paths[firstPathKey];
    const methods = ["get", "post", "put", "delete", "patch", "options", "head"];
    const method = methods.find((m) => (pathItem as any)[m]);

    if (!method) {
      throw new Error(`No supported method found for path ${firstPathKey}`);
    }

    const operation = (pathItem as any)[method];
    const operationId = operation.operationId || `${method}${firstPathKey.replace(/\//g, "_")}`;
    
    // Extract input schema from requestBody or parameters
    let inputSchema: Record<string, any> = { type: "object", properties: {}, description: "Input parameters" };
    
    // Try to get schema from requestBody
    const requestBody = operation.requestBody;
    if (requestBody && !("$ref" in requestBody)) { // Simple handling, resolve refs if needed later
         const content = requestBody.content?.["application/json"];
         if (content?.schema) {
             inputSchema = content.schema;
         }
    }
    
    // Extract output schema from responses
    let outputSchema: Record<string, any> = { type: "object", properties: {}, description: "Output response" };
    const successResponse = operation.responses?.["200"] || operation.responses?.["201"];
    if (successResponse && !("$ref" in successResponse)) {
        const content = successResponse.content?.["application/json"];
         if (content?.schema) {
             outputSchema = content.schema;
         }
    }

    // 生成 skill.json
    const anyApi = api as any;
    const serverUrl = anyApi.servers?.[0]?.url || "http://localhost";
    const entrypoint = `${serverUrl}${firstPathKey}`;

    const skillJson = {
      id: name.toLowerCase().replace(/[^a-z0-9_-]/g, "_"),
      name,
      version: api.info.version || "0.1.0",
      description: operation.summary || operation.description || `Skill generated from OpenAPI: ${name}`,
      tags: ["openapi", ...(api.info.contact?.name ? [api.info.contact.name] : [])],
      inputSchema,
      outputSchema,
      adapterType: "http",
      entrypoint,
      metadata: {
        author: api.info.contact?.name || "",
        license: api.info.license?.name || "MIT",
        openapi: {
            specPath,
            operationId,
            method: method.toUpperCase(),
        }
      },
    };

    const skillJsonPath = path.join(skillDir, "skill.json");
    fs.writeFileSync(skillJsonPath, JSON.stringify(skillJson, null, 2));
    files.push(skillJsonPath);

    // 生成 adapter.config.json
    const adapterConfig = {
      type: "http",
      baseUrl: serverUrl,
      method: method.toUpperCase(),
      timeoutMs: 30000,
      headers: {
          "Content-Type": "application/json"
      }
    };
    const adapterConfigPath = path.join(skillDir, "adapter.config.json");
    fs.writeFileSync(adapterConfigPath, JSON.stringify(adapterConfig, null, 2));
    files.push(adapterConfigPath);
    
    // 生成 tests/basic.eval.json
    const evalJson = {
      id: `${name}-openapi-test`,
      name: `${name} OpenAPI Test`,
      version: "1.0.0",
      domain: "api",
      tasks: [
        {
          id: `${name}_test_001`,
          description: `Test for ${operationId}`,
          inputData: {},
          expectedOutput: { type: "json_schema", schema: { type: "object" } }, // Generic schema
          evaluator: { type: "json_schema" },
          timeoutMs: 30000,
        },
      ],
    };
    const evalJsonPath = path.join(skillDir, "tests", "basic.eval.json");
    fs.writeFileSync(evalJsonPath, JSON.stringify(evalJson, null, 2));
    files.push(evalJsonPath);

    return { skillDir, files };
  }

  private static generateSkillJson(
    name: string,
    template: TemplateType,
    description: string,
  ) {
    const adapterMap: Record<TemplateType, string> = {
      http_request: "http",
      python_script: "subprocess",
      mcp_tool: "mcp",
    };
    const entrypointMap: Record<TemplateType, string> = {
      http_request: "http://localhost:3000/invoke",
      python_script: `python3 skill.py`,
      mcp_tool: "mcp://localhost:8080/tools/" + name,
    };

    return {
      id: name.toLowerCase().replace(/[^a-z0-9_-]/g, "_"),
      name,
      version: "0.1.0",
      description: description || `A ${template} skill: ${name}`,
      tags: [],
      inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] },
      outputSchema: { type: "object", properties: { result: { type: "string" } } },
      adapterType: adapterMap[template],
      entrypoint: entrypointMap[template],
      metadata: { author: "", license: "MIT" },
    };
  }

  private static generateAdapterConfig(template: TemplateType) {
    if (template === "http_request") {
      return {
        type: "http",
        baseUrl: "http://localhost:3000",
        authType: "none",
        timeoutMs: 15000,
        retries: 1,
      };
    }
    if (template === "python_script") {
      return {
        type: "subprocess",
        command: "python3",
        args: ["skill.py"],
        timeoutMs: 30000,
      };
    }
    return { type: "mcp", timeoutMs: 30000 };
  }

  private static generateBasicEval(name: string) {
    return {
      id: `${name}-basic`,
      name: `${name} Basic Test`,
      version: "1.0.0",
      domain: "general",
      scoringMethod: "mean",
      metadata: {},
      tasks: [
        {
          id: `${name}_test_001`,
          description: `Basic test for ${name}`,
          inputData: { query: "test input" },
          expectedOutput: { type: "contains", keywords: ["result"] },
          evaluator: { type: "contains" },
          timeoutMs: 30000,
        },
      ],
    };
  }

  private static generatePythonScript(name: string): string {
    return `#!/usr/bin/env python3
"""${name} — JSON-RPC subprocess skill"""
import json
import sys

def invoke(params):
    """Handle invoke method. Override this with your logic."""
    query = params.get("query", "")
    return {"result": f"Processed: {query}"}

def healthcheck(params):
    return {"status": "healthy"}

def main():
    raw = sys.stdin.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}))
        return

    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    handlers = {"invoke": invoke, "healthcheck": healthcheck}
    handler = handlers.get(method)

    if handler is None:
        response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {method}"}, "id": req_id}
    else:
        try:
            result = handler(params)
            response = {"jsonrpc": "2.0", "result": result, "id": req_id}
        except Exception as e:
            response = {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}, "id": req_id}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
`;
  }
}
