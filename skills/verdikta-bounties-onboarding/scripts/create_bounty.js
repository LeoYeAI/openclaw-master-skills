#!/usr/bin/env node
// Complete bounty creation: API (build evaluation package) → on-chain (fund bounty).
// The bot wallet signs the on-chain transaction automatically.
//
// Usage:
//   node create_bounty.js --config bounty.json
//
// bounty.json example:
// {
//   "title": "Book Review: The Pragmatic Programmer",
//   "description": "Write a 500-word review...",
//   "bountyAmount": "0.001",
//   "threshold": 75,
//   "classId": 128,
//   "submissionWindowHours": 24,
//   "workProductType": "writing",
//   "rubricJson": {
//     "title": "Book Review",
//     "criteria": [
//       { "id": "quality", "label": "Quality", "description": "...", "weight": 0.5, "must": false },
//       { "id": "clarity", "label": "Clarity", "description": "...", "weight": 0.5, "must": true }
//     ],
//     "threshold": 75,
//     "forbiddenContent": []
//   },
//   "juryNodes": [
//     { "provider": "OpenAI", "model": "gpt-5.2-2025-12-11", "weight": 0.5, "runs": 1 },
//     { "provider": "Anthropic", "model": "claude-3-5-haiku-20241022", "weight": 0.5, "runs": 1 }
//   ]
// }
//
// Prerequisites:
//   - Bot onboarded (onboard.js completed)
//   - Bot wallet funded with ETH
//   - Bot registered (API key saved)

import './_env.js';
import fs from 'node:fs/promises';
import { ethers } from 'ethers';
import {
  getNetwork, providerFor, loadWallet,
  ESCROW, escrowContract, arg, loadApiKey,
} from './_lib.js';

const configPath = arg('config');
if (!configPath) {
  console.error('Usage: node create_bounty.js --config bounty.json');
  console.error('See script header for bounty.json format.');
  process.exit(1);
}

// ---- Load config ----

let config;
try {
  const raw = await fs.readFile(configPath, 'utf8');
  config = JSON.parse(raw);
} catch (e) {
  console.error(`Failed to read config file: ${e.message}`);
  process.exit(1);
}

const {
  title,
  description,
  bountyAmount,
  bountyAmountUSD,
  threshold = 75,
  classId = 128,
  submissionWindowHours = 24,
  workProductType = 'writing',
  rubricJson,
  juryNodes,
} = config;

// Validate required fields
if (!title || !description) {
  console.error('Config must include "title" and "description".');
  process.exit(1);
}
if (!bountyAmount || isNaN(Number(bountyAmount)) || Number(bountyAmount) <= 0) {
  console.error('Config must include a positive "bountyAmount" (ETH).');
  process.exit(1);
}
if (!rubricJson || !Array.isArray(rubricJson.criteria) || rubricJson.criteria.length === 0) {
  console.error('Config must include "rubricJson" with at least one criterion.');
  process.exit(1);
}

// Validate each criterion has all required fields
const criterionErrors = [];
const seenIds = new Set();
for (let i = 0; i < rubricJson.criteria.length; i++) {
  const c = rubricJson.criteria[i];
  if (!c.id || typeof c.id !== 'string') criterionErrors.push(`Criterion ${i}: missing or invalid "id" (string)`);
  if (seenIds.has(c.id)) criterionErrors.push(`Criterion ${i}: duplicate id "${c.id}"`);
  seenIds.add(c.id);
  if (!c.description || typeof c.description !== 'string') criterionErrors.push(`Criterion ${i}: missing "description" (string)`);
  if (typeof c.weight !== 'number' || c.weight < 0 || c.weight > 1) criterionErrors.push(`Criterion ${i}: missing or invalid "weight" (number 0-1)`);
  if (typeof c.must !== 'boolean') criterionErrors.push(`Criterion ${i}: missing "must" field (boolean, required). Set true for must-pass, false for weighted.`);
}
if (criterionErrors.length > 0) {
  console.error('Rubric criteria validation failed:');
  criterionErrors.forEach(e => console.error(`  - ${e}`));
  process.exit(1);
}

// Validate criteria weights sum to ~1.0
const criteriaWeightSum = rubricJson.criteria.reduce((s, c) => s + (c.weight || 0), 0);
if (Math.abs(criteriaWeightSum - 1.0) > 0.01) {
  console.error(`Criteria weights must sum to 1.0 (got ${criteriaWeightSum.toFixed(4)}).`);
  process.exit(1);
}

if (!juryNodes || !Array.isArray(juryNodes) || juryNodes.length === 0) {
  console.error('Config must include "juryNodes" array with at least one model.');
  process.exit(1);
}

