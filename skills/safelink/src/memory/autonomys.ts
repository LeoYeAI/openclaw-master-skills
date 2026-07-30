import { getConfig } from "../utils/config.js";
import { MemoryError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AutonomysUploadResult {
  cid: string;
  network: string;
  permanent: boolean;
}

// ── Autonomys Auto SDK integration ────────────────────────────────────────────
//
// Autonomys Auto Drive provides permanent decentralised storage.
// SDK: https://github.com/autonomys/auto-sdk / @autonomys/auto-drive
//
// ConnectionOptions:
//   { apiKey: string | null, network: "taurus" | "mainnet" }
//   { apiKey: string | null, apiUrl: string }  ← for custom endpoints

const AUTONOMYS_NETWORKS: Record<string, string> = {
  "taurus-testnet": "taurus",
  mainnet: "mainnet",
};

async function getAutoDriveApi() {
  const config = getConfig();
  const { createAutoDriveApi } = await import("@autonomys/auto-drive");

  if (config.AUTONOMYS_RPC_URL) {
    return createAutoDriveApi({
      apiKey: null,
      apiUrl: config.AUTONOMYS_RPC_URL,
    });
  }

  const network = (AUTONOMYS_NETWORKS[config.AUTONOMYS_NETWORK] ?? "taurus") as "taurus";
  return createAutoDriveApi({ apiKey: null, network });
}

/**
 * Upload encrypted memory checkpoint to Autonomys permanent storage.
 *
 * @param encryptedContent  AES-256-GCM encrypted bytes (already encrypted by caller)
 * @param filename          Logical filename — no PII
 * @returns                 CID and network info
 */
export async function uploadToAutonomys(
  encryptedContent: Uint8Array,
  filename: string
): Promise<AutonomysUploadResult> {
  const config = getConfig();

  try {
    const api = await getAutoDriveApi();

    // uploadFileFromBuffer(buffer, name, options) → CID string
    const cid = await api.uploadFileFromBuffer(
      Buffer.from(encryptedContent),
      filename,
      { compression: true }
    );

    logger.info({
      event: "autonomys_upload",
      cid,
      network: config.AUTONOMYS_NETWORK,
      sizeBytes: encryptedContent.length,
    });

    return {
      cid,
      network: config.AUTONOMYS_NETWORK,
      permanent: true,
    };
  } catch (err) {
    throw new MemoryError(
      `Autonomys upload failed: ${err instanceof Error ? err.message : String(err)}`
    );
  }
}
