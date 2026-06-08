/**
 * Search Source Registry
 * 搜索源注册表 - 管理所有可用的搜索适配器
 */

import type { SearchSourceAdapter, SourceTier, SourceDomain } from './base';
import type { SearchSource } from '../../../shared/types';

export class SearchSourceRegistry {
  private adapters = new Map<SearchSource, SearchSourceAdapter>();

  /**
   * Register an adapter
   */
  register(adapter: SearchSourceAdapter): void {
    this.adapters.set(adapter.meta.sourceId, adapter);
  }

  /**
   * Get adapter by source ID
   */
  get(sourceId: SearchSource): SearchSourceAdapter | undefined {
    return this.adapters.get(sourceId);
  }

  /**
   * Get all registered adapters
   */
  getAll(): SearchSourceAdapter[] {
    return Array.from(this.adapters.values());
  }

  /**
   * Get only available adapters (API keys present, etc.)
   */
  getAvailable(): SearchSourceAdapter[] {
    return this.getAll().filter(a => a.isAvailable());
  }

  /**
   * Get adapters by tier
   */
  getByTier(tier: SourceTier): SearchSourceAdapter[] {
    return this.getAll().filter(a => a.meta.tier === tier);
  }

  /**
   * Get adapters by domain
   */
  getByDomain(domain: SourceDomain): SearchSourceAdapter[] {
    return this.getAll().filter(a => a.meta.domains.includes(domain));
  }

  /**
   * Get available adapters filtered by source IDs, maintaining order
   */
  getBySourceIds(sourceIds: SearchSource[]): SearchSourceAdapter[] {
    const result: SearchSourceAdapter[] = [];
    for (const id of sourceIds) {
      const adapter = this.adapters.get(id);
      if (adapter && adapter.isAvailable()) {
        result.push(adapter);
      }
    }
    return result;
  }

  /**
   * Check if a source is registered and available
   */
  isAvailable(sourceId: SearchSource): boolean {
    const adapter = this.adapters.get(sourceId);
    return adapter ? adapter.isAvailable() : false;
  }

  /**
   * Get all registered source IDs
   */
  getSourceIds(): SearchSource[] {
    return Array.from(this.adapters.keys());
  }
}
