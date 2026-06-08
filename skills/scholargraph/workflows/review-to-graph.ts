/**
 * Review-to-Graph Workflow - 端到端工作流
 * 从综述搜索到知识图谱构建的完整流程
 *
 * 流程:
 * 1. 搜索综述
 * 2. 识别综述并标记置信度
 * 3. 用户确认综述列表
 * 4. 分析确认的综述
 * 5. 提取概念
 * 6. 去重合并概念
 * 7. 构建知识图谱
 * 8. 搜索并关联关键论文
 * 9. 构建双向索引
 * 10. 持久化到SQLite
 */

import LiteratureSearch from '../literature-search/scripts/search';
import ReviewDetector from '../review-detector/scripts/detect';
import PaperAnalyzer from '../paper-analyzer/scripts/analyze';
import ConceptExtractor from '../concept-extractor/scripts/extract';
import KnowledgeGraphBuilder from '../knowledge-graph/scripts/graph';
import KnowledgeGraphIndexer from '../knowledge-graph/scripts/indexer';
import GraphEnricher from '../knowledge-graph/scripts/enricher';
import GraphStorage from '../knowledge-graph/scripts/storage';
import type { SearchResult } from '../literature-search/scripts/types';
import type { ReviewDetectionResult } from '../review-detector/scripts/types';
import type { ConceptExtractionResult, ExtractedConcept } from '../concept-extractor/scripts/types';
import type { KnowledgeGraphData } from '../knowledge-graph/scripts/graph';
import { getErrorMessage } from '../shared/errors';

/**
 * 工作流选项
 */
export interface WorkflowOptions {
  /** 搜索结果数量 */
  searchLimit?: number;
  /** 是否丰富关键论文 */
  enrichWithPapers?: boolean;
  /** 每个概念的关键论文数 */
  papersPerConcept?: number;
  /** 输出图谱名称 */
  graphName?: string;
  /** 数据库路径 */
  dbPath?: string;
  /** 是否自动确认（不需要交互） */
  autoConfirm?: boolean;
  /** 最小综述置信度 */
  minReviewConfidence?: number;
}

/**
 * 工作流结果
 */
export interface WorkflowResult {
  /** 图谱名称 */
  graphName: string;
  /** 处理的综述数 */
  reviewCount: number;
  /** 提取的概念数 */
  conceptCount: number;
  /** 关联的论文数 */
  paperCount: number;
  /** 关系数 */
  relationCount: number;
  /** 图谱数据 */
  graph: KnowledgeGraphData;
}

export default class ReviewToGraphWorkflow {
  private searcher: LiteratureSearch;
  private detector: ReviewDetector;
  private analyzer: PaperAnalyzer;
  private extractor: ConceptExtractor;
  private graphBuilder: KnowledgeGraphBuilder;
  private indexer: KnowledgeGraphIndexer;
  private enricher: GraphEnricher;

  constructor() {
    this.searcher = new LiteratureSearch();
    this.detector = new ReviewDetector();
    this.analyzer = new PaperAnalyzer();
    this.extractor = new ConceptExtractor();
    this.graphBuilder = new KnowledgeGraphBuilder();
    this.indexer = new KnowledgeGraphIndexer();
    this.enricher = new GraphEnricher();
  }

  /**
   * 初始化所有模块
   */
  async initialize(): Promise<void> {
    await Promise.all([
      this.searcher.initialize(),
      this.detector.initialize(),
      this.analyzer.initialize(),
      this.extractor.initialize(),
      this.graphBuilder.initialize(),
      this.enricher.initialize()
    ]);
  }

  /**
   * 步骤1: 搜索综述
   */
  async searchReviews(
    query: string,
    limit: number = 10
  ): Promise<ReviewDetectionResult[]> {
    console.log(`\n🔍 搜索 "${query}" 相关综述...\n`);

    // 添加综述关键词增强搜索
    const reviewQuery = `${query} survey OR review OR overview`;

    const searchResponse = await this.searcher.search(reviewQuery, {
      limit: limit * 2, // 多搜索一些以备过滤
      sources: ['arxiv', 'semantic_scholar'],
      sortBy: 'citations'
    });

    console.log(`  📚 搜索到 ${searchResponse.results.length} 篇论文`);

    // 识别综述
    const detection = await this.detector.filterReviews(searchResponse.results, {
      useAI: true,
      minConfidence: 0.3
    });

    console.log(`  ✅ 识别到 ${detection.reviews.length} 篇综述`);
    console.log(this.detector.formatResults(detection.reviews));

    return detection.reviews;
  }

