/**
 * Types for Lista Lending skill
 */
import type { Address } from "viem";
export interface ParsedArgs {
    vault?: string;
    market?: string;
    amount?: string;
    chain?: string;
    walletTopic?: string;
    walletAddress?: string;
    withdrawAll?: boolean;
    repayAll?: boolean;
    simulate?: boolean;
    simulateSupply?: string;
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
export type TxResult = TxSentResult | TxPendingResult | TxRejectedResult | TxRevertedResult | TxErrorResult | TxNeedsApprovalResult;
export type { StepParam, BuildVaultDepositParams, BuildVaultWithdrawParams, } from "@lista-dao/moolah-lending-sdk";
export type { VaultInfo, VaultUserData, MarketUserData, } from "@lista-dao/moolah-lending-sdk";
export type { Address };
