import { Decimal } from "@lista-dao/moolah-sdk-core";
import { executeSteps } from "../../executor.js";
import { mapMarketUserPosition } from "../../utils/position.js";
import { parsePositiveUnits } from "../../utils/validators.js";
import { buildMarketPositionPayload } from "../shared/market.js";
import { buildExecutionFailureOutput, buildPendingExecutionOutput, ensureStepsGenerated, } from "../shared/tx.js";
export async function executeBorrowTransaction(runtime, amount) {
    const { marketId, chain, chainId, walletAddress, walletTopic, marketInfo, userData, } = runtime;
    const loanInfo = marketInfo.loanInfo;
    const assets = parsePositiveUnits(amount, loanInfo.decimals, "amount");
    const requestedAmount = new Decimal(assets, loanInfo.decimals);
    if (userData.loanable.lt(requestedAmount)) {
        return {
            exitCode: 1,
            payload: {
                status: "error",
                reason: "insufficient_collateral",
                message: `Cannot borrow ${amount} ${loanInfo.symbol}. Max borrowable: ${userData.loanable.toFixed(4)} ${loanInfo.symbol}`,
                maxBorrowable: userData.loanable.toFixed(8),
                hint: "Supply more collateral or reduce borrow amount",
            },
        };
    }
    const steps = ensureStepsGenerated(await runtime.sdk.buildBorrowParams({
        chainId,
        marketId,
        assets,
        walletAddress,
        marketInfo,
    }));
    const results = await executeSteps(steps, {
        topic: walletTopic,
        chain,
    });
    const lastResult = results[results.length - 1];
    if (lastResult.status === "pending") {
        return {
            exitCode: 0,
            payload: buildPendingExecutionOutput(lastResult, results, steps.length),
        };
    }
    if (lastResult.status === "sent") {
        const newUserData = await runtime.sdk.getMarketUserData(chainId, marketId, walletAddress);
        const mappedPosition = mapMarketUserPosition(newUserData, {
            collateralPrice: 0,
            loanPrice: 0,
        });
        return {
            exitCode: 0,
            payload: {
                status: "success",
                market: marketId,
                chain,
                loan: loanInfo.symbol,
                borrowed: amount,
                txHash: lastResult.txHash,
                explorer: lastResult.explorer,
                position: buildMarketPositionPayload(mappedPosition, {
                    loanable: newUserData.loanable?.toFixed(8) || "0",
                }),
                warning: parseFloat(mappedPosition.health) < 1.2
                    ? "Health factor is low. Consider repaying some debt to avoid liquidation."
                    : undefined,
            },
        };
    }
    return {
        exitCode: 1,
        payload: buildExecutionFailureOutput(results, steps.length),
    };
}
