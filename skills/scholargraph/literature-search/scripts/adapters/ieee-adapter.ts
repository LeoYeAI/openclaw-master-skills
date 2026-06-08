/**
 * IEEE Xplore Adapter
 * Engineering/EE/CS papers, requires API key
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const IEEE_API_URL = 'https://ieeexploreapi.ieee.org/api/v1/search/articles';

export class IeeeAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'IEEE Xplore',
    sourceId: 'ieee',
    tier: 'freemium',
    domains: ['engineering', 'cs'],
    rateLimit: { requests: 3, windowMs: 1000 },
    description: 'IEEE digital library for engineering, CS, and EE research'
  };

  private apiKey?: string;

  constructor(apiKey?: string) {
    super();
    this.apiKey = apiKey || process.env.IEEE_API_KEY;
  }

  isAvailable(): boolean {
    return !!this.apiKey;
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    if (!this.apiKey) return [];

    try {
      const url = `${IEEE_API_URL}?apikey=${this.apiKey}&querytext=${encodeURIComponent(query)}&max_records=${limit}&sort_field=article_title&sort_order=asc`;

      const response = await this.rateLimitedFetch(url);
      const data = await response.json() as {
        articles?: Array<{
          article_number?: string;
          title?: string;
          authors?: { authors: Array<{ full_name: string }> };
          abstract?: string;
          publication_year?: string;
          publication_title?: string;
          doi?: string;
          html_url?: string;
          pdf_url?: string;
          citing_paper_count?: number;
          is_open_access?: boolean;
        }>;
      };

      if (!data.articles) return [];

      return data.articles.map(article => ({
        id: `ieee:${article.article_number || ''}`,
        title: article.title || '',
        authors: article.authors?.authors.map(a => a.full_name) || [],
        abstract: article.abstract || '',
        publishDate: article.publication_year || '',
        source: 'ieee',
        url: article.html_url || `https://ieeexplore.ieee.org/document/${article.article_number}`,
        doi: article.doi,
        pdfUrl: article.pdf_url,
        citations: article.citing_paper_count,
        venue: article.publication_title,
        journal: article.publication_title,
        openAccess: article.is_open_access
      }));
    } catch (error) {
      console.error('IEEE Xplore search error:', getErrorMessage(error));
      return [];
    }
  }
}
