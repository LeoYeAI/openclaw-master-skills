import { fetchVaultPositions } from "./vault.js";
import { fetchMarketPositions } from "./market.js";
export async function fetchUserPositions(userAddress) {
    const [vaults, markets] = await Promise.all([
        fetchVaultPositions(userAddress),
        fetchMarketPositions(userAddress),
    ]);
    return {
        vaults,
        markets,
    };
}
