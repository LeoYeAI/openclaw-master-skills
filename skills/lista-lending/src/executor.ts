/**
 * Transaction executor - bridges SDK steps to lista-wallet-connect call command
 */

import { execSync } from "child_process";
import type { StepParam } from "@lista-dao/moolah-lending-sdk";
import type { TxResult } from "./types.js";
import { mapWalletConnectResponse, mapExecutionError } from "./utils/tx-error.js";
import { getExplorerUrl, WALLET_CONNECT_CLI } from "./executor/constants.js";
import { waitForTransactionFinality } from "./executor/receipt.js";

export interface ExecuteOptions {
  topic: string;
  chain?: string;
}

export async function executeStep(
  step: StepParam,
  options: ExecuteOptions
): Promise<TxResult> {
  const { topic, chain = "eip155:56" } = options;
  const { params } = step;

  const args = [
    "call",
    "--topic",
    topic,
    "--chain",
    chain,
    "--to",
    params.to,
    "--data",
    params.data,
  ];

  if (params.value && params.value > 0n) {
    args.push("--value", params.value.toString());
  }

  try {
    const cmd = `node "${WALLET_CONNECT_CLI}" ${args.map((a) => `"${a}"`).join(" ")}`;
    const result = execSync(cmd, {
      encoding: "utf-8",
      timeout: 5 * 60 * 1000,
      env: {
        ...process.env,
        WALLETCONNECT_PROJECT_ID: process.env.WALLETCONNECT_PROJECT_ID,
      },
    });

    const lines = result.trim().split("\n");
    const response = JSON.parse(lines[lines.length - 1]);
    const txResult = mapWalletConnectResponse(
      response,
      step.step,
      response.txHash ? getExplorerUrl(chain, response.txHash) : undefined
    );
    if (txResult.status !== "sent") {
      return txResult;
    }
    if (!txResult.txHash) {
      return {
        status: "error",
        reason: "wallet_connect_missing_tx_hash",
        step: step.step,
      };
    }

    const receiptResult = await waitForTransactionFinality(chain, txResult.txHash);
    if (!receiptResult.ok) {
      return {
        status: "pending",
        reason: receiptResult.reason || "tx_submitted_pending_confirmation",
        step: step.step,
        txHash: txResult.txHash,
        explorer: txResult.explorer,
      };
    }

    if (receiptResult.reverted) {
      return {
        status: "reverted",
        reason: "transaction_reverted_onchain",
        step: step.step,
        txHash: txResult.txHash,
        explorer: txResult.explorer,
      };
    }

    return txResult;
  } catch (err) {
    return mapExecutionError(err, step.step);
  }
}

export async function executeSteps(
  steps: StepParam[],
  options: ExecuteOptions
): Promise<TxResult[]> {
  const results: TxResult[] = [];
  for (let i = 0; i < steps.length; i++) {
    const result = await executeStep(steps[i], options);
    results.push(result);
    if (result.status !== "sent") break;
  }
  return results;
}