  /**
   * 步骤2: 用户确认综述列表
   */
  async confirmReviews(
    candidates: ReviewDetectionResult[],
    autoConfirm: boolean = false,
    minConfidence: number = 0.5
  ): Promise<SearchResult[]> {
    if (autoConfirm) {
      // 自动模式：选择置信度高于阈值的综述
      const selected = candidates
        .filter(c => c.confidence >= minConfidence)
        .map(c => c.paper);
      console.log(`\n🤖 自动选择 ${selected.length} 篇综述 (置信度 >= ${(minConfidence * 100).toFixed(0)}%)`);
      return selected;
    }

    // 交互模式
    console.log('\n📋 识别到以下候选综述:\n');
    candidates.forEach((c, i) => {
      const confidence = (c.confidence * 100).toFixed(0);
      const icon = c.confidence > 0.7 ? '✅' : c.confidence > 0.4 ? '⚠️' : '❓';
      console.log(`${i + 1}. ${icon} ${c.paper.title} (置信度: ${confidence}%)`);
      console.log(`   类型: ${c.reviewType} | ${c.reasoning}\n`);
    });

    const readline = await import('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const answer = await new Promise<string>((resolve) => {
      rl.question('请选择要处理的综述（逗号分隔，如 1,3,5；输入 all 选择全部）: ', (ans) => {
        rl.close();
        resolve(ans);
      });
    });

    if (answer.toLowerCase() === 'all') {
      return candidates.map(c => c.paper);
    }

    const indices = answer.split(',')
      .map(n => parseInt(n.trim()) - 1)
      .filter(i => i >= 0 && i < candidates.length);

