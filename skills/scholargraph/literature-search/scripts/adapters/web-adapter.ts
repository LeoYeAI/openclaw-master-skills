/**
 * Web Search Adapter - via AI provider web search
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import type { AIProvider } from '../../../shared/ai-provider';
import type { WebSearchResultItem } from '../../../shared/types';
import { getErrorMessage } from '../../../shared/errors';

export class WebAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'Web Search',
    sourceId: 'web',
    tier: 'free',
    domains: ['general', 'multidisciplinary'],
    rateLimit: { requests: 5, windowMs: 1000 },
    description: 'Web search via AI provider (Serper API)'
  };

  private ai: AIProvider | null = null;

  setAIProvider(ai: AIProvider): void {
    this.ai = ai;
  }

  isAvailable(): boolean {
    return this.ai !== null && typeof this.ai.webSearch === 'function';
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    if (!this.ai?.webSearch) {
      return [];
    }

    try {
      const academicQuery = `${query} research paper arxiv OR scholar OR "paper" OR "publication"`;
      const results: WebSearchResultItem[] = await this.ai.webSearch(academicQuery, limit);

      return results.map((item, index) => ({
        id: `web_${index}`,
        title: item.name,
        authors: [],
        abstract: item.snippet || '',
        publishDate: item.date || '',
        source: 'web',
        url: item.url,
        snippet: item.snippet
      }));
    } catch (error) {
      console.error('Web search error:', getErrorMessage(error));
      return [];
    }
  }
}
