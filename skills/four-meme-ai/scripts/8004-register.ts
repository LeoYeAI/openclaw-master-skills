#!/usr/bin/env node
/**
 * EIP-8004 NFT – register agent (mint identity NFT).
 * Builds agentURI as data:application/json;base64,<payload> and calls contract.register(agentURI).
 *
 * Usage:
 *   npx tsx 8004-register.ts <name> [imageUrl] [description]
 *   - name: required
 *   - imageUrl: optional (URL string)
 *   - description: optional
 *
 * Env: PRIVATE_KEY. Optional: BSC_RPC_URL, 8004_NFT_ADDRESS.
 * Default contract: 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 (BSC).
 */

import { createPublicClient, createWalletClient, decodeEventLog, http, parseAbi } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { bsc } from 'viem/chains';

const DEFAULT_8004_NFT = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432' as const;

const REGISTRATION_TYPE = 'https://eips.ethereum.org/EIPS/eip-8004#registration-v1';

const ABI = parseAbi([
  'function register(string agentURI) returns (uint256 agentId)',
  'event Registered(uint256 indexed agentId, string agentURI, address indexed owner)',
]);

function buildAgentURI(name: string, imageUrl: string, description: string): string {
  const payload = {
    type: REGISTRATION_TYPE,
    name: name || '',
    description: description || 'I\'m four.meme trading agent',
    image: imageUrl || '',
    active: true,
    supportedTrust: [''],
  };
  const json = JSON.stringify(payload);
  const base64 = Buffer.from(json, 'utf8').toString('base64');
  return `data:application/json;base64,${base64}`;
}

async function main() {
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error('Set PRIVATE_KEY');
    process.exit(1);
  }
  const pk = privateKey.startsWith('0x') ? (privateKey as `0x${string}`) : (`0x${privateKey}` as `0x${string}`);
  const account = privateKeyToAccount(pk);

  const name = process.argv[2];
  const imageUrl = process.argv[3] ?? '';
  const description = process.argv[4] ?? '';

  if (!name || name.trim() === '') {
    console.error('Usage: 8004-register.ts <name> [imageUrl] [description]');
    console.error('  name: required. imageUrl and description are optional.');
    process.exit(1);
  }

  const agentURI = buildAgentURI(name.trim(), imageUrl.trim(), description.trim());
  const contractAddress = (process.env['8004_NFT_ADDRESS'] || process.env.EIP8004_NFT_ADDRESS || DEFAULT_8004_NFT) as `0x${string}`;
  const rpcUrl = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

  const wallet = createWalletClient({
    account,
    chain: bsc,
    transport: http(rpcUrl),
  });
  const publicClient = createPublicClient({
    chain: bsc,
    transport: http(rpcUrl),
  });

  const txHash = await wallet.writeContract({
    address: contractAddress,
    abi: ABI,
    functionName: 'register',
    args: [agentURI],
  });

  const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash });
  let agentId: number | null = null;
  for (const l of receipt.logs) {
    if (l.address.toLowerCase() !== contractAddress.toLowerCase()) continue;
    try {
      const d = decodeEventLog({
        abi: ABI,
        data: l.data,
        topics: l.topics,
      });
      if (d.eventName === 'Registered') {
        agentId = Number((d.args as { agentId: bigint }).agentId);
        break;
      }
    } catch {
      /* ignore */
    }
  }

  console.log(JSON.stringify({ txHash, agentId, agentURI }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
