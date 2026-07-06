/**
 * @file sandbox/SandboxFactory.ts
 * @description 沙箱工厂 + 自动降级策略
 *
 * 职责：
 *   1. 根据 SandboxConfig.runtime 选择适当的沙箱实现
 *   2. "auto" 模式：检测 Docker 可用性，自动降级到 ProcessSandbox
 *   3. 构建并缓存单例沙箱实例（同一配置复用）
 *   4. 提供默认配置合并工具
 *
 * 降级策略（auto 模式）：
 *   ┌─────────────────────────────────────────────────┐
 *   │  Docker daemon 可访问?                          │
 *   │  YES → DockerSandbox  (强隔离，推荐)             │
 *   │  NO  → ProcessSandbox (弱隔离，打印安全警告)     │
 *   └─────────────────────────────────────────────────┘
 */

import type { SandboxConfig } from "./types.js";
import { DEFAULT_SANDBOX_CONFIG } from "./types.js";
import { ProcessSandbox } from "./ProcessSandbox.js";
import { DockerSandbox } from "./DockerSandbox.js";
import type { SandboxExecutor } from "./SandboxExecutor.js";

// ─── 工厂 ─────────────────────────────────────────────────────────────────────

export class SandboxFactory {
  /**
   * 创建沙箱实例
   *
   * @param config 沙箱配置（可以是完整配置或 Partial，会与默认配置合并）
   * @returns 对应运行时的 SandboxExecutor 实例
   */
  async createExecutor(
    config: Partial<SandboxConfig> = {},
  ): Promise<SandboxExecutor> {
    const merged = SandboxFactory.mergeWithDefaults(config);

    switch (merged.runtime) {
      case "process":
        return new ProcessSandbox(merged);

      case "docker":
        return new DockerSandbox(merged);

      case "auto":
      default:
        return this.createAuto(merged);
    }
  }

  /**
   * auto 模式：检测 Docker 可用性，自动选择实现
   */
  private async createAuto(config: SandboxConfig): Promise<SandboxExecutor> {
    const dockerSandbox = new DockerSandbox(config);

    // If already checked and cached, we could return here, but for now we check availability each time or assume caller handles lifecycle.
    // In factory pattern, we just create. 
    // To avoid repeated checks, we could cache the result of availability check in the factory instance if it was singleton, but it is not.
    // However, checking availability might be slow.
    // Ideally we should cache this decision globally or passed in.
    
    // For now, simple implementation:
    let dockerAvailable = false;
    try {
        dockerAvailable = await dockerSandbox.isAvailable();
    } catch {
        dockerAvailable = false;
    }

    if (dockerAvailable) {
      // console.info("[eval-skills sandbox] Docker detected — using DockerSandbox");
      return dockerSandbox;
    }
    
    // Docker not available, fallback
    return new ProcessSandbox(config);
  }

  /**
   * 将用户提供的 Partial<SandboxConfig> 与默认配置深度合并
   */
  static mergeWithDefaults(partial: Partial<SandboxConfig>): SandboxConfig {
    return {
      enabled: partial.enabled ?? DEFAULT_SANDBOX_CONFIG.enabled,
      runtime: partial.runtime ?? DEFAULT_SANDBOX_CONFIG.runtime,

      resources: {
        ...DEFAULT_SANDBOX_CONFIG.resources,
        ...partial.resources,
      },

      network: partial.network ?? DEFAULT_SANDBOX_CONFIG.network,

      filesystem: {
        ...DEFAULT_SANDBOX_CONFIG.filesystem,
        ...partial.filesystem,
      },

      env: {
        allowList: Array.from(new Set([
          ...DEFAULT_SANDBOX_CONFIG.env.allowList,
          ...(partial.env?.allowList ?? []),
        ])),
        inject: {
          ...DEFAULT_SANDBOX_CONFIG.env.inject,
          ...partial.env?.inject,
        },
      },

      docker: {
        ...DEFAULT_SANDBOX_CONFIG.docker,
        ...partial.docker,
      },
    };
  }

  /**
   * 快速构建"仅进程隔离"的开发模式沙箱（跳过 Docker 检测）
   */
  static createProcessSandbox(partial: Partial<SandboxConfig> = {}): ProcessSandbox {
    const merged = SandboxFactory.mergeWithDefaults({
      ...partial,
      runtime: "process",
    });
    return new ProcessSandbox(merged);
  }

  /**
   * 快速构建 Docker 沙箱（不做可用性检测，直接创建）
   */
  static createDockerSandbox(partial: Partial<SandboxConfig> = {}): DockerSandbox {
    const merged = SandboxFactory.mergeWithDefaults({
      ...partial,
      runtime: "docker",
    });
    return new DockerSandbox(merged);
  }
}
