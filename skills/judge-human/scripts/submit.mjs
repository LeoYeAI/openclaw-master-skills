#!/usr/bin/env node
// Judge Human — Submit a new case
// Requires JUDGEHUMAN_API_KEY env var
// Usage: node submit.mjs --title "..." --content "..." [--content-type TEXT] [--type ETHICAL_DILEMMA]

import { parseArgs } from "node:util";

const BASE = "https://www.judgehuman.ai";
const CONTENT_TYPES = ["TEXT", "URL", "IMAGE"];
const CASE_TYPES = ["ETHICAL_DILEMMA", "CREATIVE_WORK", "PUBLIC_STATEMENT", "PRODUCT_BRAND", "PERSONAL_BEHAVIOR"];

const { values } = parseArgs({
  options: {
    title: { type: "string" },
    content: { type: "string" },
    "content-type": { type: "string" },
    "source-url": { type: "string" },
    context: { type: "string" },
    type: { type: "string" },
    help: { type: "boolean", short: "h" },
  },
  strict: true,
});

if (values.help) {
  console.error(`Usage: node submit.mjs --title <title> --content <content> [options]

Required:
  --title         Case title (5-200 chars)
  --content       Case content (10-5000 chars)

Optional:
  --content-type  Content type: ${CONTENT_TYPES.join(", ")} (default: TEXT)
  --source-url    Source URL
  --context       Additional context (max 1000 chars)
  --type          Suggested case type: ${CASE_TYPES.join(", ")}
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

if (!values.title || !values.content) {
  console.error("Error: --title and --content are required. Use --help for usage.");
  process.exit(2);
}

const body = {
  title: values.title,
  content: values.content,
};

if (values["content-type"]) {
  const ct = values["content-type"].toUpperCase();
  if (!CONTENT_TYPES.includes(ct)) {
    console.error(`Error: --content-type must be one of: ${CONTENT_TYPES.join(", ")}`);
    process.exit(2);
  }
  body.contentType = ct;
}

if (values["source-url"]) body.sourceUrl = values["source-url"];
if (values.context) body.context = values.context;

if (values.type) {
  const t = values.type.toUpperCase();
  if (!CASE_TYPES.includes(t)) {
    console.error(`Error: --type must be one of: ${CASE_TYPES.join(", ")}`);
    process.exit(2);
  }
  body.suggestedType = t;
}

try {
  const res = await fetch(`${BASE}/api/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${KEY}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || "Submission failed"}`);
    if (data.details) console.error(JSON.stringify(data.details, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(data, null, 2));
} catch (err) {
  console.error(`Network error: ${err.message}`);
  process.exit(1);
}
