/**
 * Types for Lista Lending skill
 */

import type { Address } from "viem";

export interface ParsedArgs {
  // Target selection
  vault?: string;
  market?: string;
  // Operation amounts
  amount?: string;
  // Chain
  chain?: string;
  // Wallet connection
  walletTopic?: string;
  walletAddress?: string;
  // Vault operations
  withdrawAll?: boolean;
  // Market operations
  repayAll?: boolean;
  simulate?: boolean;
  simulateSupply?: string;
  // General
  help?: boolean;
}

interface TxResultBase {
  step?: string;
  reason?: string;
  txHash?: string;
  explorer?: string;
}

export type TxSentResult = TxResultBase & {
  status: "sent";
  txHash: string;
};

export type TxPendingResult = TxResultBase & {
  status: "pending";
  txHash: string;
  reason: string;
};

export type TxRejectedResult = TxResultBase & {
  status: "rejected";
  reason: string;
};

export type TxRevertedResult = TxResultBase & {
  status: "reverted";
  reason: string;
};

export type TxErrorResult = TxResultBase & {
  status: "error";
  reason: string;
};

export type TxNeedsApprovalResult = TxResultBase & {
  status: "needs_approval";
  token: string;
  spender: string;
  requiredAmount: string;
};

export type TxResult =
  | TxSentResult
  | TxPendingResult
  | TxRejectedResult
  | TxRevertedResult
  | TxErrorResult
  | TxNeedsApprovalResult;

// Re-export SDK types we use
export type {
  StepParam,
  BuildVaultDepositParams,
  BuildVaultWithdrawParams,
} from "@lista-dao/moolah-lending-sdk";
export type {
  VaultInfo,
  VaultUserData,
  MarketUserData,
} from "@lista-dao/moolah-lending-sdk";
export type { Address };
