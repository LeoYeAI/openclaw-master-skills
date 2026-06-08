/**
 * arXiv Adapter - arXiv API search
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { parseArxivXml } from '../../../shared/utils';
import { getErrorMessage } from '../../../shared/errors';

const ARXIV_API_URL = 'http://export.arxiv.org/api/query';

export class ArxivAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'arXiv',
    sourceId: 'arxiv',
    tier: 'free',
    domains: ['physics', 'cs', 'general'],
    rateLimit: { requests: 3, windowMs: 1000 },
    description: 'Open access preprint repository for physics, mathematics, CS, and more'
  };

  isAvailable(): boolean {
    return true; // No API key required
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const searchQuery = encodeURIComponent(`all:${query}`);
      const url = `${ARXIV_API_URL}?search_query=${searchQuery}&max_results=${limit}&sortBy=relevance`;

      const response = await this.rateLimitedFetch(url, undefined, { maxRetries: 3 });
      const text = await response.text();

      const entries = parseArxivXml(text);
      return entries.map(entry => ({
        id: entry.id,
        title: entry.title,
        authors: entry.authors,
        abstract: entry.abstract,
        publishDate: entry.published,
        source: 'arxiv',
        url: `https://arxiv.org/abs/${entry.id}`,
        pdfUrl: entry.pdfUrl,
        keywords: entry.categories,
        openAccess: true
      }));
    } catch (error) {
      console.error('arXiv search error:', getErrorMessage(error));
      return [];
    }
  }
}
