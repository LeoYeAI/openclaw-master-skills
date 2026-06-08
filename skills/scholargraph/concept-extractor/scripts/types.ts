/**
 * Concept Extractor - Type Definitions
 * 概念提取模块类型定义
 */

/**
 * 概念类别
 */
export type ConceptCategory = 'foundation' | 'core' | 'advanced' | 'application';

/**
 * 提取的概念
 */
export interface ExtractedConcept {
  /** 概念ID */
  id: string;
  /** 概念名称 */
  name: string;
  /** 英文名 */
  nameEn?: string;
  /** 中文名 */
  nameZh?: string;
  /** 概念类别 */
  category: ConceptCategory;
  /** 重要性评分 (1-5) */
  importance: number;
  /** 概念定义 */
  definition: string;
  /** 在综述中的出现频率估计 */
  frequency: 'high' | 'medium' | 'low';
  /** 相关概念ID列表 */
  relatedConcepts: string[];
  /** 关键词/别名 */
  aliases: string[];
}

/**
 * 概念间关系
 */
export interface ConceptRelation {
  /** 源概念ID */
  sourceId: string;
  /** 目标概念ID */
  targetId: string;
  /** 关系类型 */
  relationType: 'prerequisite' | 'related' | 'derived' | 'component' | 'contrast';
  /** 关系强度 (0-1) */
  strength: number;
  /** 关系描述 */
  description?: string;
}

/**
 * 概念分类体系
 */
export interface ConceptTaxonomy {
  /** 基础概念 */
  foundation: ExtractedConcept[];
  /** 核心概念 */
  core: ExtractedConcept[];
  /** 进阶概念 */
  advanced: ExtractedConcept[];
  /** 应用概念 */
  application: ExtractedConcept[];
}

/**
 * 概念提取结果
 */
export interface ConceptExtractionResult {
  /** 提取来源论文标题 */
  sourceTitle: string;
  /** 提取来源URL */
  sourceUrl: string;
  /** 提取的所有概念 */
  concepts: ExtractedConcept[];
  /** 概念间关系 */
  relations: ConceptRelation[];
  /** 概念分类体系 */
  taxonomy: ConceptTaxonomy;
  /** 统计信息 */
  stats: {
    totalConcepts: number;
    byCategory: Record<ConceptCategory, number>;
    byImportance: Record<number, number>;
  };
}

/**
 * 概念提取选项
 */
export interface ConceptExtractionOptions {
  /** 提取概念数量范围 */
  minConcepts?: number;
  maxConcepts?: number;
  /** 最小重要性 */
  minImportance?: number;
  /** 语言偏好 */
  language?: 'zh-CN' | 'en';
  /** 是否提取关系 */
  extractRelations?: boolean;
}

/**
 * 合并后的概念（多综述去重后） */
export interface MergedConcept extends ExtractedConcept {
  /** 来源综述列表 */
  sources: string[];
  /** 合并后的综合重要性 */
  mergedImportance: number;
  /** 出现次数 */
  occurrenceCount: number;
}

/**
 * 概念合并结果
 */
export interface ConceptMergeResult {
  /** 合并后的概念列表 */
  concepts: MergedConcept[];
  /** 合并后的关系列表 */
  relations: ConceptRelation[];
  /** 合并统计 */
  stats: {
    totalBefore: number;
    totalAfter: number;
    duplicatesRemoved: number;
    sourcesCount: number;
  };
}
