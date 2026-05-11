/**
 * Debug logging utility for TotalReclaw Skill
 *
 * Logging is gated behind TOTALRECLAW_DEBUG=true (env var) OR an explicit
 * `enabled` override passed by callers that have their own debug flag.
 * Production builds are silent by default.
 */
/**
 * Log a debug message.
 *
 * Silent unless TOTALRECLAW_DEBUG=true OR the caller passes `enabled: true`.
 * The optional first boolean argument acts as a local override so that
 * hook-level `options.debug` flags still work.
 */
export declare function debugLog(enabled: boolean, ...args: unknown[]): void;
export declare function debugLog(...args: unknown[]): void;
//# sourceMappingURL=debug.d.ts.map