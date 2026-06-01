"use strict";
/**
 * config.ts — loads environment variables into a typed BotConfig.
 *
 * env vars:
 *   SOLANA_RPC_URL    — solana RPC endpoint (required, fallback: RPC_URL)
 *   VAULT_CREATOR     — vault creator pubkey (required)
 *   SOLANA_PRIVATE_KEY — disposable controller keypair, base58 (optional)
 *   SCAN_INTERVAL_MS  — ms between scan cycles (default 30000, min 5000)
 *   LOG_LEVEL         — debug | info | warn | error (default info)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfig = void 0;
const LOG_LEVELS = ['debug', 'info', 'warn', 'error'];
const loadConfig = () => {
    const rpcUrl = process.env.SOLANA_RPC_URL ?? process.env.RPC_URL;
    if (!rpcUrl)
        throw new Error('SOLANA_RPC_URL env var is required (fallback: RPC_URL)');
    const vaultCreator = process.env.VAULT_CREATOR;
    if (!vaultCreator)
        throw new Error('VAULT_CREATOR env var is required (vault creator pubkey)');
    const privateKey = process.env.SOLANA_PRIVATE_KEY ?? null;
    const scanIntervalMs = parseInt(process.env.SCAN_INTERVAL_MS ?? '30000', 10);
    if (isNaN(scanIntervalMs) || scanIntervalMs < 5000) {
        throw new Error('SCAN_INTERVAL_MS must be a number >= 5000');
    }
    const logLevel = (process.env.LOG_LEVEL ?? 'info');
    if (!LOG_LEVELS.includes(logLevel)) {
        throw new Error(`LOG_LEVEL must be one of: ${LOG_LEVELS.join(', ')}`);
    }
    return { rpcUrl, vaultCreator, privateKey, scanIntervalMs, logLevel };
};
exports.loadConfig = loadConfig;
//# sourceMappingURL=config.js.map