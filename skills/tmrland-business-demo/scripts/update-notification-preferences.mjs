#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: update-notification-preferences.mjs [--order-status true|false] [--dispute-update true|false] [--payment-received true|false] [--system-announcement true|false]");
  process.exit(2);
}

const body = {};
for (const [flag, key] of [
  ["order-status", "order_status"],
  ["dispute-update", "dispute_update"],
  ["payment-received", "payment_received"],
  ["system-announcement", "system_announcement"],
  ["intention-matched", "intention_matched"],
  ["intention-expired", "intention_expired"],
  ["dispute-sla-warning", "dispute_sla_warning"],
]) {
  if (named[flag] !== undefined) body[key] = named[flag] === "true";
}

const data = await tmrFetch("PATCH", "/notifications/preferences", body);
console.log(JSON.stringify(data, null, 2));
