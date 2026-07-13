import type { ApiUserPositions } from "../types/lista-api.js";
import { fetchVaultPositions } from "./vault.js";
import { fetchMarketPositions } from "./market.js";

export async function fetchUserPositions(
  userAddress: string
): Promise<ApiUserPositions> {
  const [vaults, markets] = await Promise.all([
    fetchVaultPositions(userAddress),
    fetchMarketPositions(userAddress),
  ]);

  return {
    vaults,
    markets,
  };
}
