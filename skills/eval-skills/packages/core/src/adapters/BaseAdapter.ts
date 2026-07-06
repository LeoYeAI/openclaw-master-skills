import type {
  SkillAdapter,
  AdapterResponse,
  InvokeOptions,
  HealthCheckResult,
  Skill,
  AdapterType,
} from "../types/index.js";

/**
 * Adapter 抽象基类
 *
 * 提供通用逻辑：
 * - 超时控制（AbortController + setTimeout）
 * - 重试（简单重试 N 次，间隔递增）
 * - latencyMs 计算（performance.now 差值）
 * - 返回标准 AdapterResponse
 */
export abstract class BaseAdapter implements SkillAdapter {
  abstract readonly type: AdapterType;

  /**
   * 调用 Skill，带超时和重试逻辑
   */
  async invoke(
    skill: Skill,
    input: Record<string, unknown>,
    options?: InvokeOptions,
  ): Promise<AdapterResponse> {
    const timeoutMs = options?.timeoutMs ?? 30_000;
    const retries = options?.retries ?? 0;

    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const start = performance.now();
        const response = await this.executeWithTimeout(
          skill,
          input,
          timeoutMs,
          options,
        );
        const latencyMs = performance.now() - start;
        return { ...response, latencyMs };
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        if (attempt < retries) {
          // Incremental backoff: 1s, 2s, 3s, ...
          await this.delay(1_000 * (attempt + 1));
        }
      }
    }

    return {
      success: false,
      error: lastError?.message ?? "Unknown error",
      latencyMs: 0,
    };
  }

  /**
   * 子类必须实现的实际调用逻辑
   */
  protected abstract doInvoke(
    skill: Skill,
    input: Record<string, unknown>,
    signal: AbortSignal,
    options?: InvokeOptions,
  ): Promise<AdapterResponse>;

  /**
   * 健康检查，子类必须实现
   */
  abstract healthCheck(skill: Skill): Promise<HealthCheckResult>;

  /**
   * 使用 AbortController 包装超时逻辑
   */
  private async executeWithTimeout(
    skill: Skill,
    input: Record<string, unknown>,
    timeoutMs: number,
    options?: InvokeOptions,
  ): Promise<AdapterResponse> {
    const controller = new AbortController();
    const { signal } = controller;

    const timer = setTimeout(() => {
      controller.abort(
        new Error(
          `Adapter invocation timed out after ${timeoutMs}ms for skill "${skill.id}"`,
        ),
      );
    }, timeoutMs);

    try {
      const result = await this.doInvoke(skill, input, signal, options);
      return result;
    } catch (err) {
      if (signal.aborted) {
        throw signal.reason;
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * 延迟工具函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
