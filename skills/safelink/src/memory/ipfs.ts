import { createHelia } from "helia";
import { unixfs } from "@helia/unixfs";
import { MemoryBlockstore } from "blockstore-core";
import { MemoryDatastore } from "datastore-core";
import { MemoryError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface IPFSUploadResult {
  cid: string;
  url: string;
  sizeBytes: number;
}

// ── Helia IPFS node (in-process) ─────────────────────────────────────────────

let _helia: Awaited<ReturnType<typeof createHelia>> | undefined;

async function getHeliaNode() {
  if (_helia) return _helia;

  _helia = await createHelia({
    blockstore: new MemoryBlockstore(),
    datastore: new MemoryDatastore(),
  });

  logger.debug({ event: "helia_started" });
  return _helia;
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Upload content to IPFS via an in-process Helia node.
 * Content is encrypted before upload — never store plaintext.
 *
 * @param content  Already-encrypted bytes (encrypt before calling this)
 * @returns        CID and public gateway URL
 */
export async function uploadToIPFS(
  content: Uint8Array
): Promise<IPFSUploadResult> {
  const helia = await getHeliaNode();
  const fs = unixfs(helia);

  try {
    const cid = await fs.addBytes(content);
    const cidStr = cid.toString();

    logger.info({ event: "ipfs_upload", cid: cidStr, sizeBytes: content.length });

    return {
      cid: cidStr,
      url: `https://ipfs.io/ipfs/${cidStr}`,
      sizeBytes: content.length,
    };
  } catch (err) {
    throw new MemoryError(
      `IPFS upload failed: ${err instanceof Error ? err.message : String(err)}`
    );
  }
}

/**
 * Download content from IPFS by CID.
 * Returns raw bytes (caller is responsible for decryption).
 */
export async function downloadFromIPFS(cid: string): Promise<Uint8Array> {
  const helia = await getHeliaNode();
  const fs = unixfs(helia);

  const { CID } = await import("multiformats/cid");
  const parsedCid = CID.parse(cid);

  const chunks: Uint8Array[] = [];
  for await (const chunk of fs.cat(parsedCid)) {
    chunks.push(chunk);
  }

  const totalLength = chunks.reduce((acc, c) => acc + c.length, 0);
  const result = new Uint8Array(totalLength);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }

  return result;
}

/** Gracefully stop the Helia node (call on process exit). */
export async function stopHeliaNode(): Promise<void> {
  if (_helia) {
    await _helia.stop();
    _helia = undefined;
    logger.debug({ event: "helia_stopped" });
  }
}
