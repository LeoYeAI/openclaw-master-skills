import type { ApiMarketHoldingItem, ApiMarketPosition, ApiVaultHoldingItem, ApiVaultPosition } from "../types/lista-api.js";
export declare function mapVaultErrorPosition(holding: ApiVaultHoldingItem, chain: string, error: string): ApiVaultPosition;
export declare function mapMarketErrorPosition(holding: ApiMarketHoldingItem, chain: string, error: string): ApiMarketPosition;
