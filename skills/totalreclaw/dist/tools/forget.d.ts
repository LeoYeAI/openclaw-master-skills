/**
 * TotalReclaw Skill - Forget Tool
 *
 * Tool for deleting memories from TotalReclaw.
 * This is the totalreclaw_forget tool implementation.
 *
 * @example
 * ```typescript
 * const result = await forgetTool(client, {
 *   factId: '01234567-89ab-cdef-0123-456789abcdef',
 * });
 * // result: { success: true }
 * ```
 */
import type { TotalReclaw } from '@totalreclaw/client';
import type { ForgetToolParams } from '../types';
/**
 * Result of the forget tool operation
 */
export interface ForgetToolResult {
    /** Whether the operation succeeded */
    success: boolean;
    /** The ID of the deleted fact (if successful) */
    factId?: string;
    /** Error message (if failed) */
    error?: string;
}
/**
 * Delete a memory from TotalReclaw
 *
 * @param client - The TotalReclaw client instance
 * @param params - Tool parameters (factId)
 * @returns Result containing success status
 *
 * @throws {TotalReclawError} If the client is not initialized or operation fails
 *
 * @example
 * ```typescript
 * // Delete a specific memory
 * const result = await forgetTool(client, {
 *   factId: '018d4c7a-1234-7abc-8def-0123456789ab',
 * });
 *
 * if (result.success) {
 *   console.log(`Memory ${result.factId} deleted successfully`);
 * } else {
 *   console.error(`Failed to delete: ${result.error}`);
 * }
 * ```
 */
export declare function forgetTool(client: TotalReclaw, params: ForgetToolParams): Promise<ForgetToolResult>;
/**
 * Create a bound forget tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts ForgetToolParams and returns ForgetToolResult
 */
export declare function createForgetTool(client: TotalReclaw): (params: ForgetToolParams) => Promise<ForgetToolResult>;
export default forgetTool;
//# sourceMappingURL=forget.d.ts.map