    return indices.map(i => candidates[i].paper);
  }

  /**
   * 步骤3-6: 分析综述并提取概念
   */
  async analyzeAndExtract(reviews: SearchResult[]): Promise<{
    concepts: ExtractedConcept[];
    relations: ConceptExtractionResult[];
  }> {
    console.log(`\n📄 分析 ${reviews.length} 篇综述并提取概念...\n`);

    const allExtractions: ConceptExtractionResult[] = [];

    for (const review of reviews) {
      try {
        console.log(`  分析: ${review.title}...`);

        // 分析论文
        const analysis = await this.analyzer.analyze({
          url: review.url,
          mode: 'standard'
        });

        // 提取概念
        const extraction = await this.extractor.extractFromReview(analysis, {
          minConcepts: 10,
          maxConcepts: 25,
          extractRelations: true
        });

        console.log(`    ✓ 提取 ${extraction.concepts.length} 个概念`);
        allExtractions.push(extraction);
      } catch (error) {
        console.error(`    ✗ 分析失败: ${getErrorMessage(error)}`);
      }
    }

    // 合并去重
    if (allExtractions.length > 1) {
      console.log('\n🔄 合并去重概念...');
      const merged = this.extractor.mergeConcepts(allExtractions);
      console.log(`  合并前: ${merged.stats.totalBefore} | 合并后: ${merged.stats.totalAfter} | 去除重复: ${merged.stats.duplicatesRemoved}`);
      return { concepts: merged.concepts, relations: allExtractions };
    } else if (allExtractions.length === 1) {
      return { concepts: allExtractions[0].concepts, relations: allExtractions };
    }

    return { concepts: [], relations: [] };
  }

  /**
   * 步骤7-9: 构建图谱、丰富论文、建索引
   */
  async buildGraph(
    concepts: ExtractedConcept[],
    reviews: SearchResult[],
    options: WorkflowOptions = {}
  ): Promise<KnowledgeGraphData> {
    const { enrichWithPapers = true, papersPerConcept = 3, graphName = 'unnamed' } = options;

    // 从概念构建知识图谱
    console.log('\n🔗 构建知识图谱...');
    const conceptNames = concepts.map(c => c.name);
    const graph = await this.graphBuilder.build(conceptNames);

    // 用概念的详细信息更新节点
    for (const node of graph.nodes) {
      const concept = concepts.find(c => c.name === node.label);
      if (concept) {
        node.description = concept.definition;
        node.importance = concept.importance;
        node.metadata = {
          extractedFrom: reviews.map(r => r.title),
          lastUpdated: new Date().toISOString(),
          confidence: concept.importance / 5
        };
      }
    }

    // 初始化索引结构
    graph.literatureIndex = { papers: new Map(), paperToConcepts: new Map() };
    graph.conceptIndex = { conceptToPapers: new Map() };
    graph.graphMetadata = {
      name: graphName,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      sourceReviews: reviews.map(r => r.title),
      totalConcepts: concepts.length,
      totalPapers: 0,
      totalRelations: graph.edges.length
    };

    // 添加综述论文到图谱
    console.log('\n📚 关联综述论文...');
    for (const review of reviews) {
      const conceptIds = graph.nodes.map(n => n.id);
      this.enricher.addReviewToGraph(graph, review, conceptIds);
    }

    // 搜索并关联关键论文
    if (enrichWithPapers) {
      await this.enricher.enrichWithKeyPapers(graph, concepts, {
        papersPerConcept,
        filterReviews: true,
        minRelevance: 0.3
      });
    }

    // 构建双向索引
    console.log('\n📑 构建双向索引...');
    this.indexer.buildIndex(graph);

    // 更新统计
    graph.graphMetadata.totalPapers = graph.literatureIndex.papers.size;

    const stats = this.indexer.getIndexStats(graph);
    console.log(this.indexer.formatStats(stats));

    return graph;
  }

  /**
   * 步骤10: 持久化存储
   */
  saveGraph(graph: KnowledgeGraphData, name: string, dbPath?: string): void {
    console.log(`\n💾 保存图谱 "${name}" 到数据库...`);

    const storage = new GraphStorage(dbPath);
    try {
      storage.saveGraph(graph, name);
      console.log('  ✅ 保存成功');
    } finally {
      storage.close();
    }
  }

  /**
   * 完整工作流
   */
  async run(query: string, options: WorkflowOptions = {}): Promise<WorkflowResult> {
    const {
      searchLimit = 10,
      graphName = query.replace(/\s+/g, '-').toLowerCase(),
      autoConfirm = false,
      minReviewConfidence = 0.5,
      dbPath
    } = options;

    await this.initialize();

    // 1. 搜索综述
    const reviewCandidates = await this.searchReviews(query, searchLimit);

    if (reviewCandidates.length === 0) {
      console.log('\n⚠️ 未找到综述论文。');
      throw new Error('No review papers found');
    }

    // 2. 确认综述列表
    const confirmedReviews = await this.confirmReviews(
      reviewCandidates, autoConfirm, minReviewConfidence
    );

    if (confirmedReviews.length === 0) {
      console.log('\n⚠️ 未选择任何综述。');
      throw new Error('No reviews selected');
    }

    // 3-6. 分析并提取概念
    const { concepts } = await this.analyzeAndExtract(confirmedReviews);

    if (concepts.length === 0) {
      console.log('\n⚠️ 未能提取到概念。');
      throw new Error('No concepts extracted');
    }

    // 7-9. 构建图谱
    const graph = await this.buildGraph(concepts, confirmedReviews, options);

    // 10. 保存
    this.saveGraph(graph, graphName, dbPath);

    console.log(`\n✅ 知识图谱 "${graphName}" 构建完成！`);

    return {
      graphName,
      reviewCount: confirmedReviews.length,
      conceptCount: concepts.length,
      paperCount: graph.literatureIndex?.papers.size || 0,
      relationCount: graph.edges.length,
      graph
    };
  }

  /**
   * 从单个综述URL构建图谱
   */
  async runFromUrl(
    reviewUrl: string,
    options: WorkflowOptions = {}
  ): Promise<WorkflowResult> {
    const { graphName = 'review-graph', dbPath } = options;

    await this.initialize();

    // 直接分析该URL
    const review: SearchResult = {
      id: reviewUrl,
      title: '',
      authors: [],
      abstract: '',
      publishDate: '',
      source: 'direct',
      url: reviewUrl
    };

    console.log(`\n📄 分析综述: ${reviewUrl}\n`);

    const analysis = await this.analyzer.analyze({
      url: reviewUrl,
      mode: 'deep'
    });

    review.title = analysis.metadata.title;
    review.authors = analysis.metadata.authors;
    review.abstract = analysis.abstract;

    // 提取概念
    const extraction = await this.extractor.extractFromReview(analysis, {
      minConcepts: 15,
      maxConcepts: 30,
      extractRelations: true
    });

    console.log(`  ✓ 提取 ${extraction.concepts.length} 个概念`);

    // 构建图谱
    const graph = await this.buildGraph(extraction.concepts, [review], options);

    // 保存
    this.saveGraph(graph, graphName, dbPath);

    console.log(`\n✅ 知识图谱 "${graphName}" 构建完成！`);

    return {
      graphName,
      reviewCount: 1,
      conceptCount: extraction.concepts.length,
      paperCount: graph.literatureIndex?.papers.size || 0,
      relationCount: graph.edges.length,
      graph
    };
  }
}
