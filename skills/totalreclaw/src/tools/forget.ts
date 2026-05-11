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
import { TotalReclawError, TotalReclawErrorCode } from '@totalreclaw/client';

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
 * UUID v7 regex pattern for validation
 * Matches format: xxxxxxxx-xxxx-7xxx-xxxx-xxxxxxxxxxxx
 */
const UUID_V7_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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
export async function forgetTool(
  client: TotalReclaw,
  params: ForgetToolParams
): Promise<ForgetToolResult> {
  // Validate input
  if (!params || typeof params.factId !== 'string' || params.factId.trim().length === 0) {
    return {
      success: false,
      error: 'Invalid input: factId is required and must be a non-empty string',
    };
  }

  const factId = params.factId.trim();

  // Validate UUID format (loose validation - allow any UUID format)
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidPattern.test(factId)) {
    return {
      success: false,
      error: 'Invalid input: factId must be a valid UUID format (e.g., 01234567-89ab-cdef-0123-456789abcdef)',
    };
  }

  try {
    // Delete the memory
    await client.forget(factId);

    return {
      success: true,
      factId,
    };
  } catch (error) {
    // Handle known error types
    if (error instanceof TotalReclawError) {
      // Map specific error codes to user-friendly messages
      switch (error.code) {
        case TotalReclawErrorCode.NOT_REGISTERED:
          return {
            success: false,
            error: 'Client not authenticated. Please initialize the client first.',
          };
        case TotalReclawErrorCode.AUTH_FAILED:
          return {
            success: false,
            error: 'Authentication failed. Unable to delete memory.',
          };
        case TotalReclawErrorCode.NETWORK_ERROR:
          return {
            success: false,
            error: 'Network error. Please check your connection and try again.',
          };
        default:
          return {
            success: false,
            error: `TotalReclaw error (${error.code}): ${error.message}`,
          };
      }
    }

    // Handle unknown errors
    const message = error instanceof Error ? error.message : 'Unknown error occurred';
    return {
      success: false,
      error: `Failed to forget memory: ${message}`,
    };
  }
}

/**
 * Create a bound forget tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts ForgetToolParams and returns ForgetToolResult
 */
export function createForgetTool(client: TotalReclaw): (params: ForgetToolParams) => Promise<ForgetToolResult> {
  return (params: ForgetToolParams) => forgetTool(client, params);
}

export default forgetTool;
