import type { AdapterType, Skill } from "./skill.js";

/**
 * Adapter 调用响应
 */
export interface AdapterResponse {
  /** 调用是否成功 */
  success: boolean;
  /** 输出数据 */
  output?: unknown;
  /** 错误信息 */
  error?: string;
  /** 响应延迟（毫秒） */
  latencyMs: number;
  /** 原始响应（调试用） */
  rawResponse?: unknown;
  /** Token usage */
  usage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
  };
}

/**
 * 调用选项
 */
export interface InvokeOptions {
  /** 超时（毫秒） */
  timeoutMs?: number;
  /** 额外 HTTP 头 */
  headers?: Record<string, string>;
  /** 重试次数 */
  retries?: number;
}

/**
 * 健康检查结果
 */
export interface HealthCheckResult {
  healthy: boolean;
  message?: string;
  latencyMs: number;
}

/**
 * Skill Adapter 接口
 * 将标准调用转换为特定框架/协议调用
 */
export interface SkillAdapter {
  readonly type: AdapterType;

  /**
   * 调用 Skill 并返回原始输出
   */
  invoke(
    skill: Skill,
    input: Record<string, unknown>,
    options?: InvokeOptions,
  ): Promise<AdapterResponse>;

  /**
   * 健康检查
   */
  healthCheck(skill: Skill): Promise<HealthCheckResult>;
}
