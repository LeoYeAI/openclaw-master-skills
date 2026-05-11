"use strict";
/**
 * oracle.ts — resolution logic for prediction markets.
 *
 * price_feed: fetches current price from CoinGecko public API.
 * manual: returns 'unresolved' (resolved by editing markets.json directly).
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkOracle = exports.checkPriceFeed = void 0;
const COINGECKO_API = 'https://api.coingecko.com/api/v3/simple/price';
const ALLOWED_ORACLE_ASSETS = new Set([
    'solana',
    'bitcoin',
    'ethereum',
    'binancecoin',
    'ripple',
    'cardano',
    'dogecoin',
    'polkadot',
    'avalanche-2',
    'chainlink',
    'uniswap',
    'litecoin',
    'near',
    'aptos',
    'sui',
    'arbitrum',
    'optimism',
    'celestia',
    'jupiter-exchange-solana',
    'render-token',
    'bonk',
    'jito-governance-token',
    'raydium',
    'pyth-network',
    'helium',
    'tether',
    'usd-coin',
]);
const checkPriceFeed = async (oracle) => {
    if (!ALLOWED_ORACLE_ASSETS.has(oracle.asset)) {
        throw new Error(`oracle asset "${oracle.asset}" is not in the allowlist. ` +
            `Allowed: ${[...ALLOWED_ORACLE_ASSETS].join(', ')}`);
    }
    const url = `${COINGECKO_API}?ids=${oracle.asset}&vs_currencies=usd`;
    const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (!res.ok) {
        throw new Error(`CoinGecko API error: ${res.status} ${res.statusText}`);
    }
    const data = (await res.json());
    const price = data[oracle.asset]?.usd;
    if (price == null) {
        throw new Error(`no price data for asset: ${oracle.asset}`);
    }
    if (oracle.condition === 'above') {
        return price > oracle.target ? 'yes' : 'no';
    }
    return price < oracle.target ? 'yes' : 'no';
};
exports.checkPriceFeed = checkPriceFeed;
const checkOracle = async (oracle) => {
    if (oracle.type === 'price_feed') {
        return (0, exports.checkPriceFeed)(oracle);
    }
    // manual oracle — resolved by editing markets.json directly
    return 'unresolved';
};
exports.checkOracle = checkOracle;
//# sourceMappingURL=oracle.js.map