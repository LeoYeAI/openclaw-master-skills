#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateScraperTicker = exports.evaluateDomain = exports.scanDomains = exports.generateTicker = exports.updateLeases = exports.checkTopHolder = exports.launchDomainToken = exports.Logger = exports.Liquidator = exports.scoreLoan = exports.WalletProfiler = exports.scanForLendingMarkets = void 0;
const web3_js_1 = require("@solana/web3.js");
const config_1 = require("./config");
const logger_1 = require("./logger");
const monitor_1 = require("./monitor");
const launcher_1 = require("./launcher");
const torchsdk_1 = require("torchsdk");
const utils_1 = require("./utils");
// bot exports
var scanner_1 = require("./scanner");
Object.defineProperty(exports, "scanForLendingMarkets", { enumerable: true, get: function () { return scanner_1.scanForLendingMarkets; } });
var wallet_profiler_1 = require("./wallet-profiler");
Object.defineProperty(exports, "WalletProfiler", { enumerable: true, get: function () { return wallet_profiler_1.WalletProfiler; } });
var risk_scorer_1 = require("./risk-scorer");
Object.defineProperty(exports, "scoreLoan", { enumerable: true, get: function () { return risk_scorer_1.scoreLoan; } });
var liquidator_1 = require("./liquidator");
Object.defineProperty(exports, "Liquidator", { enumerable: true, get: function () { return liquidator_1.Liquidator; } });
var logger_2 = require("./logger");
Object.defineProperty(exports, "Logger", { enumerable: true, get: function () { return logger_2.Logger; } });
var launcher_2 = require("./launcher");
Object.defineProperty(exports, "launchDomainToken", { enumerable: true, get: function () { return launcher_2.launchDomainToken; } });
var domain_manager_1 = require("./domain-manager");
Object.defineProperty(exports, "checkTopHolder", { enumerable: true, get: function () { return domain_manager_1.checkTopHolder; } });
Object.defineProperty(exports, "updateLeases", { enumerable: true, get: function () { return domain_manager_1.updateLeases; } });
var ticker_1 = require("./ticker");
Object.defineProperty(exports, "generateTicker", { enumerable: true, get: function () { return ticker_1.generateTicker; } });
// scraper exports
var scanner_2 = require("./scraper/scanner");
Object.defineProperty(exports, "scanDomains", { enumerable: true, get: function () { return scanner_2.scanDomains; } });
var evaluator_1 = require("./scraper/evaluator");
Object.defineProperty(exports, "evaluateDomain", { enumerable: true, get: function () { return evaluator_1.evaluateDomain; } });
var ticker_2 = require("./scraper/ticker");
Object.defineProperty(exports, "generateScraperTicker", { enumerable: true, get: function () { return ticker_2.generateTicker; } });
const printUsage = () => {
    console.log(`torch-domain-bot — domain auction bot for torch.market

Usage:
  torch-domain-bot monitor    Start the lending monitor and auto-liquidator
  torch-domain-bot launch     Launch a domain token (interactive)
  torch-domain-bot info       Show token info for a mint
  torch-domain-bot help       Show this help message
`);
};
const main = async () => {
    const args = process.argv.slice(2);
    const command = args[0] ?? 'help';
    if (command === 'help' || command === '--help') {
        printUsage();
        return;
    }
    const config = (0, config_1.loadConfig)();
    const log = new logger_1.Logger('bot', config.logLevel);
    const connection = new web3_js_1.Connection(config.rpcUrl, 'confirmed');
    // startup banner
    console.log('=== torch domain auction bot ===');
    console.log(`agent wallet: ${config.walletKeypair.publicKey.toBase58()}`);
    console.log(`vault creator: ${config.vaultCreator}`);
    console.log(`scan interval: ${config.scanIntervalMs}ms`);
    console.log();
    // verify vault exists
    const vault = await (0, utils_1.withTimeout)((0, torchsdk_1.getVault)(connection, config.vaultCreator), 30000, 'getVault');
    if (!vault) {
        throw new Error(`vault not found for creator ${config.vaultCreator}`);
    }
    log.info(`vault found — authority=${vault.authority}`);
    // verify agent wallet is linked to vault
    const link = await (0, utils_1.withTimeout)((0, torchsdk_1.getVaultForWallet)(connection, config.walletKeypair.publicKey.toBase58()), 30000, 'getVaultForWallet');
    if (!link) {
        console.log();
        console.log('--- ACTION REQUIRED ---');
        console.log('agent wallet is NOT linked to the vault.');
        console.log('link it by running (from your authority wallet):');
        console.log();
        console.log(`  buildLinkWalletTransaction(connection, {`);
        console.log(`    authority: "<your-authority-pubkey>",`);
        console.log(`    vault_creator: "${config.vaultCreator}",`);
        console.log(`    wallet_to_link: "${config.walletKeypair.publicKey.toBase58()}"`);
        console.log(`  })`);
        console.log();
        console.log('then restart the bot.');
        console.log('-----------------------');
        process.exit(1);
    }
    log.info('agent wallet linked to vault — starting');
    log.info(`treasury: ${(0, utils_1.sol)(vault.sol_balance ?? 0)} SOL`);
    if (command === 'monitor') {
        await (0, monitor_1.runMonitor)(config);
    }
    else if (command === 'launch') {
        const domain = args[1];
        if (!domain) {
            console.error('Usage: torch-domain-bot launch <domain>');
            process.exit(1);
        }
        const result = await (0, launcher_1.launchDomainToken)(connection, config.walletKeypair, domain, undefined, log);
        console.log(`launched: mint=${result.mint}, ticker=${result.ticker}`);
    }
    else if (command === 'info') {
        const mint = args[1];
        if (!mint) {
            console.error('Usage: torch-domain-bot info <mint>');
            process.exit(1);
        }
        const detail = await (0, torchsdk_1.getToken)(connection, mint);
        console.log(JSON.stringify(detail, null, 2));
    }
    else {
        console.error(`unknown command: ${command}`);
        printUsage();
        process.exit(1);
    }
};
if (require.main === module) {
    main().catch((err) => {
        console.error('FATAL:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=index.js.map