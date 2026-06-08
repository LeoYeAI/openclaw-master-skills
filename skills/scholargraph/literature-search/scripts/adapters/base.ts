/**
 * Search Source Adapter - Base Interface & Abstract Class
 * 搜索源适配器基类
 */

import type { SearchResult } from '../types';
import type { SearchSource } from '../../../shared/types';
import { fetchWithRetry } from '../../../shared/utils';
import type { RetryOptions } from '../../../shared/types';

/** Source tier classification */
export type SourceTier = 'free' | 'freemium' | 'paid';

/** Academic domain coverage */
export type SourceDomain = 'general' | 'biomedical' | 'cs' | 'engineering' | 'physics' | 'multidisciplinary';

/** Adapter metadata */
export interface AdapterMeta {
  name: string;
  sourceId: SearchSource;
  tier: SourceTier;
  domains: SourceDomain[];
  rateLimit: { requests: number; windowMs: number };
  description: string;
}

/**
 * SearchSourceAdapter interface - contract for all search adapters
 */
export interface SearchSourceAdapter {
  readonly meta: AdapterMeta;

  /** Check if this adapter is available (API keys present, etc.) */
  isAvailable(): boolean;

  /** Execute a search query */
  search(query: string, limit: number): Promise<SearchResult[]>;

  /** Optional: resolve PDF URL for a given result */
  getPdfUrl?(result: SearchResult): Promise<string | undefined>;
}

/**
 * AbstractSearchAdapter - provides common functionality
 */
export abstract class AbstractSearchAdapter implements SearchSourceAdapter {
  abstract readonly meta: AdapterMeta;

  abstract isAvailable(): boolean;
  abstract search(query: string, limit: number): Promise<SearchResult[]>;

  private lastRequestTime = 0;

  /**
   * Rate-limited fetch wrapper
   */
  protected async rateLimitedFetch(
    url: string,
    init?: RequestInit,
    retryOpts?: RetryOptions
  ): Promise<Response> {
    const { requests, windowMs } = this.meta.rateLimit;
    const minInterval = windowMs / requests;

    const now = Date.now();
    const elapsed = now - this.lastRequestTime;
    if (elapsed < minInterval) {
      await new Promise(resolve => setTimeout(resolve, minInterval - elapsed));
    }

    this.lastRequestTime = Date.now();
    return fetchWithRetry(url, init, retryOpts ?? { maxRetries: 2 });
  }
}
