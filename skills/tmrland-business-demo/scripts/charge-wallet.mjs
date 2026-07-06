#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.amount) {
  console.error("Usage: charge-wallet.mjs --amount N [--currency USD]");
  process.exit(2);
}

const body = {
  amount: Number.parseFloat(named.amount),
  currency: named.currency ?? "USD",
};

const data = await tmrFetch("POST", "/wallet/charge", body);
console.log(JSON.stringify(data, null, 2));
