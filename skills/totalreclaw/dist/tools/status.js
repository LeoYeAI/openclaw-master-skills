"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.statusTool = statusTool;
exports.createStatusTool = createStatusTool;
const debug_1 = require("../debug");
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
async function statusTool(serverUrl, authKeyHex, walletAddress) {
    if (!serverUrl) {
        return {
            success: false,
            error: 'Server URL is not configured',
        };
    }
    if (!authKeyHex) {
        return {
            success: false,
            error: 'Auth credentials are not available. Please initialize the skill first.',
        };
    }
    try {
        const baseUrl = `${serverUrl.replace(/\/+$/, '')}/v1/billing/status`;
        const url = walletAddress ? `${baseUrl}?wallet_address=${encodeURIComponent(walletAddress)}` : baseUrl;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authKeyHex}`,
                'Accept': 'application/json',
            },
        });
        if (!response.ok) {
            const body = await response.text().catch(() => '');
            return {
                success: false,
                error: `Failed to fetch billing status (HTTP ${response.status}): ${body || response.statusText}`,
            };
        }
        const data = await response.json();
        const tier = data.tier || 'free';
        const freeWritesUsed = data.free_writes_used ?? 0;
        const freeWritesLimit = data.free_writes_limit ?? 0;
        const freeReadsUsed = data.free_reads_used ?? 0;
        const freeReadsLimit = data.free_reads_limit ?? 0;
        const freeWritesResetAt = data.free_writes_reset_at;
        const upgradeUrl = data.upgrade_url;
        // Build formatted summary
        const tierLabel = tier === 'pro' ? 'Pro' : 'Free';
        const lines = [
            `Tier: ${tierLabel}`,
            `Writes: ${freeWritesUsed}/${freeWritesLimit} used`,
            `Reads: ${freeReadsUsed}/${freeReadsLimit} used`,
        ];
        if (freeWritesResetAt) {
            lines.push(`Resets: ${new Date(freeWritesResetAt).toLocaleDateString()}`);
        }
        if (tier !== 'pro' && upgradeUrl) {
            lines.push(`Upgrade: ${upgradeUrl}`);
        }
        return {
            success: true,
            tier,
            free_writes_used: freeWritesUsed,
            free_writes_limit: freeWritesLimit,
            free_reads_used: freeReadsUsed,
            free_reads_limit: freeReadsLimit,
            free_writes_reset_at: freeWritesResetAt,
            upgrade_url: upgradeUrl,
            formatted: lines.join('\n'),
        };
    }
    catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error occurred';
        (0, debug_1.debugLog)(`Status tool failed: ${message}`);
        return {
            success: false,
            error: `Failed to check billing status: ${message}`,
        };
    }
}
/**
 * Create a bound status tool function
 *
 * Useful for creating a tool that's pre-bound to server URL and auth key.
 *
 * @param serverUrl - The TotalReclaw server URL
 * @param authKeyHex - Hex-encoded auth key for Bearer token
 * @returns A function that returns StatusToolResult
 */
function createStatusTool(serverUrl, authKeyHex, walletAddress) {
    return () => statusTool(serverUrl, authKeyHex, walletAddress);
}
exports.default = statusTool;
//# sourceMappingURL=status.js.map