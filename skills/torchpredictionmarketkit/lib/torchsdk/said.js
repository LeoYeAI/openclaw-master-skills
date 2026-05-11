"use strict";
/**
 * SAID Protocol integration
 *
 * Verify wallet reputation and confirm transactions for SAID feedback.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.confirmTransaction = exports.verifySaid = void 0;
const constants_1 = require("./constants");
const SAID_API_URL = 'https://api.saidprotocol.com/api';
// ============================================================================
// Verify
// ============================================================================
/**
 * Check SAID verification status for a wallet.
 *
 * @param wallet - Wallet address to verify
 * @returns Verification status including trust tier
 */
const verifySaid = async (wallet) => {
    try {
        const res = await fetch(`${SAID_API_URL}/verify/${wallet}`);
        const data = (await res.json());
        return {
            verified: data.verified ?? false,
            trustTier: data.trustTier ?? null,
            name: data.name,
        };
    }
    catch {
        return { verified: false, trustTier: null };
    }
};
exports.verifySaid = verifySaid;
// ============================================================================
// Confirm
// ============================================================================
/**
 * Confirm a transaction on-chain and determine event type.
 *
 * After an agent submits a transaction, call this to verify it succeeded
 * and determine the event type for reputation tracking.
 *
 * @param connection - Solana RPC connection
 * @param signature - Transaction signature to confirm
 * @param wallet - Wallet address that signed the transaction
 * @returns Confirmation result with event type
 */
const confirmTransaction = async (connection, signature, wallet) => {
    const tx = await connection.getParsedTransaction(signature, {
        maxSupportedTransactionVersion: 0,
        commitment: 'confirmed',
    });
    if (!tx)
        throw new Error('Transaction not found or not confirmed');
    if (tx.meta?.err)
        throw new Error('Transaction failed on-chain');
    // Verify wallet was a signer
    const signers = tx.transaction.message.accountKeys
        .filter((key) => key.signer)
        .map((key) => key.pubkey.toString());
    if (!signers.includes(wallet)) {
        throw new Error('Wallet was not a signer on this transaction');
    }
    // Find Torch Market instructions
    const torchInstructions = tx.transaction.message.instructions.filter((ix) => {
        const programId = 'programId' in ix ? ix.programId.toString() : '';
        return programId === constants_1.PROGRAM_ID.toString();
    });
    if (torchInstructions.length === 0) {
        throw new Error('Transaction does not involve Torch Market');
    }
    // Determine event type from logs
    const logs = tx.meta?.logMessages || [];
    const isCreateToken = logs.some((log) => log.includes('Instruction: CreateToken') || log.includes('create_token'));
    const isBuy = logs.some((log) => log.includes('Instruction: Buy') || log.includes('Program log: Buy'));
    const isSell = logs.some((log) => log.includes('Instruction: Sell') || log.includes('Program log: Sell'));
    const isVote = logs.some((log) => log.includes('Instruction: Vote') || log.includes('Program log: Vote'));
    let event_type = 'unknown';
    if (isCreateToken)
        event_type = 'token_launch';
    else if (isBuy || isSell)
        event_type = 'trade_complete';
    else if (isVote)
        event_type = 'governance_vote';
    return { confirmed: true, event_type };
};
exports.confirmTransaction = confirmTransaction;
//# sourceMappingURL=said.js.map