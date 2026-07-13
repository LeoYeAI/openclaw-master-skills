/**
 * Transaction executor - bridges SDK steps to lista-wallet-connect call command
 */
import type { StepParam } from "@lista-dao/moolah-lending-sdk";
import type { TxResult } from "./types.js";
export interface ExecuteOptions {
    topic: string;
    chain?: string;
}
export declare function executeStep(step: StepParam, options: ExecuteOptions): Promise<TxResult>;
export declare function executeSteps(steps: StepParam[], options: ExecuteOptions): Promise<TxResult[]>;
