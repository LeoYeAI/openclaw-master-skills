/**
 * Market withdraw command
 * Withdraw collateral from a Lista Lending market
 *
 * Features:
 * - --amount: Withdraw specific amount
 * - --withdraw-all: Withdraw all collateral (only if no debt)
 */

import { Decimal } from "@lista-dao/moolah-sdk-core";
import {
  getSDK,
  getChainId,
  SUPPORTED_CHAINS,
  getMarketRuntimeData,
} from "../sdk.js";
import { executeSteps } from "../executor.js";
import {
  loadContext,
  TargetType,
} from "../context.js";
import type { ParsedArgs } from "../types.js";
import { mapMarketUserPosition } from "../utils/position.js";
import { InputValidationError, parsePositiveUnits } from "../utils/validators.js";
import {
  requireAmountOrAll,
  resolveMarketContext,
} from "./shared/context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import {
  buildExecutionFailureOutput,
  buildPendingExecutionOutput,
  ensureStepsGenerated,
} from "./shared/tx.js";
import { buildSdkErrorOutput } from "./shared/errors.js";
import {
  buildMarketPositionPayload,
  getExceedsWithdrawableError,
  getWithdrawAllHasDebtError,
  getWithdrawNoCollateralError,
} from "./shared/market.js";

export async function cmdMarketWithdraw(args: ParsedArgs): Promise<void> {
  const ctx = loadContext();
  let operationContext:
    | {
        marketId: string;
        chain: string;
        amount: string;
      }
    | undefined;

  try {
    requireAmountOrAll(args.amount, args.withdrawAll, "--withdraw-all");
    const { marketId, chain, walletAddress, walletTopic } = resolveMarketContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();

    // 1. Get market info and user data
    const { marketInfo, userData } = await getMarketRuntimeData(
      chainId,
      marketId,
      walletAddress
    );
    const collateralInfo = marketInfo.collateralInfo;

    // Check if user has collateral to withdraw
    if (userData.collateral.isZero()) {
      printJson(getWithdrawNoCollateralError());
      exitWithCode(1);
    }

    // Check if user can withdraw all (only if no debt)
    if (args.withdrawAll && !userData.borrowed.isZero()) {
      printJson(getWithdrawAllHasDebtError(userData));
      exitWithCode(1);
    }

    // 2. Parse amount (if not withdraw-all)
    const decimals = collateralInfo.decimals;
    let assets: bigint | undefined;
    if (args.amount) {
      assets = parsePositiveUnits(args.amount, decimals, "amount");
      const requestedWithdrawAmount = new Decimal(assets, decimals);

      // Check if withdraw amount exceeds withdrawable
      if (userData.withdrawable.lt(requestedWithdrawAmount)) {
        printJson(
          getExceedsWithdrawableError(args.amount, userData, collateralInfo.symbol)
        );
        exitWithCode(1);
      }
    }

    const operationAmount = args.amount || "all";
    operationContext = {
      marketId,
      chain,
      amount: operationAmount,
    };

    // 3. Build withdraw steps
    const steps = ensureStepsGenerated(
      await sdk.buildWithdrawParams({
        chainId,
        marketId,
        assets,
        withdrawAll: args.withdrawAll,
        walletAddress,
        marketInfo,
        userData,
      })
    );

    // 4. Execute steps via lista-wallet-connect
    const results = await executeSteps(steps, {
      topic: walletTopic!,
      chain,
    });

    // 5. Check result
    const lastResult = results[results.length - 1];

    if (lastResult.status === "pending") {
      printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
      exitWithCode(0);
    }

    if (lastResult.status === "sent") {
      // 6. Re-query position on-chain after successful withdraw
      const newUserData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
      const mappedPosition = mapMarketUserPosition(newUserData, {
        collateralPrice: 0,
        loanPrice: 0,
      });

      printJson({
        status: "success",
        market: marketId,
        chain,
        collateral: collateralInfo.symbol,
        withdrawn: operationAmount,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          withdrawable: newUserData.withdrawable?.toFixed(8) || "0",
          remainingCollateral: mappedPosition.collateral !== "0",
        }),
      });
      exitWithCode(0);
    }

    printJson(buildExecutionFailureOutput(results, steps.length));
    exitWithCode(1);
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
        targetId: operationContext?.marketId,
        insufficientReason: "exceeds_withdrawable",
        insufficientMessage: "Withdraw amount exceeds available withdrawable collateral",
      })
    );
    exitWithCode(1);
  }
}
