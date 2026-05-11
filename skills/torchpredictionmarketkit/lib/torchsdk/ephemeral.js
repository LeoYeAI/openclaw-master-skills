"use strict";
/**
 * Ephemeral Agent Keypair
 *
 * Generates an in-process keypair that lives only in memory.
 * The authority links this wallet to their vault, and the SDK
 * uses it to sign transactions. When the process stops, the
 * private key is lost — zero key management, zero risk.
 *
 * Flow:
 *   1. const agent = createEphemeralAgent()
 *   2. Authority calls buildLinkWalletTransaction({ wallet_to_link: agent.publicKey })
 *   3. SDK uses agent.sign(tx) for all vault operations
 *   4. On shutdown, keys are GC'd. Authority unlinks the wallet.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createEphemeralAgent = void 0;
const web3_js_1 = require("@solana/web3.js");
/**
 * Create an ephemeral agent keypair.
 *
 * The keypair exists only in memory. No file is written to disk.
 * When the process exits, the private key is permanently lost.
 *
 * @returns EphemeralAgent with publicKey, sign function, and raw keypair
 */
const createEphemeralAgent = () => {
    const keypair = web3_js_1.Keypair.generate();
    return {
        publicKey: keypair.publicKey.toBase58(),
        keypair,
        sign: (tx) => {
            tx.partialSign(keypair);
            return tx;
        },
    };
};
exports.createEphemeralAgent = createEphemeralAgent;
//# sourceMappingURL=ephemeral.js.map