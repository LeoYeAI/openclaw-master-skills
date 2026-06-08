/**
 * Knowledge Graph Indexer - 双向索引系统
 * 构建概念→文献和文献→概念的双向索引
 * 支持按相关度、引用数、日期排序
 */

import type {
  KnowledgeGraphData,
  KnowledgeNode,
  PaperMetadata,
  LiteratureReference,
  LiteratureIndex,
  ConceptIndex
} from './graph';

/**
 * 论文查询选项
 */
export interface PaperQueryOptions {
  minRelevance?: number;
  sortBy?: 'relevance' | 'citations' | 'date';
  limit?: number;
  paperType?: 'review' | 'research' | 'all';
}

/**
 * 概念查询选项
 */
export interface ConceptQueryOptions {
  minRelevance?: number;
  sortBy?: 'relevance' | 'importance';
  limit?: number;
}

/**
 * 索引统计信息
 */
export interface IndexStatistics {
  totalConcepts: number;
  totalPapers: number;
  totalIndexEntries: number;
  avgPapersPerConcept: number;
  avgConceptsPerPaper: number;
  papersByType: { review: number; research: number };
}

/**
 * 带相关度的论文结果
 */
export interface PaperWithRelevance {
  paper: PaperMetadata;
  relevance: number;
  mentionType: string;
}

/**
 * 带相关度的概念结果
 */
export interface ConceptWithRelevance {
  concept: KnowledgeNode;
  relevance: number;
  mentionType: string;
}

export default class KnowledgeGraphIndexer {

  /**
   * 为图谱构建双向索引
   */
  buildIndex(graph: KnowledgeGraphData): KnowledgeGraphData {
    if (!graph.literatureIndex) {
      graph.literatureIndex = {
        papers: new Map(),
        paperToConcepts: new Map()
      };
    }
    if (!graph.conceptIndex) {
      graph.conceptIndex = {
        conceptToPapers: new Map()
      };
    }

    // 从节点的literatureReferences构建索引
    for (const node of graph.nodes) {
      if (!node.literatureReferences) continue;

      for (const ref of node.literatureReferences) {
        // 更新概念→论文索引
        const existingRefs = graph.conceptIndex.conceptToPapers.get(node.id) || [];
        if (!existingRefs.find(r => r.paperId === ref.paperId)) {
          existingRefs.push(ref);
          graph.conceptIndex.conceptToPapers.set(node.id, existingRefs);
        }

        // 更新论文→概念索引
        const existingConcepts = graph.literatureIndex.paperToConcepts.get(ref.paperId) || [];
        if (!existingConcepts.includes(node.id)) {
          existingConcepts.push(node.id);
          graph.literatureIndex.paperToConcepts.set(ref.paperId, existingConcepts);
        }
      }
    }

    return graph;
  }

  /**
   * 添加论文到索引
   */
  addPaperToIndex(
    graph: KnowledgeGraphData,
    conceptId: string,
    paper: PaperMetadata,
    reference: LiteratureReference
  ): void {
    if (!graph.literatureIndex) {
      graph.literatureIndex = { papers: new Map(), paperToConcepts: new Map() };
    }
    if (!graph.conceptIndex) {
      graph.conceptIndex = { conceptToPapers: new Map() };
    }

    // 存储论文元数据
    graph.literatureIndex.papers.set(paper.id, paper);

    // 更新概念→论文索引
    const refs = graph.conceptIndex.conceptToPapers.get(conceptId) || [];
    if (!refs.find(r => r.paperId === paper.id)) {
      refs.push(reference);
      graph.conceptIndex.conceptToPapers.set(conceptId, refs);
    }

    // 更新论文→概念索引
    const concepts = graph.literatureIndex.paperToConcepts.get(paper.id) || [];
    if (!concepts.includes(conceptId)) {
      concepts.push(conceptId);
      graph.literatureIndex.paperToConcepts.set(paper.id, concepts);
    }

    // 更新节点的literatureReferences
    const node = graph.nodes.find(n => n.id === conceptId);
    if (node) {
      if (!node.literatureReferences) node.literatureReferences = [];
      if (!node.literatureReferences.find(r => r.paperId === paper.id)) {
        node.literatureReferences.push(reference);
      }
      if (!node.keyPapers) node.keyPapers = [];
      if (!node.keyPapers.includes(paper.id)) {
        node.keyPapers.push(paper.id);
      }
    }
  }

