/**
 * Subgraph store path — writes facts on-chain via ERC-4337 UserOps.
 *
 * Used when the managed service is active (TOTALRECLAW_SELF_HOSTED is not
 * "true"). Replaces the HTTP POST to /v1/store with an on-chain transaction
 * flow.
 *
 * Builds UserOps client-side using `permissionless` + `viem` and submits
 * them through the TotalReclaw relay server, which proxies bundler/paymaster
 * JSON-RPC to Pimlico with its own API key. Clients never need a Pimlico key.
 */

import { createPublicClient, http, type Hex, type Address, type Chain } from 'viem';
import { entryPoint07Address } from 'viem/account-abstraction';
import { mnemonicToAccount } from 'viem/accounts';
import { gnosis, gnosisChiado, baseSepolia } from 'viem/chains';
import { createSmartAccountClient } from 'permissionless';
import { toSimpleSmartAccount } from 'permissionless/accounts';
import { createPimlicoClient } from 'permissionless/clients/pimlico';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Default EventfulDataEdge contract address on Gnosis mainnet */
const DEFAULT_DATA_EDGE_ADDRESS = '0xC445af1D4EB9fce4e1E61fE96ea7B8feBF03c5ca';

/** Well-known ERC-4337 EntryPoint v0.7 address (same on all chains) */
const DEFAULT_ENTRYPOINT_ADDRESS = '0x0000000071727De22E5E9d8BAf0edAc6f37da032';

export interface SubgraphStoreConfig {
  relayUrl: string;           // TotalReclaw relay server URL (proxies bundler + subgraph)
  mnemonic: string;           // BIP-39 mnemonic for key derivation
  cachePath: string;          // Hot cache file path
  chainId: number;            // 100 for Gnosis mainnet, 10200 for Chiado testnet, 84532 for Base Sepolia
  dataEdgeAddress: string;    // EventfulDataEdge contract address
  entryPointAddress: string;  // ERC-4337 EntryPoint v0.7
  authKeyHex?: string;        // HKDF auth key for relay server Authorization header
  rpcUrl?: string;            // Override chain RPC URL for public client reads
  walletAddress?: string;     // Smart Account address for billing (X-Wallet-Address header)
}

export interface FactPayload {
  id: string;
  timestamp: string;
  owner: string;           // Smart Account address (hex)
  encryptedBlob: string;   // Hex-encoded AES-256-GCM ciphertext
  blindIndices: string[];   // SHA-256 hashes (word + LSH)
  decayScore: number;
  source: string;
  contentFp: string;
  agentId: string;
  encryptedEmbedding?: string;
}

// ---------------------------------------------------------------------------
// Protobuf encoding (unchanged)
// ---------------------------------------------------------------------------

/**
 * Encode a fact payload as a minimal Protobuf wire format.
 *
 * Field numbers match server/proto/totalreclaw.proto:
 *   1: id (string), 2: timestamp (string), 3: owner (string),
 *   4: encrypted_blob (bytes), 5: blind_indices (repeated string),
 *   6: decay_score (double), 7: is_active (bool), 8: version (int32),
 *   9: source (string), 10: content_fp (string), 11: agent_id (string),
 *   12: sequence_id (int64), 13: encrypted_embedding (string)
 */
export function encodeFactProtobuf(fact: FactPayload): Buffer {
  const parts: Buffer[] = [];

  // Helper: encode a string field
  const writeString = (fieldNumber: number, value: string) => {
    if (!value) return;
    const data = Buffer.from(value, 'utf-8');
    const key = (fieldNumber << 3) | 2; // wire type 2 = length-delimited
    parts.push(encodeVarint(key));
    parts.push(encodeVarint(data.length));
    parts.push(data);
  };

  // Helper: encode a bytes field
  const writeBytes = (fieldNumber: number, value: Buffer) => {
    const key = (fieldNumber << 3) | 2;
    parts.push(encodeVarint(key));
    parts.push(encodeVarint(value.length));
    parts.push(value);
  };

  // Helper: encode a double field (wire type 1 = 64-bit)
  const writeDouble = (fieldNumber: number, value: number) => {
    const key = (fieldNumber << 3) | 1;
    parts.push(encodeVarint(key));
    const buf = Buffer.alloc(8);
    buf.writeDoubleLE(value);
    parts.push(buf);
  };

  // Helper: encode a varint field (wire type 0)
  const writeVarintField = (fieldNumber: number, value: number) => {
    const key = (fieldNumber << 3) | 0;
    parts.push(encodeVarint(key));
    parts.push(encodeVarint(value));
  };

  // Encode fields
  writeString(1, fact.id);
  writeString(2, fact.timestamp);
  writeString(3, fact.owner);
  writeBytes(4, Buffer.from(fact.encryptedBlob, 'hex'));

  for (const index of fact.blindIndices) {
    writeString(5, index);
  }

  writeDouble(6, fact.decayScore);
  writeVarintField(7, 1); // is_active = true
  writeVarintField(8, 2); // version = 2
  writeString(9, fact.source);
  writeString(10, fact.contentFp);
  writeString(11, fact.agentId);
  // Field 12 (sequence_id) is assigned by the subgraph mapping, not the client
  if (fact.encryptedEmbedding) {
    writeString(13, fact.encryptedEmbedding);
  }

  return Buffer.concat(parts);
}

