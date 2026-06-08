/**
 * Review Detector - Type Definitions
 * 综述识别模块类型定义
 */

import type { SearchResult } from '../../literature-search/scripts/types';

/**
 * 综述类型
 */
export type ReviewType = 'survey' | 'systematic_review' | 'tutorial' | 'meta_analysis' | 'none';

/**
 * 综述识别结果
 */
export interface ReviewDetectionResult {
  /** 原始论文信息 */
  paper: SearchResult;
  /** 是否为综述 */
  isReview: boolean;
  /** 置信度 (0-1) */
  confidence: number;
  /** 综述类型 */
  reviewType: ReviewType;
  /** 判断依据说明（给用户看） */
  reasoning: string;
  /** 各维度评分详情 */
  scores: {
    /** 标题关键词得分 (0-1) */
    titleScore: number;
    /** 引用数得分 (0-1) */
    citationScore: number;
    /** 摘要模式得分 (0-1) */
    abstractScore: number;
    /** AI辅助判断得分 (0-1) */
    aiScore: number;
  };
}

/**
 * 综述识别选项
 */
export interface ReviewDetectionOptions {
  /** 是否启用AI辅助判断 */
  useAI?: boolean;
  /** 最小置信度阈值 */
  minConfidence?: number;
  /** 语言偏好 */
  language?: 'zh-CN' | 'en';
}

/**
 * 批量识别结果
 */
export interface BatchDetectionResult {
  /** 所有识别结果 */
  results: ReviewDetectionResult[];
  /** 识别为综述的论文 */
  reviews: ReviewDetectionResult[];
  /** 非综述论文 */
  nonReviews: ReviewDetectionResult[];
  /** 统计信息 */
  stats: {
    total: number;
    reviewCount: number;
    averageConfidence: number;
    byType: Record<ReviewType, number>;
  };
}

/**
 * 综述关键词配置
 */
export interface ReviewKeywordsConfig {
  /** 英文综述关键词（标题） */
  englishTitle: string[];
  /** 中文综述关键词（标题） */
  chineseTitle: string[];
  /** 英文综述关键词（摘要） */
  englishAbstract: string[];
  /** 中文综述关键词（摘要） */
  chineseAbstract: string[];
}
