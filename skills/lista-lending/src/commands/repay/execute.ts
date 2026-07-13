import { executeSteps } from "../../executor.js";
import type { ParsedArgs } from "../../types.js";
import { mapMarketUserPosition } from "../../utils/position.js";
import { parsePositiveUnits } from "../../utils/validators.js";
import {
  buildMarketPositionPayload,
  buildRepayHint,
} from "../shared/market.js";
import type { CommandResult } from "../shared/result.js";
import {
  buildExecutionFailureOutput,
  buildPendingExecutionOutput,
  ensureStepsGenerated,
} from "../shared/tx.js";
import type { RepayRuntime } from "./types.js";

export async function executeRepayTransaction(
  runtime: RepayRuntime,
  args: Pick<ParsedArgs, "amount" | "repayAll">
): Promise<CommandResult> {
  const { marketId, chain, chainId, walletAddress, walletTopic, marketInfo, userData } =
    runtime;

  let assets: bigint | undefined;
  if (args.amount) {
    assets = parsePositiveUnits(args.amount, marketInfo.loanInfo.decimals, "amount");
  }

  const steps = ensureStepsGenerated(
    await runtime.sdk.buildRepayParams({
      chainId,
      marketId,
      assets,
      repayAll: args.repayAll,
      walletAddress,
      marketInfo,
      userData,
    })
  );

  const results = await executeSteps(steps, {
    topic: walletTopic!,
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
    const newUserData = await runtime.sdk.getMarketUserData(
      chainId,
      marketId,
      walletAddress
    );
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
        loan: marketInfo.loanInfo.symbol,
        repaid: args.amount || "all",
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          withdrawable: newUserData.withdrawable?.toFixed(8) || "0",
          remainingDebt: mappedPosition.borrowed !== "0",
        }),
        hint: buildRepayHint(newUserData),
      },
    };
  }

  return {
    exitCode: 1,
    payload: buildExecutionFailureOutput(results, steps.length),
  };
}
