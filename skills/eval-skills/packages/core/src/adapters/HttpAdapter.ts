import { BaseAdapter } from "./BaseAdapter.js";
import type {
  Skill,
  AdapterType,
  AdapterResponse,
  HealthCheckResult,
  InvokeOptions,
} from "../types/index.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../errors.js";

const EVAL_SKILLS_VERSION = "0.1.0";

/**
 * HTTP Adapter 可选配置
 */
export interface HttpAdapterConfig {
  /** 基础 URL，拼接到 skill.entrypoint 前面 */
  baseUrl?: string;
  /** 认证类型：bearer / api-key / none */
  authType?: "bearer" | "api-key" | "none";
  /** 认证 token 对应的环境变量名 */
  authTokenEnvKey?: string;
}

/**
 * HTTP Adapter
 *
 * 通过 HTTP POST 调用 Skill：
 * - POST {skill.entrypoint}
 * - Headers: Content-Type: application/json, X-Eval-Skills-Version: 0.1.0
 * - Body: { skillId, version, input }
 *
 * 使用 Node.js 原生 fetch（Node 18+）
 */
export class HttpAdapter extends BaseAdapter {
  readonly type: AdapterType = "http";

  private readonly config: HttpAdapterConfig;

  constructor(config?: HttpAdapterConfig) {
    super();
    this.config = config ?? {};
  }

  /**
   * 构建完整 URL
   */
  private buildUrl(skill: Skill): string {
    if (this.config.baseUrl) {
      // 移除 baseUrl 尾部斜杠和 entrypoint 前导斜杠，然后拼接
      const base = this.config.baseUrl.replace(/\/+$/, "");
      const path = skill.entrypoint.replace(/^\/+/, "");
      return `${base}/${path}`;
    }
    return skill.entrypoint;
  }

  /**
   * 构建认证 headers
   */
  private buildAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};

    if (
      this.config.authType &&
      this.config.authType !== "none" &&
      this.config.authTokenEnvKey
    ) {
      const envKey = this.config.authTokenEnvKey;
      
      // Security check: Only allow accessing specific env vars
      const ALLOWED_PREFIXES = ["EVAL_SKILLS_", "SKILL_", "OPENAI_", "ANTHROPIC_", "API_KEY_"];
      const isAllowed = ALLOWED_PREFIXES.some(p => envKey.startsWith(p));
      
      if (!isAllowed) {
          throw new EvalSkillsError(
              EvalSkillsErrorCode.SECURITY_VIOLATION,
              `Security violation: Access to environment variable "${envKey}" is not allowed. Allowed prefixes: ${ALLOWED_PREFIXES.join(", ")}`
          );
      }

      const token = process.env[envKey];
      if (token) {
        switch (this.config.authType) {
          case "bearer":
            headers["Authorization"] = `Bearer ${token}`;
            break;
          case "api-key":
            headers["X-API-Key"] = token;
            break;
        }
      }
    }

    return headers;
  }

  /**
   * 发送 POST 请求调用 Skill
   */
  protected async doInvoke(
    skill: Skill,
    input: Record<string, unknown>,
    signal?: AbortSignal,
    options?: InvokeOptions,
  ): Promise<AdapterResponse> {
    const url = this.buildUrl(skill);

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-Eval-Skills-Version": EVAL_SKILLS_VERSION,
      ...this.buildAuthHeaders(),
      ...options?.headers,
    };

    const body = JSON.stringify({
      skillId: skill.id,
      version: skill.version,
      input,
    });

    const response = await fetch(url, {
      method: "POST",
      headers,
      body,
      signal,
    });

    const rawResponse = await response.json() as unknown;

    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
        latencyMs: 0,
        rawResponse: rawResponse as unknown,
      };
    }

    // Try to extract token usage from headers
    // x-usage-input-tokens, x-usage-output-tokens, x-usage-total-tokens
    const inputTokens = parseInt(response.headers.get("x-usage-input-tokens") || "0", 10);
    const outputTokens = parseInt(response.headers.get("x-usage-output-tokens") || "0", 10);
    const totalTokens = parseInt(response.headers.get("x-usage-total-tokens") || "0", 10);
    
    const usage = (inputTokens || outputTokens || totalTokens) ? {
        promptTokens: inputTokens,
        completionTokens: outputTokens,
        totalTokens: totalTokens || (inputTokens + outputTokens)
    } : undefined;

    return {
      success: true,
      output: rawResponse as unknown,
      latencyMs: 0, // BaseAdapter 会覆写
      rawResponse: rawResponse as unknown,
      usage,
    };
  }

  /**
   * 健康检查：GET 请求到 entrypoint
   */
  async healthCheck(skill: Skill): Promise<HealthCheckResult> {
    const url = this.buildUrl(skill);
    const start = performance.now();

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "X-Eval-Skills-Version": EVAL_SKILLS_VERSION,
          ...this.buildAuthHeaders(),
        },
        signal: AbortSignal.timeout(5_000),
      });

      const latencyMs = performance.now() - start;

      return {
        healthy: response.ok,
        message: response.ok
          ? "OK"
          : `HTTP ${response.status}: ${response.statusText}`,
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
}
