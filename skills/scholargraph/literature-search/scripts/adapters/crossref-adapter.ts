/**
 * CrossRef Adapter - DOI registration and metadata
 * 150M+ records, excellent for DOI resolution
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult, CrossRefWork } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const CROSSREF_API_URL = 'https://api.crossref.org/works';

export class CrossRefAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'CrossRef',
    sourceId: 'crossref',
    tier: 'free',
    domains: ['general', 'multidisciplinary'],
    rateLimit: { requests: 5, windowMs: 1000 },
    description: 'Official DOI registration agency with 150M+ metadata records'
  };

  private mailto?: string;

  constructor(mailto?: string) {
    super();
    this.mailto = mailto || process.env.CROSSREF_MAILTO;
  }

  isAvailable(): boolean {
    return true; // No API key required
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const url = `${CROSSREF_API_URL}?query=${encodeURIComponent(query)}&rows=${limit}&sort=relevance`;

      const headers: Record<string, string> = {};
      if (this.mailto) {
        headers['User-Agent'] = `ScholarGraph/1.0 (mailto:${this.mailto})`;
      }

      const response = await this.rateLimitedFetch(url, { headers });
      const data = await response.json() as {
        message?: { items?: CrossRefWork[] };
      };

      if (!data.message?.items) return [];

      return data.message.items.map((work) => {
        const authors = work.author?.map(a => {
          const parts = [a.given, a.family].filter(Boolean);
          return parts.join(' ');
        }) || [];

        const dateParts = work['published-print']?.['date-parts']?.[0]
          || work['published-online']?.['date-parts']?.[0];
        const publishDate = dateParts
          ? dateParts.filter(Boolean).join('-')
          : '';

        // Find PDF link if available
        const pdfLink = work.link?.find(l => l['content-type']?.includes('pdf'));

        return {
          id: `doi:${work.DOI}`,
          title: work.title?.[0] || '',
          authors,
          abstract: work.abstract?.replace(/<[^>]*>/g, '') || '', // Strip JATS XML tags
          publishDate,
          source: 'crossref',
          url: work.URL || `https://doi.org/${work.DOI}`,
          doi: work.DOI,
          citations: work['is-referenced-by-count'],
          venue: work['container-title']?.[0],
          journal: work['container-title']?.[0],
          pdfUrl: pdfLink?.URL
        };
      });
    } catch (error) {
      console.error('CrossRef search error:', getErrorMessage(error));
      return [];
    }
  }
}
