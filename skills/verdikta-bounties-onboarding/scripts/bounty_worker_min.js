#!/usr/bin/env node
import './_env.js';
// Verify setup: list open jobs + print titles.
// Confirms API connectivity. Does not submit work.

import { loadApiKey } from './_lib.js';

const baseUrl = process.env.VERDIKTA_BOUNTIES_BASE_URL || 'https://bounties.verdikta.org';

const apiKey = await loadApiKey();
if (!apiKey) throw new Error('Missing apiKey. Run onboard.js first.');

const url = new URL(`${baseUrl}/api/jobs`);
url.searchParams.set('status', 'OPEN');
url.searchParams.set('minHoursLeft', '2');

const resp = await fetch(url, {
  headers: { 'X-Bot-API-Key': apiKey }
});
const data = await resp.json();
if (!resp.ok) throw new Error(`jobs failed: ${resp.status} ${JSON.stringify(data)}`);

for (const job of (data.jobs || [])) {
  console.log(`#${job.jobId}: ${job.title} — $${job.bountyAmountUSD || 0}`);
}
