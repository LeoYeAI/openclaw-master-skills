/**
 * DBLP Adapter - Computer science bibliography
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult, DblpHit } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const DBLP_API_URL = 'https://dblp.org/search/publ/api';

export class DblpAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'DBLP',
    sourceId: 'dblp',
    tier: 'free',
    domains: ['cs'],
    rateLimit: { requests: 1, windowMs: 1000 },
    description: 'Computer science bibliography with comprehensive CS publication coverage'
  };

  isAvailable(): boolean {
    return true; // No API key required
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const url = `${DBLP_API_URL}?q=${encodeURIComponent(query)}&format=json&h=${limit}`;

      const response = await this.rateLimitedFetch(url);
      const data = await response.json() as {
        result?: { hits?: { hit?: DblpHit[] } };
      };

      const hits = data.result?.hits?.hit;
      if (!hits) return [];

      return hits.map((hit, index) => {
        const info = hit.info;

        // Parse authors - can be array or single object
        let authors: string[] = [];
        if (info.authors?.author) {
          const authorData = info.authors.author;
          if (Array.isArray(authorData)) {
            authors = authorData.map(a => a.text);
          } else {
            authors = [authorData.text];
          }
        }

        return {
          id: `dblp_${index}`,
          title: info.title || '',
          authors,
          abstract: '', // DBLP doesn't provide abstracts
          publishDate: info.year || '',
          source: 'dblp',
          url: info.ee || info.url || '',
          doi: info.doi,
          venue: info.venue
        };
      });
    } catch (error) {
      console.error('DBLP search error:', getErrorMessage(error));
      return [];
    }
  }
}
