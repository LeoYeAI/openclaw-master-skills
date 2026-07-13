/**
 * API facade for vault, market and holdings queries.
 * Public imports keep using `./api.js` while internals are split by domain.
 */

export { fetchVaults, fetchVaultPositions } from "./api/vault.js";
export { fetchMarkets, fetchMarketPositions } from "./api/market.js";
export { fetchUserPositions } from "./api/user.js";
