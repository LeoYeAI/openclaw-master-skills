#!/usr/bin/env node
// Poll for evaluation result and claim payout if the submission passed.
// The bot wallet signs the finalizeSubmission transaction automatically.
//
// Usage:
//   node claim_bounty.js --jobId 80 --submissionId 0
//   node claim_bounty.js --jobId 80 --submissionId 0 --maxWait 600
//
// Typical flow:
//   1. Run submit_to_bounty.js → submission enters PENDING_EVALUATION
//   2. Wait 2-5 minutes for oracle evaluation
//   3. Run this script → polls, then claims payout if passed
//
// Prerequisites:
//   - Submission already started (via submit_to_bounty.js)
//   - Bot wallet has ETH for gas (finalize tx)

import './_env.js';
import {
  getNetwork, providerFor, loadWallet, redactApiKey,
  arg, loadApiKey, sendTx,
} from './_lib.js';

const jobId = arg('jobId');
const submissionId = arg('submissionId');
const maxWaitSec = Number(arg('maxWait', '600')); // default 10 min

if (!jobId || submissionId == null) {
  console.error('Usage: node claim_bounty.js --jobId <ID> --submissionId <ID> [--maxWait <seconds>]');
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
const hunter = signer.address;

const apiKey = await loadApiKey();
if (!apiKey) {
  console.error('Missing API key. Run onboard.js first.');
  process.exit(1);
}

const headers = { 'X-Bot-API-Key': apiKey };
const jsonHeaders = { ...headers, 'Content-Type': 'application/json' };

console.log(`\nClaim bounty payout`);
console.log(`Job:          #${jobId}`);
console.log(`Submission:   #${submissionId}`);
console.log(`Network:      ${network}`);
console.log(`Hunter:       ${hunter}`);
console.log(`API:          ${baseUrl}`);
console.log(`Max wait:     ${maxWaitSec}s`);

// ---- Helper: sleep ----

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ---- Step 1: Poll for evaluation result ----

console.log('\n--- Step 1: Wait for evaluation result ---');

const POLL_INTERVAL_SEC = 30;
const startTime = Date.now();
let status = null;
let acceptance = null;
let rejection = null;

while (true) {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);

  // Refresh submission status from blockchain
  const refreshRes = await fetch(
    `${baseUrl}/api/jobs/${jobId}/submissions/${submissionId}/refresh`,
    { method: 'POST', headers }
  );

  if (!refreshRes.ok) {
    const errData = await refreshRes.json().catch(() => ({}));
    console.error(`  Refresh failed (HTTP ${refreshRes.status}):`, JSON.stringify(errData));
    process.exit(1);
  }

  const refreshData = await refreshRes.json();
  const sub = refreshData.submission || refreshData;
  status = sub.status;
  acceptance = sub.acceptance;
  rejection = sub.rejection;

  console.log(`  [${elapsed}s] Status: ${status}  (acceptance: ${acceptance ?? '?'}, rejection: ${rejection ?? '?'})`);

  // Terminal states — evaluation is done
  if (status === 'ACCEPTED_PENDING_CLAIM') {
    console.log(`\n  ✓ Evaluation passed! Score: ${acceptance}%`);
    break;
  }
  if (status === 'REJECTED_PENDING_FINALIZATION') {
    console.log(`\n  ✗ Evaluation failed. Score: ${acceptance}% (threshold not met)`);
    console.log(`  The submission did not pass. No payout to claim.`);
    // Still finalize to pull results on-chain (releases LINK back)
    break;
  }
  if (status === 'APPROVED' || status === 'REJECTED') {
    console.log(`\n  Already finalized (status: ${status}).`);
    if (sub.paidWinner) {
      console.log('  Payout already claimed.');
    }
    process.exit(0);
  }

  // Check timeout
  if (elapsed >= maxWaitSec) {
    console.error(`\n  Timed out after ${maxWaitSec}s. Status still: ${status}`);
    console.error(`  Re-run this script later to check again.`);
    process.exit(1);
  }

  // Wait before next poll
  const remaining = maxWaitSec - elapsed;
  const waitSec = Math.min(POLL_INTERVAL_SEC, remaining);
  console.log(`  Waiting ${waitSec}s before next check...`);
  await sleep(waitSec * 1000);
}

// ---- Step 2: Finalize submission (claim payout) ----

console.log('\n--- Step 2: Finalize submission (claim payout) ---');

const finalizeRes = await fetch(
  `${baseUrl}/api/jobs/${jobId}/submissions/${submissionId}/finalize`,
  {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify({ hunter }),
  }
);
const finalizeData = await finalizeRes.json();

if (!finalizeRes.ok || !finalizeData.transaction) {
  if (finalizeData.error === 'Evaluation not ready') {
    console.error('  Evaluation not ready yet. Wait a bit longer and re-run.');
  } else {
    console.error('  Finalize failed:', JSON.stringify(finalizeData, null, 2));
  }
  // Try /diagnose for more context
  try {
    const diagRes = await fetch(
      `${baseUrl}/api/jobs/${jobId}/submissions/${submissionId}/diagnose`,
      { headers }
    );
    if (diagRes.ok) {
      const diag = await diagRes.json();
      if (diag.issues?.length) {
        console.error('\n  Diagnosis:');
        diag.issues.forEach(i => console.error(`    - [${i.severity || 'info'}] ${i.message || i}`));
      }
      if (diag.recommendations?.length) {
        console.error('  Recommendations:');
        diag.recommendations.forEach(r => console.error(`    → ${r}`));
      }
    }
  } catch { /* best-effort */ }
  process.exit(1);
}

if (finalizeData.oracleResult) {
  const or = finalizeData.oracleResult;
  console.log(`  Oracle result: acceptance=${or.acceptance}%, rejection=${or.rejection}%, passed=${or.passed}`);
}
if (finalizeData.expectedPayout) {
  console.log(`  Expected payout: ${finalizeData.expectedPayout} ETH`);
}

const finalizeReceipt = await sendTx(signer, 'finalizeSubmission', finalizeData.transaction);

// ---- Done ----

const passed = status === 'ACCEPTED_PENDING_CLAIM';

console.log(`\n✅ Finalization complete!`);
console.log(`   Job:          #${jobId}`);
console.log(`   Submission:   #${submissionId}`);
console.log(`   Score:        ${acceptance}%`);
console.log(`   Result:       ${passed ? 'PASSED — payout claimed!' : 'FAILED — LINK refunded'}`);
if (passed && finalizeData.expectedPayout) {
  console.log(`   Payout:       ${finalizeData.expectedPayout} ETH → ${hunter}`);
}
const safeKey = redactApiKey(apiKey);
console.log(`\nTo see detailed evaluation feedback:`);
console.log(`  curl -H "X-Bot-API-Key: ${safeKey}" ${baseUrl}/api/jobs/${jobId}/submissions/${submissionId}/evaluation`);
