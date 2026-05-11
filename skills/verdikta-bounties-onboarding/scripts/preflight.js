#!/usr/bin/env node
// Pre-flight GO/NO-GO check before submitting to a bounty.
// Runs all safety checks without spending funds.
//
// Usage:
//   node preflight.js --jobId 72
//   node preflight.js --jobId 72 --minBuffer 60   # require 60 min before deadline
//
// Checks:
//   1. API job exists and status is OPEN
//   2. Evaluation package is valid (/validate)
//   3. On-chain bounty matches API (creator, CID, classId, threshold)
//   4. On-chain isAcceptingSubmissions returns true
//   5. Deadline has sufficient buffer
//   6. Bot has sufficient LINK balance (via /estimate-fee)
//   7. Bot has sufficient ETH for gas
//
// Prints a clear GO / NO-GO verdict.

import './_env.js';
import { ethers } from 'ethers';
import {
  getNetwork, providerFor, loadWallet,
  escrowContract, linkBalance, arg, loadApiKey,
} from './_lib.js';

const jobId = arg('jobId');
const minBufferMin = Number(arg('minBuffer', '30')); // minutes before deadline

if (!jobId) {
  console.error('Usage: node preflight.js --jobId <ID> [--minBuffer <minutes>]');
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
const botAddress = signer.address;

const apiKey = await loadApiKey();
if (!apiKey) {
  console.error('Missing API key. Run onboard.js first.');
  process.exit(1);
}

const headers = { 'X-Bot-API-Key': apiKey };

console.log(`\nPre-flight check for bounty #${jobId}`);
console.log(`Network:  ${network}`);
console.log(`Bot:      ${botAddress}`);
console.log(`API:      ${baseUrl}`);
console.log(`Buffer:   ${minBufferMin} min before deadline\n`);

// ---- Run checks ----

const results = [];

function check(name, pass, detail) {
  results.push({ name, pass, detail });
  const icon = pass ? '✓' : '✖';
  console.log(`  ${icon} ${name}: ${detail}`);
}

// 1. API job exists and is OPEN
let job = null;
try {
  const res = await fetch(`${baseUrl}/api/jobs/${jobId}`, { headers });
  if (!res.ok) {
    check('API job exists', false, `HTTP ${res.status}`);
  } else {
    const data = await res.json();
    job = data.job || data;
    const isOpen = !job.status || job.status === 'OPEN';
    check('API job exists', isOpen, isOpen ? `status=${job.status || 'OPEN'}` : `status=${job.status} (not OPEN)`);
  }
} catch (err) {
  check('API job exists', false, err.message);
}

// 2. Evaluation package valid
if (job) {
  try {
    const res = await fetch(`${baseUrl}/api/jobs/${jobId}/validate`, { headers });
    if (res.ok) {
      const data = await res.json();
      const errors = (data.issues || []).filter(i => i.severity === 'error');
      const warnings = (data.issues || []).filter(i => i.severity === 'warning');
      if (data.valid === false && errors.length > 0) {
        check('Evaluation package', false, `${errors.length} error(s): ${errors.map(e => e.message).join('; ')}`);
      } else {
        const warnNote = warnings.length > 0 ? ` (${warnings.length} warning(s))` : '';
        check('Evaluation package', true, `valid${warnNote}`);
      }
    } else {
      check('Evaluation package', true, '(/validate not available — skipped)');
    }
  } catch {
    check('Evaluation package', true, '(/validate unreachable — skipped)');
  }
}

// 3 & 4. On-chain bounty verification
//
// The API uses a unified ID model: after reconciliation, job.jobId IS the
// on-chain bountyId. There is no separate "bountyId" field on API jobs.
// We detect on-chain linkage via job.onChain or job.txHash.
const onChainBountyId = job?.bountyId ?? (job?.onChain || job?.txHash ? job.jobId : null);

if (onChainBountyId != null) {
  try {
    const readContract = escrowContract(network, provider);

    // getBounty (with retry for RPC eventual consistency)
    let onChain;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        onChain = await readContract.getBounty(BigInt(onChainBountyId));
        break;
      } catch (rpcErr) {
        if (attempt < 3 && rpcErr.message?.includes('bad bountyId')) {
          console.log(`  (RPC returned stale state, retrying in ${attempt * 2}s...)`);
          await new Promise(r => setTimeout(r, attempt * 2000));
        } else {
          throw rpcErr;
        }
      }
    }

    const chainCid = onChain.evaluationCid ?? onChain[1];
    const chainClass = Number(onChain.requestedClass ?? onChain[2]);
    const chainThreshold = Number(onChain.threshold ?? onChain[3]);

    const mismatches = [];
    const jobCid = job.primaryCid || job.evaluationCid;
    if (jobCid && chainCid !== jobCid) mismatches.push(`CID(chain=${chainCid.slice(0, 12)}…)`);
    if (job.classId != null && chainClass !== Number(job.classId)) mismatches.push(`classId(chain=${chainClass})`);
    if (job.threshold != null && chainThreshold !== Number(job.threshold)) mismatches.push(`threshold(chain=${chainThreshold})`);

    if (mismatches.length > 0) {
      check('On-chain match', false, `mismatches: ${mismatches.join(', ')}`);
    } else {
      check('On-chain match', true, `CID, classId, threshold all match (bountyId=${onChainBountyId})`);
    }

    // isAcceptingSubmissions
    const accepting = await readContract.isAcceptingSubmissions(BigInt(onChainBountyId));
    check('Accepting submissions', accepting, accepting ? 'yes' : 'no (closed or deadline passed)');

  } catch (err) {
    check('On-chain verification', false, err.message);
  }
} else {
  check('On-chain match', false, 'job not linked to chain (no onChain flag or txHash)');
}