  /**
   * 按概念查找论文
   */
  findPapersByConcept(
    graph: KnowledgeGraphData,
    conceptId: string,
    options: PaperQueryOptions = {}
  ): PaperWithRelevance[] {
    const {
      minRelevance = 0,
      sortBy = 'relevance',
      limit = 10,
      paperType = 'all'
    } = options;

    if (!graph.conceptIndex || !graph.literatureIndex) return [];

    const refs = graph.conceptIndex.conceptToPapers.get(conceptId) || [];
    let results: PaperWithRelevance[] = [];

    for (const ref of refs) {
      if (ref.relevance < minRelevance) continue;

      const paper = graph.literatureIndex.papers.get(ref.paperId);
      if (!paper) continue;
      if (paperType !== 'all' && paper.paperType !== paperType) continue;

      results.push({
        paper,
        relevance: ref.relevance,
        mentionType: ref.mentionType
      });
    }

    // 排序
    switch (sortBy) {
      case 'relevance':
        results.sort((a, b) => b.relevance - a.relevance);
        break;
      case 'citations':
        results.sort((a, b) => (b.paper.citations || 0) - (a.paper.citations || 0));
        break;
      case 'date':
        results.sort((a, b) =>
          new Date(b.paper.publishDate).getTime() - new Date(a.paper.publishDate).getTime()
        );
        break;
    }

    return results.slice(0, limit);
  }

  /**
   * 按论文查找概念
   */
  findConceptsByPaper(
    graph: KnowledgeGraphData,
    paperId: string,
    options: ConceptQueryOptions = {}
  ): ConceptWithRelevance[] {
    const { minRelevance = 0, sortBy = 'relevance', limit = 20 } = options;

    if (!graph.literatureIndex || !graph.conceptIndex) return [];

    const conceptIds = graph.literatureIndex.paperToConcepts.get(paperId) || [];
    let results: ConceptWithRelevance[] = [];

    for (const conceptId of conceptIds) {
      const node = graph.nodes.find(n => n.id === conceptId);
      if (!node) continue;

      // 找到该论文在该概念下的引用信息
      const refs = graph.conceptIndex.conceptToPapers.get(conceptId) || [];
      const ref = refs.find(r => r.paperId === paperId);
      const relevance = ref?.relevance || 0;

      if (relevance < minRelevance) continue;

      results.push({
        concept: node,
        relevance,
        mentionType: ref?.mentionType || 'related'
      });
    }

    // 排序
    switch (sortBy) {
      case 'relevance':
        results.sort((a, b) => b.relevance - a.relevance);
        break;
      case 'importance':
        results.sort((a, b) => b.concept.importance - a.concept.importance);
        break;
    }

    return results.slice(0, limit);
  }

