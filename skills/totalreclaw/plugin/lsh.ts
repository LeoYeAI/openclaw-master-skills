/**
 * TotalReclaw Plugin - LSH Hasher (Locality-Sensitive Hashing)
 *
 * Pure TypeScript implementation of Random Hyperplane LSH for server-blind
 * semantic search. Generates deterministic hyperplane matrices from a seed
 * derived from the user's master key, so the same embedding always hashes to
 * the same buckets across sessions.
 *
 * Architecture overview:
 *   1. Seed (32 bytes from HKDF) -> HKDF per table -> random bytes
 *   2. Random bytes -> Box-Muller transform -> Gaussian-distributed hyperplanes
 *   3. Embedding dot hyperplane -> sign bit -> N-bit signature per table
 *   4. Signature -> `lsh_t{table}_{signature}` -> SHA-256 -> blind hash
 *
 * The blind hashes are merged with the existing blind word indices in the
 * `blind_indices` array. The server never knows which hashes are word-based
 * and which are LSH-based.
 *
 * Default parameters:
 *   - 32 bits per table (balanced discrimination vs. recall)
 *   - 20 tables (moderate table count for good coverage)
 *   - Middle ground between 64-bit x 12 (too strict) and 12-bit x 28 (too loose)
 *
 * Dependencies: @noble/hashes only (already in project).
 */

import { hkdf } from '@noble/hashes/hkdf.js';
import { sha256 } from '@noble/hashes/sha2.js';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Default number of independent hash tables. */
const DEFAULT_N_TABLES = 20;

/** Default number of bits (hyperplanes) per table. */
const DEFAULT_N_BITS = 32;

/** Number of bytes needed per Gaussian float via Box-Muller (2 x uint32 = 8 bytes). */
const BYTES_PER_FLOAT = 8;

// ---------------------------------------------------------------------------
// LSHHasher
// ---------------------------------------------------------------------------

/**
 * Random Hyperplane LSH hasher.
 *
 * All state is deterministic from the seed -- no randomness at hash time.
 * Construct once per session; call `hash()` for every store/search operation.
 */
export class LSHHasher {
  /**
   * Flat hyperplane storage.
   *
   * `hyperplanes[t]` is a Float64Array of length `dims * nBits` containing the
   * hyperplane matrix for table `t`. The hyperplane for bit `b` starts at
   * offset `b * dims`.
   */
  private hyperplanes: Float64Array[];

  /** Embedding dimensionality. */
  private readonly dims: number;

  /** Number of independent hash tables. */
  private readonly nTables: number;

  /** Number of bits (hyperplanes) per table. */
  private readonly nBits: number;

  /**
   * Create a new LSH hasher.
   *
   * @param seed   - 32-byte seed from `deriveLshSeed()` in crypto.ts.
   * @param dims   - Embedding dimensionality (e.g. 1536 for text-embedding-3-small).
   * @param nTables - Number of independent hash tables (default 20).
   * @param nBits   - Number of bits per table (default 32).
   */
  constructor(
    seed: Uint8Array,
    dims: number,
    nTables: number = DEFAULT_N_TABLES,
    nBits: number = DEFAULT_N_BITS,
  ) {
    if (seed.length < 16) {
      throw new Error(`LSH seed too short: expected >= 16 bytes, got ${seed.length}`);
    }
    if (dims < 1) {
      throw new Error(`dims must be positive, got ${dims}`);
    }
    if (nTables < 1) {
      throw new Error(`nTables must be positive, got ${nTables}`);
    }
    if (nBits < 1) {
      throw new Error(`nBits must be positive, got ${nBits}`);
    }

    this.dims = dims;
    this.nTables = nTables;
    this.nBits = nBits;
    this.hyperplanes = new Array(nTables);

    // Generate hyperplane matrices deterministically from the seed.
    for (let t = 0; t < nTables; t++) {
      this.hyperplanes[t] = this.generateTableHyperplanes(seed, t);
    }
  }

  // -------------------------------------------------------------------------
  // Hyperplane generation (deterministic from seed)
  // -------------------------------------------------------------------------

