#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.capabilities) {
  console.error('Usage: discover-agents.mjs --capabilities "a,b,c"');
  process.exit(2);
}

const body = { capabilities: named.capabilities.split(",").map(s => s.trim()) };

const data = await tmrFetch("POST", "/a2a/discover", body);
console.log(JSON.stringify(data, null, 2));
