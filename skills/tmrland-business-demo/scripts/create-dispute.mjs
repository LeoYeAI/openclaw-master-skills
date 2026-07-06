#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0] || !named.reason) {
  console.error("Usage: create-dispute.mjs <order-id> --reason \"...\" [--refund-type full|partial] [--refund-amount N]");
  process.exit(2);
}

const body = { reason: named.reason };
if (named["refund-type"]) body.refund_type = named["refund-type"];
if (named["refund-amount"]) body.refund_amount = Number.parseFloat(named["refund-amount"]);

const data = await tmrFetch("POST", `/orders/${positional[0]}/dispute`, body);
console.log(JSON.stringify(data, null, 2));