  /**
   * Generate the hyperplane matrix for a single table.
   *
   * Each table gets a unique HKDF-derived byte stream. We consume 8 bytes
   * per Gaussian sample (Box-Muller uses two uniform uint32 values).
   *
   * The hyperplanes are NOT normalised to unit length. Normalisation is
   * unnecessary because we only care about the sign of the dot product,
   * which is scale-invariant.
   */
  private generateTableHyperplanes(seed: Uint8Array, tableIndex: number): Float64Array {
    const totalFloats = this.dims * this.nBits;
    const totalBytes = totalFloats * BYTES_PER_FLOAT;

    // Derive enough random bytes for this table.
    // HKDF can produce up to 255 * HashLen bytes (255 * 32 = 8,160 for SHA-256).
    // For large dims (e.g. 1536 * 64 * 8 = 786,432 bytes) we need multiple
    // HKDF calls with sub-block indexing.
    const randomBytes = this.deriveRandomBytes(
      seed,
      `lsh_table_${tableIndex}`,
      totalBytes,
    );

    // Convert the random bytes to Gaussian-distributed floats via Box-Muller.
    const hyperplaneMatrix = new Float64Array(totalFloats);
    const view = new DataView(randomBytes.buffer, randomBytes.byteOffset, randomBytes.byteLength);

    for (let i = 0; i < totalFloats; i++) {
      const offset = i * BYTES_PER_FLOAT;
      // Two uint32 values -> two uniform [0,1) samples -> one Gaussian via Box-Muller.
      const u1Raw = view.getUint32(offset, true);
      const u2Raw = view.getUint32(offset + 4, true);

      // Map to (0, 1] -- avoid exactly 0 for the log in Box-Muller.
      const u1 = (u1Raw + 1) / (0xFFFFFFFF + 2);
      const u2 = (u2Raw + 1) / (0xFFFFFFFF + 2);

      // Box-Muller transform (we only need one of the two outputs).
      hyperplaneMatrix[i] = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    return hyperplaneMatrix;
  }

  /**
   * Derive `length` pseudo-random bytes from the seed using HKDF with
   * chunked sub-blocks.
   *
   * A single HKDF-SHA256 call can output at most 255 * 32 = 8,160 bytes.
   * For large embedding dimensions we need more, so we iterate over
   * sub-block indices as part of the info string.
   */
  private deriveRandomBytes(
    seed: Uint8Array,
    baseInfo: string,
    length: number,
  ): Uint8Array {
    const MAX_HKDF_OUTPUT = 255 * 32; // SHA-256 hash length = 32
    const result = new Uint8Array(length);
    let offset = 0;
    let blockIndex = 0;

    while (offset < length) {
      const remaining = length - offset;
      const chunkLen = Math.min(remaining, MAX_HKDF_OUTPUT);
      const info = Buffer.from(`${baseInfo}_block_${blockIndex}`, 'utf8');
      const chunk = hkdf(sha256, seed, new Uint8Array(0), info, chunkLen);
      result.set(new Uint8Array(chunk), offset);
      offset += chunkLen;
      blockIndex++;
    }

    return result;
  }

  // -------------------------------------------------------------------------
  // Hash function
  // -------------------------------------------------------------------------

  /**
   * Hash an embedding vector to an array of blind-hashed bucket IDs.
   *
   * For each table:
   *   1. Compute the 64-bit signature (sign of dot product with each hyperplane).
   *   2. Build the bucket string: `lsh_t{tableIndex}_{binarySignature}`.
   *   3. SHA-256 the bucket string to produce a blind hash (hex).
   *
   * @param embedding - The embedding vector (must have `dims` elements).
   * @returns Array of `nTables` hex strings (one blind hash per table).
   */
  hash(embedding: number[]): string[] {
    if (embedding.length !== this.dims) {
      throw new Error(
        `Embedding dimension mismatch: expected ${this.dims}, got ${embedding.length}`,
      );
    }

    const results: string[] = new Array(this.nTables);

    for (let t = 0; t < this.nTables; t++) {
      const matrix = this.hyperplanes[t];

      // Build the binary signature.
      const bits = new Array<string>(this.nBits);
      for (let b = 0; b < this.nBits; b++) {
        const baseOffset = b * this.dims;
        let dot = 0;
        for (let d = 0; d < this.dims; d++) {
          dot += matrix[baseOffset + d] * embedding[d];
        }
        bits[b] = dot >= 0 ? '1' : '0';
      }

      const signature = bits.join('');
      const bucketId = `lsh_t${t}_${signature}`;

      // Blind-hash the bucket ID with SHA-256.
      const hashBytes = sha256(Buffer.from(bucketId, 'utf8'));
      results[t] = Buffer.from(hashBytes).toString('hex');
    }

    return results;
  }

  // -------------------------------------------------------------------------
  // Accessors
  // -------------------------------------------------------------------------

  /** Number of hash tables. */
  get tables(): number {
    return this.nTables;
  }

  /** Number of bits per table. */
  get bits(): number {
    return this.nBits;
  }

  /** Embedding dimensionality. */
  get dimensions(): number {
    return this.dims;
  }
}
