/**
 * Graph Enricher - 图谱丰富模块
 * 搜索并关联关键论文到知识图谱中的概念
 */

import LiteratureSearch from '../../literature-search/scripts/search';
import ReviewDetector from '../../review-detector/scripts/detect';
import KnowledgeGraphIndexer from './indexer';
import type { SearchResult } from '../../literature-search/scripts/types';
import type { ExtractedConcept } from '../../concept-extractor/scripts/types';
import type {
  KnowledgeGraphData,
  PaperMetadata,
  LiteratureReference
} from './graph';

/**
 * 丰富选项
 */
export interface EnrichOptions {
  /** 每个概念搜索的论文数 */
  papersPerConcept?: number;
  /** 最小引用数过滤 */
  minCitations?: number;
  /** 最小相关度阈值 */
  minRelevance?: number;
  /** 是否过滤掉综述 */
  filterReviews?: boolean;
  /** 搜索数据源 */
  sources?: ('arxiv' | 'semantic_scholar' | 'web')[];
}

export default class GraphEnricher {
  private searcher: LiteratureSearch;
  private detector: ReviewDetector;
  private indexer: KnowledgeGraphIndexer;

  constructor() {
    this.searcher = new LiteratureSearch();
    this.detector = new ReviewDetector();
    this.indexer = new KnowledgeGraphIndexer();
  }

  async initialize(): Promise<void> {
    await this.searcher.initialize();
    // detector初始化延迟到需要AI判断时
  }

  /**
   * 为图谱中的概念搜索并关联关键论文
   */
  async enrichWithKeyPapers(
    graph: KnowledgeGraphData,
    concepts: ExtractedConcept[],
    options: EnrichOptions = {}
  ): Promise<KnowledgeGraphData> {
    const {
      papersPerConcept = 5,
      minCitations = 0,
      minRelevance = 0.3,
      filterReviews = true,
      sources = ['arxiv', 'semantic_scholar']
    } = options;

    console.log('\n🔍 搜索关键论文...');

    let totalAssociated = 0;

    for (const concept of concepts) {
      try {
        // 搜索论文
        const searchResults = await this.searcher.search(concept.name, {
          limit: papersPerConcept * 2, // 多搜索一些以备过滤
          sources,
          sortBy: 'citations',
          filters: { minCitations }
        });

        let candidatePapers = searchResults.results;

        // 过滤综述（只保留研究论文）
        if (filterReviews) {
          candidatePapers = await this.filterOutReviews(candidatePapers);
        }

        // 取前N篇
        const keyPapers = candidatePapers.slice(0, papersPerConcept);

        // 找到图谱中对应的节点
        const node = graph.nodes.find(n =>
          n.label === concept.name ||
          n.label === concept.nameEn ||
          n.label === concept.nameZh
        );

        if (!node) continue;

        let conceptAssociated = 0;

        for (const paper of keyPapers) {
          const relevance = this.calculateRelevance(paper, concept);
          if (relevance < minRelevance) continue;

          const paperMetadata: PaperMetadata = {
            id: paper.id,
            title: paper.title,
            authors: paper.authors,
            abstract: paper.abstract,
            publishDate: paper.publishDate,
            url: paper.url,
            pdfUrl: paper.pdfUrl,
            citations: paper.citations,
            paperType: 'research',
            keywords: paper.keywords || []
          };

          const reference: LiteratureReference = {
            paperId: paper.id,
            title: paper.title,
            relevance,
            mentionType: this.determineMentionType(concept, paper),
            contexts: []
          };

          this.indexer.addPaperToIndex(graph, node.id, paperMetadata, reference);
          conceptAssociated++;
          totalAssociated++;
        }

        console.log(`  ✓ ${concept.name}: 关联 ${conceptAssociated} 篇关键论文`);
      } catch (error) {
        console.error(`  ✗ ${concept.name}: 搜索失败 - ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    console.log(`\n📊 共关联 ${totalAssociated} 篇关键论文`);

    // 重建索引
    this.indexer.buildIndex(graph);

    return graph;
  }

  /**
   * 添加综述论文到图谱
   */
  addReviewToGraph(
    graph: KnowledgeGraphData,
    review: SearchResult,
    relatedConceptIds: string[]
  ): void {
    const paperMetadata: PaperMetadata = {
      id: review.id,
      title: review.title,
      authors: review.authors,
      abstract: review.abstract,
      publishDate: review.publishDate,
      url: review.url,
      pdfUrl: review.pdfUrl,
      citations: review.citations,
      paperType: 'review',
      keywords: review.keywords || []
    };

    for (const conceptId of relatedConceptIds) {
      const reference: LiteratureReference = {
        paperId: review.id,
        title: review.title,
        relevance: 0.9, // 综述与其提取的概念高度相关
        mentionType: 'foundational',
        contexts: []
      };

      this.indexer.addPaperToIndex(graph, conceptId, paperMetadata, reference);
    }
  }

  /**
   * 过滤掉综述论文
   */
  private async filterOutReviews(papers: SearchResult[]): Promise<SearchResult[]> {
    const result: SearchResult[] = [];

    for (const paper of papers) {
      // 快速启发式检测（不使用AI，速度更快）
      const detection = await this.detector.detectReview(paper, { useAI: false });
      if (!detection.isReview || detection.confidence < 0.5) {
        result.push(paper);
      }
    }

    return result;
  }

  /**
   * 计算论文与概念的相关度
   */
  private calculateRelevance(paper: SearchResult, concept: ExtractedConcept): number {
    let score = 0;

    const titleLower = paper.title.toLowerCase();
    const abstractLower = (paper.abstract || '').toLowerCase();
    const conceptLower = concept.name.toLowerCase();

    // 标题包含概念名 - 高相关
    if (titleLower.includes(conceptLower)) {
      score += 0.4;
    }

    // 摘要包含概念名
    if (abstractLower.includes(conceptLower)) {
      score += 0.2;
    }

    // 检查别名匹配
    for (const alias of concept.aliases) {
      const aliasLower = alias.toLowerCase();
      if (titleLower.includes(aliasLower)) {
        score += 0.2;
        break;
      }
      if (abstractLower.includes(aliasLower)) {
        score += 0.1;
        break;
      }
    }

    // 引用数加分
    if (paper.citations) {
      if (paper.citations >= 500) score += 0.2;
      else if (paper.citations >= 100) score += 0.15;
      else if (paper.citations >= 50) score += 0.1;
      else if (paper.citations >= 10) score += 0.05;
    }

    return Math.min(1, Math.round(score * 100) / 100);
  }

  /**
   * 确定引用类型
   */
  private determineMentionType(
    concept: ExtractedConcept,
    paper: SearchResult
  ): 'foundational' | 'methodological' | 'application' {
    const titleLower = paper.title.toLowerCase();
    const abstractLower = (paper.abstract || '').toLowerCase();
    const text = `${titleLower} ${abstractLower}`;

    // 方法论相关
    const methodKeywords = ['method', 'algorithm', 'approach', 'technique', 'framework', 'architecture',
      '方法', '算法', '技术', '框架', '架构'];
    if (methodKeywords.some(k => text.includes(k))) {
      return 'methodological';
    }

    // 应用相关
    const appKeywords = ['application', 'applied', 'use case', 'deploy', 'system',
      '应用', '部署', '系统', '实践'];
    if (appKeywords.some(k => text.includes(k))) {
      return 'application';
    }

    return 'foundational';
  }
}
