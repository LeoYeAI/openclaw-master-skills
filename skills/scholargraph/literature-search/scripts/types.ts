/**
 * Literature Search - Type Definitions
 * 文献检索类型定义
 */

import type { SearchSource } from '../../shared/types';

export interface SearchOptions {
  sources?: SearchSource[];
  limit?: number;
  sortBy?: 'relevance' | 'date' | 'citations';
  domainHint?: string;
  filters?: {
    yearRange?: [number, number];
    categories?: string[];
    minCitations?: number;
    authors?: string[];
  };
}

export interface SearchResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  publishDate: string;
  source: string;
  url: string;
  pdfUrl?: string;
  citations?: number;
  venue?: string;
  keywords?: string[];
  doi?: string;
  snippet?: string;
  openAccess?: boolean;
  concepts?: string[];
  meshTerms?: string[];
  journal?: string;
}

export interface ArxivPaper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  published: string;
  updated: string;
  categories: string[];
  pdfUrl: string;
  entryId: string;
}

export interface SemanticScholarPaper {
  paperId: string;
  title: string;
  abstract?: string;
  authors: Array<{ authorId: string; name: string }>;
  year?: number;
  citationCount?: number;
  venue?: string;
  url: string;
  openAccessPdf?: { url: string };
}

export interface SearchResponse {
  query: string;
  totalResults: number;
  results: SearchResult[];
  sources: string[];
  timestamp: string;
}

// OpenAlex API response types
export interface OpenAlexWork {
  id: string;
  doi?: string;
  title?: string;
  display_name?: string;
  publication_year?: number;
  publication_date?: string;
  type?: string;
  cited_by_count?: number;
  is_oa?: boolean;
  open_access?: {
    is_oa: boolean;
    oa_url?: string;
  };
  authorships?: Array<{
    author: {
      id: string;
      display_name: string;
    };
  }>;
  primary_location?: {
    source?: {
      display_name?: string;
    };
  };
  abstract_inverted_index?: Record<string, number[]>;
  concepts?: Array<{
    display_name: string;
    score: number;
  }>;
  best_oa_location?: {
    pdf_url?: string;
    landing_page_url?: string;
  };
}

// PubMed API response types
export interface PubMedArticle {
  pmid: string;
  title: string;
  authors: string[];
  abstract: string;
  publishDate: string;
  journal?: string;
  doi?: string;
  meshTerms?: string[];
  pdfUrl?: string;
}

// CrossRef API response types
export interface CrossRefWork {
  DOI: string;
  title?: string[];
  author?: Array<{
    given?: string;
    family?: string;
  }>;
  abstract?: string;
  'container-title'?: string[];
  'published-print'?: { 'date-parts': number[][] };
  'published-online'?: { 'date-parts': number[][] };
  'is-referenced-by-count'?: number;
  type?: string;
  URL?: string;
  link?: Array<{
    URL: string;
    'content-type'?: string;
  }>;
}

// DBLP API response types
export interface DblpHit {
  info: {
    title?: string;
    authors?: { author: Array<{ text: string }> | { text: string } };
    venue?: string;
    year?: string;
    type?: string;
    doi?: string;
    url?: string;
    ee?: string;
  };
}

// PDF download types
export interface PdfDownloadOptions {
  outputDir?: string;
  maxFileSize?: number;
  skipExisting?: boolean;
  concurrency?: number;
  namingStrategy?: 'title' | 'id' | 'doi';
}

export interface PdfDownloadResult {
  filePath: string;
  title: string;
  source: string;
  size: number;
  doi?: string;
}

export interface PdfMetadataIndex {
  files: Array<{
    filePath: string;
    title: string;
    authors: string[];
    source: string;
    doi?: string;
    url: string;
    downloadedAt: string;
  }>;
}