// Validate jury weights sum to ~1.0
const weightSum = juryNodes.reduce((s, n) => s + (n.weight || 0), 0);
if (Math.abs(weightSum - 1.0) > 0.01) {
  console.error(`Jury node weights must sum to 1.0 (got ${weightSum.toFixed(4)}).`);
  process.exit(1);
}

// ---- Setup ----

const network = getNetwork();
const baseUrl = (process.env.VERDIKTA_BOUNTIES_BASE_URL || '').replace(/\/+$/, '');
if (!baseUrl) {
  console.error('VERDIKTA_BOUNTIES_BASE_URL not set. Run onboard.js first.');
  process.exit(1);
}

const provider = providerFor(network);
const wallet = await loadWallet();
const signer = wallet.connect(provider);
const creator = signer.address;

const apiKey = await loadApiKey();
if (!apiKey) {
  console.error('Missing API key. Run onboard.js first.');
  process.exit(1);
}

console.log(`\nCreating bounty: ${title}`);
console.log(`Network:  ${network}`);
console.log(`Creator:  ${creator}`);
console.log(`Amount:   ${bountyAmount} ETH`);
console.log(`Threshold: ${threshold}%`);
console.log(`Class:    ${classId}`);
console.log(`Window:   ${submissionWindowHours}h`);
console.log(`Jury:     ${juryNodes.map(n => `${n.provider}/${n.model}`).join(', ')}`);
console.log(`API:      ${baseUrl}`);

// ---- Step 1: Create job via API ----

console.log('\n--- Step 1: Create job via API (builds evaluation package + pins to IPFS) ---');

const apiBody = {
  title,
  description,
  creator,
  bountyAmount: String(bountyAmount),
  bountyAmountUSD: bountyAmountUSD || 0,
  threshold: Number(threshold),
  classId: Number(classId),
  submissionWindowHours: Number(submissionWindowHours),
  workProductType,
  rubricJson,
  juryNodes,
};

const apiRes = await fetch(`${baseUrl}/api/jobs/create`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Bot-API-Key': apiKey,
  },
  body: JSON.stringify(apiBody),
});

const apiData = await apiRes.json();
if (!apiRes.ok || !apiData.success) {
  console.error('API create failed:', JSON.stringify(apiData, null, 2));
  process.exit(1);
}

const jobId = apiData.job?.jobId;
// API may return the CID as primaryCid or evaluationCid depending on version
const primaryCid = apiData.job?.primaryCid || apiData.job?.evaluationCid;

if (!primaryCid) {
  console.error('API response missing primaryCid/evaluationCid:', JSON.stringify(apiData));
  process.exit(1);
}

console.log(`  Initial API Job ID: ${jobId}`);
console.log(`  evaluationCid: ${primaryCid}`);

// ---- Step 2: Create bounty on-chain ----

console.log('\n--- Step 2: Create bounty on-chain (bot wallet signs tx) ---');

const contractAddress = ESCROW[network];
if (!contractAddress) {
  console.error(`No escrow address for network ${network}`);
  process.exit(1);
}

const contract = escrowContract(network, signer);
const deadline = Math.floor(Date.now() / 1000) + (Number(submissionWindowHours) * 3600);
const value = ethers.parseEther(String(bountyAmount));

console.log(`  Escrow:    ${contractAddress}`);
console.log(`  CID:       ${primaryCid}`);
console.log(`  Deadline:  ${new Date(deadline * 1000).toISOString()}`);

// Dry-run first to catch revert reasons before spending gas
try {
  const gas = await contract.createBounty.estimateGas(primaryCid, classId, threshold, deadline, { value });
  console.log(`  estimated gas: ${gas.toString()}`);
} catch (err) {
  const reason = err.reason || err.shortMessage || err.message || 'unknown';
  console.error(`\n✖ createBounty will revert! Reason: ${reason}`);
  if (err.data) console.error(`  revert data: ${err.data}`);
  process.exit(1);
}

const tx = await contract.createBounty(primaryCid, classId, threshold, deadline, { value });
console.log(`  tx: ${tx.hash}`);
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

console.log(`  Confirmed in block: ${receipt.blockNumber}`);
console.log(`  On-chain bountyId:  ${bountyId ?? '(not parsed)'}`);

// ---- Step 3: Link on-chain bounty to API job ----
//
// The API sync service may reconcile the jobId to match the on-chain bountyId
// before our link call runs. When that happens, the job moves from apiJobId (e.g. 19)
// to bountyId (e.g. 12) in the API. We handle this by checking both IDs.

console.log('\n--- Step 3: Link on-chain bounty ID to API job ---');

