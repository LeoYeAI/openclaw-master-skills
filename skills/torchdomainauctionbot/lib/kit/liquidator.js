"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Liquidator = void 0;
const torchsdk_1 = require("torchsdk");
const utils_1 = require("./utils");
class Liquidator {
    constructor(config, log) {
        /**
         * Attempt to liquidate a scored loan position.
         * Returns null if the position should be skipped (healthy, not profitable, below threshold).
         */
        this.tryLiquidate = async (connection, scored) => {
            // skip healthy positions
            if (scored.position.health === 'healthy') {
                this.log.debug(`skipping ${scored.borrower.slice(0, 8)}... — position is healthy`);
                return null;
            }
            // skip if risk score below threshold
            if (scored.riskScore < this.config.riskThreshold) {
                this.log.debug(`skipping ${scored.borrower.slice(0, 8)}... — risk ${scored.riskScore} < threshold ${this.config.riskThreshold}`);
                return null;
            }
            // skip if not profitable enough
            if (scored.estimatedProfitLamports < this.config.minProfitLamports) {
                this.log.debug(`skipping ${scored.borrower.slice(0, 8)}... — profit ${scored.estimatedProfitLamports} < min ${this.config.minProfitLamports}`);
                return null;
            }
            // only liquidate positions that are actually liquidatable
            if (scored.position.health !== 'liquidatable') {
                this.log.info(`skipping ${scored.borrower.slice(0, 8)}... — health=${scored.position.health} (not liquidatable)`);
                return null;
            }
            this.log.info(`liquidating ${scored.borrower.slice(0, 8)}... on ${scored.tokenName} — risk=${scored.riskScore}, profit=${scored.estimatedProfitLamports}`);
            try {
                const result = await (0, utils_1.withTimeout)((0, torchsdk_1.buildLiquidateTransaction)(connection, {
                    mint: scored.mint,
                    liquidator: this.config.walletKeypair.publicKey.toBase58(),
                    borrower: scored.borrower,
                    vault: this.config.vaultCreator,
                }), 30000, 'buildLiquidateTransaction');
                result.transaction.partialSign(this.config.walletKeypair);
                const sig = await connection.sendRawTransaction(result.transaction.serialize(), {
                    skipPreflight: false,
                    preflightCommitment: 'confirmed',
                });
                await connection.confirmTransaction(sig, 'confirmed');
                this.log.info(`liquidation success: sig=${sig.slice(0, 8)}...`);
                return {
                    mint: scored.mint,
                    borrower: scored.borrower,
                    signature: sig,
                    profitLamports: scored.estimatedProfitLamports,
                    timestamp: Date.now(),
                    confirmed: true,
                };
            }
            catch (err) {
                this.log.error(`liquidation failed for ${scored.borrower.slice(0, 8)}...`, err);
                return null;
            }
        };
        this.config = config;
        this.log = log;
    }
}
exports.Liquidator = Liquidator;
//# sourceMappingURL=liquidator.js.map