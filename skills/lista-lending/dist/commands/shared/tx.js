import { InputValidationError } from "../../utils/validators.js";
export function ensureStepsGenerated(steps) {
    if (steps.length === 0) {
        throw new InputValidationError("No steps generated");
    }
    return steps;
}
export function buildExecutionFailureOutput(results, totalSteps) {
    const lastResult = results[results.length - 1];
    const completedSteps = countCompletedSentSteps(results);
    const output = {
        status: lastResult?.status || "error",
        reason: lastResult?.reason || "execution_failed",
        failedStep: lastResult?.step,
        completedSteps,
        totalSteps,
    };
    const successfulTxs = collectSuccessfulTxs(results);
    if (successfulTxs.length > 0) {
        output.completedTxs = successfulTxs;
    }
    return output;
}
export function buildPendingExecutionOutput(result, results, totalSteps) {
    return {
        status: "pending",
        reason: result.reason || "tx_submitted_pending_confirmation",
        pendingStep: result.step,
        txHash: result.txHash,
        explorer: result.explorer,
        completedSteps: countCompletedSentSteps(results),
        totalSteps,
        message: "Transaction was submitted but confirmation is still pending. Please check explorer and avoid resubmitting the same action.",
    };
}
function countCompletedSentSteps(results) {
    return results.filter((r) => r.status === "sent").length;
}
function collectSuccessfulTxs(results) {
    return results
        .filter((r) => r.status === "sent")
        .map((r) => ({ step: r.step, txHash: r.txHash }));
}
