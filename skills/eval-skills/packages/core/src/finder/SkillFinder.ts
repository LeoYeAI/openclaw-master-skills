import type { Skill } from "../types/index.js";
import { SkillStore } from "../registry/SkillStore.js";

/**
 * 技能发现搜索选项
 */
export interface FindOptions {
  /** 关键词搜索 */
  query?: string;
  /** 标签过滤（交集） */
  tags?: string[];
  /** Adapter 类型过滤 */
  adapterType?: string;
  /** 最低完成率 */
  minCompletion?: number;
  /** 返回数量限制，默认 20 */
  limit?: number;
}

/**
 * 技能发现搜索结果
 */
export interface FindResult {
  skills: Skill[];
  total: number;
}

/**
 * 获取 Skill 最高 completionRate（从 benchmarkResults 中取最大值）
 */
function getMaxCompletionRate(skill: Skill): number {
  const results = skill.metadata.benchmarkResults;
  if (!results || results.length === 0) {
    return 0;
  }
  return Math.max(...results.map((r) => r.completionRate));
}

/**
 * 计算关键词搜索匹配度评分
 * name 匹配权重最高，description 次之，tags 最低
 */
function computeSearchScore(skill: Skill, query: string): number {
  const lowerQuery = query.toLowerCase();
  let score = 0;

  if (skill.name.toLowerCase().includes(lowerQuery)) {
    score += 3;
  }
  if (skill.description.toLowerCase().includes(lowerQuery)) {
    score += 2;
  }
  if (skill.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))) {
    score += 1;
  }

  return score;
}

/**
 * 技能发现模块
 * 基于 SkillStore 提供多条件搜索和筛选能力
 */
export class SkillFinder {
  private store: SkillStore;

  constructor(store: SkillStore) {
    this.store = store;
  }

  /**
   * 根据选项查找技能
   *
   * 流程：
   * 1. 调用 SkillStore 的 search（有 query）或 list 获取候选
   * 2. 按 tags 交集过滤
   * 3. 按 adapterType 过滤
   * 4. 按 minCompletion 过滤
   * 5. 排序（有 query 按匹配度，否则按 completionRate 降序）
   * 6. 应用 limit
   */
  find(options: FindOptions = {}): FindResult {
    const { query, tags, adapterType, minCompletion, limit = 20 } = options;

    // Step 1: 获取候选列表
    let candidates: Skill[];
    if (query) {
      candidates = this.store.search(query);
    } else {
      candidates = this.store.list();
    }

    // Step 2: 按 tags 交集过滤（候选 skill 必须包含所有指定 tags）
    if (tags && tags.length > 0) {
      candidates = candidates.filter((skill) =>
        tags.every((tag) => skill.tags.includes(tag)),
      );
    }

    // Step 3: 按 adapterType 过滤
    if (adapterType) {
      candidates = candidates.filter(
        (skill) => skill.adapterType === adapterType,
      );
    }

    // Step 4: 按 minCompletion 过滤
    if (minCompletion !== undefined) {
      candidates = candidates.filter(
        (skill) => getMaxCompletionRate(skill) >= minCompletion,
      );
    }

    const total = candidates.length;

    // Step 5: 排序
    if (query) {
      // 有 query 时按搜索匹配度降序排列
      candidates.sort(
        (a, b) => computeSearchScore(b, query) - computeSearchScore(a, query),
      );
    } else {
      // 无 query 时按 completionRate 降序排列
      candidates.sort(
        (a, b) => getMaxCompletionRate(b) - getMaxCompletionRate(a),
      );
    }

    // Step 6: 应用 limit
    const skills = candidates.slice(0, limit);

    return { skills, total };
  }
}
