#!/usr/bin/env node
/**
 * Four.meme - fetch public config (raisedToken for create-token API)
 * Usage: npx tsx skills/four-meme-integration/scripts/get-public-config.ts
 * Output: JSON with raisedToken and other config (use raisedToken in create body as-is).
 */

const API_BASE = 'https://four.meme/meme-api/v1';

async function main() {
  const res = await fetch(`${API_BASE}/public/config`);
  if (!res.ok) {
    throw new Error(`Config request failed: ${res.status} ${await res.text()}`);
  }
  const data = await res.json();
  if (data.code !== '0' && data.code !== 0) {
    throw new Error(`Config error: ${JSON.stringify(data)}`);
  }
  console.log(JSON.stringify(data.data ?? data, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
