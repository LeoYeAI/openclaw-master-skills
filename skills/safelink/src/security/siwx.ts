import { toError } from "../utils/errors.js";

interface VerifySIWxInput {
  assertion: string;
  payer: `0x${string}`;
  taskId: string;
  verifierUrl: string;
  timeoutMs?: number;
}

interface SIWxVerifyResponse {
  valid: boolean;
  subject?: string;
  expires_at?: string;
}

export async function verifySIWxAssertion(input: VerifySIWxInput): Promise<void> {
  const resp = await fetch(input.verifierUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      assertion: input.assertion,
      payer: input.payer,
      task_id: input.taskId,
      audience: "safelink-task",
    }),
    signal: AbortSignal.timeout(input.timeoutMs ?? 7_000),
  });

  if (!resp.ok) {
    throw new Error(`SIWx verifier returned ${resp.status}`);
  }

  let payload: SIWxVerifyResponse;
  try {
    payload = await resp.json() as SIWxVerifyResponse;
  } catch (err) {
    throw new Error(`SIWx verifier returned invalid JSON: ${toError(err).message}`);
  }

  if (!payload.valid) {
    throw new Error("SIWx assertion is invalid");
  }

  if (payload.expires_at) {
    const exp = Date.parse(payload.expires_at);
    if (!Number.isFinite(exp) || exp <= Date.now()) {
      throw new Error("SIWx assertion is expired");
    }
  }
}

