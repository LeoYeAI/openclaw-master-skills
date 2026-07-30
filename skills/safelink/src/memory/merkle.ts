import { keccak256, encodePacked, encodeAbiParameters } from "viem";
import { createCipheriv, createDecipheriv, randomBytes } from "crypto";
import { MemoryError } from "../utils/errors.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface MemoryEntry {
  /** Unique key identifying this memory entry (no PII). */
  key: string;
  /** Arbitrary content — will be hashed into Merkle leaf. */
  content: string;
  /** Unix timestamp of this entry. */
  timestamp: number;
}

export interface MerkleResult {
  root: `0x${string}`;
  leaves: `0x${string}`[];
  /** Proof for each leaf (index-aligned with leaves). */
  proofs: `0x${string}`[][];
}

export interface EncryptedPayload {
  ciphertext: string; // hex
  iv: string;         // hex (12 bytes for AES-GCM)
  tag: string;        // hex (16 bytes auth tag)
}

// ── Merkle tree ───────────────────────────────────────────────────────────────

/**
 * Build a Merkle tree from an array of memory entries.
 * Each leaf = keccak256(abi.encode(key, contentHash, timestamp)).
 */
export function buildMerkleTree(entries: MemoryEntry[]): MerkleResult {
  if (entries.length === 0) {
    throw new MemoryError("Cannot build Merkle tree from empty entries array");
  }

  // Compute leaves
  const leaves: `0x${string}`[] = entries.map((entry) => {
    const contentHash = keccak256(encodePacked(["string"], [entry.content]));
    return keccak256(
      encodeAbiParameters(
        [
          { name: "key", type: "string" },
          { name: "contentHash", type: "bytes32" },
          { name: "timestamp", type: "uint256" },
        ],
        [entry.key, contentHash, BigInt(entry.timestamp)]
      )
    );
  });

  // Build tree layer by layer
  const tree: `0x${string}`[][] = [leaves];
  let current = leaves;

  while (current.length > 1) {
    const next: `0x${string}`[] = [];
    for (let i = 0; i < current.length; i += 2) {
      const left = current[i] as `0x${string}`;
      const right = (current[i + 1] ?? current[i]) as `0x${string}`; // duplicate last if odd
      // Sort for deterministic root regardless of leaf order
      const [a, b] = left <= right ? [left, right] : [right, left];
      next.push(keccak256(encodePacked(["bytes32", "bytes32"], [a, b])));
    }
    tree.push(next);
    current = next;
  }

  const root = current[0] as `0x${string}`;

  // Generate Merkle proofs for each leaf
  const proofs: `0x${string}`[][] = leaves.map((_, leafIdx) => {
    const proof: `0x${string}`[] = [];
    let idx = leafIdx;

    for (let level = 0; level < tree.length - 1; level++) {
      const levelNodes = tree[level] as `0x${string}`[];
      const siblingIdx = idx % 2 === 0 ? idx + 1 : idx - 1;
      const sibling = (levelNodes[siblingIdx] ?? levelNodes[idx]) as `0x${string}`;
      proof.push(sibling);
      idx = Math.floor(idx / 2);
    }

    return proof;
  });

  return { root, leaves, proofs };
}

/**
 * Verify a Merkle proof for a single leaf.
 */
export function verifyMerkleProof(
  leaf: `0x${string}`,
  proof: `0x${string}`[],
  root: `0x${string}`
): boolean {
  let computed: `0x${string}` = leaf;

  for (const sibling of proof) {
    const [a, b] =
      computed <= sibling ? [computed, sibling] : [sibling, computed];
    computed = keccak256(encodePacked(["bytes32", "bytes32"], [a, b]));
  }

  return computed === root;
}

// ── Encryption ────────────────────────────────────────────────────────────────

/**
 * Encrypt a session summary using AES-256-GCM.
 * The key is derived per-session and destroyed after use.
 */
export function encryptPayload(
  plaintext: string,
  key: Buffer
): EncryptedPayload {
  if (key.length !== 32) {
    throw new MemoryError("Encryption key must be exactly 32 bytes (AES-256)");
  }

  const iv = randomBytes(12); // 96-bit IV for AES-GCM
  const cipher = createCipheriv("aes-256-gcm", key, iv);

  const ciphertextBuf = Buffer.concat([
    cipher.update(plaintext, "utf8"),
    cipher.final(),
  ]);
  const tag = cipher.getAuthTag();

  return {
    ciphertext: ciphertextBuf.toString("hex"),
    iv: iv.toString("hex"),
    tag: tag.toString("hex"),
  };
}

/**
 * Decrypt an AES-256-GCM payload.
 */
export function decryptPayload(
  payload: EncryptedPayload,
  key: Buffer
): string {
  const iv = Buffer.from(payload.iv, "hex");
  const tag = Buffer.from(payload.tag, "hex");
  const ciphertext = Buffer.from(payload.ciphertext, "hex");

  const decipher = createDecipheriv("aes-256-gcm", key, iv);
  decipher.setAuthTag(tag);

  return decipher.update(ciphertext) + decipher.final("utf8");
}

/** Generate a fresh 256-bit session encryption key. */
export function generateSessionKey(): Buffer {
  return randomBytes(32);
}

/** Zero out a buffer (call after use to limit key material in memory). */
export function destroyKey(key: Buffer): void {
  key.fill(0);
}
