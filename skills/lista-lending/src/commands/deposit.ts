/**
 * Vault deposit command
 * Deposits assets into a Lista Lending vault
 * After success, re-queries position on-chain
 */

import type { ParsedArgs, StepParam } from "../types.js";
import { getSDK, getChainId, SUPPORTED_CHAINS } from "../sdk.js";
import { executeSteps } from "../executor.js";
import {
  loadContext,
  TargetType,
  updatePosition,
  type UserPosition,
} from "../context.js";
import { mapVaultUserPosition } from "../utils/position.js";
import { InputValidationError, parsePositiveUnits } from "../utils/validators.js";
import {
  resolveVaultContext,
  requireAmount,
} from "./shared/context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import {
  buildExecutionFailureOutput,
  buildPendingExecutionOutput,
  ensureStepsGenerated,
} from "./shared/tx.js";
import { buildSdkErrorOutput } from "./shared/errors.js";

export async function cmdDeposit(args: ParsedArgs): Promise<void> {
  const ctx = loadContext();
  let operationContext:
    | {
        vaultAddress: string;
        chain: string;
        amount: string;
      }
    | undefined;

  try {
    const amount = requireAmount(args.amount);
    const { vaultAddress, chain, walletAddress, walletTopic } = resolveVaultContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();
    operationContext = {
      vaultAddress,
      chain,
      amount,
    };

    // 1. Get vault info to determine asset decimals
    const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);

    // 2. Parse amount with correct decimals (SDK uses assetInfo)
    const assetInfo = vaultInfo.assetInfo;
    const decimals = assetInfo.decimals;
    const assets = parsePositiveUnits(amount, decimals, "amount");
    // 3. Build deposit steps (may include approve step)
    const steps = ensureStepsGenerated(
      await sdk.buildVaultDepositParams({
        chainId,
        vaultAddress,
        assets,
        walletAddress,
        vaultInfo,
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
      // 6. Re-query position on-chain after successful deposit
      // Re-fetch vault info to get fresh state after deposit
      const freshVaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
      const userData = await sdk.getVaultUserData(
        chainId,
        vaultAddress,
        walletAddress,
        freshVaultInfo
      );

      const mappedPosition = mapVaultUserPosition(userData);

      const newPosition: UserPosition = mappedPosition.position;

      // Update context if this is the selected vault
      if (ctx.selectedVault?.address === vaultAddress) {
        updatePosition(newPosition);
      }

      printJson({
        status: "success",
        vault: vaultAddress,
        chain,
        asset: assetInfo.symbol,
        deposited: amount,
        steps: results.length,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        balance: mappedPosition.walletBalance,
        vaultBalance: newPosition.assets,
        position: {
          balance: newPosition.assets,
          assets: newPosition.assets,
          walletBalance: mappedPosition.walletBalance,
          assetSymbol: assetInfo.symbol,
        },
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
        targetType: TargetType.Vault,
        targetId: operationContext?.vaultAddress,
      })
    );
    exitWithCode(1);
  }
}
