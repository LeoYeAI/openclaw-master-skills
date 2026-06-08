/**
 * OpenAlex Adapter - Open scholarly metadata
 * 250M+ records, comprehensive coverage
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult, OpenAlexWork } from '../types';
import { reconstructAbstract } from '../../../shared/utils';
import { getErrorMessage } from '../../../shared/errors';

const OPENALEX_API_URL = 'https://api.openalex.org/works';

export class OpenAlexAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'OpenAlex',
    sourceId: 'openalex',
    tier: 'free',
    domains: ['general', 'multidisciplinary', 'biomedical', 'cs', 'physics', 'engineering'],
    rateLimit: { requests: 10, windowMs: 1000 },
    description: 'Open catalog of 250M+ scholarly works, authors, venues, and concepts'
  };

  private mailto?: string;

  constructor(mailto?: string) {
    super();
    this.mailto = mailto || process.env.OPENALEX_MAILTO;
  }

  isAvailable(): boolean {
    return true; // No API key required
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      let url = `${OPENALEX_API_URL}?search=${encodeURIComponent(query)}&per_page=${limit}`;
      if (this.mailto) {
        url += `&mailto=${encodeURIComponent(this.mailto)}`;
      }

      const response = await this.rateLimitedFetch(url);
      const data = await response.json() as { results?: OpenAlexWork[] };

      if (!data.results) return [];

      return data.results.map((work) => {
        const abstract = work.abstract_inverted_index
          ? reconstructAbstract(work.abstract_inverted_index)
          : '';

        const authors = work.authorships?.map(a => a.author.display_name) || [];
        const doi = work.doi?.replace('https://doi.org/', '');

        return {
          id: work.id.replace('https://openalex.org/', ''),
          title: work.display_name || work.title || '',
          authors,
          abstract,
          publishDate: work.publication_date || work.publication_year?.toString() || '',
          source: 'openalex',
          url: work.doi || work.id,
          doi,
          pdfUrl: work.best_oa_location?.pdf_url || work.open_access?.oa_url,
          citations: work.cited_by_count,
          venue: work.primary_location?.source?.display_name,
          openAccess: work.is_oa || work.open_access?.is_oa,
          concepts: work.concepts?.filter(c => c.score > 0.3).map(c => c.display_name)
        };
      });
    } catch (error) {
      console.error('OpenAlex search error:', getErrorMessage(error));
      return [];
    }
  }
}