// effectiveJobId is the ID to use for all subsequent API calls.
// Starts as the original apiJobId, but may change to bountyId after reconciliation.
let effectiveJobId = jobId;
let linked = false;

if (bountyId != null) {
  // Attempt 1: Direct link via original apiJobId
  const linkRes = await fetch(`${baseUrl}/api/jobs/${jobId}/bountyId`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-Bot-API-Key': apiKey,
    },
    body: JSON.stringify({
      bountyId: Number(bountyId),
      txHash: tx.hash,
      blockNumber: receipt.blockNumber,
    }),
  });

  if (linkRes.ok) {
    const linkData = await linkRes.json();
    const reconciledId = linkData.job?.jobId ?? bountyId;
    effectiveJobId = reconciledId;
    linked = true;
    console.log(`  Linked: API job ${jobId} → on-chain bounty ${reconciledId}`);
    if (Number(reconciledId) !== Number(jobId)) {
      console.log(`  Note: API reconciled jobId from ${jobId} → ${reconciledId} (aligned with on-chain)`);
    }
  } else {
    console.warn(`  Direct link failed (HTTP ${linkRes.status}) — job ${jobId} may have been reconciled by sync service.`);

    // Attempt 2: Check if sync service already reconciled the job under the bountyId
    console.log(`  Waiting 3s for sync service, then checking API job at bountyId ${bountyId}...`);
    await new Promise(r => setTimeout(r, 3000));

    const syncCheckRes = await fetch(`${baseUrl}/api/jobs/${bountyId}`, {
      headers: { 'X-Bot-API-Key': apiKey },
    });

    if (syncCheckRes.ok) {
      const syncCheckData = await syncCheckRes.json();
      const syncJob = syncCheckData.job || syncCheckData;
      const syncCid = syncJob.primaryCid || syncJob.evaluationCid;

      if (syncCid === primaryCid) {
        // Sync service reconciled correctly — job now lives at bountyId
        effectiveJobId = Number(bountyId);
        linked = true;
        console.log(`  ✓ Sync service already reconciled: job now at ID ${bountyId} with matching CID.`);
      } else if (syncCid) {
        console.warn(`  Found job at bountyId ${bountyId} but CID doesn't match:`);
        console.warn(`    API CID:      ${syncCid}`);
        console.warn(`    Expected CID: ${primaryCid}`);
        console.warn(`  This may be a different bounty occupying ID ${bountyId}.`);
      }
    }

    if (!linked) {
      // Attempt 3: Try resolve endpoint using bountyId (in case job moved)
      console.warn(`  Trying resolve via bountyId ${bountyId}...`);
      const resolveRes = await fetch(`${baseUrl}/api/jobs/${bountyId}/bountyId/resolve`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-Bot-API-Key': apiKey,
        },
        body: JSON.stringify({
          creator,
          rubricCid: primaryCid,
          submissionCloseTime: deadline,
          txHash: tx.hash,
        }),
      });

      if (resolveRes.ok) {
        const resolveData = await resolveRes.json();
        effectiveJobId = resolveData.bountyId ?? bountyId;
        linked = true;
        console.log(`  Linked via resolve (method: ${resolveData.method}, bountyId: ${resolveData.bountyId})`);
      } else {
        // Attempt 4: Also try resolve with the original apiJobId
        const resolveRes2 = await fetch(`${baseUrl}/api/jobs/${jobId}/bountyId/resolve`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-Bot-API-Key': apiKey,
          },
          body: JSON.stringify({
            creator,
            rubricCid: primaryCid,
            submissionCloseTime: deadline,
            txHash: tx.hash,
          }),
        });

        if (resolveRes2.ok) {
          const resolveData2 = await resolveRes2.json();
          effectiveJobId = resolveData2.bountyId ?? bountyId;
          linked = true;
          console.log(`  Linked via resolve on apiJobId (method: ${resolveData2.method}, bountyId: ${resolveData2.bountyId})`);
        } else {
          console.warn(`  ⚠ All link attempts failed. The bounty exists on-chain (bountyId=${bountyId})`);
          console.warn(`    but the API could not be linked.`);
          console.warn(`    The sync service may resolve this automatically. Use bountyId ${bountyId} for API calls.`);
          // Default to bountyId since that's the on-chain truth
          effectiveJobId = Number(bountyId);
        }
      }
    }
  }
} else {
  console.warn('  ⚠ Could not parse bountyId from event — skipping link step.');
  console.warn(`    Wait for auto-sync or manually call: PATCH /api/jobs/${jobId}/bountyId/resolve`);
}

console.log(`\n  Effective job ID for API calls: ${effectiveJobId}`);

// ---- Step 4: Verify on-chain integrity ----

console.log('\n--- Step 4: Verify on-chain ↔ API integrity ---');