  /**
   * 推荐论文（基于多个概念）
   */
  recommendPapers(
    graph: KnowledgeGraphData,
    conceptIds: string[],
    limit: number = 10
  ): PaperWithRelevance[] {
    if (!graph.conceptIndex || !graph.literatureIndex) return [];

    // 收集所有相关论文及其累计相关度
    const paperScores = new Map<string, { totalRelevance: number; matchedConcepts: number; mentionType: string }>();

    for (const conceptId of conceptIds) {
      const refs = graph.conceptIndex.conceptToPapers.get(conceptId) || [];
      for (const ref of refs) {
        const existing = paperScores.get(ref.paperId) || { totalRelevance: 0, matchedConcepts: 0, mentionType: ref.mentionType };
        existing.totalRelevance += ref.relevance;
        existing.matchedConcepts++;
        paperScores.set(ref.paperId, existing);
      }
    }

    // 构建结果，按综合评分排序
    const results: PaperWithRelevance[] = [];
    for (const [paperId, score] of paperScores) {
      const paper = graph.literatureIndex.papers.get(paperId);
      if (!paper) continue;

      // 综合评分 = 平均相关度 * 匹配概念比例
      const avgRelevance = score.totalRelevance / score.matchedConcepts;
      const coverageBonus = score.matchedConcepts / conceptIds.length;
      const compositeScore = avgRelevance * 0.6 + coverageBonus * 0.4;

      results.push({
        paper,
        relevance: Math.round(compositeScore * 100) / 100,
        mentionType: score.mentionType
      });
    }

    results.sort((a, b) => b.relevance - a.relevance);
    return results.slice(0, limit);
  }

  /**
   * 获取索引统计信息
   */
  getIndexStats(graph: KnowledgeGraphData): IndexStatistics {
    const totalConcepts = graph.nodes.length;
    let totalPapers = 0;
    let totalIndexEntries = 0;
    let reviewCount = 0;
    let researchCount = 0;

    if (graph.literatureIndex) {
      totalPapers = graph.literatureIndex.papers.size;
      for (const paper of graph.literatureIndex.papers.values()) {
        if (paper.paperType === 'review') reviewCount++;
        else researchCount++;
      }
      for (const concepts of graph.literatureIndex.paperToConcepts.values()) {
        totalIndexEntries += concepts.length;
      }
    }

    return {
      totalConcepts,
      totalPapers,
      totalIndexEntries,
      avgPapersPerConcept: totalConcepts > 0
        ? Math.round((totalIndexEntries / totalConcepts) * 10) / 10
        : 0,
      avgConceptsPerPaper: totalPapers > 0
        ? Math.round((totalIndexEntries / totalPapers) * 10) / 10
        : 0,
      papersByType: { review: reviewCount, research: researchCount }
    };
  }

  /**
   * 格式化统计信息
   */
  formatStats(stats: IndexStatistics): string {
    return `📊 图谱统计信息:
  概念数: ${stats.totalConcepts}
  文献数: ${stats.totalPapers} (综述: ${stats.papersByType.review}, 研究: ${stats.papersByType.research})
  索引条目: ${stats.totalIndexEntries}
  平均每概念关联论文: ${stats.avgPapersPerConcept}
  平均每论文关联概念: ${stats.avgConceptsPerPaper}`;
  }

  /**
   * 格式化概念查询结果
   */
  formatPaperResults(conceptLabel: string, results: PaperWithRelevance[]): string {
    const reviews = results.filter(r => r.paper.paperType === 'review');
    const research = results.filter(r => r.paper.paperType === 'research');

    const lines: string[] = [`🔍 "${conceptLabel}" 相关文献:\n`];

    if (reviews.length > 0) {
      lines.push(`📚 综述文献 (${reviews.length}篇):`);
      reviews.forEach((r, i) => {
        lines.push(`  ${i + 1}. ${r.paper.title} (相关度: ${(r.relevance * 100).toFixed(0)}%)`);
        lines.push(`     ${r.paper.url}`);
      });
      lines.push('');
    }

    if (research.length > 0) {
      lines.push(`📄 关键论文 (${research.length}篇):`);
      research.forEach((r, i) => {
        lines.push(`  ${i + 1}. ${r.paper.title} (相关度: ${(r.relevance * 100).toFixed(0)}%)`);
        if (r.paper.citations) {
          lines.push(`     引用: ${r.paper.citations} | ${r.paper.url}`);
        } else {
          lines.push(`     ${r.paper.url}`);
        }
      });
    }

    if (results.length === 0) {
      lines.push('  未找到相关文献');
    }

    return lines.join('\n');
  }
}
