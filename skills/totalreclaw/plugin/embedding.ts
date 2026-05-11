/**
 * TotalReclaw Plugin - Local Embedding via @huggingface/transformers
 *
 * Uses the Qwen3-Embedding-0.6B ONNX model to generate 1024-dimensional
 * text embeddings locally. No API key needed, no data leaves the machine.
 * Supports 100+ languages (EN, PT, ES, ZH, etc.).
 *
 * This preserves the E2EE guarantee: embeddings are generated
 * CLIENT-SIDE before encryption, so no plaintext ever reaches an external API.
 *
 * Model details:
 *   - Quantized (int8) ONNX model: ~600MB download on first use
 *   - Cached in ~/.cache/huggingface/ after first download
 *   - Lazy initialization: first call ~3-5s (model load), subsequent ~100ms
 *   - Output: 1024-dimensional normalized embedding vector
 *   - No instruction prefix needed (bare queries perform better)
 *
 * Dependencies: @huggingface/transformers (handles model download,
 * tokenization, ONNX inference, last-token pooling, and normalization).
 */

// @ts-ignore - @huggingface/transformers types may not be perfect
import { pipeline, type FeatureExtractionPipeline } from '@huggingface/transformers';

/** ONNX-optimized Qwen3-Embedding-0.6B from HuggingFace Hub. */
const MODEL_ID = 'onnx-community/Qwen3-Embedding-0.6B-ONNX';

/** Fixed output dimensionality for Qwen3-Embedding-0.6B. */
const EMBEDDING_DIM = 1024;

/** Lazily initialized feature extraction pipeline. */
let extractor: FeatureExtractionPipeline | null = null;

/**
 * Generate a 1024-dimensional embedding vector for the given text.
 *
 * On first call, downloads and loads the ONNX model (~600MB, cached).
 * Subsequent calls reuse the loaded model and run in ~100ms.
 *
 * The isQuery option is accepted for forward compatibility but does not
 * change behavior -- Qwen3 performs better without instruction prefixes.
 *
 * @param text - The text to embed.
 * @param options - Optional settings.
 * @param options.isQuery - Accepted for forward compatibility (no-op).
 * @returns 1024-dimensional normalized embedding as a number array.
 */
export async function generateEmbedding(
  text: string,
  options?: { isQuery?: boolean },
): Promise<number[]> {
  if (!extractor) {
    console.log('Downloading embedding model (one-time setup, ~600MB)...');
    extractor = await pipeline('feature-extraction', MODEL_ID, {
      quantized: true,
    });
    console.log('Embedding model ready.');
  }

  const input = text;
  const output = await extractor(input, { pooling: 'last_token', normalize: true });
  // output.data is a Float32Array; convert to plain number[]
  return Array.from(output.data as Float32Array);
}

/**
 * Get the embedding vector dimensionality.
 *
 * Always returns 1024 (fixed for Qwen3-Embedding-0.6B).
 * This is needed by downstream code (e.g. LSH hasher) to know the vector
 * size without calling the embedding model.
 */
export function getEmbeddingDims(): number {
  return EMBEDDING_DIM;
}
