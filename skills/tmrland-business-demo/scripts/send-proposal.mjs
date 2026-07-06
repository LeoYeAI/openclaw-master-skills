#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0] || !named.terms || !named.amount) {
  console.error('Usage: send-proposal.mjs <session-id> --terms \'{"key":"val"}\' --amount N [--status proposal|final_offer]');
  process.exit(2);
}

const body = {
  terms: JSON.parse(named.terms),
  amount: Number.parseFloat(named.amount),
  proposal_status: named.status ?? "proposal",
};

const data = await tmrFetch("POST", `/negotiations/${positional[0]}/propose`, body);
console.log(JSON.stringify(data, null, 2));