// 5. Deadline buffer
if (job?.submissionCloseTime) {
  const deadline = new Date(typeof job.submissionCloseTime === 'number'
    ? job.submissionCloseTime * 1000
    : job.submissionCloseTime);
  const msLeft = deadline.getTime() - Date.now();
  const minLeft = Math.floor(msLeft / 60000);
  const hasBuffer = minLeft >= minBufferMin;
  check('Deadline buffer', hasBuffer,
    hasBuffer
      ? `${minLeft} min remaining (deadline: ${deadline.toISOString()})`
      : `only ${minLeft} min left (need ${minBufferMin}). Deadline: ${deadline.toISOString()}`
  );
} else {
  check('Deadline buffer', true, 'no deadline set');
}

// 6. LINK balance (vs estimate-fee)
let estimatedLink = 0.05; // fallback
try {
  const feeRes = await fetch(`${baseUrl}/api/jobs/${jobId}/estimate-fee`, { headers });
  if (feeRes.ok) {
    const feeData = await feeRes.json();
    estimatedLink = Number(feeData.estimatedFee || feeData.fee || feeData.linkCost || 0.05);
  }
} catch { /* use fallback */ }

try {
  const { bal, dec } = await linkBalance(network, provider, botAddress);
  const linkHuman = Number(ethers.formatUnits(bal, dec));
  const enough = linkHuman >= estimatedLink;
  check('LINK balance', enough,
    enough
      ? `${linkHuman.toFixed(4)} LINK (need ~${estimatedLink.toFixed(4)})`
      : `${linkHuman.toFixed(4)} LINK — need ~${estimatedLink.toFixed(4)} LINK`
  );
} catch (err) {
  check('LINK balance', false, err.message);
}

// 7. ETH balance for gas
try {
  const ethBal = await provider.getBalance(botAddress);
  const ethHuman = Number(ethers.formatEther(ethBal));
  const minEth = 0.001; // rough gas estimate for 3 txs
  const enough = ethHuman >= minEth;
  check('ETH balance', enough,
    enough
      ? `${ethHuman.toFixed(6)} ETH (gas for ~3 txs)`
      : `${ethHuman.toFixed(6)} ETH — need at least ~${minEth} ETH for gas`
  );
} catch (err) {
  check('ETH balance', false, err.message);
}

// ---- Verdict ----

const allPassed = results.every(r => r.pass);
const failures = results.filter(r => !r.pass);

console.log(`\n${'='.repeat(50)}`);
if (allPassed) {
  console.log(`  VERDICT: GO — all ${results.length} checks passed`);
} else {
  console.log(`  VERDICT: NO-GO — ${failures.length} of ${results.length} check(s) failed`);
  failures.forEach(f => console.log(`    ✖ ${f.name}: ${f.detail}`));
}
console.log(`${'='.repeat(50)}\n`);

process.exit(allPassed ? 0 : 1);
