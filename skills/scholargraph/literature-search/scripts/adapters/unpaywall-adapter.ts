/**
 * Unpaywall Adapter - DOI-to-OA-PDF resolver
 * Not a search engine - resolves DOIs to open access PDF URLs
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const UNPAYWALL_API_URL = 'https://api.unpaywall.org/v2';

export class UnpaywallAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'Unpaywall',
    sourceId: 'unpaywall',
    tier: 'free',
    domains: ['general', 'multidisciplinary'],
    rateLimit: { requests: 10, windowMs: 1000 },
    description: 'DOI-to-open-access PDF resolver (enrichment, not search)'
  };

  private email?: string;

  constructor(email?: string) {
    super();
    this.email = email || process.env.UNPAYWALL_EMAIL;
  }

  isAvailable(): boolean {
    return !!this.email;
  }

  /**
   * Unpaywall is not a search engine - returns empty for search queries.
   * Use getPdfUrl() to resolve DOIs to PDF URLs.
   */
  async search(_query: string, _limit: number): Promise<SearchResult[]> {
    return []; // Not a search engine
  }

  /**
   * Resolve a DOI to an open access PDF URL
   */
  async getPdfUrl(result: SearchResult): Promise<string | undefined> {
    if (!this.email || !result.doi) return undefined;

    try {
      const url = `${UNPAYWALL_API_URL}/${encodeURIComponent(result.doi)}?email=${encodeURIComponent(this.email)}`;
      const response = await this.rateLimitedFetch(url);
      const data = await response.json() as {
        best_oa_location?: {
          url_for_pdf?: string;
          url?: string;
        };
        is_oa?: boolean;
      };

      return data.best_oa_location?.url_for_pdf || data.best_oa_location?.url;
    } catch (error) {
      console.error('Unpaywall lookup error:', getErrorMessage(error));
      return undefined;
    }
  }

  /**
   * Batch resolve DOIs
   */
  async batchResolvePdfUrls(results: SearchResult[]): Promise<Map<string, string>> {
    const urlMap = new Map<string, string>();
    const resultsWithDois = results.filter(r => r.doi && !r.pdfUrl);

    for (const result of resultsWithDois) {
      const pdfUrl = await this.getPdfUrl(result);
      if (pdfUrl && result.doi) {
        urlMap.set(result.doi, pdfUrl);
      }
    }

    return urlMap;
  }
}
