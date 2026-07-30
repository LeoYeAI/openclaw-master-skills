import { describe, it, expect } from "vitest";
import {
  buildMerkleTree,
  verifyMerkleProof,
  encryptPayload,
  decryptPayload,
  generateSessionKey,
  destroyKey,
} from "../../src/memory/merkle.js";

describe("buildMerkleTree", () => {
  const sampleEntries = [
    { key: "session:abc:summary", content: "Task completed successfully", timestamp: 1000 },
    { key: "session:abc:timestamp", content: "2025-01-01T00:00:00Z", timestamp: 1001 },
  ];

  it("builds tree with correct root (bytes32 hex)", () => {
    const { root } = buildMerkleTree(sampleEntries);
    expect(root).toMatch(/^0x[a-fA-F0-9]{64}$/);
  });

  it("produces deterministic root for same inputs", () => {
    const { root: r1 } = buildMerkleTree(sampleEntries);
    const { root: r2 } = buildMerkleTree(sampleEntries);
    expect(r1).toBe(r2);
  });

  it("produces different roots for different inputs", () => {
    const { root: r1 } = buildMerkleTree(sampleEntries);
    const { root: r2 } = buildMerkleTree([
      { ...sampleEntries[0]!, content: "Different content" },
      sampleEntries[1]!,
    ]);
    expect(r1).not.toBe(r2);
  });

  it("leaf count matches entry count", () => {
    const { leaves } = buildMerkleTree(sampleEntries);
    expect(leaves).toHaveLength(sampleEntries.length);
  });

  it("handles single entry", () => {
    const { root, leaves } = buildMerkleTree([sampleEntries[0]!]);
    expect(root).toMatch(/^0x[a-fA-F0-9]{64}$/);
    expect(leaves).toHaveLength(1);
  });

  it("throws on empty array", () => {
    expect(() => buildMerkleTree([])).toThrow("empty entries");
  });
});

describe("verifyMerkleProof", () => {
  const entries = [
    { key: "k1", content: "c1", timestamp: 1 },
    { key: "k2", content: "c2", timestamp: 2 },
    { key: "k3", content: "c3", timestamp: 3 },
    { key: "k4", content: "c4", timestamp: 4 },
  ];

  it("verifies proofs for all leaves", () => {
    const { root, leaves, proofs } = buildMerkleTree(entries);
    for (let i = 0; i < leaves.length; i++) {
      expect(verifyMerkleProof(leaves[i]!, proofs[i]!, root)).toBe(true);
    }
  });

  it("rejects wrong root", () => {
    const { leaves, proofs } = buildMerkleTree(entries);
    const fakeRoot = "0x" + "ff".repeat(32) as `0x${string}`;
    expect(verifyMerkleProof(leaves[0]!, proofs[0]!, fakeRoot)).toBe(false);
  });

  it("rejects tampered leaf", () => {
    const { root, leaves, proofs } = buildMerkleTree(entries);
    const tampered = ("0x" + "aa".repeat(32)) as `0x${string}`;
    expect(verifyMerkleProof(tampered, proofs[0]!, root)).toBe(false);
  });
});

describe("encrypt/decrypt", () => {
  it("round-trips plaintext", () => {
    const key = generateSessionKey();
    const plaintext = "Hello, safe memory!";
    const payload = encryptPayload(plaintext, key);
    const decrypted = decryptPayload(payload, key);
    expect(decrypted).toBe(plaintext);
    destroyKey(key);
  });

  it("produces different ciphertext each time (random IV)", () => {
    const key = generateSessionKey();
    const p1 = encryptPayload("same plaintext", key);
    const p2 = encryptPayload("same plaintext", key);
    expect(p1.ciphertext).not.toBe(p2.ciphertext);
    expect(p1.iv).not.toBe(p2.iv);
    destroyKey(key);
  });

  it("rejects wrong key on decrypt", () => {
    const key1 = generateSessionKey();
    const key2 = generateSessionKey();
    const payload = encryptPayload("secret", key1);
    expect(() => decryptPayload(payload, key2)).toThrow();
    destroyKey(key1);
    destroyKey(key2);
  });

  it("rejects tampered ciphertext", () => {
    const key = generateSessionKey();
    const payload = encryptPayload("secret", key);
    const tampered = { ...payload, ciphertext: "deadbeef".repeat(8) };
    expect(() => decryptPayload(tampered, key)).toThrow();
    destroyKey(key);
  });

  it("throws on wrong key length", () => {
    const shortKey = Buffer.alloc(16);
    expect(() => encryptPayload("test", shortKey)).toThrow("32 bytes");
  });
});
