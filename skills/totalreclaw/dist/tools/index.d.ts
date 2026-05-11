/**
 * TotalReclaw Skill - Tools Barrel Export
 *
 * This module exports all tool implementations for the TotalReclaw skill.
 * Each tool provides a specific capability for interacting with memories.
 *
 * ## Available Tools
 *
 * - **remember** - Store a new memory
 * - **recall** - Search and retrieve memories
 * - **forget** - Delete a specific memory
 * - **export** - Export all memories for portability
 *
 * ## Usage
 *
 * ```typescript
 * import {
 *   rememberTool,
 *   recallTool,
 *   forgetTool,
 *   exportTool,
 *   createRememberTool,
 *   createRecallTool,
 *   createForgetTool,
 *   createExportTool,
 * } from './tools';
 *
 * // Direct usage
 * const result = await rememberTool(client, { text: 'Important fact' });
 *
 * // Factory usage (pre-bound to client)
 * const remember = createRememberTool(client);
 * const result = await remember({ text: 'Important fact' });
 * ```
 *
 * ## Tool Results
 *
 * All tools return a result object with:
 * - `success: boolean` - Whether the operation succeeded
 * - `error?: string` - Error message if failed
 * - Tool-specific fields (e.g., `factId`, `results`, `data`)
 */
export { rememberTool, createRememberTool, type RememberToolResult, } from './remember';
export { recallTool, createRecallTool, formatRecallResults, type RecallToolResult, type RecallToolResultItem, } from './recall';
export { forgetTool, createForgetTool, type ForgetToolResult, } from './forget';
export { exportTool, createExportTool, restoreBuffers, type ExportToolResult, } from './export';
export { statusTool, createStatusTool, type StatusToolResult, } from './status';
export type { RememberToolParams, RecallToolParams, ForgetToolParams, ExportToolParams, } from '../types';
//# sourceMappingURL=index.d.ts.map