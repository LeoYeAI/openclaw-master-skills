import fs from "node:fs";
import path from "node:path";
import type { Skill, AdapterType } from "../types/index.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../errors.js";

export interface SkillListFilters {
  tag?: string;
  adapterType?: AdapterType;
}

/**
 * JSON 文件存储的 Skill 注册表
 * 内部使用 Map<string, Skill> 存储
 */
export class SkillStore {
  private skills: Map<string, Skill> = new Map();
  private skillPaths: Map<string, string> = new Map();
  private readonly strict: boolean;

  /**
   * @param options.strict 开启严格模式时，register 和 loadDir 会用 Zod 校验 Skill 结构
   */
  constructor(options?: { strict?: boolean }) {
    this.strict = options?.strict ?? false;
  }

  /**
   * 注册一个 Skill
   * @param sourcePath 来源文件路径
   */
  register(skill: Skill, sourcePath?: string): void {
    if (this.strict) {
      try {
        // 延迟导入避免循环依赖
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const { validateSkill } = require("../validation.js");
        validateSkill(skill);
      } catch (err) {
        throw new EvalSkillsError(
          EvalSkillsErrorCode.SKILL_SCHEMA_INVALID,
          `Invalid skill schema for "${skill.id ?? "(unknown)"}": ${(err as Error).message}`,
          { skillId: skill.id },
        );
      }
    }
    this.skills.set(skill.id, skill);
    if (sourcePath) {
        this.skillPaths.set(skill.id, sourcePath);
    }
  }

  /**
   * 按 ID 获取 Skill
   */
  get(id: string): Skill | undefined {
    return this.skills.get(id);
  }

  /**
   * 获取 Skill 的来源文件路径
   */
  getSourcePath(id: string): string | undefined {
    return this.skillPaths.get(id);
  }

  /**
   * 列出所有 Skill，支持 tag/adapter 过滤
   */
  list(filters?: SkillListFilters): Skill[] {
    let results = Array.from(this.skills.values());

    if (filters?.tag) {
      results = results.filter((s) => s.tags.includes(filters.tag!));
    }

    if (filters?.adapterType) {
      results = results.filter((s) => s.adapterType === filters.adapterType);
    }

    return results;
  }

  /**
   * 从目录递归批量加载 skill.json 文件
   */
  loadDir(dirPath: string): Skill[] {
    const loaded: Skill[] = [];
    const jsonFiles = this.findSkillJsonFiles(dirPath);

    for (const filePath of jsonFiles) {
      const content = fs.readFileSync(filePath, "utf-8");
      const skill: Skill = JSON.parse(content);
      
      // Set rootPath to the directory containing skill.json
      skill.rootPath = path.dirname(filePath);

      this.register(skill, filePath);
      loaded.push(skill);
    }

    return loaded;
  }

  /**
   * 按 ID 移除 Skill
   */
  remove(id: string): boolean {
    return this.skills.delete(id);
  }

  /**
   * 关键词搜索（name + description + tags），大小写不敏感
   */
  search(query: string): Skill[] {
    const lowerQuery = query.toLowerCase();

    return Array.from(this.skills.values()).filter((skill) => {
      const nameMatch = skill.name.toLowerCase().includes(lowerQuery);
      const descMatch = skill.description.toLowerCase().includes(lowerQuery);
      const tagsMatch = skill.tags.some((tag) =>
        tag.toLowerCase().includes(lowerQuery),
      );
      return nameMatch || descMatch || tagsMatch;
    });
  }

  /**
   * 清空所有 Skill
   */
  clear(): void {
    this.skills.clear();
  }

  /**
   * 返回已注册的 Skill 数量
   */
  count(): number {
    return this.skills.size;
  }

  /**
   * 递归查找目录下所有 skill.json 文件
   */
  private findSkillJsonFiles(dirPath: string): string[] {
    const results: string[] = [];

    if (!fs.existsSync(dirPath)) {
      return results;
    }

    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory()) {
        results.push(...this.findSkillJsonFiles(fullPath));
      } else if (entry.name === "skill.json") {
        results.push(fullPath);
      }
    }

    return results;
  }
}
