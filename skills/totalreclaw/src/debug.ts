/**
 * Debug logging utility for TotalReclaw Skill
 *
 * Logging is gated behind TOTALRECLAW_DEBUG=true (env var) OR an explicit
 * `enabled` override passed by callers that have their own debug flag.
 * Production builds are silent by default.
 */

const DEBUG = process.env.TOTALRECLAW_DEBUG === 'true';

/**
 * Log a debug message.
 *
 * Silent unless TOTALRECLAW_DEBUG=true OR the caller passes `enabled: true`.
 * The optional first boolean argument acts as a local override so that
 * hook-level `options.debug` flags still work.
 */
export function debugLog(enabled: boolean, ...args: unknown[]): void;
export function debugLog(...args: unknown[]): void;
export function debugLog(...args: unknown[]): void {
  let enabled: boolean;
  let rest: unknown[];

  if (typeof args[0] === 'boolean') {
    enabled = args[0] || DEBUG;
    rest = args.slice(1);
  } else {
    enabled = DEBUG;
    rest = args;
  }

  if (enabled) {
    console.log('[TotalReclaw]', ...rest);
  }
}
