/**
 * TotalReclaw Plugin for OpenClaw
 *
 * Registers runtime tools so OpenClaw can execute TotalReclaw operations:
 *   - totalreclaw_remember     -- store an encrypted memory
 *   - totalreclaw_recall       -- search and decrypt memories
 *   - totalreclaw_forget       -- soft-delete a memory
 *   - totalreclaw_export       -- export all memories (JSON or Markdown)
 *   - totalreclaw_status       -- check billing/subscription status
 *   - totalreclaw_consolidate  -- scan and merge near-duplicate memories
 *   - totalreclaw_import_from  -- import memories from other tools (Mem0, MCP Memory, etc.)
 *   - totalreclaw_upgrade      -- create Stripe checkout for Pro upgrade
 *   - totalreclaw_migrate      -- migrate testnet memories to mainnet after Pro upgrade
 *
 * Also registers a `before_agent_start` hook that automatically injects
 * relevant memories into the agent's context.
 *
 * All data is encrypted client-side with AES-256-GCM. The server never
 * sees plaintext.
 */

import {
  deriveKeys,
  deriveLshSeed,
  computeAuthKeyHash,
  encrypt,
  decrypt,
  generateBlindIndices,
  generateContentFingerprint,
} from './crypto.js';
import { createApiClient, type StoreFactPayload } from './api-client.js';
import { extractFacts, type ExtractedFact } from './extractor.js';
import { initLLMClient, generateEmbedding, getEmbeddingDims } from './llm-client.js';
import { LSHHasher } from './lsh.js';
import { rerank, cosineSimilarity, detectQueryIntent, INTENT_WEIGHTS, type RerankerCandidate } from './reranker.js';
import { deduplicateBatch } from './semantic-dedup.js';
import {
  findNearDuplicate,
  shouldSupersede,
  clusterFacts,
  getStoreDedupThreshold,
  getConsolidationThreshold,
  STORE_DEDUP_MAX_CANDIDATES,
  type DecryptedCandidate,
} from './consolidation.js';
import { isSubgraphMode, getSubgraphConfig, encodeFactProtobuf, submitFactOnChain, submitFactBatchOnChain, deriveSmartAccountAddress, type FactPayload } from './subgraph-store.js';
import { searchSubgraph, getSubgraphFactCount } from './subgraph-search.js';
import { PluginHotCache, type HotFact } from './hot-cache-wrapper.js';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

// ---------------------------------------------------------------------------
// OpenClaw Plugin API type (defined locally to avoid SDK dependency)
// ---------------------------------------------------------------------------

interface OpenClawPluginApi {
  logger: {
    info(...args: unknown[]): void;
    warn(...args: unknown[]): void;
    error(...args: unknown[]): void;
  };
  config?: {
    agents?: {
      defaults?: {
        model?: {
          primary?: string;
        };
      };
    };
    [key: string]: unknown;
  };
  pluginConfig?: Record<string, unknown>;
  registerTool(tool: unknown, opts?: { name?: string; names?: string[] }): void;
  registerService(service: { id: string; start(): void; stop?(): void }): void;
  on(hookName: string, handler: (...args: unknown[]) => unknown, opts?: { priority?: number }): void;
}

// ---------------------------------------------------------------------------
// Persistent credential storage
// ---------------------------------------------------------------------------

/** Path where we persist userId + salt across restarts. */
const CREDENTIALS_PATH = process.env.TOTALRECLAW_CREDENTIALS_PATH || `${process.env.HOME ?? '/home/node'}/.totalreclaw/credentials.json`;

// ---------------------------------------------------------------------------
// Cosine similarity threshold — skip injection when top result is below this
// ---------------------------------------------------------------------------

/**
 * Minimum cosine similarity of the top reranked result required to inject
 * memories into context. Below this threshold, the query is considered
 * irrelevant to any stored memories and results are suppressed.
 *
 * Default 0.15 is tuned for bge-small-en-v1.5 which produces lower
 * similarity scores than OpenAI models. Configurable via env var.
 */
const COSINE_THRESHOLD = parseFloat(
  process.env.TOTALRECLAW_COSINE_THRESHOLD ?? '0.15',
);

// ---------------------------------------------------------------------------
// Module-level state (persists across tool calls within a session)
// ---------------------------------------------------------------------------

let authKeyHex: string | null = null;
let encryptionKey: Buffer | null = null;
let dedupKey: Buffer | null = null;
let userId: string | null = null;
let subgraphOwner: string | null = null; // Smart Account address for subgraph queries
let apiClient: ReturnType<typeof createApiClient> | null = null;
let initPromise: Promise<void> | null = null;

// LSH hasher — lazily initialized on first use (needs credentials + embedding dims)
let lshHasher: LSHHasher | null = null;
let lshInitFailed = false; // If true, skip LSH on future calls (provider doesn't support embeddings)

// Hot cache for managed service (subgraph mode) — lazily initialized
let pluginHotCache: PluginHotCache | null = null;

// Two-tier search state (C1): skip redundant searches when query is semantically similar
let lastSearchTimestamp = 0;
let lastQueryEmbedding: number[] | null = null;

// Feature flags — configurable for A/B testing
const CACHE_TTL_MS = parseInt(process.env.TOTALRECLAW_CACHE_TTL_MS ?? String(5 * 60 * 1000), 10);
const SEMANTIC_SKIP_THRESHOLD = parseFloat(process.env.TOTALRECLAW_SEMANTIC_SKIP_THRESHOLD ?? '0.85');

// Auto-extract throttle (C3): only extract every N turns in agent_end hook
let turnsSinceLastExtraction = 0;
const AUTO_EXTRACT_EVERY_TURNS_ENV = parseInt(process.env.TOTALRECLAW_EXTRACT_EVERY_TURNS ?? '3', 10);

// Hard cap on facts per extraction to prevent LLM over-extraction from dense conversations
const MAX_FACTS_PER_EXTRACTION = 15;

// Store-time near-duplicate detection (consolidation module)
const STORE_DEDUP_ENABLED = process.env.TOTALRECLAW_STORE_DEDUP !== 'false';

// One-time welcome-back message for returning Pro users (set during init, consumed by first before_agent_start)
let welcomeBackMessage: string | null = null;

// B2: Minimum relevance threshold — cosine below this means no memory injection
const RELEVANCE_THRESHOLD = parseFloat(process.env.TOTALRECLAW_RELEVANCE_THRESHOLD ?? '0.3');

// ---------------------------------------------------------------------------
// Billing cache infrastructure
// ---------------------------------------------------------------------------

const BILLING_CACHE_PATH = path.join(process.env.HOME ?? '/home/node', '.totalreclaw', 'billing-cache.json');
const BILLING_CACHE_TTL = 2 * 60 * 60 * 1000; // 2 hours
const QUOTA_WARNING_THRESHOLD = 0.8; // 80%

interface BillingCache {
  tier: string;
  free_writes_used: number;
  free_writes_limit: number;
  features?: {
    llm_dedup?: boolean;
    custom_extract_interval?: boolean;
    min_extract_interval?: number;
    extraction_interval?: number;
    max_facts_per_extraction?: number;
    max_candidate_pool?: number;
  };
  checked_at: number;
}

function readBillingCache(): BillingCache | null {
  try {
    if (!fs.existsSync(BILLING_CACHE_PATH)) return null;
    const raw = JSON.parse(fs.readFileSync(BILLING_CACHE_PATH, 'utf-8')) as BillingCache;
    if (!raw.checked_at || Date.now() - raw.checked_at > BILLING_CACHE_TTL) return null;
    return raw;
  } catch {
    return null;
  }
}