let integrityOk = true;
const issues = [];

if (bountyId != null) {
  try {
    // On-chain verification via getBounty
    // Retry with backoff to handle RPC eventual consistency on public endpoints
    // (load-balanced RPCs may serve stale state right after tx.wait())
    const readContract = escrowContract(network, provider);
    let onChain;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        onChain = await readContract.getBounty(BigInt(bountyId));
        break;
      } catch (rpcErr) {
        if (attempt < 3 && rpcErr.message?.includes('bad bountyId')) {
          console.log(`  (RPC returned stale state for bountyId ${bountyId}, retrying in ${attempt * 2}s...)`);
          await new Promise(r => setTimeout(r, attempt * 2000));
        } else {
          throw rpcErr;
        }
      }
    }
    // onChain is a tuple: { creator, evaluationCid, requestedClass, threshold, payoutWei, createdAt, submissionDeadline, status, winner, submissions }

    const chainCreator = onChain.creator ?? onChain[0];
    const chainCid = onChain.evaluationCid ?? onChain[1];
    const chainClass = Number(onChain.requestedClass ?? onChain[2]);
    const chainThreshold = Number(onChain.threshold ?? onChain[3]);

    if (chainCreator.toLowerCase() !== creator.toLowerCase()) {
      issues.push(`creator mismatch: on-chain=${chainCreator}, expected=${creator}`);
    }
    if (chainCid !== primaryCid) {
      issues.push(`evaluationCid mismatch: on-chain=${chainCid}, expected=${primaryCid}`);
    }
    if (chainClass !== Number(classId)) {
      issues.push(`classId mismatch: on-chain=${chainClass}, expected=${classId}`);
    }
    if (chainThreshold !== Number(threshold)) {
      issues.push(`threshold mismatch: on-chain=${chainThreshold}, expected=${threshold}`);
    }

    if (issues.length === 0) {
      console.log('  On-chain: creator, CID, classId, threshold all match. ✓');
    }
  } catch (err) {
    issues.push(`on-chain getBounty failed: ${err.message}`);
  }

  // API cross-check (use effectiveJobId, which may be bountyId after reconciliation)
  try {
    const verifyRes = await fetch(`${baseUrl}/api/jobs/${effectiveJobId}`, {
      headers: { 'X-Bot-API-Key': apiKey },
    });
    if (verifyRes.ok) {
      const verifyData = await verifyRes.json();
      const apiJob = verifyData.job || verifyData;
      const apiCid = apiJob.primaryCid || apiJob.evaluationCid;
      if (apiCid && apiCid !== primaryCid) {
        issues.push(`API CID mismatch: API=${apiCid}, expected=${primaryCid}`);
      }
      if (issues.length === 0) {
        console.log(`  API cross-check (jobId=${effectiveJobId}): evaluationCid match. ✓`);
      }
    } else {
      issues.push(`API job fetch failed: GET /api/jobs/${effectiveJobId} returned HTTP ${verifyRes.status}`);
    }
  } catch (err) {
    issues.push(`API cross-check failed: ${err.message}`);
  }

  if (issues.length > 0) {
    integrityOk = false;
    console.warn('\n  ⚠ INTEGRITY ISSUES DETECTED:');
    issues.forEach(i => console.warn(`    - ${i}`));
    console.warn('  DO NOT submit to this bounty until issues are resolved.');
    console.warn('  This may indicate API index drift or ID collision on mainnet.');
  }
} else {
  console.warn('  Skipping integrity check (bountyId not parsed from event).');
  integrityOk = false;
}

// ---- Done ----

const verdict = integrityOk ? 'GO' : 'NO-GO (see warnings above)';
console.log(`\n✅ Bounty created successfully!  Integrity: ${verdict}`);
console.log(`   Title:        ${title}`);
console.log(`   API Job ID:   ${jobId} (original)`);
console.log(`   Effective ID: ${effectiveJobId} (use this for API calls)`);
console.log(`   Bounty ID:    ${bountyId} (on-chain)`);
console.log(`   Amount:       ${bountyAmount} ETH`);
console.log(`   Deadline:     ${new Date(deadline * 1000).toISOString()}`);
console.log(`   Linked:       ${linked ? 'yes' : 'no (sync service may resolve automatically)'}`);
console.log(`\n   View: ${baseUrl.replace('/api', '')}`);

// Machine-parseable identifiers for automation harnesses
console.log(`API_JOB_ID=${jobId}`);
console.log(`EFFECTIVE_JOB_ID=${effectiveJobId}`);
console.log(`CANONICAL_JOB_ID=${effectiveJobId}`);
console.log(`BOUNTY_ID=${bountyId}`);
