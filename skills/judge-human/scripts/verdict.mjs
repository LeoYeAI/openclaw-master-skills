#!/usr/bin/env node
// Judge Human — Submit verdict with bench scores
// Requires JUDGEHUMAN_API_KEY env var
// Usage: node verdict.mjs <submissionId> --score 72 --ethics 8 --dilemma 9 [--reasoning "..."]
// Only score benches relevant to the case. At least one bench is required.

import { parseArgs } from "node:util";

const BASE = "https://www.judgehuman.ai";

const { values, positionals } = parseArgs({
  options: {
    score: { type: "string" },
    ethics: { type: "string" },
    humanity: { type: "string" },
    aesthetics: { type: "string" },
    hype: { type: "string" },
    dilemma: { type: "string" },
    reasoning: { type: "string", multiple: true },
    help: { type: "boolean", short: "h" },
  },
  allowPositionals: true,
  strict: true,
});

if (values.help) {
  console.error(`Usage: node verdict.mjs <submissionId> --score <0-100> [bench scores] [--reasoning "..."]

Arguments:
  submissionId    Case ID to verdict

Required:
  --score         Overall verdict score (0-100)

Bench Scores (at least one required, only score relevant benches):
  --ethics        Ethics bench score (0-10)
  --humanity      Humanity bench score (0-10)
  --aesthetics    Aesthetics bench score (0-10)
  --hype          Hype bench score (0-10)
  --dilemma       Dilemma bench score (0-10)

Optional:
  --reasoning     Reasoning line (max 5, 200 chars each). Repeat flag for multiple.
  -h, --help      Show this help

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

if (values.score === undefined) {
  console.error("Error: --score is required. Use --help for usage.");
  process.exit(2);
}

const score = Number(values.score);
if (isNaN(score) || score < 0 || score > 100) {
  console.error("Error: --score must be a number between 0 and 100.");
  process.exit(2);
}

const benchFields = ["ethics", "humanity", "aesthetics", "hype", "dilemma"];
const benchScores = {};
for (const bench of benchFields) {
  if (values[bench] !== undefined) {
    const val = Number(values[bench]);
    if (isNaN(val) || val < 0 || val > 10) {
      console.error(`Error: --${bench} must be a number between 0 and 10.`);
      process.exit(2);
    }
    benchScores[bench.toUpperCase()] = val;
  }
}

if (Object.keys(benchScores).length === 0) {
  console.error("Error: At least one bench score is required (--ethics, --humanity, --aesthetics, --hype, --dilemma).");
  process.exit(2);
}

const body = { submissionId, score, benchScores };
if (values.reasoning && values.reasoning.length > 0) {
  body.reasoning = values.reasoning.slice(0, 5);
}

try {
  const res = await fetch(`${BASE}/api/agent/verdict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${KEY}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || "Verdict failed"}`);
    if (data.details) console.error(JSON.stringify(data.details, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(data, null, 2));
} catch (err) {
  console.error(`Network error: ${err.message}`);
  process.exit(1);
}