/** Encode an integer as a Protobuf varint */
export function encodeVarint(value: number): Buffer {
  const bytes: number[] = [];
  let v = value >>> 0; // unsigned
  while (v > 0x7f) {
    bytes.push((v & 0x7f) | 0x80);
    v >>>= 7;
  }
  bytes.push(v & 0x7f);
  return Buffer.from(bytes);
}

// ---------------------------------------------------------------------------
// Chain helpers
// ---------------------------------------------------------------------------

/** Resolve a viem Chain object from chain ID */
function getChainFromId(chainId: number): Chain {
  switch (chainId) {
    case 100:
      return gnosis;
    case 10200:
      return gnosisChiado;
    case 84532:
      return baseSepolia;
    default:
      return gnosis;
  }
}

/** Build the relay bundler RPC URL from the relay server URL */
function getRelayBundlerUrl(relayUrl: string): string {
  return `${relayUrl}/v1/bundler`;
}

// ---------------------------------------------------------------------------
// On-chain submission (Pimlico UserOps)
// ---------------------------------------------------------------------------

/**
 * Submit a fact on-chain via ERC-4337 UserOp through the relay server.
 *
 * Builds a UserOp client-side using `permissionless` + `viem`:
 * 1. Derives private key from mnemonic (BIP-39 + BIP-44 m/44'/60'/0'/0/0)
 * 2. Creates a SimpleSmartAccount
 * 3. Gets paymaster sponsorship (via relay proxy to Pimlico)
 * 4. Signs and submits the UserOp to relay bundler endpoint
 * 5. Waits for the transaction receipt
 *
 * The relay server proxies all bundler/paymaster JSON-RPC to Pimlico
 * with its own API key. Clients never need a Pimlico API key.
 */
