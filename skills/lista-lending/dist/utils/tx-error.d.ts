import type { StepParam } from "@lista-dao/moolah-lending-sdk";
import type { TxResult } from "../types.js";
interface WalletConnectResponse {
    status?: string;
    txHash?: string;
    error?: string;
    reason?: string;
    revertReason?: string;
}
export declare function mapWalletConnectResponse(response: WalletConnectResponse, step: StepParam["step"], explorerUrl?: string): TxResult;
export declare function mapExecutionError(err: unknown, step: StepParam["step"]): TxResult;
export {};
