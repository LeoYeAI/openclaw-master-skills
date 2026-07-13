/**
 * Configuration storage for Lista Lending skill
 * Stores RPC URLs and other settings in ~/.agent-wallet/lending-config.json
 */
export declare const DEFAULT_RPCS: Record<string, string[]>;
export declare const CHAIN_IDS: Record<string, number>;
export declare const SUPPORTED_CHAINS: string[];
export interface LendingConfig {
    rpcUrls: Record<string, string>;
    defaultChain: string;
}
/**
 * Load config from disk
 */
export declare function loadConfig(): LendingConfig;
/**
 * Save config to disk
 */
export declare function saveConfig(config: LendingConfig): void;
/**
 * Get RPC URL for a chain (custom override > default)
 */
export declare function getRpcUrl(chain: string): string;
/**
 * Get all RPC URLs for a chain (for fallback)
 */
export declare function getRpcUrls(chain: string): string[];
/**
 * Set custom RPC URL for a chain
 */
export declare function setRpcUrl(chain: string, url: string): void;
/**
 * Clear custom RPC URL (revert to default)
 */
export declare function clearRpcUrl(chain: string): void;
/**
 * Get chain ID number from CAIP-2 format
 */
export declare function getChainId(chain: string): number;
/**
 * Check if using custom RPC (vs default public RPC)
 */
export declare function isUsingCustomRpc(chain: string): boolean;
/**
 * RPC configuration type
 */
export type RpcType = "public" | "custom";
/**
 * Get RPC type for a chain
 */
export declare function getRpcType(chain: string): RpcType;
/**
 * Get optimized concurrency and timeout settings based on RPC type
 */
export interface RpcConfig {
    type: RpcType;
    vaultConcurrency: number;
    marketConcurrency: number;
    itemTimeout: number;
    totalBudget: number;
    retryCount: number;
    retryDelay: number;
}
export declare function getRpcConfig(chain: string): RpcConfig;
