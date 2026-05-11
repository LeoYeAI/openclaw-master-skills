/**
 * TotalReclaw Skill - Export Tool
 *
 * Tool for exporting memories from TotalReclaw.
 * This is the totalreclaw_export tool implementation.
 *
 * Supports two formats:
 * - JSON: Structured data format for programmatic use
 * - Markdown: Human-readable format for documentation
 *
 * @example
 * ```typescript
 * // Export as JSON
 * const jsonResult = await exportTool(client, { format: 'json' });
 *
 * // Export as Markdown
 * const mdResult = await exportTool(client, { format: 'markdown' });
 * ```
 */
import type { TotalReclaw } from '@totalreclaw/client';
import type { ExportToolParams } from '../types';
/**
 * Result of the export tool operation
 */
export interface ExportToolResult {
    /** Whether the operation succeeded */
    success: boolean;
    /** Exported data as formatted string (if successful) */
    data?: string;
    /** Export format used */
    format?: 'json' | 'markdown';
    /** Number of memories exported */
    count?: number;
    /** Error message (if failed) */
    error?: string;
}
/**
 * Export all memories from TotalReclaw
 *
 * @param client - The TotalReclaw client instance
 * @param params - Tool parameters (format?)
 * @returns Result containing success status and exported data
 *
 * @throws {TotalReclawError} If the client is not initialized or operation fails
 *
 * @example
 * ```typescript
 * // Export as JSON (default)
 * const result = await exportTool(client, {});
 *
 * // Export as Markdown
 * const result = await exportTool(client, { format: 'markdown' });
 *
 * if (result.success) {
 *   console.log(`Exported ${result.count} memories`);
 *   fs.writeFileSync('export.md', result.data);
 * }
 * ```
 */
export declare function exportTool(client: TotalReclaw, params?: ExportToolParams): Promise<ExportToolResult>;
/**
 * Create a bound export tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts ExportToolParams and returns ExportToolResult
 */
export declare function createExportTool(client: TotalReclaw): (params: ExportToolParams) => Promise<ExportToolResult>;
/**
 * Restore a Buffer from JSON-serialized format
 *
 * Useful for parsing exported JSON data.
 *
 * @param obj - Object that may contain serialized Buffers
 * @returns Object with restored Buffers
 */
export declare function restoreBuffers(obj: unknown): unknown;
export default exportTool;
//# sourceMappingURL=export.d.ts.map