import type { TransactionRequest, Hash } from "viem";

// ── MPC Wallet abstraction ────────────────────────────────────────────────────
//
// Both Privy and Coinbase AgentKit implement this interface.
// Private keys are NEVER returned or exposed — signing happens in HSM/TEE.

export interface MPCWallet {
  /** EVM address of this wallet. */
  readonly address: `0x${string}`;
  /** Wallet ID in the MPC provider (opaque). */
  readonly walletId: string;
  /** MPC provider in use. */
  readonly provider: "privy" | "coinbase";

  /** Sign and broadcast a transaction. Returns tx hash. */
  sendTransaction(tx: TransactionRequest & { to: `0x${string}` }): Promise<Hash>;

  /** Sign a typed data payload (EIP-712). */
  signTypedData(params: {
    domain: Record<string, unknown>;
    types: Record<string, unknown>;
    primaryType: string;
    message: Record<string, unknown>;
  }): Promise<`0x${string}`>;

  /** Sign a raw message (EIP-191). */
  signMessage(message: string): Promise<`0x${string}`>;
}

export interface WalletCreateResult {
  wallet: MPCWallet;
  /** True if the wallet already existed (loaded from env). */
  existed: boolean;
}
