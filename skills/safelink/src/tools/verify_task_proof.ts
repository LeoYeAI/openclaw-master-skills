import { z } from "zod";
import { encodePacked, keccak256 } from "viem";
import { EvmAddress, validateInput } from "../security/input-gate.js";
import { getEscrowRecord } from "../payments/escrow.js";

const VerifyTaskProofSchema = z.object({
  escrow_id: z.string().regex(/^0x[a-fA-F0-9]{64}$/),
  session_id: z.string().regex(/^[a-f0-9]{32}$/),
  agent_id: EvmAddress,
  proof_hash: z.string().regex(/^0x[a-fA-F0-9]{64}$/),
  check_onchain: z.boolean().optional().default(true),
  zk_proof: z.string().optional(),
  tee_attestation: z.string().optional(),
});

export async function verify_task_proof(rawInput: unknown) {
  const input = validateInput(VerifyTaskProofSchema, rawInput);
  const expected = keccak256(
    encodePacked(["string", "address"], [input.session_id, input.agent_id as `0x${string}`])
  );
  const localMatch = expected.toLowerCase() === input.proof_hash.toLowerCase();

  let onchainMatch: boolean | undefined;
  let escrowStatus: string | undefined;

  if (input.check_onchain) {
    const record = await getEscrowRecord(input.escrow_id as `0x${string}`);
    onchainMatch = record.proofCommitment.toLowerCase() === input.proof_hash.toLowerCase();
    escrowStatus = record.status;
  }

  return {
    verified:
      localMatch &&
      (onchainMatch === undefined || onchainMatch),
    local_match: localMatch,
    onchain_match: onchainMatch,
    escrow_status: escrowStatus,
    expected_proof_hash: expected,
    zk_hook: input.zk_proof ? "received_not_verified" : "not_provided",
    tee_hook: input.tee_attestation ? "received_not_verified" : "not_provided",
  };
}
