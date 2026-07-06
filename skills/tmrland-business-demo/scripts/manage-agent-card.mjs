#!/usr/bin/env node
import { tmrFetch, tmrFetchSafe, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named["business-id"]) {
  console.error('Usage: manage-agent-card.mjs --business-id <id> [--capabilities "a,b,c"] [--a2a-endpoint URL]');
  process.exit(2);
}

const businessId = named["business-id"];
const body = {};
if (named.capabilities) body.capabilities = named.capabilities.split(",").map(s => s.trim());
if (named["a2a-endpoint"]) body.a2a_endpoint = named["a2a-endpoint"];

// Try PATCH first (update); fall back to POST (create) on 404
const patchResult = await tmrFetchSafe("PATCH", `/businesses/${businessId}/agent-card`, body);
if (patchResult.ok) {
  console.log(JSON.stringify(patchResult.data, null, 2));
} else if (patchResult.status === 404) {
  const data = await tmrFetch("POST", `/businesses/${businessId}/agent-card`, body);
  console.log(JSON.stringify(data, null, 2));
} else {
  console.error(`API error ${patchResult.status}: ${patchResult.error}`);
  process.exit(1);
}
