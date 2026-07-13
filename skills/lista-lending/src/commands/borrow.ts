import { getSDK, getChainId, SUPPORTED_CHAINS, getMarketRuntimeData } from "../sdk.js";
import { loadContext, TargetType } from "../context.js";
import type { ParsedArgs } from "../types.js";
import { InputValidationError } from "../utils/validators.js";
import { resolveMarketContext } from "./shared/context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import { buildSdkErrorOutput } from "./shared/errors.js";
import { executeBorrowTransaction } from "./borrow/execute.js";
import { buildBorrowSimulationPayload } from "./borrow/simulate.js";
import type { BorrowRuntime } from "./borrow/types.js";

export async function cmdBorrow(args: ParsedArgs): Promise<void> {
  const ctx = loadContext();
  let marketId: string | undefined;

  try {
    if (!args.simulate && !args.amount) {
      throw new InputValidationError("--amount or --simulate required");
    }

    const {
      marketId: resolvedMarketId,
      chain,
      walletAddress,
      walletTopic,
    } = resolveMarketContext(args, ctx, {
      supportedChains: SUPPORTED_CHAINS,
      requireWalletTopic: !args.simulate,
    });

    marketId = resolvedMarketId;
    const chainId = getChainId(chain);

    const runtime: BorrowRuntime = {
      sdk: getSDK(),
      marketId: resolvedMarketId,
      chain,
      chainId,
      walletAddress,
      walletTopic,
      ...(await getMarketRuntimeData(chainId, resolvedMarketId, walletAddress)),
    };

    if (args.simulate) {
      printJson(await buildBorrowSimulationPayload(args, runtime));
      exitWithCode(0);
    }

    const result = await executeBorrowTransaction(runtime, args.amount as string);
    printJson(result.payload);
    exitWithCode(result.exitCode);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message,
      });
      exitWithCode(1);
    }

    const message = (err as Error).message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: TargetType.Market,
        targetId: marketId,
        insufficientReason: "insufficient_collateral",
        insufficientMessage: "Borrow amount exceeds available collateral capacity",
      })
    );
    exitWithCode(1);
  }
}
