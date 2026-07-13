export interface ReceiptWaitResult {
    ok: boolean;
    reverted?: boolean;
    rpcUrl?: string;
    blockNumber?: string;
    reason?: string;
    attempts?: Array<{
        rpcUrl: string;
        error: string;
    }>;
}
export declare function waitForTransactionFinality(chain: string, txHash: string): Promise<ReceiptWaitResult>;
