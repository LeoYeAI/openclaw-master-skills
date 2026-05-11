#!/usr/bin/env node
import './_env.js';
import { ethers } from 'ethers';
import { getNetwork, providerFor, loadWallet, parseEth, arg, loadApiKey, ESCROW } from './_lib.js';

// Minimal on-chain bounty creation (no IPFS upload).
// Intended for testnet smoke tests only.
//
// IMPORTANT: This uses a hardcoded evaluation CID by default, which produces
// a bounty without a real evaluation package (no title, rubric, or jury config
// in the UI). For a full end-to-end test with a properly evaluable bounty,
// create via the web UI or the HTTP API (POST /api/jobs/create) instead.

const network = getNetwork();
const provider = providerFor(network);
const wallet = await loadWallet();
const signer = wallet.connect(provider);

const contractAddress = ESCROW[network];
if (!contractAddress) throw new Error(`Missing escrow address for network=${network}`);

const evaluationCid = arg('cid', 'QmRLB6LYe6VER6UQDoX7wt4LmKATHbGA81ny5vgRMbfrtX');
// NOTE: This script does on-chain creation only. If you want a titled job + full evaluation package,
// create via the HTTP API first (POST /api/jobs/create), then create on-chain with job.primaryCid.
const classId = Number(arg('classId', '128')); // default active class (Core)

// ---- Preflight: verify class exists + is ACTIVE and has models (via Agent API) ----

async function preflightClassOrThrow(classId) {
  const noPreflight = process.argv.includes('--no-preflight');
  if (noPreflight) return;

  const baseUrl = (process.env.VERDIKTA_BOUNTIES_BASE_URL || '').replace(/\/+$/, '');
  if (!baseUrl) {
    console.warn('[preflight] VERDIKTA_BOUNTIES_BASE_URL not set; skipping class preflight. (use --no-preflight to silence)');
    return;
  }

  let apiKey = null;
  try {
    apiKey = await loadApiKey();
  } catch (e) {
    console.warn(`[preflight] Could not load bot API key; skipping class preflight: ${e.message}`);
    return;
  }
  if (!apiKey) {
    console.warn('[preflight] Bot file missing apiKey; skipping class preflight.');
    return;
  }

  const headers = { 'X-Bot-API-Key': apiKey };

  const clsRes = await fetch(`${baseUrl}/api/classes/${classId}`, { headers });
  if (!clsRes.ok) {
    const t = await clsRes.text().catch(() => '');
    throw new Error(`[preflight] Class ${classId} not available on ${baseUrl} (HTTP ${clsRes.status}). ${t}`);
  }
  const clsJson = await clsRes.json();
  const status = clsJson?.class?.status;
  if (status !== 'ACTIVE') {
    throw new Error(`[preflight] Class ${classId} is not ACTIVE (status=${status}). Pick an ACTIVE class from GET /api/classes?status=ACTIVE`);
  }

  const modelsRes = await fetch(`${baseUrl}/api/classes/${classId}/models`, { headers });
  if (!modelsRes.ok) {
    const t = await modelsRes.text().catch(() => '');
    throw new Error(`[preflight] Failed to fetch models for class ${classId} (HTTP ${modelsRes.status}). ${t}`);
  }
  const modelsJson = await modelsRes.json();
  const modelCount = Array.isArray(modelsJson?.models) ? modelsJson.models.length : 0;
  if (modelCount === 0) {
    throw new Error(`[preflight] Class ${classId} returned 0 models. Refusing to create bounty (would likely be unevaluable).`);
  }

  console.log(`[preflight] ✅ class ${classId} ACTIVE; models available: ${modelCount}`);
}
const threshold = Number(arg('threshold', '80'));
const hours = Number(arg('hours', '6'));
const amountEth = arg('eth', '0.001');

const deadline = Math.floor(Date.now() / 1000) + Math.floor(hours * 3600);
const value = parseEth(amountEth);

const ABI = [
  'function createBounty(string evaluationCid, uint64 requestedClass, uint8 threshold, uint64 submissionDeadline) payable returns (uint256)',
  'event BountyCreated(uint256 indexed bountyId, address indexed creator, string evaluationCid, uint64 classId, uint8 threshold, uint256 payoutWei, uint64 submissionDeadline)'
];

const contract = new ethers.Contract(contractAddress, ABI, signer);

await preflightClassOrThrow(classId);

console.log('Creating bounty on-chain');
console.log('Network:', network);
console.log('Escrow:', contractAddress);
console.log('Creator:', signer.address);
console.log('CID:', evaluationCid);
console.log('classId:', classId);
console.log('threshold:', threshold);
console.log('deadline:', deadline, `(in ${hours}h)`);
console.log('value:', amountEth, 'ETH');

const tx = await contract.createBounty(evaluationCid, classId, threshold, deadline, { value });
console.log('Tx:', tx.hash);
const receipt = await tx.wait();

let bountyId = null;
for (const log of (receipt.logs || [])) {
  try {
    const parsed = contract.interface.parseLog(log);
    if (parsed?.name === 'BountyCreated') {
      bountyId = String(parsed.args.bountyId ?? parsed.args[0]);
      break;
    }
  } catch {}
}

console.log('Confirmed in block:', receipt.blockNumber);
console.log('BountyId:', bountyId ?? '(not parsed)');
