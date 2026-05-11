"use strict";
/**
 * Quote calculations
 *
 * Get expected output for buy/sell operations.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSellQuote = exports.getBuyQuote = void 0;
const web3_js_1 = require("@solana/web3.js");
const program_1 = require("./program");
const constants_1 = require("./constants");
const tokens_1 = require("./tokens");
/**
 * Get a buy quote: how many tokens for a given SOL amount.
 */
const getBuyQuote = async (connection, mintStr, amountSolLamports) => {
    const mint = new web3_js_1.PublicKey(mintStr);
    const tokenData = await (0, tokens_1.fetchTokenRaw)(connection, mint);
    if (!tokenData) {
        throw new Error(`Token not found: ${mintStr}`);
    }
    const { bondingCurve } = tokenData;
    if (bondingCurve.bonding_complete) {
        throw new Error('Bonding curve complete, trade on DEX');
    }
    const virtualSol = BigInt(bondingCurve.virtual_sol_reserves.toString());
    const virtualTokens = BigInt(bondingCurve.virtual_token_reserves.toString());
    const realSol = BigInt(bondingCurve.real_sol_reserves.toString());
    const bondingTarget = BigInt(bondingCurve.bonding_target.toString());
    const amountSol = BigInt(amountSolLamports);
    const result = (0, program_1.calculateTokensOut)(amountSol, virtualSol, virtualTokens, realSol, 100, 100, bondingTarget);
    const priceBefore = (0, program_1.calculatePrice)(virtualSol, virtualTokens);
    const priceAfter = (0, program_1.calculatePrice)(virtualSol + result.solToCurve, virtualTokens - result.tokensOut);
    const priceImpact = ((priceAfter - priceBefore) / priceBefore) * 100;
    const minOutput = (result.tokensToUser * BigInt(99)) / BigInt(100);
    return {
        input_sol: Number(amountSol),
        output_tokens: Number(result.tokensOut),
        tokens_to_user: Number(result.tokensToUser),
        tokens_to_treasury: Number(result.tokensToCommunity),
        protocol_fee_sol: Number(result.protocolFee),
        price_per_token_sol: (priceBefore * constants_1.TOKEN_MULTIPLIER) / constants_1.LAMPORTS_PER_SOL,
        price_impact_percent: priceImpact,
        min_output_tokens: Number(minOutput),
    };
};
exports.getBuyQuote = getBuyQuote;
/**
 * Get a sell quote: how much SOL for a given token amount.
 */
const getSellQuote = async (connection, mintStr, amountTokens) => {
    const mint = new web3_js_1.PublicKey(mintStr);
    const tokenData = await (0, tokens_1.fetchTokenRaw)(connection, mint);
    if (!tokenData) {
        throw new Error(`Token not found: ${mintStr}`);
    }
    const { bondingCurve } = tokenData;
    if (bondingCurve.bonding_complete) {
        throw new Error('Bonding curve complete, trade on DEX');
    }
    const virtualSol = BigInt(bondingCurve.virtual_sol_reserves.toString());
    const virtualTokens = BigInt(bondingCurve.virtual_token_reserves.toString());
    const tokenAmount = BigInt(amountTokens);
    const result = (0, program_1.calculateSolOut)(tokenAmount, virtualSol, virtualTokens);
    const priceBefore = (0, program_1.calculatePrice)(virtualSol, virtualTokens);
    const priceAfter = (0, program_1.calculatePrice)(virtualSol - result.solOut, virtualTokens + tokenAmount);
    const priceImpact = ((priceBefore - priceAfter) / priceBefore) * 100;
    const minOutput = (result.solToUser * BigInt(99)) / BigInt(100);
    return {
        input_tokens: Number(tokenAmount),
        output_sol: Number(result.solToUser),
        protocol_fee_sol: 0,
        price_per_token_sol: (priceBefore * constants_1.TOKEN_MULTIPLIER) / constants_1.LAMPORTS_PER_SOL,
        price_impact_percent: priceImpact,
        min_output_sol: Number(minOutput),
    };
};
exports.getSellQuote = getSellQuote;
//# sourceMappingURL=quotes.js.map