export async function submitFactOnChain(
  protobufPayload: Buffer,
  config: SubgraphStoreConfig,
): Promise<{ txHash: string; userOpHash: string; success: boolean }> {
  if (!config.relayUrl) {
    throw new Error('Relay URL (TOTALRECLAW_SERVER_URL) is required for on-chain submission');
  }

  if (!config.mnemonic) {
    throw new Error('Mnemonic (TOTALRECLAW_RECOVERY_PHRASE) is required for on-chain submission');
  }

  const chain = getChainFromId(config.chainId);
  const bundlerRpcUrl = getRelayBundlerUrl(config.relayUrl);
  const dataEdgeAddress = config.dataEdgeAddress as Address;
  const entryPointAddr = (config.entryPointAddress || entryPoint07Address) as Address;

  // Build authenticated transport for relay server proxy
  const headers: Record<string, string> = {
    'X-TotalReclaw-Client': 'openclaw-plugin',
  };
  if (config.authKeyHex) headers['Authorization'] = `Bearer ${config.authKeyHex}`;
  if (config.walletAddress) headers['X-Wallet-Address'] = config.walletAddress;

  const authTransport = Object.keys(headers).length > 0
    ? http(bundlerRpcUrl, { fetchOptions: { headers } })
    : http(bundlerRpcUrl);

  // 1. Derive EOA signer from mnemonic (BIP-44 m/44'/60'/0'/0/0)
  const ownerAccount = mnemonicToAccount(config.mnemonic);

  // 2. Create a public client for chain reads (using explicit RPC if configured,
  //    NOT the bundler proxy which only supports ERC-4337 JSON-RPC methods)
  const publicClient = createPublicClient({
    chain,
    transport: config.rpcUrl ? http(config.rpcUrl) : http(),
  });

  // 3. Create Pimlico client for bundler + paymaster operations (via relay)
  const pimlicoClient = createPimlicoClient({
    chain,
    transport: authTransport,
    entryPoint: {
      address: entryPointAddr,
      version: '0.7',
    },
  });

  // 4. Create a SimpleSmartAccount (auto-generates initCode if undeployed)
  const smartAccount = await toSimpleSmartAccount({
    client: publicClient,
    owner: ownerAccount,
    entryPoint: {
      address: entryPointAddr,
      version: '0.7',
    },
  });

  // 5. Create smart account client wired to relay bundler + paymaster
  const smartAccountClient = createSmartAccountClient({
    account: smartAccount,
    chain,
    bundlerTransport: authTransport,
    // Paymaster sponsorship proxied through relay to Pimlico
    paymaster: pimlicoClient,
    userOperation: {
      estimateFeesPerGas: async () => {
        return (await pimlicoClient.getUserOperationGasPrice()).fast;
      },
    },
  });

  // 6. Send the transaction: Smart Account execute(dataEdgeAddress, 0, protobufPayload)
  //    The DataEdge contract has a fallback() that emits Log(bytes), so the calldata
  //    IS the protobuf payload directly (no function selector needed).
  //    permissionless encodes the execute() call internally from to/value/data.
  const calldata = `0x${protobufPayload.toString('hex')}` as Hex;

  // Use sendUserOperation to get the userOpHash, then wait for receipt
  const userOpHash = await smartAccountClient.sendUserOperation({
    calls: [
      {
        to: dataEdgeAddress,
        value: 0n,
        data: calldata,
      },
    ],
  });

  // 7. Wait for the UserOp to be included in a transaction
  const receipt = await pimlicoClient.waitForUserOperationReceipt({
    hash: userOpHash,
  });

  return {
    txHash: receipt.receipt.transactionHash,
    userOpHash,
    success: receipt.success,
  };
}

/**
 * Submit multiple facts on-chain in a single ERC-4337 UserOp (batched).
 *
 * Each protobuf payload becomes one call in a multi-call UserOp. The
 * DataEdge contract emits a separate Log(bytes) event per call, and the
 * subgraph indexes each event independently (by txHash + logIndex).
 *
 * Falls back to single-fact path for batches of 1 (no multicall overhead).
 */
export async function submitFactBatchOnChain(
  protobufPayloads: Buffer[],
  config: SubgraphStoreConfig,
): Promise<{ txHash: string; userOpHash: string; success: boolean; batchSize: number }> {
  if (!protobufPayloads.length) {
    return { txHash: '', userOpHash: '', success: true, batchSize: 0 };
  }

  // Single fact — use standard path (avoids multicall overhead)
  if (protobufPayloads.length === 1) {
    const result = await submitFactOnChain(protobufPayloads[0], config);
    return { ...result, batchSize: 1 };
  }

  if (!config.relayUrl) {
    throw new Error('Relay URL (TOTALRECLAW_SERVER_URL) is required for on-chain submission');
  }
  if (!config.mnemonic) {
    throw new Error('Mnemonic (TOTALRECLAW_RECOVERY_PHRASE) is required for on-chain submission');
  }

  const chain = getChainFromId(config.chainId);
  const bundlerRpcUrl = getRelayBundlerUrl(config.relayUrl);
  const dataEdgeAddress = config.dataEdgeAddress as Address;
  const entryPointAddr = (config.entryPointAddress || entryPoint07Address) as Address;

  const headers: Record<string, string> = {
    'X-TotalReclaw-Client': 'openclaw-plugin',
  };
  if (config.authKeyHex) headers['Authorization'] = `Bearer ${config.authKeyHex}`;
  if (config.walletAddress) headers['X-Wallet-Address'] = config.walletAddress;

  const authTransport = Object.keys(headers).length > 0
    ? http(bundlerRpcUrl, { fetchOptions: { headers } })
    : http(bundlerRpcUrl);

  const ownerAccount = mnemonicToAccount(config.mnemonic);
  const publicClient = createPublicClient({
    chain,
    transport: config.rpcUrl ? http(config.rpcUrl) : http(),
  });

  const pimlicoClient = createPimlicoClient({
    chain,
    transport: authTransport,
    entryPoint: {
      address: entryPointAddr,
      version: '0.7',
    },
  });

  const smartAccount = await toSimpleSmartAccount({
    client: publicClient,
    owner: ownerAccount,
    entryPoint: {
      address: entryPointAddr,
      version: '0.7',
    },
  });

  const smartAccountClient = createSmartAccountClient({
    account: smartAccount,
    chain,
    bundlerTransport: authTransport,
    paymaster: pimlicoClient,
    userOperation: {
      estimateFeesPerGas: async () => {
        return (await pimlicoClient.getUserOperationGasPrice()).fast;
      },
    },
  });

  // Build multi-call batch: each payload → one call to DataEdge fallback()
  const calls = protobufPayloads.map(payload => ({
    to: dataEdgeAddress,
    value: 0n,
    data: `0x${payload.toString('hex')}` as Hex,
  }));

  const userOpHash = await smartAccountClient.sendUserOperation({ calls });
  const receipt = await pimlicoClient.waitForUserOperationReceipt({ hash: userOpHash });

  return {
    txHash: receipt.receipt.transactionHash,
    userOpHash,
    success: receipt.success,
    batchSize: protobufPayloads.length,
  };
}

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * Check if subgraph mode is enabled (i.e. using the managed service).
 *
 * Returns true when TOTALRECLAW_SELF_HOSTED is NOT set to "true".
 * The managed service (subgraph mode) is the default.
 */
