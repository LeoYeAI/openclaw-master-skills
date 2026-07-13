import type { StepParam } from "@lista-dao/moolah-lending-sdk";
import type { TxResult } from "../../types.js";
export declare function ensureStepsGenerated(steps: StepParam[]): StepParam[];
export declare function buildExecutionFailureOutput(results: TxResult[], totalSteps: number): Record<string, unknown>;
export declare function buildPendingExecutionOutput(result: Extract<TxResult, {
    status: "pending";
}>, results: TxResult[], totalSteps: number): Record<string, unknown>;
