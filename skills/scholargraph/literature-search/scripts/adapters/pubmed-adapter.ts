/**
 * PubMed Adapter - NCBI E-utilities
 * Best for biomedical/life sciences
 */

import { AbstractSearchAdapter, type AdapterMeta } from './base';
import type { SearchResult } from '../types';
import { parsePubMedXml } from '../../../shared/utils';
import { getErrorMessage } from '../../../shared/errors';

const EUTILS_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';

export class PubMedAdapter extends AbstractSearchAdapter {
  readonly meta: AdapterMeta = {
    name: 'PubMed',
    sourceId: 'pubmed',
    tier: 'free',
    domains: ['biomedical'],
    rateLimit: { requests: 3, windowMs: 1000 },
    description: 'NCBI biomedical literature database with 35M+ citations'
  };

  private apiKey?: string;

  constructor(apiKey?: string) {
    super();
    this.apiKey = apiKey || process.env.NCBI_API_KEY;
    // With API key, rate limit is 10/s
    if (this.apiKey) {
      (this.meta as AdapterMeta).rateLimit = { requests: 10, windowMs: 1000 };
    }
  }

  isAvailable(): boolean {
    return true; // Works without API key (lower rate limit)
  }

  async search(query: string, limit: number): Promise<SearchResult[]> {
    try {
      // Step 1: esearch to get PMIDs
      let searchUrl = `${EUTILS_BASE}/esearch.fcgi?db=pubmed&term=${encodeURIComponent(query)}&retmax=${limit}&retmode=json`;
      if (this.apiKey) searchUrl += `&api_key=${this.apiKey}`;

      const searchResp = await this.rateLimitedFetch(searchUrl);
      const searchData = await searchResp.json() as {
        esearchresult?: { idlist?: string[] };
      };

      const pmids = searchData.esearchresult?.idlist;
      if (!pmids || pmids.length === 0) return [];

      // Step 2: efetch to get article details
      let fetchUrl = `${EUTILS_BASE}/efetch.fcgi?db=pubmed&id=${pmids.join(',')}&rettype=xml&retmode=xml`;
      if (this.apiKey) fetchUrl += `&api_key=${this.apiKey}`;

      const fetchResp = await this.rateLimitedFetch(fetchUrl);
      const xml = await fetchResp.text();

      const articles = parsePubMedXml(xml);

      return articles.map(article => ({
        id: `pmid:${article.pmid}`,
        title: article.title,
        authors: article.authors,
        abstract: article.abstract,
        publishDate: article.publishDate,
        source: 'pubmed',
        url: `https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`,
        doi: article.doi,
        journal: article.journal,
        meshTerms: article.meshTerms,
        pdfUrl: article.doi ? `https://doi.org/${article.doi}` : undefined
      }));
    } catch (error) {
      console.error('PubMed search error:', getErrorMessage(error));
      return [];
    }
  }
}
