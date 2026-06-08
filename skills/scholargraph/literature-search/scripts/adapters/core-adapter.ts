/**
 * CORE Adapter - Open access full text
 * Requires API key for access
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const CORE_API_URL = 'https://api.core.ac.uk/v3/search/works';

export class CoreAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'CORE',
    sourceId: 'core',
    tier: 'freemium',
    domains: ['general', 'multidisciplinary'],
    rateLimit: { requests: 1, windowMs: 10000 }, // 1 req/10s on free tier
    description: 'Open access aggregator with full text from 10K+ repositories'
  };

  private apiKey?: string;

  constructor(apiKey?: string) {
    super();
    this.apiKey = apiKey || process.env.CORE_API_KEY;
  }

  isAvailable(): boolean {
    return !!this.apiKey;
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    if (!this.apiKey) return [];

    try {
      const url = `${CORE_API_URL}?q=${encodeURIComponent(query)}&limit=${limit}`;

      const response = await this.rateLimitedFetch(url, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });
      const data = await response.json() as {
        results?: Array<{
          id?: string;
          title?: string;
          authors?: Array<{ name?: string }>;
          abstract?: string;
          yearPublished?: number;
          doi?: string;
          downloadUrl?: string;
          sourceFulltextUrls?: string[];
          citationCount?: number;
          journals?: Array<{ title?: string }>;
        }>;
      };

      if (!data.results) return [];

      return data.results.map(work => ({
        id: `core:${work.id || ''}`,
        title: work.title || '',
        authors: work.authors?.map(a => a.name || '').filter(Boolean) || [],
        abstract: work.abstract || '',
        publishDate: work.yearPublished?.toString() || '',
        source: 'core',
        url: work.doi ? `https://doi.org/${work.doi}` : (work.sourceFulltextUrls?.[0] || ''),
        doi: work.doi,
        pdfUrl: work.downloadUrl,
        citations: work.citationCount,
        journal: work.journals?.[0]?.title,
        openAccess: true
      }));
    } catch (error) {
      console.error('CORE search error:', getErrorMessage(error));
      return [];
    }
  }

  async getPdfUrl(result: SearchResult): Promise<string | undefined> {
    if (!this.apiKey || !result.doi) return undefined;
    // CORE already provides download URLs in search results
    return result.pdfUrl;
  }
}
