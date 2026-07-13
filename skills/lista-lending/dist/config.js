/**
 * Configuration storage for Lista Lending skill
 * Stores RPC URLs and other settings in ~/.agent-wallet/lending-config.json
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
const CONFIG_DIR = join(homedir(), ".agent-wallet");
const CONFIG_FILE = join(CONFIG_DIR, "lending-config.json");
// Default public RPC endpoints with fallbacks
export const DEFAULT_RPCS = {
    "eip155:56": [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.bnbchain.org",
        "https://bsc-dataseed2.bnbchain.org",
        "https://bsc-dataseed3.bnbchain.org",
        "https://bsc-rpc.publicnode.com",
        "https://bsc-dataseed1.binance.org",
    ],
    "eip155:1": [
        "https://eth.drpc.org",
        "https://mainnet.gateway.tenderly.co",
        "https://ethereum-rpc.publicnode.com",
        "https://cloudflare-eth.com",
        "https://eth.llamarpc.com",
    ],
};
// Chain ID mapping
export const CHAIN_IDS = {
    "eip155:56": 56,
    "eip155:1": 1,
};
export const SUPPORTED_CHAINS = ["eip155:56", "eip155:1"];
const DEFAULT_CONFIG = {
    rpcUrls: {},
    defaultChain: "eip155:56",
};
/**
 * Ensure config directory exists
 */
function ensureConfigDir() {
    if (!existsSync(CONFIG_DIR)) {
        mkdirSync(CONFIG_DIR, { recursive: true });
    }
}
/**
 * Load config from disk
 */
export function loadConfig() {
    try {
        if (existsSync(CONFIG_FILE)) {
            const data = readFileSync(CONFIG_FILE, "utf-8");
            const parsed = JSON.parse(data);
            return {
                ...DEFAULT_CONFIG,
                ...parsed,
            };
        }
    }
    catch {
        // Ignore errors, return default
    }
    return { ...DEFAULT_CONFIG };
}
/**
 * Save config to disk
 */
export function saveConfig(config) {
    ensureConfigDir();
    writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}
/**
 * Get RPC URL for a chain (custom override > default)
 */
export function getRpcUrl(chain) {
    const candidates = getRpcUrls(chain);
    if (candidates.length > 0) {
        return candidates[0];
    }
    throw new Error(`No RPC URL configured for chain: ${chain}`);
}
/**
 * Get all RPC URLs for a chain (for fallback)
 */
export function getRpcUrls(chain) {
    const config = loadConfig();
    const result = [];
    const seen = new Set();
    const addUrl = (value) => {
        if (!value)
            return;
        const normalized = value.trim();
        if (!normalized || seen.has(normalized))
            return;
        seen.add(normalized);
        result.push(normalized);
    };
    // Custom override takes priority, but keep defaults as fallbacks.
    addUrl(config.rpcUrls[chain]);
    const defaults = DEFAULT_RPCS[chain] || [];
    for (const url of defaults) {
        addUrl(url);
    }
    return result;
}
/**
 * Set custom RPC URL for a chain
 */
export function setRpcUrl(chain, url) {
    if (!SUPPORTED_CHAINS.includes(chain)) {
        throw new Error(`Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`);
    }
    const config = loadConfig();
    config.rpcUrls[chain] = url;
    saveConfig(config);
}
/**
 * Clear custom RPC URL (revert to default)
 */
export function clearRpcUrl(chain) {
    const config = loadConfig();
    delete config.rpcUrls[chain];
    saveConfig(config);
}
/**
 * Get chain ID number from CAIP-2 format
 */
export function getChainId(chain) {
    const chainId = CHAIN_IDS[chain];
    if (!chainId) {
        throw new Error(`Unknown chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`);
    }
    return chainId;
}
/**
 * Check if using custom RPC (vs default public RPC)
 */
export function isUsingCustomRpc(chain) {
    const config = loadConfig();
    return !!config.rpcUrls[chain];
}
/**
 * Get RPC type for a chain
 */
export function getRpcType(chain) {
    return isUsingCustomRpc(chain) ? "custom" : "public";
}
export function getRpcConfig(chain) {
    const type = getRpcType(chain);
    if (type === "custom") {
        return {
            type: "custom",
            vaultConcurrency: 5,
            marketConcurrency: 3,
            itemTimeout: 8000,
            totalBudget: 35000,
            retryCount: 2,
            retryDelay: 500,
        };
    }
    // Public RPC: conservative settings to avoid rate limits
    return {
        type: "public",
        vaultConcurrency: 2,
        marketConcurrency: 1,
        itemTimeout: 12000,
        totalBudget: 70000,
        retryCount: 3,
        retryDelay: 800,
    };
}
