import type { ApiVaultItem, ApiVaultPosition, VaultListQuery } from "../types/lista-api.js";
export declare function fetchVaults(query?: VaultListQuery): Promise<ApiVaultItem[]>;
export declare function fetchVaultPositions(userAddress: string): Promise<ApiVaultPosition[]>;