function writeBillingCache(cache: BillingCache): void {
  try {
    const dir = path.dirname(BILLING_CACHE_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(BILLING_CACHE_PATH, JSON.stringify(cache));
  } catch {
    // Best-effort — don't block on cache write failure.
  }
}

/**
 * Check if LLM-guided dedup is enabled for the current tier.
 * Returns true for Pro users, or when no billing cache exists (fail-open for self-hosters).
 */
function isLlmDedupEnabled(): boolean {
  const cache = readBillingCache();
  if (!cache) return true;
  if (cache.tier === 'pro') return true;
  if (cache.features?.llm_dedup !== undefined) return cache.features.llm_dedup;
  return false;
}

/**
 * Get the effective extraction interval.
 * Server-side config takes priority (from billing cache), then env var fallback.
 * This allows the relay admin to tune extraction without an npm publish.
 */
function getExtractInterval(): number {
  const cache = readBillingCache();
  if (cache?.features?.extraction_interval != null) return cache.features.extraction_interval;
  return AUTO_EXTRACT_EVERY_TURNS_ENV;
}

/**
 * Get the max facts per extraction cycle.
 * Server-side config takes priority (from billing cache), then env var / constant fallback.
 */
function getMaxFactsPerExtraction(): number {
  const cache = readBillingCache();
  if (cache?.features?.max_facts_per_extraction != null) return cache.features.max_facts_per_extraction;
  return MAX_FACTS_PER_EXTRACTION;
}

/**
 * Ensure MEMORY.md has a TotalReclaw header so the agent knows encrypted
 * memories are injected automatically via the before_agent_start hook.
 *
 * Option 3 approach: don't delete or stub MEMORY.md — let the agent use it
 * for workspace-level notes, but make clear that user facts/preferences are
 * handled by TotalReclaw's E2EE pipeline. This avoids confusing the agent
 * (OpenClaw's system prompt still tells it to search MEMORY.md) while
 * guiding it away from writing sensitive data in cleartext.
 */
const MEMORY_HEADER = `# Memory

> **TotalReclaw is active.** Your encrypted memories are loaded automatically
> at the start of each conversation — no need to search this file for them.
> Use \`totalreclaw_remember\` to store new memories and \`totalreclaw_recall\`
> to search. Do NOT write user facts, preferences, or decisions to this file.
> This file is for workspace-level notes only (non-sensitive).

`;

function ensureMemoryHeader(logger: OpenClawPluginApi['logger']): void {
  try {
    const workspace = path.join(process.env.HOME ?? '/home/node', '.openclaw', 'workspace');
    const memoryMd = path.join(workspace, 'MEMORY.md');

    if (fs.existsSync(memoryMd)) {
      const content = fs.readFileSync(memoryMd, 'utf-8');
      if (!content.includes('TotalReclaw is active')) {
        fs.writeFileSync(memoryMd, MEMORY_HEADER + content);
        logger.info('Added TotalReclaw header to MEMORY.md');
      }
    } else {
      // Create MEMORY.md with the header so the agent doesn't get ENOENT
      const dir = path.dirname(memoryMd);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(memoryMd, MEMORY_HEADER);
      logger.info('Created MEMORY.md with TotalReclaw header');
    }
  } catch {
    // Best-effort — don't block the hook
  }
}

// ---------------------------------------------------------------------------
// Dynamic candidate pool sizing
// ---------------------------------------------------------------------------

/** Cached fact count for dynamic candidate pool sizing. */
let cachedFactCount: number | null = null;
/** Timestamp of last fact count fetch (ms). */
let lastFactCountFetch: number = 0;
/** Cache TTL for fact count: 5 minutes. */
const FACT_COUNT_CACHE_TTL = 5 * 60 * 1000;

/**
 * Compute the candidate pool size from a fact count.
 *
 * Server-side config takes priority (from billing cache), then local fallback.
 * The server computes the optimal pool based on vault size and tier caps.
 *
 * Local fallback formula: pool = min(max(factCount * 3, 400), 5000)
 *   - At least 400 candidates (even for tiny vaults)
 *   - At most 5000 candidates (to bound decryption + reranking cost)
 *   - 3x fact count in between
 */
function computeCandidatePool(factCount: number): number {
  const cache = readBillingCache();
  if (cache?.features?.max_candidate_pool != null) return cache.features.max_candidate_pool;
  // Fallback to local formula if no server config
  return Math.min(Math.max(factCount * 3, 400), 5000);
}

/**
 * Fetch the user's fact count from the server, with caching.
 *
 * Uses the /v1/export endpoint with limit=1 to get `total_count` without
 * downloading all facts. Falls back to 400 (which gives pool=1200) if
 * the server is unreachable or returns no count.
 */
async function getFactCount(logger: OpenClawPluginApi['logger']): Promise<number> {
  const now = Date.now();

  // Return cached value if fresh.
  if (cachedFactCount !== null && (now - lastFactCountFetch) < FACT_COUNT_CACHE_TTL) {
    return cachedFactCount;
  }

  try {
    if (!apiClient || !authKeyHex) {
      return cachedFactCount ?? 400; // Not initialized yet, use default
    }

    const page = await apiClient.exportFacts(authKeyHex, 1);
    const count = page.total_count ?? page.facts.length;

    cachedFactCount = count;
    lastFactCountFetch = now;
    logger.info(`Fact count updated: ${count} (candidate pool: ${computeCandidatePool(count)})`);
    return count;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logger.warn(`Failed to fetch fact count (using ${cachedFactCount ?? 400}): ${msg}`);
    return cachedFactCount ?? 400; // Fall back to cached or default
  }
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

/** True when recovery phrase is missing — tools return setup instructions. */
let needsSetup = false;

/**
 * Derive keys from the recovery phrase, load or create credentials, and
 * register with the server if this is the first run.
 */
async function initialize(logger: OpenClawPluginApi['logger']): Promise<void> {
  const serverUrl =
    process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz';
  const masterPassword = process.env.TOTALRECLAW_RECOVERY_PHRASE;

  if (!masterPassword) {
    needsSetup = true;
    logger.info('TOTALRECLAW_RECOVERY_PHRASE not set — setup required (see SKILL.md Post-Install Setup)');
    return;
  }

  apiClient = createApiClient(serverUrl);

  // --- Attempt to load existing credentials ---
  let existingSalt: Buffer | undefined;
  let existingUserId: string | undefined;

  try {
    if (fs.existsSync(CREDENTIALS_PATH)) {
      const creds = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
      existingSalt = Buffer.from(creds.salt, 'base64');
      existingUserId = creds.userId;
      logger.info(`Loaded existing credentials for user ${existingUserId}`);
    }
  } catch (e) {
    logger.warn('Failed to load credentials, will register new account');
  }

  // --- Derive keys ---
  const keys = deriveKeys(masterPassword, existingSalt);
  authKeyHex = keys.authKey.toString('hex');
  encryptionKey = keys.encryptionKey;
  dedupKey = keys.dedupKey;

  // Cache credentials for lazy LSH seed derivation
  masterPasswordCache = masterPassword;
  saltCache = keys.salt;

  if (existingUserId) {
    userId = existingUserId;
    logger.info(`Authenticated as user ${userId}`);
  } else {
    // First run -- register with the server.
    const authHash = computeAuthKeyHash(keys.authKey);
    const saltHex = keys.salt.toString('hex');

    let registeredUserId: string | undefined;
    try {
      const result = await apiClient.register(authHash, saltHex);
      registeredUserId = result.user_id;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes('USER_EXISTS') && isSubgraphMode()) {
        // In managed mode, derive a deterministic userId from the auth key
        // hash. The server is only a relay proxy — userId is used as the
        // subgraph owner field and must be consistent between store/search.
        registeredUserId = authHash.slice(0, 32);
        logger.info(`Using derived userId for managed mode (server returned USER_EXISTS)`);
      } else {
        throw err;
      }
    }

    userId = registeredUserId!;

    // Persist credentials so we can resume later.
    const dir = path.dirname(CREDENTIALS_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(
      CREDENTIALS_PATH,
      JSON.stringify({ userId, salt: keys.salt.toString('base64') }),
    );

    logger.info(`Registered new user: ${userId}`);
  }

  // Derive Smart Account address for subgraph queries (on-chain owner identity).
  if (isSubgraphMode()) {
    try {
      const config = getSubgraphConfig();
      subgraphOwner = await deriveSmartAccountAddress(config.mnemonic, config.chainId);
      logger.info(`Subgraph owner (Smart Account): ${subgraphOwner}`);
    } catch (err) {
      logger.warn(`Failed to derive Smart Account address: ${err instanceof Error ? err.message : String(err)}`);
      // Fall back to userId — won't match subgraph Bytes format, but better than null
      subgraphOwner = userId;
    }
  }

  // One-time billing check for returning users (imported recovery phrase).
  // If they already have an active Pro subscription, inform them on next conversation start.
  if (existingUserId && authKeyHex) {
    try {
      const walletAddr = subgraphOwner || userId || '';
      if (walletAddr) {
        const billingUrl = (process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz').replace(/\/+$/, '');
        const resp = await fetch(`${billingUrl}/v1/billing/status?wallet_address=${encodeURIComponent(walletAddr)}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authKeyHex}`,
            'Accept': 'application/json',
            'X-TotalReclaw-Client': 'openclaw-plugin',
          },
        });
        if (resp.ok) {
          const billingData = await resp.json() as Record<string, unknown>;
          const tier = billingData.tier as string;
          const expiresAt = billingData.expires_at as string | undefined;
          // Populate billing cache for future use.
          writeBillingCache({
            tier: tier || 'free',
            free_writes_used: (billingData.free_writes_used as number) ?? 0,
            free_writes_limit: (billingData.free_writes_limit as number) ?? 0,
            features: billingData.features as BillingCache['features'] | undefined,
            checked_at: Date.now(),
          });
          if (tier === 'pro' && expiresAt) {
            const expiryDate = new Date(expiresAt).toLocaleDateString();
            welcomeBackMessage = `Welcome back! Your Pro subscription is active (expires: ${expiryDate}).`;
            logger.info(`Returning Pro user detected — expires ${expiryDate}`);
          }
        }
      }
    } catch {
      // Best-effort — don't block initialization on billing check failure.
    }
  }
}

function isDocker(): boolean {
  try {
    return fs.existsSync('/.dockerenv') ||
      (fs.existsSync('/proc/1/cgroup') &&
        fs.readFileSync('/proc/1/cgroup', 'utf8').includes('docker'));
  } catch { return false; }
}

function buildSetupErrorMsg(): string {
  const base =
    'TotalReclaw setup required:\n' +
    '1. Set TOTALRECLAW_RECOVERY_PHRASE — ask the user if they have an existing recovery phrase or generate a new 12-word BIP-39 mnemonic.\n' +
    '2. Restart the gateway to apply changes.\n' +
    '   (Optional: set TOTALRECLAW_SELF_HOSTED=true if using your own server instead of the managed service.)\n\n';

  if (isDocker()) {
    return base +
      'Running in Docker — pass env vars via `-e` flags or your compose file:\n' +
      '  -e TOTALRECLAW_RECOVERY_PHRASE="word1 word2 ..."';
  }

  if (process.platform === 'darwin') {
    return base +
      'Running on macOS — add env vars to the LaunchAgent plist at\n' +
      '~/Library/LaunchAgents/ai.openclaw.gateway.plist under <key>EnvironmentVariables</key>:\n' +
      '  <key>TOTALRECLAW_RECOVERY_PHRASE</key><string>word1 word2 ...</string>\n' +
      'Then run: openclaw gateway restart';
  }

  return base +
    'Running on Linux — add env vars to the systemd unit override or your shell profile:\n' +
    '  export TOTALRECLAW_RECOVERY_PHRASE="word1 word2 ..."\n' +
    'Then run: openclaw gateway restart';
}

const SETUP_ERROR_MSG = buildSetupErrorMsg();

/**
 * Ensure `initialize()` has completed (runs at most once).
 */
async function ensureInitialized(logger: OpenClawPluginApi['logger']): Promise<void> {
  if (!initPromise) {
    initPromise = initialize(logger);
  }
  await initPromise;
}

/**
 * Like ensureInitialized, but throws if setup is still needed.
 * Use in tool handlers where we need a fully configured plugin.
 */
async function requireFullSetup(logger: OpenClawPluginApi['logger']): Promise<void> {
  await ensureInitialized(logger);
  if (needsSetup) {
    throw new Error(SETUP_ERROR_MSG);
  }
}

// ---------------------------------------------------------------------------
// LSH + Embedding helpers
// ---------------------------------------------------------------------------

/** Recovery phrase cached for LSH seed derivation (set during initialize()). */
let masterPasswordCache: string | null = null;
/** Salt cached for LSH seed derivation (set during initialize()). */
let saltCache: Buffer | null = null;

/**
 * Get or initialize the LSH hasher.
 *
 * The hasher is created lazily because it needs:
 *   1. The recovery phrase + salt (available after initialize())
 *   2. The embedding dimensions (available after initLLMClient())
 *
 * If the provider doesn't support embeddings, this returns null and
 * sets `lshInitFailed` to avoid retrying.
 */
function getLSHHasher(logger: OpenClawPluginApi['logger']): LSHHasher | null {
  if (lshHasher) return lshHasher;
  if (lshInitFailed) return null;

  try {
    if (!masterPasswordCache || !saltCache) {
      logger.warn('LSH hasher: credentials not available yet');
      return null;
    }

    const dims = getEmbeddingDims();
    const lshSeed = deriveLshSeed(masterPasswordCache, saltCache);
    lshHasher = new LSHHasher(lshSeed, dims);
    logger.info(`LSH hasher initialized (dims=${dims}, tables=${lshHasher.tables}, bits=${lshHasher.bits})`);
    return lshHasher;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logger.warn(`LSH hasher initialization failed (will use word-only indices): ${msg}`);
    lshInitFailed = true;
    return null;
  }
}

/**
 * Generate an embedding for the given text and compute LSH bucket hashes.
 *
 * Returns null if embedding generation fails (provider doesn't support it,
 * network error, etc.). In that case, the caller should fall back to
 * word-only blind indices.
 */
async function generateEmbeddingAndLSH(
  text: string,
  logger: OpenClawPluginApi['logger'],
): Promise<{ embedding: number[]; lshBuckets: string[]; encryptedEmbedding: string } | null> {
  try {
    const embedding = await generateEmbedding(text);

    const hasher = getLSHHasher(logger);
    const lshBuckets = hasher ? hasher.hash(embedding) : [];

    // Encrypt the embedding (JSON array of numbers) for server-blind storage
    const encryptedEmbedding = encryptToHex(JSON.stringify(embedding), encryptionKey!);

    return { embedding, lshBuckets, encryptedEmbedding };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logger.warn(`Embedding/LSH generation failed (falling back to word-only indices): ${msg}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Store-time near-duplicate search helper
// ---------------------------------------------------------------------------

/**
 * Search the vault for near-duplicates of a fact about to be stored.
 *
 * Uses the fact's blind indices as trapdoors to fetch candidates, decrypts
 * them, extracts embeddings, and calls `findNearDuplicate()` from the
 * consolidation module.
 *
 * Returns null on any failure (fail-open: we'd rather store a duplicate than
 * lose a fact).
 */
async function searchForNearDuplicates(
  factText: string,
  factEmbedding: number[],
  allIndices: string[],
  logger: OpenClawPluginApi['logger'],
): Promise<{ match: DecryptedCandidate; similarity: number } | null> {
  try {
    if (!encryptionKey || !authKeyHex || !userId) return null;

    // Fetch candidates from the vault using the fact's blind indices as trapdoors.
    let decryptedCandidates: DecryptedCandidate[] = [];

    if (isSubgraphMode()) {
      const results = await searchSubgraph(
        subgraphOwner || userId,
        allIndices,
        STORE_DEDUP_MAX_CANDIDATES,
        authKeyHex,
      );
      for (const result of results) {
        try {
          const docJson = decryptFromHex(result.encryptedBlob, encryptionKey);
          const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

          let embedding: number[] | null = null;
          if (result.encryptedEmbedding) {
            try {
              embedding = JSON.parse(decryptFromHex(result.encryptedEmbedding, encryptionKey));
            } catch { /* skip */ }
          }

          decryptedCandidates.push({
            id: result.id,
            text: doc.text,
            embedding,
            importance: doc.metadata?.importance
              ? Math.round((doc.metadata.importance as number) * 10)
              : 5,
            decayScore: 5,
            createdAt: result.timestamp ? parseInt(result.timestamp, 10) * 1000 : Date.now(),
            version: 1,
          });
        } catch { /* skip undecryptable */ }
      }
    } else if (apiClient) {
      const candidates = await apiClient.search(
        userId,
        allIndices,
        STORE_DEDUP_MAX_CANDIDATES,
        authKeyHex,
      );
      for (const candidate of candidates) {
        try {
          const docJson = decryptFromHex(candidate.encrypted_blob, encryptionKey);
          const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

          let embedding: number[] | null = null;
          if (candidate.encrypted_embedding) {
            try {
              embedding = JSON.parse(decryptFromHex(candidate.encrypted_embedding, encryptionKey));
            } catch { /* skip */ }
          }

          decryptedCandidates.push({
            id: candidate.fact_id,
            text: doc.text,
            embedding,
            importance: doc.metadata?.importance
              ? Math.round((doc.metadata.importance as number) * 10)
              : 5,
            decayScore: candidate.decay_score,
            createdAt: typeof candidate.timestamp === 'number'
              ? candidate.timestamp
              : new Date(candidate.timestamp).getTime(),
            version: candidate.version,
          });
        } catch { /* skip undecryptable */ }
      }
    }

    if (decryptedCandidates.length === 0) return null;

    const result = findNearDuplicate(factEmbedding, decryptedCandidates, getStoreDedupThreshold());
    if (!result) return null;

    return { match: result.existingFact, similarity: result.similarity };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logger.warn(`Store-time dedup search failed (proceeding with store): ${msg}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

/**
 * Encrypt a plaintext document string and return its hex-encoded ciphertext.
 *
 * The server stores blobs as hex (not base64), so we convert the base64
 * output of `encrypt()` into hex.
 */
function encryptToHex(plaintext: string, key: Buffer): string {
  const b64 = encrypt(plaintext, key);
  return Buffer.from(b64, 'base64').toString('hex');
}

/**
 * Decrypt a hex-encoded ciphertext blob into a UTF-8 string.
 */
function decryptFromHex(hexBlob: string, key: Buffer): string {
  const hex = hexBlob.startsWith('0x') ? hexBlob.slice(2) : hexBlob;
  const b64 = Buffer.from(hex, 'hex').toString('base64');
  return decrypt(b64, key);
}

// ---------------------------------------------------------------------------
// Migration GraphQL helpers
// ---------------------------------------------------------------------------

interface MigrationFact {
  id: string;
  owner: string;
  encryptedBlob: string;
  encryptedEmbedding: string | null;
  decayScore: string;
  isActive: boolean;
  contentFp: string;
  source: string;
  agentId: string;
  version: number;
  timestamp: string;
}

const MIGRATION_PAGE_SIZE = 1000;

/** Execute a GraphQL query against a subgraph endpoint. Returns null on error. */
async function migrationGqlQuery<T>(
  endpoint: string,
  query: string,
  variables: Record<string, unknown>,
  authKey?: string,
): Promise<T | null> {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-TotalReclaw-Client': 'openclaw-plugin',
    };
    if (authKey) headers['Authorization'] = `Bearer ${authKey}`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({ query, variables }),
    });
    if (!response.ok) return null;
    const json = await response.json() as { data?: T; errors?: unknown[] };
    return json.data ?? null;
  } catch {
    return null;
  }
}

