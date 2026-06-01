"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getRaydiumMigrationAccounts = exports.getRaydiumObservationPda = exports.getRaydiumVaultPda = exports.getRaydiumLpMintPda = exports.getRaydiumPoolStatePda = exports.getRaydiumAuthorityPda = exports.orderTokensForRaydium = exports.calculateBondingProgress = exports.calculatePrice = exports.calculateSolOut = exports.calculateTokensOut = exports.getProgram = exports.getTreasuryLockTokenAccount = exports.getTreasuryLockPda = exports.getVaultWalletLinkPda = exports.getTorchVaultPda = exports.getCollateralVaultPda = exports.getLoanPositionPda = exports.getStarRecordPda = exports.getUserStatsPda = exports.getProtocolTreasuryPda = exports.getTokenTreasuryPda = exports.getVoteRecordPda = exports.getUserPositionPda = exports.getTreasuryTokenAccount = exports.getBondingCurvePda = exports.getGlobalConfigPda = exports.decodeString = exports.PROGRAM_ID = void 0;
const anchor_1 = require("@coral-xyz/anchor");
const web3_js_1 = require("@solana/web3.js");
const constants_1 = require("./constants");
Object.defineProperty(exports, "PROGRAM_ID", { enumerable: true, get: function () { return constants_1.PROGRAM_ID; } });
const spl_token_1 = require("@solana/spl-token");
const torch_market_json_1 = __importDefault(require("./torch_market.json"));
// Helper to decode byte arrays to strings
const decodeString = (bytes) => {
    return Buffer.from(bytes).toString('utf8').replace(/\0/g, '');
};
exports.decodeString = decodeString;
// PDA derivation helpers
const getGlobalConfigPda = () => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.GLOBAL_CONFIG_SEED)], constants_1.PROGRAM_ID);
};
exports.getGlobalConfigPda = getGlobalConfigPda;
const getBondingCurvePda = (mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.BONDING_CURVE_SEED), mint.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getBondingCurvePda = getBondingCurvePda;
// [V13] Treasury's token account (ATA) - holds vote vault tokens during bonding
const getTreasuryTokenAccount = (mint, treasury) => {
    return (0, spl_token_1.getAssociatedTokenAddressSync)(mint, treasury, true, // allowOwnerOffCurve (PDA)
    constants_1.TOKEN_2022_PROGRAM_ID);
};
exports.getTreasuryTokenAccount = getTreasuryTokenAccount;
const getUserPositionPda = (bondingCurve, user) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.USER_POSITION_SEED), bondingCurve.toBuffer(), user.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getUserPositionPda = getUserPositionPda;
const getVoteRecordPda = (bondingCurve, voter) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.VOTE_SEED), bondingCurve.toBuffer(), voter.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getVoteRecordPda = getVoteRecordPda;
const getTokenTreasuryPda = (mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.TREASURY_SEED), mint.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getTokenTreasuryPda = getTokenTreasuryPda;
// V11: Protocol treasury PDA
const getProtocolTreasuryPda = () => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.PROTOCOL_TREASURY_SEED)], constants_1.PROGRAM_ID);
};
exports.getProtocolTreasuryPda = getProtocolTreasuryPda;
// V4: User stats PDA
const getUserStatsPda = (user) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.USER_STATS_SEED), user.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getUserStatsPda = getUserStatsPda;
// V10: Star record PDA (per user-token, not user-creator)
const getStarRecordPda = (user, mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.STAR_RECORD_SEED), user.toBuffer(), mint.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getStarRecordPda = getStarRecordPda;
// V2.4: Loan position PDA (per user-token)
const getLoanPositionPda = (mint, borrower) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.LOAN_SEED), mint.toBuffer(), borrower.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getLoanPositionPda = getLoanPositionPda;
// V2.4: Collateral vault PDA (per token)
const getCollateralVaultPda = (mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.COLLATERAL_VAULT_SEED), mint.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getCollateralVaultPda = getCollateralVaultPda;
// V2.0: Torch Vault PDA (per creator)
const getTorchVaultPda = (creator) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.TORCH_VAULT_SEED), creator.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getTorchVaultPda = getTorchVaultPda;
// V2.0: Vault Wallet Link PDA (per wallet)
const getVaultWalletLinkPda = (wallet) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.VAULT_WALLET_LINK_SEED), wallet.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getVaultWalletLinkPda = getVaultWalletLinkPda;
// V27: Treasury Lock PDA (per mint)
const getTreasuryLockPda = (mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from(constants_1.TREASURY_LOCK_SEED), mint.toBuffer()], constants_1.PROGRAM_ID);
};
exports.getTreasuryLockPda = getTreasuryLockPda;
// V27: Treasury Lock's Token-2022 ATA
const getTreasuryLockTokenAccount = (mint, treasuryLock) => {
    return (0, spl_token_1.getAssociatedTokenAddressSync)(mint, treasuryLock, true, // allowOwnerOffCurve (PDA)
    constants_1.TOKEN_2022_PROGRAM_ID);
};
exports.getTreasuryLockTokenAccount = getTreasuryLockTokenAccount;
// Get program instance
const getProgram = (provider) => {
    return new anchor_1.Program(torch_market_json_1.default, provider);
};
exports.getProgram = getProgram;
// [V25] Flat treasury SOL rate: 20% → 5% across all tiers (reverted from V24 tiered fees)
const TREASURY_SOL_MAX_BPS = 2000; // 20% at start
const TREASURY_SOL_MIN_BPS = 500; // 5% at completion
// [V34] Creator SOL share: 0.2% → 1% during bonding (carved from treasury rate)
const CREATOR_SOL_MIN_BPS = 20; // 0.2% at start
const CREATOR_SOL_MAX_BPS = 100; // 1% at completion
// Calculate tokens out for a given SOL amount (V2.3: dynamic treasury rate, V34: creator share)
const calculateTokensOut = (solAmount, virtualSolReserves, virtualTokenReserves, realSolReserves = BigInt(0), // V2.3: needed for dynamic rate calculation
protocolFeeBps = 100, // 1% protocol fee (90% protocol treasury, 10% dev)
treasuryFeeBps = 100, // 1% treasury fee
bondingTarget = BigInt('200000000000')) => {
    // Calculate protocol fee (1%)
    const protocolFee = (solAmount * BigInt(protocolFeeBps)) / BigInt(10000);
    // Calculate treasury fee (1%)
    const treasuryFee = (solAmount * BigInt(treasuryFeeBps)) / BigInt(10000);
    const solAfterFees = solAmount - protocolFee - treasuryFee;
    // [V25] Flat 20% → 5% treasury rate across all tiers
    const resolvedTarget = bondingTarget === BigInt(0) ? BigInt('200000000000') : bondingTarget;
    // V2.3: Dynamic treasury rate - decays from 20% to 5% as bonding progresses
    const rateRange = BigInt(TREASURY_SOL_MAX_BPS - TREASURY_SOL_MIN_BPS);
    const decay = (realSolReserves * rateRange) / resolvedTarget;
    const treasuryRateBps = Math.max(TREASURY_SOL_MAX_BPS - Number(decay), TREASURY_SOL_MIN_BPS);
    // [V34] Creator rate - grows from 0.2% to 1% (inverse of treasury decay)
    const creatorRange = BigInt(CREATOR_SOL_MAX_BPS - CREATOR_SOL_MIN_BPS);
    const creatorGrowth = (realSolReserves * creatorRange) / resolvedTarget;
    const creatorRateBps = Math.min(CREATOR_SOL_MIN_BPS + Number(creatorGrowth), CREATOR_SOL_MAX_BPS);
    // Split remaining SOL: total rate → creator + treasury + curve
    const totalSplit = (solAfterFees * BigInt(treasuryRateBps)) / BigInt(10000);
    const solToCreator = (solAfterFees * BigInt(creatorRateBps)) / BigInt(10000);
    const solToTreasurySplit = totalSplit - solToCreator;
    const solToCurve = solAfterFees - totalSplit;
    // Total to treasury = flat fee + dynamic split (minus creator)
    const solToTreasury = treasuryFee + solToTreasurySplit;
    // Calculate tokens using constant product formula (based on SOL going to curve)
    const tokensOut = (virtualTokenReserves * solToCurve) / (virtualSolReserves + solToCurve);
    // Split tokens: 90% to user, 10% to community treasury
    // No permanent burn during bonding - community votes on treasury tokens at migration
    const tokensToUser = (tokensOut * BigInt(9000)) / BigInt(10000);
    const tokensToCommunity = tokensOut - tokensToUser;
    return {
        tokensOut,
        tokensToUser,
        tokensToCommunity,
        protocolFee,
        treasuryFee,
        solToCurve,
        solToTreasury,
        solToCreator,
        treasuryRateBps,
        creatorRateBps,
    };
};
exports.calculateTokensOut = calculateTokensOut;
// Calculate SOL out for a given token amount (no sell fee)
const calculateSolOut = (tokenAmount, virtualSolReserves, virtualTokenReserves) => {
    // Calculate SOL using inverse formula
    const solOut = (virtualSolReserves * tokenAmount) / (virtualTokenReserves + tokenAmount);
    // No fees on sells - user gets full amount
    return { solOut, solToUser: solOut };
};
exports.calculateSolOut = calculateSolOut;
// Calculate current token price in SOL
const calculatePrice = (virtualSolReserves, virtualTokenReserves) => {
    // Price = virtualSol / virtualTokens
    return Number(virtualSolReserves) / Number(virtualTokenReserves);
};
exports.calculatePrice = calculatePrice;
// Calculate bonding progress percentage
const calculateBondingProgress = (realSolReserves) => {
    const target = BigInt('200000000000'); // 200 SOL in lamports
    if (realSolReserves >= target)
        return 100;
    return (Number(realSolReserves) / Number(target)) * 100;
};
exports.calculateBondingProgress = calculateBondingProgress;
// ============================================================================
// RAYDIUM CPMM PDA DERIVATION (V5)
// ============================================================================
// Order tokens for Raydium (token_0 < token_1 by pubkey bytes)
const orderTokensForRaydium = (tokenA, tokenB) => {
    const aBytes = tokenA.toBuffer();
    const bBytes = tokenB.toBuffer();
    for (let i = 0; i < 32; i++) {
        if (aBytes[i] < bBytes[i]) {
            return { token0: tokenA, token1: tokenB, isToken0First: true };
        }
        else if (aBytes[i] > bBytes[i]) {
            return { token0: tokenB, token1: tokenA, isToken0First: false };
        }
    }
    // Equal - shouldn't happen
    return { token0: tokenA, token1: tokenB, isToken0First: true };
};
exports.orderTokensForRaydium = orderTokensForRaydium;
// Raydium authority PDA
const getRaydiumAuthorityPda = () => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('vault_and_lp_mint_auth_seed')], (0, constants_1.getRaydiumCpmmProgram)());
};
exports.getRaydiumAuthorityPda = getRaydiumAuthorityPda;
// Raydium pool state PDA
const getRaydiumPoolStatePda = (ammConfig, token0Mint, token1Mint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('pool'), ammConfig.toBuffer(), token0Mint.toBuffer(), token1Mint.toBuffer()], (0, constants_1.getRaydiumCpmmProgram)());
};
exports.getRaydiumPoolStatePda = getRaydiumPoolStatePda;
// Raydium LP mint PDA
const getRaydiumLpMintPda = (poolState) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('pool_lp_mint'), poolState.toBuffer()], (0, constants_1.getRaydiumCpmmProgram)());
};
exports.getRaydiumLpMintPda = getRaydiumLpMintPda;
// Raydium pool vault PDA
const getRaydiumVaultPda = (poolState, tokenMint) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('pool_vault'), poolState.toBuffer(), tokenMint.toBuffer()], (0, constants_1.getRaydiumCpmmProgram)());
};
exports.getRaydiumVaultPda = getRaydiumVaultPda;
// Raydium observation state PDA
const getRaydiumObservationPda = (poolState) => {
    return web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('observation'), poolState.toBuffer()], (0, constants_1.getRaydiumCpmmProgram)());
};
exports.getRaydiumObservationPda = getRaydiumObservationPda;
// Get all Raydium accounts needed for migration
const getRaydiumMigrationAccounts = (tokenMint) => {
    const { token0, token1, isToken0First } = (0, exports.orderTokensForRaydium)(constants_1.WSOL_MINT, tokenMint);
    const isWsolToken0 = isToken0First;
    const [raydiumAuthority] = (0, exports.getRaydiumAuthorityPda)();
    const [poolState] = (0, exports.getRaydiumPoolStatePda)((0, constants_1.getRaydiumAmmConfig)(), token0, token1);
    const [lpMint] = (0, exports.getRaydiumLpMintPda)(poolState);
    const [token0Vault] = (0, exports.getRaydiumVaultPda)(poolState, token0);
    const [token1Vault] = (0, exports.getRaydiumVaultPda)(poolState, token1);
    const [observationState] = (0, exports.getRaydiumObservationPda)(poolState);
    return {
        token0,
        token1,
        isWsolToken0,
        raydiumAuthority,
        poolState,
        lpMint,
        token0Vault,
        token1Vault,
        observationState,
    };
};
exports.getRaydiumMigrationAccounts = getRaydiumMigrationAccounts;
//# sourceMappingURL=program.js.map