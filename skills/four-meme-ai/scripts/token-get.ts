#!/usr/bin/env node
/**
 * Four.meme - token detail + trading info (REST API)
 * GET /meme-api/v1/private/token/get/v2?address=<address>
 * Usage: npx tsx token-get.ts <tokenAddress>
 * Output: JSON token info and trading info.
 */

const API_BASE = 'https://four.meme/meme-api/v1';

async function main() {
  const address = process.argv[2];
  if (!address) {
    console.error('Usage: npx tsx token-get.ts <tokenAddress>');
    process.exit(1);
  }
  const url = `${API_BASE}/private/token/get/v2?address=${encodeURIComponent(address)}`;
  const res = await fetch(url, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`token/get/v2 failed: ${res.status} ${await res.text()}`);
  }
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
