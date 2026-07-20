// ============================================================
// Afterself — Mortality Pool (CLI)
// Solana-based tontine: check balances, transfer tokens to
// the shared pool on trigger, create wallets for new users.
// Called by the OpenClaw agent via CLI commands.
// ============================================================
import { Connection, Keypair, PublicKey, Transaction, sendAndConfirmTransaction, } from "@solana/web3.js";
import { getAssociatedTokenAddress, getAccount, createTransferInstruction, TOKEN_PROGRAM_ID, getOrCreateAssociatedTokenAccount, } from "@solana/spl-token";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import { loadConfig, saveConfig, updateState, appendAudit } from "./state.js";
const WALLET_DIR = join(process.env.HOME || "~", ".afterself");
const DEFAULT_WALLET_PATH = join(WALLET_DIR, "wallet.json");
// -----------------------------------------------------------
// Solana Helpers
// -----------------------------------------------------------
/** Load a Solana keypair from a JSON file (standard CLI format: [byte, byte, ...]) */
function loadKeypair(path) {
    if (!existsSync(path)) {
        throw new Error(`Keypair file not found: ${path}`);
    }
    const raw = readFileSync(path, "utf-8");
    const secretKey = Uint8Array.from(JSON.parse(raw));
    return Keypair.fromSecretKey(secretKey);
}
/** Get a Connection to the configured Solana RPC */
function getConnection() {
    const config = loadConfig();
    return new Connection(config.mortalityPool.rpcUrl, "confirmed");
}
/** Get the configured keypair path, or fail */
function getKeypairPath() {
    const config = loadConfig();
    const path = config.mortalityPool.keypairPath;
    if (!path) {
        throw new Error("No keypair configured. Run 'create-wallet' or set mortalityPool.keypairPath in config.");
    }
    return path;
}
// -----------------------------------------------------------
// Commands
// -----------------------------------------------------------
/** Generate a new Solana keypair and save it locally */
async function createWallet() {
    const keypair = Keypair.generate();
    const secretKeyArray = Array.from(keypair.secretKey);
    writeFileSync(DEFAULT_WALLET_PATH, JSON.stringify(secretKeyArray), {
        mode: 0o600,
    });
    // Auto-set config
    const config = loadConfig();
    config.mortalityPool.keypairPath = DEFAULT_WALLET_PATH;
    saveConfig(config);
    appendAudit("mortality", "wallet_created", {
        publicKey: keypair.publicKey.toBase58(),
        keypairPath: DEFAULT_WALLET_PATH,
    });
    return {
        publicKey: keypair.publicKey.toBase58(),
        keypairPath: DEFAULT_WALLET_PATH,
    };
}
/** Check the user's SPL token balance */
async function checkBalance() {
    const config = loadConfig();
    const keypairPath = getKeypairPath();
    const keypair = loadKeypair(keypairPath);
    const connection = getConnection();
    const tokenMint = new PublicKey(config.mortalityPool.tokenMint);
    const walletPubkey = keypair.publicKey;
    let balance = 0;
    try {
        const tokenAccountAddress = await getAssociatedTokenAddress(tokenMint, walletPubkey);
        const tokenAccount = await getAccount(connection, tokenAccountAddress);
        balance = Number(tokenAccount.amount);
    }
    catch (err) {
        // TokenAccountNotFoundError means balance is 0
        if (err?.name !== "TokenAccountNotFoundError") {
            throw err;
        }
    }
    // Update state
    updateState((s) => ({
        ...s,
        mortalityTokenBalance: balance,
    }));
    return {
        balance,
        wallet: walletPubkey.toBase58(),
        tokenMint: config.mortalityPool.tokenMint,
    };
}
/** Transfer ALL user's tokens to the mortality pool wallet */
async function transferToPool() {
    const config = loadConfig();
    const keypairPath = getKeypairPath();
    const keypair = loadKeypair(keypairPath);
    const connection = getConnection();
    const tokenMint = new PublicKey(config.mortalityPool.tokenMint);
    const poolWallet = new PublicKey(config.mortalityPool.poolWallet);
    const walletPubkey = keypair.publicKey;
    // Get user's token account
    const userTokenAddress = await getAssociatedTokenAddress(tokenMint, walletPubkey);
    const userTokenAccount = await getAccount(connection, userTokenAddress);
    const amount = Number(userTokenAccount.amount);
    if (amount === 0) {
        throw new Error("No tokens to transfer — balance is 0");
    }
    // Get or create pool's token account
    const poolTokenAccount = await getOrCreateAssociatedTokenAccount(connection, keypair, // payer (user pays for pool ATA creation if needed)
    tokenMint, poolWallet);
    // Create transfer instruction
    const transferIx = createTransferInstruction(userTokenAddress, poolTokenAccount.address, walletPubkey, BigInt(userTokenAccount.amount), [], TOKEN_PROGRAM_ID);
    const transaction = new Transaction().add(transferIx);
    // Sign and send
    const txSignature = await sendAndConfirmTransaction(connection, transaction, [keypair]);
    // Update state
    updateState((s) => ({
        ...s,
        mortalityTokenBalance: 0,
        mortalityTransferComplete: true,
    }));
    appendAudit("mortality", "tokens_transferred", {
        amount,
        txSignature,
        poolWallet: config.mortalityPool.poolWallet,
        tokenMint: config.mortalityPool.tokenMint,
    });
    return { success: true, txSignature, amount };
}
/** Check the pool wallet's total token balance */
async function poolBalance() {
    const config = loadConfig();
    const connection = getConnection();
    const tokenMint = new PublicKey(config.mortalityPool.tokenMint);
    const poolWallet = new PublicKey(config.mortalityPool.poolWallet);
    let balance = 0;
    try {
        const poolTokenAddress = await getAssociatedTokenAddress(tokenMint, poolWallet);
        const poolTokenAccount = await getAccount(connection, poolTokenAddress);
        balance = Number(poolTokenAccount.amount);
    }
    catch (err) {
        if (err?.name !== "TokenAccountNotFoundError") {
            throw err;
        }
    }
    return {
        poolWallet: config.mortalityPool.poolWallet,
        balance,
        tokenMint: config.mortalityPool.tokenMint,
    };
}
/** Validate the mortality pool configuration */
async function validateConfig() {
    const config = loadConfig();
    const issues = [];
    // Check keypair
    const keypairPath = config.mortalityPool.keypairPath;
    if (!keypairPath) {
        issues.push("No keypairPath configured");
    }
    else if (!existsSync(keypairPath)) {
        issues.push(`Keypair file not found: ${keypairPath}`);
    }
    else {
        try {
            loadKeypair(keypairPath);
        }
        catch {
            issues.push(`Invalid keypair file: ${keypairPath}`);
        }
    }
    // Check RPC connectivity
    try {
        const connection = getConnection();
        await connection.getLatestBlockhash();
    }
    catch {
        issues.push(`Cannot connect to RPC: ${config.mortalityPool.rpcUrl}`);
    }
    // Check token mint
    try {
        const connection = getConnection();
        const mintPubkey = new PublicKey(config.mortalityPool.tokenMint);
        const mintAccount = await connection.getAccountInfo(mintPubkey);
        if (!mintAccount) {
            issues.push(`Token mint not found on-chain: ${config.mortalityPool.tokenMint}`);
        }
    }
    catch {
        issues.push(`Invalid token mint address: ${config.mortalityPool.tokenMint}`);
    }
    // Check pool wallet
    try {
        new PublicKey(config.mortalityPool.poolWallet);
    }
    catch {
        issues.push(`Invalid pool wallet address: ${config.mortalityPool.poolWallet}`);
    }
    return { valid: issues.length === 0, issues };
}
// -----------------------------------------------------------
// CLI
// -----------------------------------------------------------
function output(data) {
    console.log(JSON.stringify({ ok: true, data }, null, 2));
}
function fail(message) {
    console.log(JSON.stringify({ ok: false, error: message }, null, 2));
    process.exit(1);
}
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    try {
        switch (command) {
            case "create-wallet": {
                const result = await createWallet();
                output(result);
                break;
            }
            case "check-balance": {
                const result = await checkBalance();
                output(result);
                break;
            }
            case "transfer-to-pool": {
                const result = await transferToPool();
                output(result);
                break;
            }
            case "pool-balance": {
                const result = await poolBalance();
                output(result);
                break;
            }
            case "validate-config": {
                const result = await validateConfig();
                output(result);
                break;
            }
            default: {
                fail(`Unknown command: ${command}\n` +
                    `Available commands: create-wallet, check-balance, transfer-to-pool, pool-balance, validate-config`);
            }
        }
    }
    catch (err) {
        fail(err.message || String(err));
    }
}
// Only run CLI when this is the entry point
import { fileURLToPath } from "url";
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}
