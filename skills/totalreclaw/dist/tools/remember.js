"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.rememberTool = rememberTool;
exports.createRememberTool = createRememberTool;
const client_1 = require("@totalreclaw/client");
/**
 * Default importance value (1-10 scale normalized to 0-1)
 */
const DEFAULT_IMPORTANCE = 7;
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
async function rememberTool(client, params) {
    // Validate input
    if (!params || typeof params.text !== 'string' || params.text.trim().length === 0) {
        return {
            success: false,
            error: 'Invalid input: text is required and must be a non-empty string',
        };
    }
    // Validate importance if provided
    if (params.importance !== undefined) {
        if (typeof params.importance !== 'number' || params.importance < 1 || params.importance > 10) {
            return {
                success: false,
                error: 'Invalid input: importance must be a number between 1 and 10',
            };
        }
    }
    // Validate type if provided
    const validTypes = ['fact', 'preference', 'decision', 'episodic', 'goal'];
    if (params.type !== undefined && !validTypes.includes(params.type)) {
        return {
            success: false,
            error: `Invalid input: type must be one of: ${validTypes.join(', ')}`,
        };
    }
    try {
        // Build metadata
        const metadata = {
            importance: (params.importance ?? DEFAULT_IMPORTANCE) / 10, // Normalize to 0-1
            source: 'explicit_tool',
        };
        // Add type as a tag if provided
        if (params.type) {
            metadata.tags = [params.type];
        }
        // Store the memory
        const factId = await client.remember(params.text.trim(), metadata);
        return {
            success: true,
            factId,
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
            error: `Failed to store memory: ${message}`,
        };
    }
}
/**
 * Create a bound remember tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts RememberToolParams and returns RememberToolResult
 */
function createRememberTool(client) {
    return (params) => rememberTool(client, params);
}
exports.default = rememberTool;
//# sourceMappingURL=remember.js.map