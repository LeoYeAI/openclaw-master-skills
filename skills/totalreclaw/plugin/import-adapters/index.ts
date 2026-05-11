export { BaseImportAdapter } from './base-adapter.js';
export * from './types.js';
export { Mem0Adapter } from './mem0-adapter.js';
export { MCPMemoryAdapter } from './mcp-memory-adapter.js';

import type { ImportSource } from './types.js';
import { Mem0Adapter } from './mem0-adapter.js';
import { MCPMemoryAdapter } from './mcp-memory-adapter.js';
import type { BaseImportAdapter } from './base-adapter.js';

const ADAPTERS: Partial<Record<ImportSource, () => BaseImportAdapter>> = {
  'mem0': () => new Mem0Adapter(),
  'mcp-memory': () => new MCPMemoryAdapter(),
};

export function getAdapter(source: ImportSource): BaseImportAdapter {
  const factory = ADAPTERS[source];
  if (!factory) {
    throw new Error(`Unknown import source: ${source}. Valid sources: ${Object.keys(ADAPTERS).join(', ')}`);
  }
  return factory();
}
