"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.decodeBase58 = exports.withTimeout = exports.clamp = exports.bpsToPercent = exports.sol = exports.sleep = void 0;
const web3_js_1 = require("@solana/web3.js");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
exports.sleep = sleep;
const sol = (lamports) => (lamports / web3_js_1.LAMPORTS_PER_SOL).toFixed(4);
exports.sol = sol;
const bpsToPercent = (bps) => (bps / 100).toFixed(2) + '%';
exports.bpsToPercent = bpsToPercent;
const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
exports.clamp = clamp;
const withTimeout = (promise, ms, label) => {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error(`timeout after ${ms}ms: ${label}`)), ms);
        promise.then((val) => { clearTimeout(timer); resolve(val); }, (err) => { clearTimeout(timer); reject(err); });
    });
};
exports.withTimeout = withTimeout;
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
//# sourceMappingURL=utils.js.map