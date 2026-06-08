/**
 * Review Detector - 综述识别模块
 * 多维度评分识别综述论文，支持中英文
 *
 * 评分维度:
 * - 标题关键词 (30%)
 * - 引用数 (25%)
 * - 摘要模式 (25%)
 * - AI辅助判断 (20%)
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { extractJson } from '../../shared/utils';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';
import type { SearchResult } from '../../literature-search/scripts/types';
import type {
  ReviewDetectionResult,
  ReviewDetectionOptions,
  BatchDetectionResult,
  ReviewType,
  ReviewKeywordsConfig
} from './types';

/** 综述关键词配置 */
const REVIEW_KEYWORDS: ReviewKeywordsConfig = {
  englishTitle: [
    'survey', 'review', 'overview', 'tutorial', 'comprehensive study',
    'state of the art', 'state-of-the-art', 'systematic review',
    'meta-analysis', 'meta analysis', 'literature review',
    'comparative study', 'taxonomy', 'roadmap', 'landscape',
    'benchmark', 'position paper', 'retrospective', 'progress',
    'trends in', 'advances in', 'recent advances'
  ],
  chineseTitle: [
    '综述', '调查', '概述', '回顾', '进展',
    '研究综述', '文献综述', '系统综述', '元分析',
    '前沿', '发展趋势', '研究进展', '技术综述',
    '全面调查', '比较研究', '分类体系'
  ],
  englishAbstract: [
    'this survey', 'this review', 'we survey', 'we review',
    'comprehensive overview', 'systematic review', 'in this survey',
    'this paper surveys', 'this paper reviews', 'provide an overview',
    'extensive survey', 'thorough review', 'we provide a comprehensive',
    'categorize', 'taxonomy', 'classify existing', 'summarize existing',
    'compare existing', 'literature review', 'body of work',
    'existing approaches', 'existing methods', 'prior work',
    'open challenges', 'future directions', 'research directions'
  ],
  chineseAbstract: [
    '本文综述', '本文概述', '本文回顾', '本综述',
    '全面概述', '系统回顾', '对现有', '分类总结',
    '研究现状', '发展趋势', '技术挑战', '未来方向',
    '文献调研', '梳理了', '归纳了', '总结了现有'
  ]
};

export default class ReviewDetector {
  private ai: AIProvider | null = null;

  async initialize(): Promise<void> {
    if (!this.ai) {
      try {
        this.ai = await createAIProvider();
      } catch (error) {
        throw new ApiInitializationError(
          `Failed to initialize AI provider: ${getErrorMessage(error)}`,
          error instanceof Error ? error : undefined
        );
      }
    }
  }

  /**
   * 检测单篇论文是否为综述
   */
  async detectReview(
    paper: SearchResult,
    options: ReviewDetectionOptions = {}
  ): Promise<ReviewDetectionResult> {
    const { useAI = true, minConfidence = 0.3 } = options;

    // 1. 标题关键词评分 (30%)
    const titleScore = this.scoreTitleKeywords(paper.title);

    // 2. 引用数评分 (25%)
    const citationScore = this.scoreCitations(paper.citations);

    // 3. 摘要模式评分 (25%)
    const abstractScore = this.scoreAbstractPatterns(paper.abstract);

    // 4. AI辅助判断 (20%)
    let aiScore = 0;
    if (useAI && (titleScore + abstractScore > 0.3)) {
      try {
        await this.initialize();
        aiScore = await this.scoreWithAI(paper);
      } catch {
        aiScore = 0;
      }
    }

    // 加权计算总分
    const confidence =
      titleScore * 0.30 +
      citationScore * 0.25 +
      abstractScore * 0.25 +
      aiScore * 0.20;

    const isReview = confidence >= minConfidence;
    const reviewType = this.determineReviewType(paper, titleScore, abstractScore);
    const reasoning = this.generateReasoning(paper, { titleScore, citationScore, abstractScore, aiScore });

    return {
      paper,
      isReview,
      confidence: Math.round(confidence * 100) / 100,
      reviewType: isReview ? reviewType : 'none',
      reasoning,
      scores: { titleScore, citationScore, abstractScore, aiScore }
    };
  }

  /**
   * 批量检测并过滤综述
   */
  async filterReviews(
    papers: SearchResult[],
    options: ReviewDetectionOptions = {}
  ): Promise<BatchDetectionResult> {
    const results: ReviewDetectionResult[] = [];

    for (const paper of papers) {
      const result = await this.detectReview(paper, options);
      results.push(result);
    }

    // 按置信度排序
    results.sort((a, b) => b.confidence - a.confidence);

    const reviews = results.filter(r => r.isReview);
    const nonReviews = results.filter(r => !r.isReview);

    const byType: Record<ReviewType, number> = {
      survey: 0, systematic_review: 0, tutorial: 0, meta_analysis: 0, none: 0
    };
    for (const r of results) {
      byType[r.reviewType]++;
    }

    return {
      results,
      reviews,
      nonReviews,
      stats: {
        total: results.length,
        reviewCount: reviews.length,
        averageConfidence: reviews.length > 0
          ? reviews.reduce((sum, r) => sum + r.confidence, 0) / reviews.length
          : 0,
        byType
      }
    };
  }

