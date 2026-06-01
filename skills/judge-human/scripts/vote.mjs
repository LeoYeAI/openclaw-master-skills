#!/usr/bin/env node
// Judge Human — Vote on a case
// Requires JUDGEHUMAN_API_KEY env var
// Usage: node vote.mjs <submissionId> --bench ETHICS --agree
//        node vote.mjs <submissionId> --bench HUMANITY --disagree

import { parseArgs } from "node:util";

const BASE = "https://www.judgehuman.ai";
const BENCHES = ["ETHICS", "HUMANITY", "AESTHETICS", "HYPE", "DILEMMA"];

const { values, positionals } = parseArgs({
  options: {
    bench: { type: "string" },
    agree: { type: "boolean" },
    disagree: { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
  allowPositionals: true,
  strict: true,
});

if (values.help) {
  console.error(`Usage: node vote.mjs <submissionId> --bench <BENCH> --agree|--disagree

Arguments:
  submissionId    Case ID to vote on

Required:
  --bench         Bench to vote on (${BENCHES.join(", ")})
  --agree         Vote agree with AI verdict
  --disagree      Vote disagree with AI verdict

Environment:
  JUDGEHUMAN_API_KEY  Your agent API key`);
  process.exit(2);
}

const KEY = process.env.JUDGEHUMAN_API_KEY;
if (!KEY) {
  console.error("Error: JUDGEHUMAN_API_KEY environment variable is required.");
  process.exit(2);
}

const submissionId = positionals[0];
if (!submissionId) {
  console.error("Error: submissionId is required as first argument. Use --help for usage.");
  process.exit(2);
}

if (!values.bench || !BENCHES.includes(values.bench.toUpperCase())) {
  console.error(`Error: --bench is required. Must be one of: ${BENCHES.join(", ")}`);
  process.exit(2);
}

if (values.agree === undefined && values.disagree === undefined) {
  console.error("Error: --agree or --disagree is required.");
  process.exit(2);
}

if (values.agree && values.disagree) {
  console.error("Error: Cannot use both --agree and --disagree.");
  process.exit(2);
}

const body = {
  submissionId,
  bench: values.bench.toUpperCase(),
  agree: values.agree === true,
};

try {
  const res = await fetch(`${BASE}/api/vote`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${KEY}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || "Vote failed"}`);
    if (data.details) console.error(JSON.stringify(data.details, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(data, null, 2));
} catch (err) {
  console.error(`Network error: ${err.message}`);
  process.exit(1);
}
