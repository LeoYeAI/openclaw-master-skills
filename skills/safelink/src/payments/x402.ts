import { getConfig } from "../utils/config.js";
import { PaymentError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { getMPCWalletClient } from "../wallet/mpc.js";
import { USDC_ADDRESSES, getUSDCAddress } from "./usdc.js";
import { getPublicClient } from "../wallet/provider.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export type PaymentModel = "per_request" | "per_min" | "per_execution";

export interface X402PaymentRequest {
  /** Target agent's registered payment endpoint or address. */
  agentId: `0x${string}`;
  /** Amount in human-readable USDC (e.g. 0.05 for 5 cents). */
  amount: bigint;
  /** Payment cadence. */
  paymentModel: PaymentModel;
}

export interface X402PaymentResult {
  /** x402 payment receipt — attach to subsequent task request as proof. */
  receipt: string;
  /** Transaction hash of the USDC transfer. */
  txHash: `0x${string}`;
  /** Amount paid in atomic USDC units. */
  amountPaid: bigint;
}

// ── x402 payment header constants ─────────────────────────────────────────────
// Based on: https://github.com/coinbase/x402
// The x402 protocol works as follows:
//   1. Client sends request to agent endpoint (no payment yet)
//   2. Agent returns HTTP 402 with X-Payment-Required header
//   3. Client sends X-Payment header with signed payment proof
//   4. Agent verifies payment and fulfils request

const X402_PAYMENT_REQUIRED_STATUS = 402;

function getUSDCNetwork(baseRpcUrl: string): "base-sepolia" | "base-mainnet" {
  return baseRpcUrl.includes("mainnet") ? "base-mainnet" : "base-sepolia";
}

// ── x402 client ───────────────────────────────────────────────────────────────

/**
 * Execute an x402 micropayment to a target agent.
 *
 * Flow:
 *   1. Call facilitator to get payment requirements for this agent
 *   2. Build EIP-712 payment authorization (USDC transfer via permit)
 *   3. MPC-sign the authorization (key never leaves Privy HSM)
 *   4. Submit signed authorization to facilitator
 *   5. Receive receipt → use as proof in task request
 */
export async function sendX402Payment(
  req: X402PaymentRequest
): Promise<X402PaymentResult> {
  const config = getConfig();
  const wallet = await getMPCWalletClient();
  const usdcNetwork = getUSDCNetwork(config.BASE_RPC_URL);

  logger.info({
    event: "x402_payment_start",
    agentId: req.agentId,
    paymentModel: req.paymentModel,
    network: usdcNetwork,
  });

  // Step 1: Get payment requirements from facilitator
  const requirementsRes = await fetch(
    `${config.X402_FACILITATOR_URL}/requirements`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipient: req.agentId,
        network: usdcNetwork,
        amount: req.amount.toString(),
        token: USDC_ADDRESSES[usdcNetwork],
        paymentModel: req.paymentModel,
      }),
      signal: AbortSignal.timeout(15_000), // MED-07: prevent indefinite hang
    }
  );

  if (!requirementsRes.ok) {
    throw new PaymentError(
      `x402 facilitator error getting requirements: ${requirementsRes.status}`
    );
  }

  const requirements = (await requirementsRes.json()) as {
    payTo: `0x${string}`;
    amount: string;
    token: `0x${string}`;
    nonce: string;
    deadline: string;
    chainId: number;
  };

  // HIGH-04: Validate EIP-712 domain parameters from facilitator against known-good values.
  // A compromised or MITM'd facilitator could inject wrong chainId/token to steal funds.
  const expectedChainId = await getPublicClient().getChainId();
  const expectedToken = getUSDCAddress(config.BASE_RPC_URL);

  if (requirements.chainId !== expectedChainId) {
    throw new PaymentError(
      `Facilitator returned wrong chainId: ${requirements.chainId}, expected ${expectedChainId}. ` +
        "Possible MITM attack on x402 facilitator."
    );
  }
  if (requirements.token.toLowerCase() !== expectedToken.toLowerCase()) {
    throw new PaymentError(
      `Facilitator returned wrong token: ${requirements.token}, expected ${expectedToken}. ` +
        "Possible MITM attack on x402 facilitator."
    );
  }
  const deadlineTs = Number(requirements.deadline);
  const nowSec = Math.floor(Date.now() / 1000);
  if (deadlineTs < nowSec) {
    throw new PaymentError(`Payment deadline already expired: ${deadlineTs} < ${nowSec}`);
  }
  if (deadlineTs > nowSec + 3600) {
    throw new PaymentError("Payment deadline too far in the future (> 1 hour) — suspicious");
  }

  // Step 2: Build EIP-712 USDC permit/transfer authorization
  // This allows the facilitator to pull USDC from our wallet without
  // us needing to approve first — cleaner UX, one-shot.
  const typedData = {
    domain: {
      name: "USDC",
      version: "2",
      chainId: requirements.chainId,
      verifyingContract: requirements.token,
    },
    types: {
      TransferWithAuthorization: [
        { name: "from", type: "address" },
        { name: "to", type: "address" },
        { name: "value", type: "uint256" },
        { name: "validAfter", type: "uint256" },
        { name: "validBefore", type: "uint256" },
        { name: "nonce", type: "bytes32" },
      ],
    },
    primaryType: "TransferWithAuthorization" as const,
    message: {
      from: wallet.address,
      to: requirements.payTo,
      value: BigInt(requirements.amount),
      validAfter: 0n,
      validBefore: BigInt(requirements.deadline),
      nonce: requirements.nonce,
    },
  };

  // Step 3: MPC-sign (Privy HSM — private key never exposed)
  const signature = await wallet.signTypedData(typedData);

  // Step 4: Submit signed authorization to facilitator
  const paymentRes = await fetch(`${config.X402_FACILITATOR_URL}/pay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...typedData.message,
      value: typedData.message.value.toString(),
      validBefore: typedData.message.validBefore.toString(),
      signature,
      network: usdcNetwork,
    }),
    signal: AbortSignal.timeout(20_000), // MED-07
  });

  if (!paymentRes.ok) {
    const errBody = await paymentRes.text();
    throw new PaymentError(`x402 payment failed: ${paymentRes.status} — ${errBody}`);
  }

  const result = (await paymentRes.json()) as {
    receipt: string;
    txHash: `0x${string}`;
  };

  logger.info({
    event: "x402_payment_complete",
    agentId: req.agentId,
    txHash: result.txHash,
  });

  return {
    receipt: result.receipt,
    txHash: result.txHash,
    amountPaid: req.amount,
  };
}

/**
 * Verify an x402 receipt received from a hiring agent.
 * Call this in safe_listen_for_hire() before executing any task.
 */
export async function verifyX402Receipt(
  receipt: string,
  expectedAmount: bigint,
  expectedPayer?: `0x${string}`
): Promise<boolean> {
  const config = getConfig();
  const usdcNetwork = getUSDCNetwork(config.BASE_RPC_URL);

  const res = await fetch(`${config.X402_FACILITATOR_URL}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      receipt,
      expectedAmount: expectedAmount.toString(),
      expectedPayer,
      network: usdcNetwork,
    }),
    signal: AbortSignal.timeout(15_000), // MED-07
  });

  if (!res.ok) return false;

  const data = (await res.json()) as { valid: boolean };
  return data.valid;
}