/** Fetch all active facts by owner from a subgraph, paginated. */
async function fetchAllFactsByOwner(
  subgraphUrl: string,
  owner: string,
  authKey: string,
): Promise<MigrationFact[]> {
  const allFacts: MigrationFact[] = [];
  let lastId = '';

  while (true) {
    const hasLastId = lastId !== '';
    const query = hasLastId
      ? `query($owner:Bytes!,$first:Int!,$lastId:String!){facts(where:{owner:$owner,isActive:true,id_gt:$lastId},first:$first,orderBy:id,orderDirection:asc){id owner encryptedBlob encryptedEmbedding decayScore isActive contentFp source agentId version timestamp}}`
      : `query($owner:Bytes!,$first:Int!){facts(where:{owner:$owner,isActive:true},first:$first,orderBy:id,orderDirection:asc){id owner encryptedBlob encryptedEmbedding decayScore isActive contentFp source agentId version timestamp}}`;
    const vars: Record<string, unknown> = hasLastId
      ? { owner, first: MIGRATION_PAGE_SIZE, lastId }
      : { owner, first: MIGRATION_PAGE_SIZE };

    const data = await migrationGqlQuery<{ facts?: MigrationFact[] }>(subgraphUrl, query, vars, authKey);
    const facts = data?.facts ?? [];
    if (facts.length === 0) break;
    allFacts.push(...facts);
    if (facts.length < MIGRATION_PAGE_SIZE) break;
    lastId = facts[facts.length - 1].id;
  }

  return allFacts;
}

/** Fetch content fingerprints from a subgraph for idempotency. */
async function fetchContentFingerprintsByOwner(
  subgraphUrl: string,
  owner: string,
  authKey: string,
): Promise<Set<string>> {
  const fps = new Set<string>();
  let lastId = '';

  while (true) {
    const hasLastId = lastId !== '';
    const query = hasLastId
      ? `query($owner:Bytes!,$first:Int!,$lastId:String!){facts(where:{owner:$owner,isActive:true,id_gt:$lastId},first:$first,orderBy:id,orderDirection:asc){id contentFp}}`
      : `query($owner:Bytes!,$first:Int!){facts(where:{owner:$owner,isActive:true},first:$first,orderBy:id,orderDirection:asc){id contentFp}}`;
    const vars: Record<string, unknown> = hasLastId
      ? { owner, first: MIGRATION_PAGE_SIZE, lastId }
      : { owner, first: MIGRATION_PAGE_SIZE };

    const data = await migrationGqlQuery<{ facts?: Array<{ id: string; contentFp: string }> }>(subgraphUrl, query, vars, authKey);
    const facts = data?.facts ?? [];
    if (facts.length === 0) break;
    for (const f of facts) {
      if (f.contentFp) fps.add(f.contentFp);
    }
    if (facts.length < MIGRATION_PAGE_SIZE) break;
    lastId = facts[facts.length - 1].id;
  }

  return fps;
}

/** Fetch blind index hashes for given fact IDs. */
async function fetchBlindIndicesByFactIds(
  subgraphUrl: string,
  factIds: string[],
  authKey: string,
): Promise<Map<string, string[]>> {
  const result = new Map<string, string[]>();
  const CHUNK = 50;

  for (let i = 0; i < factIds.length; i += CHUNK) {
    const chunk = factIds.slice(i, i + CHUNK);
    const query = `query($factIds:[String!]!,$first:Int!){blindIndexes(where:{fact_in:$factIds},first:$first){hash fact{id}}}`;
    const data = await migrationGqlQuery<{
      blindIndexes?: Array<{ hash: string; fact: { id: string } }>;
    }>(subgraphUrl, query, { factIds: chunk, first: 1000 }, authKey);

    for (const entry of data?.blindIndexes ?? []) {
      const existing = result.get(entry.fact.id) || [];
      existing.push(entry.hash);
      result.set(entry.fact.id, existing);
    }
  }

  return result;
}

/**
 * Fetch existing memories from the vault to provide dedup context for extraction.
 * Returns a lightweight list of {id, text} pairs for the LLM prompt.
 * Fails silently — returns empty array on any error.
 */
async function fetchExistingMemoriesForExtraction(
  logger: { warn: (msg: string) => void },
  limit: number = 30,
  rawMessages: unknown[] = [],
): Promise<Array<{ id: string; text: string }>> {
  try {
    if (!encryptionKey || !authKeyHex || !userId) return [];

    // Extract key terms from the last few messages to generate meaningful trapdoors.
    // Using '*' would produce zero trapdoors (stripped as punctuation), so we pull
    // text from the conversation to find memories relevant to the current context.
    const recentMessages = rawMessages.slice(-4);
    const textChunks: string[] = [];
    for (const msg of recentMessages) {
      const m = msg as { content?: string | Array<{ text?: string }>; text?: string };
      if (typeof m.content === 'string') {
        textChunks.push(m.content);
      } else if (Array.isArray(m.content)) {
        for (const block of m.content) {
          if (block.text) textChunks.push(block.text);
        }
      } else if (typeof m.text === 'string') {
        textChunks.push(m.text);
      }
    }
    const queryText = textChunks.join(' ').slice(0, 500); // cap to avoid giant trapdoor sets
    if (!queryText.trim()) return [];

    const trapdoors = generateBlindIndices(queryText);
    if (trapdoors.length === 0) return [];

    const results: Array<{ id: string; text: string }> = [];

    if (isSubgraphMode()) {
      const rawResults = await searchSubgraph(
        subgraphOwner || userId,
        trapdoors,
        limit,
        authKeyHex,
      );
      for (const r of rawResults) {
        try {
          const docJson = decryptFromHex(r.encryptedBlob, encryptionKey);
          const doc = JSON.parse(docJson) as { text: string };
          results.push({ id: r.id, text: doc.text });
        } catch { /* skip undecryptable */ }
      }
    } else if (apiClient) {
      const candidates = await apiClient.search(userId, trapdoors, limit, authKeyHex);
      for (const c of candidates) {
        try {
          const docJson = decryptFromHex(c.encrypted_blob, encryptionKey);
          const doc = JSON.parse(docJson) as { text: string };
          results.push({ id: c.fact_id, text: doc.text });
        } catch { /* skip undecryptable */ }
      }
    }

    return results;
  } catch (err) {
    logger.warn(`Failed to fetch existing memories for extraction context: ${err instanceof Error ? err.message : String(err)}`);
    return [];
  }
}

/**
 * Simple text-overlap scoring between a query and a candidate document.
 * Returns the number of overlapping lowercase words.
 */
function textScore(query: string, docText: string): number {
  const queryWords = new Set(
    query.toLowerCase().split(/\s+/).filter((w) => w.length >= 2),
  );
  const docWords = docText.toLowerCase().split(/\s+/);
  let score = 0;
  for (const word of docWords) {
    if (queryWords.has(word)) score++;
  }
  return score;
}

/**
 * Format a relative time string (e.g. "2 hours ago").
 */
