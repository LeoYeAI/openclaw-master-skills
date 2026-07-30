import { z } from "zod";
import { validateInput, stripPII } from "../security/input-gate.js";
import { uploadToIPFS } from "../memory/ipfs.js";
import { uploadToAutonomys } from "../memory/autonomys.js";
import {
  buildMerkleTree,
  encryptPayload,
  generateSessionKey,
  destroyKey,
  type MemoryEntry,
} from "../memory/merkle.js";
import { safe_execute_tx } from "./execute_tx.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { MemoryError, toError } from "../utils/errors.js";
import { generateText } from "../llm/client.js";

const CheckpointSchema = z.object({
  session_id: z
    .string()
    .min(1, "session_id is required")
    .describe("Session ID to checkpoint (from createTempSession)"),
  summary: z
    .string()
    .max(5000)
    .optional()
    .transform((s) => (s ? stripPII(s) : s))
    .describe("Optional manual summary; auto-generated if omitted"),
  persist_key: z
    .boolean()
    .optional()
    .default(false)
    .describe("If true, keep the session key for later retrieval (default: destroy after anchor)"),
});

export type CheckpointInput = z.infer<typeof CheckpointSchema>;

export interface CheckpointResult {
  ipfs_cid: string;
  autonomys_cid?: string;
  merkle_root: `0x${string}`;
  anchor_tx_hash: `0x${string}` | null;
  expires_at: string | null;
  entries_count: number;
}

async function summarizeSession(sessionId: string, manualSummary?: string): Promise<MemoryEntry[]> {
  if (manualSummary) {
    return [
      {
        key: `session:${sessionId}:summary`,
        content: manualSummary,
        timestamp: Date.now(),
      },
    ];
  }

  const summaryText =
    (await generateText({
      maxTokens: 512,
      system:
        "Summarise the session in 3-5 bullet points. Be concise. " +
        "Include: what was accomplished, any on-chain actions taken, status. " +
        "Remove all PII, private keys, and wallet addresses from the summary.",
      user: `Session ID: ${sessionId}\nGenerate a structured summary for archiving.`,
    })) || `Session ${sessionId} completed.`;

  return [
    {
      key: `session:${sessionId}:summary`,
      content: summaryText,
      timestamp: Date.now(),
    },
    {
      key: `session:${sessionId}:timestamp`,
      content: new Date().toISOString(),
      timestamp: Date.now(),
    },
  ];
}

export async function checkpoint_memory(rawInput: unknown): Promise<CheckpointResult> {
  const input = validateInput(CheckpointSchema, rawInput);
  const config = getConfig();

  logger.info({ event: "checkpoint_start", sessionId: input.session_id });

  const entries = await summarizeSession(input.session_id, input.summary);

  if (entries.length === 0) {
    throw new MemoryError("No memory entries to checkpoint");
  }

  const { root, leaves } = buildMerkleTree(entries);

  logger.debug({
    event: "merkle_built",
    root,
    leaves: leaves.length,
  });

  const sessionKey = generateSessionKey();
  let ipfsCid: string;
  let autonomysCid: string | undefined;

  try {
    const plaintext = JSON.stringify({
      sessionId: input.session_id,
      entries,
      merkleRoot: root,
      merkleLeaves: leaves,
      createdAt: new Date().toISOString(),
    });

    const encrypted = encryptPayload(plaintext, sessionKey);
    const encryptedBytes = Buffer.from(JSON.stringify(encrypted), "utf8");

    const ipfsResult = await uploadToIPFS(encryptedBytes);
    ipfsCid = ipfsResult.cid;

    try {
      const autonomysResult = await uploadToAutonomys(
        encryptedBytes,
        `safechain-checkpoint-${input.session_id.slice(0, 8)}.json`
      );
      autonomysCid = autonomysResult.cid;
    } catch (err) {
      logger.warn({
        event: "autonomys_upload_failed",
        reason: toError(err).message,
      });
    }
  } finally {
    if (!input.persist_key) {
      destroyKey(sessionKey);
    }
  }

  let anchorTxHash: `0x${string}` | null = null;

  if (config.ERC8004_REGISTRY_ADDRESS) {
    try {
      const txResult = await safe_execute_tx({
        intent_description: `Anchor SafeLink checkpoint root for session ${input.session_id.slice(0, 8)}`,
        tx: {
          to: config.ERC8004_REGISTRY_ADDRESS,
          data: root,
          value_wei: "0",
        },
        confirmed: true,
      });
      anchorTxHash = txResult.tx_hash;
    } catch (err) {
      logger.warn({
        event: "anchor_failed",
        reason: toError(err).message,
      });
    }
  }

  logger.info({
    event: "checkpoint_complete",
    ipfsCid,
    autonomysCid,
    merkleRoot: root,
    anchorTxHash,
  });

  return {
    ipfs_cid: ipfsCid,
    ...(autonomysCid !== undefined ? { autonomys_cid: autonomysCid } : {}),
    merkle_root: root,
    anchor_tx_hash: anchorTxHash,
    expires_at: null,
    entries_count: entries.length,
  };
}