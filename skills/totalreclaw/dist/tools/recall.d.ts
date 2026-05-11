/**
 * TotalReclaw Skill - Recall Tool
 *
 * Tool for searching and retrieving memories from TotalReclaw.
 * This is the totalreclaw_recall tool implementation.
 *
 * @example
 * ```typescript
 * const results = await recallTool(client, reranker, {
 *   query: 'What does the user prefer to drink?',
 *   k: 5,
 * });
 * // results: Array of RerankedResult with fact, score, etc.
 * ```
 */
import type { TotalReclaw, RerankedResult } from '@totalreclaw/client';
import type { RecallToolParams } from '../types';
import type { CrossEncoderReranker } from '../reranker/cross-encoder';
/**
 * Result item from the recall tool (extends RerankedResult with additional context)
 */
export interface RecallToolResultItem extends RerankedResult {
    /** Whether this result was reranked by cross-encoder */
    rerankedByCrossEncoder: boolean;
}
/**
 * Result of the recall tool operation
 */
export interface RecallToolResult {
    /** Whether the operation succeeded */
    success: boolean;
    /** Search results (if successful) */
    results?: RecallToolResultItem[];
    /** Number of results returned */
    count?: number;
    /** Error message (if failed) */
    error?: string;
}
/**
 * Search for memories in TotalReclaw
 *
 * @param client - The TotalReclaw client instance
 * @param reranker - Optional cross-encoder reranker for improved ranking
 * @param params - Tool parameters (query, k?)
 * @returns Result containing success status and search results
 *
 * @throws {TotalReclawError} If the client is not initialized or operation fails
 *
 * @example
 * ```typescript
 * // Basic search
 * const result = await recallTool(client, reranker, {
 *   query: 'user preferences about food',
 * });
 *
 * // With custom result count
 * const result = await recallTool(client, reranker, {
 *   query: 'project deadlines',
 *   k: 15,
 * });
 *
 * // Without reranker (faster, less accurate)
 * const result = await recallTool(client, null, {
 *   query: 'meeting notes from last week',
 * });
 * ```
 */
export declare function recallTool(client: TotalReclaw, reranker: CrossEncoderReranker | null, params: RecallToolParams): Promise<RecallToolResult>;
/**
 * Format recall results as a human-readable string
 *
 * @param result - The recall tool result
 * @returns Formatted string representation
 */
export declare function formatRecallResults(result: RecallToolResult): string;
/**
 * Create a bound recall tool function
 *
 * Useful for creating a tool that's pre-bound to client and reranker instances.
 *
 * @param client - The TotalReclaw client instance
 * @param reranker - Optional cross-encoder reranker
 * @returns A function that accepts RecallToolParams and returns RecallToolResult
 */
export declare function createRecallTool(client: TotalReclaw, reranker?: CrossEncoderReranker | null): (params: RecallToolParams) => Promise<RecallToolResult>;
export default recallTool;
//# sourceMappingURL=recall.d.ts.map