function relativeTime(isoOrMs: string | number): string {
  const ms = typeof isoOrMs === 'number' ? isoOrMs : new Date(isoOrMs).getTime();
  const diffMs = Date.now() - ms;
  const seconds = Math.floor(diffMs / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ---------------------------------------------------------------------------
// Importance filter for auto-extraction
// ---------------------------------------------------------------------------

/**
 * Minimum importance score (1-10) for auto-extracted facts to be stored.
 * Facts below this threshold are silently dropped to save storage and gas.
 * Configurable via TOTALRECLAW_MIN_IMPORTANCE env var (default: 3).
 *
 * NOTE: This filter is ONLY applied to auto-extraction (hooks).
 * The explicit `totalreclaw_remember` tool always stores regardless of importance.
 */
const MIN_IMPORTANCE_THRESHOLD = Math.max(
  1,
  Math.min(10, Number(process.env.TOTALRECLAW_MIN_IMPORTANCE) || 3),
);

/**
 * Filter extracted facts by importance threshold.
 * Facts with importance < MIN_IMPORTANCE_THRESHOLD are dropped.
 * Facts with missing/undefined importance are treated as importance=5 (kept).
 */
function filterByImportance(
  facts: ExtractedFact[],
  logger: OpenClawPluginApi['logger'],
): { kept: ExtractedFact[]; dropped: number } {
  const kept: ExtractedFact[] = [];
  let dropped = 0;

  for (const fact of facts) {
    const importance = fact.importance ?? 5;
    if (importance >= MIN_IMPORTANCE_THRESHOLD) {
      kept.push(fact);
    } else {
      dropped++;
    }
  }

  if (dropped > 0) {
    logger.info(
      `Importance filter: dropped ${dropped}/${facts.length} facts below threshold ${MIN_IMPORTANCE_THRESHOLD}`,
    );
  }

  return { kept, dropped };
}

// ---------------------------------------------------------------------------
// Auto-extraction helper
// ---------------------------------------------------------------------------

/**
 * Store extracted facts in the TotalReclaw server.
 * Encrypts each fact, generates blind indices and fingerprint, stores via API.
 * Silently skips duplicates.
 *
 * Before storing, performs semantic near-duplicate detection within the batch:
 * facts whose embeddings have cosine similarity >= threshold (default 0.9)
 * against an already-accepted fact in the same batch are skipped.
 */
async function storeExtractedFacts(
  facts: ExtractedFact[],
  logger: OpenClawPluginApi['logger'],
): Promise<number> {
  if (!encryptionKey || !dedupKey || !authKeyHex || !userId || !apiClient) return 0;

  // Phase 1: Generate embeddings for all facts (needed for dedup + storage).
  const embeddingMap = new Map<string, number[]>();
  const embeddingResultMap = new Map<
    string,
    { embedding: number[]; lshBuckets: string[]; encryptedEmbedding: string }
  >();

  for (const fact of facts) {
    try {
      const result = await generateEmbeddingAndLSH(fact.text, logger);
      if (result) {
        embeddingMap.set(fact.text, result.embedding);
        embeddingResultMap.set(fact.text, result);
      }
    } catch {
      // Embedding generation failed for this fact -- proceed without it.
    }
  }

  // Phase 2: Semantic batch dedup.
  const dedupedFacts = deduplicateBatch(facts, embeddingMap, logger);

  if (dedupedFacts.length < facts.length) {
    logger.info(
      `Semantic dedup: ${facts.length - dedupedFacts.length} near-duplicate(s) removed from batch of ${facts.length}`,
    );
  }

  // Phase 3: Store the deduplicated facts (with optional store-time dedup).
  // In subgraph mode, collect all protobuf payloads (tombstones + new facts)
  // and submit them in a single batched UserOp for gas efficiency.
  let stored = 0;
  let superseded = 0;
  let skipped = 0;
  const pendingPayloads: Buffer[] = []; // Batched subgraph payloads
  let preparedForSubgraph = 0;

  for (const fact of dedupedFacts) {
    try {
      const blindIndices = generateBlindIndices(fact.text);

      // Use pre-computed embedding result if available.
      const embeddingResult = embeddingResultMap.get(fact.text) ?? null;
      const allIndices = embeddingResult
        ? [...blindIndices, ...embeddingResult.lshBuckets]
        : blindIndices;

      // LLM-guided dedup: handle UPDATE/DELETE/NOOP actions.
      if (fact.action === 'NOOP') {
        logger.info(`LLM dedup: NOOP — skipping "${fact.text.slice(0, 60)}…"`);
        skipped++;
        continue;
      }

      if (fact.action === 'DELETE' && fact.existingFactId) {
        // Tombstone the old fact, don't store anything new.
        if (isSubgraphMode()) {
          const tombstone: FactPayload = {
            id: fact.existingFactId,
            timestamp: new Date().toISOString(),
            owner: subgraphOwner || userId!,
            encryptedBlob: '00',
            blindIndices: [],
            decayScore: 0,
            source: 'tombstone',
            contentFp: '',
            agentId: 'openclaw-plugin-auto',
          };
          pendingPayloads.push(encodeFactProtobuf(tombstone));
          logger.info(`LLM dedup: DELETE — queued tombstone for ${fact.existingFactId}`);
        } else if (apiClient && authKeyHex) {
          try {
            await apiClient.deleteFact(fact.existingFactId, authKeyHex);
            logger.info(`LLM dedup: DELETE — removed ${fact.existingFactId}`);
          } catch (delErr) {
            logger.warn(`LLM dedup: DELETE failed for ${fact.existingFactId}: ${delErr instanceof Error ? delErr.message : String(delErr)}`);
          }
        }
        superseded++;
        continue;
      }

      if (fact.action === 'UPDATE' && fact.existingFactId) {
        // Tombstone the old fact, then fall through to store the new version.
        if (isSubgraphMode()) {
          const tombstone: FactPayload = {
            id: fact.existingFactId,
            timestamp: new Date().toISOString(),
            owner: subgraphOwner || userId!,
            encryptedBlob: '00',
            blindIndices: [],
            decayScore: 0,
            source: 'tombstone',
            contentFp: '',
            agentId: 'openclaw-plugin-auto',
          };
          pendingPayloads.push(encodeFactProtobuf(tombstone));
          logger.info(`LLM dedup: UPDATE — queued tombstone for ${fact.existingFactId}, storing replacement`);
        } else if (apiClient && authKeyHex) {
          try {
            await apiClient.deleteFact(fact.existingFactId, authKeyHex);
            logger.info(`LLM dedup: UPDATE — deleted ${fact.existingFactId}, storing replacement`);
          } catch (delErr) {
            logger.warn(`LLM dedup: UPDATE delete failed for ${fact.existingFactId}: ${delErr instanceof Error ? delErr.message : String(delErr)}`);
          }
        }
        superseded++;
        // Fall through to store the new replacement fact below.
      }

      // ADD (default) or UPDATE (after tombstoning old) — proceed to store.
      // The cosine-based store-time dedup below provides an additional safety net.

      // Store-time near-duplicate check: search vault before writing.
      let effectiveImportance = fact.importance;

      if (STORE_DEDUP_ENABLED && embeddingResult) {
        const dupResult = await searchForNearDuplicates(
          fact.text,
          embeddingResult.embedding,
          allIndices,
          logger,
        );

        if (dupResult) {
          const action = shouldSupersede(fact.importance, dupResult.match);
          if (action === 'skip') {
            logger.info(
              `Store-time dedup: skipping "${fact.text.slice(0, 60)}…" (sim=${dupResult.similarity.toFixed(3)}, existing ID=${dupResult.match.id})`,
            );
            skipped++;
            continue;
          }
          // action === 'supersede': delete old fact, inherit higher importance
          if (isSubgraphMode()) {
            const tombstone: FactPayload = {
              id: dupResult.match.id,
              timestamp: new Date().toISOString(),
              owner: subgraphOwner || userId!,
              encryptedBlob: '00',
              blindIndices: [],
              decayScore: 0,
              source: 'tombstone',
              contentFp: '',
              agentId: 'openclaw-plugin-auto',
            };
            pendingPayloads.push(encodeFactProtobuf(tombstone));
            logger.info(
              `Store-time dedup: queued supersede for ${dupResult.match.id} (sim=${dupResult.similarity.toFixed(3)})`,
            );
          } else if (apiClient && authKeyHex) {
            try {
              await apiClient.deleteFact(dupResult.match.id, authKeyHex);
              logger.info(
                `Store-time dedup: superseding ${dupResult.match.id} (sim=${dupResult.similarity.toFixed(3)})`,
              );
            } catch (delErr) {
              logger.warn(
                `Store-time dedup: failed to delete superseded fact ${dupResult.match.id}: ${delErr instanceof Error ? delErr.message : String(delErr)}`,
              );
            }
          }
          effectiveImportance = Math.max(fact.importance, dupResult.match.decayScore);
          superseded++;
        }
      }

      const doc = {
        text: fact.text,
        metadata: {
          type: fact.type,
          importance: effectiveImportance / 10,
          source: 'auto-extraction',
          created_at: new Date().toISOString(),
        },
      };

      const encryptedBlob = encryptToHex(JSON.stringify(doc), encryptionKey);

      const contentFp = generateContentFingerprint(fact.text, dedupKey);
      const factId = crypto.randomUUID();

      if (isSubgraphMode()) {
        const protobuf = encodeFactProtobuf({
          id: factId,
          timestamp: new Date().toISOString(),
          owner: subgraphOwner || userId!,
          encryptedBlob: encryptedBlob,
          blindIndices: allIndices,
          decayScore: effectiveImportance,
          source: 'auto-extraction',
          contentFp: contentFp,
          agentId: 'openclaw-plugin-auto',
          encryptedEmbedding: embeddingResult?.encryptedEmbedding,
        });
        pendingPayloads.push(protobuf);
        preparedForSubgraph++;
      } else {
        const payload: StoreFactPayload = {
          id: factId,
          timestamp: new Date().toISOString(),
          encrypted_blob: encryptedBlob,
          blind_indices: allIndices,
          decay_score: effectiveImportance,
          source: 'auto-extraction',
          content_fp: contentFp,
          agent_id: 'openclaw-plugin-auto',
          encrypted_embedding: embeddingResult?.encryptedEmbedding,
        };
        await apiClient.store(userId, [payload], authKeyHex);
        stored++;
      }
    } catch (err: unknown) {
      // Check for 403 / quota exceeded — invalidate billing cache so next
      // before_agent_start re-fetches and warns the user.
      const errMsg = err instanceof Error ? err.message : String(err);
      if (errMsg.includes('403') || errMsg.toLowerCase().includes('quota')) {
        try { fs.unlinkSync(BILLING_CACHE_PATH); } catch { /* ignore */ }
        logger.warn(`Quota exceeded — billing cache invalidated. ${errMsg}`);
        break; // Stop trying to store remaining facts — they'll all fail too
      }
      // Otherwise skip failed facts (e.g., duplicates return success with duplicate_ids)
    }
  }

  // Batch-submit all subgraph payloads in a single UserOp (gas-efficient).
  if (pendingPayloads.length > 0 && isSubgraphMode()) {
    try {
      const batchConfig = { ...getSubgraphConfig(), authKeyHex: authKeyHex!, walletAddress: subgraphOwner ?? undefined };
      const result = await submitFactBatchOnChain(pendingPayloads, batchConfig);
      if (result.success) {
        stored += preparedForSubgraph;
        logger.info(`Batch submitted ${result.batchSize} payloads in 1 UserOp (tx=${result.txHash.slice(0, 10)}…)`);
      } else {
        logger.warn(`Batch UserOp failed on-chain (tx=${result.txHash.slice(0, 10)}…)`);
      }
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err);
      if (errMsg.includes('403') || errMsg.toLowerCase().includes('quota')) {
        try { fs.unlinkSync(BILLING_CACHE_PATH); } catch { /* ignore */ }
        logger.warn(`Quota exceeded during batch submit — billing cache invalidated. ${errMsg}`);
      } else {
        logger.warn(`Batch submission failed: ${errMsg}`);
      }
    }
  }

  if (stored > 0 || superseded > 0 || skipped > 0) {
    logger.info(`Auto-extraction results: stored=${stored}, superseded=${superseded}, skipped=${skipped}`);
  }

  return stored;
}

// ---------------------------------------------------------------------------
// Import handler (for totalreclaw_import_from tool)
// ---------------------------------------------------------------------------

/**
 * Handle import_from tool calls in the plugin context.
 *
 * Uses the shared adapters to parse, then stores via storeExtractedFacts().
 */
async function handlePluginImportFrom(
  params: Record<string, unknown>,
  logger: OpenClawPluginApi['logger'],
): Promise<Record<string, unknown>> {
  const startTime = Date.now();

  const source = params.source as string;
  const validSources = ['mem0', 'mcp-memory', 'memoclaw', 'generic-json', 'generic-csv'];

  if (!source || !validSources.includes(source)) {
    return { success: false, error: `Invalid source. Must be one of: ${validSources.join(', ')}` };
  }

  try {
    const { getAdapter } = await import('./import-adapters/index.js');
    const adapter = getAdapter(source as import('./import-adapters/types.js').ImportSource);

    const parseResult = await adapter.parse({
      content: params.content as string | undefined,
      api_key: params.api_key as string | undefined,
      source_user_id: params.source_user_id as string | undefined,
      api_url: params.api_url as string | undefined,
      file_path: params.file_path as string | undefined,
    });

    if (parseResult.errors.length > 0 && parseResult.facts.length === 0) {
      return {
        success: false,
        error: `Failed to parse ${adapter.displayName} data`,
        details: parseResult.errors,
      };
    }

    if (params.dry_run) {
      return {
        success: true,
        dry_run: true,
        source,
        total_found: parseResult.facts.length,
        preview: parseResult.facts.slice(0, 10).map((f) => ({
          type: f.type,
          text: f.text.slice(0, 100),
          importance: f.importance,
        })),
        warnings: parseResult.warnings,
      };
    }

    // Convert NormalizedFact[] to ExtractedFact[] for storeExtractedFacts()
    const extractedFacts: ExtractedFact[] = parseResult.facts.map((f) => ({
      text: f.text,
      type: f.type,
      importance: f.importance,
      action: 'ADD' as const,
    }));

    // Store in batches of 50
    let totalStored = 0;
    const batchSize = 50;

    for (let i = 0; i < extractedFacts.length; i += batchSize) {
      const batch = extractedFacts.slice(i, i + batchSize);
      const stored = await storeExtractedFacts(batch, logger);
      totalStored += stored;

      logger.info(
        `Import progress: ${Math.min(i + batchSize, extractedFacts.length)}/${extractedFacts.length} processed, ${totalStored} stored`,
      );
    }

    return {
      success: true,
      source,
      import_id: crypto.randomUUID(),
      total_found: parseResult.facts.length,
      imported: totalStored,
      skipped: parseResult.facts.length - totalStored,
      warnings: parseResult.warnings,
      duration_ms: Date.now() - startTime,
    };
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Unknown error';
    logger.error(`Import failed: ${msg}`);
    return { success: false, error: `Import failed: ${msg}` };
  }
}

// ---------------------------------------------------------------------------
// Plugin definition
// ---------------------------------------------------------------------------

const plugin = {
  id: 'totalreclaw',
  name: 'TotalReclaw',
  description: 'End-to-end encrypted memory vault for AI agents',
  kind: 'memory' as const,
  configSchema: {
    type: 'object',
    additionalProperties: false,
    properties: {
      extraction: {
        type: 'object',
        properties: {
          model: { type: 'string', description: "Override the extraction model (e.g., 'glm-4.5-flash', 'gpt-4.1-mini')" },
          enabled: { type: 'boolean', description: 'Enable/disable auto-extraction (default: true)' },
        },
        additionalProperties: false,
      },
    },
  },

  register(api: OpenClawPluginApi) {
    // ---------------------------------------------------------------
    // LLM client initialization (auto-detect provider from OpenClaw config)
    // ---------------------------------------------------------------

    initLLMClient({
      primaryModel: api.config?.agents?.defaults?.model?.primary as string | undefined,
      pluginConfig: api.pluginConfig,
      logger: api.logger,
    });

    // ---------------------------------------------------------------
    // Service registration (lifecycle logging)
    // ---------------------------------------------------------------

    api.registerService({
      id: 'totalreclaw',
      start: () => {
        api.logger.info('TotalReclaw plugin loaded');
      },
      stop: () => {
        api.logger.info('TotalReclaw plugin stopped');
      },
    });

    // ---------------------------------------------------------------
    // Tool: totalreclaw_remember
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_remember',
        label: 'Remember',
        description:
          'Store a memory in the encrypted vault. Use this when the user shares important information worth remembering.',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'The memory text to store',
            },
            type: {
              type: 'string',
              enum: ['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'],
              description: 'The kind of memory (default: fact)',
            },
            importance: {
              type: 'number',
              minimum: 1,
              maximum: 10,
              description: 'Importance score 1-10 (default: 5)',
            },
          },
          required: ['text'],
          additionalProperties: false,
        },
        async execute(_toolCallId: string, params: { text: string; type?: string; importance?: number }) {
          try {
            await requireFullSetup(api.logger);

            const memoryType = params.type ?? 'fact';
            let importance = params.importance ?? 5;

            // Generate blind indices for server-side search.
            const blindIndices = generateBlindIndices(params.text);

            // Generate embedding + LSH bucket hashes (PoC v2).
            // Falls back to word-only indices if embedding generation fails.
            const embeddingResult = await generateEmbeddingAndLSH(params.text, api.logger);

            // Merge LSH bucket hashes into blind indices.
            const allIndices = embeddingResult
              ? [...blindIndices, ...embeddingResult.lshBuckets]
              : blindIndices;

            // Store-time dedup: for explicit remember, ALWAYS supersede
            // (user explicitly wants this stored — just remove the old one).
            let supersededId: string | undefined;
            if (STORE_DEDUP_ENABLED && embeddingResult) {
              const dupResult = await searchForNearDuplicates(
                params.text,
                embeddingResult.embedding,
                allIndices,
                api.logger,
              );
              if (dupResult) {
                // Inherit higher importance from existing fact.
                importance = Math.max(importance, dupResult.match.decayScore);
                supersededId = dupResult.match.id;

                if (isSubgraphMode()) {
                  try {
                    const tombConfig = { ...getSubgraphConfig(), authKeyHex: authKeyHex!, walletAddress: subgraphOwner ?? undefined };
                    const tombstone: FactPayload = {
                      id: dupResult.match.id,
                      timestamp: new Date().toISOString(),
                      owner: subgraphOwner || userId!,
                      encryptedBlob: '00',
                      blindIndices: [],
                      decayScore: 0,
                      source: 'tombstone',
                      contentFp: '',
                      agentId: 'openclaw-plugin',
                    };
                    const tombProtobuf = encodeFactProtobuf(tombstone);
                    await submitFactOnChain(tombProtobuf, tombConfig);
                    api.logger.info(
                      `Remember dedup: superseded ${dupResult.match.id} on-chain (sim=${dupResult.similarity.toFixed(3)})`,
                    );
                  } catch (tombErr) {
                    api.logger.warn(
                      `Remember dedup: failed to tombstone ${dupResult.match.id}: ${tombErr instanceof Error ? tombErr.message : String(tombErr)}`,
                    );
                    supersededId = undefined;
                  }
                } else if (apiClient && authKeyHex) {
                  try {
                    await apiClient.deleteFact(dupResult.match.id, authKeyHex);
                    api.logger.info(
                      `Remember dedup: superseded ${dupResult.match.id} (sim=${dupResult.similarity.toFixed(3)})`,
                    );
                  } catch (delErr) {
                    api.logger.warn(
                      `Remember dedup: failed to delete superseded fact ${dupResult.match.id}: ${delErr instanceof Error ? delErr.message : String(delErr)}`,
                    );
                    supersededId = undefined; // Don't report supersession if delete failed
                  }
                }
              }
            }

            // Build the document JSON that will be encrypted.
            const doc = {
              text: params.text,
              metadata: {
                type: memoryType,
                importance: importance / 10, // normalise to 0-1 range
                source: 'explicit',
                created_at: new Date().toISOString(),
              },
            };

            // Encrypt the document.
            const encryptedBlob = encryptToHex(JSON.stringify(doc), encryptionKey!);

            // Generate content fingerprint for dedup.
            const contentFp = generateContentFingerprint(params.text, dedupKey!);

            // Generate a unique fact ID.
            const factId = crypto.randomUUID();

            // Build the payload matching the server's FactJSON schema.
            const factPayload: StoreFactPayload = {
              id: factId,
              timestamp: new Date().toISOString(),
              encrypted_blob: encryptedBlob,
              blind_indices: allIndices,
              decay_score: importance,
              source: 'explicit',
              content_fp: contentFp,
              agent_id: 'openclaw-plugin',
              encrypted_embedding: embeddingResult?.encryptedEmbedding,
            };

            if (isSubgraphMode()) {
              // Subgraph mode: encode as Protobuf and submit on-chain via relay UserOp
              const config = { ...getSubgraphConfig(), authKeyHex: authKeyHex!, walletAddress: subgraphOwner ?? undefined };
              const protobuf = encodeFactProtobuf({
                id: factId,
                timestamp: new Date().toISOString(),
                owner: subgraphOwner || userId!,
                encryptedBlob: encryptedBlob,
                blindIndices: allIndices,
                decayScore: importance,
                source: 'explicit',
                contentFp: contentFp,
                agentId: 'openclaw-plugin',
                encryptedEmbedding: embeddingResult?.encryptedEmbedding,
              });
              await submitFactOnChain(protobuf, config);
            } else {
              await apiClient!.store(userId!, [factPayload], authKeyHex!);
            }

            const statusMsg = supersededId
              ? `Memory stored (ID: ${factId}). Superseded an older similar memory.`
              : `Memory stored (ID: ${factId})`;

            return {
              content: [{ type: 'text', text: statusMsg }],
              details: { factId, supersededId },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_remember failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to store memory: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_remember' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_recall
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_recall',
        label: 'Recall',
        description:
          'Search the encrypted memory vault. Returns the most relevant memories matching the query.',
        parameters: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query text',
            },
            k: {
              type: 'number',
              minimum: 1,
              maximum: 20,
              description: 'Number of results to return (default: 8)',
            },
          },
          required: ['query'],
          additionalProperties: false,
        },
        async execute(_toolCallId: string, params: { query: string; k?: number }) {
          try {
            await requireFullSetup(api.logger);

            const k = Math.min(params.k ?? 8, 20);

            // 1. Generate word trapdoors (blind indices for the query).
            const wordTrapdoors = generateBlindIndices(params.query);

            // 2. Generate query embedding + LSH trapdoors (may fail gracefully).
            let queryEmbedding: number[] | null = null;
            let lshTrapdoors: string[] = [];
            try {
              queryEmbedding = await generateEmbedding(params.query, { isQuery: true });
              const hasher = getLSHHasher(api.logger);
              if (hasher && queryEmbedding) {
                lshTrapdoors = hasher.hash(queryEmbedding);
              }
            } catch (err) {
              const msg = err instanceof Error ? err.message : String(err);
              api.logger.warn(`Recall: embedding/LSH generation failed (using word-only trapdoors): ${msg}`);
            }

            // 3. Merge word trapdoors + LSH trapdoors.
            const allTrapdoors = [...wordTrapdoors, ...lshTrapdoors];

            if (allTrapdoors.length === 0) {
              return {
                content: [{ type: 'text', text: 'No searchable terms in query.' }],
                details: { count: 0, memories: [] },
              };
            }

            // 4. Request more candidates than needed so we can re-rank client-side.
            // 5. Decrypt candidates (text + embeddings) and build reranker input.
            const rerankerCandidates: RerankerCandidate[] = [];
            const metaMap = new Map<string, { metadata: Record<string, unknown>; timestamp: number }>();

            if (isSubgraphMode()) {
              // --- Subgraph search path ---
              const factCount = await getSubgraphFactCount(subgraphOwner || userId!, authKeyHex!);
              const pool = computeCandidatePool(factCount);
              const subgraphResults = await searchSubgraph(subgraphOwner || userId!, allTrapdoors, pool, authKeyHex!);

              for (const result of subgraphResults) {
                try {
                  const docJson = decryptFromHex(result.encryptedBlob, encryptionKey!);
                  const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

                  let decryptedEmbedding: number[] | undefined;
                  if (result.encryptedEmbedding) {
                    try {
                      decryptedEmbedding = JSON.parse(
                        decryptFromHex(result.encryptedEmbedding, encryptionKey!),
                      );
                    } catch {
                      // Embedding decryption failed -- proceed without it.
                    }
                  }

                  rerankerCandidates.push({
                    id: result.id,
                    text: doc.text,
                    embedding: decryptedEmbedding,
                    importance: (doc.metadata?.importance as number) ?? 0.5,
                    createdAt: result.timestamp ? parseInt(result.timestamp, 10) : undefined,
                  });

                  metaMap.set(result.id, {
                    metadata: doc.metadata ?? {},
                    timestamp: Date.now(), // Subgraph doesn't return ms timestamp; use current
                  });
                } catch {
                  // Skip candidates we cannot decrypt.
                }
              }

              // Update hot cache with top results for instant auto-recall.
              try {
                if (!pluginHotCache && encryptionKey) {
                  const config = getSubgraphConfig();
                  pluginHotCache = new PluginHotCache(config.cachePath, encryptionKey.toString('hex'));
                  pluginHotCache.load();
                }
                if (pluginHotCache) {
                  const hotFacts: HotFact[] = rerankerCandidates.map((c) => {
                    const meta = metaMap.get(c.id);
                    const importance = meta?.metadata.importance
                      ? Math.round((meta.metadata.importance as number) * 10)
                      : 5;
                    return { id: c.id, text: c.text, importance };
                  });
                  pluginHotCache.setHotFacts(hotFacts);
                  pluginHotCache.setFactCount(rerankerCandidates.length);
                  pluginHotCache.flush();
                }
              } catch {
                // Hot cache update is best-effort -- don't fail the recall.
              }
            } else {
              // --- Server search path (existing behavior) ---
              const factCount = await getFactCount(api.logger);
              const pool = computeCandidatePool(factCount);
              const candidates = await apiClient!.search(
                userId!,
                allTrapdoors,
                pool,
                authKeyHex!,
              );

              for (const candidate of candidates) {
                try {
                  const docJson = decryptFromHex(candidate.encrypted_blob, encryptionKey!);
                  const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

                  let decryptedEmbedding: number[] | undefined;
                  if (candidate.encrypted_embedding) {
                    try {
                      decryptedEmbedding = JSON.parse(
                        decryptFromHex(candidate.encrypted_embedding, encryptionKey!),
                      );
                    } catch {
                      // Embedding decryption failed -- proceed without it.
                    }
                  }

                  rerankerCandidates.push({
                    id: candidate.fact_id,
                    text: doc.text,
                    embedding: decryptedEmbedding,
                    importance: (doc.metadata?.importance as number) ?? 0.5,
                    createdAt: typeof candidate.timestamp === 'number'
                      ? candidate.timestamp / 1000
                      : new Date(candidate.timestamp).getTime() / 1000,
                  });

                  metaMap.set(candidate.fact_id, {
                    metadata: doc.metadata ?? {},
                    timestamp: candidate.timestamp,
                  });
                } catch {
                  // Skip candidates we cannot decrypt (e.g. corrupted data).
                }
              }
            }

            // 6. Re-rank with BM25 + cosine + intent-weighted RRF fusion.
            const queryIntent = detectQueryIntent(params.query);
            const reranked = rerank(
              params.query,
              queryEmbedding ?? [],
              rerankerCandidates,
              k,
              INTENT_WEIGHTS[queryIntent],
            );

            if (reranked.length === 0) {
              return {
                content: [{ type: 'text', text: 'No memories found matching your query.' }],
                details: { count: 0, memories: [] },
              };
            }

            // 6b. Cosine similarity threshold gate — skip results when the
            //     best match is below the minimum relevance threshold.
            const maxCosine = Math.max(
              ...reranked.map((r) => r.cosineSimilarity ?? 0),
            );
            if (maxCosine < COSINE_THRESHOLD) {
              api.logger.info(
                `Recall: cosine threshold gate filtered results (max=${maxCosine.toFixed(3)}, threshold=${COSINE_THRESHOLD})`,
              );
              return {
                content: [{ type: 'text', text: 'No relevant memories found for this query.' }],
                details: { count: 0, memories: [] },
              };
            }

            // 7. Format results.
            const lines = reranked.map((m, i) => {
              const meta = metaMap.get(m.id);
              const imp = meta?.metadata.importance
                ? ` (importance: ${Math.round((meta.metadata.importance as number) * 10)}/10)`
                : '';
              const age = meta ? relativeTime(meta.timestamp) : '';
              return `${i + 1}. ${m.text}${imp} -- ${age} [ID: ${m.id}]`;
            });

            const formatted = lines.join('\n');

            return {
              content: [{ type: 'text', text: formatted }],
              details: {
                count: reranked.length,
                memories: reranked.map((m) => ({
                  factId: m.id,
                  text: m.text,
                })),
              },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_recall failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to search memories: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_recall' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_forget
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_forget',
        label: 'Forget',
        description: 'Delete a specific memory by its ID.',
        parameters: {
          type: 'object',
          properties: {
            factId: {
              type: 'string',
              description: 'The UUID of the memory to delete',
            },
          },
          required: ['factId'],
          additionalProperties: false,
        },
        async execute(_toolCallId: string, params: { factId: string }) {
          try {
            await requireFullSetup(api.logger);

            if (isSubgraphMode()) {
              // On-chain tombstone: write a minimal protobuf with decayScore=0
              // The subgraph will overwrite the fact and set isActive=false
              const config = { ...getSubgraphConfig(), authKeyHex: authKeyHex!, walletAddress: subgraphOwner ?? undefined };
              const tombstone: FactPayload = {
                id: params.factId,
                timestamp: new Date().toISOString(),
                owner: subgraphOwner || userId!,
                encryptedBlob: '00', // minimal 1-byte placeholder
                blindIndices: [],
                decayScore: 0,
                source: 'tombstone',
                contentFp: '',
                agentId: 'openclaw-plugin',
              };
              const protobuf = encodeFactProtobuf(tombstone);
              const result = await submitFactOnChain(protobuf, config);
              api.logger.info(`Tombstone written for ${params.factId}: tx=${result.txHash}`);
              return {
                content: [{ type: 'text', text: `Memory ${params.factId} deleted (on-chain tombstone, tx: ${result.txHash})` }],
                details: { deleted: true, txHash: result.txHash },
              };
            } else {
              await apiClient!.deleteFact(params.factId, authKeyHex!);
              return {
                content: [{ type: 'text', text: `Memory ${params.factId} deleted` }],
                details: { deleted: true },
              };
            }
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_forget failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to delete memory: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_forget' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_export
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_export',
        label: 'Export',
        description:
          'Export all stored memories. Decrypts every memory and returns them as JSON or Markdown.',
        parameters: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['json', 'markdown'],
              description: 'Output format (default: json)',
            },
          },
          additionalProperties: false,
        },
        async execute(_toolCallId: string, params: { format?: string }) {
          try {
            await requireFullSetup(api.logger);

            const format = params.format ?? 'json';

            // Paginate through all facts.
            const allFacts: Array<{
              id: string;
              text: string;
              metadata: Record<string, unknown>;
              created_at: string;
            }> = [];

            if (isSubgraphMode()) {
              // Query subgraph for all active facts
              const config = getSubgraphConfig();
              const relayUrl = config.relayUrl;
              const PAGE_SIZE = 1000;
              let skip = 0;
              let hasMore = true;
              const owner = subgraphOwner || userId || '';

              while (hasMore) {
                const query = `{ facts(where: { owner: "${owner}", isActive: true }, first: ${PAGE_SIZE}, skip: ${skip}, orderBy: sequenceId, orderDirection: asc) { id encryptedBlob source agentId timestamp sequenceId } }`;

                const res = await fetch(`${relayUrl}/v1/subgraph`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'X-TotalReclaw-Client': 'openclaw-plugin',
                    ...(authKeyHex ? { Authorization: `Bearer ${authKeyHex}` } : {}),
                  },
                  body: JSON.stringify({ query }),
                });

                const json = (await res.json()) as {
                  data?: { facts?: Array<{ id: string; encryptedBlob: string; source: string; agentId: string; timestamp: string; sequenceId: string }> };
                };
                const facts = json?.data?.facts || [];

                for (const fact of facts) {
                  try {
                    let hexBlob = fact.encryptedBlob;
                    if (hexBlob.startsWith('0x')) hexBlob = hexBlob.slice(2);
                    const docJson = decryptFromHex(hexBlob, encryptionKey!);
                    const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };
                    allFacts.push({
                      id: fact.id,
                      text: doc.text,
                      metadata: doc.metadata ?? {},
                      created_at: new Date(parseInt(fact.timestamp) * 1000).toISOString(),
                    });
                  } catch {
                    // Skip facts we cannot decrypt
                  }
                }

                skip += PAGE_SIZE;
                hasMore = facts.length === PAGE_SIZE;
              }
            } else {
              // HTTP server mode — paginate through PostgreSQL facts
              let cursor: string | undefined;
              let hasMore = true;

              while (hasMore) {
                const page = await apiClient!.exportFacts(authKeyHex!, 1000, cursor);

                for (const fact of page.facts) {
                  try {
                    const docJson = decryptFromHex(fact.encrypted_blob, encryptionKey!);
                    const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };
                    allFacts.push({
                      id: fact.id,
                      text: doc.text,
                      metadata: doc.metadata ?? {},
                      created_at: fact.created_at,
                    });
                  } catch {
                    // Skip facts we cannot decrypt.
                  }
                }

                cursor = page.cursor ?? undefined;
                hasMore = page.has_more;
              }
            }

            // Format output.
            let formatted: string;

            if (format === 'markdown') {
              if (allFacts.length === 0) {
                formatted = '*No memories stored.*';
              } else {
                const lines = allFacts.map((f, i) => {
                  const meta = f.metadata;
                  const type = (meta.type as string) ?? 'fact';
                  const imp = meta.importance
                    ? ` (importance: ${Math.round((meta.importance as number) * 10)}/10)`
                    : '';
                  return `${i + 1}. **[${type}]** ${f.text}${imp}  \n   _ID: ${f.id} | Created: ${f.created_at}_`;
                });
                formatted = `# Exported Memories (${allFacts.length})\n\n${lines.join('\n')}`;
              }
            } else {
              formatted = JSON.stringify(allFacts, null, 2);
            }

            return {
              content: [{ type: 'text', text: formatted }],
              details: { count: allFacts.length },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_export failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to export memories: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_export' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_status
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_status',
        label: 'Status',
        description:
          'Check TotalReclaw billing and subscription status — tier, writes used, reset date.',
        parameters: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
        async execute() {
          try {
            await requireFullSetup(api.logger);

            if (!authKeyHex) {
              return {
                content: [{ type: 'text', text: 'Auth credentials are not available. Please initialize first.' }],
              };
            }

            const serverUrl = (process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz').replace(/\/+$/, '');
            const walletAddr = subgraphOwner || userId || '';
            const response = await fetch(`${serverUrl}/v1/billing/status?wallet_address=${encodeURIComponent(walletAddr)}`, {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${authKeyHex}`,
                'Accept': 'application/json',
                'X-TotalReclaw-Client': 'openclaw-plugin',
              },
            });

            if (!response.ok) {
              const body = await response.text().catch(() => '');
              return {
                content: [{ type: 'text', text: `Failed to fetch billing status (HTTP ${response.status}): ${body || response.statusText}` }],
              };
            }

            const data = await response.json() as Record<string, unknown>;
            const tier = (data.tier as string) || 'free';
            const freeWritesUsed = (data.free_writes_used as number) ?? 0;
            const freeWritesLimit = (data.free_writes_limit as number) ?? 0;
            const freeWritesResetAt = data.free_writes_reset_at as string | undefined;

            // Update billing cache on success.
            writeBillingCache({
              tier,
              free_writes_used: freeWritesUsed,
              free_writes_limit: freeWritesLimit,
              features: data.features as BillingCache['features'] | undefined,
              checked_at: Date.now(),
            });

            const tierLabel = tier === 'pro' ? 'Pro' : 'Free';
            const lines: string[] = [
              `Tier: ${tierLabel}`,
              `Writes: ${freeWritesUsed}/${freeWritesLimit} used this month`,
            ];
            if (freeWritesResetAt) {
              lines.push(`Resets: ${new Date(freeWritesResetAt).toLocaleDateString()}`);
            }
            if (tier !== 'pro') {
              lines.push(`Pricing: https://totalreclaw.xyz/pricing`);
            }

            return {
              content: [{ type: 'text', text: lines.join('\n') }],
              details: { tier, free_writes_used: freeWritesUsed, free_writes_limit: freeWritesLimit },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_status failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to check status: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_status' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_consolidate
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_consolidate',
        label: 'Consolidate',
        description:
          'Scan all stored memories and merge near-duplicates. Keeps the most important/recent version and removes redundant copies.',
        parameters: {
          type: 'object',
          properties: {
            dry_run: {
              type: 'boolean',
              description: 'Preview consolidation without deleting (default: false)',
            },
          },
          additionalProperties: false,
        },
        async execute(_toolCallId: string, params: { dry_run?: boolean }) {
          try {
            await requireFullSetup(api.logger);

            const dryRun = params.dry_run ?? false;

            // Consolidation is only available in centralized (HTTP server) mode.
            if (isSubgraphMode()) {
              return {
                content: [{ type: 'text', text: 'Consolidation is currently only available in centralized mode.' }],
              };
            }

            if (!apiClient || !authKeyHex || !encryptionKey) {
              return {
                content: [{ type: 'text', text: 'Plugin not fully initialized. Cannot consolidate.' }],
              };
            }

            // 1. Export all facts (paginated, max 10 pages of 1000).
            const allDecrypted: DecryptedCandidate[] = [];
            let cursor: string | undefined;
            let hasMore = true;
            let pageCount = 0;
            const MAX_PAGES = 10;

            while (hasMore && pageCount < MAX_PAGES) {
              const page = await apiClient.exportFacts(authKeyHex, 1000, cursor);

              for (const fact of page.facts) {
                try {
                  const docJson = decryptFromHex(fact.encrypted_blob, encryptionKey);
                  const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

                  let embedding: number[] | null = null;
                  // ExportedFact does not include encrypted_embedding — generate it on-the-fly.
                  // For consolidation we need embeddings, so generate them.
                  try {
                    embedding = await generateEmbedding(doc.text);
                  } catch { /* skip — fact will not be clustered */ }

                  allDecrypted.push({
                    id: fact.id,
                    text: doc.text,
                    embedding,
                    importance: doc.metadata?.importance
                      ? Math.round((doc.metadata.importance as number) * 10)
                      : 5,
                    decayScore: fact.decay_score,
                    createdAt: new Date(fact.created_at).getTime(),
                    version: fact.version,
                  });
                } catch {
                  // Skip undecryptable facts.
                }
              }

              cursor = page.cursor ?? undefined;
              hasMore = page.has_more;
              pageCount++;
            }

            if (allDecrypted.length === 0) {
              return {
                content: [{ type: 'text', text: 'No memories found to consolidate.' }],
              };
            }

            // 2. Cluster by cosine similarity.
            const clusters = clusterFacts(allDecrypted, getConsolidationThreshold());

            if (clusters.length === 0) {
              return {
                content: [{ type: 'text', text: `Scanned ${allDecrypted.length} memories — no near-duplicates found.` }],
              };
            }

            // 3. Build report.
            const totalDuplicates = clusters.reduce((sum, c) => sum + c.duplicates.length, 0);
            const reportLines: string[] = [
              `Scanned ${allDecrypted.length} memories.`,
              `Found ${clusters.length} cluster(s) with ${totalDuplicates} duplicate(s).`,
              '',
            ];

            const displayClusters = clusters.slice(0, 10);
            for (let i = 0; i < displayClusters.length; i++) {
              const cluster = displayClusters[i];
              reportLines.push(`Cluster ${i + 1}: KEEP "${cluster.representative.text.slice(0, 80)}…"`);
              for (const dup of cluster.duplicates) {
                reportLines.push(`  - REMOVE "${dup.text.slice(0, 80)}…" (ID: ${dup.id})`);
              }
            }
            if (clusters.length > 10) {
              reportLines.push(`... and ${clusters.length - 10} more cluster(s).`);
            }

            // 4. If not dry_run, batch-delete duplicates.
            if (!dryRun) {
              const idsToDelete = clusters.flatMap((c) => c.duplicates.map((d) => d.id));
              const BATCH_SIZE = 500;
              let totalDeleted = 0;

              for (let i = 0; i < idsToDelete.length; i += BATCH_SIZE) {
                const batch = idsToDelete.slice(i, i + BATCH_SIZE);
                const deleted = await apiClient.batchDelete(batch, authKeyHex);
                totalDeleted += deleted;
              }

              reportLines.push('');
              reportLines.push(`Deleted ${totalDeleted} duplicate memories.`);
            } else {
              reportLines.push('');
              reportLines.push('DRY RUN — no memories were deleted. Run without dry_run to apply.');
            }

            return {
              content: [{ type: 'text', text: reportLines.join('\n') }],
              details: {
                scanned: allDecrypted.length,
                clusters: clusters.length,
                duplicates: totalDuplicates,
                dry_run: dryRun,
              },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_consolidate failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to consolidate memories: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_consolidate' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_import_from
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_import_from',
        label: 'Import From',
        description:
          'Import memories from other AI memory tools (Mem0, MCP Memory Server, MemoClaw, or generic JSON/CSV). ' +
          'Provide the source name and either an API key or file content. ' +
          'Use dry_run=true to preview before importing. Idempotent — safe to run multiple times.',
        parameters: {
          type: 'object',
          properties: {
            source: {
              type: 'string',
              enum: ['mem0', 'mcp-memory', 'memoclaw', 'generic-json', 'generic-csv'],
              description: 'The source system to import from',
            },
            api_key: {
              type: 'string',
              description: 'API key for the source system (used once, never stored)',
            },
            source_user_id: {
              type: 'string',
              description: 'User or agent ID in the source system',
            },
            content: {
              type: 'string',
              description: 'File content (JSON, JSONL, or CSV)',
            },
            file_path: {
              type: 'string',
              description: 'Path to the file on disk',
            },
            namespace: {
              type: 'string',
              description: 'Target namespace (default: "imported")',
            },
            dry_run: {
              type: 'boolean',
              description: 'Preview without importing',
            },
          },
          required: ['source'],
        },
        async execute(_toolCallId: string, params: Record<string, unknown>) {
          try {
            await requireFullSetup(api.logger);
            return handlePluginImportFrom(params, api.logger);
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            return { error: message };
          }
        },
      },
      { name: 'totalreclaw_import_from' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_upgrade
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_upgrade',
        label: 'Upgrade to Pro',
        description:
          'Upgrade to TotalReclaw Pro for unlimited encrypted memories. ' +
          'Returns a Stripe checkout URL for the user to complete payment via credit/debit card.',
        parameters: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
        async execute() {
          try {
            await requireFullSetup(api.logger);

            if (!authKeyHex) {
              return {
                content: [{ type: 'text', text: 'Auth credentials are not available. Please initialize first.' }],
              };
            }

            const serverUrl = (process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz').replace(/\/+$/, '');
            const walletAddr = subgraphOwner || userId || '';

            if (!walletAddr) {
              return {
                content: [{ type: 'text', text: 'Wallet address not available. Please ensure the plugin is fully initialized.' }],
              };
            }

            const response = await fetch(`${serverUrl}/v1/billing/checkout`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authKeyHex}`,
                'Content-Type': 'application/json',
                'X-TotalReclaw-Client': 'openclaw-plugin',
              },
              body: JSON.stringify({
                wallet_address: walletAddr,
                tier: 'pro',
              }),
            });

            if (!response.ok) {
              const body = await response.text().catch(() => '');
              return {
                content: [{ type: 'text', text: `Failed to create checkout session (HTTP ${response.status}): ${body || response.statusText}` }],
              };
            }

            const data = await response.json() as { checkout_url?: string };

            if (!data.checkout_url) {
              return {
                content: [{ type: 'text', text: 'Failed to create checkout session: no checkout URL returned.' }],
              };
            }

            return {
              content: [{ type: 'text', text: `Open this URL to upgrade to Pro: ${data.checkout_url}` }],
              details: { checkout_url: data.checkout_url },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_upgrade failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Failed to create checkout session: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_upgrade' },
    );

    // ---------------------------------------------------------------
    // Tool: totalreclaw_migrate
    // ---------------------------------------------------------------

    api.registerTool(
      {
        name: 'totalreclaw_migrate',
        label: 'Migrate Testnet to Mainnet',
        description:
          'Migrate memories from testnet (Base Sepolia) to mainnet (Gnosis) after upgrading to Pro. ' +
          'Dry-run by default — set confirm=true to execute. Idempotent: re-running skips already-migrated facts.',
        parameters: {
          type: 'object',
          properties: {
            confirm: {
              type: 'boolean',
              description: 'Set to true to execute the migration. Without it, returns a dry-run preview.',
              default: false,
            },
          },
          additionalProperties: false,
        },
        async execute(_params: { confirm?: boolean }) {
          try {
            await requireFullSetup(api.logger);

            if (!authKeyHex || !subgraphOwner) {
              return {
                content: [{ type: 'text', text: 'Plugin not fully initialized. Ensure TOTALRECLAW_RECOVERY_PHRASE is set.' }],
              };
            }

            if (!isSubgraphMode()) {
              return {
                content: [{ type: 'text', text: 'Migration is only available with the managed service (subgraph mode).' }],
              };
            }

            const confirm = _params?.confirm === true;
            const serverUrl = (process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz').replace(/\/+$/, '');

            // 1. Check billing tier
            const billingResp = await fetch(
              `${serverUrl}/v1/billing/status?wallet_address=${encodeURIComponent(subgraphOwner)}`,
              {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${authKeyHex}`,
                  'Content-Type': 'application/json',
                  'X-TotalReclaw-Client': 'openclaw-plugin',
                },
              },
            );
            if (!billingResp.ok) {
              return { content: [{ type: 'text', text: `Failed to check billing tier (HTTP ${billingResp.status}).` }] };
            }
            const billingData = await billingResp.json() as { tier: string };
            if (billingData.tier !== 'pro') {
              return {
                content: [{ type: 'text', text: 'Migration requires Pro tier. Use totalreclaw_upgrade to upgrade first.' }],
              };
            }

            // 2. Fetch testnet facts via relay (chain=testnet query param)
            const testnetSubgraphUrl = `${serverUrl}/v1/subgraph?chain=testnet`;
            const mainnetSubgraphUrl = `${serverUrl}/v1/subgraph`;

            api.logger.info('Fetching testnet facts...');
            const testnetFacts = await fetchAllFactsByOwner(testnetSubgraphUrl, subgraphOwner, authKeyHex);

            if (testnetFacts.length === 0) {
              return {
                content: [{ type: 'text', text: 'No facts found on testnet. Nothing to migrate.' }],
              };
            }

            // 3. Check mainnet for existing facts (idempotency)
            api.logger.info('Checking mainnet for existing facts...');
            const mainnetFps = await fetchContentFingerprintsByOwner(mainnetSubgraphUrl, subgraphOwner, authKeyHex);
            const factsToMigrate = testnetFacts.filter(f => !f.contentFp || !mainnetFps.has(f.contentFp));
            const alreadyOnMainnet = testnetFacts.length - factsToMigrate.length;

            // 4. Dry-run
            if (!confirm) {
              const msg = factsToMigrate.length === 0
                ? `All ${testnetFacts.length} testnet facts already exist on mainnet. Nothing to migrate.`
                : `Found ${factsToMigrate.length} facts to migrate from testnet to Gnosis mainnet (${alreadyOnMainnet} already on mainnet). Call with confirm=true to proceed.`;
              return {
                content: [{ type: 'text', text: msg }],
                details: {
                  mode: 'dry_run',
                  testnet_facts: testnetFacts.length,
                  already_on_mainnet: alreadyOnMainnet,
                  to_migrate: factsToMigrate.length,
                },
              };
            }

            // 5. Execute migration
            if (factsToMigrate.length === 0) {
              return {
                content: [{ type: 'text', text: `All ${testnetFacts.length} testnet facts already exist on mainnet. Nothing to migrate.` }],
              };
            }

            // Fetch blind indices
            api.logger.info(`Fetching blind indices for ${factsToMigrate.length} facts...`);
            const factIds = factsToMigrate.map(f => f.id);
            const blindIndicesMap = await fetchBlindIndicesByFactIds(testnetSubgraphUrl, factIds, authKeyHex);

            // Build protobuf payloads
            const payloads: Buffer[] = [];
            for (const fact of factsToMigrate) {
              const blobHex = fact.encryptedBlob.startsWith('0x') ? fact.encryptedBlob.slice(2) : fact.encryptedBlob;
              const indices = blindIndicesMap.get(fact.id) || [];
              const factPayload: FactPayload = {
                id: fact.id,
                timestamp: new Date().toISOString(),
                owner: subgraphOwner,
                encryptedBlob: blobHex,
                blindIndices: indices,
                decayScore: parseFloat(fact.decayScore) || 0.5,
                source: fact.source || 'migration',
                contentFp: fact.contentFp || '',
                agentId: fact.agentId || 'openclaw-plugin',
                encryptedEmbedding: fact.encryptedEmbedding || undefined,
              };
              payloads.push(encodeFactProtobuf(factPayload));
            }

            // Batch submit (15 per UserOp)
            const BATCH_SIZE = 15;
            const batchConfig = { ...getSubgraphConfig(), authKeyHex: authKeyHex!, walletAddress: subgraphOwner ?? undefined };
            let migrated = 0;
            let failedBatches = 0;

            for (let i = 0; i < payloads.length; i += BATCH_SIZE) {
              const batch = payloads.slice(i, i + BATCH_SIZE);
              const batchNum = Math.floor(i / BATCH_SIZE) + 1;
              const totalBatches = Math.ceil(payloads.length / BATCH_SIZE);
              api.logger.info(`Migrating batch ${batchNum}/${totalBatches} (${batch.length} facts)...`);

              try {
                const result = await submitFactBatchOnChain(batch, batchConfig);
                if (result.success) {
                  migrated += batch.length;
                } else {
                  failedBatches++;
                }
              } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : String(err);
                api.logger.error(`Migration batch ${batchNum} failed: ${msg}`);
                failedBatches++;
              }
            }

            const resultMsg = failedBatches === 0
              ? `Successfully migrated ${migrated} memories from testnet to Gnosis mainnet.`
              : `Migrated ${migrated}/${factsToMigrate.length} memories. ${failedBatches} batch(es) failed — re-run to retry (idempotent).`;

            return {
              content: [{ type: 'text', text: resultMsg }],
              details: {
                mode: 'executed',
                testnet_facts: testnetFacts.length,
                already_on_mainnet: alreadyOnMainnet,
                to_migrate: factsToMigrate.length,
                migrated,
                failed_batches: failedBatches,
              },
            };
          } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            api.logger.error(`totalreclaw_migrate failed: ${message}`);
            return {
              content: [{ type: 'text', text: `Migration failed: ${message}` }],
            };
          }
        },
      },
      { name: 'totalreclaw_migrate' },
    );

    // ---------------------------------------------------------------
    // Hook: before_agent_start
    // ---------------------------------------------------------------

    api.on(
      'before_agent_start',
      async (event: unknown) => {
        try {
          // Prevent cleartext leakage from OpenClaw's native memory system.
          ensureMemoryHeader(api.logger);

          const evt = event as { prompt?: string } | undefined;

          // Skip trivial or missing prompts.
          if (!evt?.prompt || evt.prompt.length < 5) {
            return undefined;
          }

          await ensureInitialized(api.logger);

          // If setup is still needed after init, inject setup instructions
          if (needsSetup) {
            return {
              prependContext:
                '## TotalReclaw Setup Required\n\n' +
                'TotalReclaw is installed but needs configuration. Follow the "Post-Install Setup" steps in SKILL.md to complete setup.\n' +
                'Ask the user: "Do you have an existing TotalReclaw recovery phrase, or should I generate a new one?"',
            };
          }

          // One-time welcome-back message for returning Pro users.
          let welcomeBack = '';
          if (welcomeBackMessage) {
            welcomeBack = `\n\n${welcomeBackMessage}`;
            welcomeBackMessage = null; // Consume — only show once
          }

          // Billing cache check — warn if quota is approaching limit.
          let billingWarning = '';
          try {
            let cache = readBillingCache();
            if (!cache && authKeyHex) {
              // Cache is stale or missing — fetch fresh billing status.
              const billingUrl = (process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz').replace(/\/+$/, '');
              const walletParam = encodeURIComponent(subgraphOwner || userId || '');
              const billingResp = await fetch(`${billingUrl}/v1/billing/status?wallet_address=${walletParam}`, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${authKeyHex}`, 'Accept': 'application/json', 'X-TotalReclaw-Client': 'openclaw-plugin' },
              });
              if (billingResp.ok) {
                const billingData = await billingResp.json() as Record<string, unknown>;
                cache = {
                  tier: (billingData.tier as string) || 'free',
                  free_writes_used: (billingData.free_writes_used as number) ?? 0,
                  free_writes_limit: (billingData.free_writes_limit as number) ?? 0,
                  features: billingData.features as BillingCache['features'] | undefined,
                  checked_at: Date.now(),
                };
                writeBillingCache(cache);
              }
            }
            if (cache && cache.free_writes_limit > 0) {
              const usageRatio = cache.free_writes_used / cache.free_writes_limit;
              if (usageRatio >= QUOTA_WARNING_THRESHOLD) {
                billingWarning = `\n\nTotalReclaw quota warning: ${cache.free_writes_used}/${cache.free_writes_limit} writes used this month (${Math.round(usageRatio * 100)}%). Visit https://totalreclaw.xyz/pricing to upgrade.`;
              }
            }
          } catch {
            // Best-effort — don't block on billing check failure.
          }

          if (isSubgraphMode()) {
            // --- Subgraph mode: hot cache first, then background refresh ---

            // Initialize hot cache if needed.
            if (!pluginHotCache && encryptionKey) {
              const config = getSubgraphConfig();
              pluginHotCache = new PluginHotCache(config.cachePath, encryptionKey.toString('hex'));
              pluginHotCache.load();
            }

            // Try to return cached facts instantly.
            const cachedFacts = pluginHotCache?.getHotFacts() ?? [];

            // Query subgraph in parallel for fresh results.
            // 1. Generate word trapdoors from the user prompt.
            const wordTrapdoors = generateBlindIndices(evt.prompt);

            // 2. Generate query embedding + LSH trapdoors (may fail gracefully).
            let queryEmbedding: number[] | null = null;
            let lshTrapdoors: string[] = [];
            try {
              queryEmbedding = await generateEmbedding(evt.prompt, { isQuery: true });
              const hasher = getLSHHasher(api.logger);
              if (hasher && queryEmbedding) {
                lshTrapdoors = hasher.hash(queryEmbedding);
              }
            } catch {
              // Embedding/LSH failed -- proceed with word-only trapdoors.
            }

            // Two-tier search (C1): if cache is fresh AND query is semantically similar, return cached
            const now = Date.now();
            const cacheAge = now - lastSearchTimestamp;
            if (cacheAge < CACHE_TTL_MS && cachedFacts.length > 0 && queryEmbedding && lastQueryEmbedding) {
              const querySimilarity = cosineSimilarity(queryEmbedding, lastQueryEmbedding);
              if (querySimilarity > SEMANTIC_SKIP_THRESHOLD) {
                const lines = cachedFacts.slice(0, 8).map((f, i) =>
                  `${i + 1}. ${f.text} (importance: ${f.importance}/10, cached)`,
                );
                return { prependContext: `## Relevant Memories\n\n${lines.join('\n')}` + welcomeBack + billingWarning };
              }
            }

            // 3. Merge trapdoors — always include word trapdoors for small-dataset coverage.
            // LSH alone has low collision probability on <100 facts, causing 0 matches.
            const allTrapdoors = [...wordTrapdoors, ...lshTrapdoors];

            // If we have cached facts and no trapdoors, return cached facts.
            if (allTrapdoors.length === 0 && cachedFacts.length > 0) {
              const lines = cachedFacts.slice(0, 8).map((f, i) =>
                `${i + 1}. ${f.text} (importance: ${f.importance}/10, cached)`,
              );
              return { prependContext: `## Relevant Memories\n\n${lines.join('\n')}` + welcomeBack + billingWarning };
            }

            if (allTrapdoors.length === 0) return undefined;

            // 4. Query subgraph for fresh results.
            let subgraphResults: Awaited<ReturnType<typeof searchSubgraph>> = [];
            try {
              const factCount = await getSubgraphFactCount(subgraphOwner || userId!, authKeyHex!);
              const pool = computeCandidatePool(factCount);
              subgraphResults = await searchSubgraph(subgraphOwner || userId!, allTrapdoors, pool, authKeyHex!);
            } catch {
              // Subgraph query failed -- fall back to cached facts if available.
              if (cachedFacts.length > 0) {
                const lines = cachedFacts.slice(0, 8).map((f, i) =>
                  `${i + 1}. ${f.text} (importance: ${f.importance}/10, cached)`,
                );
                return { prependContext: `## Relevant Memories\n\n${lines.join('\n')}` + welcomeBack + billingWarning };
              }
              return undefined;
            }

            if (subgraphResults.length === 0 && cachedFacts.length === 0) return undefined;

            // If subgraph returned no results but we have cache, use cache.
            if (subgraphResults.length === 0) {
              const lines = cachedFacts.slice(0, 8).map((f, i) =>
                `${i + 1}. ${f.text} (importance: ${f.importance}/10, cached)`,
              );
              return { prependContext: `## Relevant Memories\n\n${lines.join('\n')}` + welcomeBack + billingWarning };
            }

            // 5. Decrypt subgraph results and build reranker input.
            const rerankerCandidates: RerankerCandidate[] = [];
            const hookMetaMap = new Map<string, { importance: number; age: string }>();

            for (const result of subgraphResults) {
              try {
                const docJson = decryptFromHex(result.encryptedBlob, encryptionKey!);
                const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

                let decryptedEmbedding: number[] | undefined;
                if (result.encryptedEmbedding) {
                  try {
                    decryptedEmbedding = JSON.parse(
                      decryptFromHex(result.encryptedEmbedding, encryptionKey!),
                    );
                  } catch {
                    // Embedding decryption failed -- proceed without it.
                  }
                }

                const importanceRaw = (doc.metadata?.importance as number) ?? 0.5;
                const createdAtSec = result.timestamp ? parseInt(result.timestamp, 10) : undefined;
                rerankerCandidates.push({
                  id: result.id,
                  text: doc.text,
                  embedding: decryptedEmbedding,
                  importance: importanceRaw,
                  createdAt: createdAtSec,
                });

                const importance = doc.metadata?.importance
                  ? Math.round((doc.metadata.importance as number) * 10)
                  : 5;
                hookMetaMap.set(result.id, {
                  importance,
                  age: 'subgraph',
                });
              } catch {
                // Skip un-decryptable candidates.
              }
            }

            // 6. Re-rank with BM25 + cosine + intent-weighted RRF fusion.
            const hookQueryIntent = detectQueryIntent(evt.prompt);
            const reranked = rerank(
              evt.prompt,
              queryEmbedding ?? [],
              rerankerCandidates,
              8,
              INTENT_WEIGHTS[hookQueryIntent],
            );

            // B2: Minimum relevance threshold — skip noise injection for irrelevant turns.
            const candidatesWithEmb = rerankerCandidates.filter(c => c.embedding && c.embedding.length > 0);
            if (candidatesWithEmb.length > 0 && queryEmbedding && queryEmbedding.length > 0) {
              const topCosine = Math.max(
                ...candidatesWithEmb.map(c => cosineSimilarity(queryEmbedding!, c.embedding!))
              );
              if (topCosine < RELEVANCE_THRESHOLD) return undefined;
            }

            // Update hot cache with reranked results.
            try {
              if (pluginHotCache) {
                const hotFacts: HotFact[] = rerankerCandidates.map((c) => {
                  const meta = hookMetaMap.get(c.id);
                  return { id: c.id, text: c.text, importance: meta?.importance ?? 5 };
                });
                pluginHotCache.setHotFacts(hotFacts);
                pluginHotCache.setLastQueryEmbedding(queryEmbedding);
                pluginHotCache.flush();
              }
            } catch {
              // Hot cache update is best-effort.
            }

            // Record search state for two-tier cache (C1).
            lastSearchTimestamp = Date.now();
            lastQueryEmbedding = queryEmbedding;

            if (reranked.length === 0) return undefined;

            // 6b. Cosine similarity threshold gate — skip injection when the
            //     best match is below the minimum relevance threshold.
            const hookMaxCosine = Math.max(
              ...reranked.map((r) => r.cosineSimilarity ?? 0),
            );
            if (hookMaxCosine < COSINE_THRESHOLD) {
              api.logger.info(
                `Hook: cosine threshold gate filtered results (max=${hookMaxCosine.toFixed(3)}, threshold=${COSINE_THRESHOLD})`,
              );
              return undefined;
            }

            // 7. Build context string.
            const lines = reranked.map((m, i) => {
              const meta = hookMetaMap.get(m.id);
              const importance = meta?.importance ?? 5;
              const age = meta?.age ?? '';
              return `${i + 1}. ${m.text} (importance: ${importance}/10, ${age})`;
            });
            const contextString = `## Relevant Memories\n\n${lines.join('\n')}`;

            return { prependContext: contextString + welcomeBack + billingWarning };
          }

          // --- Server mode (existing behavior) ---

          // 1. Generate word trapdoors from the user prompt.
          const wordTrapdoors = generateBlindIndices(evt.prompt);

          // 2. Generate query embedding + LSH trapdoors (may fail gracefully).
          let queryEmbedding: number[] | null = null;
          let lshTrapdoors: string[] = [];
          try {
            queryEmbedding = await generateEmbedding(evt.prompt, { isQuery: true });
            const hasher = getLSHHasher(api.logger);
            if (hasher && queryEmbedding) {
              lshTrapdoors = hasher.hash(queryEmbedding);
            }
          } catch {
            // Embedding/LSH failed -- proceed with word-only trapdoors.
          }

          // 3. Merge word + LSH trapdoors.
          const allTrapdoors = [...wordTrapdoors, ...lshTrapdoors];
          if (allTrapdoors.length === 0) return undefined;

          // 4. Fetch candidates from the server (dynamic pool sizing).
          const factCount = await getFactCount(api.logger);
          const pool = computeCandidatePool(factCount);
          const candidates = await apiClient!.search(
            userId!,
            allTrapdoors,
            pool,
            authKeyHex!,
          );

          if (candidates.length === 0) return undefined;

          // 5. Decrypt candidates (text + embeddings) and build reranker input.
          const rerankerCandidates: RerankerCandidate[] = [];
          const hookMetaMap = new Map<string, { importance: number; age: string }>();

          for (const candidate of candidates) {
            try {
              const docJson = decryptFromHex(candidate.encrypted_blob, encryptionKey!);
              const doc = JSON.parse(docJson) as { text: string; metadata?: Record<string, unknown> };

              // Decrypt embedding if present.
              let decryptedEmbedding: number[] | undefined;
              if (candidate.encrypted_embedding) {
                try {
                  decryptedEmbedding = JSON.parse(
                    decryptFromHex(candidate.encrypted_embedding, encryptionKey!),
                  );
                } catch {
                  // Embedding decryption failed -- proceed without it.
                }
              }

              const importanceRaw = (doc.metadata?.importance as number) ?? 0.5;
              const createdAtSec = typeof candidate.timestamp === 'number'
                ? candidate.timestamp / 1000
                : new Date(candidate.timestamp).getTime() / 1000;
              rerankerCandidates.push({
                id: candidate.fact_id,
                text: doc.text,
                embedding: decryptedEmbedding,
                importance: importanceRaw,
                createdAt: createdAtSec,
              });

              const importance = doc.metadata?.importance
                ? Math.round((doc.metadata.importance as number) * 10)
                : 5;
              hookMetaMap.set(candidate.fact_id, {
                importance,
                age: relativeTime(candidate.timestamp),
              });
            } catch {
              // Skip un-decryptable candidates.
            }
          }

          // 6. Re-rank with BM25 + cosine + RRF fusion (intent-weighted).
          const srvHookIntent = detectQueryIntent(evt.prompt);
          const reranked = rerank(
            evt.prompt,
            queryEmbedding ?? [],
            rerankerCandidates,
            8,
            INTENT_WEIGHTS[srvHookIntent],
          );

          // B2: Minimum relevance threshold — skip noise injection for irrelevant turns.
          const candidatesWithEmbSrv = rerankerCandidates.filter(c => c.embedding && c.embedding.length > 0);
          if (candidatesWithEmbSrv.length > 0 && queryEmbedding && queryEmbedding.length > 0) {
            const topCosine = Math.max(
              ...candidatesWithEmbSrv.map(c => cosineSimilarity(queryEmbedding!, c.embedding!))
            );
            if (topCosine < RELEVANCE_THRESHOLD) return undefined;
          }

          if (reranked.length === 0) return undefined;

          // 7. Build context string.
          const lines = reranked.map((m, i) => {
            const meta = hookMetaMap.get(m.id);
            const importance = meta?.importance ?? 5;
            const age = meta?.age ?? '';
            return `${i + 1}. ${m.text} (importance: ${importance}/10, ${age})`;
          });
          const contextString = `## Relevant Memories\n\n${lines.join('\n')}`;

          return { prependContext: contextString + welcomeBack + billingWarning };
        } catch (err: unknown) {
          // The hook must NEVER throw -- log and return undefined.
          const message = err instanceof Error ? err.message : String(err);
          api.logger.warn(`before_agent_start hook failed: ${message}`);
          return undefined;
        }
      },
      { priority: 10 },
    );

    // ---------------------------------------------------------------
    // Hook: agent_end — auto-extract facts after each conversation turn
    // ---------------------------------------------------------------

    api.on(
      'agent_end',
      async (event: unknown) => {
        try {
          const evt = event as { messages?: unknown[]; success?: boolean } | undefined;
          if (!evt?.success || !evt?.messages || evt.messages.length < 2) return;

          await ensureInitialized(api.logger);
          if (needsSetup) return;

          // C3: Throttle auto-extraction to every N turns (configurable via env).
          turnsSinceLastExtraction++;
          if (turnsSinceLastExtraction >= getExtractInterval()) {
            const existingMemories = isLlmDedupEnabled()
              ? await fetchExistingMemoriesForExtraction(api.logger, 20, evt.messages)
              : [];
            const rawFacts = await extractFacts(evt.messages, 'turn', existingMemories);
            const { kept: importanceFiltered } = filterByImportance(rawFacts, api.logger);
            const maxFacts = getMaxFactsPerExtraction();
            if (importanceFiltered.length > maxFacts) {
              api.logger.info(
                `Capped extraction from ${importanceFiltered.length} to ${maxFacts} facts`,
              );
            }
            const facts = importanceFiltered.slice(0, maxFacts);
            if (facts.length > 0) {
              await storeExtractedFacts(facts, api.logger);
            }
            turnsSinceLastExtraction = 0;
          }
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          api.logger.warn(`agent_end extraction failed: ${message}`);
        }
      },
      { priority: 90 },
    );

    // ---------------------------------------------------------------
    // Hook: before_compaction — extract ALL facts before context is lost
    // ---------------------------------------------------------------

    api.on(
      'before_compaction',
      async (event: unknown) => {
        try {
          const evt = event as { messages?: unknown[]; messageCount?: number } | undefined;
          if (!evt?.messages || evt.messages.length < 2) return;

          await ensureInitialized(api.logger);
          if (needsSetup) return;

          api.logger.info(
            `Pre-compaction extraction: processing ${evt.messages.length} messages`,
          );

          const existingMemories = isLlmDedupEnabled()
            ? await fetchExistingMemoriesForExtraction(api.logger, 50, evt.messages)
            : [];
          const rawCompactFacts = await extractFacts(evt.messages, 'full', existingMemories);
          const { kept: compactImportanceFiltered } = filterByImportance(rawCompactFacts, api.logger);
          const maxFactsCompact = getMaxFactsPerExtraction();
          if (compactImportanceFiltered.length > maxFactsCompact) {
            api.logger.info(
              `Capped compaction extraction from ${compactImportanceFiltered.length} to ${maxFactsCompact} facts`,
            );
          }
          const facts = compactImportanceFiltered.slice(0, maxFactsCompact);
          if (facts.length > 0) {
            await storeExtractedFacts(facts, api.logger);
          }
          turnsSinceLastExtraction = 0; // Reset C3 counter on compaction.
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          api.logger.warn(`before_compaction extraction failed: ${message}`);
        }
      },
      { priority: 5 },
    );

    // ---------------------------------------------------------------
    // Hook: before_reset — final extraction before session is cleared
    // ---------------------------------------------------------------

    api.on(
      'before_reset',
      async (event: unknown) => {
        try {
          const evt = event as { messages?: unknown[]; reason?: string } | undefined;
          if (!evt?.messages || evt.messages.length < 2) return;

          await ensureInitialized(api.logger);
          if (needsSetup) return;

          api.logger.info(
            `Pre-reset extraction (${evt.reason ?? 'unknown'}): processing ${evt.messages.length} messages`,
          );

          const existingMemories = isLlmDedupEnabled()
            ? await fetchExistingMemoriesForExtraction(api.logger, 50, evt.messages)
            : [];
          const rawResetFacts = await extractFacts(evt.messages, 'full', existingMemories);
          const { kept: resetImportanceFiltered } = filterByImportance(rawResetFacts, api.logger);
          const maxFactsReset = getMaxFactsPerExtraction();
          if (resetImportanceFiltered.length > maxFactsReset) {
            api.logger.info(
              `Capped reset extraction from ${resetImportanceFiltered.length} to ${maxFactsReset} facts`,
            );
          }
          const facts = resetImportanceFiltered.slice(0, maxFactsReset);
          if (facts.length > 0) {
            await storeExtractedFacts(facts, api.logger);
          }
          turnsSinceLastExtraction = 0; // Reset C3 counter on reset.
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          api.logger.warn(`before_reset extraction failed: ${message}`);
        }
      },
      { priority: 5 },
    );
  },
};

export default plugin;

/**
 * Reset all module-level state for test isolation.
 * ONLY call this from test code — never in production.
 */
export function __resetForTesting(): void {
  authKeyHex = null;
  encryptionKey = null;
  dedupKey = null;
  userId = null;
  subgraphOwner = null;
  apiClient = null;
  initPromise = null;
  lshHasher = null;
  lshInitFailed = false;
  masterPasswordCache = null;
  saltCache = null;
  cachedFactCount = null;
  lastFactCountFetch = 0;
  pluginHotCache = null;
  lastSearchTimestamp = 0;
  lastQueryEmbedding = null;
  turnsSinceLastExtraction = 0;
}
