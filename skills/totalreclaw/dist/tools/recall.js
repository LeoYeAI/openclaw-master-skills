"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.recallTool = recallTool;
exports.formatRecallResults = formatRecallResults;
exports.createRecallTool = createRecallTool;
const client_1 = require("@totalreclaw/client");
/**
 * Default number of results to return
 */
const DEFAULT_K = 8;
/**
 * Maximum number of results allowed
 */
const MAX_K = 50;
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
async function recallTool(client, reranker, params) {
    // Validate input
    if (!params || typeof params.query !== 'string' || params.query.trim().length === 0) {
        return {
            success: false,
            error: 'Invalid input: query is required and must be a non-empty string',
        };
    }
    // Validate and normalize k
    let k = params.k ?? DEFAULT_K;
    if (typeof k !== 'number' || k < 1) {
        k = DEFAULT_K;
    }
    else if (k > MAX_K) {
        k = MAX_K;
    }
    k = Math.floor(k);
    try {
        // Search for memories
        const results = await client.recall(params.query.trim(), k);
        // If no results, return early
        if (results.length === 0) {
            return {
                success: true,
                results: [],
                count: 0,
            };
        }
        // Re-rank with cross-encoder if available
        let finalResults;
        if (reranker && reranker.isReady()) {
            const facts = results.map((r) => r.fact);
            const crossEncoderResults = await reranker.rerank(params.query.trim(), facts, k);
            finalResults = crossEncoderResults.map((ceResult) => ({
                fact: ceResult.fact,
                score: ceResult.score,
                vectorScore: ceResult.vectorScore,
                textScore: ceResult.textScore,
                decayAdjustedScore: ceResult.decayAdjustedScore,
                rerankedByCrossEncoder: true,
            }));
        }
        else {
            // Use original results without cross-encoder reranking
            finalResults = results.slice(0, k).map((result) => ({
                ...result,
                rerankedByCrossEncoder: false,
            }));
        }
        return {
            success: true,
            results: finalResults,
            count: finalResults.length,
        };
    }
    catch (error) {
        // Handle known error types
        if (error instanceof client_1.TotalReclawError) {
            return {
                success: false,
                error: `TotalReclaw error (${error.code}): ${error.message}`,
            };
        }
        // Handle unknown errors
        const message = error instanceof Error ? error.message : 'Unknown error occurred';
        return {
            success: false,
            error: `Failed to recall memories: ${message}`,
        };
    }
}
/**
 * Format recall results as a human-readable string
 *
 * @param result - The recall tool result
 * @returns Formatted string representation
 */
function formatRecallResults(result) {
    if (!result.success) {
        return `Search failed: ${result.error}`;
    }
    if (!result.results || result.results.length === 0) {
        return 'No memories found matching your query.';
    }
    const lines = [
        `Found ${result.results.length} relevant memories:`,
        '',
    ];
    for (let i = 0; i < result.results.length; i++) {
        const item = result.results[i];
        const importance = Math.round((item.fact.metadata.importance ?? 0.5) * 10);
        const rerankedTag = item.rerankedByCrossEncoder ? ' [reranked]' : '';
        lines.push(`${i + 1}. ${item.fact.text}`);
        lines.push(`   Score: ${item.score.toFixed(3)} | Importance: ${importance}/10${rerankedTag}`);
        lines.push('');
    }
    return lines.join('\n');
}
/**
 * Create a bound recall tool function
 *
 * Useful for creating a tool that's pre-bound to client and reranker instances.
 *
 * @param client - The TotalReclaw client instance
 * @param reranker - Optional cross-encoder reranker
 * @returns A function that accepts RecallToolParams and returns RecallToolResult
 */
function createRecallTool(client, reranker = null) {
    return (params) => recallTool(client, reranker, params);
}
exports.default = recallTool;
//# sourceMappingURL=recall.js.map