export function isSubgraphMode(): boolean {
  return process.env.TOTALRECLAW_SELF_HOSTED !== 'true';
}

/**
 * Get subgraph configuration from environment variables.
 *
 * After the relay refactor, clients only need:
 *   - TOTALRECLAW_RECOVERY_PHRASE -- BIP-39 mnemonic
 *   - TOTALRECLAW_SERVER_URL -- relay server URL (default: https://api.totalreclaw.xyz)
 *   - TOTALRECLAW_SELF_HOSTED -- set "true" to use self-hosted server (default: managed service)
 *   - TOTALRECLAW_CHAIN_ID -- optional, defaults to 100 (Gnosis mainnet)
 *
 * Removed from client-side config (now server-side only):
 *   - PIMLICO_API_KEY
 *   - TOTALRECLAW_SUBGRAPH_ENDPOINT
 */
/**
 * Derive the Smart Account address from a BIP-39 mnemonic.
 * This is the on-chain owner identity used in the subgraph.
 */
export async function deriveSmartAccountAddress(mnemonic: string, chainId?: number): Promise<string> {
  const chain: Chain = getChainFromId(chainId ?? 100);
  const ownerAccount = mnemonicToAccount(mnemonic);
  const entryPointAddr = (process.env.TOTALRECLAW_ENTRYPOINT_ADDRESS || DEFAULT_ENTRYPOINT_ADDRESS) as Address;
  const rpcUrl = process.env.TOTALRECLAW_RPC_URL;

  const publicClient = createPublicClient({
    chain,
    transport: rpcUrl ? http(rpcUrl) : http(),
  });

  const smartAccount = await toSimpleSmartAccount({
    client: publicClient,
    owner: ownerAccount,
    entryPoint: {
      address: entryPointAddr,
      version: '0.7',
    },
  });

  return smartAccount.address.toLowerCase();
}

export function getSubgraphConfig(): SubgraphStoreConfig {
  return {
    relayUrl: process.env.TOTALRECLAW_SERVER_URL || 'https://api.totalreclaw.xyz',
    mnemonic: process.env.TOTALRECLAW_RECOVERY_PHRASE || '',
    cachePath: process.env.TOTALRECLAW_CACHE_PATH || `${process.env.HOME}/.totalreclaw/cache.enc`,
    chainId: parseInt(process.env.TOTALRECLAW_CHAIN_ID || '100'),
    dataEdgeAddress: process.env.TOTALRECLAW_DATA_EDGE_ADDRESS || DEFAULT_DATA_EDGE_ADDRESS,
    entryPointAddress: process.env.TOTALRECLAW_ENTRYPOINT_ADDRESS || DEFAULT_ENTRYPOINT_ADDRESS,
    rpcUrl: process.env.TOTALRECLAW_RPC_URL || undefined,
  };
}