  /**
   * 标题关键词评分
   */
  private scoreTitleKeywords(title: string): number {
    const lowerTitle = title.toLowerCase();
    let maxScore = 0;

    // 英文关键词匹配
    for (const keyword of REVIEW_KEYWORDS.englishTitle) {
      if (lowerTitle.includes(keyword.toLowerCase())) {
        // 强信号关键词得分更高
        const strongKeywords = ['survey', 'review', 'systematic review', 'meta-analysis', 'tutorial'];
        const score = strongKeywords.includes(keyword.toLowerCase()) ? 1.0 : 0.7;
        maxScore = Math.max(maxScore, score);
      }
    }

    // 中文关键词匹配
    for (const keyword of REVIEW_KEYWORDS.chineseTitle) {
      if (title.includes(keyword)) {
        const strongKeywords = ['综述', '调查', '系统综述', '元分析'];
        const score = strongKeywords.includes(keyword) ? 1.0 : 0.7;
        maxScore = Math.max(maxScore, score);
      }
    }

    return maxScore;
  }

  /**
   * 引用数评分
   */
  private scoreCitations(citations?: number): number {
    if (citations === undefined || citations === null) return 0.3; // 无数据给中性分

    if (citations >= 500) return 1.0;
    if (citations >= 200) return 0.8;
    if (citations >= 100) return 0.6;
    if (citations >= 50) return 0.4;
    if (citations >= 20) return 0.2;
    return 0.1;
  }

  /**
   * 摘要模式评分
   */
  private scoreAbstractPatterns(abstract: string): number {
    if (!abstract) return 0;

    const lowerAbstract = abstract.toLowerCase();
    let matchCount = 0;

    // 英文摘要模式匹配
    for (const pattern of REVIEW_KEYWORDS.englishAbstract) {
      if (lowerAbstract.includes(pattern.toLowerCase())) {
        matchCount++;
      }
    }

    // 中文摘要模式匹配
    for (const pattern of REVIEW_KEYWORDS.chineseAbstract) {
      if (abstract.includes(pattern)) {
        matchCount++;
      }
    }

    // 根据匹配数量计算得分
    if (matchCount >= 5) return 1.0;
    if (matchCount >= 3) return 0.8;
    if (matchCount >= 2) return 0.6;
    if (matchCount >= 1) return 0.4;
    return 0;
  }

  /**
   * AI辅助评分
   */
  private async scoreWithAI(paper: SearchResult): Promise<number> {
    const prompt = `判断以下论文是否为综述(survey/review)论文。

标题: ${paper.title}
摘要: ${(paper.abstract || '').substring(0, 500)}

请返回JSON格式:
{
  "isReview": true/false,
  "confidence": 0.0-1.0,
  "reviewType": "survey" | "systematic_review" | "tutorial" | "meta_analysis" | "none",
  "reason": "简短判断依据"
}`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是学术论文分类专家，擅长识别综述论文。只返回JSON。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.1 });

    const result = extractJson<{
      isReview?: boolean;
      confidence?: number;
      reviewType?: string;
      reason?: string;
    }>(responseText);

    if (result.success && result.data) {
      return result.data.confidence || (result.data.isReview ? 0.8 : 0.2);
    }

    return 0;
  }

  /**
   * 确定综述类型
   */
  private determineReviewType(
    paper: SearchResult,
    titleScore: number,
    abstractScore: number
  ): ReviewType {
    const lowerTitle = paper.title.toLowerCase();
    const text = `${lowerTitle} ${(paper.abstract || '').toLowerCase()}`;

    if (text.includes('meta-analysis') || text.includes('meta analysis') || text.includes('元分析')) {
      return 'meta_analysis';
    }
    if (text.includes('systematic review') || text.includes('系统综述')) {
      return 'systematic_review';
    }
    if (text.includes('tutorial') || text.includes('教程')) {
      return 'tutorial';
    }
    if (titleScore > 0 || abstractScore > 0.3) {
      return 'survey';
    }
    return 'none';
  }

  /**
   * 生成人类可读的判断依据
   */
  private generateReasoning(
    paper: SearchResult,
    scores: { titleScore: number; citationScore: number; abstractScore: number; aiScore: number }
  ): string {
    const reasons: string[] = [];

    if (scores.titleScore >= 0.7) {
      reasons.push('标题包含明显的综述关键词');
    } else if (scores.titleScore > 0) {
      reasons.push('标题包含可能的综述关键词');
    }

    if (scores.citationScore >= 0.8) {
      reasons.push(`高引用数(${paper.citations || '未知'}), 综述论文通常被广泛引用`);
    }

    if (scores.abstractScore >= 0.6) {
      reasons.push('摘要包含多个综述特征表述');
    } else if (scores.abstractScore > 0) {
      reasons.push('摘要包含部分综述特征表述');
    }

    if (scores.aiScore >= 0.7) {
      reasons.push('AI判断为综述论文');
    }

    if (reasons.length === 0) {
      reasons.push('未发现明显的综述特征');
    }

    return reasons.join('; ');
  }

  /**
   * 格式化显示检测结果
   */
  formatResults(results: ReviewDetectionResult[]): string {
    const lines: string[] = ['📋 综述识别结果:\n'];

    results.forEach((r, i) => {
      const confidence = (r.confidence * 100).toFixed(0);
      const icon = r.confidence > 0.7 ? '✅' : r.confidence > 0.4 ? '⚠️' : '❓';
      lines.push(`${i + 1}. ${icon} ${r.paper.title}`);
      lines.push(`   置信度: ${confidence}% | 类型: ${r.reviewType} | 来源: ${r.paper.source}`);
      lines.push(`   依据: ${r.reasoning}`);
      if (r.paper.url) {
        lines.push(`   URL: ${r.paper.url}`);
      }
      lines.push('');
    });

    return lines.join('\n');
  }
}
