"use strict";
/**
 * Debug logging utility for TotalReclaw Skill
 *
 * Logging is gated behind TOTALRECLAW_DEBUG=true (env var) OR an explicit
 * `enabled` override passed by callers that have their own debug flag.
 * Production builds are silent by default.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.debugLog = debugLog;
const DEBUG = process.env.TOTALRECLAW_DEBUG === 'true';
function debugLog(...args) {
    let enabled;
    let rest;
    if (typeof args[0] === 'boolean') {
        enabled = args[0] || DEBUG;
        rest = args.slice(1);
    }
    else {
        enabled = DEBUG;
        rest = args;
    }
    if (enabled) {
        console.log('[TotalReclaw]', ...rest);
    }
}
//# sourceMappingURL=debug.js.map