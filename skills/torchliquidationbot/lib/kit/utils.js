"use strict";
/**
 * utils.ts — shared helpers.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.decodeBase58 = exports.bpsToPercent = exports.sol = void 0;
exports.withTimeout = withTimeout;
exports.createLogger = createLogger;
const torchsdk_1 = require("torchsdk");
const sol = (lamports) => (lamports / torchsdk_1.LAMPORTS_PER_SOL).toFixed(4);
exports.sol = sol;
const bpsToPercent = (bps) => (bps / 100).toFixed(2) + '%';
exports.bpsToPercent = bpsToPercent;
// base58 decoder — avoids ESM-only bs58 dependency
const B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const decodeBase58 = (s) => {
    const result = [];
    for (let i = 0; i < s.length; i++) {
        let carry = B58.indexOf(s[i]);
        if (carry < 0)
            throw new Error(`invalid base58 character: ${s[i]}`);
        for (let j = 0; j < result.length; j++) {
            carry += result[j] * 58;
            result[j] = carry & 0xff;
            carry >>= 8;
        }
        while (carry > 0) {
            result.push(carry & 0xff);
            carry >>= 8;
        }
    }
    for (let i = 0; i < s.length && s[i] === '1'; i++) {
        result.push(0);
    }
    return new Uint8Array(result.reverse());
};
exports.decodeBase58 = decodeBase58;
const RPC_TIMEOUT_MS = 30000;
function withTimeout(promise, label) {
    return Promise.race([
        promise,
        new Promise((_, reject) => setTimeout(() => reject(new Error(`${label} timed out after ${RPC_TIMEOUT_MS}ms`)), RPC_TIMEOUT_MS)),
    ]);
}
const LEVEL_ORDER = ['debug', 'info', 'warn', 'error'];
function createLogger(minLevel) {
    const minIdx = LEVEL_ORDER.indexOf(minLevel);
    return function log(level, msg) {
        if (LEVEL_ORDER.indexOf(level) < minIdx)
            return;
        const ts = new Date().toISOString().substr(11, 12);
        const tag = level.toUpperCase().padEnd(5);
        console.log(`[${ts}] ${tag} ${msg}`);
    };
}
//# sourceMappingURL=utils.js.map