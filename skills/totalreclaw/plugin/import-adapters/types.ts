/**
 * Normalized fact — the common format all adapters produce.
 * Maps directly to what storeExtractedFacts() / client.remember() expect.
 */
export interface NormalizedFact {
  /** The atomic fact text (max 512 chars) */
  text: string;
  /** Fact type matching TotalReclaw's taxonomy */
  type: 'fact' | 'preference' | 'decision' | 'episodic' | 'goal' | 'context' | 'summary';
  /** Importance score 1-10 */
  importance: number;
  /** Original source system */
  source: ImportSource;
  /** Original ID in the source system (for traceability) */
  sourceId?: string;
  /** Original timestamp from source */
  sourceTimestamp?: string;
  /** Additional tags */
  tags?: string[];
}

export type ImportSource = 'mem0' | 'mcp-memory' | 'memoclaw' | 'generic-json' | 'generic-csv';

/**
 * What the user passes to the import tool.
 */
export interface ImportFromInput {
  /** Which source to import from */
  source: ImportSource;
  /** For API-based sources: the API key or auth token */
  api_key?: string;
  /** For API-based sources: the user/agent ID in the source system */
  source_user_id?: string;
  /** For file-based sources: the file content (pasted or read) */
  content?: string;
  /** For file-based sources: path to the file on disk */
  file_path?: string;
  /** Optional: target namespace in TotalReclaw */
  namespace?: string;
  /** Optional: dry run — parse and report without storing */
  dry_run?: boolean;
  /** Optional: API base URL override (for self-hosted instances) */
  api_url?: string;
}

/**
 * Result of an import operation.
 */
export interface ImportResult {
  success: boolean;
  source: ImportSource;
  /** Total facts found in source */
  total_found: number;
  /** Facts successfully imported */
  imported: number;
  /** Facts skipped (duplicates via content fingerprint) */
  skipped_duplicate: number;
  /** Facts skipped (validation errors) */
  skipped_invalid: number;
  /** Individual errors */
  errors: Array<{ index: number; text_preview: string; error: string }>;
  /** Warnings */
  warnings: string[];
  /** Unique import run ID */
  import_id: string;
  /** Duration in ms */
  duration_ms: number;
}

/**
 * Progress callback for long-running imports.
 */
export type ProgressCallback = (progress: {
  current: number;
  total: number;
  phase: 'fetching' | 'parsing' | 'storing';
  message: string;
}) => void;

/**
 * Adapter parse result — returned by each adapter's parse method.
 */
export interface AdapterParseResult {
  facts: NormalizedFact[];
  warnings: string[];
  errors: string[];
  /** Metadata about the source (for logging) */
  source_metadata?: Record<string, unknown>;
}
