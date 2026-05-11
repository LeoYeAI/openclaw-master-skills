"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfig = void 0;
const envOrDefault = (key, fallback) => process.env[key] ?? fallback;
const loadConfig = (providers = []) => ({
    maxPriceUsd: Number(envOrDefault('SCRAPER_MAX_PRICE_USD', '50')),
    minScore: Number(envOrDefault('SCRAPER_MIN_SCORE', '40')),
    scanIntervalMs: Number(envOrDefault('SCRAPER_SCAN_INTERVAL_MS', '300000')),
    providers,
    logLevel: envOrDefault('SCRAPER_LOG_LEVEL', 'info'),
});
exports.loadConfig = loadConfig;
//# sourceMappingURL=config.js.map