import { getSDK, getChainId, SUPPORTED_CHAINS, getMarketRuntimeData } from "../sdk.js";
import { loadContext, TargetType } from "../context.js";
import { InputValidationError } from "../utils/validators.js";
import { requireAmountOrAll, resolveMarketContext } from "./shared/context.js";
import { buildSdkErrorOutput } from "./shared/errors.js";
import { getRepayNoDebtError } from "./shared/market.js";
import { printJson, exitWithCode } from "./shared/output.js";
import { executeRepayTransaction } from "./repay/execute.js";
import { buildRepaySimulationPayload } from "./repay/simulate.js";
export async function cmdRepay(args) {
    const ctx = loadContext();
    let marketId;
    try {
        requireAmountOrAll(args.amount, args.repayAll, "--repay-all");
        const { marketId: resolvedMarketId, chain, walletAddress, walletTopic, } = resolveMarketContext(args, ctx, {
            supportedChains: SUPPORTED_CHAINS,
            requireWalletTopic: !args.simulate,
        });
        marketId = resolvedMarketId;
        const chainId = getChainId(chain);
        const runtime = {
            sdk: getSDK(),
            marketId: resolvedMarketId,
            chain,
            chainId,
            walletAddress,
            walletTopic,
            ...(await getMarketRuntimeData(chainId, resolvedMarketId, walletAddress)),
        };
        if (runtime.userData.borrowed.isZero()) {
            printJson(getRepayNoDebtError());
            exitWithCode(1);
        }
        if (args.simulate) {
            printJson(await buildRepaySimulationPayload(args, runtime));
            exitWithCode(0);
        }
        const result = await executeRepayTransaction(runtime, args);
        printJson(result.payload);
        exitWithCode(result.exitCode);
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
            targetId: marketId,
            insufficientReason: "insufficient_balance",
            insufficientMessage: "Insufficient loan token balance in wallet to repay",
        }));
        exitWithCode(1);
    }
}
