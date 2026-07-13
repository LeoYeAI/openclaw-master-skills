/**
 * Context storage for Lista Lending skill
 * Stores selected position and user info for session continuity
 */
export interface SelectedVault {
    address: string;
    name: string;
    asset: {
        symbol: string;
        address: string;
        decimals: number;
    };
    chain: string;
}
export interface UserPosition {
    shares: string;
    assets: string;
    assetsUsd?: string;
}
export interface SelectedMarket {
    marketId: string;
    chain: string;
    collateralSymbol?: string;
    loanSymbol?: string;
    zone?: number;
    termType?: number;
}
export declare enum TargetType {
    Vault = "vault",
    Market = "market"
}
export interface LastFilters {
    vaults?: Record<string, unknown>;
    markets?: Record<string, unknown>;
    holdings?: Record<string, unknown>;
}
export interface LendingContext {
    schemaVersion: number;
    selectedVault: SelectedVault | null;
    selectedMarket: SelectedMarket | null;
    userAddress: string | null;
    walletTopic: string | null;
    userPosition: UserPosition | null;
    lastFilters: LastFilters | null;
    lastUpdated: string | null;
}
/**
 * Load context from disk
 */
export declare function loadContext(): LendingContext;
/**
 * Save context to disk
 */
export declare function saveContext(context: LendingContext): void;
/**
 * Set selected vault
 */
export declare function setSelectedVault(vault: SelectedVault, userAddress: string, walletTopic: string, position?: UserPosition): void;
/**
 * Set selected market
 */
export declare function setSelectedMarket(market: SelectedMarket, userAddress: string, walletTopic: string): void;
/**
 * Update user position for selected vault
 */
export declare function updatePosition(position: UserPosition): void;
/**
 * Persist latest user-facing filters for vaults/markets/holdings.
 */
export declare function setLastFilters(filters: LastFilters): void;
/**
 * Clear selection context.
 */
export declare function clearContext(): void;
