/**
 * TotalReclaw Skill - Status Tool
 *
 * Tool for checking billing/subscription status in TotalReclaw.
 * This is the totalreclaw_status tool implementation.
 *
 * Unlike other tools that use the TotalReclaw client (protobuf API),
 * this tool calls the REST billing endpoint directly.
 *
 * @example
 * ```typescript
 * const result = await statusTool('https://api.totalreclaw.xyz', 'deadbeef...');
 * // result: { success: true, tier: 'free', formatted: '...' }
 * ```
 */
/**
 * Result of the status tool operation
 */
export interface StatusToolResult {
    /** Whether the operation succeeded */
    success: boolean;
    /** Current subscription tier */
    tier?: string;
    /** Number of writes used this month */
    free_writes_used?: number;
    /** Monthly write limit */
    free_writes_limit?: number;
    /** Number of reads used this month */
    free_reads_used?: number;
    /** Monthly read limit */
    free_reads_limit?: number;
    /** When the free tier counters reset */
    free_writes_reset_at?: string;
    /** Upgrade URL (if on free tier) */
    upgrade_url?: string;
    /** Human-readable formatted summary */
    formatted?: string;
    /** Error message (if failed) */
    error?: string;
}
/**
 * Fetch billing/subscription status from the TotalReclaw server
 *
 * @param serverUrl - The TotalReclaw server URL
 * @param authKeyHex - Hex-encoded auth key for Bearer token
 * @returns Result containing success status and billing information
 *
 * @example
 * ```typescript
 * const result = await statusTool(
 *   'https://api.totalreclaw.xyz',
 *   'deadbeef0123456789abcdef...',
 * );
 *
 * if (result.success) {
 *   console.log(result.formatted);
 * }
 * ```
 */
export declare function statusTool(serverUrl: string, authKeyHex: string, walletAddress?: string): Promise<StatusToolResult>;
/**
 * Create a bound status tool function
 *
 * Useful for creating a tool that's pre-bound to server URL and auth key.
 *
 * @param serverUrl - The TotalReclaw server URL
 * @param authKeyHex - Hex-encoded auth key for Bearer token
 * @returns A function that returns StatusToolResult
 */
export declare function createStatusTool(serverUrl: string, authKeyHex: string, walletAddress?: string): () => Promise<StatusToolResult>;
export default statusTool;
//# sourceMappingURL=status.d.ts.map