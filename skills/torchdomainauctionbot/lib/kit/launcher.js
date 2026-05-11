"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.launchDomainToken = void 0;
const torchsdk_1 = require("torchsdk");
const ticker_1 = require("./ticker");
const utils_1 = require("./utils");
const launchDomainToken = async (connection, wallet, domain, ticker, log) => {
    const symbol = ticker ?? (0, ticker_1.generateTicker)(domain);
    const name = domain;
    const metadataUri = `https://${domain}`;
    log?.info(`launching token for ${domain} — symbol=${symbol}`);
    const result = await (0, utils_1.withTimeout)((0, torchsdk_1.buildCreateTokenTransaction)(connection, {
        creator: wallet.publicKey.toBase58(),
        name,
        symbol,
        metadata_uri: metadataUri,
    }), 30000, 'buildCreateTokenTransaction');
    // sign and send
    result.transaction.partialSign(wallet);
    const sig = await connection.sendRawTransaction(result.transaction.serialize(), {
        skipPreflight: false,
        preflightCommitment: 'confirmed',
    });
    await connection.confirmTransaction(sig, 'confirmed');
    const mint = result.mint.toBase58();
    log?.info(`launched: mint=${mint.slice(0, 8)}... sig=${sig.slice(0, 8)}...`);
    return { domain, mint, signature: sig, ticker: symbol };
};
exports.launchDomainToken = launchDomainToken;
//# sourceMappingURL=launcher.js.map