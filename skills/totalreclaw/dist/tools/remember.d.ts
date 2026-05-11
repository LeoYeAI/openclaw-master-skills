/**
 * TotalReclaw Skill - Remember Tool
 *
 * Tool for explicitly storing memories in TotalReclaw.
 * This is the totalreclaw_remember tool implementation.
 *
 * @example
 * ```typescript
 * const result = await rememberTool(client, {
 *   text: 'User prefers dark mode in all applications',
 *   type: 'preference',
 *   importance: 8,
 * });
 * // result: { success: true, factId: '01234567-...' }
 * ```
 */
import type { TotalReclaw } from '@totalreclaw/client';
import type { RememberToolParams } from '../types';
/**
 * Result of the remember tool operation
 */
export interface RememberToolResult {
    /** Whether the operation succeeded */
    success: boolean;
    /** The ID of the stored fact (if successful) */
    factId?: string;
    /** Error message (if failed) */
    error?: string;
}
/**
 * Store a memory in TotalReclaw
 *
 * @param client - The TotalReclaw client instance
 * @param params - Tool parameters (text, type?, importance?)
 * @returns Result containing success status and fact ID
 *
 * @throws {TotalReclawError} If the client is not initialized or operation fails
 *
 * @example
 * ```typescript
 * // Basic usage
 * const result = await rememberTool(client, {
 *   text: 'User\'s favorite programming language is TypeScript',
 * });
 *
 * // With all options
 * const result = await rememberTool(client, {
 *   text: 'User is working on the TotalReclaw project',
 *   type: 'fact',
 *   importance: 9,
 * });
 * ```
 */
export declare function rememberTool(client: TotalReclaw, params: RememberToolParams): Promise<RememberToolResult>;
/**
 * Create a bound remember tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts RememberToolParams and returns RememberToolResult
 */
export declare function createRememberTool(client: TotalReclaw): (params: RememberToolParams) => Promise<RememberToolResult>;
export default rememberTool;
//# sourceMappingURL=remember.d.ts.map