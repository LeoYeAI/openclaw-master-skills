/**
 * Google Scholar Adapter (via SerpAPI)
 * Requires SERPAPI_KEY
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const SERPAPI_URL = 'https://serpapi.com/search';

export class GoogleScholarAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'Google Scholar',
    sourceId: 'google_scholar',
    tier: 'paid',
    domains: ['general', 'multidisciplinary', 'cs', 'biomedical', 'engineering', 'physics'],
    rateLimit: { requests: 1, windowMs: 2000 },
    description: 'Google Scholar search via SerpAPI proxy'
  };

  private apiKey?: string;

  constructor(apiKey?: string) {
    super();
    this.apiKey = apiKey || process.env.SERPAPI_KEY;
  }

  isAvailable(): boolean {
    return !!this.apiKey;
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    if (!this.apiKey) return [];

    try {
      const url = `${SERPAPI_URL}?engine=google_scholar&q=${encodeURIComponent(query)}&num=${limit}&api_key=${this.apiKey}`;

      const response = await this.rateLimitedFetch(url);
      const data = await response.json() as {
        organic_results?: Array<{
          position?: number;
          title?: string;
          result_id?: string;
          link?: string;
          snippet?: string;
          publication_info?: {
            summary?: string;
            authors?: Array<{ name: string }>;
          };
          inline_links?: {
            cited_by?: { total?: number };
          };
          resources?: Array<{
            title?: string;
            file_format?: string;
            link?: string;
          }>;
        }>;
      };

      if (!data.organic_results) return [];

      return data.organic_results.map((result, index) => {
        const pdfResource = result.resources?.find(r =>
          r.file_format?.toLowerCase() === 'pdf' || r.link?.endsWith('.pdf')
        );

        const authors = result.publication_info?.authors?.map(a => a.name) || [];
        // Try to extract year from publication summary
        const yearMatch = result.publication_info?.summary?.match(/\b(19|20)\d{2}\b/);

        return {
          id: result.result_id || `gs_${index}`,
          title: result.title || '',
          authors,
          abstract: result.snippet || '',
          publishDate: yearMatch ? yearMatch[0] : '',
          source: 'google_scholar',
          url: result.link || '',
          pdfUrl: pdfResource?.link,
          citations: result.inline_links?.cited_by?.total,
          snippet: result.snippet
        };
      });
    } catch (error) {
      console.error('Google Scholar search error:', getErrorMessage(error));
      return [];
    }
  }
}
