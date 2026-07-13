/**
 * Vault withdraw command
 * Withdraws assets from a Lista Lending vault
 * After success, re-queries position on-chain
 */
import { getSDK, getChainId, SUPPORTED_CHAINS } from "../sdk.js";
import { executeSteps } from "../executor.js";
import { loadContext, TargetType, updatePosition, } from "../context.js";
import { mapVaultUserPosition } from "../utils/position.js";
import { InputValidationError, parsePositiveUnits } from "../utils/validators.js";
import { requireAmountOrAll, resolveVaultContext, } from "./shared/context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import { buildExecutionFailureOutput, buildPendingExecutionOutput, ensureStepsGenerated, } from "./shared/tx.js";
import { buildSdkErrorOutput } from "./shared/errors.js";
export async function cmdWithdraw(args) {
    const ctx = loadContext();
    let operationContext;
    try {
        requireAmountOrAll(args.amount, args.withdrawAll, "--withdraw-all");
        const { vaultAddress, chain, walletAddress, walletTopic } = resolveVaultContext(args, ctx, { supportedChains: SUPPORTED_CHAINS });
        const chainId = getChainId(chain);
        const sdk = getSDK();
        // 1. Get vault info
        const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
        // 2. Get user data (required for withdraw-all)
        const userData = await sdk.getVaultUserData(chainId, vaultAddress, walletAddress, vaultInfo);
        if (args.withdrawAll && (!userData.shares || userData.shares.isZero())) {
            printJson({
                status: "error",
                reason: "no_position",
                message: "No shares to withdraw from this vault",
            });
            exitWithCode(1);
        }
        // 3. Parse amount (SDK uses assetInfo)
        const assetInfo = vaultInfo.assetInfo;
        const decimals = assetInfo.decimals;
        let assets;
        if (args.amount) {
            assets = parsePositiveUnits(args.amount, decimals, "amount");
        }
        const operationAmount = args.amount || "all";
        operationContext = {
            vaultAddress,
            chain,
            amount: operationAmount,
        };
        // 4. Build withdraw steps
        const steps = ensureStepsGenerated(await sdk.buildVaultWithdrawParams({
            chainId,
            vaultAddress,
            assets,
            withdrawAll: args.withdrawAll,
            walletAddress,
            vaultInfo,
            userData,
        }));
        // 5. Execute steps via lista-wallet-connect
        const results = await executeSteps(steps, {
            topic: walletTopic,
            chain,
        });
        // 6. Check result
        const lastResult = results[results.length - 1];
        if (lastResult.status === "pending") {
            printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
            exitWithCode(0);
        }
        if (lastResult.status === "sent") {
            // 7. Re-query position on-chain after successful withdraw
            // Re-fetch vault info to get fresh state after withdraw
            const freshVaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
            const newUserData = await sdk.getVaultUserData(chainId, vaultAddress, walletAddress, freshVaultInfo);
            const mappedPosition = mapVaultUserPosition(newUserData);
            const newPosition = mappedPosition.position;
            // Update context if this is the selected vault
            if (ctx.selectedVault?.address === vaultAddress) {
                updatePosition(newPosition);
            }
            printJson({
                status: "success",
                vault: vaultAddress,
                chain,
                asset: assetInfo.symbol,
                withdrawn: operationAmount,
                txHash: lastResult.txHash,
                explorer: lastResult.explorer,
                balance: mappedPosition.walletBalance,
                vaultBalance: newPosition.assets,
                position: {
                    balance: newPosition.assets,
                    assets: newPosition.assets,
                    walletBalance: mappedPosition.walletBalance,
                    assetSymbol: assetInfo.symbol,
                    remaining: newPosition.assets !== "0",
                },
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
            targetType: TargetType.Vault,
            targetId: operationContext?.vaultAddress,
            insufficientReason: "insufficient_assets",
            insufficientMessage: "Withdrawal amount exceeds your vault balance",
            insufficientKeywords: ["insufficient", "exceeds balance"],
        }));
        exitWithCode(1);
    }
}
