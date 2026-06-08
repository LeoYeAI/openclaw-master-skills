/**
 * Literature Search - Core Module
 * 文献检索核心模块
 *
 * 提供多源文献检索能力，使用适配器注册表模式：
 * - arXiv, Semantic Scholar, Web (原有)
 * - OpenAlex, PubMed, CrossRef, DBLP (免费源)
 * - IEEE, CORE, Unpaywall, Google Scholar (需 API Key)
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { normalizeTitle, withTimeout } from '../../shared/utils';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';
import type { SearchSource } from '../../shared/types';
import type { SearchOptions, SearchResult, SearchResponse } from './types';

import { SearchSourceRegistry } from './adapters/registry';
import { ArxivAdapter } from './adapters/arxiv-adapter';
import { SemanticScholarAdapter } from './adapters/semantic-scholar-adapter';
import { WebAdapter } from './adapters/web-adapter';
import { OpenAlexAdapter } from './adapters/openalex-adapter';
import { PubMedAdapter } from './adapters/pubmed-adapter';
import { CrossRefAdapter } from './adapters/crossref-adapter';
import { DblpAdapter } from './adapters/dblp-adapter';
import { IeeeAdapter } from './adapters/ieee-adapter';
import { CoreAdapter } from './adapters/core-adapter';
import { UnpaywallAdapter } from './adapters/unpaywall-adapter';
import { GoogleScholarAdapter } from './adapters/google-scholar-adapter';
import { ComplementarySearchStrategy } from './search-strategy';

// 默认超时时间
const DEFAULT_TIMEOUT_MS = 30000;

export default class LiteratureSearch {
  private ai: AIProvider | null = null;
  private registry: SearchSourceRegistry;
  private strategy: ComplementarySearchStrategy;
  private webAdapter: WebAdapter;

  constructor() {
    this.registry = new SearchSourceRegistry();
    this.strategy = new ComplementarySearchStrategy();
    this.webAdapter = new WebAdapter();

    // Register all adapters
    this.registry.register(new ArxivAdapter());
    this.registry.register(new SemanticScholarAdapter());
    this.registry.register(this.webAdapter);
    this.registry.register(new OpenAlexAdapter());
    this.registry.register(new PubMedAdapter());
    this.registry.register(new CrossRefAdapter());
    this.registry.register(new DblpAdapter());
    this.registry.register(new IeeeAdapter());
    this.registry.register(new CoreAdapter());
    this.registry.register(new UnpaywallAdapter());
    this.registry.register(new GoogleScholarAdapter());
  }

  /**
   * 初始化搜索器
   */
  async initialize(): Promise<void> {
    if (!this.ai) {
      try {
        this.ai = await createAIProvider();
        this.webAdapter.setAIProvider(this.ai);
      } catch (error) {
        throw new ApiInitializationError(
          `Failed to initialize AI provider: ${getErrorMessage(error)}`,
          error instanceof Error ? error : undefined
        );
      }
    }
  }

  /**
   * Get the adapter registry
   */
  getRegistry(): SearchSourceRegistry {
    return this.registry;
  }

  /**
   * Get the search strategy
   */
  getStrategy(): ComplementarySearchStrategy {
    return this.strategy;
  }

  /**
   * 综合搜索入口
   */
  async search(query: string, options: SearchOptions = {}): Promise<SearchResponse> {
    await this.initialize();

    const {
      limit = 10,
      sortBy = 'relevance',
      domainHint,
      filters
    } = options;

    let sources: SearchSource[];

    if (options.sources && options.sources.length > 0) {
      // Explicit sources specified
      sources = options.sources;
    } else {
      // Auto-select using complementary strategy
      sources = this.strategy.selectSources(query, this.registry, domainHint);
    }

    const allResults: SearchResult[] = [];
    const usedSources: string[] = [];

    // 并行搜索多个数据源（带超时）
    const searchPromises: Promise<SearchResult[]>[] = [];

    for (const sourceId of sources) {
      const adapter = this.registry.get(sourceId);
      if (!adapter || !adapter.isAvailable()) continue;

      // Skip unpaywall for search (it's an enrichment source)
      if (sourceId === 'unpaywall') continue;

      searchPromises.push(
        withTimeout(
          adapter.search(query, limit),
          DEFAULT_TIMEOUT_MS,
          `${adapter.meta.name} search`
        ).catch(err => {
          console.error(`${adapter.meta.name} search failed:`, getErrorMessage(err));
          return [];
        })
      );
      usedSources.push(sourceId);
    }

    const results = await Promise.allSettled(searchPromises);

    // 合并结果
    results.forEach((result) => {
      if (result.status === 'fulfilled') {
        allResults.push(...result.value);
      }
    });

    // 应用过滤
    let filtered = this.applyFilters(allResults, filters);

    // 排序
    filtered = this.sortResults(filtered, sortBy);

    // 限制结果数量
    filtered = filtered.slice(0, limit * usedSources.length);

    // 去重（基于标题相似度）
    filtered = this.deduplicateResults(filtered);

    return {
      query,
      totalResults: filtered.length,
      results: filtered.slice(0, limit),
      sources: usedSources,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 按作者搜索
   */
  async searchByAuthor(authorName: string, options: SearchOptions = {}): Promise<SearchResponse> {
    const query = `author:"${authorName}"`;
    return this.search(query, { ...options, sources: ['arxiv', 'semantic_scholar'] });
  }

  /**
   * 应用过滤条件
   */
  private applyFilters(results: SearchResult[], filters?: SearchOptions['filters']): SearchResult[] {
    if (!filters) return results;

    let filtered = [...results];

    // 年份过滤
    if (filters.yearRange) {
      const [start, end] = filters.yearRange;
      filtered = filtered.filter(r => {
        const year = parseInt(r.publishDate.split('-')[0]);
        return !isNaN(year) && year >= start && year <= end;
      });
    }

    // 最小引用数过滤
    if (filters.minCitations) {
      filtered = filtered.filter(r =>
        !r.citations || r.citations >= filters.minCitations!
      );
    }

    // 分类过滤
    if (filters.categories?.length) {
      filtered = filtered.filter(r =>
        r.keywords?.some(k => filters.categories!.includes(k))
      );
    }

    return filtered;
  }

  /**
   * 排序结果
   */
  private sortResults(results: SearchResult[], sortBy: string): SearchResult[] {
    const sorted = [...results];

    switch (sortBy) {
      case 'citations':
        return sorted.sort((a, b) => (b.citations || 0) - (a.citations || 0));
      case 'date':
        return sorted.sort((a, b) =>
          new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime()
        );
      default:
        return sorted; // 按相关性（API默认顺序）
    }
  }

  /**
   * 去重（基于标题相似度）
   */
  private deduplicateResults(results: SearchResult[]): SearchResult[] {
    const seen = new Set<string>();
    const deduped: SearchResult[] = [];

    for (const result of results) {
      const normalizedTitle = normalizeTitle(result.title);

      if (!seen.has(normalizedTitle)) {
        seen.add(normalizedTitle);
        deduped.push(result);
      }
    }

    return deduped;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const query = args[0];

  if (!query) {
    console.error('Usage: bun run search.ts <query> [--limit N] [--source <source>]');
    process.exit(1);
  }

  const limitIndex = args.indexOf('--limit');
  const limit = limitIndex > -1 ? parseInt(args[limitIndex + 1]) || 10 : 10;

  const sourceIndex = args.indexOf('--source');
  const source = sourceIndex > -1 ? args[sourceIndex + 1] as SearchSource : undefined;

  const searcher = new LiteratureSearch();

  searcher.search(query, {
    limit,
    sources: source ? [source] : undefined
  }).then(response => {
    console.log(JSON.stringify(response, null, 2));
  }).catch(err => {
    console.error('Search failed:', getErrorMessage(err));
    process.exit(1);
  });
}
