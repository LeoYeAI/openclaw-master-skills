"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runMonitor = void 0;
const web3_js_1 = require("@solana/web3.js");
const torchsdk_1 = require("torchsdk");
const scanner_1 = require("./scanner");
const wallet_profiler_1 = require("./wallet-profiler");
const risk_scorer_1 = require("./risk-scorer");
const liquidator_1 = require("./liquidator");
const domain_manager_1 = require("./domain-manager");
const logger_1 = require("./logger");
const utils_1 = require("./utils");
const runMonitor = async (config, domainTokens = []) => {
    const log = new logger_1.Logger('monitor', config.logLevel);
    const connection = new web3_js_1.Connection(config.rpcUrl, 'confirmed');
    const profiler = new wallet_profiler_1.WalletProfiler(log.child('profiler'));
    const liquidator = new liquidator_1.Liquidator(config, log.child('liquidator'));
    let tokens = new Map();
    let leases = [];
    log.info('domain auction bot monitor starting');
    while (true) {
        try {
            // scan for lending markets
            tokens = await (0, scanner_1.scanForLendingMarkets)(connection, tokens, config.priceHistoryDepth, log.child('scanner'));
            // update domain leases (check top holders, expire/rotate)
            if (domainTokens.length > 0) {
                leases = await (0, domain_manager_1.updateLeases)(connection, domainTokens, leases, log.child('leases'));
            }
            // score and attempt liquidation for each token with borrowers
            for (const [mint, token] of tokens) {
                if (!token.lendingInfo.active_loans || token.lendingInfo.active_loans === 0)
                    continue;
                // update price
                try {
                    const detail = await (0, utils_1.withTimeout)((0, torchsdk_1.getToken)(connection, mint), 30000, 'getToken');
                    const newPrice = detail.price_sol / torchsdk_1.LAMPORTS_PER_SOL;
                    token.priceHistory.push(newPrice);
                    if (token.priceHistory.length > config.priceHistoryDepth) {
                        token.priceHistory.shift();
                    }
                    token.priceSol = newPrice;
                }
                catch {
                    log.debug(`price update failed for ${token.symbol}`);
                }
                // score all active borrowers via bulk scan
                try {
                    const { positions } = await (0, utils_1.withTimeout)((0, torchsdk_1.getAllLoanPositions)(connection, mint), 30000, 'getAllLoanPositions');
                    for (const pos of positions) {
                        try {
                            const profile = await profiler.profile(connection, pos.borrower, mint);
                            const scored = (0, risk_scorer_1.scoreLoan)(token, pos.borrower, pos, profile);
                            log.info(`${token.symbol} — ${pos.borrower.slice(0, 8)}... risk=${scored.riskScore} health=${pos.health}`);
                            await liquidator.tryLiquidate(connection, scored);
                        }
                        catch (err) {
                            log.debug(`error scoring ${pos.borrower.slice(0, 8)}...`, err);
                        }
                    }
                }
                catch (err) {
                    log.debug(`bulk loan scan failed for ${token.symbol}`, err);
                }
            }
        }
        catch (err) {
            log.error('monitor tick failed', err);
        }
        await (0, utils_1.sleep)(config.scoreIntervalMs);
    }
};
exports.runMonitor = runMonitor;
//# sourceMappingURL=monitor.js.map