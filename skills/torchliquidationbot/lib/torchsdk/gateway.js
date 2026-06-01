"use strict";
/**
 * Gateway URL utilities for Irys content
 * Use uploader.irys.xyz as fallback when gateway.irys.xyz has issues
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.fetchWithFallback = exports.isIrysUrl = exports.irysToUploader = void 0;
const IRYS_GATEWAY = 'gateway.irys.xyz';
const IRYS_UPLOADER = 'uploader.irys.xyz';
/**
 * Convert an Irys gateway URL to uploader URL (fallback)
 */
const irysToUploader = (url) => url.replace(IRYS_GATEWAY, IRYS_UPLOADER);
exports.irysToUploader = irysToUploader;
/**
 * Check if URL is from Irys gateway
 */
const isIrysUrl = (url) => {
    try {
        return new URL(url).hostname === IRYS_GATEWAY;
    }
    catch {
        return false;
    }
};
exports.isIrysUrl = isIrysUrl;
/**
 * Fetch with automatic fallback from gateway.irys.xyz to uploader.irys.xyz
 */
const fetchWithFallback = async (url, options, timeoutMs = 10000) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const opts = { ...options, signal: controller.signal };
    try {
        // If it's an Irys gateway URL, use uploader directly (gateway has SSL issues)
        if ((0, exports.isIrysUrl)(url)) {
            const uploaderUrl = (0, exports.irysToUploader)(url);
            return await fetch(uploaderUrl, opts);
        }
        // For non-Irys URLs, fetch normally
        return await fetch(url, opts);
    }
    finally {
        clearTimeout(timer);
    }
};
exports.fetchWithFallback = fetchWithFallback;
//# sourceMappingURL=gateway.js.map