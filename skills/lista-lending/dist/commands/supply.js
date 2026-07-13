/**
 * Market supply command
 * Supply collateral to a Lista Lending market
 * After success, shows updated position and max borrowable
 */
import { getSDK, getChainId, SUPPORTED_CHAINS } from "../sdk.js";
import { executeSteps } from "../executor.js";
import { loadContext, TargetType, } from "../context.js";
import { mapMarketUserPosition } from "../utils/position.js";
import { InputValidationError, parsePositiveUnits } from "../utils/validators.js";
import { requireAmount, resolveMarketContext, } from "./shared/context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import { buildExecutionFailureOutput, buildPendingExecutionOutput, ensureStepsGenerated, } from "./shared/tx.js";
import { buildSdkErrorOutput } from "./shared/errors.js";
import { buildMarketPositionPayload } from "./shared/market.js";
export async function cmdSupply(args) {
    const ctx = loadContext();
    let operationContext;
    try {
        const amount = requireAmount(args.amount);
        const { marketId, chain, walletAddress, walletTopic } = resolveMarketContext(args, ctx, { supportedChains: SUPPORTED_CHAINS });
        const chainId = getChainId(chain);
        const sdk = getSDK();
        // 1. Get market info for collateral decimals
        const marketInfo = await sdk.getWriteConfig(chainId, marketId);
        const collateralInfo = marketInfo.collateralInfo;
        const decimals = collateralInfo.decimals;
        // 2. Parse amount with correct decimals
        const assets = parsePositiveUnits(amount, decimals, "amount");
        operationContext = { marketId, chain, amount };
        // 3. Build supply steps (may include approve step)
        const steps = ensureStepsGenerated(await sdk.buildSupplyParams({
            chainId,
            marketId,
            assets,
            walletAddress,
            marketInfo,
        }));
        // 4. Execute steps via lista-wallet-connect
        const results = await executeSteps(steps, {
            topic: walletTopic,
            chain,
        });
        // 5. Check result
        const lastResult = results[results.length - 1];
        if (lastResult.status === "pending") {
            printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
            exitWithCode(0);
        }
        if (lastResult.status === "sent") {
            // 6. Re-query position on-chain after successful supply
            const userData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
            const mappedPosition = mapMarketUserPosition(userData, {
                collateralPrice: 0,
                loanPrice: 0,
            });
            printJson({
                status: "success",
                market: marketId,
                chain,
                collateral: collateralInfo.symbol,
                supplied: amount,
                steps: results.length,
                txHash: lastResult.txHash,
                explorer: lastResult.explorer,
                position: buildMarketPositionPayload(mappedPosition, {
                    loanable: userData.loanable?.toFixed(8) || "0",
                }),
                hint: userData.loanable?.gt(0)
                    ? `You can now borrow up to ${userData.loanable.toFixed(4)} ${userData.loanInfo.symbol}`
                    : undefined,
            });
            exitWithCode(0);
        }
        printJson(buildExecutionFailureOutput(results, steps.length));
        exitWithCode(1);
    }
    catch (err) {
        if (err instanceof InputValidationError) {
            printJson({
                status: "error",
                reason: err.message,
            });
            exitWithCode(1);
        }
        const message = err.message || String(err);
        printJson(buildSdkErrorOutput(message, {
            targetType: TargetType.Market,
            targetId: operationContext?.marketId,
        }));
        exitWithCode(1);
    }
}
