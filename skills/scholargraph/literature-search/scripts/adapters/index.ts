/**
 * Adapters - Barrel Export
 */

export { type SearchSourceAdapter, AbstractSearchAdapter, type AdapterMeta, type SourceTier, type SourceDomain } from './base';
export { SearchSourceRegistry } from './registry';

// Source adapters
export { ArxivAdapter } from './arxiv-adapter';
export { SemanticScholarAdapter } from './semantic-scholar-adapter';
export { WebAdapter } from './web-adapter';
export { OpenAlexAdapter } from './openalex-adapter';
export { PubMedAdapter } from './pubmed-adapter';
export { CrossRefAdapter } from './crossref-adapter';
export { DblpAdapter } from './dblp-adapter';
export { IeeeAdapter } from './ieee-adapter';
export { CoreAdapter } from './core-adapter';
export { UnpaywallAdapter } from './unpaywall-adapter';
export { GoogleScholarAdapter } from './google-scholar-adapter';
