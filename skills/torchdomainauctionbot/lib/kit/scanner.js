"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.scanForLendingMarkets = void 0;
const torchsdk_1 = require("torchsdk");
const utils_1 = require("./utils");
const MAX_PRICE_HISTORY = 50;
/**
 * Discover all active borrowers for a token using bulk loan scanner.
 * Returns all borrower addresses with open positions (not just top-20 holders).
 */
const discoverBorrowers = async (connection, mint, log) => {
    try {
        const { positions } = await (0, utils_1.withTimeout)((0, torchsdk_1.getAllLoanPositions)(connection, mint), 30000, 'getAllLoanPositions');
        return positions.map((p) => p.borrower);
    }
    catch (err) {
        log.debug(`borrower discovery failed for ${mint.slice(0, 8)}...: ${err}`);
        return [];
    }
};
/**
 * Scan for tokens with active lending markets.
 * Discovers migrated tokens, builds MonitoredToken entries, and probes for borrowers.
 */
const scanForLendingMarkets = async (connection, existing, depth, log) => {
    const tokens = new Map(existing);
    log.info(`scanning for lending markets (depth=${depth})`);
    try {
        const result = await (0, utils_1.withTimeout)((0, torchsdk_1.getTokens)(connection, {
            status: 'migrated',
            limit: depth,
            sort: 'newest',
        }), 30000, 'getTokens');
        log.info(`found ${result.tokens.length} migrated tokens`);
        for (const summary of result.tokens) {
            try {
                // skip if recently scanned
                const prev = tokens.get(summary.mint);
                if (prev && Date.now() - prev.lastScanned < 30000)
                    continue;
                const detail = await (0, utils_1.withTimeout)((0, torchsdk_1.getToken)(connection, summary.mint), 30000, 'getToken');
                const lending = await (0, utils_1.withTimeout)((0, torchsdk_1.getLendingInfo)(connection, summary.mint), 30000, 'getLendingInfo');
                const priceSol = detail.price_sol / torchsdk_1.LAMPORTS_PER_SOL;
                const prevHistory = prev?.priceHistory ?? [];
                const trimmedHistory = [...prevHistory, priceSol].slice(-MAX_PRICE_HISTORY);
                // discover borrowers when there are active loans
                let borrowers = prev?.activeBorrowers ?? [];
                if (lending.active_loans && lending.active_loans > 0) {
                    borrowers = await discoverBorrowers(connection, summary.mint, log);
                    log.info(`${detail.symbol}: ${lending.active_loans} active loans, ${borrowers.length} borrowers found, price=${priceSol.toFixed(8)} SOL`);
                }
                tokens.set(summary.mint, {
                    mint: summary.mint,
                    name: detail.name,
                    symbol: detail.symbol,
                    lendingInfo: lending,
                    priceSol,
                    priceHistory: trimmedHistory,
                    activeBorrowers: borrowers,
                    lastScanned: Date.now(),
                });
            }
            catch (err) {
                log.debug(`skipping ${summary.mint}: ${err}`);
            }
        }
    }
    catch (err) {
        log.error('scan failed', err);
    }
    return tokens;
};
exports.scanForLendingMarkets = scanForLendingMarkets;
//# sourceMappingURL=scanner.js.map