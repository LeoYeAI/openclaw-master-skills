#!/usr/bin/env node
"use strict";
/**
 * torch-prediction-market-bot — vault-based prediction market bot.
 *
 * generates an agent keypair in-process (or uses SOLANA_PRIVATE_KEY if provided).
 * all operations route through a torch vault identified by VAULT_CREATOR.
 *
 * usage:
 *   VAULT_CREATOR=<pubkey> SOLANA_RPC_URL=<rpc> npx tsx src/index.ts
 *
 * env:
 *   SOLANA_RPC_URL    — solana RPC endpoint (required, fallback: RPC_URL)
 *   VAULT_CREATOR     — vault creator pubkey (required)
 *   SOLANA_PRIVATE_KEY — disposable controller keypair, base58 (optional)
 *   SCAN_INTERVAL_MS  — ms between scan cycles (default 60000, min 5000)
 *   LOG_LEVEL         — debug | info | warn | error (default info)
 *   MARKETS_PATH      — path to markets JSON file (default ./markets.json)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.withTimeout = void 0;
const web3_js_1 = require("@solana/web3.js");
const torchsdk_1 = require("torchsdk");
const config_1 = require("./config");
const utils_1 = require("./utils");
const markets_1 = require("./markets");
var utils_2 = require("./utils");
Object.defineProperty(exports, "withTimeout", { enumerable: true, get: function () { return utils_2.withTimeout; } });
// ---------------------------------------------------------------------------
// market cycle — create pending, snapshot active, resolve expired
// ---------------------------------------------------------------------------
const marketCycle = async (connection, log, marketsPath, vaultCreator, agentKeypair) => {
    const markets = (0, markets_1.loadMarkets)(marketsPath);
    let dirty = false;
    for (const market of markets) {
        try {
            // --- create pending markets ---
            if (market.status === 'pending') {
                log('info', `CREATING | ${market.id} — "${market.question}"`);
                const mint = await (0, markets_1.createMarket)(connection, market, agentKeypair, vaultCreator);
                market.mint = mint;
                market.status = 'active';
                market.createdAt = Date.now();
                dirty = true;
                log('info', `CREATED | ${market.id} — mint=${mint.slice(0, 12)}... | seed=${(0, utils_1.sol)(market.initialLiquidityLamports)} SOL`);
                continue;
            }
            // --- snapshot active markets ---
            if (market.status === 'active') {
                const snapshot = await (0, markets_1.snapshotMarket)(connection, market);
                if (snapshot) {
                    log('debug', `SNAPSHOT | ${market.id} — price=${snapshot.price.toFixed(6)} SOL | ` +
                        `mcap=${snapshot.marketCap.toFixed(4)} | holders=${snapshot.holders}`);
                }
                // check if deadline has passed
                if (Date.now() >= market.deadline * 1000) {
                    log('info', `RESOLVING | ${market.id} — deadline reached`);
                    const outcome = await (0, markets_1.resolveMarket)(market);
                    if (outcome !== 'unresolved') {
                        market.status = 'resolved';
                        market.outcome = outcome;
                        market.resolvedAt = Date.now();
                        dirty = true;
                        log('info', `RESOLVED | ${market.id} — outcome=${outcome}`);
                    }
                    else {
                        log('info', `UNRESOLVED | ${market.id} — manual oracle, awaiting resolution`);
                    }
                }
                continue;
            }
            // --- resolved / cancelled — skip ---
        }
        catch (err) {
            log('warn', `ERROR | ${market.id} — ${err.message}`);
        }
    }
    if (dirty) {
        (0, markets_1.saveMarkets)(marketsPath, markets);
        log('debug', `saved ${markets.length} markets to ${marketsPath}`);
    }
};
// ---------------------------------------------------------------------------
// main — vault-routed prediction market loop
// ---------------------------------------------------------------------------
const main = async () => {
    const config = (0, config_1.loadConfig)();
    const log = (0, utils_1.createLogger)(config.logLevel);
    const connection = new web3_js_1.Connection(config.rpcUrl, 'confirmed');
    // load or generate agent keypair
    let agentKeypair;
    if (config.privateKey) {
        try {
            const parsed = JSON.parse(config.privateKey);
            if (Array.isArray(parsed)) {
                agentKeypair = web3_js_1.Keypair.fromSecretKey(Uint8Array.from(parsed));
            }
            else {
                throw new Error('SOLANA_PRIVATE_KEY JSON must be a byte array');
            }
        }
        catch (e) {
            if (e.message?.includes('byte array'))
                throw e;
            // not JSON — try base58
            agentKeypair = web3_js_1.Keypair.fromSecretKey((0, utils_1.decodeBase58)(config.privateKey));
        }
        log('info', 'loaded keypair from SOLANA_PRIVATE_KEY');
    }
    else {
        agentKeypair = web3_js_1.Keypair.generate();
        log('info', 'generated fresh agent keypair');
    }
    console.log('=== torch prediction market bot ===');
    console.log(`agent wallet: ${agentKeypair.publicKey.toBase58()}`);
    console.log(`vault creator: ${config.vaultCreator}`);
    console.log(`markets file: ${config.marketsPath}`);
    console.log(`scan interval: ${config.scanIntervalMs}ms`);
    console.log();
    // verify vault exists
    const vault = await (0, utils_1.withTimeout)((0, torchsdk_1.getVault)(connection, config.vaultCreator), 30000, 'getVault');
    if (!vault) {
        throw new Error(`vault not found for creator ${config.vaultCreator}`);
    }
    log('info', `vault found — authority=${vault.authority}`);
    // verify agent wallet is linked to vault
    const link = await (0, utils_1.withTimeout)((0, torchsdk_1.getVaultForWallet)(connection, agentKeypair.publicKey.toBase58()), 30000, 'getVaultForWallet');
    if (!link) {
        console.log();
        console.log('--- ACTION REQUIRED ---');
        console.log('agent wallet is NOT linked to the vault.');
        console.log('link it by running (from your authority wallet):');
        console.log();
        console.log(`  buildLinkWalletTransaction(connection, {`);
        console.log(`    authority: "<your-authority-pubkey>",`);
        console.log(`    vault_creator: "${config.vaultCreator}",`);
        console.log(`    wallet_to_link: "${agentKeypair.publicKey.toBase58()}"`);
        console.log(`  })`);
        console.log();
        console.log('then restart the bot.');
        console.log('-----------------------');
        process.exit(1);
    }
    log('info', 'agent wallet linked to vault — starting market cycle');
    log('info', `treasury: ${(0, utils_1.sol)(vault.sol_balance ?? 0)} SOL`);
    // market cycle loop
    while (true) {
        try {
            log('debug', '--- market cycle start ---');
            await marketCycle(connection, log, config.marketsPath, config.vaultCreator, agentKeypair);
            log('debug', '--- market cycle end ---');
        }
        catch (err) {
            log('error', `market cycle error: ${err.message}`);
        }
        await new Promise((resolve) => setTimeout(resolve, config.scanIntervalMs));
    }
};
main().catch((err) => {
    console.error('FATAL:', err.message ?? err);
    process.exit(1);
});
//# sourceMappingURL=index.js.map