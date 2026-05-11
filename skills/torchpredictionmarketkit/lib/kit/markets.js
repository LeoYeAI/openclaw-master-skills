"use strict";
/**
 * markets.ts — market CRUD, lifecycle, and on-chain operations.
 *
 * file-based state: markets.json is the source of truth.
 * each prediction market = a torch token on the bonding curve.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolveMarket = exports.snapshotMarket = exports.createMarket = exports.saveMarkets = exports.loadMarkets = void 0;
const fs = __importStar(require("fs"));
const torchsdk_1 = require("torchsdk");
const oracle_1 = require("./oracle");
const utils_1 = require("./utils");
const SDK_TIMEOUT_MS = 30000;
// --- input validation allowlists ---
const ALLOWED_METADATA_DOMAINS = new Set([
    'arweave.net',
    'www.arweave.net',
    'gateway.irys.xyz',
    'ipfs.io',
    'cloudflare-ipfs.com',
    'nftstorage.link',
    'dweb.link',
]);
const MAX_LIQUIDITY_LAMPORTS = 10000000000; // 10 SOL
const validateMetadataUri = (uri, marketId) => {
    let hostname;
    try {
        hostname = new URL(uri).hostname;
    }
    catch {
        throw new Error(`invalid metadataUri for market "${marketId}": ${uri}`);
    }
    if (!ALLOWED_METADATA_DOMAINS.has(hostname)) {
        throw new Error(`metadataUri domain "${hostname}" is not allowed for market "${marketId}". ` +
            `Allowed: ${[...ALLOWED_METADATA_DOMAINS].join(', ')}`);
    }
};
const validateLiquidity = (lamports, marketId) => {
    if (lamports < 0) {
        throw new Error(`initialLiquidityLamports cannot be negative for market "${marketId}"`);
    }
    if (lamports > MAX_LIQUIDITY_LAMPORTS) {
        throw new Error(`initialLiquidityLamports ${lamports} exceeds max ${MAX_LIQUIDITY_LAMPORTS} (10 SOL) for market "${marketId}"`);
    }
};
const loadMarkets = (path) => {
    if (!fs.existsSync(path))
        return [];
    const raw = fs.readFileSync(path, 'utf-8');
    const definitions = JSON.parse(raw);
    const markets = definitions.map((d) => ({
        ...d,
        mint: d.mint ?? null,
        status: d.status ?? 'pending',
        outcome: d.outcome ?? 'unresolved',
        createdAt: d.createdAt ?? null,
        resolvedAt: d.resolvedAt ?? null,
    }));
    const seen = new Set();
    for (const m of markets) {
        if (seen.has(m.id)) {
            throw new Error(`duplicate market id: "${m.id}" in ${path}`);
        }
        seen.add(m.id);
        // validate inputs on pending markets (already-created markets are not re-validated)
        if (m.status === 'pending') {
            validateMetadataUri(m.metadataUri, m.id);
            validateLiquidity(m.initialLiquidityLamports, m.id);
        }
    }
    return markets;
};
exports.loadMarkets = loadMarkets;
const saveMarkets = (path, markets) => {
    fs.writeFileSync(path, JSON.stringify(markets, null, 2) + '\n', 'utf-8');
};
exports.saveMarkets = saveMarkets;
const createMarket = async (connection, market, agentKeypair, vaultCreator) => {
    // create the torch token
    const createResult = await (0, utils_1.withTimeout)((0, torchsdk_1.buildCreateTokenTransaction)(connection, {
        creator: agentKeypair.publicKey.toBase58(),
        name: market.name,
        symbol: market.symbol,
        metadata_uri: market.metadataUri,
    }), SDK_TIMEOUT_MS, 'buildCreateTokenTransaction');
    createResult.transaction.sign(agentKeypair);
    const createSig = await (0, utils_1.withTimeout)(connection.sendRawTransaction(createResult.transaction.serialize()), SDK_TIMEOUT_MS, 'sendRawTransaction(create)');
    await (0, utils_1.withTimeout)((0, torchsdk_1.confirmTransaction)(connection, createSig, agentKeypair.publicKey.toBase58()), SDK_TIMEOUT_MS, 'confirmTransaction(create)');
    const mintAddress = createResult.mint.toBase58();
    // seed liquidity via vault buy
    if (market.initialLiquidityLamports > 0) {
        const buyResult = await (0, utils_1.withTimeout)((0, torchsdk_1.buildBuyTransaction)(connection, {
            mint: mintAddress,
            buyer: agentKeypair.publicKey.toBase58(),
            amount_sol: market.initialLiquidityLamports,
            slippage_bps: 500,
            vault: vaultCreator,
        }), SDK_TIMEOUT_MS, 'buildBuyTransaction');
        buyResult.transaction.sign(agentKeypair);
        const buySig = await (0, utils_1.withTimeout)(connection.sendRawTransaction(buyResult.transaction.serialize()), SDK_TIMEOUT_MS, 'sendRawTransaction(buy)');
        await (0, utils_1.withTimeout)((0, torchsdk_1.confirmTransaction)(connection, buySig, agentKeypair.publicKey.toBase58()), SDK_TIMEOUT_MS, 'confirmTransaction(buy)');
        // v3.7.22: if the buy completed the bonding curve, send the migration transaction
        if (buyResult.migrationTransaction) {
            buyResult.migrationTransaction.sign(agentKeypair);
            const migSig = await (0, utils_1.withTimeout)(connection.sendRawTransaction(buyResult.migrationTransaction.serialize()), SDK_TIMEOUT_MS, 'sendRawTransaction(migrate)');
            await (0, utils_1.withTimeout)((0, torchsdk_1.confirmTransaction)(connection, migSig, agentKeypair.publicKey.toBase58()), SDK_TIMEOUT_MS, 'confirmTransaction(migrate)');
        }
    }
    return mintAddress;
};
exports.createMarket = createMarket;
const snapshotMarket = async (connection, market) => {
    if (!market.mint)
        return null;
    const token = await (0, utils_1.withTimeout)((0, torchsdk_1.getToken)(connection, market.mint), SDK_TIMEOUT_MS, 'getToken');
    const { holders: holdersList } = await (0, utils_1.withTimeout)((0, torchsdk_1.getHolders)(connection, market.mint), SDK_TIMEOUT_MS, 'getHolders');
    return {
        marketId: market.id,
        mint: market.mint,
        price: token.price_sol,
        marketCap: token.market_cap_sol,
        volume: token.sol_raised ?? 0,
        treasuryBalance: token.treasury_sol_balance ?? 0,
        holders: holdersList.length,
        timestamp: Date.now(),
    };
};
exports.snapshotMarket = snapshotMarket;
const resolveMarket = async (market) => {
    return (0, oracle_1.checkOracle)(market.oracle);
};
exports.resolveMarket = resolveMarket;
//# sourceMappingURL=markets.js.map