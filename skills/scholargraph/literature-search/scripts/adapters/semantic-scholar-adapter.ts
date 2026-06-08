/**
 * Semantic Scholar Adapter
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult, SemanticScholarPaper } from '../types';
import { getErrorMessage } from '../../../shared/errors';

const S2_API_URL = 'https://api.semanticscholar.org/graph/v1';

export class SemanticScholarAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'Semantic Scholar',
    sourceId: 'semantic_scholar',
    tier: 'free',
    domains: ['general', 'cs', 'biomedical', 'multidisciplinary'],
    rateLimit: { requests: 10, windowMs: 1000 },
    description: 'AI-powered academic search engine with 200M+ papers'
  };

  isAvailable(): boolean {
    return true; // No API key required (has optional key for higher limits)
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const fields = 'paperId,title,abstract,authors,year,citationCount,venue,url,openAccessPdf';
      const url = `${S2_API_URL}/paper/search?query=${encodeURIComponent(query)}&limit=${limit}&fields=${fields}`;

      const response = await this.rateLimitedFetch(url, undefined, { maxRetries: 3 });
      const data = await response.json() as { data?: SemanticScholarPaper[] };

      if (!data.data) return [];

      return data.data.map((paper) => ({
        id: paper.paperId,
        title: paper.title,
        authors: paper.authors.map(a => a.name),
        abstract: paper.abstract || '',
        publishDate: paper.year?.toString() || '',
        source: 'semantic_scholar',
        url: paper.url,
        pdfUrl: paper.openAccessPdf?.url,
        citations: paper.citationCount,
        venue: paper.venue,
        openAccess: !!paper.openAccessPdf
      }));
    } catch (error) {
      console.error('Semantic Scholar search error:', getErrorMessage(error));
      return [];
    }
  }
}
