import { spawn } from "node:child_process";
import * as path from "node:path";
import { BaseAdapter } from "./BaseAdapter.js";
import {
    SandboxFactory,
    SandboxExecutor,
    DEFAULT_SANDBOX_CONFIG,
    type SandboxConfig,
    type JsonRpcRequest as SandboxRpcRequest
} from "../sandbox/index.js";
import type {
  Skill,
  AdapterType,
  AdapterResponse,
  HealthCheckResult,
} from "../types/index.js";

/**
 * JSON-RPC 2.0 请求结构
 */
interface JsonRpcRequest {
  jsonrpc: "2.0";
  method: "invoke" | "healthcheck";
  params: Record<string, unknown>;
  id: number;
}

/**
 * JSON-RPC 2.0 响应结构
 */
interface JsonRpcResponse {
  jsonrpc: "2.0";
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
  id: number;
}

export interface SubprocessAdapterConfig {
    /**
     * 沙箱隔离级别
     * - "process": 进程级隔离 (默认)
     * - "docker": Docker 容器隔离 (需安装 Docker)
     * - "auto": 自动选择
     */
    sandboxLevel?: "process" | "docker" | "auto";
    
    /**
     * 自定义沙箱配置 (可选)
     */
    sandboxConfig?: Partial<SandboxConfig>;
}

/**
 * Subprocess Adapter
 *
 * 通过沙箱 (SandboxExecutor) 调用 Skill：
 * - 默认使用 ProcessSandbox (进程隔离)
 * - 可配置 DockerSandbox (容器隔离)
 * - 自动处理 JSON-RPC 通信
 */
export class SubprocessAdapter extends BaseAdapter {
  readonly type: AdapterType = "subprocess";
  private sandboxFactory: SandboxFactory;
  private sandboxLevel: "process" | "docker" | "auto";
  private customSandboxConfig?: Partial<SandboxConfig>;

  constructor(config?: SubprocessAdapterConfig) {
    super();
    this.sandboxLevel = config?.sandboxLevel ?? "process";
    this.customSandboxConfig = config?.sandboxConfig;
    this.sandboxFactory = new SandboxFactory();
  }

  /**
   * 通过沙箱调用 Skill
   */
  protected async doInvoke(
    skill: Skill,
    input: Record<string, unknown>,
    signal?: AbortSignal,
  ): Promise<AdapterResponse> {
    const request: JsonRpcRequest = {
      jsonrpc: "2.0",
      method: "invoke",
      params: input,
      id: 1,
    };

    const sandbox = await this.createSandbox(skill);

    try {
        const response = await this.executeInSandbox(sandbox, skill, request, signal);
        
        if (response.error) {
            return {
              success: false,
              error: `JSON-RPC error ${response.error.code}: ${response.error.message}`,
              latencyMs: 0,
              rawResponse: response,
            };
        }

        return {
            success: true,
            output: response.result,
            latencyMs: 0, // BaseAdapter 会覆写
            rawResponse: response,
        };
    } finally {
        // 这里的 cleanup 主要是为了清理 Docker 容器等重资源
        // ProcessSandbox 的 cleanup 可能是 no-op，但保持一致性很重要
        // 目前 SandboxExecutor 接口没有 cleanup，但 DockerSandbox 内部有清理逻辑
        // 实际上 SandboxExecutor 是单次执行的抽象，执行完即结束
        // 如果是长活沙箱，需要 explicit cleanup
        // 当前架构 execute() 内部负责了生命周期管理 (ProcessSandbox kill tree, DockerSandbox rm container)
        // 所以这里不需要显式 cleanup，除非我们改变了 execute 的语义
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(skill: Skill): Promise<HealthCheckResult> {
    const request: JsonRpcRequest = {
      jsonrpc: "2.0",
      method: "healthcheck",
      params: {},
      id: 0,
    };

    const start = performance.now();
    const sandbox = await this.createSandbox(skill);

    try {
      const response = await this.executeInSandbox(
        sandbox, 
        skill, 
        request, 
        AbortSignal.timeout(5_000)
      );

      const latencyMs = performance.now() - start;

      if (response.error) {
        return {
          healthy: false,
          message: `JSON-RPC error ${response.error.code}: ${response.error.message}`,
          latencyMs,
        };
      }

      return {
        healthy: true,
        message: "OK",
        latencyMs,
      };
    } catch (err) {
      const latencyMs = performance.now() - start;
      return {
        healthy: false,
        message: err instanceof Error ? err.message : String(err),
        latencyMs,
      };
    }
  }

  private async createSandbox(skill: Skill): Promise<SandboxExecutor> {
      const skillDir = skill.rootPath || process.cwd();
      
      const config: SandboxConfig = {
          ...DEFAULT_SANDBOX_CONFIG,
          runtime: this.sandboxLevel,
          ...this.customSandboxConfig,
          filesystem: {
              ...DEFAULT_SANDBOX_CONFIG.filesystem,
              ...this.customSandboxConfig?.filesystem,
              allowPaths: Array.from(new Set([
                  ...(DEFAULT_SANDBOX_CONFIG.filesystem.allowPaths || []),
                  ...(this.customSandboxConfig?.filesystem?.allowPaths || []),
                  skillDir
              ]))
          }
      };

      return this.sandboxFactory.createExecutor(config);
  }

  private async executeInSandbox(
      sandbox: SandboxExecutor,
      skill: Skill,
      request: JsonRpcRequest,
      signal?: AbortSignal
  ): Promise<JsonRpcResponse> {
      const skillDir = skill.rootPath || process.cwd(); 

      // Execute in sandbox
      const result = await sandbox.execute(
          skill.entrypoint,
          skillDir,
          request as SandboxRpcRequest,
          signal
      );

      if (!result.success) {
          throw new Error(
              `Sandbox execution failed: ${result.error || "Unknown error"}\nStdout: ${result.stdout}\nStderr: ${result.stderr}`
          );
      }

      // Parse JSON-RPC response from stdout
      return this.parseJsonRpcResponse(result.stdout, request.id);
  }

  private parseJsonRpcResponse(stdout: string, expectedId: number): JsonRpcResponse {
      const lines = stdout.trim().split("\n");
      let parsed: JsonRpcResponse | undefined;

      // Scan from end to start
      const validLines = lines
          .map(line => line.trim())
          .filter(line => line.startsWith("{") && line.endsWith("}"))
          .reverse();

      for (const line of validLines) {
          try {
              const obj = JSON.parse(line);
              if (
                  obj.jsonrpc === "2.0" && 
                  (obj.result !== undefined || obj.error !== undefined) &&
                  (obj.id === expectedId || obj.id === null)
              ) {
                  parsed = obj;
                  break;
              }
          } catch {}
      }

      if (!parsed) {
          throw new Error(`Failed to find valid JSON-RPC response. Output: ${stdout.trim()}`);
      }
      return parsed;
  }
}
