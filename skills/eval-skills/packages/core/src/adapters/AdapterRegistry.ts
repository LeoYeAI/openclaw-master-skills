import type { SkillAdapter, AdapterType, Skill } from "../types/index.js";
import { HttpAdapter } from "./HttpAdapter.js";
import { SubprocessAdapter } from "./SubprocessAdapter.js";
import { McpAdapter } from "./McpAdapter.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../errors.js";

/**
 * Adapter 注册表
 *
 * - 内置预注册 http → HttpAdapter, subprocess → SubprocessAdapter, mcp → McpAdapter
 * - 支持自定义注册扩展 adapter
 * - 通过 AdapterType 或 Skill 解析对应 adapter
 */
export class AdapterRegistry {
  private readonly adapters = new Map<string, SkillAdapter>();

  constructor() {
    // 预注册内置 adapters
    this.adapters.set("http", new HttpAdapter());
    this.adapters.set("subprocess", new SubprocessAdapter());
    this.adapters.set("mcp", new McpAdapter());
  }

  /**
   * 注册自定义 Adapter
   *
   * @param type - adapter 类型标识
   * @param adapter - SkillAdapter 实例
   */
  register(type: string, adapter: SkillAdapter): void {
    this.adapters.set(type, adapter);
  }

  /**
   * 按类型解析 Adapter
   *
   * @throws EvalSkillsError 当 adapter 类型未注册时
   */
  resolve(type: AdapterType): SkillAdapter {
    const adapter = this.adapters.get(type);
    if (!adapter) {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.ADAPTER_NOT_FOUND,
        `No adapter registered for type "${type}"`,
        { type },
      );
    }
    return adapter;
  }

  /**
   * 根据 Skill 解析对应的 Adapter（便捷方法）
   *
   * @throws EvalSkillsError 当 skill 的 adapterType 未注册时
   */
  resolveForSkill(skill: Skill): SkillAdapter {
    return this.resolve(skill.adapterType);
  }

  /**
   * 检查某类型是否已注册
   */
  has(type: string): boolean {
    return this.adapters.has(type);
  }

  /**
   * 获取所有已注册的 adapter 类型
   */
  registeredTypes(): string[] {
    return Array.from(this.adapters.keys());
  }
}
